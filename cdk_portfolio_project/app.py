from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3_deployment,
)
from constructs import Construct


class CdkPortfolioProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. S3 bucket to hold the website files
        site_bucket = s3.Bucket(
            self, "CdkPortfolioBucket",
            removal_policy=RemovalPolicy.DESTROY,  # so 'cdk destroy' cleans up fully (fine for learning)
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # CloudFront will access it privately
        )

        # 2. CloudFront distribution serving that bucket
        distribution = cloudfront.Distribution(
            self, "CdkPortfolioDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(site_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
        )

        # 3. Automatically upload your site files to the bucket on every deploy
        s3_deployment.BucketDeployment(
            self, "DeploySiteContent",
            sources=[s3_deployment.Source.asset("./website")],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=["/*"],  # auto-invalidate CloudFront cache on deploy
        )

        # Print the CloudFront URL after deployment finishes
        CfnOutput(
            self, "SiteURL",
            value=f"https://{distribution.distribution_domain_name}",
        )