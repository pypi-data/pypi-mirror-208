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
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="cdk-extensions.lambda.ExecutionLogOptions",
    jsii_struct_bases=[],
    name_mapping={
        "include_execution_data": "includeExecutionData",
        "level": "level",
        "enabled": "enabled",
        "log_group": "logGroup",
        "retention": "retention",
    },
)
class ExecutionLogOptions:
    def __init__(
        self,
        *,
        include_execution_data: builtins.bool,
        level: _aws_cdk_aws_stepfunctions_ceddda9d.LogLevel,
        enabled: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''Options for configuring logging from an executing state machine.

        :param include_execution_data: Determines whether execution data is included in your log. When set to ``false``, data is excluded. Default: true
        :param level: Defines which category of execution history events are logged. Default: LogLevel.ALL
        :param enabled: Controls whether logging from the state machine is enabled. Default: true
        :param log_group: Specifies a log group which will receive execution events from the state machine. If no log group is passed and loggin is enabled, a log group will be created automatically.
        :param retention: The number of days execution logging events should be retained before being deleted. This value is ignored if ``logGroup`` is passed.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1422e1e5cb340ad7527b012dbade682e87ad88bb3fc97f280eae77512638906)
            check_type(argname="argument include_execution_data", value=include_execution_data, expected_type=type_hints["include_execution_data"])
            check_type(argname="argument level", value=level, expected_type=type_hints["level"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "include_execution_data": include_execution_data,
            "level": level,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if log_group is not None:
            self._values["log_group"] = log_group
        if retention is not None:
            self._values["retention"] = retention

    @builtins.property
    def include_execution_data(self) -> builtins.bool:
        '''Determines whether execution data is included in your log.

        When set to
        ``false``, data is excluded.

        :default: true

        :see: `StateMachine LoggingConfiguration.IncludeExecutionData <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html#cfn-stepfunctions-statemachine-loggingconfiguration-includeexecutiondata>`_
        '''
        result = self._values.get("include_execution_data")
        assert result is not None, "Required property 'include_execution_data' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def level(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.LogLevel:
        '''Defines which category of execution history events are logged.

        :default: LogLevel.ALL

        :see: `StateMachine LoggingConfiguration.Level <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html#cfn-stepfunctions-statemachine-loggingconfiguration-level>`_
        '''
        result = self._values.get("level")
        assert result is not None, "Required property 'level' is missing"
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.LogLevel, result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Controls whether logging from the state machine is enabled.

        :default: true

        :see: `StateMachine LoggingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-loggingconfiguration>`_
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''Specifies a log group which will receive execution events from the state machine.

        If no log group is passed and loggin is enabled, a log group will be
        created automatically.

        :see: `StateMachine LoggingConfiguration.Destinations.CloudWatchLogsLogGroup.LogGroupArn <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-cloudwatchlogsloggroup.html#cfn-stepfunctions-statemachine-cloudwatchlogsloggroup-loggrouparn>`_
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def retention(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days execution logging events should be retained before being deleted.

        This value is ignored if ``logGroup`` is passed.

        :see: `LogGroup RetentionInDays <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-logs-loggroup-retentionindays>`_
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExecutionLogOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LogRetentionController(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.lambda.LogRetentionController",
):
    '''Deploys a solution that automatically sets a log retention policy for all CloudWatch log groups created by AWS Lamba.

    The controller consists of an EventBridge rule that detects the creation of
    new log groups and a state machine that sets a retention policy for any log
    groups that triggered the rule.

    The rule triggers for any log group that is created with a name that starts
    with ``/aws/lambda/``.

    Currently existing log groups created by AWS Lambda are not affected by the
    policy. It is also possible that log groups created by means other than AWS
    Lambda that have a retention policy specified could have their retention
    policy overridden if the log group name starts with ``/aws/lambda/``.

    :see: `Reduce log-storage costs by automating retention settings in Amazon CloudWatch <https://aws.amazon.com/blogs/infrastructure-and-automation/reduce-log-storage-costs-by-automating-retention-settings-in-amazon-cloudwatch/>`_
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        execution_logging: typing.Optional[typing.Union[ExecutionLogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new instance of the LogRetentionController class.

        :param scope: A CDK Construct that will serve as this resource's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param execution_logging: Execution logging configuration for the state machine that is used to configure log retention for log groups created via AWS Lambda.
        :param retention: The length of time logs sent to log groups created by AWS Lambda should be retained before being deleted.
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d68841e84fe5094172d2e5829ef18ca9356ce737282bcba5018b0346af894ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LogRetentionControllerProps(
            execution_logging=execution_logging,
            retention=retention,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="logGroupCreatedRule")
    def log_group_created_rule(self) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''The EventBridge rule that detects the creation of new log groups with a name matching the prefix used by AWS Lambda.

        :group: Resources
        '''
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.get(self, "logGroupCreatedRule"))

    @builtins.property
    @jsii.member(jsii_name="retention")
    def retention(self) -> _aws_cdk_aws_logs_ceddda9d.RetentionDays:
        '''The length of time logs sent to log groups created by AWS Lambda should be retained before being deleted.

        :see: `LogGroup RetentionInDays <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-logs-loggroup-retentionindays>`_
        :group: Inputs
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.RetentionDays, jsii.get(self, "retention"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''The state machine that is triggered to add a retention policy for all new log groups that trigger the EventBridge rule.

        :group: Resources
        '''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="executionLogging")
    def execution_logging(self) -> typing.Optional[ExecutionLogOptions]:
        '''Execution logging configuration for the state machine that is used to configure log retention for log groups created via AWS Lambda.

        :see: `StateMachine LoggingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-loggingconfiguration>`_
        :group: Inputs
        '''
        return typing.cast(typing.Optional[ExecutionLogOptions], jsii.get(self, "executionLogging"))

    @builtins.property
    @jsii.member(jsii_name="executionLogGroup")
    def execution_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''The log group which will receive execution events from the state machine.

        :group: Resources
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], jsii.get(self, "executionLogGroup"))


