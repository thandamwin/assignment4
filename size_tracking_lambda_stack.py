from aws_cdk import (
    Stack,
    Duration,
    aws_s3_notifications as s3_notifications,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_sources,
    CfnOutput
)
from constructs import Construct

class SizeTrackingLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dynamodb_table = dynamodb.Table.from_table_name(
            self,
            "ImportedS3ObjectSizeHistory",
            table_name="cdk-S3-object-size-history"
        )

        size_tracking_queue = sqs.Queue.from_queue_arn(
            self,
            "ImportedSizeTrackingQueue",
            queue_arn="arn:aws:sqs:us-east-1:445567102516:ResourcesStack-SizeTrackingQueue7EE021D2-JoVMYkHz56TC"
        )

        size_tracking_lambda = _lambda.Function(
            self,
            "SizeTrackingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="size_tracking_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/size_tracking_lambda"),
            environment={
                "DYNAMODB_TABLE_NAME": dynamodb_table.table_name,
            },
            timeout=Duration.seconds(25)
        )

        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )

        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
        )

        sqs_event_source = lambda_sources.SqsEventSource(size_tracking_queue, batch_size=10)
        size_tracking_lambda.add_event_source(sqs_event_source)

        CfnOutput(self, "LambdaFunctionName", value=size_tracking_lambda.function_name)
        CfnOutput(self, "DynamoDBTableName", value=dynamodb_table.table_name)
        CfnOutput(self, "SQSQueueUrl", value=size_tracking_queue.queue_url)