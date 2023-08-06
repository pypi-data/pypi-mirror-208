from dataclasses import dataclass
from typing import Optional

import aws_cdk as cdk
from aws_cdk import (
    aws_cognito as cognito,
    aws_certificatemanager as certificatemanager,
    aws_route53 as route53,
    aws_ssm as ssm
)
from constructs import Construct

from .branch_config import BranchConfig

USER_POOL_ARN_PARAM = "UserPoolArn"


@dataclass
class AuthStackOutputs(object):
    user_pool_id: cdk.CfnOutput
    user_pool_frontend_client_id: cdk.CfnOutput


class AuthStack(cdk.Stack):
    def __init__(
            self,
            scope: Construct,
            branch_config: BranchConfig,
            user_pool_name: Optional[str] = None,
            **kwargs
    ) -> None:
        super().__init__(scope, "AuthStack", **kwargs, stack_name=branch_config.auth_stack_name())
        self._user_pool_name = user_pool_name

        if branch_config.build_user_pool:
            user_pool = self.build_user_pool(branch_config)
        else:
            user_pool = self.find_user_pool()

        development_signin_url = "http://localhost:3000/signin"
        production_signin_url = f"https://{branch_config.domain_name}/signin"

        frontend_pool_client = user_pool.add_client(
            "app-client",
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    development_signin_url,
                    production_signin_url
                ]
            )
        )

        self.outputs = AuthStackOutputs(
            cdk.CfnOutput(
                self,
                "UserPoolId",
                value=user_pool.user_pool_id
            ),
            cdk.CfnOutput(
                self,
                "UserPoolFrontClientId",
                value=frontend_pool_client.user_pool_client_id
            )
        )

    def find_user_pool(self):
        user_pool_arn = ssm.StringParameter.value_for_string_parameter(
            self,
            parameter_name=USER_POOL_ARN_PARAM
        )
        return cognito.UserPool.from_user_pool_arn(self, "UserPool", user_pool_arn)

    def build_user_pool(self, branch_config: BranchConfig):
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=self._user_pool_name,
            sign_in_case_sensitive=False,
        )

        root_hosted_zone = branch_config.get_hosted_zone(self)
        auth_domain_name = branch_config.auth_domain_name

        if root_hosted_zone is not None:
            auth_domain_certificate = certificatemanager.Certificate(
                self,
                'apiCert',
                domain_name=auth_domain_name,
                validation=certificatemanager.CertificateValidation.from_dns(root_hosted_zone)
            )

            user_pool_domain = user_pool.add_domain("Domain", custom_domain=cognito.CustomDomainOptions(
                certificate=auth_domain_certificate,
                domain_name=auth_domain_name
            ))

            route53.CnameRecord(
                self,
                "UserPoolDomainCNameRecord",
                zone=root_hosted_zone,
                domain_name=user_pool_domain.cloud_front_domain_name,
                record_name="auth"
            )

        ssm.StringParameter(
            self,
            "UserPoolArn",
            description='The ARN of the user pool.',
            parameter_name=USER_POOL_ARN_PARAM,
            string_value=user_pool.user_pool_arn,
            tier=ssm.ParameterTier.STANDARD,
        )

        return user_pool
