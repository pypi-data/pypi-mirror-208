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
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kinesisfirehose as _aws_cdk_aws_kinesisfirehose_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8
from ..glue import Database as _Database_5971ae38, Table as _Table_114d5aef


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.AppendDelimiterProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"delimiter": "delimiter"},
)
class AppendDelimiterProcessorOptions:
    def __init__(self, *, delimiter: builtins.str) -> None:
        '''
        :param delimiter: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d89cbf1928d2e92a6f324db6cf3cc7bfce4f5462b42f0a2c2441d56ec253fd7)
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delimiter": delimiter,
        }

    @builtins.property
    def delimiter(self) -> builtins.str:
        result = self._values.get("delimiter")
        assert result is not None, "Required property 'delimiter' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppendDelimiterProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.BackupConfiguration",
):
    def __init__(
        self,
        *,
        destination: "IDeliveryStreamBackupDestination",
        enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param destination: 
        :param enabled: 
        '''
        options = BackupConfigurationOptions(destination=destination, enabled=enabled)

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> "BackupConfigurationResult":
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39eeb1ec9ea9eedecc9eb4e100a7292a06bfbf35fee776a4c6e026bbe5311593)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("BackupConfigurationResult", jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> "IDeliveryStreamBackupDestination":
        return typing.cast("IDeliveryStreamBackupDestination", jsii.get(self, "destination"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.BackupConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination", "enabled": "enabled"},
)
class BackupConfigurationOptions:
    def __init__(
        self,
        *,
        destination: "IDeliveryStreamBackupDestination",
        enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param destination: 
        :param enabled: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b823f6ef73a229f88b0512bf65acd3fc7ed4339f19ab4c804d7afaeaf85f7f08)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def destination(self) -> "IDeliveryStreamBackupDestination":
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("IDeliveryStreamBackupDestination", result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.BackupConfigurationResult",
    jsii_struct_bases=[],
    name_mapping={
        "s3_backup_configuration": "s3BackupConfiguration",
        "s3_backup_mode": "s3BackupMode",
    },
)
class BackupConfigurationResult:
    def __init__(
        self,
        *,
        s3_backup_configuration: typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]],
        s3_backup_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param s3_backup_configuration: 
        :param s3_backup_mode: 
        '''
        if isinstance(s3_backup_configuration, dict):
            s3_backup_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty(**s3_backup_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72bd9180ce9c696a91ceb3527c6ae02102aec7e84c061131f3018798060b08c4)
            check_type(argname="argument s3_backup_configuration", value=s3_backup_configuration, expected_type=type_hints["s3_backup_configuration"])
            check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_backup_configuration": s3_backup_configuration,
        }
        if s3_backup_mode is not None:
            self._values["s3_backup_mode"] = s3_backup_mode

    @builtins.property
    def s3_backup_configuration(
        self,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty:
        result = self._values.get("s3_backup_configuration")
        assert result is not None, "Required property 's3_backup_configuration' is missing"
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, result)

    @builtins.property
    def s3_backup_mode(self) -> typing.Optional[builtins.str]:
        result = self._values.get("s3_backup_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupConfigurationResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BufferingConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.BufferingConfiguration",
):
    def __init__(
        self,
        *,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        size_in_mb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: 
        :param size_in_mb: 
        '''
        options = BufferingConfigurationOptions(
            interval=interval, size_in_mb=size_in_mb
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.BufferingHintsProperty]:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0eed7bb4fde4a6987300bd36297cf67f0616aceeba5a6791afd9f373526bd25)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.BufferingHintsProperty], jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="interval")
    def interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "interval"))

    @builtins.property
    @jsii.member(jsii_name="sizeInMb")
    def size_in_mb(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInMb"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.BufferingConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "size_in_mb": "sizeInMb"},
)
class BufferingConfigurationOptions:
    def __init__(
        self,
        *,
        interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        size_in_mb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param interval: 
        :param size_in_mb: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7d59d5b3f0eed355b5cbd9da2160d4889272b5dcde9045cf9e5052d9e828192)
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument size_in_mb", value=size_in_mb, expected_type=type_hints["size_in_mb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if interval is not None:
            self._values["interval"] = interval
        if size_in_mb is not None:
            self._values["size_in_mb"] = size_in_mb

    @builtins.property
    def interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        result = self._values.get("interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def size_in_mb(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("size_in_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BufferingConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudWatchLoggingConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.CloudWatchLoggingConfiguration",
):
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        log_stream: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream] = None,
    ) -> None:
        '''
        :param enabled: 
        :param log_group: 
        :param log_stream: 
        '''
        options = CloudWatchLoggingConfigurationOptions(
            enabled=enabled, log_group=log_group, log_stream=log_stream
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.CloudWatchLoggingOptionsProperty]:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5e2c7d3332348dce4e30482a87105eac01663461092f0049ebdb74f3d1f2ff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.CloudWatchLoggingOptionsProperty], jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="logStream")
    def log_stream(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream]:
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream], jsii.get(self, "logStream"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.CloudWatchLoggingConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "log_group": "logGroup",
        "log_stream": "logStream",
    },
)
class CloudWatchLoggingConfigurationOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        log_stream: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream] = None,
    ) -> None:
        '''
        :param enabled: 
        :param log_group: 
        :param log_stream: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ecec857bb4ba40438742cd87f379b7e20785adf28d3923c5ce0b766abd16c1c)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument log_stream", value=log_stream, expected_type=type_hints["log_stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if log_group is not None:
            self._values["log_group"] = log_group
        if log_stream is not None:
            self._values["log_stream"] = log_stream

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def log_stream(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream]:
        result = self._values.get("log_stream")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudWatchLoggingConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.CommonPartitioningOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "retry_interval": "retryInterval"},
)
class CommonPartitioningOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param enabled: 
        :param retry_interval: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75d6a25de990c726583508ec70890fce216775086c75be0c640c664e4c58b420)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument retry_interval", value=retry_interval, expected_type=type_hints["retry_interval"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if retry_interval is not None:
            self._values["retry_interval"] = retry_interval

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retry_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        result = self._values.get("retry_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonPartitioningOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.ContentEncoding")
class ContentEncoding(enum.Enum):
    GZIP = "GZIP"
    NONE = "NONE"


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.CustomProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"processor_type": "processorType", "parameters": "parameters"},
)
class CustomProcessorOptions:
    def __init__(
        self,
        *,
        processor_type: "ProcessorType",
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param processor_type: 
        :param parameters: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78eae023c40cee15f57bf2117b663e893117034113c0c434c7503e6dc039d504)
            check_type(argname="argument processor_type", value=processor_type, expected_type=type_hints["processor_type"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "processor_type": processor_type,
        }
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def processor_type(self) -> "ProcessorType":
        result = self._values.get("processor_type")
        assert result is not None, "Required property 'processor_type' is missing"
        return typing.cast("ProcessorType", result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataFormatConversion(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.DataFormatConversion",
):
    def __init__(
        self,
        *,
        database: _Database_5971ae38,
        input_format: "InputFormat",
        output_format: "OutputFormat",
        table: _Table_114d5aef,
        catalog_id: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        region: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version: typing.Optional["TableVersion"] = None,
    ) -> None:
        '''
        :param database: 
        :param input_format: 
        :param output_format: 
        :param table: 
        :param catalog_id: 
        :param enabled: 
        :param region: 
        :param role: 
        :param version: 
        '''
        options = DataFormatConversionOptions(
            database=database,
            input_format=input_format,
            output_format=output_format,
            table=table,
            catalog_id=catalog_id,
            enabled=enabled,
            region=region,
            role=role,
            version=version,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DataFormatConversionConfigurationProperty:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f34563e2a338b831b08054a8158cbd3bec4ae881f2f6e2da967dacfec61a44df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DataFormatConversionConfigurationProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> _Database_5971ae38:
        return typing.cast(_Database_5971ae38, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="inputFormat")
    def input_format(self) -> "InputFormat":
        return typing.cast("InputFormat", jsii.get(self, "inputFormat"))

    @builtins.property
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> "OutputFormat":
        return typing.cast("OutputFormat", jsii.get(self, "outputFormat"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _Table_114d5aef:
        return typing.cast(_Table_114d5aef, jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="catalogId")
    def catalog_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "catalogId"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional["TableVersion"]:
        return typing.cast(typing.Optional["TableVersion"], jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DataFormatConversionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "input_format": "inputFormat",
        "output_format": "outputFormat",
        "table": "table",
        "catalog_id": "catalogId",
        "enabled": "enabled",
        "region": "region",
        "role": "role",
        "version": "version",
    },
)
class DataFormatConversionOptions:
    def __init__(
        self,
        *,
        database: _Database_5971ae38,
        input_format: "InputFormat",
        output_format: "OutputFormat",
        table: _Table_114d5aef,
        catalog_id: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        region: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version: typing.Optional["TableVersion"] = None,
    ) -> None:
        '''
        :param database: 
        :param input_format: 
        :param output_format: 
        :param table: 
        :param catalog_id: 
        :param enabled: 
        :param region: 
        :param role: 
        :param version: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9567fc6b66b0e53903494269a652d394f7cc50bac28b4ba8aa05c042942cbdd0)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument input_format", value=input_format, expected_type=type_hints["input_format"])
            check_type(argname="argument output_format", value=output_format, expected_type=type_hints["output_format"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument catalog_id", value=catalog_id, expected_type=type_hints["catalog_id"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "input_format": input_format,
            "output_format": output_format,
            "table": table,
        }
        if catalog_id is not None:
            self._values["catalog_id"] = catalog_id
        if enabled is not None:
            self._values["enabled"] = enabled
        if region is not None:
            self._values["region"] = region
        if role is not None:
            self._values["role"] = role
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def database(self) -> _Database_5971ae38:
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(_Database_5971ae38, result)

    @builtins.property
    def input_format(self) -> "InputFormat":
        result = self._values.get("input_format")
        assert result is not None, "Required property 'input_format' is missing"
        return typing.cast("InputFormat", result)

    @builtins.property
    def output_format(self) -> "OutputFormat":
        result = self._values.get("output_format")
        assert result is not None, "Required property 'output_format' is missing"
        return typing.cast("OutputFormat", result)

    @builtins.property
    def table(self) -> _Table_114d5aef:
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(_Table_114d5aef, result)

    @builtins.property
    def catalog_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("catalog_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def version(self) -> typing.Optional["TableVersion"]:
        result = self._values.get("version")
        return typing.cast(typing.Optional["TableVersion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataFormatConversionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DelimitedDeaggregationOptions",
    jsii_struct_bases=[],
    name_mapping={"delimiter": "delimiter"},
)
class DelimitedDeaggregationOptions:
    def __init__(self, *, delimiter: builtins.str) -> None:
        '''
        :param delimiter: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f18e1356030ed7e6e9769bc02289a51fae7c3b805209bde84ef0204406cdc297)
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delimiter": delimiter,
        }

    @builtins.property
    def delimiter(self) -> builtins.str:
        result = self._values.get("delimiter")
        assert result is not None, "Required property 'delimiter' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DelimitedDeaggregationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_arn": "deliveryStreamArn",
        "delivery_stream_name": "deliveryStreamName",
        "role": "role",
    },
)
class DeliveryStreamAttributes:
    def __init__(
        self,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param delivery_stream_arn: 
        :param delivery_stream_name: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5070987c69666d624d69af7fd0e1b1930354030e542513b8a2efe27b4188a31)
            check_type(argname="argument delivery_stream_arn", value=delivery_stream_arn, expected_type=type_hints["delivery_stream_arn"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delivery_stream_arn is not None:
            self._values["delivery_stream_arn"] = delivery_stream_arn
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def delivery_stream_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("delivery_stream_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeliveryStreamDestination(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamDestination",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> "DeliveryStreamDestinationConfiguration":
        '''
        :param scope: -
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


class _DeliveryStreamDestinationProxy(DeliveryStreamDestination):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> "DeliveryStreamDestinationConfiguration":
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41587c0ee8bc81bcc496a1b1197d62bf43fe2c2ff76c9b7511f0a5d2b21f153a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("DeliveryStreamDestinationConfiguration", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, DeliveryStreamDestination).__jsii_proxy_class__ = lambda : _DeliveryStreamDestinationProxy


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamDestinationConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "amazonopensearchservice_destination_configuration": "amazonopensearchserviceDestinationConfiguration",
        "elasticsearch_destination_configuration": "elasticsearchDestinationConfiguration",
        "extended_s3_destination_configuration": "extendedS3DestinationConfiguration",
        "http_endpoint_destination_configuration": "httpEndpointDestinationConfiguration",
        "redshift_destination_configuration": "redshiftDestinationConfiguration",
        "s3_destination_configuration": "s3DestinationConfiguration",
        "splunk_destination_configuration": "splunkDestinationConfiguration",
    },
)
class DeliveryStreamDestinationConfiguration:
    def __init__(
        self,
        *,
        amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        extended_s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.RedshiftDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.SplunkDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param amazonopensearchservice_destination_configuration: 
        :param elasticsearch_destination_configuration: 
        :param extended_s3_destination_configuration: 
        :param http_endpoint_destination_configuration: 
        :param redshift_destination_configuration: 
        :param s3_destination_configuration: 
        :param splunk_destination_configuration: 
        '''
        if isinstance(amazonopensearchservice_destination_configuration, dict):
            amazonopensearchservice_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty(**amazonopensearchservice_destination_configuration)
        if isinstance(elasticsearch_destination_configuration, dict):
            elasticsearch_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty(**elasticsearch_destination_configuration)
        if isinstance(extended_s3_destination_configuration, dict):
            extended_s3_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(**extended_s3_destination_configuration)
        if isinstance(http_endpoint_destination_configuration, dict):
            http_endpoint_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty(**http_endpoint_destination_configuration)
        if isinstance(redshift_destination_configuration, dict):
            redshift_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(**redshift_destination_configuration)
        if isinstance(s3_destination_configuration, dict):
            s3_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty(**s3_destination_configuration)
        if isinstance(splunk_destination_configuration, dict):
            splunk_destination_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.SplunkDestinationConfigurationProperty(**splunk_destination_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff5c5fd4c2fde1759984bade800eb7acb9b938f66435a1eeb50642a1ab888d9)
            check_type(argname="argument amazonopensearchservice_destination_configuration", value=amazonopensearchservice_destination_configuration, expected_type=type_hints["amazonopensearchservice_destination_configuration"])
            check_type(argname="argument elasticsearch_destination_configuration", value=elasticsearch_destination_configuration, expected_type=type_hints["elasticsearch_destination_configuration"])
            check_type(argname="argument extended_s3_destination_configuration", value=extended_s3_destination_configuration, expected_type=type_hints["extended_s3_destination_configuration"])
            check_type(argname="argument http_endpoint_destination_configuration", value=http_endpoint_destination_configuration, expected_type=type_hints["http_endpoint_destination_configuration"])
            check_type(argname="argument redshift_destination_configuration", value=redshift_destination_configuration, expected_type=type_hints["redshift_destination_configuration"])
            check_type(argname="argument s3_destination_configuration", value=s3_destination_configuration, expected_type=type_hints["s3_destination_configuration"])
            check_type(argname="argument splunk_destination_configuration", value=splunk_destination_configuration, expected_type=type_hints["splunk_destination_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if amazonopensearchservice_destination_configuration is not None:
            self._values["amazonopensearchservice_destination_configuration"] = amazonopensearchservice_destination_configuration
        if elasticsearch_destination_configuration is not None:
            self._values["elasticsearch_destination_configuration"] = elasticsearch_destination_configuration
        if extended_s3_destination_configuration is not None:
            self._values["extended_s3_destination_configuration"] = extended_s3_destination_configuration
        if http_endpoint_destination_configuration is not None:
            self._values["http_endpoint_destination_configuration"] = http_endpoint_destination_configuration
        if redshift_destination_configuration is not None:
            self._values["redshift_destination_configuration"] = redshift_destination_configuration
        if s3_destination_configuration is not None:
            self._values["s3_destination_configuration"] = s3_destination_configuration
        if splunk_destination_configuration is not None:
            self._values["splunk_destination_configuration"] = splunk_destination_configuration

    @builtins.property
    def amazonopensearchservice_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty]:
        result = self._values.get("amazonopensearchservice_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty], result)

    @builtins.property
    def elasticsearch_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty]:
        result = self._values.get("elasticsearch_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty], result)

    @builtins.property
    def extended_s3_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty]:
        result = self._values.get("extended_s3_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty], result)

    @builtins.property
    def http_endpoint_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty]:
        result = self._values.get("http_endpoint_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty], result)

    @builtins.property
    def redshift_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.RedshiftDestinationConfigurationProperty]:
        result = self._values.get("redshift_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.RedshiftDestinationConfigurationProperty], result)

    @builtins.property
    def s3_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty]:
        result = self._values.get("s3_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty], result)

    @builtins.property
    def splunk_destination_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.SplunkDestinationConfigurationProperty]:
        result = self._values.get("splunk_destination_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.SplunkDestinationConfigurationProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamDestinationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeliveryStreamProcessor(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamProcessor",
):
    def __init__(
        self,
        *,
        processor_type: "ProcessorType",
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param processor_type: 
        :param parameters: 
        '''
        options = DeliveryStreamProcessorOptions(
            processor_type=processor_type, parameters=parameters
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addProcessorParameter")
    def _add_processor_parameter(self, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__392f37faf2c6e54ea42383b8a1706ddb8cd3e52cabfdcb5e5c3af36d5fcdf7eb)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "addProcessorParameter", [name, value]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessorProperty:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a58ae9fb2fa71b23b2dd37c0b9b517eb33b12ffcf1679c535d8870179ec79b9)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessorProperty, jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="processorType")
    def processor_type(self) -> "ProcessorType":
        return typing.cast("ProcessorType", jsii.get(self, "processorType"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"processor_type": "processorType", "parameters": "parameters"},
)
class DeliveryStreamProcessorOptions:
    def __init__(
        self,
        *,
        processor_type: "ProcessorType",
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param processor_type: 
        :param parameters: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4633e8d78e091ab02719695d8d2c88323161cacd6cb9bd6639fa12b351454aff)
            check_type(argname="argument processor_type", value=processor_type, expected_type=type_hints["processor_type"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "processor_type": processor_type,
        }
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def processor_type(self) -> "ProcessorType":
        result = self._values.get("processor_type")
        assert result is not None, "Required property 'processor_type' is missing"
        return typing.cast("ProcessorType", result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "destination": "destination",
        "name": "name",
        "stream_type": "streamType",
    },
)
class DeliveryStreamProps(_aws_cdk_ceddda9d.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        destination: DeliveryStreamDestination,
        name: typing.Optional[builtins.str] = None,
        stream_type: typing.Optional["DeliveryStreamType"] = None,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param destination: 
        :param name: 
        :param stream_type: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__440cfb7edd010dcdea81cac29f91707905f287c17f672fedbb1ebcaba556b7a1)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument stream_type", value=stream_type, expected_type=type_hints["stream_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if name is not None:
            self._values["name"] = name
        if stream_type is not None:
            self._values["stream_type"] = stream_type

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination(self) -> DeliveryStreamDestination:
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(DeliveryStreamDestination, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stream_type(self) -> typing.Optional["DeliveryStreamType"]:
        result = self._values.get("stream_type")
        return typing.cast(typing.Optional["DeliveryStreamType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.DeliveryStreamType")
class DeliveryStreamType(enum.Enum):
    DIRECT_PUT = "DIRECT_PUT"
    KINESIS_STREAM_AS_SOURCE = "KINESIS_STREAM_AS_SOURCE"


class DynamicPartitioning(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.DynamicPartitioning",
):
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param enabled: 
        :param retry_interval: 
        '''
        options = CommonPartitioningOptions(
            enabled=enabled, retry_interval=retry_interval
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="fromJson")
    @builtins.classmethod
    def from_json(
        cls,
        *,
        partitions: typing.Mapping[builtins.str, builtins.str],
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> "JsonPartitioningSource":
        '''
        :param partitions: 
        :param enabled: 
        :param retry_interval: 
        '''
        options = JsonPartitioningOptions(
            partitions=partitions, enabled=enabled, retry_interval=retry_interval
        )

        return typing.cast("JsonPartitioningSource", jsii.sinvoke(cls, "fromJson", [options]))

    @jsii.member(jsii_name="fromLambda")
    @builtins.classmethod
    def from_lambda(
        cls,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> "LambdaPartitioningSource":
        '''
        :param lambda_function: 
        :param enabled: 
        :param retry_interval: 
        '''
        options = LambdaPartitioningOptions(
            lambda_function=lambda_function,
            enabled=enabled,
            retry_interval=retry_interval,
        )

        return typing.cast("LambdaPartitioningSource", jsii.sinvoke(cls, "fromLambda", [options]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> "DynamicPartitioningConfiguration":
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2bd84810b50cb68268c2a97bfe1b190becaf4e80f78f04b0cb9893b592b4ff8)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast("DynamicPartitioningConfiguration", jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="retryInterval")
    def retry_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "retryInterval"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.DynamicPartitioningConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "partitioning_configuration": "partitioningConfiguration",
        "processors": "processors",
    },
)
class DynamicPartitioningConfiguration:
    def __init__(
        self,
        *,
        partitioning_configuration: typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DynamicPartitioningConfigurationProperty, typing.Dict[builtins.str, typing.Any]],
        processors: typing.Optional[typing.Sequence[DeliveryStreamProcessor]] = None,
    ) -> None:
        '''
        :param partitioning_configuration: 
        :param processors: 
        '''
        if isinstance(partitioning_configuration, dict):
            partitioning_configuration = _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(**partitioning_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5916bca326decbc140e0564c1a76889229c1ec60795e765e7936bb66704859c)
            check_type(argname="argument partitioning_configuration", value=partitioning_configuration, expected_type=type_hints["partitioning_configuration"])
            check_type(argname="argument processors", value=processors, expected_type=type_hints["processors"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "partitioning_configuration": partitioning_configuration,
        }
        if processors is not None:
            self._values["processors"] = processors

    @builtins.property
    def partitioning_configuration(
        self,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DynamicPartitioningConfigurationProperty:
        result = self._values.get("partitioning_configuration")
        assert result is not None, "Required property 'partitioning_configuration' is missing"
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DynamicPartitioningConfigurationProperty, result)

    @builtins.property
    def processors(self) -> typing.Optional[typing.List[DeliveryStreamProcessor]]:
        result = self._values.get("processors")
        return typing.cast(typing.Optional[typing.List[DeliveryStreamProcessor]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicPartitioningConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.HiveJsonInputSerDeOptions",
    jsii_struct_bases=[],
    name_mapping={"timestamp_formats": "timestampFormats"},
)
class HiveJsonInputSerDeOptions:
    def __init__(
        self,
        *,
        timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param timestamp_formats: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b0084542b1ce34e535ddbf630f88e241e5c77ee3aca6a6f2b7f3d734a1e0e26)
            check_type(argname="argument timestamp_formats", value=timestamp_formats, expected_type=type_hints["timestamp_formats"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if timestamp_formats is not None:
            self._values["timestamp_formats"] = timestamp_formats

    @builtins.property
    def timestamp_formats(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("timestamp_formats")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HiveJsonInputSerDeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpEndpointDestination(
    DeliveryStreamDestination,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.HttpEndpointDestination",
):
    def __init__(
        self,
        url: builtins.str,
        *,
        access_key: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        backup_configuration: typing.Optional[BackupConfiguration] = None,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        common_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        content_encoding: typing.Optional[ContentEncoding] = None,
        endpoint_name: typing.Optional[builtins.str] = None,
        processor_configuration: typing.Optional["ProcessorConfiguration"] = None,
        retry_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param url: -
        :param access_key: 
        :param backup_configuration: 
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param common_attributes: 
        :param content_encoding: 
        :param endpoint_name: 
        :param processor_configuration: 
        :param retry_duration: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6582b21a2533517358f209922ce90e2a7f4cd38f6753705d50def9ea3a7e44b1)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        options = HttpEndpointDestinationOptions(
            access_key=access_key,
            backup_configuration=backup_configuration,
            buffering=buffering,
            cloudwatch_logging_configuration=cloudwatch_logging_configuration,
            common_attributes=common_attributes,
            content_encoding=content_encoding,
            endpoint_name=endpoint_name,
            processor_configuration=processor_configuration,
            retry_duration=retry_duration,
        )

        jsii.create(self.__class__, self, [url, options])

    @jsii.member(jsii_name="addCommonAttribute")
    def add_common_attribute(
        self,
        name: builtins.str,
        value: builtins.str,
    ) -> "HttpEndpointDestination":
        '''
        :param name: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7fd3de331f3de9e6cf31b86e6897c829a5de47c3a0d181bf976b007b5b6a444)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("HttpEndpointDestination", jsii.invoke(self, "addCommonAttribute", [name, value]))

    @jsii.member(jsii_name="addProcessor")
    def add_processor(
        self,
        processor: DeliveryStreamProcessor,
    ) -> "HttpEndpointDestination":
        '''
        :param processor: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50521eaec241f51d9f40a0cb9e9ff249c81ff399a57814426fdca964e29403f7)
            check_type(argname="argument processor", value=processor, expected_type=type_hints["processor"])
        return typing.cast("HttpEndpointDestination", jsii.invoke(self, "addProcessor", [processor]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> DeliveryStreamDestinationConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5e7d3b1d23f51b37027fac0cc97ddbf20afdec2b7a352579db009d48496a8d1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(DeliveryStreamDestinationConfiguration, jsii.invoke(self, "bind", [scope]))

    @jsii.member(jsii_name="buildBackupConfiguration")
    def _build_backup_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> BackupConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d531d1e5cdd19cc324f9f73ef7f210530200b242626cf917de7bc71db40b832a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(BackupConfiguration, jsii.invoke(self, "buildBackupConfiguration", [scope]))

    @jsii.member(jsii_name="getOrCreateRole")
    def _get_or_create_role(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bed9b7561cbeae33da160c724a0a82b7ab489c26312e7e4042cd7bd4ff674936)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.invoke(self, "getOrCreateRole", [scope]))

    @jsii.member(jsii_name="renderProcessorConfiguration")
    def _render_processor_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessingConfigurationProperty]:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a39f3047199326013e7d9897ee142decf1c2c6dad9a6900daafa1bf1f6d94c8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessingConfigurationProperty], jsii.invoke(self, "renderProcessorConfiguration", [scope]))

    @builtins.property
    @jsii.member(jsii_name="endpointUrl")
    def endpoint_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUrl"))

    @builtins.property
    @jsii.member(jsii_name="processingEnabled")
    def processing_enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "processingEnabled"))

    @builtins.property
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], jsii.get(self, "accessKey"))

    @builtins.property
    @jsii.member(jsii_name="backupConfiguration")
    def backup_configuration(self) -> typing.Optional[BackupConfiguration]:
        return typing.cast(typing.Optional[BackupConfiguration], jsii.get(self, "backupConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="buffering")
    def buffering(self) -> typing.Optional[BufferingConfiguration]:
        return typing.cast(typing.Optional[BufferingConfiguration], jsii.get(self, "buffering"))

    @builtins.property
    @jsii.member(jsii_name="cloudwatchLoggingConfiguration")
    def cloudwatch_logging_configuration(
        self,
    ) -> typing.Optional[CloudWatchLoggingConfiguration]:
        return typing.cast(typing.Optional[CloudWatchLoggingConfiguration], jsii.get(self, "cloudwatchLoggingConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="commonAttributes")
    def common_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "commonAttributes"))

    @builtins.property
    @jsii.member(jsii_name="contentEncoding")
    def content_encoding(self) -> typing.Optional[ContentEncoding]:
        return typing.cast(typing.Optional[ContentEncoding], jsii.get(self, "contentEncoding"))

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointName"))

    @builtins.property
    @jsii.member(jsii_name="processorConfiguration")
    def processor_configuration(self) -> typing.Optional["ProcessorConfiguration"]:
        return typing.cast(typing.Optional["ProcessorConfiguration"], jsii.get(self, "processorConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="retryDuration")
    def retry_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "retryDuration"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.HttpEndpointDestinationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "access_key": "accessKey",
        "backup_configuration": "backupConfiguration",
        "buffering": "buffering",
        "cloudwatch_logging_configuration": "cloudwatchLoggingConfiguration",
        "common_attributes": "commonAttributes",
        "content_encoding": "contentEncoding",
        "endpoint_name": "endpointName",
        "processor_configuration": "processorConfiguration",
        "retry_duration": "retryDuration",
    },
)
class HttpEndpointDestinationOptions:
    def __init__(
        self,
        *,
        access_key: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        backup_configuration: typing.Optional[BackupConfiguration] = None,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        common_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        content_encoding: typing.Optional[ContentEncoding] = None,
        endpoint_name: typing.Optional[builtins.str] = None,
        processor_configuration: typing.Optional["ProcessorConfiguration"] = None,
        retry_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param access_key: 
        :param backup_configuration: 
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param common_attributes: 
        :param content_encoding: 
        :param endpoint_name: 
        :param processor_configuration: 
        :param retry_duration: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f22be593ceb1483c63bf50da018e6c92f4a317b11a6b951c5bfd60a0a713ad0)
            check_type(argname="argument access_key", value=access_key, expected_type=type_hints["access_key"])
            check_type(argname="argument backup_configuration", value=backup_configuration, expected_type=type_hints["backup_configuration"])
            check_type(argname="argument buffering", value=buffering, expected_type=type_hints["buffering"])
            check_type(argname="argument cloudwatch_logging_configuration", value=cloudwatch_logging_configuration, expected_type=type_hints["cloudwatch_logging_configuration"])
            check_type(argname="argument common_attributes", value=common_attributes, expected_type=type_hints["common_attributes"])
            check_type(argname="argument content_encoding", value=content_encoding, expected_type=type_hints["content_encoding"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument processor_configuration", value=processor_configuration, expected_type=type_hints["processor_configuration"])
            check_type(argname="argument retry_duration", value=retry_duration, expected_type=type_hints["retry_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_key is not None:
            self._values["access_key"] = access_key
        if backup_configuration is not None:
            self._values["backup_configuration"] = backup_configuration
        if buffering is not None:
            self._values["buffering"] = buffering
        if cloudwatch_logging_configuration is not None:
            self._values["cloudwatch_logging_configuration"] = cloudwatch_logging_configuration
        if common_attributes is not None:
            self._values["common_attributes"] = common_attributes
        if content_encoding is not None:
            self._values["content_encoding"] = content_encoding
        if endpoint_name is not None:
            self._values["endpoint_name"] = endpoint_name
        if processor_configuration is not None:
            self._values["processor_configuration"] = processor_configuration
        if retry_duration is not None:
            self._values["retry_duration"] = retry_duration

    @builtins.property
    def access_key(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        result = self._values.get("access_key")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def backup_configuration(self) -> typing.Optional[BackupConfiguration]:
        result = self._values.get("backup_configuration")
        return typing.cast(typing.Optional[BackupConfiguration], result)

    @builtins.property
    def buffering(self) -> typing.Optional[BufferingConfiguration]:
        result = self._values.get("buffering")
        return typing.cast(typing.Optional[BufferingConfiguration], result)

    @builtins.property
    def cloudwatch_logging_configuration(
        self,
    ) -> typing.Optional[CloudWatchLoggingConfiguration]:
        result = self._values.get("cloudwatch_logging_configuration")
        return typing.cast(typing.Optional[CloudWatchLoggingConfiguration], result)

    @builtins.property
    def common_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("common_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def content_encoding(self) -> typing.Optional[ContentEncoding]:
        result = self._values.get("content_encoding")
        return typing.cast(typing.Optional[ContentEncoding], result)

    @builtins.property
    def endpoint_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("endpoint_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def processor_configuration(self) -> typing.Optional["ProcessorConfiguration"]:
        result = self._values.get("processor_configuration")
        return typing.cast(typing.Optional["ProcessorConfiguration"], result)

    @builtins.property
    def retry_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        result = self._values.get("retry_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpEndpointDestinationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk-extensions.kinesis_firehose.IDeliveryStream")
class IDeliveryStream(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        :param actions: -
        '''
        ...

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...


class _IDeliveryStreamProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.kinesis_firehose.IDeliveryStream"

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf7bcbe9748a6da845cceb739b108bffe77c724cee970b1c266a6a3f202b9272)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b93bb27770d9b8546ee8588396fce92c33131b61b55f0e09c5be13e362589ca)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf65fe3d702e9cb684464674963ccf372b5514566edde6bc90567ac3428b4ab2)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeliveryStream).__jsii_proxy_class__ = lambda : _IDeliveryStreamProxy


