from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    Duration,
    aws_logs as logs,
    aws_lambda_event_sources as lambda_sources,
    aws_cloudwatch as cloudwatch,
    CfnOutput
)
from constructs import Construct

class LogLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        log_lambda = _lambda.Function(
            self,
            "LogLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="log_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/log_lambda"), 
            timeout=Duration.seconds(30),
            memory_size=128
        )

        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name="/aws/lambda/s3_operation",
            retention=logs.RetentionDays.ONE_WEEK 
        )

        logs.LogStream(
            self,
            "LogStream",
            log_group=log_group,
            log_stream_name="s3_log"
        )

        log_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[log_group.log_group_arn]
        ))

        log_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["logs:StartQuery", "logs:GetQueryResults", "logs:StopQuery"],
            resources=[log_group.log_group_arn]
        ))

        metric_filter = logs.MetricFilter(
            self,
            "ObjectSizeChangeMetricFilter",
            log_group=log_group,
            metric_namespace="Assignment4App",
            metric_name="TotalObjectSize",
            filter_pattern=logs.FilterPattern.exists("$.size_delta"),
            metric_value="$.size_delta" 
        )

        alarm = cloudwatch.Alarm(
            self,
            "ObjectSizeThresholdAlarm",
            metric=metric_filter.metric(statistic="sum", period=Duration.minutes(1)),
            threshold=20,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )

        queue = sqs.Queue.from_queue_arn(
            self,
            "LogQueue",
            queue_arn="arn:aws:sqs:us-east-1:445567102516:ResourcesStack-LoggingQueue2008486F-d7tVOAkcDyai"
        )

        queue.grant_consume_messages(log_lambda)

        sqs_event_source = lambda_sources.SqsEventSource(queue, batch_size=10)
        log_lambda.add_event_source(sqs_event_source)

        CfnOutput(self, "LambdaFunctionName", value=log_lambda.function_name)
        CfnOutput(self, "LogGroupName", value=log_group.log_group_name)
        CfnOutput(self, "LogStreamName", value="s3_operations") 
        CfnOutput(self, "CloudWatchAlarmName", value=alarm.alarm_name)