import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest

from sagemaker_ssh_helper.cdk.cdk.cdk_stack import CdkStack


# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/cdk_stack.py
@pytest.mark.manual
def test_sqs_queue_created():
    app = core.App()
    stack = CdkStack(app, "cdk")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })
