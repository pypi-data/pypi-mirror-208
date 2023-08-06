import abc
from abc import ABC
from typing import Optional

from aws_cdk import aws_route53 as route53
from aws_cdk import pipelines as pipelines
from constructs import Construct


class BranchConfig(ABC):
    def __init__(self, branch_name):
        """

        :param branch_name:
        """
        domain = branch_name.replace("_", "-")
        self._env_name = "Prod" if branch_name == self.main_branch_name else domain
        self._branch_name = branch_name
        self._domain_prefix = (
            "" if branch_name == self.main_branch_name else f"{domain}."
        )

    @property
    @abc.abstractmethod
    def domain_name_base(self) -> Optional[str]:
        ...

    @property
    @abc.abstractmethod
    def source(self) -> pipelines.CodePipelineSource:
        ...

    @abc.abstractmethod
    def get_hosted_zone(self, scope: Construct) -> Optional[route53.IHostedZone]:
        ...

    @property
    def main_branch_name(self) -> str:
        return "main"

    @classmethod
    def from_branch_name(cls, branch_name):
        return cls(branch_name)

    @property
    def branch_name(self):
        return self._branch_name

    def construct_id(self, id_: str):
        """
        Contextualizes constructs by environment.
        :param id_: construct id
        :return: ConstructId prefixed by the environment name (either "Prod" or branch name)
        """
        return f"{self._env_name}{id_}"

    def auth_stack_name(self) -> Optional[str]:
        """

        :return: Fixed Auth stack name or None.
        """
        return "AuthStack" if self._branch_name == self.main_branch_name else None

    @property
    def build_user_pool(self):
        return self._branch_name == self.main_branch_name

    @property
    def domain_name(self):
        return f"{self._domain_prefix}{self.domain_name_base}"

    @property
    def auth_domain_name(self):
        return f"auth.{self.domain_name_base}"

    @property
    def notify_email(self) -> Optional[str]:
        """Email address to send deploy and alarm notifications to."""
        return None
