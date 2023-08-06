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

import aws_cdk.aws_codebuild as _aws_cdk_aws_codebuild_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import constructs as _constructs_77d1e7e8
from ..ec2 import (
    IIpamPool as _IIpamPool_511f311d, ITransitGateway as _ITransitGateway_25936657
)
from ..ram import ISharable as _ISharable_ffb95c3b


@jsii.implements(_ISharable_ffb95c3b)
class SharedResource(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.ram_resources.SharedResource",
):
    @jsii.member(jsii_name="fromArn")
    @builtins.classmethod
    def from_arn(cls, arn: builtins.str) -> "SharedResource":
        '''
        :param arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82c6e68eec0de5fca8b463c5c3b7112ef4274e8a16b3014e8a2df4d8a4578c1c)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SharedResource", jsii.sinvoke(cls, "fromArn", [arn]))

    @jsii.member(jsii_name="fromIpamPool")
    @builtins.classmethod
    def from_ipam_pool(cls, pool: _IIpamPool_511f311d) -> "SharedResource":
        '''
        :param pool: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0576f61062c11fb38035ae71969f2682c71bdc34133398b8aba999ac1f962ff1)
            check_type(argname="argument pool", value=pool, expected_type=type_hints["pool"])
        return typing.cast("SharedResource", jsii.sinvoke(cls, "fromIpamPool", [pool]))

    @jsii.member(jsii_name="fromProject")
    @builtins.classmethod
    def from_project(
        cls,
        project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
    ) -> "SharedResource":
        '''
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d1ebb15d9bdd6b5f747b43f752477c8deb4e9208a4c3ad912068a1cca90157)
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast("SharedResource", jsii.sinvoke(cls, "fromProject", [project]))

    @jsii.member(jsii_name="fromSubnet")
    @builtins.classmethod
    def from_subnet(cls, subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet) -> "SharedResource":
        '''
        :param subnet: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eccc4e2a5f9de8aa2100dd8c9e5bdd1c9875ad5f0fc8c5682dfc595819e80648)
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        return typing.cast("SharedResource", jsii.sinvoke(cls, "fromSubnet", [subnet]))

    @jsii.member(jsii_name="fromTransitGateway")
    @builtins.classmethod
    def from_transit_gateway(
        cls,
        transit_gateway: _ITransitGateway_25936657,
    ) -> "SharedResource":
        '''
        :param transit_gateway: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a326a54062f4ec237617554f76fc2b00dd1686bbee27e878c2531f30507041e)
            check_type(argname="argument transit_gateway", value=transit_gateway, expected_type=type_hints["transit_gateway"])
        return typing.cast("SharedResource", jsii.sinvoke(cls, "fromTransitGateway", [transit_gateway]))

    @jsii.member(jsii_name="share")
    def share(self, _scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''Configures resource sharing for the associated resource.

        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7919681af13ea8bd7512ef57b923e7175d0a26f2d28aa004ff412c9cc732c841)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(builtins.str, jsii.invoke(self, "share", [_scope]))


__all__ = [
    "SharedResource",
]

publication.publish()

def _typecheckingstub__82c6e68eec0de5fca8b463c5c3b7112ef4274e8a16b3014e8a2df4d8a4578c1c(
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0576f61062c11fb38035ae71969f2682c71bdc34133398b8aba999ac1f962ff1(
    pool: _IIpamPool_511f311d,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d1ebb15d9bdd6b5f747b43f752477c8deb4e9208a4c3ad912068a1cca90157(
    project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eccc4e2a5f9de8aa2100dd8c9e5bdd1c9875ad5f0fc8c5682dfc595819e80648(
    subnet: _aws_cdk_aws_ec2_ceddda9d.ISubnet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a326a54062f4ec237617554f76fc2b00dd1686bbee27e878c2531f30507041e(
    transit_gateway: _ITransitGateway_25936657,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7919681af13ea8bd7512ef57b923e7175d0a26f2d28aa004ff412c9cc732c841(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass
