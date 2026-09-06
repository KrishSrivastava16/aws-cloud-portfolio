import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_portfolio_project.cdk_portfolio_project_stack import CdkPortfolioProjectStack


def get_template():
    app = core.App()
    stack = CdkPortfolioProjectStack(app, "cdk-portfolio-project")
    return assertions.Template.from_stack(stack)


def test_dynamodb_table_uses_on_demand_billing():
    template = get_template()
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST"
    })


def test_exactly_one_cloudfront_distribution():
    template = get_template()
    template.resource_count_is("AWS::CloudFront::Distribution", 1)


def test_s3_bucket_blocks_public_access():
    template = get_template()
    template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })


def test_api_gateway_has_count_route():
    template = get_template()
    template.has_resource_properties("AWS::ApiGatewayV2::Route", {
        "RouteKey": "GET /count"
    })


def test_lambda_uses_python312_runtime():
    template = get_template()
    template.has_resource_properties("AWS::Lambda::Function", {
        "Runtime": "python3.12"
    })