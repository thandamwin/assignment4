#!/usr/bin/env python3
import aws_cdk as cdk
from driver_lambda_stack import DriverLambdaStack
from plotting_lambda_stack import PlottingLambdaStack
from size_tracking_lambda_stack import SizeTrackingLambdaStack
from hw3_stack import ResourcesStack
from log_stack import LogLambdaStack
from cleaner_lambda_stack import CleanerLambdaStack

app = cdk.App()

# Define each Lambda in its own stack
DriverLambdaStack(app, "DriverLambdaStack")
PlottingLambdaStack(app, "PlottingLambdaStack")
SizeTrackingLambdaStack(app, "SizeTrackingLambdaStack")
ResourcesStack(app, "ResourcesStack")
LogLambdaStack(app, "LogLambdaStack")
CleanerLambdaStack(app, "CleanerLambdaStack")

app.synth()