@jsii.data_type(
    jsii_type="cdk-extensions.lambda.LogRetentionControllerProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "execution_logging": "executionLogging",
        "retention": "retention",
    },
)
class LogRetentionControllerProps(_aws_cdk_ceddda9d.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        execution_logging: typing.Optional[typing.Union[ExecutionLogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''Configuration for the LogRetentionController resource.

        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param execution_logging: Execution logging configuration for the state machine that is used to configure log retention for log groups created via AWS Lambda.
        :param retention: The length of time logs sent to log groups created by AWS Lambda should be retained before being deleted.
        '''
        if isinstance(execution_logging, dict):
            execution_logging = ExecutionLogOptions(**execution_logging)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d470cb30648a6606e4d06e7a8fde25241c40d0bbc017511dd32f5a345b3dd1cb)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument execution_logging", value=execution_logging, expected_type=type_hints["execution_logging"])
            check_type(argname="argument retention", value=retention, expected_type=type_hints["retention"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if execution_logging is not None:
            self._values["execution_logging"] = execution_logging
        if retention is not None:
            self._values["retention"] = retention

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
    def execution_logging(self) -> typing.Optional[ExecutionLogOptions]:
        '''Execution logging configuration for the state machine that is used to configure log retention for log groups created via AWS Lambda.

        :see: `StateMachine LoggingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-loggingconfiguration>`_
        '''
        result = self._values.get("execution_logging")
        return typing.cast(typing.Optional[ExecutionLogOptions], result)

    @builtins.property
    def retention(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The length of time logs sent to log groups created by AWS Lambda should be retained before being deleted.

        :see: `LogGroup RetentionInDays <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html#cfn-logs-loggroup-retentionindays>`_
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogRetentionControllerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ExecutionLogOptions",
    "LogRetentionController",
    "LogRetentionControllerProps",
]

publication.publish()

def _typecheckingstub__f1422e1e5cb340ad7527b012dbade682e87ad88bb3fc97f280eae77512638906(
    *,
    include_execution_data: builtins.bool,
    level: _aws_cdk_aws_stepfunctions_ceddda9d.LogLevel,
    enabled: typing.Optional[builtins.bool] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d68841e84fe5094172d2e5829ef18ca9356ce737282bcba5018b0346af894ab(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    execution_logging: typing.Optional[typing.Union[ExecutionLogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d470cb30648a6606e4d06e7a8fde25241c40d0bbc017511dd32f5a345b3dd1cb(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    execution_logging: typing.Optional[typing.Union[ExecutionLogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass
