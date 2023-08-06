'''
# Vibe-io CDK-Extensions Athena Construct Library

The @cdk-extensions/athena package contains advanced constructs and patterns for
setting up named queries. The constructs presented here are intended
to be replacements for equivalent AWS constructs in the CDK Athena module, but with
additional features included.

[AWS CDK Athena API Reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_athena-readme.html)

To import and use this module within your CDK project:

```python
import * as athena from 'cdk-extensions/athena';
```

## Objective

The Athena module is a component of the logging strategy provided by this project defined by **stacks/AwsLoggingStack**. Athena uses the AWS Glue Data Catalog to store and retrieve table metadata for the Amazon S3 data in your Amazon Web Services account. The table metadata lets the Athena query engine know how to find, read, and process the data that you want to query.

The logging strategy defined in this project accounts for all AWS services that log to S3 including ALB, CloudFront, CloudTrail, Flow Logs, S3 access logs, SES, and WAF. For each service a Glue crawler preforms an ETL process to analyze and categorize data in Amazon S3 and store the associated metadata in AWS Glue Data Catalog.

## Usage

The Athena module creates `CfnNamedQuery` resources when the `createQueries` property is set to `true` in the `glue-tables` module. Several default named queires are defined that aid in improving the security posture of your AWS Account. This package introduces several named queries for the following AWS services:

Examples for each of the services below can be found in **src/glue-tables**

Example of an Athena query to retrive the 100 most active IP addresses by request count:

```python
if (this.createQueries) {
    this.topIpsNamedQuery = new NamedQuery(this, 'top-ips-named-query', {
    database: this.database,
    description: 'Gets the 100 most actvie IP addresses by request count.',
    name: this.friendlyQueryNames ? 'alb-top-ips' : undefined,
    queryString: [
        'SELECT client_ip,',
        '    COUNT(*) AS requests,',
        '    COUNT_IF(elb_status_code BETWEEN 400 AND 499) AS errors_4xx,',
        '    COUNT_IF(elb_status_code BETWEEN 500 AND 599) AS errors_5xx,',
        '    SUM(sent_bytes) AS sent,',
        '    SUM(received_bytes) AS received,',
        '    SUM(sent_bytes + received_bytes) AS total,',
        '    ARBITRARY(user_agent) as user_agent',
        `FROM ${this.tableName}`,
        "WHERE day >= DATE_FORMAT(NOW() - PARSE_DURATION('1d'), '%Y/%m/%d')",
        "    AND FROM_ISO8601_TIMESTAMP(time) >= NOW() - PARSE_DURATION('1d')",
        'GROUP BY client_ip',
        'ORDER by total DESC LIMIT 100;',
    ].join('\n'),
    });
```

### ALB

See **src/glue-tables/alb-logs-table.ts**

Gets the 100 most actvie IP addresses by request count.

Gets the 100 most recent ELB 5XX responses.

### CloudFront

See **src/glue-tables/cloudfront-logs-table.ts**

Gets statistics for CloudFront distributions for the last day.

Gets the 100 most recent requests that resulted in an error from CloudFront.

Gets the 100 most active IP addresses by request count.

Gets the 100 most requested CloudFront objects.

### CloudTrail

See **src/glue-tables/cloudtrail-logs-table.ts**

Gets the 100 most recent unauthorized AWS API calls.

Gets the 100 most recent AWS user logins.

### Flow Logs

See **src/glue-tables/flow-logs-table.ts**

Gets the 100 most recent rejected packets that stayed within the private network ranges.

### S3 Access Logs

See **src/glue-tables/s3-access-logs-table.ts**

Gets the 100 most recent failed S3 access requests.

### SES Logs

See **src/glue-tables/ses-logs-table.ts**

Gets the 100 most recent bounces from the last day.

Gets the 100 most recent complaints from the last day.

### WAF Logs

See **src/glue-tables/waf-logs-table.ts**
'''
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
import aws_cdk.aws_athena as _aws_cdk_aws_athena_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8
from ..core import DataSize as _DataSize_d20aaece
from ..glue import Database as _Database_5971ae38


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AddNamedQueryOptions",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "database": "database",
        "query_string": "queryString",
        "description": "description",
        "name": "name",
    },
)
class AddNamedQueryOptions(_aws_cdk_ceddda9d.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        database: _Database_5971ae38,
        query_string: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration for adding a NamedQuery to a WorkGroup.

        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param database: The Glue database to which the query belongs.
        :param query_string: The SQL statements that make up the query.
        :param description: A human friendly description explaining the functionality of the query.
        :param name: The name of the query.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6512310d3609053368f001951acf4c2ef208998c5eb3d409419fa27ddd1d06c5)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument query_string", value=query_string, expected_type=type_hints["query_string"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "query_string": query_string,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

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
    def database(self) -> _Database_5971ae38:
        '''The Glue database to which the query belongs.

        :see: `NamedQuery Database <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-database>`_
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(_Database_5971ae38, result)

    @builtins.property
    def query_string(self) -> builtins.str:
        '''The SQL statements that make up the query.

        :see: `Athena SQL reference <https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html>`_
        '''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A human friendly description explaining the functionality of the query.

        :see: `NamedQuery Description <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-description>`_
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the query.

        :see: `NamedQuery Name <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-name>`_
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddNamedQueryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AnalyticsEngine(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.AnalyticsEngine",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="apacheSpark")
    @builtins.classmethod
    def apache_spark(cls, options: "ApacheSparkEngineOptions") -> "IAnalyticsEngine":
        '''
        :param options: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__517ba90f76f3cfef347c8cc4705bfaf074148757ecc2fed0c0a0b1191bef4f79)
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        return typing.cast("IAnalyticsEngine", jsii.sinvoke(cls, "apacheSpark", [options]))

    @jsii.member(jsii_name="athenaSql")
    @builtins.classmethod
    def athena_sql(
        cls,
        *,
        enforce_configuration: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional["AthenaSqlEngineVersion"] = None,
        output: typing.Optional[typing.Union["AnalyticsEngineOutputOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        publish_metrics: typing.Optional[builtins.bool] = None,
        query_scanned_bytes_limit: typing.Optional[_DataSize_d20aaece] = None,
        requester_pays: typing.Optional[builtins.bool] = None,
    ) -> "IAnalyticsEngine":
        '''
        :param enforce_configuration: 
        :param engine_version: 
        :param output: 
        :param publish_metrics: 
        :param query_scanned_bytes_limit: 
        :param requester_pays: 
        '''
        options = AthenaSqlEngineOptions(
            enforce_configuration=enforce_configuration,
            engine_version=engine_version,
            output=output,
            publish_metrics=publish_metrics,
            query_scanned_bytes_limit=query_scanned_bytes_limit,
            requester_pays=requester_pays,
        )

        return typing.cast("IAnalyticsEngine", jsii.sinvoke(cls, "athenaSql", [options]))


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AnalyticsEngineBindProps",
    jsii_struct_bases=[],
    name_mapping={"work_group_name": "workGroupName"},
)
class AnalyticsEngineBindProps:
    def __init__(self, *, work_group_name: builtins.str) -> None:
        '''
        :param work_group_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2b98ca85dace249810228d13e757b3bf4288091b08373d097a6707d00830f64)
            check_type(argname="argument work_group_name", value=work_group_name, expected_type=type_hints["work_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "work_group_name": work_group_name,
        }

    @builtins.property
    def work_group_name(self) -> builtins.str:
        result = self._values.get("work_group_name")
        assert result is not None, "Required property 'work_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalyticsEngineBindProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AnalyticsEngineConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "encrpytion_key": "encrpytionKey",
        "enforce_configuration": "enforceConfiguration",
        "engine_version": "engineVersion",
        "expected_bucket_owner": "expectedBucketOwner",
        "output_location": "outputLocation",
        "publish_metrics": "publishMetrics",
        "query_scanned_bytes_limit": "queryScannedBytesLimit",
        "requester_pays": "requesterPays",
        "results_bucket": "resultsBucket",
        "results_bucket_encryption_key": "resultsBucketEncryptionKey",
        "results_bucket_encryption_type": "resultsBucketEncryptionType",
        "role": "role",
    },
)
class AnalyticsEngineConfiguration:
    def __init__(
        self,
        *,
        encrpytion_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_configuration: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional["AnalyticsEngineVersion"] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        output_location: typing.Optional[builtins.str] = None,
        publish_metrics: typing.Optional[builtins.bool] = None,
        query_scanned_bytes_limit: typing.Optional[_DataSize_d20aaece] = None,
        requester_pays: typing.Optional[builtins.bool] = None,
        results_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        results_bucket_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        results_bucket_encryption_type: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param encrpytion_key: 
        :param enforce_configuration: 
        :param engine_version: 
        :param expected_bucket_owner: 
        :param output_location: 
        :param publish_metrics: 
        :param query_scanned_bytes_limit: 
        :param requester_pays: 
        :param results_bucket: 
        :param results_bucket_encryption_key: 
        :param results_bucket_encryption_type: 
        :param role: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2160d0713dbc156c463c4a2160781e63bde03868934454097543aa481b78e07)
            check_type(argname="argument encrpytion_key", value=encrpytion_key, expected_type=type_hints["encrpytion_key"])
            check_type(argname="argument enforce_configuration", value=enforce_configuration, expected_type=type_hints["enforce_configuration"])
            check_type(argname="argument engine_version", value=engine_version, expected_type=type_hints["engine_version"])
            check_type(argname="argument expected_bucket_owner", value=expected_bucket_owner, expected_type=type_hints["expected_bucket_owner"])
            check_type(argname="argument output_location", value=output_location, expected_type=type_hints["output_location"])
            check_type(argname="argument publish_metrics", value=publish_metrics, expected_type=type_hints["publish_metrics"])
            check_type(argname="argument query_scanned_bytes_limit", value=query_scanned_bytes_limit, expected_type=type_hints["query_scanned_bytes_limit"])
            check_type(argname="argument requester_pays", value=requester_pays, expected_type=type_hints["requester_pays"])
            check_type(argname="argument results_bucket", value=results_bucket, expected_type=type_hints["results_bucket"])
            check_type(argname="argument results_bucket_encryption_key", value=results_bucket_encryption_key, expected_type=type_hints["results_bucket_encryption_key"])
            check_type(argname="argument results_bucket_encryption_type", value=results_bucket_encryption_type, expected_type=type_hints["results_bucket_encryption_type"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if encrpytion_key is not None:
            self._values["encrpytion_key"] = encrpytion_key
        if enforce_configuration is not None:
            self._values["enforce_configuration"] = enforce_configuration
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if expected_bucket_owner is not None:
            self._values["expected_bucket_owner"] = expected_bucket_owner
        if output_location is not None:
            self._values["output_location"] = output_location
        if publish_metrics is not None:
            self._values["publish_metrics"] = publish_metrics
        if query_scanned_bytes_limit is not None:
            self._values["query_scanned_bytes_limit"] = query_scanned_bytes_limit
        if requester_pays is not None:
            self._values["requester_pays"] = requester_pays
        if results_bucket is not None:
            self._values["results_bucket"] = results_bucket
        if results_bucket_encryption_key is not None:
            self._values["results_bucket_encryption_key"] = results_bucket_encryption_key
        if results_bucket_encryption_type is not None:
            self._values["results_bucket_encryption_type"] = results_bucket_encryption_type
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def encrpytion_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("encrpytion_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def enforce_configuration(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enforce_configuration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_version(self) -> typing.Optional["AnalyticsEngineVersion"]:
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional["AnalyticsEngineVersion"], result)

    @builtins.property
    def expected_bucket_owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("expected_bucket_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_location(self) -> typing.Optional[builtins.str]:
        result = self._values.get("output_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_metrics(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("publish_metrics")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def query_scanned_bytes_limit(self) -> typing.Optional[_DataSize_d20aaece]:
        result = self._values.get("query_scanned_bytes_limit")
        return typing.cast(typing.Optional[_DataSize_d20aaece], result)

    @builtins.property
    def requester_pays(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("requester_pays")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def results_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        result = self._values.get("results_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def results_bucket_encryption_key(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("results_bucket_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def results_bucket_encryption_type(self) -> typing.Optional[builtins.str]:
        result = self._values.get("results_bucket_encryption_type")
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
        return "AnalyticsEngineConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AnalyticsEngineOutputOptions",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "encryption": "encryption",
        "expected_owner_id": "expectedOwnerId",
        "key_prefix": "keyPrefix",
    },
)
class AnalyticsEngineOutputOptions:
    def __init__(
        self,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        encryption: typing.Optional["IAthenaResultEncryption"] = None,
        expected_owner_id: typing.Optional[builtins.str] = None,
        key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: 
        :param encryption: 
        :param expected_owner_id: 
        :param key_prefix: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1327e74fb57fa696e9b7f12f550167b48c11a619bf215bd66644031234444be4)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument expected_owner_id", value=expected_owner_id, expected_type=type_hints["expected_owner_id"])
            check_type(argname="argument key_prefix", value=key_prefix, expected_type=type_hints["key_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if encryption is not None:
            self._values["encryption"] = encryption
        if expected_owner_id is not None:
            self._values["expected_owner_id"] = expected_owner_id
        if key_prefix is not None:
            self._values["key_prefix"] = key_prefix

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def encryption(self) -> typing.Optional["IAthenaResultEncryption"]:
        result = self._values.get("encryption")
        return typing.cast(typing.Optional["IAthenaResultEncryption"], result)

    @builtins.property
    def expected_owner_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("expected_owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AnalyticsEngineOutputOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AnalyticsEngineVersion(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-extensions.athena.AnalyticsEngineVersion",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @builtins.property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        ...


class _AnalyticsEngineVersionProxy(AnalyticsEngineVersion):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, AnalyticsEngineVersion).__jsii_proxy_class__ = lambda : _AnalyticsEngineVersionProxy


class ApacheSparkEngineOptions(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.ApacheSparkEngineOptions",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional["ApacheSparkEngineVersion"]:
        return typing.cast(typing.Optional["ApacheSparkEngineVersion"], jsii.get(self, "engineVersion"))

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Optional[AnalyticsEngineOutputOptions]:
        return typing.cast(typing.Optional[AnalyticsEngineOutputOptions], jsii.get(self, "output"))

    @builtins.property
    @jsii.member(jsii_name="publishMetrics")
    def publish_metrics(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "publishMetrics"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


class ApacheSparkEngineVersion(
    AnalyticsEngineVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.ApacheSparkEngineVersion",
):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "ApacheSparkEngineVersion":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e518f3eef9a2b61f523817344378dd46fc425bb293455a93969c8ef37339b3e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ApacheSparkEngineVersion", jsii.sinvoke(cls, "of", [name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO")
    def AUTO(cls) -> "ApacheSparkEngineVersion":
        return typing.cast("ApacheSparkEngineVersion", jsii.sget(cls, "AUTO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3")
    def V3(cls) -> "ApacheSparkEngineVersion":
        return typing.cast("ApacheSparkEngineVersion", jsii.sget(cls, "V3"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


class ApacheSparkOutputEncryption(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.ApacheSparkOutputEncryption",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="sseKms")
    @builtins.classmethod
    def sse_kms(
        cls,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> "IAthenaResultEncryption":
        '''
        :param encryption_key: 
        '''
        options = AthenaResultKmsEncryptionOptions(encryption_key=encryption_key)

        return typing.cast("IAthenaResultEncryption", jsii.sinvoke(cls, "sseKms", [options]))

    @jsii.member(jsii_name="sseS3")
    @builtins.classmethod
    def sse_s3(cls) -> "IAthenaResultEncryption":
        return typing.cast("IAthenaResultEncryption", jsii.sinvoke(cls, "sseS3", []))


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AthenaResultEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_encryption": "bucketEncryption",
        "encryption_label": "encryptionLabel",
        "encryption_key": "encryptionKey",
    },
)
class AthenaResultEncryptionConfiguration:
    def __init__(
        self,
        *,
        bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        encryption_label: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''
        :param bucket_encryption: 
        :param encryption_label: 
        :param encryption_key: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a04eafe57e61fc5ccd899afa72790241eeaae2e864f900de8912895977c7cbf)
            check_type(argname="argument bucket_encryption", value=bucket_encryption, expected_type=type_hints["bucket_encryption"])
            check_type(argname="argument encryption_label", value=encryption_label, expected_type=type_hints["encryption_label"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_encryption": bucket_encryption,
            "encryption_label": encryption_label,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key

    @builtins.property
    def bucket_encryption(self) -> _aws_cdk_aws_s3_ceddda9d.BucketEncryption:
        result = self._values.get("bucket_encryption")
        assert result is not None, "Required property 'bucket_encryption' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.BucketEncryption, result)

    @builtins.property
    def encryption_label(self) -> builtins.str:
        result = self._values.get("encryption_label")
        assert result is not None, "Required property 'encryption_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaResultEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AthenaResultKmsEncryptionOptions",
    jsii_struct_bases=[],
    name_mapping={"encryption_key": "encryptionKey"},
)
class AthenaResultKmsEncryptionOptions:
    def __init__(
        self,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''
        :param encryption_key: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5db9e4fbc6c7f0e8d28e130a3790bc86fcf38f7eefbcd05bc74722fb1586be5d)
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaResultKmsEncryptionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.AthenaSqlEngineOptions",
    jsii_struct_bases=[],
    name_mapping={
        "enforce_configuration": "enforceConfiguration",
        "engine_version": "engineVersion",
        "output": "output",
        "publish_metrics": "publishMetrics",
        "query_scanned_bytes_limit": "queryScannedBytesLimit",
        "requester_pays": "requesterPays",
    },
)
class AthenaSqlEngineOptions:
    def __init__(
        self,
        *,
        enforce_configuration: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional["AthenaSqlEngineVersion"] = None,
        output: typing.Optional[typing.Union[AnalyticsEngineOutputOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        publish_metrics: typing.Optional[builtins.bool] = None,
        query_scanned_bytes_limit: typing.Optional[_DataSize_d20aaece] = None,
        requester_pays: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param enforce_configuration: 
        :param engine_version: 
        :param output: 
        :param publish_metrics: 
        :param query_scanned_bytes_limit: 
        :param requester_pays: 
        '''
        if isinstance(output, dict):
            output = AnalyticsEngineOutputOptions(**output)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805c3dd9d7b04b66bdba626e5b17402504118fe3778f46e43d9bf9ba3cebb7f9)
            check_type(argname="argument enforce_configuration", value=enforce_configuration, expected_type=type_hints["enforce_configuration"])
            check_type(argname="argument engine_version", value=engine_version, expected_type=type_hints["engine_version"])
            check_type(argname="argument output", value=output, expected_type=type_hints["output"])
            check_type(argname="argument publish_metrics", value=publish_metrics, expected_type=type_hints["publish_metrics"])
            check_type(argname="argument query_scanned_bytes_limit", value=query_scanned_bytes_limit, expected_type=type_hints["query_scanned_bytes_limit"])
            check_type(argname="argument requester_pays", value=requester_pays, expected_type=type_hints["requester_pays"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enforce_configuration is not None:
            self._values["enforce_configuration"] = enforce_configuration
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if output is not None:
            self._values["output"] = output
        if publish_metrics is not None:
            self._values["publish_metrics"] = publish_metrics
        if query_scanned_bytes_limit is not None:
            self._values["query_scanned_bytes_limit"] = query_scanned_bytes_limit
        if requester_pays is not None:
            self._values["requester_pays"] = requester_pays

    @builtins.property
    def enforce_configuration(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enforce_configuration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_version(self) -> typing.Optional["AthenaSqlEngineVersion"]:
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional["AthenaSqlEngineVersion"], result)

    @builtins.property
    def output(self) -> typing.Optional[AnalyticsEngineOutputOptions]:
        result = self._values.get("output")
        return typing.cast(typing.Optional[AnalyticsEngineOutputOptions], result)

    @builtins.property
    def publish_metrics(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("publish_metrics")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def query_scanned_bytes_limit(self) -> typing.Optional[_DataSize_d20aaece]:
        result = self._values.get("query_scanned_bytes_limit")
        return typing.cast(typing.Optional[_DataSize_d20aaece], result)

    @builtins.property
    def requester_pays(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("requester_pays")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaSqlEngineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaSqlEngineVersion(
    AnalyticsEngineVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.AthenaSqlEngineVersion",
):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "AthenaSqlEngineVersion":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bf5f7d72a639611e2619f6469be2a8100a6a4a5a687167b3f98553be1fcee56)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("AthenaSqlEngineVersion", jsii.sinvoke(cls, "of", [name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AUTO")
    def AUTO(cls) -> "AthenaSqlEngineVersion":
        return typing.cast("AthenaSqlEngineVersion", jsii.sget(cls, "AUTO"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2")
    def V2(cls) -> "AthenaSqlEngineVersion":
        return typing.cast("AthenaSqlEngineVersion", jsii.sget(cls, "V2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V3")
    def V3(cls) -> "AthenaSqlEngineVersion":
        return typing.cast("AthenaSqlEngineVersion", jsii.sget(cls, "V3"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


class AthenaSqlOutputEncryption(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.AthenaSqlOutputEncryption",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="cseKms")
    @builtins.classmethod
    def cse_kms(
        cls,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> "IAthenaResultEncryption":
        '''
        :param encryption_key: 
        '''
        options = AthenaResultKmsEncryptionOptions(encryption_key=encryption_key)

        return typing.cast("IAthenaResultEncryption", jsii.sinvoke(cls, "cseKms", [options]))

    @jsii.member(jsii_name="sseKms")
    @builtins.classmethod
    def sse_kms(
        cls,
        *,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> "IAthenaResultEncryption":
        '''
        :param encryption_key: 
        '''
        options = AthenaResultKmsEncryptionOptions(encryption_key=encryption_key)

        return typing.cast("IAthenaResultEncryption", jsii.sinvoke(cls, "sseKms", [options]))

    @jsii.member(jsii_name="sseS3")
    @builtins.classmethod
    def sse_s3(cls) -> "IAthenaResultEncryption":
        return typing.cast("IAthenaResultEncryption", jsii.sinvoke(cls, "sseS3", []))


@jsii.interface(jsii_type="cdk-extensions.athena.IAnalyticsEngine")
class IAnalyticsEngine(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        *,
        work_group_name: builtins.str,
    ) -> AnalyticsEngineConfiguration:
        '''
        :param scope: -
        :param work_group_name: 
        '''
        ...


class _IAnalyticsEngineProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.athena.IAnalyticsEngine"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        *,
        work_group_name: builtins.str,
    ) -> AnalyticsEngineConfiguration:
        '''
        :param scope: -
        :param work_group_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53fa5b0b8f832ef566b05c5e2b916749b519cb6c023372108ea5a344d22870c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = AnalyticsEngineBindProps(work_group_name=work_group_name)

        return typing.cast(AnalyticsEngineConfiguration, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAnalyticsEngine).__jsii_proxy_class__ = lambda : _IAnalyticsEngineProxy


@jsii.interface(jsii_type="cdk-extensions.athena.IAthenaResultEncryption")
class IAthenaResultEncryption(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> AthenaResultEncryptionConfiguration:
        '''
        :param scope: -
        '''
        ...


class _IAthenaResultEncryptionProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.athena.IAthenaResultEncryption"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
    ) -> AthenaResultEncryptionConfiguration:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8af3df5e2b7067e040025279eff24c4ad991a5ba74c4f78754e20b4f0eafb653)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(AthenaResultEncryptionConfiguration, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAthenaResultEncryption).__jsii_proxy_class__ = lambda : _IAthenaResultEncryptionProxy


@jsii.interface(jsii_type="cdk-extensions.athena.IWorkGroup")
class IWorkGroup(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="workGroupArn")
    def work_group_arn(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="workGroupCreationTime")
    def work_group_creation_time(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="workGroupEffectiveEngineVersion")
    def work_group_effective_engine_version(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="workGroupName")
    def work_group_name(self) -> builtins.str:
        ...


class _IWorkGroupProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.athena.IWorkGroup"

    @builtins.property
    @jsii.member(jsii_name="workGroupArn")
    def work_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="workGroupCreationTime")
    def work_group_creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupCreationTime"))

    @builtins.property
    @jsii.member(jsii_name="workGroupEffectiveEngineVersion")
    def work_group_effective_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupEffectiveEngineVersion"))

    @builtins.property
    @jsii.member(jsii_name="workGroupName")
    def work_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWorkGroup).__jsii_proxy_class__ = lambda : _IWorkGroupProxy


class NamedQuery(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.NamedQuery",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        database: _Database_5971ae38,
        query_string: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        work_group: typing.Optional[IWorkGroup] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new instance of the NamedQuery class.

        :param scope: A CDK Construct that will serve as this resource's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param database: The Glue database to which the query belongs.
        :param query_string: The SQL statements that make up the query.
        :param description: A human friendly description explaining the functionality of the query.
        :param name: The name of the query.
        :param work_group: The name of the workgroup that contains the named query.
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24bebf373c33fd4a77bf71e90e7c492972fd93b1f5d672bb7fc4c032b6884b65)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NamedQueryProps(
            database=database,
            query_string=query_string,
            description=description,
            name=name,
            work_group=work_group,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> _Database_5971ae38:
        '''The Glue database to which the query belongs.

        :see: `NamedQuery Database <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-database>`_
        :group: Inputs
        '''
        return typing.cast(_Database_5971ae38, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="namedQueryId")
    def named_query_id(self) -> builtins.str:
        '''The unique ID of the query.'''
        return typing.cast(builtins.str, jsii.get(self, "namedQueryId"))

    @builtins.property
    @jsii.member(jsii_name="namedQueryName")
    def named_query_name(self) -> builtins.str:
        '''The name of the query.'''
        return typing.cast(builtins.str, jsii.get(self, "namedQueryName"))

    @builtins.property
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> builtins.str:
        '''The SQL statements that make up the query.

        :see: `Athena SQL reference <https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html>`_
        :group: Inputs
        '''
        return typing.cast(builtins.str, jsii.get(self, "queryString"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_athena_ceddda9d.CfnNamedQuery:
        '''The underlying NamedQuery CloudFormation resource.

        :see: `AWS::Athena::NamedQuery <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html>`_
        :group: Resources
        '''
        return typing.cast(_aws_cdk_aws_athena_ceddda9d.CfnNamedQuery, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''A human friendly description explaining the functionality of the query.

        :see: `NamedQuery Description <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-description>`_
        :group: Inputs
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the query.

        :see: `NamedQuery Name <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-name>`_
        :group: Inputs
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="workGroup")
    def work_group(self) -> typing.Optional[IWorkGroup]:
        '''The name of the workgroup that contains the named query.

        :see: `Setting up workgroups <https://docs.aws.amazon.com/athena/latest/ug/workgroups-procedure.html>`_
        :group: Inputs
        '''
        return typing.cast(typing.Optional[IWorkGroup], jsii.get(self, "workGroup"))


@jsii.data_type(
    jsii_type="cdk-extensions.athena.NamedQueryProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "database": "database",
        "query_string": "queryString",
        "description": "description",
        "name": "name",
        "work_group": "workGroup",
    },
)
class NamedQueryProps(_aws_cdk_ceddda9d.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        database: _Database_5971ae38,
        query_string: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        work_group: typing.Optional[IWorkGroup] = None,
    ) -> None:
        '''Configuration for a NamedQuery.

        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param database: The Glue database to which the query belongs.
        :param query_string: The SQL statements that make up the query.
        :param description: A human friendly description explaining the functionality of the query.
        :param name: The name of the query.
        :param work_group: The name of the workgroup that contains the named query.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0ee8336d4e5d9aa76d3f19dd0afd580bbb01600fb5a10a09b4395918b8d2163)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument query_string", value=query_string, expected_type=type_hints["query_string"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument work_group", value=work_group, expected_type=type_hints["work_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "query_string": query_string,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if work_group is not None:
            self._values["work_group"] = work_group

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
    def database(self) -> _Database_5971ae38:
        '''The Glue database to which the query belongs.

        :see: `NamedQuery Database <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-database>`_
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(_Database_5971ae38, result)

    @builtins.property
    def query_string(self) -> builtins.str:
        '''The SQL statements that make up the query.

        :see: `Athena SQL reference <https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html>`_
        '''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A human friendly description explaining the functionality of the query.

        :see: `NamedQuery Description <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-description>`_
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the query.

        :see: `NamedQuery Name <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-namedquery.html#cfn-athena-namedquery-name>`_
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def work_group(self) -> typing.Optional[IWorkGroup]:
        '''The name of the workgroup that contains the named query.

        :see: `Setting up workgroups <https://docs.aws.amazon.com/athena/latest/ug/workgroups-procedure.html>`_
        '''
        result = self._values.get("work_group")
        return typing.cast(typing.Optional[IWorkGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NamedQueryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWorkGroup)
class WorkGroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.WorkGroup",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        engine: typing.Optional[IAnalyticsEngine] = None,
        name: typing.Optional[builtins.str] = None,
        recursive_delete: typing.Optional[builtins.bool] = None,
        state: typing.Optional["WorkGroupState"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param description: 
        :param engine: 
        :param name: 
        :param recursive_delete: 
        :param state: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1378d58180a256a2dbadba25152c30deffec262f47ee784e868ac8e5167858cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkGroupProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
            description=description,
            engine=engine,
            name=name,
            recursive_delete=recursive_delete,
            state=state,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWorkGroupArn")
    @builtins.classmethod
    def from_work_group_arn(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        arn: builtins.str,
    ) -> IWorkGroup:
        '''
        :param scope: -
        :param id: -
        :param arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b5abbcd5a5865301a73584ac58fdc732d323b66394552c2eb61e0b53c85353f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast(IWorkGroup, jsii.sinvoke(cls, "fromWorkGroupArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromWorkGroupAttributes")
    @builtins.classmethod
    def from_work_group_attributes(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        arn: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[builtins.str] = None,
        effective_engine_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> IWorkGroup:
        '''
        :param scope: -
        :param id: -
        :param arn: 
        :param creation_time: 
        :param effective_engine_version: 
        :param name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da1002d928446567ce3e5f01ac0606bf0e9197a2d17e9137525067250d8c0643)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WorkGroupAttributes(
            arn=arn,
            creation_time=creation_time,
            effective_engine_version=effective_engine_version,
            name=name,
        )

        return typing.cast(IWorkGroup, jsii.sinvoke(cls, "fromWorkGroupAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromWorkGroupName")
    @builtins.classmethod
    def from_work_group_name(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        name: builtins.str,
    ) -> IWorkGroup:
        '''
        :param scope: -
        :param id: -
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__313d6bd8a1f85d2dd32cfb56aeb873c94ea01f7a30bb1dd69edea998725020de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(IWorkGroup, jsii.sinvoke(cls, "fromWorkGroupName", [scope, id, name]))

    @jsii.member(jsii_name="addNamedQuery")
    def add_named_query(
        self,
        id: builtins.str,
        *,
        database: _Database_5971ae38,
        query_string: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> NamedQuery:
        '''
        :param id: -
        :param database: The Glue database to which the query belongs.
        :param query_string: The SQL statements that make up the query.
        :param description: A human friendly description explaining the functionality of the query.
        :param name: The name of the query.
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8f293a9f61f5c7745109e72ce8b090f0994cc876efff5674160b0f464b6efad)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = AddNamedQueryOptions(
            database=database,
            query_string=query_string,
            description=description,
            name=name,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        return typing.cast(NamedQuery, jsii.invoke(self, "addNamedQuery", [id, options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ARN_FORMAT")
    def ARN_FORMAT(cls) -> _aws_cdk_ceddda9d.ArnFormat:
        return typing.cast(_aws_cdk_ceddda9d.ArnFormat, jsii.sget(cls, "ARN_FORMAT"))

    @builtins.property
    @jsii.member(jsii_name="engine")
    def engine(self) -> IAnalyticsEngine:
        return typing.cast(IAnalyticsEngine, jsii.get(self, "engine"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="recursiveDelete")
    def recursive_delete(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "recursiveDelete"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_athena_ceddda9d.CfnWorkGroup:
        return typing.cast(_aws_cdk_aws_athena_ceddda9d.CfnWorkGroup, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="workGroupArn")
    def work_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="workGroupCreationTime")
    def work_group_creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupCreationTime"))

    @builtins.property
    @jsii.member(jsii_name="workGroupEffectiveEngineVersion")
    def work_group_effective_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupEffectiveEngineVersion"))

    @builtins.property
    @jsii.member(jsii_name="workGroupName")
    def work_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workGroupName"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> typing.Optional["WorkGroupState"]:
        return typing.cast(typing.Optional["WorkGroupState"], jsii.get(self, "state"))


@jsii.data_type(
    jsii_type="cdk-extensions.athena.WorkGroupAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "arn": "arn",
        "creation_time": "creationTime",
        "effective_engine_version": "effectiveEngineVersion",
        "name": "name",
    },
)
class WorkGroupAttributes:
    def __init__(
        self,
        *,
        arn: typing.Optional[builtins.str] = None,
        creation_time: typing.Optional[builtins.str] = None,
        effective_engine_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param arn: 
        :param creation_time: 
        :param effective_engine_version: 
        :param name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf8de514e7f9e92c3859670de6d4d9d2966601bb4bb6303c6d75b39a05fa25a)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument creation_time", value=creation_time, expected_type=type_hints["creation_time"])
            check_type(argname="argument effective_engine_version", value=effective_engine_version, expected_type=type_hints["effective_engine_version"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if arn is not None:
            self._values["arn"] = arn
        if creation_time is not None:
            self._values["creation_time"] = creation_time
        if effective_engine_version is not None:
            self._values["effective_engine_version"] = effective_engine_version
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_time(self) -> typing.Optional[builtins.str]:
        result = self._values.get("creation_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def effective_engine_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("effective_engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkGroupAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.WorkGroupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "engine": "engine",
        "name": "name",
        "recursive_delete": "recursiveDelete",
        "state": "state",
    },
)
class WorkGroupOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        engine: typing.Optional[IAnalyticsEngine] = None,
        name: typing.Optional[builtins.str] = None,
        recursive_delete: typing.Optional[builtins.bool] = None,
        state: typing.Optional["WorkGroupState"] = None,
    ) -> None:
        '''
        :param description: 
        :param engine: 
        :param name: 
        :param recursive_delete: 
        :param state: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f3705383a51352fa32ae967481d668794e45b5b35b13c19e8a88be58bf44f72)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument recursive_delete", value=recursive_delete, expected_type=type_hints["recursive_delete"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if engine is not None:
            self._values["engine"] = engine
        if name is not None:
            self._values["name"] = name
        if recursive_delete is not None:
            self._values["recursive_delete"] = recursive_delete
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[IAnalyticsEngine]:
        result = self._values.get("engine")
        return typing.cast(typing.Optional[IAnalyticsEngine], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recursive_delete(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("recursive_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def state(self) -> typing.Optional["WorkGroupState"]:
        result = self._values.get("state")
        return typing.cast(typing.Optional["WorkGroupState"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkGroupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.athena.WorkGroupProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps, WorkGroupOptions],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "description": "description",
        "engine": "engine",
        "name": "name",
        "recursive_delete": "recursiveDelete",
        "state": "state",
    },
)
class WorkGroupProps(_aws_cdk_ceddda9d.ResourceProps, WorkGroupOptions):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        engine: typing.Optional[IAnalyticsEngine] = None,
        name: typing.Optional[builtins.str] = None,
        recursive_delete: typing.Optional[builtins.bool] = None,
        state: typing.Optional["WorkGroupState"] = None,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param description: 
        :param engine: 
        :param name: 
        :param recursive_delete: 
        :param state: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__766a682c9e4b3a7bccf1937b86a475f523588224767d2d1e48fe7567a3c9e287)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument recursive_delete", value=recursive_delete, expected_type=type_hints["recursive_delete"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if description is not None:
            self._values["description"] = description
        if engine is not None:
            self._values["engine"] = engine
        if name is not None:
            self._values["name"] = name
        if recursive_delete is not None:
            self._values["recursive_delete"] = recursive_delete
        if state is not None:
            self._values["state"] = state

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
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[IAnalyticsEngine]:
        result = self._values.get("engine")
        return typing.cast(typing.Optional[IAnalyticsEngine], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recursive_delete(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("recursive_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def state(self) -> typing.Optional["WorkGroupState"]:
        result = self._values.get("state")
        return typing.cast(typing.Optional["WorkGroupState"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkGroupState(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.athena.WorkGroupState",
):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, name: builtins.str) -> "WorkGroupState":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__703bc5f69cf40e9084fcc7e5d65da706cc8d3bd543b6514e165c602bb8a63059)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("WorkGroupState", jsii.sinvoke(cls, "of", [name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DISABLED")
    def DISABLED(cls) -> "WorkGroupState":
        return typing.cast("WorkGroupState", jsii.sget(cls, "DISABLED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ENABLED")
    def ENABLED(cls) -> "WorkGroupState":
        return typing.cast("WorkGroupState", jsii.sget(cls, "ENABLED"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


__all__ = [
    "AddNamedQueryOptions",
    "AnalyticsEngine",
    "AnalyticsEngineBindProps",
    "AnalyticsEngineConfiguration",
    "AnalyticsEngineOutputOptions",
    "AnalyticsEngineVersion",
    "ApacheSparkEngineOptions",
    "ApacheSparkEngineVersion",
    "ApacheSparkOutputEncryption",
    "AthenaResultEncryptionConfiguration",
    "AthenaResultKmsEncryptionOptions",
    "AthenaSqlEngineOptions",
    "AthenaSqlEngineVersion",
    "AthenaSqlOutputEncryption",
    "IAnalyticsEngine",
    "IAthenaResultEncryption",
    "IWorkGroup",
    "NamedQuery",
    "NamedQueryProps",
    "WorkGroup",
    "WorkGroupAttributes",
    "WorkGroupOptions",
    "WorkGroupProps",
    "WorkGroupState",
]

publication.publish()

def _typecheckingstub__6512310d3609053368f001951acf4c2ef208998c5eb3d409419fa27ddd1d06c5(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    database: _Database_5971ae38,
    query_string: builtins.str,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517ba90f76f3cfef347c8cc4705bfaf074148757ecc2fed0c0a0b1191bef4f79(
    options: ApacheSparkEngineOptions,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b98ca85dace249810228d13e757b3bf4288091b08373d097a6707d00830f64(
    *,
    work_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2160d0713dbc156c463c4a2160781e63bde03868934454097543aa481b78e07(
    *,
    encrpytion_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_configuration: typing.Optional[builtins.bool] = None,
    engine_version: typing.Optional[AnalyticsEngineVersion] = None,
    expected_bucket_owner: typing.Optional[builtins.str] = None,
    output_location: typing.Optional[builtins.str] = None,
    publish_metrics: typing.Optional[builtins.bool] = None,
    query_scanned_bytes_limit: typing.Optional[_DataSize_d20aaece] = None,
    requester_pays: typing.Optional[builtins.bool] = None,
    results_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    results_bucket_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    results_bucket_encryption_type: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1327e74fb57fa696e9b7f12f550167b48c11a619bf215bd66644031234444be4(
    *,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    encryption: typing.Optional[IAthenaResultEncryption] = None,
    expected_owner_id: typing.Optional[builtins.str] = None,
    key_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e518f3eef9a2b61f523817344378dd46fc425bb293455a93969c8ef37339b3e(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a04eafe57e61fc5ccd899afa72790241eeaae2e864f900de8912895977c7cbf(
    *,
    bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
    encryption_label: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5db9e4fbc6c7f0e8d28e130a3790bc86fcf38f7eefbcd05bc74722fb1586be5d(
    *,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805c3dd9d7b04b66bdba626e5b17402504118fe3778f46e43d9bf9ba3cebb7f9(
    *,
    enforce_configuration: typing.Optional[builtins.bool] = None,
    engine_version: typing.Optional[AthenaSqlEngineVersion] = None,
    output: typing.Optional[typing.Union[AnalyticsEngineOutputOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    publish_metrics: typing.Optional[builtins.bool] = None,
    query_scanned_bytes_limit: typing.Optional[_DataSize_d20aaece] = None,
    requester_pays: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bf5f7d72a639611e2619f6469be2a8100a6a4a5a687167b3f98553be1fcee56(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53fa5b0b8f832ef566b05c5e2b916749b519cb6c023372108ea5a344d22870c6(
    scope: _constructs_77d1e7e8.IConstruct,
    *,
    work_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af3df5e2b7067e040025279eff24c4ad991a5ba74c4f78754e20b4f0eafb653(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24bebf373c33fd4a77bf71e90e7c492972fd93b1f5d672bb7fc4c032b6884b65(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    database: _Database_5971ae38,
    query_string: builtins.str,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    work_group: typing.Optional[IWorkGroup] = None,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0ee8336d4e5d9aa76d3f19dd0afd580bbb01600fb5a10a09b4395918b8d2163(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    database: _Database_5971ae38,
    query_string: builtins.str,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    work_group: typing.Optional[IWorkGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1378d58180a256a2dbadba25152c30deffec262f47ee784e868ac8e5167858cd(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    engine: typing.Optional[IAnalyticsEngine] = None,
    name: typing.Optional[builtins.str] = None,
    recursive_delete: typing.Optional[builtins.bool] = None,
    state: typing.Optional[WorkGroupState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b5abbcd5a5865301a73584ac58fdc732d323b66394552c2eb61e0b53c85353f(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da1002d928446567ce3e5f01ac0606bf0e9197a2d17e9137525067250d8c0643(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    arn: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[builtins.str] = None,
    effective_engine_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__313d6bd8a1f85d2dd32cfb56aeb873c94ea01f7a30bb1dd69edea998725020de(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8f293a9f61f5c7745109e72ce8b090f0994cc876efff5674160b0f464b6efad(
    id: builtins.str,
    *,
    database: _Database_5971ae38,
    query_string: builtins.str,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf8de514e7f9e92c3859670de6d4d9d2966601bb4bb6303c6d75b39a05fa25a(
    *,
    arn: typing.Optional[builtins.str] = None,
    creation_time: typing.Optional[builtins.str] = None,
    effective_engine_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3705383a51352fa32ae967481d668794e45b5b35b13c19e8a88be58bf44f72(
    *,
    description: typing.Optional[builtins.str] = None,
    engine: typing.Optional[IAnalyticsEngine] = None,
    name: typing.Optional[builtins.str] = None,
    recursive_delete: typing.Optional[builtins.bool] = None,
    state: typing.Optional[WorkGroupState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__766a682c9e4b3a7bccf1937b86a475f523588224767d2d1e48fe7567a3c9e287(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    engine: typing.Optional[IAnalyticsEngine] = None,
    name: typing.Optional[builtins.str] = None,
    recursive_delete: typing.Optional[builtins.bool] = None,
    state: typing.Optional[WorkGroupState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703bc5f69cf40e9084fcc7e5d65da706cc8d3bd543b6514e165c602bb8a63059(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
