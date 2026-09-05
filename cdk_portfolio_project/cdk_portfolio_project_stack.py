from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3_deployment,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations,
)
from constructs import Construct


class CdkPortfolioProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------- FRONTEND: S3 + CloudFront ----------

        site_bucket = s3.Bucket(
            self, "CdkPortfolioBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        distribution = cloudfront.Distribution(
            self, "CdkPortfolioDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(site_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
        )

        # ---------- BACKEND: DynamoDB ----------

        visitor_table = dynamodb.Table(
            self, "VisitorCounterTable",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # same as on-demand mode you used manually
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ---------- BACKEND: Lambda ----------

        visitor_function = _lambda.Function(
            self, "VisitorCounterFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="visitor_counter.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": visitor_table.table_name
            },
            timeout=Duration.seconds(10),
        )

        # Grant Lambda read/write access to just this table (scoped down, unlike the FullAccess you used manually)
        visitor_table.grant_read_write_data(visitor_function)

        # ---------- BACKEND: API Gateway (HTTP API) ----------

        http_api = apigwv2.HttpApi(
            self, "VisitorCounterApi",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigwv2.CorsHttpMethod.GET],
            ),
        )

        http_api.add_routes(
            path="/count",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "VisitorCounterIntegration", visitor_function
            ),
        )

        # ---------- Deploy site files ----------

        s3_deployment.BucketDeployment(
            self, "DeploySiteContent",
            sources=[s3_deployment.Source.asset("./website")],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # ---------- Outputs ----------

        CfnOutput(self, "SiteURL", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "ApiURL", value=f"{http_api.api_endpoint}/count")