from typing import Dict, Optional

import aws_cdk as cdk
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_codeguruprofiler as codeguruprofiler
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sns as sns
from constructs import Construct


class MonitoredLambdaFunction(Construct):
    def __init__(
        self,
        scope: "Construct",
        _id: str,
        code: _lambda.DockerImageCode = None,
        lambda_runtime_environment: Optional[Dict] = None,
        memory_size: Optional[int] = 256,
        timeout: Optional[cdk.Duration] = None,
        alarm_topic: Optional[sns.ITopic] = None,
    ):
        super().__init__(scope, _id + "Monitor")
        if lambda_runtime_environment is None:
            lambda_runtime_environment = {}
        else:
            lambda_runtime_environment = lambda_runtime_environment.copy()

        profiling_group = codeguruprofiler.ProfilingGroup(
            scope,
            _id + "ProfilingGroup",
            compute_platform=codeguruprofiler.ComputePlatform.AWS_LAMBDA,
        )

        lambda_runtime_environment.update(
            {
                "AWS_CODEGURU_PROFILER_GROUP_ARN": profiling_group.profiling_group_arn,
            }
        )

        self.lambda_function = _lambda.DockerImageFunction(
            scope,
            _id,
            code=code,
            environment=lambda_runtime_environment,
            log_retention=logs.RetentionDays.TWO_WEEKS,
            memory_size=memory_size,
            tracing=_lambda.Tracing.ACTIVE,
            timeout=timeout,
        )

        profiling_group.grant_publish(self.lambda_function)

        timeouts_metric_filter = logs.MetricFilter(
            scope,
            _id + "TimeoutsMetricFilter",
            log_group=self.lambda_function.log_group,
            filter_pattern=logs.FilterPattern.literal('"Task timed out"'),
            metric_name="Timeouts",
            metric_namespace=_id,
            metric_value="1",
            default_value=0,
            unit=cloudwatch.Unit.COUNT,
        )

        throttles_alarm = cloudwatch.Alarm(
            scope,
            _id + "Throttles",
            metric=self.lambda_function.metric_throttles(),
            evaluation_periods=1,
            threshold=0,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
        )

        errors_alarm = cloudwatch.Alarm(
            scope,
            _id + "Errors",
            metric=self.lambda_function.metric_errors(),
            evaluation_periods=1,
            threshold=0,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
        )

        timeouts_alarm = cloudwatch.Alarm(
            scope,
            _id + "Timeouts",
            metric=timeouts_metric_filter.metric(statistic=cloudwatch.Stats.SUM),
            evaluation_periods=1,
            threshold=0,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
        )

        if alarm_topic is not None:
            throttles_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
            errors_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
            timeouts_alarm.add_alarm_action(cloudwatch_actions.SnsAction(alarm_topic))
