import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8
from ..stack import (
    BaseStack as _BaseStack_8603347c, BaseStackProps as _BaseStackProps_bfec638c
)


class GithubOIDCStack(
    _BaseStack_8603347c,
    metaclass=jsii.JSIIMeta,
    jsii_type="neulabs-cdk-constructs.oidc.GithubOIDCStack",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        github_repository: builtins.str,
        github_user: builtins.str,
        token_action: "TokenActions",
        cdk_bootstrap_role_name: typing.Optional[builtins.str] = None,
        cdk_deploy_role_aws_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_deploy_role_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_deploy_role_name: typing.Optional[builtins.str] = None,
        cdk_deploy_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        oidc_role_name: typing.Optional[builtins.str] = None,
        token_action_custom: typing.Optional[builtins.str] = None,
        stage: builtins.str,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param github_repository: 
        :param github_user: 
        :param token_action: 
        :param cdk_bootstrap_role_name: 
        :param cdk_deploy_role_aws_managed_policies: 
        :param cdk_deploy_role_managed_policies: 
        :param cdk_deploy_role_name: 
        :param cdk_deploy_role_policy_statements: 
        :param oidc_role_name: 
        :param token_action_custom: 
        :param stage: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71fabbd315f27662df384897235533205fa1984af573f69ade1128bc72da169d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GithubOIDCStackStackProps(
            github_repository=github_repository,
            github_user=github_user,
            token_action=token_action,
            cdk_bootstrap_role_name=cdk_bootstrap_role_name,
            cdk_deploy_role_aws_managed_policies=cdk_deploy_role_aws_managed_policies,
            cdk_deploy_role_managed_policies=cdk_deploy_role_managed_policies,
            cdk_deploy_role_name=cdk_deploy_role_name,
            cdk_deploy_role_policy_statements=cdk_deploy_role_policy_statements,
            oidc_role_name=oidc_role_name,
            token_action_custom=token_action_custom,
            stage=stage,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createCdkBootstrapRole")
    def create_cdk_bootstrap_role(
        self,
        role_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''
        :param role_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7435c95806e36818a64c38633e8ce59dec0d4ed44b9da5cc643d8fc571164011)
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.invoke(self, "createCdkBootstrapRole", [role_name]))

    @jsii.member(jsii_name="createCdkDeployRole")
    def create_cdk_deploy_role(
        self,
        role_name: typing.Optional[builtins.str] = None,
        managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        aws_managed_policy: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''
        :param role_name: -
        :param managed_policies: -
        :param aws_managed_policy: -
        :param policy_statements: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38a804dad69a7e88a361d5bccc16731b0a29b939ca83b1a6ef43cd272245e971)
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument aws_managed_policy", value=aws_managed_policy, expected_type=type_hints["aws_managed_policy"])
            check_type(argname="argument policy_statements", value=policy_statements, expected_type=type_hints["policy_statements"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.invoke(self, "createCdkDeployRole", [role_name, managed_policies, aws_managed_policy, policy_statements]))

    @jsii.member(jsii_name="createOidcRole")
    def create_oidc_role(
        self,
        provider_url: builtins.str,
        token: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''
        :param provider_url: -
        :param token: -
        :param role_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3ff2f52a754bcc8ac66171d89cb70ca23ceedd5d32cd487bb12f17483fa9054)
            check_type(argname="argument provider_url", value=provider_url, expected_type=type_hints["provider_url"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.invoke(self, "createOidcRole", [provider_url, token, role_name]))

    @jsii.member(jsii_name="createTokenAction")
    def create_token_action(
        self,
        token_action: "TokenActions",
        github_user: builtins.str,
        github_repository: builtins.str,
        token_action_custom: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''
        :param token_action: -
        :param github_user: -
        :param github_repository: -
        :param token_action_custom: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3344037305683895c810bcace91c4aeb8caf295f9d93a6b912f0c80d5ccc69a)
            check_type(argname="argument token_action", value=token_action, expected_type=type_hints["token_action"])
            check_type(argname="argument github_user", value=github_user, expected_type=type_hints["github_user"])
            check_type(argname="argument github_repository", value=github_repository, expected_type=type_hints["github_repository"])
            check_type(argname="argument token_action_custom", value=token_action_custom, expected_type=type_hints["token_action_custom"])
        return typing.cast(builtins.str, jsii.invoke(self, "createTokenAction", [token_action, github_user, github_repository, token_action_custom]))

    @builtins.property
    @jsii.member(jsii_name="cdkBootstrapRole")
    def cdk_bootstrap_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "cdkBootstrapRole"))

    @cdk_bootstrap_role.setter
    def cdk_bootstrap_role(self, value: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d03b4657acfbe01f82348279990243fc398f96a4aead89b130a2bbd97b9a640c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cdkBootstrapRole", value)

    @builtins.property
    @jsii.member(jsii_name="cdkDeployRole")
    def cdk_deploy_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "cdkDeployRole"))

    @cdk_deploy_role.setter
    def cdk_deploy_role(self, value: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaf8b5f41f94e8d3bced0204d4fd7e5884aea6f192876268da6de7a620825908)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cdkDeployRole", value)

    @builtins.property
    @jsii.member(jsii_name="githubRepository")
    def github_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "githubRepository"))

    @github_repository.setter
    def github_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fadc1042dd9e4b7857fa25f0a4fbc168efe7860074e61c8cd8cc2592bd5de4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubRepository", value)

    @builtins.property
    @jsii.member(jsii_name="githubUser")
    def github_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "githubUser"))

    @github_user.setter
    def github_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e9d5202f45acf031df1e81c3020e1f010e57d1d39dff59eca6ce51a26e02791)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubUser", value)

    @builtins.property
    @jsii.member(jsii_name="oidcRole")
    def oidc_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "oidcRole"))

    @oidc_role.setter
    def oidc_role(self, value: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07e76d2f21f74572cf409524582bcce2357678180aeb43e8ecfd1043bcb3f210)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcRole", value)

    @builtins.property
    @jsii.member(jsii_name="tokenAction")
    def token_action(self) -> "TokenActions":
        return typing.cast("TokenActions", jsii.get(self, "tokenAction"))

    @token_action.setter
    def token_action(self, value: "TokenActions") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bd4e27b23fafc5b18640f9f3bcb5f8d377178e9ee818017fc064e45c9ffe9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenAction", value)

    @builtins.property
    @jsii.member(jsii_name="cdkDeployRoleAwsManagedPolicies")
    def cdk_deploy_role_aws_managed_policies(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cdkDeployRoleAwsManagedPolicies"))

    @cdk_deploy_role_aws_managed_policies.setter
    def cdk_deploy_role_aws_managed_policies(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118110011a00e54769ad26aae3f4147ce2a03b30a6a1767adf34ab290769ae94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cdkDeployRoleAwsManagedPolicies", value)

    @builtins.property
    @jsii.member(jsii_name="cdkDeployRoleManagedPolicies")
    def cdk_deploy_role_managed_policies(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cdkDeployRoleManagedPolicies"))

    @cdk_deploy_role_managed_policies.setter
    def cdk_deploy_role_managed_policies(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb7c5799447871d7244ed8f819a93a50ee2bdf4efa6b5632a166e6328dcb9e42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cdkDeployRoleManagedPolicies", value)

    @builtins.property
    @jsii.member(jsii_name="cdkDeployRolePolicyStatements")
    def cdk_deploy_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], jsii.get(self, "cdkDeployRolePolicyStatements"))

    @cdk_deploy_role_policy_statements.setter
    def cdk_deploy_role_policy_statements(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee7947bb0d3c0b596daf1087e748fb7729130cd41bc163bb8d67823f75c6a075)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cdkDeployRolePolicyStatements", value)


@jsii.data_type(
    jsii_type="neulabs-cdk-constructs.oidc.GithubOIDCStackStackProps",
    jsii_struct_bases=[_BaseStackProps_bfec638c],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "permissions_boundary": "permissionsBoundary",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "stage": "stage",
        "github_repository": "githubRepository",
        "github_user": "githubUser",
        "token_action": "tokenAction",
        "cdk_bootstrap_role_name": "cdkBootstrapRoleName",
        "cdk_deploy_role_aws_managed_policies": "cdkDeployRoleAwsManagedPolicies",
        "cdk_deploy_role_managed_policies": "cdkDeployRoleManagedPolicies",
        "cdk_deploy_role_name": "cdkDeployRoleName",
        "cdk_deploy_role_policy_statements": "cdkDeployRolePolicyStatements",
        "oidc_role_name": "oidcRoleName",
        "token_action_custom": "tokenActionCustom",
    },
)
class GithubOIDCStackStackProps(_BaseStackProps_bfec638c):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        stage: builtins.str,
        github_repository: builtins.str,
        github_user: builtins.str,
        token_action: "TokenActions",
        cdk_bootstrap_role_name: typing.Optional[builtins.str] = None,
        cdk_deploy_role_aws_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_deploy_role_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        cdk_deploy_role_name: typing.Optional[builtins.str] = None,
        cdk_deploy_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        oidc_role_name: typing.Optional[builtins.str] = None,
        token_action_custom: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param stage: 
        :param github_repository: 
        :param github_user: 
        :param token_action: 
        :param cdk_bootstrap_role_name: 
        :param cdk_deploy_role_aws_managed_policies: 
        :param cdk_deploy_role_managed_policies: 
        :param cdk_deploy_role_name: 
        :param cdk_deploy_role_policy_statements: 
        :param oidc_role_name: 
        :param token_action_custom: 
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81f6128649596f1f89adf6d54553924e5a8f7172f0dbfd21eefa659cb4adb68d)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument github_repository", value=github_repository, expected_type=type_hints["github_repository"])
            check_type(argname="argument github_user", value=github_user, expected_type=type_hints["github_user"])
            check_type(argname="argument token_action", value=token_action, expected_type=type_hints["token_action"])
            check_type(argname="argument cdk_bootstrap_role_name", value=cdk_bootstrap_role_name, expected_type=type_hints["cdk_bootstrap_role_name"])
            check_type(argname="argument cdk_deploy_role_aws_managed_policies", value=cdk_deploy_role_aws_managed_policies, expected_type=type_hints["cdk_deploy_role_aws_managed_policies"])
            check_type(argname="argument cdk_deploy_role_managed_policies", value=cdk_deploy_role_managed_policies, expected_type=type_hints["cdk_deploy_role_managed_policies"])
            check_type(argname="argument cdk_deploy_role_name", value=cdk_deploy_role_name, expected_type=type_hints["cdk_deploy_role_name"])
            check_type(argname="argument cdk_deploy_role_policy_statements", value=cdk_deploy_role_policy_statements, expected_type=type_hints["cdk_deploy_role_policy_statements"])
            check_type(argname="argument oidc_role_name", value=oidc_role_name, expected_type=type_hints["oidc_role_name"])
            check_type(argname="argument token_action_custom", value=token_action_custom, expected_type=type_hints["token_action_custom"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stage": stage,
            "github_repository": github_repository,
            "github_user": github_user,
            "token_action": token_action,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if cdk_bootstrap_role_name is not None:
            self._values["cdk_bootstrap_role_name"] = cdk_bootstrap_role_name
        if cdk_deploy_role_aws_managed_policies is not None:
            self._values["cdk_deploy_role_aws_managed_policies"] = cdk_deploy_role_aws_managed_policies
        if cdk_deploy_role_managed_policies is not None:
            self._values["cdk_deploy_role_managed_policies"] = cdk_deploy_role_managed_policies
        if cdk_deploy_role_name is not None:
            self._values["cdk_deploy_role_name"] = cdk_deploy_role_name
        if cdk_deploy_role_policy_statements is not None:
            self._values["cdk_deploy_role_policy_statements"] = cdk_deploy_role_policy_statements
        if oidc_role_name is not None:
            self._values["oidc_role_name"] = oidc_role_name
        if token_action_custom is not None:
            self._values["token_action_custom"] = token_action_custom

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stage(self) -> builtins.str:
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def github_repository(self) -> builtins.str:
        result = self._values.get("github_repository")
        assert result is not None, "Required property 'github_repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def github_user(self) -> builtins.str:
        result = self._values.get("github_user")
        assert result is not None, "Required property 'github_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token_action(self) -> "TokenActions":
        result = self._values.get("token_action")
        assert result is not None, "Required property 'token_action' is missing"
        return typing.cast("TokenActions", result)

    @builtins.property
    def cdk_bootstrap_role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("cdk_bootstrap_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_deploy_role_aws_managed_policies(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("cdk_deploy_role_aws_managed_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_deploy_role_managed_policies(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("cdk_deploy_role_managed_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cdk_deploy_role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("cdk_deploy_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk_deploy_role_policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        result = self._values.get("cdk_deploy_role_policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def oidc_role_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("oidc_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_action_custom(self) -> typing.Optional[builtins.str]:
        result = self._values.get("token_action_custom")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubOIDCStackStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="neulabs-cdk-constructs.oidc.ProviderUrl")
class ProviderUrl(enum.Enum):
    GITHUB = "GITHUB"


@jsii.enum(jsii_type="neulabs-cdk-constructs.oidc.TokenActions")
class TokenActions(enum.Enum):
    ALL = "ALL"
    ALL_BRANCH = "ALL_BRANCH"
    ALL_TAGS = "ALL_TAGS"
    ONLY_MAIN = "ONLY_MAIN"
    CUSTOM = "CUSTOM"


__all__ = [
    "GithubOIDCStack",
    "GithubOIDCStackStackProps",
    "ProviderUrl",
    "TokenActions",
]

publication.publish()

def _typecheckingstub__71fabbd315f27662df384897235533205fa1984af573f69ade1128bc72da169d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    github_repository: builtins.str,
    github_user: builtins.str,
    token_action: TokenActions,
    cdk_bootstrap_role_name: typing.Optional[builtins.str] = None,
    cdk_deploy_role_aws_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_deploy_role_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_deploy_role_name: typing.Optional[builtins.str] = None,
    cdk_deploy_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    oidc_role_name: typing.Optional[builtins.str] = None,
    token_action_custom: typing.Optional[builtins.str] = None,
    stage: builtins.str,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7435c95806e36818a64c38633e8ce59dec0d4ed44b9da5cc643d8fc571164011(
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38a804dad69a7e88a361d5bccc16731b0a29b939ca83b1a6ef43cd272245e971(
    role_name: typing.Optional[builtins.str] = None,
    managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    aws_managed_policy: typing.Optional[typing.Sequence[builtins.str]] = None,
    policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ff2f52a754bcc8ac66171d89cb70ca23ceedd5d32cd487bb12f17483fa9054(
    provider_url: builtins.str,
    token: builtins.str,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3344037305683895c810bcace91c4aeb8caf295f9d93a6b912f0c80d5ccc69a(
    token_action: TokenActions,
    github_user: builtins.str,
    github_repository: builtins.str,
    token_action_custom: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d03b4657acfbe01f82348279990243fc398f96a4aead89b130a2bbd97b9a640c(
    value: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaf8b5f41f94e8d3bced0204d4fd7e5884aea6f192876268da6de7a620825908(
    value: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fadc1042dd9e4b7857fa25f0a4fbc168efe7860074e61c8cd8cc2592bd5de4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9d5202f45acf031df1e81c3020e1f010e57d1d39dff59eca6ce51a26e02791(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e76d2f21f74572cf409524582bcce2357678180aeb43e8ecfd1043bcb3f210(
    value: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd4e27b23fafc5b18640f9f3bcb5f8d377178e9ee818017fc064e45c9ffe9cb(
    value: TokenActions,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118110011a00e54769ad26aae3f4147ce2a03b30a6a1767adf34ab290769ae94(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7c5799447871d7244ed8f819a93a50ee2bdf4efa6b5632a166e6328dcb9e42(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee7947bb0d3c0b596daf1087e748fb7729130cd41bc163bb8d67823f75c6a075(
    value: typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81f6128649596f1f89adf6d54553924e5a8f7172f0dbfd21eefa659cb4adb68d(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    stage: builtins.str,
    github_repository: builtins.str,
    github_user: builtins.str,
    token_action: TokenActions,
    cdk_bootstrap_role_name: typing.Optional[builtins.str] = None,
    cdk_deploy_role_aws_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_deploy_role_managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    cdk_deploy_role_name: typing.Optional[builtins.str] = None,
    cdk_deploy_role_policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    oidc_role_name: typing.Optional[builtins.str] = None,
    token_action_custom: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
