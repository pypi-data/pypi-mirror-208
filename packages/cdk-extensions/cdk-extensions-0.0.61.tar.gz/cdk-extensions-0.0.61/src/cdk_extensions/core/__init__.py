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

import constructs as _constructs_77d1e7e8


class DataSize(metaclass=jsii.JSIIMeta, jsii_type="cdk-extensions.core.DataSize"):
    @jsii.member(jsii_name="bytes")
    @builtins.classmethod
    def bytes(cls, bytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of bytes.

        :param bytes: The number of bytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of bytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9f8028b9df6cecb71705d69960039e03fa9e4095a8366346d67d0018eba56b)
            check_type(argname="argument bytes", value=bytes, expected_type=type_hints["bytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "bytes", [bytes]))

    @jsii.member(jsii_name="gibibytes")
    @builtins.classmethod
    def gibibytes(cls, gibibytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of gibibytes.

        :param gibibytes: The number of gibibytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of gibibytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f94a313e7517e3248b9269dee52f9add5c947249a5922cbd8848af09f78d67a)
            check_type(argname="argument gibibytes", value=gibibytes, expected_type=type_hints["gibibytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "gibibytes", [gibibytes]))

    @jsii.member(jsii_name="gigabytes")
    @builtins.classmethod
    def gigabytes(cls, gigabytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of gigabytes.

        :param gigabytes: The number of gigabytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of gigabytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9671e763fd6866b0fadfdc37f12f32076b1a3c0eb1e6c8c44a98d18d705ea84)
            check_type(argname="argument gigabytes", value=gigabytes, expected_type=type_hints["gigabytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "gigabytes", [gigabytes]))

    @jsii.member(jsii_name="kibibytes")
    @builtins.classmethod
    def kibibytes(cls, kibibytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of kibibytes.

        :param kibibytes: The number of kibibytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of kibibytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5b6bef5d79ca1256cc7bb00906e642cd3b2e20a12b9e6d6a167a61a90b9226d)
            check_type(argname="argument kibibytes", value=kibibytes, expected_type=type_hints["kibibytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "kibibytes", [kibibytes]))

    @jsii.member(jsii_name="kilobytes")
    @builtins.classmethod
    def kilobytes(cls, kilobytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of kilobytes.

        :param kilobytes: The number of kilobytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of kilobytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c94d834fb141b951612c01011b4f5aa439864f5ce2ae7abdbc3193647cb674)
            check_type(argname="argument kilobytes", value=kilobytes, expected_type=type_hints["kilobytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "kilobytes", [kilobytes]))

    @jsii.member(jsii_name="mebibytes")
    @builtins.classmethod
    def mebibytes(cls, mebibytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of mebibytes.

        :param mebibytes: The number of mebibytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of mebibytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efeefc197c919d59ac34d36fa74acf9e7d8dd02726f7c7d3efa1c41934c442ae)
            check_type(argname="argument mebibytes", value=mebibytes, expected_type=type_hints["mebibytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "mebibytes", [mebibytes]))

    @jsii.member(jsii_name="megabytes")
    @builtins.classmethod
    def megabytes(cls, megabytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of megabytes.

        :param megabytes: The number of megabytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of megabytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba0e534201cb35600e74c0127e594c357a205baae2a7ca5e219e86519d724436)
            check_type(argname="argument megabytes", value=megabytes, expected_type=type_hints["megabytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "megabytes", [megabytes]))

    @jsii.member(jsii_name="pebibytes")
    @builtins.classmethod
    def pebibytes(cls, pebibytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of pebibytes.

        :param pebibytes: The number of pebibytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of pebibytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58df2f97fe7cd00e39848c2e503d47b97ddc84419ee92b27027b37a33e0726e4)
            check_type(argname="argument pebibytes", value=pebibytes, expected_type=type_hints["pebibytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "pebibytes", [pebibytes]))

    @jsii.member(jsii_name="petabytes")
    @builtins.classmethod
    def petabytes(cls, petabytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of petabytes.

        :param petabytes: The number of petabytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of petabytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cd6affb76d41d4c55a0ec1b18ac8ef79ac06717362bec8d544a653c2d8dd7c2)
            check_type(argname="argument petabytes", value=petabytes, expected_type=type_hints["petabytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "petabytes", [petabytes]))

    @jsii.member(jsii_name="tebibytes")
    @builtins.classmethod
    def tebibytes(cls, tebibytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of tebibytes.

        :param tebibytes: The number of tebibytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of tebibytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85dbc9806ab6c89dd5e9acba67ba9df2bf3df8fe9d7945b51f2a2bcdbdf6666f)
            check_type(argname="argument tebibytes", value=tebibytes, expected_type=type_hints["tebibytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "tebibytes", [tebibytes]))

    @jsii.member(jsii_name="terabytes")
    @builtins.classmethod
    def terabytes(cls, terabytes: jsii.Number) -> "DataSize":
        '''Create a ``DataSize`` representing an amount of terabytes.

        :param terabytes: The number of terabytes this ``DataSize`` will represent.

        :return: A ``DataSize`` representing the specified number of terabytes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8ef754d3db22071d621691377690e190f31f885f5a6de57a65eb27e715b2a58)
            check_type(argname="argument terabytes", value=terabytes, expected_type=type_hints["terabytes"])
        return typing.cast("DataSize", jsii.sinvoke(cls, "terabytes", [terabytes]))

    @jsii.member(jsii_name="toBytes")
    def to_bytes(self) -> jsii.Number:
        '''Convert the DataSize object to the byte representation.

        :return: The number of bytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toBytes", []))

    @jsii.member(jsii_name="toGibibytes")
    def to_gibibytes(self) -> jsii.Number:
        '''Convert the DataSize object to its gibibyte representation.

        If the data size doesn't fit evently into gibibytes it will be rounded
        up to the closest gibibyte which will be required to hold all the data.

        :return: The number of gibibytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toGibibytes", []))

    @jsii.member(jsii_name="toGigabytes")
    def to_gigabytes(self) -> jsii.Number:
        '''Convert the DataSize object to its gigabyte representation.

        If the data size doesn't fit evently into gigabytes it will be rounded
        up to the closest gigabyte which will be required to hold all the data.

        :return: The number of gigabytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toGigabytes", []))

    @jsii.member(jsii_name="toKibibytes")
    def to_kibibytes(self) -> jsii.Number:
        '''Convert the DataSize object to its kibibyte representation.

        If the data size doesn't fit evently into kibibytes it will be rounded
        up to the closest kibibyte which will be required to hold all the data.

        :return: The number of kibibytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toKibibytes", []))

    @jsii.member(jsii_name="toKilobytes")
    def to_kilobytes(self) -> jsii.Number:
        '''Convert the DataSize object to its kilobyte representation.

        If the data size doesn't fit evently into kilobytes it will be rounded
        up to the closest kilobyte which will be required to hold all the data.

        :return: The number of kilobytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toKilobytes", []))

    @jsii.member(jsii_name="toMebibytes")
    def to_mebibytes(self) -> jsii.Number:
        '''Convert the DataSize object to its mebibyte representation.

        If the data size doesn't fit evently into mebibytes it will be rounded
        up to the closest mebibyte which will be required to hold all the data.

        :return: The number of mebibytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toMebibytes", []))

    @jsii.member(jsii_name="toMegabytes")
    def to_megabytes(self) -> jsii.Number:
        '''Convert the DataSize object to its megabyte representation.

        If the data size doesn't fit evently into megabytes it will be rounded
        up to the closest megabyte which will be required to hold all the data.

        :return: The number of megabytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toMegabytes", []))

    @jsii.member(jsii_name="toPebibytes")
    def to_pebibytes(self) -> jsii.Number:
        '''Convert the DataSize object to its pebibyte representation.

        If the data size doesn't fit evently into pebibytes it will be rounded
        up to the closest pebibyte which will be required to hold all the data.

        :return: The number of pebibytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toPebibytes", []))

    @jsii.member(jsii_name="toPetabytes")
    def to_petabytes(self) -> jsii.Number:
        '''Convert the DataSize object to its petabyte representation.

        If the data size doesn't fit evently into petabytes it will be rounded
        up to the closest petabyte which will be required to hold all the data.

        :return: The number of petabytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toPetabytes", []))

    @jsii.member(jsii_name="toTebibytes")
    def to_tebibytes(self) -> jsii.Number:
        '''Convert the DataSize object to its tebibyte representation.

        If the data size doesn't fit evently into tebibytes it will be rounded
        up to the closest tebibyte which will be required to hold all the data.

        :return: The number of tebibytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toTebibytes", []))

    @jsii.member(jsii_name="toTerabytes")
    def to_terabytes(self) -> jsii.Number:
        '''Convert the DataSize object to its terabyte representation.

        If the data size doesn't fit evently into terabytes it will be rounded
        up to the closest terabyte which will be required to hold all the data.

        :return: The number of terabytes for the data size.
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "toTerabytes", []))


class SecretReference(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.core.SecretReference",
):
    @jsii.member(jsii_name="string")
    @builtins.classmethod
    def string(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        key: builtins.str,
        value: builtins.str,
    ) -> builtins.str:
        '''
        :param scope: -
        :param key: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd4b34a78fd0292690f71372b5fb13734a651aa94133c7764eb1f489bf762a6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "string", [scope, key, value]))

    @jsii.member(jsii_name="valueForScope")
    def value_for_scope(self, scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd003344de5d30b75c139b405ee802d237515fcd42d8c15e6b89428bf1b5b071)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(builtins.str, jsii.invoke(self, "valueForScope", [scope]))


class State(metaclass=jsii.JSIIMeta, jsii_type="cdk-extensions.core.State"):
    '''Provides a means of storing and retrieving arbitrary data that can be associated with a construct.'''

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, scope: _constructs_77d1e7e8.IConstruct) -> "State":
        '''Gets an object that allows for interacting with the stored state of a construct.

        :param scope: The construct for which state information is desired.

        :return:

        An object that provides a means for interacting with the stored
        state of the construct.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b950d29e4cfab77ec7d5a53e4bd8261c1670424a85a8771da53dca2e60bb6c8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("State", jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="get")
    def get(self, key: builtins.str, default_value: typing.Any = None) -> typing.Any:
        '''Gets the value of a key from state.

        :param key: The key to get from state.
        :param default_value: The value to return if the requested key does not exist in state.

        :return:

        The value of the requested key or ``defaultValue`` if the requested
        key was not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c1accd384eae2ad1e95ee01b90cde97e9975e6ffc78f8895d2c13182bf67d12)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
        return typing.cast(typing.Any, jsii.invoke(self, "get", [key, default_value]))

    @jsii.member(jsii_name="set")
    def set(self, key: builtins.str, value: typing.Any) -> typing.Any:
        '''Sets the value of a key in state.

        :param key: The key to set in state.
        :param value: The value to set for the key in state.

        :return: The previous value for the key that was set (if one exists).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2319ca99243664f7c9ad3ca20c5970ee1890296b0438ae3b813dbc6095162ef)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(typing.Any, jsii.invoke(self, "set", [key, value]))


__all__ = [
    "DataSize",
    "SecretReference",
    "State",
]

publication.publish()

def _typecheckingstub__3f9f8028b9df6cecb71705d69960039e03fa9e4095a8366346d67d0018eba56b(
    bytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f94a313e7517e3248b9269dee52f9add5c947249a5922cbd8848af09f78d67a(
    gibibytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9671e763fd6866b0fadfdc37f12f32076b1a3c0eb1e6c8c44a98d18d705ea84(
    gigabytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5b6bef5d79ca1256cc7bb00906e642cd3b2e20a12b9e6d6a167a61a90b9226d(
    kibibytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c94d834fb141b951612c01011b4f5aa439864f5ce2ae7abdbc3193647cb674(
    kilobytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efeefc197c919d59ac34d36fa74acf9e7d8dd02726f7c7d3efa1c41934c442ae(
    mebibytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba0e534201cb35600e74c0127e594c357a205baae2a7ca5e219e86519d724436(
    megabytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58df2f97fe7cd00e39848c2e503d47b97ddc84419ee92b27027b37a33e0726e4(
    pebibytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cd6affb76d41d4c55a0ec1b18ac8ef79ac06717362bec8d544a653c2d8dd7c2(
    petabytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85dbc9806ab6c89dd5e9acba67ba9df2bf3df8fe9d7945b51f2a2bcdbdf6666f(
    tebibytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8ef754d3db22071d621691377690e190f31f885f5a6de57a65eb27e715b2a58(
    terabytes: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd4b34a78fd0292690f71372b5fb13734a651aa94133c7764eb1f489bf762a6(
    scope: _constructs_77d1e7e8.IConstruct,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd003344de5d30b75c139b405ee802d237515fcd42d8c15e6b89428bf1b5b071(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b950d29e4cfab77ec7d5a53e4bd8261c1670424a85a8771da53dca2e60bb6c8(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c1accd384eae2ad1e95ee01b90cde97e9975e6ffc78f8895d2c13182bf67d12(
    key: builtins.str,
    default_value: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2319ca99243664f7c9ad3ca20c5970ee1890296b0438ae3b813dbc6095162ef(
    key: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass
