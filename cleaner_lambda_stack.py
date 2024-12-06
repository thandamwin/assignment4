from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    CfnOutput
)
from constructs import Construct

class CleanerLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        cleaner_lambda = _lambda.Function(
            self,
            "CleanerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="cleaner_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/cleaner_lambda"),
        )

        bucket = s3.Bucket.from_bucket_name(self, "MyBucket", "cdk-tmw-testbucket")

        bucket.grant_delete(cleaner_lambda)

        alarm = cloudwatch.Alarm.from_alarm_arn(
            self, "MyAlarm", 
            alarm_arn="arn:aws:cloudwatch:us-east-1:445567102516:alarm:LogLambdaStack-ObjectSizeThresholdAlarm7C7E90CA-fWPWHOI5anI1"
        )

        alarm.add_alarm_action(
            cw_actions.LambdaAction(cleaner_lambda)
        )

        cleaner_lambda.add_permission(
            "AllowCloudWatchInvoke",
            principal=iam.ServicePrincipal("cloudwatch.amazonaws.com"),
            source_arn=alarm.alarm_arn
        )