@jsii.interface(
    jsii_type="cdk-extensions.kinesis_firehose.IDeliveryStreamBackupDestination"
)
class IDeliveryStreamBackupDestination(typing_extensions.Protocol):
    @jsii.member(jsii_name="renderBackupConfiguration")
    def render_backup_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        enabled: typing.Optional[builtins.bool] = None,
    ) -> BackupConfigurationResult:
        '''
        :param scope: -
        :param enabled: -
        '''
        ...


class _IDeliveryStreamBackupDestinationProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.kinesis_firehose.IDeliveryStreamBackupDestination"

    @jsii.member(jsii_name="renderBackupConfiguration")
    def render_backup_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        enabled: typing.Optional[builtins.bool] = None,
    ) -> BackupConfigurationResult:
        '''
        :param scope: -
        :param enabled: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0342c34585fb8eaed0dac1dc61ffa2c0d173d315ac38ef2182806ef6d38aea22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        return typing.cast(BackupConfigurationResult, jsii.invoke(self, "renderBackupConfiguration", [scope, enabled]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeliveryStreamBackupDestination).__jsii_proxy_class__ = lambda : _IDeliveryStreamBackupDestinationProxy


class InputFormat(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-extensions.kinesis_firehose.InputFormat",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="hiveJson")
    @builtins.classmethod
    def hive_json(
        cls,
        *,
        timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "HiveJsonInputSerDe":
        '''
        :param timestamp_formats: 
        '''
        options = HiveJsonInputSerDeOptions(timestamp_formats=timestamp_formats)

        return typing.cast("HiveJsonInputSerDe", jsii.sinvoke(cls, "hiveJson", [options]))

    @jsii.member(jsii_name="openxJson")
    @builtins.classmethod
    def openx_json(
        cls,
        *,
        case_insensitive: typing.Optional[builtins.bool] = None,
        column_key_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        convert_dots_to_underscores: typing.Optional[builtins.bool] = None,
    ) -> "OpenxJsonInputSerDe":
        '''
        :param case_insensitive: 
        :param column_key_mappings: 
        :param convert_dots_to_underscores: 
        '''
        options = OpenxJsonInputSerDeOptions(
            case_insensitive=case_insensitive,
            column_key_mappings=column_key_mappings,
            convert_dots_to_underscores=convert_dots_to_underscores,
        )

        return typing.cast("OpenxJsonInputSerDe", jsii.sinvoke(cls, "openxJson", [options]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty:
        '''
        :param scope: -
        '''
        ...


class _InputFormatProxy(InputFormat):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a19f76095e079e46f5f7165b14aa5174f980d9a8da4779646f8aaeda38c063)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, InputFormat).__jsii_proxy_class__ = lambda : _InputFormatProxy


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.JsonParsingEngine")
class JsonParsingEngine(enum.Enum):
    JQ_1_6 = "JQ_1_6"


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.JsonPartitioningOptions",
    jsii_struct_bases=[CommonPartitioningOptions],
    name_mapping={
        "enabled": "enabled",
        "retry_interval": "retryInterval",
        "partitions": "partitions",
    },
)
class JsonPartitioningOptions(CommonPartitioningOptions):
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        partitions: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''
        :param enabled: 
        :param retry_interval: 
        :param partitions: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba50ad7522466bb0437400cbe9a708cb5f284208a7da53fdac531bd091ea4418)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument retry_interval", value=retry_interval, expected_type=type_hints["retry_interval"])
            check_type(argname="argument partitions", value=partitions, expected_type=type_hints["partitions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "partitions": partitions,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if retry_interval is not None:
            self._values["retry_interval"] = retry_interval

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retry_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        result = self._values.get("retry_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def partitions(self) -> typing.Mapping[builtins.str, builtins.str]:
        result = self._values.get("partitions")
        assert result is not None, "Required property 'partitions' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsonPartitioningOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class JsonPartitioningSource(
    DynamicPartitioning,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.JsonPartitioningSource",
):
    def __init__(
        self,
        *,
        partitions: typing.Mapping[builtins.str, builtins.str],
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param partitions: 
        :param enabled: 
        :param retry_interval: 
        '''
        options = JsonPartitioningOptions(
            partitions=partitions, enabled=enabled, retry_interval=retry_interval
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addPartition")
    def add_partition(self, name: builtins.str, query: builtins.str) -> None:
        '''
        :param name: -
        :param query: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99613095e9e0b584d502e7e0a99aa1a9afdf6b641e1edff1691cc6e76cc172f0)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        return typing.cast(None, jsii.invoke(self, "addPartition", [name, query]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> DynamicPartitioningConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4d0e96c22d2b377915c808428e42408811ebe6b4ec98aa4c634992d1e433b3e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(DynamicPartitioningConfiguration, jsii.invoke(self, "bind", [scope]))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.LambdaPartitioningOptions",
    jsii_struct_bases=[CommonPartitioningOptions],
    name_mapping={
        "enabled": "enabled",
        "retry_interval": "retryInterval",
        "lambda_function": "lambdaFunction",
    },
)
class LambdaPartitioningOptions(CommonPartitioningOptions):
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''
        :param enabled: 
        :param retry_interval: 
        :param lambda_function: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33af2c81bc5a83bb701c31329741ebf03be603636bd2333602e214020eac0ed0)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument retry_interval", value=retry_interval, expected_type=type_hints["retry_interval"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lambda_function": lambda_function,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if retry_interval is not None:
            self._values["retry_interval"] = retry_interval

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retry_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        result = self._values.get("retry_interval")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaPartitioningOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaPartitioningSource(
    DynamicPartitioning,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.LambdaPartitioningSource",
):
    def __init__(
        self,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        enabled: typing.Optional[builtins.bool] = None,
        retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param lambda_function: 
        :param enabled: 
        :param retry_interval: 
        '''
        options = LambdaPartitioningOptions(
            lambda_function=lambda_function,
            enabled=enabled,
            retry_interval=retry_interval,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> DynamicPartitioningConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d9a4c8f309bd9a368157f94cf9541a573da0fb985b70ce340bda80e4b48d4be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(DynamicPartitioningConfiguration, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "lambdaFunction"))


class LambdaProcessor(
    DeliveryStreamProcessor,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.LambdaProcessor",
):
    def __init__(
        self,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''
        :param lambda_function: 
        '''
        options = LambdaProcessorOptions(lambda_function=lambda_function)

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "lambdaFunction"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.LambdaProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"lambda_function": "lambdaFunction"},
)
class LambdaProcessorOptions:
    def __init__(
        self,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''
        :param lambda_function: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955a878a98a24d4bb0c4e55d76bd5c20e36162215a3b05dc533898b69b8be1b5)
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lambda_function": lambda_function,
        }

    @builtins.property
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetaDataExtractionQuery(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.MetaDataExtractionQuery",
):
    def __init__(self, query: builtins.str) -> None:
        '''
        :param query: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__169f59ac5ef018ff3132111f756fe912271effad7f2fb91cabc8bd84dcba81db)
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        jsii.create(self.__class__, self, [query])

    @jsii.member(jsii_name="jq")
    @builtins.classmethod
    def jq(cls, fields: typing.Mapping[builtins.str, builtins.str]) -> "JsonQuery":
        '''
        :param fields: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1c87bfa00fa0b282a284d13ed075f362fece18bb715bb6b13ec033e3969920e)
            check_type(argname="argument fields", value=fields, expected_type=type_hints["fields"])
        return typing.cast("JsonQuery", jsii.sinvoke(cls, "jq", [fields]))

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, query: builtins.str) -> "MetaDataExtractionQuery":
        '''
        :param query: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ab103735cc2be78f22e2df46e8008a770f114052c04d2d227ddce0a993c0579)
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        return typing.cast("MetaDataExtractionQuery", jsii.sinvoke(cls, "of", [query]))

    @jsii.member(jsii_name="render")
    def render(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="query")
    def _query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @_query.setter
    def _query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b8c72648253650e08268e4eff28118ed70690a4925325ba11244527c440ec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "query", value)


