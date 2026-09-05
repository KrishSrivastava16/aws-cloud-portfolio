import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_portfolio_project.cdk_portfolio_project_stack import CdkPortfolioProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_portfolio_project/cdk_portfolio_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkPortfolioProjectStack(app, "cdk-portfolio-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
