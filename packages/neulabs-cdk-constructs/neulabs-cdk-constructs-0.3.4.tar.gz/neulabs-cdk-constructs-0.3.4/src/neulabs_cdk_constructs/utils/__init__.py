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


@jsii.data_type(
    jsii_type="neulabs-cdk-constructs.utils.BaseTagProps",
    jsii_struct_bases=[],
    name_mapping={
        "business_unit": "businessUnit",
        "domain": "domain",
        "repository_name": "repositoryName",
        "repository_version": "repositoryVersion",
    },
)
class BaseTagProps:
    def __init__(
        self,
        *,
        business_unit: typing.Optional[builtins.str] = None,
        domain: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        repository_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param business_unit: 
        :param domain: 
        :param repository_name: 
        :param repository_version: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f59f73fdaf30660375badd7563a2c88d571a3f3c13954be279edbfc5e101a01f)
            check_type(argname="argument business_unit", value=business_unit, expected_type=type_hints["business_unit"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument repository_version", value=repository_version, expected_type=type_hints["repository_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if business_unit is not None:
            self._values["business_unit"] = business_unit
        if domain is not None:
            self._values["domain"] = domain
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if repository_version is not None:
            self._values["repository_version"] = repository_version

    @builtins.property
    def business_unit(self) -> typing.Optional[builtins.str]:
        result = self._values.get("business_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("repository_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseTagProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="neulabs-cdk-constructs.utils.TagsKey")
class TagsKey(enum.Enum):
    ENVIRONMENT = "ENVIRONMENT"
    TIMESTAMP_DEPLOY_CDK = "TIMESTAMP_DEPLOY_CDK"
    BUSINESS_UNIT = "BUSINESS_UNIT"
    DOMAIN = "DOMAIN"
    REPOSITORY_NAME = "REPOSITORY_NAME"
    REPOSITORY_VERSION = "REPOSITORY_VERSION"


__all__ = [
    "BaseTagProps",
    "TagsKey",
]

publication.publish()

def _typecheckingstub__f59f73fdaf30660375badd7563a2c88d571a3f3c13954be279edbfc5e101a01f(
    *,
    business_unit: typing.Optional[builtins.str] = None,
    domain: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    repository_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
