from typing import Mapping, Optional, Sequence

import aws_cdk as cdk
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from aws_cdk import pipelines
from cloudcomponents.cdk_static_website import StaticWebsite
from constructs import Construct

from .branch_config import BranchConfig

FRONTEND_DEPLOY_ROLE_ARN_PARAM = "FrontendBundleDeployRoleArn"


class ReactWebsite(Construct):
    def __init__(
        self, scope: "Construct", construct_id: str, branch_config: BranchConfig
    ):
        super().__init__(scope, construct_id)

        root_hosted_zone = branch_config.get_hosted_zone(scope)

        static_website = StaticWebsite(
            scope,
            "Frontend",
            hosted_zone=root_hosted_zone,
            domain_names=[
                branch_config.domain_name,
                "www." + branch_config.domain_name,
            ],
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
            security_headers_behavior=cloudfront.ResponseSecurityHeadersBehavior(
                content_security_policy=cloudfront.ResponseHeadersContentSecurityPolicy(
                    content_security_policy="default-src 'self'; img-src 'self'; script-src 'self' https: ; "
                    "style-src 'self' 'unsafe-inline' https: ; font-src 'self' data:; "
                    f"object-src 'none'; connect-src 'self' *.{branch_config.domain_name} "
                    f"cognito-idp.us-east-1.amazonaws.com {branch_config.auth_domain_name}",
                    override=True,
                )
            ),
            disable_upload=True,  # deployment is done separately, from the frontend build
        )

        deploy_role_arn = ssm.StringParameter.value_for_string_parameter(
            scope,
            parameter_name=branch_config.construct_id(FRONTEND_DEPLOY_ROLE_ARN_PARAM),
        )
        deploy_role = iam.Role.from_role_arn(scope, "BundleDeployRole", deploy_role_arn)
        static_website.bucket.grant_read_write(deploy_role)

        self.website_bucket_name = cdk.CfnOutput(
            scope, "WebsiteBucketName", value=static_website.bucket.bucket_name
        )
        self.cloudfront_distribution_id = cdk.CfnOutput(
            scope,
            "WebsiteDistribution",
            value=static_website.distribution.distribution_id,
        )


class WebsiteDeployStep(Construct):
    def __init__(
        self,
        scope: "Construct",
        construct_id: str,
        branch_config: BranchConfig,
        commands: Sequence[str],
        env_from_cfn_outputs=Optional[Mapping[str, cdk.CfnOutput]],
    ):
        super().__init__(scope, construct_id)

        bundle_deploy_role = iam.Role(
            scope,
            branch_config.construct_id("FrontendBundleDeployRole"),
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            inline_policies={
                "AllowCloudFrontInvalidation": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["cloudfront:CreateInvalidation"],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        )
                    ]
                )
            },
        )
        ssm.StringParameter(
            scope,
            branch_config.construct_id("FrontendBundleDeployRoleArnParameter"),
            description="The ARN of the role that is used to deploy the frontend bundle into the S3 bucket.",
            parameter_name=branch_config.construct_id(FRONTEND_DEPLOY_ROLE_ARN_PARAM),
            string_value=bundle_deploy_role.role_arn,
            tier=ssm.ParameterTier.STANDARD,
        )
        # TODO Consider replacing it with a higher-level abstraction like FileAsset or something? So that we aren't
        #  describing build steps here.
        self.code_build_step = pipelines.CodeBuildStep(
            "BuildFrontend",
            input=branch_config.source,
            commands=commands,
            env_from_cfn_outputs=env_from_cfn_outputs,
            env={
                "AUTH_DOMAIN_NAME": branch_config.auth_domain_name,
                "DOMAIN_NAME": branch_config.domain_name,
            },
            role=bundle_deploy_role,
        )
