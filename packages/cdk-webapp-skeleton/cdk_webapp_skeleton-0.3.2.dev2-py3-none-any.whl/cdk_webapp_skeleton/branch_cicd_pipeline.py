import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_s3 as s3
from aws_cdk import pipelines as pipelines
from constructs import Construct

from .branch_config import BranchConfig


class BranchCICDPipeline(Construct):
    def __init__(self, scope: Construct, branch_config: BranchConfig):
        super().__init__(scope, "BranchCICDPipeline")

        cache_bucket = s3.Bucket(
            scope,
            "CacheBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        synth_step = pipelines.ShellStep(
            "Synth",
            input=branch_config.source,
            env={
                "BRANCH": branch_config.branch_name,
            },
            commands=["./synth.sh"],
        )

        self.cdk_pipeline = pipelines.CodePipeline(
            scope,
            "Pipeline",  # Pipeline name gets the stack name prepended
            synth=synth_step,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.SMALL
                ),
                cache=codebuild.Cache.bucket(cache_bucket),
            ),
            cross_account_keys=False,
            publish_assets_in_parallel=False,
        )

    def add_stage(self, stage: cdk.Stage) -> pipelines.StageDeployment:
        return self.cdk_pipeline.add_stage(stage)

    def build_pipeline(self):
        self.cdk_pipeline.build_pipeline()
