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

import aws_cdk.assertions as _aws_cdk_assertions_ceddda9d


class JoinedJson(
    _aws_cdk_assertions_ceddda9d.Matcher,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.asserts.JoinedJson",
):
    def __init__(self, pattern: typing.Any) -> None:
        '''
        :param pattern: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a613ff7ce33e96575f12d8bf718be54231fe72fc308dc394ad6cf5276e50682e)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        jsii.create(self.__class__, self, [pattern])

    @jsii.member(jsii_name="test")
    def test(self, actual: typing.Any) -> _aws_cdk_assertions_ceddda9d.MatchResult:
        '''Test whether a target matches the provided pattern.

        Every Matcher must implement this method.
        This method will be invoked by the assertions framework. Do not call this method directly.

        :param actual: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e48f1cba62bf1f2442ff386fa62a13a3a15ebb93a268386458ba08508c8f483)
            check_type(argname="argument actual", value=actual, expected_type=type_hints["actual"])
        return typing.cast(_aws_cdk_assertions_ceddda9d.MatchResult, jsii.invoke(self, "test", [actual]))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''A name for the matcher.

        This is collected as part of the result and may be presented to the user.
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))


class Match(
    _aws_cdk_assertions_ceddda9d.Match,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.asserts.Match",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="joinedJson")
    @builtins.classmethod
    def joined_json(cls, pattern: typing.Any) -> _aws_cdk_assertions_ceddda9d.Matcher:
        '''
        :param pattern: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0ee524ca5b8f9098f4df7d5afe1174da54ca48cff127e60f1176ee915ac4b50)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast(_aws_cdk_assertions_ceddda9d.Matcher, jsii.sinvoke(cls, "joinedJson", [pattern]))


__all__ = [
    "JoinedJson",
    "Match",
]

publication.publish()

def _typecheckingstub__a613ff7ce33e96575f12d8bf718be54231fe72fc308dc394ad6cf5276e50682e(
    pattern: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e48f1cba62bf1f2442ff386fa62a13a3a15ebb93a268386458ba08508c8f483(
    actual: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0ee524ca5b8f9098f4df7d5afe1174da54ca48cff127e60f1176ee915ac4b50(
    pattern: typing.Any,
) -> None:
    """Type checking stubs"""
    pass
