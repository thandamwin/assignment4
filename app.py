#!/usr/bin/env python3
import aws_cdk as cdk
from driver_lambda_stack import DriverLambdaStack
from plotting_lambda_stack import PlottingLambdaStack
# from size_tracking_lambda_stack import SizeTrackingLambdaStack
# from hw3_stack import ResourcesStack

app = cdk.App()

# Define each Lambda in its own stack
DriverLambdaStack(app, "DriverLambdaStack")
PlottingLambdaStack(app, "PlottingLambdaStack")
# SizeTrackingLambdaStack(app, "SizeTrackingLambdaStack")
# ResourcesStack(app, "ResourcesStack")

app.synth()