class MetadataExtractionProcessor(
    DeliveryStreamProcessor,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.MetadataExtractionProcessor",
):
    def __init__(
        self,
        *,
        query: MetaDataExtractionQuery,
        engine: typing.Optional[JsonParsingEngine] = None,
    ) -> None:
        '''
        :param query: 
        :param engine: 
        '''
        options = MetadataExtractionProcessorOptions(query=query, engine=engine)

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="engine")
    def engine(self) -> JsonParsingEngine:
        return typing.cast(JsonParsingEngine, jsii.get(self, "engine"))

    @builtins.property
    @jsii.member(jsii_name="query")
    def query(self) -> MetaDataExtractionQuery:
        return typing.cast(MetaDataExtractionQuery, jsii.get(self, "query"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.MetadataExtractionProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "engine": "engine"},
)
class MetadataExtractionProcessorOptions:
    def __init__(
        self,
        *,
        query: MetaDataExtractionQuery,
        engine: typing.Optional[JsonParsingEngine] = None,
    ) -> None:
        '''
        :param query: 
        :param engine: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce29299765030b4b969264a272477e1caee2edf4fc3f0cc7e53f0cd073912374)
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "query": query,
        }
        if engine is not None:
            self._values["engine"] = engine

    @builtins.property
    def query(self) -> MetaDataExtractionQuery:
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(MetaDataExtractionQuery, result)

    @builtins.property
    def engine(self) -> typing.Optional[JsonParsingEngine]:
        result = self._values.get("engine")
        return typing.cast(typing.Optional[JsonParsingEngine], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataExtractionProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenxJsonInputSerDe(
    InputFormat,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.OpenxJsonInputSerDe",
):
    def __init__(
        self,
        *,
        case_insensitive: typing.Optional[builtins.bool] = None,
        column_key_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        convert_dots_to_underscores: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param case_insensitive: 
        :param column_key_mappings: 
        :param convert_dots_to_underscores: 
        '''
        options = OpenxJsonInputSerDeOptions(
            case_insensitive=case_insensitive,
            column_key_mappings=column_key_mappings,
            convert_dots_to_underscores=convert_dots_to_underscores,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addColumnKeyMapping")
    def add_column_key_mapping(
        self,
        column_name: builtins.str,
        json_key: builtins.str,
    ) -> "OpenxJsonInputSerDe":
        '''
        :param column_name: -
        :param json_key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0033a54ad96b9adb2c19922659ad359d1f977d89d613ba53b97a968e66589b0)
            check_type(argname="argument column_name", value=column_name, expected_type=type_hints["column_name"])
            check_type(argname="argument json_key", value=json_key, expected_type=type_hints["json_key"])
        return typing.cast("OpenxJsonInputSerDe", jsii.invoke(self, "addColumnKeyMapping", [column_name, json_key]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47bddcfdf0e5e4c9e12bd12d4ee77b28ad079fc718636fd27a63f16baa38c981)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty, jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="caseInsensitive")
    def case_insensitive(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "caseInsensitive"))

    @builtins.property
    @jsii.member(jsii_name="convertDotsToUnderscores")
    def convert_dots_to_underscores(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "convertDotsToUnderscores"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.OpenxJsonInputSerDeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "case_insensitive": "caseInsensitive",
        "column_key_mappings": "columnKeyMappings",
        "convert_dots_to_underscores": "convertDotsToUnderscores",
    },
)
class OpenxJsonInputSerDeOptions:
    def __init__(
        self,
        *,
        case_insensitive: typing.Optional[builtins.bool] = None,
        column_key_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        convert_dots_to_underscores: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param case_insensitive: 
        :param column_key_mappings: 
        :param convert_dots_to_underscores: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4da1e850bb46c941b499e58887f44a3981a8bcefec144c73bfb2411d856adc3)
            check_type(argname="argument case_insensitive", value=case_insensitive, expected_type=type_hints["case_insensitive"])
            check_type(argname="argument column_key_mappings", value=column_key_mappings, expected_type=type_hints["column_key_mappings"])
            check_type(argname="argument convert_dots_to_underscores", value=convert_dots_to_underscores, expected_type=type_hints["convert_dots_to_underscores"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if case_insensitive is not None:
            self._values["case_insensitive"] = case_insensitive
        if column_key_mappings is not None:
            self._values["column_key_mappings"] = column_key_mappings
        if convert_dots_to_underscores is not None:
            self._values["convert_dots_to_underscores"] = convert_dots_to_underscores

    @builtins.property
    def case_insensitive(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("case_insensitive")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def column_key_mappings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("column_key_mappings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def convert_dots_to_underscores(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("convert_dots_to_underscores")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenxJsonInputSerDeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.OrcCompressionFormat")
class OrcCompressionFormat(enum.Enum):
    NONE = "NONE"
    SNAPPY = "SNAPPY"
    ZLIB = "ZLIB"


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.OrcFormatVersion")
class OrcFormatVersion(enum.Enum):
    V0_11 = "V0_11"
    V0_12 = "V0_12"


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.OrcOutputSerDeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "block_size_bytes": "blockSizeBytes",
        "bloom_filter_columns": "bloomFilterColumns",
        "bloom_filter_false_positive_probability": "bloomFilterFalsePositiveProbability",
        "compression": "compression",
        "dictionary_key_threshold": "dictionaryKeyThreshold",
        "enable_padding": "enablePadding",
        "format_version": "formatVersion",
        "padding_tolerance": "paddingTolerance",
        "row_index_stride": "rowIndexStride",
        "stripe_size_bytes": "stripeSizeBytes",
    },
)
class OrcOutputSerDeOptions:
    def __init__(
        self,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
        compression: typing.Optional[OrcCompressionFormat] = None,
        dictionary_key_threshold: typing.Optional[jsii.Number] = None,
        enable_padding: typing.Optional[builtins.bool] = None,
        format_version: typing.Optional[OrcFormatVersion] = None,
        padding_tolerance: typing.Optional[jsii.Number] = None,
        row_index_stride: typing.Optional[jsii.Number] = None,
        stripe_size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param block_size_bytes: 
        :param bloom_filter_columns: 
        :param bloom_filter_false_positive_probability: 
        :param compression: 
        :param dictionary_key_threshold: 
        :param enable_padding: 
        :param format_version: 
        :param padding_tolerance: 
        :param row_index_stride: 
        :param stripe_size_bytes: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d09a85185c7411ebd1cf036ad4582ffd3a0fc8824517c745ac813f2db3ee008)
            check_type(argname="argument block_size_bytes", value=block_size_bytes, expected_type=type_hints["block_size_bytes"])
            check_type(argname="argument bloom_filter_columns", value=bloom_filter_columns, expected_type=type_hints["bloom_filter_columns"])
            check_type(argname="argument bloom_filter_false_positive_probability", value=bloom_filter_false_positive_probability, expected_type=type_hints["bloom_filter_false_positive_probability"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument dictionary_key_threshold", value=dictionary_key_threshold, expected_type=type_hints["dictionary_key_threshold"])
            check_type(argname="argument enable_padding", value=enable_padding, expected_type=type_hints["enable_padding"])
            check_type(argname="argument format_version", value=format_version, expected_type=type_hints["format_version"])
            check_type(argname="argument padding_tolerance", value=padding_tolerance, expected_type=type_hints["padding_tolerance"])
            check_type(argname="argument row_index_stride", value=row_index_stride, expected_type=type_hints["row_index_stride"])
            check_type(argname="argument stripe_size_bytes", value=stripe_size_bytes, expected_type=type_hints["stripe_size_bytes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if block_size_bytes is not None:
            self._values["block_size_bytes"] = block_size_bytes
        if bloom_filter_columns is not None:
            self._values["bloom_filter_columns"] = bloom_filter_columns
        if bloom_filter_false_positive_probability is not None:
            self._values["bloom_filter_false_positive_probability"] = bloom_filter_false_positive_probability
        if compression is not None:
            self._values["compression"] = compression
        if dictionary_key_threshold is not None:
            self._values["dictionary_key_threshold"] = dictionary_key_threshold
        if enable_padding is not None:
            self._values["enable_padding"] = enable_padding
        if format_version is not None:
            self._values["format_version"] = format_version
        if padding_tolerance is not None:
            self._values["padding_tolerance"] = padding_tolerance
        if row_index_stride is not None:
            self._values["row_index_stride"] = row_index_stride
        if stripe_size_bytes is not None:
            self._values["stripe_size_bytes"] = stripe_size_bytes

    @builtins.property
    def block_size_bytes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("block_size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bloom_filter_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("bloom_filter_columns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bloom_filter_false_positive_probability(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("bloom_filter_false_positive_probability")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def compression(self) -> typing.Optional[OrcCompressionFormat]:
        result = self._values.get("compression")
        return typing.cast(typing.Optional[OrcCompressionFormat], result)

    @builtins.property
    def dictionary_key_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("dictionary_key_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_padding(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_padding")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def format_version(self) -> typing.Optional[OrcFormatVersion]:
        result = self._values.get("format_version")
        return typing.cast(typing.Optional[OrcFormatVersion], result)

    @builtins.property
    def padding_tolerance(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("padding_tolerance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def row_index_stride(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("row_index_stride")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stripe_size_bytes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("stripe_size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrcOutputSerDeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OutputFormat(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-extensions.kinesis_firehose.OutputFormat",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="orc")
    @builtins.classmethod
    def orc(
        cls,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
        compression: typing.Optional[OrcCompressionFormat] = None,
        dictionary_key_threshold: typing.Optional[jsii.Number] = None,
        enable_padding: typing.Optional[builtins.bool] = None,
        format_version: typing.Optional[OrcFormatVersion] = None,
        padding_tolerance: typing.Optional[jsii.Number] = None,
        row_index_stride: typing.Optional[jsii.Number] = None,
        stripe_size_bytes: typing.Optional[jsii.Number] = None,
    ) -> "OrcOutputSerDe":
        '''
        :param block_size_bytes: 
        :param bloom_filter_columns: 
        :param bloom_filter_false_positive_probability: 
        :param compression: 
        :param dictionary_key_threshold: 
        :param enable_padding: 
        :param format_version: 
        :param padding_tolerance: 
        :param row_index_stride: 
        :param stripe_size_bytes: 
        '''
        options = OrcOutputSerDeOptions(
            block_size_bytes=block_size_bytes,
            bloom_filter_columns=bloom_filter_columns,
            bloom_filter_false_positive_probability=bloom_filter_false_positive_probability,
            compression=compression,
            dictionary_key_threshold=dictionary_key_threshold,
            enable_padding=enable_padding,
            format_version=format_version,
            padding_tolerance=padding_tolerance,
            row_index_stride=row_index_stride,
            stripe_size_bytes=stripe_size_bytes,
        )

        return typing.cast("OrcOutputSerDe", jsii.sinvoke(cls, "orc", [options]))

    @jsii.member(jsii_name="parquet")
    @builtins.classmethod
    def parquet(
        cls,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        compression: typing.Optional["ParquetCompressionFormat"] = None,
        enable_dictionary_compression: typing.Optional[builtins.bool] = None,
        max_padding_bytes: typing.Optional[jsii.Number] = None,
        page_size_bytes: typing.Optional[jsii.Number] = None,
        writer_version: typing.Optional["ParquetWriterVersion"] = None,
    ) -> "ParquetOutputSerDe":
        '''
        :param block_size_bytes: 
        :param compression: 
        :param enable_dictionary_compression: 
        :param max_padding_bytes: 
        :param page_size_bytes: 
        :param writer_version: 
        '''
        options = ParquetOutputSerDeOptions(
            block_size_bytes=block_size_bytes,
            compression=compression,
            enable_dictionary_compression=enable_dictionary_compression,
            max_padding_bytes=max_padding_bytes,
            page_size_bytes=page_size_bytes,
            writer_version=writer_version,
        )

        return typing.cast("ParquetOutputSerDe", jsii.sinvoke(cls, "parquet", [options]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty:
        '''
        :param scope: -
        '''
        ...


class _OutputFormatProxy(OutputFormat):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d80d4f975adaaf12da053053e041d05cca658eecca53198592932795cb30d2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, OutputFormat).__jsii_proxy_class__ = lambda : _OutputFormatProxy


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.ParquetCompressionFormat")
class ParquetCompressionFormat(enum.Enum):
    GZIP = "GZIP"
    SNAPPY = "SNAPPY"
    UNCOMPRESSED = "UNCOMPRESSED"


class ParquetOutputSerDe(
    OutputFormat,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.ParquetOutputSerDe",
):
    def __init__(
        self,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        compression: typing.Optional[ParquetCompressionFormat] = None,
        enable_dictionary_compression: typing.Optional[builtins.bool] = None,
        max_padding_bytes: typing.Optional[jsii.Number] = None,
        page_size_bytes: typing.Optional[jsii.Number] = None,
        writer_version: typing.Optional["ParquetWriterVersion"] = None,
    ) -> None:
        '''
        :param block_size_bytes: 
        :param compression: 
        :param enable_dictionary_compression: 
        :param max_padding_bytes: 
        :param page_size_bytes: 
        :param writer_version: 
        '''
        options = ParquetOutputSerDeOptions(
            block_size_bytes=block_size_bytes,
            compression=compression,
            enable_dictionary_compression=enable_dictionary_compression,
            max_padding_bytes=max_padding_bytes,
            page_size_bytes=page_size_bytes,
            writer_version=writer_version,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba8c2fd10a023a5ea5240bc06893dc4ef75de46a2c1c20c8d26453ea1c0fcf6)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty, jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="blockSizeBytes")
    def block_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockSizeBytes"))

    @builtins.property
    @jsii.member(jsii_name="compression")
    def compression(self) -> typing.Optional[ParquetCompressionFormat]:
        return typing.cast(typing.Optional[ParquetCompressionFormat], jsii.get(self, "compression"))

    @builtins.property
    @jsii.member(jsii_name="enableDictionaryCompression")
    def enable_dictionary_compression(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enableDictionaryCompression"))

    @builtins.property
    @jsii.member(jsii_name="maxPaddingBytes")
    def max_padding_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPaddingBytes"))

    @builtins.property
    @jsii.member(jsii_name="pageSizeBytes")
    def page_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pageSizeBytes"))

    @builtins.property
    @jsii.member(jsii_name="writerVersion")
    def writer_version(self) -> typing.Optional["ParquetWriterVersion"]:
        return typing.cast(typing.Optional["ParquetWriterVersion"], jsii.get(self, "writerVersion"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.ParquetOutputSerDeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "block_size_bytes": "blockSizeBytes",
        "compression": "compression",
        "enable_dictionary_compression": "enableDictionaryCompression",
        "max_padding_bytes": "maxPaddingBytes",
        "page_size_bytes": "pageSizeBytes",
        "writer_version": "writerVersion",
    },
)
class ParquetOutputSerDeOptions:
    def __init__(
        self,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        compression: typing.Optional[ParquetCompressionFormat] = None,
        enable_dictionary_compression: typing.Optional[builtins.bool] = None,
        max_padding_bytes: typing.Optional[jsii.Number] = None,
        page_size_bytes: typing.Optional[jsii.Number] = None,
        writer_version: typing.Optional["ParquetWriterVersion"] = None,
    ) -> None:
        '''
        :param block_size_bytes: 
        :param compression: 
        :param enable_dictionary_compression: 
        :param max_padding_bytes: 
        :param page_size_bytes: 
        :param writer_version: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d862a68d07b6ebaca9da690d424c92a8fab03bd999105e6835d0368a9cc3c73)
            check_type(argname="argument block_size_bytes", value=block_size_bytes, expected_type=type_hints["block_size_bytes"])
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument enable_dictionary_compression", value=enable_dictionary_compression, expected_type=type_hints["enable_dictionary_compression"])
            check_type(argname="argument max_padding_bytes", value=max_padding_bytes, expected_type=type_hints["max_padding_bytes"])
            check_type(argname="argument page_size_bytes", value=page_size_bytes, expected_type=type_hints["page_size_bytes"])
            check_type(argname="argument writer_version", value=writer_version, expected_type=type_hints["writer_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if block_size_bytes is not None:
            self._values["block_size_bytes"] = block_size_bytes
        if compression is not None:
            self._values["compression"] = compression
        if enable_dictionary_compression is not None:
            self._values["enable_dictionary_compression"] = enable_dictionary_compression
        if max_padding_bytes is not None:
            self._values["max_padding_bytes"] = max_padding_bytes
        if page_size_bytes is not None:
            self._values["page_size_bytes"] = page_size_bytes
        if writer_version is not None:
            self._values["writer_version"] = writer_version

    @builtins.property
    def block_size_bytes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("block_size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def compression(self) -> typing.Optional[ParquetCompressionFormat]:
        result = self._values.get("compression")
        return typing.cast(typing.Optional[ParquetCompressionFormat], result)

    @builtins.property
    def enable_dictionary_compression(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_dictionary_compression")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_padding_bytes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("max_padding_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def page_size_bytes(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("page_size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def writer_version(self) -> typing.Optional["ParquetWriterVersion"]:
        result = self._values.get("writer_version")
        return typing.cast(typing.Optional["ParquetWriterVersion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParquetOutputSerDeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.ParquetWriterVersion")
class ParquetWriterVersion(enum.Enum):
    V1 = "V1"
    V2 = "V2"


class ProcessorConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.ProcessorConfiguration",
):
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        processors: typing.Optional[typing.Sequence[DeliveryStreamProcessor]] = None,
    ) -> None:
        '''
        :param enabled: 
        :param processors: 
        '''
        options = ProcessorConfigurationOptions(enabled=enabled, processors=processors)

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> "ProcessorConfigurationResult":
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6698f7f8dfd5c9fd295ff07ff5bd3430a0b3aad4e57ef509a7fe58409362ff65)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast("ProcessorConfigurationResult", jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="processors")
    def processors(self) -> typing.Optional[typing.List[DeliveryStreamProcessor]]:
        return typing.cast(typing.Optional[typing.List[DeliveryStreamProcessor]], jsii.get(self, "processors"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.ProcessorConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "processors": "processors"},
)
class ProcessorConfigurationOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        processors: typing.Optional[typing.Sequence[DeliveryStreamProcessor]] = None,
    ) -> None:
        '''
        :param enabled: 
        :param processors: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c604ecfc5b3fcb6ecde672b2c1f0c49e055828f7173d8367b0d131a436d042a)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument processors", value=processors, expected_type=type_hints["processors"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if processors is not None:
            self._values["processors"] = processors

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def processors(self) -> typing.Optional[typing.List[DeliveryStreamProcessor]]:
        result = self._values.get("processors")
        return typing.cast(typing.Optional[typing.List[DeliveryStreamProcessor]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProcessorConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.ProcessorConfigurationResult",
    jsii_struct_bases=[],
    name_mapping={"processors": "processors", "enabled": "enabled"},
)
class ProcessorConfigurationResult:
    def __init__(
        self,
        *,
        processors: typing.Sequence[DeliveryStreamProcessor],
        enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param processors: 
        :param enabled: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1cf4ada63453854ae2e6f76805a3e74c5ddb698ae5bac1961357019ec14a8fd)
            check_type(argname="argument processors", value=processors, expected_type=type_hints["processors"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "processors": processors,
        }
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def processors(self) -> typing.List[DeliveryStreamProcessor]:
        result = self._values.get("processors")
        assert result is not None, "Required property 'processors' is missing"
        return typing.cast(typing.List[DeliveryStreamProcessor], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProcessorConfigurationResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProcessorType(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.ProcessorType",
):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "ProcessorType":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7de06d34b1cb43026a2df1e457a8c31bb6037e3435b4b5d994b35aab902da66a)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ProcessorType", jsii.sinvoke(cls, "of", [name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="APPEND_DELIMITER_TO_RECORD")
    def APPEND_DELIMITER_TO_RECORD(cls) -> "ProcessorType":
        return typing.cast("ProcessorType", jsii.sget(cls, "APPEND_DELIMITER_TO_RECORD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="LAMBDA")
    def LAMBDA_(cls) -> "ProcessorType":
        return typing.cast("ProcessorType", jsii.sget(cls, "LAMBDA"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="METADATA_EXTRACTION")
    def METADATA_EXTRACTION(cls) -> "ProcessorType":
        return typing.cast("ProcessorType", jsii.sget(cls, "METADATA_EXTRACTION"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RECORD_DEAGGREGATION")
    def RECORD_DEAGGREGATION(cls) -> "ProcessorType":
        return typing.cast("ProcessorType", jsii.sget(cls, "RECORD_DEAGGREGATION"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the processor to apply to the delivery stream.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))


class RecordDeaggregationProcessor(
    DeliveryStreamProcessor,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.RecordDeaggregationProcessor",
):
    def __init__(
        self,
        *,
        sub_record_type: "SubRecordType",
        delimiter: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param sub_record_type: 
        :param delimiter: 
        '''
        options = RecordDeaggregationProcessorOptions(
            sub_record_type=sub_record_type, delimiter=delimiter
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="delimited")
    @builtins.classmethod
    def delimited(cls, *, delimiter: builtins.str) -> "RecordDeaggregationProcessor":
        '''
        :param delimiter: 
        '''
        options = DelimitedDeaggregationOptions(delimiter=delimiter)

        return typing.cast("RecordDeaggregationProcessor", jsii.sinvoke(cls, "delimited", [options]))

    @jsii.member(jsii_name="json")
    @builtins.classmethod
    def json(cls) -> "RecordDeaggregationProcessor":
        return typing.cast("RecordDeaggregationProcessor", jsii.sinvoke(cls, "json", []))

    @builtins.property
    @jsii.member(jsii_name="subRecordType")
    def sub_record_type(self) -> "SubRecordType":
        return typing.cast("SubRecordType", jsii.get(self, "subRecordType"))

    @builtins.property
    @jsii.member(jsii_name="delimiter")
    def delimiter(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delimiter"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.RecordDeaggregationProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"sub_record_type": "subRecordType", "delimiter": "delimiter"},
)
class RecordDeaggregationProcessorOptions:
    def __init__(
        self,
        *,
        sub_record_type: "SubRecordType",
        delimiter: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param sub_record_type: 
        :param delimiter: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f754d0d19d385fdb87c2cbeef4e1761b3404e6d8ef29cb7cc7acee30f4dc8217)
            check_type(argname="argument sub_record_type", value=sub_record_type, expected_type=type_hints["sub_record_type"])
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sub_record_type": sub_record_type,
        }
        if delimiter is not None:
            self._values["delimiter"] = delimiter

    @builtins.property
    def sub_record_type(self) -> "SubRecordType":
        result = self._values.get("sub_record_type")
        assert result is not None, "Required property 'sub_record_type' is missing"
        return typing.cast("SubRecordType", result)

    @builtins.property
    def delimiter(self) -> typing.Optional[builtins.str]:
        result = self._values.get("delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecordDeaggregationProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-extensions.kinesis_firehose.S3CompressionFormat")
class S3CompressionFormat(enum.Enum):
    GZIP = "GZIP"
    HADOOP_SNAPPY = "HADOOP_SNAPPY"
    SNAPPY = "SNAPPY"
    UNCOMPRESSED = "UNCOMPRESSED"
    ZIP = "ZIP"


@jsii.implements(IDeliveryStreamBackupDestination)
class S3Destination(
    DeliveryStreamDestination,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.S3Destination",
):
    def __init__(
        self,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        *,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        compression_format: typing.Optional[S3CompressionFormat] = None,
        encryption_enabled: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        key_prefix: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param bucket: -
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param compression_format: 
        :param encryption_enabled: 
        :param encryption_key: 
        :param error_output_prefix: 
        :param key_prefix: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2173f9fb31d1332f76040a52e72bc980ef15a82f8558934300feb8e94767cb31)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        options = S3DestinationOptions(
            buffering=buffering,
            cloudwatch_logging_configuration=cloudwatch_logging_configuration,
            compression_format=compression_format,
            encryption_enabled=encryption_enabled,
            encryption_key=encryption_key,
            error_output_prefix=error_output_prefix,
            key_prefix=key_prefix,
            role=role,
        )

        jsii.create(self.__class__, self, [bucket, options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> DeliveryStreamDestinationConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f4d65756295ecfad272d0ef0118002fb31865c19caa22eaba3dc0e246f03b93)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(DeliveryStreamDestinationConfiguration, jsii.invoke(self, "bind", [scope]))

    @jsii.member(jsii_name="buildConfiguration")
    def _build_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c0d302f37ff09dc12e26d33f19da491a25a1215ed0a0c12b4f7cd60943d6655)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, jsii.invoke(self, "buildConfiguration", [scope]))

    @jsii.member(jsii_name="renderBackupConfiguration")
    def render_backup_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        enabled: typing.Optional[builtins.bool] = None,
    ) -> BackupConfigurationResult:
        '''
        :param scope: -
        :param enabled: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e7aaec8a7c3cea99db0df9d5ceb2edd3fd94a77c22f7c4f4c7907d2a5fcad1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        return typing.cast(BackupConfigurationResult, jsii.invoke(self, "renderBackupConfiguration", [scope, enabled]))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="buffering")
    def buffering(self) -> typing.Optional[BufferingConfiguration]:
        return typing.cast(typing.Optional[BufferingConfiguration], jsii.get(self, "buffering"))

    @builtins.property
    @jsii.member(jsii_name="cloudwatchLoggingConfiguration")
    def cloudwatch_logging_configuration(
        self,
    ) -> typing.Optional[CloudWatchLoggingConfiguration]:
        return typing.cast(typing.Optional[CloudWatchLoggingConfiguration], jsii.get(self, "cloudwatchLoggingConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="compressionFormat")
    def compression_format(self) -> typing.Optional[S3CompressionFormat]:
        return typing.cast(typing.Optional[S3CompressionFormat], jsii.get(self, "compressionFormat"))

    @builtins.property
    @jsii.member(jsii_name="encryptionEnabled")
    def encryption_enabled(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "encryptionEnabled"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="errorOutputPrefix")
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorOutputPrefix"))

    @builtins.property
    @jsii.member(jsii_name="keyPrefix")
    def key_prefix(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPrefix"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.S3DestinationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "buffering": "buffering",
        "cloudwatch_logging_configuration": "cloudwatchLoggingConfiguration",
        "compression_format": "compressionFormat",
        "encryption_enabled": "encryptionEnabled",
        "encryption_key": "encryptionKey",
        "error_output_prefix": "errorOutputPrefix",
        "key_prefix": "keyPrefix",
        "role": "role",
    },
)
class S3DestinationOptions:
    def __init__(
        self,
        *,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        compression_format: typing.Optional[S3CompressionFormat] = None,
        encryption_enabled: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        key_prefix: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param compression_format: 
        :param encryption_enabled: 
        :param encryption_key: 
        :param error_output_prefix: 
        :param key_prefix: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f212129c39076aa4cd62be0c8c9d0cfbcbce14e466cdd06aaeb7e05b41e21ad5)
            check_type(argname="argument buffering", value=buffering, expected_type=type_hints["buffering"])
            check_type(argname="argument cloudwatch_logging_configuration", value=cloudwatch_logging_configuration, expected_type=type_hints["cloudwatch_logging_configuration"])
            check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
            check_type(argname="argument encryption_enabled", value=encryption_enabled, expected_type=type_hints["encryption_enabled"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument error_output_prefix", value=error_output_prefix, expected_type=type_hints["error_output_prefix"])
            check_type(argname="argument key_prefix", value=key_prefix, expected_type=type_hints["key_prefix"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if buffering is not None:
            self._values["buffering"] = buffering
        if cloudwatch_logging_configuration is not None:
            self._values["cloudwatch_logging_configuration"] = cloudwatch_logging_configuration
        if compression_format is not None:
            self._values["compression_format"] = compression_format
        if encryption_enabled is not None:
            self._values["encryption_enabled"] = encryption_enabled
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if error_output_prefix is not None:
            self._values["error_output_prefix"] = error_output_prefix
        if key_prefix is not None:
            self._values["key_prefix"] = key_prefix
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def buffering(self) -> typing.Optional[BufferingConfiguration]:
        result = self._values.get("buffering")
        return typing.cast(typing.Optional[BufferingConfiguration], result)

    @builtins.property
    def cloudwatch_logging_configuration(
        self,
    ) -> typing.Optional[CloudWatchLoggingConfiguration]:
        result = self._values.get("cloudwatch_logging_configuration")
        return typing.cast(typing.Optional[CloudWatchLoggingConfiguration], result)

    @builtins.property
    def compression_format(self) -> typing.Optional[S3CompressionFormat]:
        result = self._values.get("compression_format")
        return typing.cast(typing.Optional[S3CompressionFormat], result)

    @builtins.property
    def encryption_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("encryption_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("error_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3DestinationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SubRecordType(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.SubRecordType",
):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "SubRecordType":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c4dd6d768375f11ad311e245c05d52cd892631b67637fd4a5c28c9678957f74)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SubRecordType", jsii.sinvoke(cls, "of", [name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DELIMITED")
    def DELIMITED(cls) -> "SubRecordType":
        return typing.cast("SubRecordType", jsii.sget(cls, "DELIMITED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="JSON")
    def JSON(cls) -> "SubRecordType":
        return typing.cast("SubRecordType", jsii.sget(cls, "JSON"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


class TableVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.TableVersion",
):
    @jsii.member(jsii_name="fixed")
    @builtins.classmethod
    def fixed(cls, version: jsii.Number) -> "TableVersion":
        '''
        :param version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__affa572d1b41a58fff582888d3251719057a9b8fd0e5dac5416dc6d6b8210ee0)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("TableVersion", jsii.sinvoke(cls, "fixed", [version]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="LATEST")
    def LATEST(cls) -> "TableVersion":
        return typing.cast("TableVersion", jsii.sget(cls, "LATEST"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))


class AppendDelimiterProcessor(
    DeliveryStreamProcessor,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.AppendDelimiterProcessor",
):
    def __init__(self, *, delimiter: builtins.str) -> None:
        '''
        :param delimiter: 
        '''
        options = AppendDelimiterProcessorOptions(delimiter=delimiter)

        jsii.create(self.__class__, self, [options])

    @builtins.property
    @jsii.member(jsii_name="delimiter")
    def delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delimiter"))


class CustomProcessor(
    DeliveryStreamProcessor,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.CustomProcessor",
):
    def __init__(
        self,
        *,
        processor_type: ProcessorType,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param processor_type: 
        :param parameters: 
        '''
        options = CustomProcessorOptions(
            processor_type=processor_type, parameters=parameters
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addParameter")
    def add_parameter(self, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__981f6e4d4206e5975906def40f5d872f1a70311d865f3888c663bff6bb53ed0b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "addParameter", [name, value]))


@jsii.implements(IDeliveryStream)
class DeliveryStream(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.DeliveryStream",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destination: DeliveryStreamDestination,
        name: typing.Optional[builtins.str] = None,
        stream_type: typing.Optional[DeliveryStreamType] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param destination: 
        :param name: 
        :param stream_type: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05502f0a2424a622eb9bd08c2b9ca4c578d1a74c76dbb938f6e135f7bb7d7824)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DeliveryStreamProps(
            destination=destination,
            name=name,
            stream_type=stream_type,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDeliveryStreamArn")
    @builtins.classmethod
    def from_delivery_stream_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        delivery_stream_arn: builtins.str,
    ) -> IDeliveryStream:
        '''
        :param scope: -
        :param id: -
        :param delivery_stream_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7b2a202fd5e395337cd7320a23cccb8c3885c51213c80e91fcc0debd8264dab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument delivery_stream_arn", value=delivery_stream_arn, expected_type=type_hints["delivery_stream_arn"])
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamArn", [scope, id, delivery_stream_arn]))

    @jsii.member(jsii_name="fromDeliveryStreamAttributes")
    @builtins.classmethod
    def from_delivery_stream_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IDeliveryStream:
        '''
        :param scope: -
        :param id: -
        :param delivery_stream_arn: 
        :param delivery_stream_name: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcd890c63d90230882b54e159c2228f2581fafd2daff62b2043980c1b885d0e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = DeliveryStreamAttributes(
            delivery_stream_arn=delivery_stream_arn,
            delivery_stream_name=delivery_stream_name,
            role=role,
        )

        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromDeliveryStreamName")
    @builtins.classmethod
    def from_delivery_stream_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        delivery_stream_name: builtins.str,
    ) -> IDeliveryStream:
        '''
        :param scope: -
        :param id: -
        :param delivery_stream_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8663b0c16974ee37e5785c89fd5048ece6ae3576c9b53ba242065131936b047d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamName", [scope, id, delivery_stream_name]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7fb9d82b9db30c958e61aacfc3020c3b1ce603b1db2e2a49ff02a428600d34a)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''
        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5487fc013c2e4b4254ecdcdb31ad68fde013145ed1446cc20eb1c60fbf23f54)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47205f9db0c76835c43eb68375cdad796e54aff9182a699ff35ccfc0fa290297)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The network connections associated with this resource.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> DeliveryStreamDestination:
        return typing.cast(DeliveryStreamDestination, jsii.get(self, "destination"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''The principal to grant permissions to.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream:
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="streamType")
    def stream_type(self) -> typing.Optional[DeliveryStreamType]:
        return typing.cast(typing.Optional[DeliveryStreamType], jsii.get(self, "streamType"))


class ExtendedS3Destination(
    S3Destination,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.ExtendedS3Destination",
):
    def __init__(
        self,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        *,
        backup_configuration: typing.Optional[BackupConfiguration] = None,
        data_format_conversion: typing.Optional[DataFormatConversion] = None,
        dynamic_partitioning: typing.Optional[DynamicPartitioning] = None,
        processor_configuration: typing.Optional[ProcessorConfiguration] = None,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        compression_format: typing.Optional[S3CompressionFormat] = None,
        encryption_enabled: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        key_prefix: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param bucket: -
        :param backup_configuration: 
        :param data_format_conversion: 
        :param dynamic_partitioning: 
        :param processor_configuration: 
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param compression_format: 
        :param encryption_enabled: 
        :param encryption_key: 
        :param error_output_prefix: 
        :param key_prefix: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3db0370cdc505b0fc87af66fb0a1af05cbc69ed5741001e2791add576b265bf9)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        options = ExtendedS3DestinationOptions(
            backup_configuration=backup_configuration,
            data_format_conversion=data_format_conversion,
            dynamic_partitioning=dynamic_partitioning,
            processor_configuration=processor_configuration,
            buffering=buffering,
            cloudwatch_logging_configuration=cloudwatch_logging_configuration,
            compression_format=compression_format,
            encryption_enabled=encryption_enabled,
            encryption_key=encryption_key,
            error_output_prefix=error_output_prefix,
            key_prefix=key_prefix,
            role=role,
        )

        jsii.create(self.__class__, self, [bucket, options])

    @jsii.member(jsii_name="addProcessor")
    def add_processor(
        self,
        processor: DeliveryStreamProcessor,
    ) -> "ExtendedS3Destination":
        '''
        :param processor: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7687e5a52e65228aa5e0c0fe2ef72a90ef690f5913e2e63f3d150ebab5b7098)
            check_type(argname="argument processor", value=processor, expected_type=type_hints["processor"])
        return typing.cast("ExtendedS3Destination", jsii.invoke(self, "addProcessor", [processor]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> DeliveryStreamDestinationConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27ed02c2cc71a60d26ac324c75fe5c990faaa34885fc10dafc05efc1d4b488c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(DeliveryStreamDestinationConfiguration, jsii.invoke(self, "bind", [scope]))

    @jsii.member(jsii_name="renderProcessorConfiguration")
    def _render_processor_configuration(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessingConfigurationProperty]:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61b88324642c4949dd64693f19afba43b19d0a89fab9dc832dde888ce03760d6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ProcessingConfigurationProperty], jsii.invoke(self, "renderProcessorConfiguration", [scope]))

    @builtins.property
    @jsii.member(jsii_name="processingEnabled")
    def processing_enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "processingEnabled"))

    @builtins.property
    @jsii.member(jsii_name="processors")
    def processors(self) -> typing.List[DeliveryStreamProcessor]:
        return typing.cast(typing.List[DeliveryStreamProcessor], jsii.get(self, "processors"))

    @builtins.property
    @jsii.member(jsii_name="backupConfiguration")
    def backup_configuration(self) -> typing.Optional[BackupConfiguration]:
        return typing.cast(typing.Optional[BackupConfiguration], jsii.get(self, "backupConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="dataFormatConversion")
    def data_format_conversion(self) -> typing.Optional[DataFormatConversion]:
        return typing.cast(typing.Optional[DataFormatConversion], jsii.get(self, "dataFormatConversion"))

    @builtins.property
    @jsii.member(jsii_name="dynamicPartitioning")
    def dynamic_partitioning(self) -> typing.Optional[DynamicPartitioning]:
        return typing.cast(typing.Optional[DynamicPartitioning], jsii.get(self, "dynamicPartitioning"))

    @builtins.property
    @jsii.member(jsii_name="processorConfiguration")
    def processor_configuration(self) -> typing.Optional[ProcessorConfiguration]:
        return typing.cast(typing.Optional[ProcessorConfiguration], jsii.get(self, "processorConfiguration"))


@jsii.data_type(
    jsii_type="cdk-extensions.kinesis_firehose.ExtendedS3DestinationOptions",
    jsii_struct_bases=[S3DestinationOptions],
    name_mapping={
        "buffering": "buffering",
        "cloudwatch_logging_configuration": "cloudwatchLoggingConfiguration",
        "compression_format": "compressionFormat",
        "encryption_enabled": "encryptionEnabled",
        "encryption_key": "encryptionKey",
        "error_output_prefix": "errorOutputPrefix",
        "key_prefix": "keyPrefix",
        "role": "role",
        "backup_configuration": "backupConfiguration",
        "data_format_conversion": "dataFormatConversion",
        "dynamic_partitioning": "dynamicPartitioning",
        "processor_configuration": "processorConfiguration",
    },
)
class ExtendedS3DestinationOptions(S3DestinationOptions):
    def __init__(
        self,
        *,
        buffering: typing.Optional[BufferingConfiguration] = None,
        cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
        compression_format: typing.Optional[S3CompressionFormat] = None,
        encryption_enabled: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        key_prefix: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        backup_configuration: typing.Optional[BackupConfiguration] = None,
        data_format_conversion: typing.Optional[DataFormatConversion] = None,
        dynamic_partitioning: typing.Optional[DynamicPartitioning] = None,
        processor_configuration: typing.Optional[ProcessorConfiguration] = None,
    ) -> None:
        '''
        :param buffering: 
        :param cloudwatch_logging_configuration: 
        :param compression_format: 
        :param encryption_enabled: 
        :param encryption_key: 
        :param error_output_prefix: 
        :param key_prefix: 
        :param role: 
        :param backup_configuration: 
        :param data_format_conversion: 
        :param dynamic_partitioning: 
        :param processor_configuration: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41ba06e3892af24422a75e1d7751c5be4d95052b00e8e89a92b0640704d35418)
            check_type(argname="argument buffering", value=buffering, expected_type=type_hints["buffering"])
            check_type(argname="argument cloudwatch_logging_configuration", value=cloudwatch_logging_configuration, expected_type=type_hints["cloudwatch_logging_configuration"])
            check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
            check_type(argname="argument encryption_enabled", value=encryption_enabled, expected_type=type_hints["encryption_enabled"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument error_output_prefix", value=error_output_prefix, expected_type=type_hints["error_output_prefix"])
            check_type(argname="argument key_prefix", value=key_prefix, expected_type=type_hints["key_prefix"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument backup_configuration", value=backup_configuration, expected_type=type_hints["backup_configuration"])
            check_type(argname="argument data_format_conversion", value=data_format_conversion, expected_type=type_hints["data_format_conversion"])
            check_type(argname="argument dynamic_partitioning", value=dynamic_partitioning, expected_type=type_hints["dynamic_partitioning"])
            check_type(argname="argument processor_configuration", value=processor_configuration, expected_type=type_hints["processor_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if buffering is not None:
            self._values["buffering"] = buffering
        if cloudwatch_logging_configuration is not None:
            self._values["cloudwatch_logging_configuration"] = cloudwatch_logging_configuration
        if compression_format is not None:
            self._values["compression_format"] = compression_format
        if encryption_enabled is not None:
            self._values["encryption_enabled"] = encryption_enabled
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if error_output_prefix is not None:
            self._values["error_output_prefix"] = error_output_prefix
        if key_prefix is not None:
            self._values["key_prefix"] = key_prefix
        if role is not None:
            self._values["role"] = role
        if backup_configuration is not None:
            self._values["backup_configuration"] = backup_configuration
        if data_format_conversion is not None:
            self._values["data_format_conversion"] = data_format_conversion
        if dynamic_partitioning is not None:
            self._values["dynamic_partitioning"] = dynamic_partitioning
        if processor_configuration is not None:
            self._values["processor_configuration"] = processor_configuration

    @builtins.property
    def buffering(self) -> typing.Optional[BufferingConfiguration]:
        result = self._values.get("buffering")
        return typing.cast(typing.Optional[BufferingConfiguration], result)

    @builtins.property
    def cloudwatch_logging_configuration(
        self,
    ) -> typing.Optional[CloudWatchLoggingConfiguration]:
        result = self._values.get("cloudwatch_logging_configuration")
        return typing.cast(typing.Optional[CloudWatchLoggingConfiguration], result)

    @builtins.property
    def compression_format(self) -> typing.Optional[S3CompressionFormat]:
        result = self._values.get("compression_format")
        return typing.cast(typing.Optional[S3CompressionFormat], result)

    @builtins.property
    def encryption_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("encryption_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("error_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def backup_configuration(self) -> typing.Optional[BackupConfiguration]:
        result = self._values.get("backup_configuration")
        return typing.cast(typing.Optional[BackupConfiguration], result)

    @builtins.property
    def data_format_conversion(self) -> typing.Optional[DataFormatConversion]:
        result = self._values.get("data_format_conversion")
        return typing.cast(typing.Optional[DataFormatConversion], result)

    @builtins.property
    def dynamic_partitioning(self) -> typing.Optional[DynamicPartitioning]:
        result = self._values.get("dynamic_partitioning")
        return typing.cast(typing.Optional[DynamicPartitioning], result)

    @builtins.property
    def processor_configuration(self) -> typing.Optional[ProcessorConfiguration]:
        result = self._values.get("processor_configuration")
        return typing.cast(typing.Optional[ProcessorConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtendedS3DestinationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HiveJsonInputSerDe(
    InputFormat,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.HiveJsonInputSerDe",
):
    def __init__(
        self,
        *,
        timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param timestamp_formats: 
        '''
        options = HiveJsonInputSerDeOptions(timestamp_formats=timestamp_formats)

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addTimestampFormat")
    def add_timestamp_format(self, format: builtins.str) -> "HiveJsonInputSerDe":
        '''
        :param format: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7e3a019b1c8b6718bc5f40a8483afbea2e5140654d293521505958c016c5da9)
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
        return typing.cast("HiveJsonInputSerDe", jsii.invoke(self, "addTimestampFormat", [format]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3768077bea7745cf8ccb2ced138636da879e3caa2fe1e2046122d5de31d59d)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.InputFormatConfigurationProperty, jsii.invoke(self, "bind", [_scope]))


class JsonQuery(
    MetaDataExtractionQuery,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.JsonQuery",
):
    def __init__(
        self,
        fields: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param fields: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62c7532847c88c105cfbbd6d3b50fe376eb8da94bca232ba95d5c19c3fbffb28)
            check_type(argname="argument fields", value=fields, expected_type=type_hints["fields"])
        jsii.create(self.__class__, self, [fields])

    @jsii.member(jsii_name="addField")
    def add_field(self, name: builtins.str, query: builtins.str) -> "JsonQuery":
        '''
        :param name: -
        :param query: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c5b3849cfae6e8c90ca34382ec0df4ab7f648d847a1f98d6fc2242366e40f57)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        return typing.cast("JsonQuery", jsii.invoke(self, "addField", [name, query]))


class OrcOutputSerDe(
    OutputFormat,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.kinesis_firehose.OrcOutputSerDe",
):
    def __init__(
        self,
        *,
        block_size_bytes: typing.Optional[jsii.Number] = None,
        bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
        bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
        compression: typing.Optional[OrcCompressionFormat] = None,
        dictionary_key_threshold: typing.Optional[jsii.Number] = None,
        enable_padding: typing.Optional[builtins.bool] = None,
        format_version: typing.Optional[OrcFormatVersion] = None,
        padding_tolerance: typing.Optional[jsii.Number] = None,
        row_index_stride: typing.Optional[jsii.Number] = None,
        stripe_size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param block_size_bytes: 
        :param bloom_filter_columns: 
        :param bloom_filter_false_positive_probability: 
        :param compression: 
        :param dictionary_key_threshold: 
        :param enable_padding: 
        :param format_version: 
        :param padding_tolerance: 
        :param row_index_stride: 
        :param stripe_size_bytes: 
        '''
        options = OrcOutputSerDeOptions(
            block_size_bytes=block_size_bytes,
            bloom_filter_columns=bloom_filter_columns,
            bloom_filter_false_positive_probability=bloom_filter_false_positive_probability,
            compression=compression,
            dictionary_key_threshold=dictionary_key_threshold,
            enable_padding=enable_padding,
            format_version=format_version,
            padding_tolerance=padding_tolerance,
            row_index_stride=row_index_stride,
            stripe_size_bytes=stripe_size_bytes,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addBloomFilterColumn")
    def add_bloom_filter_column(self, column: builtins.str) -> "OrcOutputSerDe":
        '''
        :param column: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eae0c95f4d76129b2fe013df0e9fb2400b7cc6b7ff3bf88e4d385dc6a9b6b64f)
            check_type(argname="argument column", value=column, expected_type=type_hints["column"])
        return typing.cast("OrcOutputSerDe", jsii.invoke(self, "addBloomFilterColumn", [column]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.IConstruct,
    ) -> _aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0facf543819a4a7f987c9cea643d1c6112ec140d5bc8ab02f8a0bb9e3dd2bf50)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.OutputFormatConfigurationProperty, jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="blockSizeBytes")
    def block_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "blockSizeBytes"))

    @builtins.property
    @jsii.member(jsii_name="bloomFilterColumns")
    def bloom_filter_columns(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "bloomFilterColumns"))

    @builtins.property
    @jsii.member(jsii_name="bloomFilterFalsePositiveProbability")
    def bloom_filter_false_positive_probability(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bloomFilterFalsePositiveProbability"))

    @builtins.property
    @jsii.member(jsii_name="compression")
    def compression(self) -> typing.Optional[OrcCompressionFormat]:
        return typing.cast(typing.Optional[OrcCompressionFormat], jsii.get(self, "compression"))

    @builtins.property
    @jsii.member(jsii_name="dictionaryKeyThreshold")
    def dictionary_key_threshold(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dictionaryKeyThreshold"))

    @builtins.property
    @jsii.member(jsii_name="enablePadding")
    def enable_padding(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enablePadding"))

    @builtins.property
    @jsii.member(jsii_name="formatVersion")
    def format_version(self) -> typing.Optional[OrcFormatVersion]:
        return typing.cast(typing.Optional[OrcFormatVersion], jsii.get(self, "formatVersion"))

    @builtins.property
    @jsii.member(jsii_name="paddingTolerance")
    def padding_tolerance(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "paddingTolerance"))

    @builtins.property
    @jsii.member(jsii_name="rowIndexStride")
    def row_index_stride(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rowIndexStride"))

    @builtins.property
    @jsii.member(jsii_name="stripeSizeBytes")
    def stripe_size_bytes(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "stripeSizeBytes"))


__all__ = [
    "AppendDelimiterProcessor",
    "AppendDelimiterProcessorOptions",
    "BackupConfiguration",
    "BackupConfigurationOptions",
    "BackupConfigurationResult",
    "BufferingConfiguration",
    "BufferingConfigurationOptions",
    "CloudWatchLoggingConfiguration",
    "CloudWatchLoggingConfigurationOptions",
    "CommonPartitioningOptions",
    "ContentEncoding",
    "CustomProcessor",
    "CustomProcessorOptions",
    "DataFormatConversion",
    "DataFormatConversionOptions",
    "DelimitedDeaggregationOptions",
    "DeliveryStream",
    "DeliveryStreamAttributes",
    "DeliveryStreamDestination",
    "DeliveryStreamDestinationConfiguration",
    "DeliveryStreamProcessor",
    "DeliveryStreamProcessorOptions",
    "DeliveryStreamProps",
    "DeliveryStreamType",
    "DynamicPartitioning",
    "DynamicPartitioningConfiguration",
    "ExtendedS3Destination",
    "ExtendedS3DestinationOptions",
    "HiveJsonInputSerDe",
    "HiveJsonInputSerDeOptions",
    "HttpEndpointDestination",
    "HttpEndpointDestinationOptions",
    "IDeliveryStream",
    "IDeliveryStreamBackupDestination",
    "InputFormat",
    "JsonParsingEngine",
    "JsonPartitioningOptions",
    "JsonPartitioningSource",
    "JsonQuery",
    "LambdaPartitioningOptions",
    "LambdaPartitioningSource",
    "LambdaProcessor",
    "LambdaProcessorOptions",
    "MetaDataExtractionQuery",
    "MetadataExtractionProcessor",
    "MetadataExtractionProcessorOptions",
    "OpenxJsonInputSerDe",
    "OpenxJsonInputSerDeOptions",
    "OrcCompressionFormat",
    "OrcFormatVersion",
    "OrcOutputSerDe",
    "OrcOutputSerDeOptions",
    "OutputFormat",
    "ParquetCompressionFormat",
    "ParquetOutputSerDe",
    "ParquetOutputSerDeOptions",
    "ParquetWriterVersion",
    "ProcessorConfiguration",
    "ProcessorConfigurationOptions",
    "ProcessorConfigurationResult",
    "ProcessorType",
    "RecordDeaggregationProcessor",
    "RecordDeaggregationProcessorOptions",
    "S3CompressionFormat",
    "S3Destination",
    "S3DestinationOptions",
    "SubRecordType",
    "TableVersion",
]

publication.publish()

def _typecheckingstub__4d89cbf1928d2e92a6f324db6cf3cc7bfce4f5462b42f0a2c2441d56ec253fd7(
    *,
    delimiter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39eeb1ec9ea9eedecc9eb4e100a7292a06bfbf35fee776a4c6e026bbe5311593(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b823f6ef73a229f88b0512bf65acd3fc7ed4339f19ab4c804d7afaeaf85f7f08(
    *,
    destination: IDeliveryStreamBackupDestination,
    enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72bd9180ce9c696a91ceb3527c6ae02102aec7e84c061131f3018798060b08c4(
    *,
    s3_backup_configuration: typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]],
    s3_backup_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0eed7bb4fde4a6987300bd36297cf67f0616aceeba5a6791afd9f373526bd25(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d59d5b3f0eed355b5cbd9da2160d4889272b5dcde9045cf9e5052d9e828192(
    *,
    interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    size_in_mb: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5e2c7d3332348dce4e30482a87105eac01663461092f0049ebdb74f3d1f2ff(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ecec857bb4ba40438742cd87f379b7e20785adf28d3923c5ce0b766abd16c1c(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    log_stream: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogStream] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75d6a25de990c726583508ec70890fce216775086c75be0c640c664e4c58b420(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78eae023c40cee15f57bf2117b663e893117034113c0c434c7503e6dc039d504(
    *,
    processor_type: ProcessorType,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f34563e2a338b831b08054a8158cbd3bec4ae881f2f6e2da967dacfec61a44df(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9567fc6b66b0e53903494269a652d394f7cc50bac28b4ba8aa05c042942cbdd0(
    *,
    database: _Database_5971ae38,
    input_format: InputFormat,
    output_format: OutputFormat,
    table: _Table_114d5aef,
    catalog_id: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[builtins.bool] = None,
    region: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version: typing.Optional[TableVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f18e1356030ed7e6e9769bc02289a51fae7c3b805209bde84ef0204406cdc297(
    *,
    delimiter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5070987c69666d624d69af7fd0e1b1930354030e542513b8a2efe27b4188a31(
    *,
    delivery_stream_arn: typing.Optional[builtins.str] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41587c0ee8bc81bcc496a1b1197d62bf43fe2c2ff76c9b7511f0a5d2b21f153a(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff5c5fd4c2fde1759984bade800eb7acb9b938f66435a1eeb50642a1ab888d9(
    *,
    amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    extended_s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.RedshiftDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.SplunkDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__392f37faf2c6e54ea42383b8a1706ddb8cd3e52cabfdcb5e5c3af36d5fcdf7eb(
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a58ae9fb2fa71b23b2dd37c0b9b517eb33b12ffcf1679c535d8870179ec79b9(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4633e8d78e091ab02719695d8d2c88323161cacd6cb9bd6639fa12b351454aff(
    *,
    processor_type: ProcessorType,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__440cfb7edd010dcdea81cac29f91707905f287c17f672fedbb1ebcaba556b7a1(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    destination: DeliveryStreamDestination,
    name: typing.Optional[builtins.str] = None,
    stream_type: typing.Optional[DeliveryStreamType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2bd84810b50cb68268c2a97bfe1b190becaf4e80f78f04b0cb9893b592b4ff8(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5916bca326decbc140e0564c1a76889229c1ec60795e765e7936bb66704859c(
    *,
    partitioning_configuration: typing.Union[_aws_cdk_aws_kinesisfirehose_ceddda9d.CfnDeliveryStream.DynamicPartitioningConfigurationProperty, typing.Dict[builtins.str, typing.Any]],
    processors: typing.Optional[typing.Sequence[DeliveryStreamProcessor]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b0084542b1ce34e535ddbf630f88e241e5c77ee3aca6a6f2b7f3d734a1e0e26(
    *,
    timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6582b21a2533517358f209922ce90e2a7f4cd38f6753705d50def9ea3a7e44b1(
    url: builtins.str,
    *,
    access_key: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    backup_configuration: typing.Optional[BackupConfiguration] = None,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    common_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    content_encoding: typing.Optional[ContentEncoding] = None,
    endpoint_name: typing.Optional[builtins.str] = None,
    processor_configuration: typing.Optional[ProcessorConfiguration] = None,
    retry_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7fd3de331f3de9e6cf31b86e6897c829a5de47c3a0d181bf976b007b5b6a444(
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50521eaec241f51d9f40a0cb9e9ff249c81ff399a57814426fdca964e29403f7(
    processor: DeliveryStreamProcessor,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e7d3b1d23f51b37027fac0cc97ddbf20afdec2b7a352579db009d48496a8d1(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d531d1e5cdd19cc324f9f73ef7f210530200b242626cf917de7bc71db40b832a(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bed9b7561cbeae33da160c724a0a82b7ab489c26312e7e4042cd7bd4ff674936(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a39f3047199326013e7d9897ee142decf1c2c6dad9a6900daafa1bf1f6d94c8(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f22be593ceb1483c63bf50da018e6c92f4a317b11a6b951c5bfd60a0a713ad0(
    *,
    access_key: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    backup_configuration: typing.Optional[BackupConfiguration] = None,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    common_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    content_encoding: typing.Optional[ContentEncoding] = None,
    endpoint_name: typing.Optional[builtins.str] = None,
    processor_configuration: typing.Optional[ProcessorConfiguration] = None,
    retry_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf7bcbe9748a6da845cceb739b108bffe77c724cee970b1c266a6a3f202b9272(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b93bb27770d9b8546ee8588396fce92c33131b61b55f0e09c5be13e362589ca(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf65fe3d702e9cb684464674963ccf372b5514566edde6bc90567ac3428b4ab2(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0342c34585fb8eaed0dac1dc61ffa2c0d173d315ac38ef2182806ef6d38aea22(
    scope: _constructs_77d1e7e8.IConstruct,
    enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a19f76095e079e46f5f7165b14aa5174f980d9a8da4779646f8aaeda38c063(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba50ad7522466bb0437400cbe9a708cb5f284208a7da53fdac531bd091ea4418(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    partitions: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99613095e9e0b584d502e7e0a99aa1a9afdf6b641e1edff1691cc6e76cc172f0(
    name: builtins.str,
    query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d0e96c22d2b377915c808428e42408811ebe6b4ec98aa4c634992d1e433b3e(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33af2c81bc5a83bb701c31329741ebf03be603636bd2333602e214020eac0ed0(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    retry_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9a4c8f309bd9a368157f94cf9541a573da0fb985b70ce340bda80e4b48d4be(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955a878a98a24d4bb0c4e55d76bd5c20e36162215a3b05dc533898b69b8be1b5(
    *,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__169f59ac5ef018ff3132111f756fe912271effad7f2fb91cabc8bd84dcba81db(
    query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1c87bfa00fa0b282a284d13ed075f362fece18bb715bb6b13ec033e3969920e(
    fields: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab103735cc2be78f22e2df46e8008a770f114052c04d2d227ddce0a993c0579(
    query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b8c72648253650e08268e4eff28118ed70690a4925325ba11244527c440ec4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce29299765030b4b969264a272477e1caee2edf4fc3f0cc7e53f0cd073912374(
    *,
    query: MetaDataExtractionQuery,
    engine: typing.Optional[JsonParsingEngine] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0033a54ad96b9adb2c19922659ad359d1f977d89d613ba53b97a968e66589b0(
    column_name: builtins.str,
    json_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47bddcfdf0e5e4c9e12bd12d4ee77b28ad079fc718636fd27a63f16baa38c981(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4da1e850bb46c941b499e58887f44a3981a8bcefec144c73bfb2411d856adc3(
    *,
    case_insensitive: typing.Optional[builtins.bool] = None,
    column_key_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    convert_dots_to_underscores: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d09a85185c7411ebd1cf036ad4582ffd3a0fc8824517c745ac813f2db3ee008(
    *,
    block_size_bytes: typing.Optional[jsii.Number] = None,
    bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
    compression: typing.Optional[OrcCompressionFormat] = None,
    dictionary_key_threshold: typing.Optional[jsii.Number] = None,
    enable_padding: typing.Optional[builtins.bool] = None,
    format_version: typing.Optional[OrcFormatVersion] = None,
    padding_tolerance: typing.Optional[jsii.Number] = None,
    row_index_stride: typing.Optional[jsii.Number] = None,
    stripe_size_bytes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d80d4f975adaaf12da053053e041d05cca658eecca53198592932795cb30d2(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba8c2fd10a023a5ea5240bc06893dc4ef75de46a2c1c20c8d26453ea1c0fcf6(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d862a68d07b6ebaca9da690d424c92a8fab03bd999105e6835d0368a9cc3c73(
    *,
    block_size_bytes: typing.Optional[jsii.Number] = None,
    compression: typing.Optional[ParquetCompressionFormat] = None,
    enable_dictionary_compression: typing.Optional[builtins.bool] = None,
    max_padding_bytes: typing.Optional[jsii.Number] = None,
    page_size_bytes: typing.Optional[jsii.Number] = None,
    writer_version: typing.Optional[ParquetWriterVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6698f7f8dfd5c9fd295ff07ff5bd3430a0b3aad4e57ef509a7fe58409362ff65(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c604ecfc5b3fcb6ecde672b2c1f0c49e055828f7173d8367b0d131a436d042a(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    processors: typing.Optional[typing.Sequence[DeliveryStreamProcessor]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1cf4ada63453854ae2e6f76805a3e74c5ddb698ae5bac1961357019ec14a8fd(
    *,
    processors: typing.Sequence[DeliveryStreamProcessor],
    enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7de06d34b1cb43026a2df1e457a8c31bb6037e3435b4b5d994b35aab902da66a(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f754d0d19d385fdb87c2cbeef4e1761b3404e6d8ef29cb7cc7acee30f4dc8217(
    *,
    sub_record_type: SubRecordType,
    delimiter: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2173f9fb31d1332f76040a52e72bc980ef15a82f8558934300feb8e94767cb31(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    *,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    compression_format: typing.Optional[S3CompressionFormat] = None,
    encryption_enabled: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    key_prefix: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f4d65756295ecfad272d0ef0118002fb31865c19caa22eaba3dc0e246f03b93(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c0d302f37ff09dc12e26d33f19da491a25a1215ed0a0c12b4f7cd60943d6655(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e7aaec8a7c3cea99db0df9d5ceb2edd3fd94a77c22f7c4f4c7907d2a5fcad1(
    scope: _constructs_77d1e7e8.IConstruct,
    enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f212129c39076aa4cd62be0c8c9d0cfbcbce14e466cdd06aaeb7e05b41e21ad5(
    *,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    compression_format: typing.Optional[S3CompressionFormat] = None,
    encryption_enabled: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    key_prefix: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c4dd6d768375f11ad311e245c05d52cd892631b67637fd4a5c28c9678957f74(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__affa572d1b41a58fff582888d3251719057a9b8fd0e5dac5416dc6d6b8210ee0(
    version: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__981f6e4d4206e5975906def40f5d872f1a70311d865f3888c663bff6bb53ed0b(
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05502f0a2424a622eb9bd08c2b9ca4c578d1a74c76dbb938f6e135f7bb7d7824(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destination: DeliveryStreamDestination,
    name: typing.Optional[builtins.str] = None,
    stream_type: typing.Optional[DeliveryStreamType] = None,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b2a202fd5e395337cd7320a23cccb8c3885c51213c80e91fcc0debd8264dab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    delivery_stream_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcd890c63d90230882b54e159c2228f2581fafd2daff62b2043980c1b885d0e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    delivery_stream_arn: typing.Optional[builtins.str] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8663b0c16974ee37e5785c89fd5048ece6ae3576c9b53ba242065131936b047d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    delivery_stream_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7fb9d82b9db30c958e61aacfc3020c3b1ce603b1db2e2a49ff02a428600d34a(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5487fc013c2e4b4254ecdcdb31ad68fde013145ed1446cc20eb1c60fbf23f54(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47205f9db0c76835c43eb68375cdad796e54aff9182a699ff35ccfc0fa290297(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3db0370cdc505b0fc87af66fb0a1af05cbc69ed5741001e2791add576b265bf9(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    *,
    backup_configuration: typing.Optional[BackupConfiguration] = None,
    data_format_conversion: typing.Optional[DataFormatConversion] = None,
    dynamic_partitioning: typing.Optional[DynamicPartitioning] = None,
    processor_configuration: typing.Optional[ProcessorConfiguration] = None,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    compression_format: typing.Optional[S3CompressionFormat] = None,
    encryption_enabled: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    key_prefix: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7687e5a52e65228aa5e0c0fe2ef72a90ef690f5913e2e63f3d150ebab5b7098(
    processor: DeliveryStreamProcessor,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27ed02c2cc71a60d26ac324c75fe5c990faaa34885fc10dafc05efc1d4b488c(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b88324642c4949dd64693f19afba43b19d0a89fab9dc832dde888ce03760d6(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41ba06e3892af24422a75e1d7751c5be4d95052b00e8e89a92b0640704d35418(
    *,
    buffering: typing.Optional[BufferingConfiguration] = None,
    cloudwatch_logging_configuration: typing.Optional[CloudWatchLoggingConfiguration] = None,
    compression_format: typing.Optional[S3CompressionFormat] = None,
    encryption_enabled: typing.Optional[builtins.bool] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    key_prefix: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    backup_configuration: typing.Optional[BackupConfiguration] = None,
    data_format_conversion: typing.Optional[DataFormatConversion] = None,
    dynamic_partitioning: typing.Optional[DynamicPartitioning] = None,
    processor_configuration: typing.Optional[ProcessorConfiguration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7e3a019b1c8b6718bc5f40a8483afbea2e5140654d293521505958c016c5da9(
    format: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3768077bea7745cf8ccb2ced138636da879e3caa2fe1e2046122d5de31d59d(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62c7532847c88c105cfbbd6d3b50fe376eb8da94bca232ba95d5c19c3fbffb28(
    fields: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c5b3849cfae6e8c90ca34382ec0df4ab7f648d847a1f98d6fc2242366e40f57(
    name: builtins.str,
    query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eae0c95f4d76129b2fe013df0e9fb2400b7cc6b7ff3bf88e4d385dc6a9b6b64f(
    column: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0facf543819a4a7f987c9cea643d1c6112ec140d5bc8ab02f8a0bb9e3dd2bf50(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass
