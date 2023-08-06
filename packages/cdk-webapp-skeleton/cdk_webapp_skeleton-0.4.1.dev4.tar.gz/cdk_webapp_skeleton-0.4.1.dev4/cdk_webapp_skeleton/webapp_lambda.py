import warnings
from typing import Optional

import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as events_targets
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_sns as sns
from constructs import Construct

from .branch_config import BranchConfig
from .monitored_lambda_function import MonitoredLambdaFunction


class WebappLambda(Construct):
    """Assumes a local folder called "webapp-backend" with a Dockerfile in it."""

    def __init__(
        self,
        scope: "Construct",
        _id: str,
        branch_config: BranchConfig,
        code: _lambda.DockerImageCode = None,
        image_directory=None,
        lambda_runtime_environment=None,
        memory_size: Optional[int] = 256,
        alarm_topic: Optional[sns.ITopic] = None,
    ):
        super().__init__(scope, branch_config.construct_id(_id) + "Construct")

        warn_stacklevel = 3
        if code is None:
            if image_directory is None:
                warnings.warn(
                    'image_directory defaults to "webapp-backend", but this will be deprecated in favor of "code"',
                    DeprecationWarning,
                    stacklevel=warn_stacklevel,
                )
                image_directory = "webapp-backend"
            else:
                warnings.warn(
                    '"image_directory" will be deprecated in favor of "code"',
                    DeprecationWarning,
                    stacklevel=warn_stacklevel,
                )
            code = _lambda.DockerImageCode.from_image_asset(directory=image_directory)
        else:
            if image_directory is not None:
                warnings.warn(
                    "image_directory is ignored when code is specified",
                    RuntimeWarning,
                    stacklevel=warn_stacklevel,
                )

        self.monitored_lambda = MonitoredLambdaFunction(
            scope,
            branch_config.construct_id(_id),
            code=code,
            lambda_runtime_environment=lambda_runtime_environment,
            memory_size=memory_size,
            alarm_topic=alarm_topic,
        )
        self.webapp_lambda_func = self.monitored_lambda.lambda_function

        root_hosted_zone = branch_config.get_hosted_zone(scope)
        if root_hosted_zone is not None:
            backend_domain_name = "api." + branch_config.domain_name

            backend_certificate = certificatemanager.Certificate(
                scope,
                "apiCert",
                domain_name=backend_domain_name,
                validation=certificatemanager.CertificateValidation.from_dns(
                    root_hosted_zone
                ),
            )

            # noinspection PyTypeChecker
            cors_options = apigateway.CorsOptions(
                # Code analysis is glitching here, this is the correct way to pass this param.
                allow_origins=apigateway.Cors.ALL_ORIGINS
            )

            lambda_gateway = apigateway.LambdaRestApi(
                scope,
                branch_config.construct_id("WebappBackendApi"),
                handler=self.webapp_lambda_func,
                domain_name=apigateway.DomainNameOptions(
                    domain_name=backend_domain_name, certificate=backend_certificate
                ),
                # Used by the RestApiWarmup event rule below.
                disable_execute_api_endpoint=False,
                default_cors_preflight_options=cors_options,
                deploy_options=apigateway.StageOptions(
                    tracing_enabled=True,
                ),
            )

            events.Rule(
                scope,
                "RestApiWarmup",
                targets=[events_targets.ApiGateway(lambda_gateway, retry_attempts=0)],
                schedule=events.Schedule.rate(cdk.Duration.minutes(1)),
            )

            route53.ARecord(
                scope,
                "BackendApiARecord",
                zone=root_hosted_zone,
                target=route53.RecordTarget.from_alias(
                    route53_targets.ApiGateway(lambda_gateway)
                ),
                record_name=backend_domain_name,
            )
