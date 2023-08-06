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
import aws_cdk.aws_ram as _aws_cdk_aws_ram_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="cdk-extensions.ram.IResourceShare")
class IResourceShare(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Represents an AWS Resource Access Manager (RAM) resource share in AWS.'''

    @builtins.property
    @jsii.member(jsii_name="resourceShareArn")
    def resource_share_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the RAM resource share.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="resourceShareId")
    def resource_share_id(self) -> builtins.str:
        '''The ID of the RAM resource share.'''
        ...

    @jsii.member(jsii_name="addPrincipal")
    def add_principal(self, principal: "ISharedPrincipal") -> None:
        '''Adds a new principal to the resource share.

        The principal will have access to all the resources associated with the
        resource share.

        :param principal: The principal to with resources belonging to the resource share will be shared.
        '''
        ...

    @jsii.member(jsii_name="addResource")
    def add_resource(self, resource: "ISharable") -> None:
        '''Adds a new resource to the resource share.

        The resource will be accessible to all pricipals associated with the
        resource share.

        :param resource: The resource to make accessible to the pricipals associated with the resource share.
        '''
        ...


class _IResourceShareProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Represents an AWS Resource Access Manager (RAM) resource share in AWS.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.ram.IResourceShare"

    @builtins.property
    @jsii.member(jsii_name="resourceShareArn")
    def resource_share_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the RAM resource share.'''
        return typing.cast(builtins.str, jsii.get(self, "resourceShareArn"))

    @builtins.property
    @jsii.member(jsii_name="resourceShareId")
    def resource_share_id(self) -> builtins.str:
        '''The ID of the RAM resource share.'''
        return typing.cast(builtins.str, jsii.get(self, "resourceShareId"))

    @jsii.member(jsii_name="addPrincipal")
    def add_principal(self, principal: "ISharedPrincipal") -> None:
        '''Adds a new principal to the resource share.

        The principal will have access to all the resources associated with the
        resource share.

        :param principal: The principal to with resources belonging to the resource share will be shared.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c8b639eb94527586d9d176da9a63029ea8e58967aa01158dfe2f74674d502f)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(None, jsii.invoke(self, "addPrincipal", [principal]))

    @jsii.member(jsii_name="addResource")
    def add_resource(self, resource: "ISharable") -> None:
        '''Adds a new resource to the resource share.

        The resource will be accessible to all pricipals associated with the
        resource share.

        :param resource: The resource to make accessible to the pricipals associated with the resource share.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be22743d8e2c78d6ea83ddd9575473468c95e1be8ecd7f17aa5ab3538a54477)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(None, jsii.invoke(self, "addResource", [resource]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IResourceShare).__jsii_proxy_class__ = lambda : _IResourceShareProxy


@jsii.interface(jsii_type="cdk-extensions.ram.ISharable")
class ISharable(typing_extensions.Protocol):
    '''Represents an AWS resource that can be shared via AWS Resource Access Manager (RAM).'''

    @jsii.member(jsii_name="share")
    def share(self, scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''Configures resource sharing for the associated resource.

        :param scope: The construct implementing the resource share that will be used to expose the associated resource to external principals.
        '''
        ...


class _ISharableProxy:
    '''Represents an AWS resource that can be shared via AWS Resource Access Manager (RAM).'''

    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.ram.ISharable"

    @jsii.member(jsii_name="share")
    def share(self, scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''Configures resource sharing for the associated resource.

        :param scope: The construct implementing the resource share that will be used to expose the associated resource to external principals.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb281a56c708e0bd3a7d012e40c232a2e15687212f795a42c8e0d138b544bdf8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(builtins.str, jsii.invoke(self, "share", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISharable).__jsii_proxy_class__ = lambda : _ISharableProxy


@jsii.interface(jsii_type="cdk-extensions.ram.ISharedPrincipal")
class ISharedPrincipal(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''
        :param scope: -
        '''
        ...


class _ISharedPrincipalProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.ram.ISharedPrincipal"

    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca72ec807b061d878f303339b081f503422720973adb273b601ddcd8837323e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(builtins.str, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISharedPrincipal).__jsii_proxy_class__ = lambda : _ISharedPrincipalProxy


@jsii.implements(IResourceShare)
class ResourceShare(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.ram.ResourceShare",
):
    '''Creates a resource share that can used to share AWS resources with other AWS accounts, organizations, or organizational units (OU's).

    :see: `AWS::RAM::ResourceShare <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html>`_
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        allow_external_principals: typing.Optional[builtins.bool] = None,
        auto_discover_accounts: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        principals: typing.Optional[typing.Sequence[ISharedPrincipal]] = None,
        resources: typing.Optional[typing.Sequence[ISharable]] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new instance of the ResourceShare class.

        :param scope: A CDK Construct that will serve as this stack's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param allow_external_principals: Specifies whether principals outside your organization in AWS Organizations can be associated with a resource share. A value of ``true`` lets you share with individual AWS accounts that are not in your organization. A value of ``false`` only has meaning if your account is a member of an AWS Organization. Default: true
        :param auto_discover_accounts: Controls whether the resource share should attempt to search for AWS accounts that are part of the same CDK application. Any accounts is finds will be added to the resource automatically and will be able to use the shared resources.
        :param name: Specifies the name of the resource share.
        :param principals: Specifies a list of one or more principals to associate with the resource share.
        :param resources: Specifies a list of AWS resources to share with the configured principal accounts and organizations.
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b89945094c7aec402867b1ed7520f94687bad190e661891b7c1898124b67b3c8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ResourceShareProps(
            allow_external_principals=allow_external_principals,
            auto_discover_accounts=auto_discover_accounts,
            name=name,
            principals=principals,
            resources=resources,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromResourceShareArn")
    @builtins.classmethod
    def from_resource_share_arn(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        resource_share_arn: builtins.str,
    ) -> IResourceShare:
        '''Imports an existing RAM resource share by specifying its Amazon Resource Name (ARN).

        :param scope: A CDK Construct that will serve as this resources's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param resource_share_arn: The ARN of the existing RAM resource share to be imported.

        :return: An object representing the imported RAM resource share.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88128eec4703a4c5efee5fff5a5dc3ce1d302e98a357a770f84947748566b98b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument resource_share_arn", value=resource_share_arn, expected_type=type_hints["resource_share_arn"])
        return typing.cast(IResourceShare, jsii.sinvoke(cls, "fromResourceShareArn", [scope, id, resource_share_arn]))

    @jsii.member(jsii_name="fromResourceShareAttributes")
    @builtins.classmethod
    def from_resource_share_attributes(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        *,
        resource_share_arn: typing.Optional[builtins.str] = None,
        resource_share_id: typing.Optional[builtins.str] = None,
    ) -> IResourceShare:
        '''Imports an existing RAM resource share by explicitly specifying its attributes.

        :param scope: A CDK Construct that will serve as this resources's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param resource_share_arn: The Amazon Resource Name (ARN) of the RAM resource share.
        :param resource_share_id: The ID generated by AWS for the RAM resource share.

        :return: An object representing the imported RAM resource share.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac9771317d76c9329bed60d3fd242a81dc33abbd82e3a406b6f45e87fc07e9fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ResourceShareAttributes(
            resource_share_arn=resource_share_arn, resource_share_id=resource_share_id
        )

        return typing.cast(IResourceShare, jsii.sinvoke(cls, "fromResourceShareAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromResourceShareId")
    @builtins.classmethod
    def from_resource_share_id(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        id: builtins.str,
        resource_share_id: builtins.str,
    ) -> IResourceShare:
        '''Imports an existing RAM resource share by specifying its AWS generated ID.

        :param scope: A CDK Construct that will serve as this resources's parent in the construct tree.
        :param id: A name to be associated with the stack and used in resource naming. Must be unique within the context of 'scope'.
        :param resource_share_id: The AWS generated ID of the existing APS workspace to be imported.

        :return: An object representing the imported RAM resource share.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ef793e59307e13cfc654aa867438f0369edaa2f4ed7119c7ed1b349d4bc4303)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument resource_share_id", value=resource_share_id, expected_type=type_hints["resource_share_id"])
        return typing.cast(IResourceShare, jsii.sinvoke(cls, "fromResourceShareId", [scope, id, resource_share_id]))

    @jsii.member(jsii_name="addPrincipal")
    def add_principal(self, principal: ISharedPrincipal) -> None:
        '''{@inheritdoc IResourceShare.addPrincipal}.

        :param principal: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10317648344034fd5b5ca01d87cb09e1b4640473e70368a712092954fc9194d9)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(None, jsii.invoke(self, "addPrincipal", [principal]))

    @jsii.member(jsii_name="addResource")
    def add_resource(self, resource: ISharable) -> None:
        '''{@inheritdoc IResourceShare.addResource}.

        :param resource: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37b07cbe6529ca7b8e8636fff5847d57fae2861e37fd631f972b1d71c6ffe532)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(None, jsii.invoke(self, "addResource", [resource]))

    @jsii.member(jsii_name="enableAutoDiscovery")
    def enable_auto_discovery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "enableAutoDiscovery", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ARN_FORMAT")
    def ARN_FORMAT(cls) -> _aws_cdk_ceddda9d.ArnFormat:
        return typing.cast(_aws_cdk_ceddda9d.ArnFormat, jsii.sget(cls, "ARN_FORMAT"))

    @builtins.property
    @jsii.member(jsii_name="autoDiscovery")
    def auto_discovery(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "autoDiscovery"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''Specifies the name of the resource share.

        :see: `ResourceShare.Name <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name>`_
        :group: Inputs
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> _aws_cdk_aws_ram_ceddda9d.CfnResourceShare:
        '''The underlying ResourceShare CloudFormation resource.

        :see: `AWS::RAM::ResourceShare <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html>`_
        :group: Resources
        '''
        return typing.cast(_aws_cdk_aws_ram_ceddda9d.CfnResourceShare, jsii.get(self, "resource"))

    @builtins.property
    @jsii.member(jsii_name="resourceShareArn")
    def resource_share_arn(self) -> builtins.str:
        '''{@inheritdoc IResourceShare.resourceShareArn}.'''
        return typing.cast(builtins.str, jsii.get(self, "resourceShareArn"))

    @builtins.property
    @jsii.member(jsii_name="resourceShareId")
    def resource_share_id(self) -> builtins.str:
        '''{@inheritdoc IResourceShare.resourceShareId}.'''
        return typing.cast(builtins.str, jsii.get(self, "resourceShareId"))

    @builtins.property
    @jsii.member(jsii_name="allowExternalPrincipals")
    def allow_external_principals(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether principals outside your organization in AWS Organizations can be associated with a resource share.

        A value of ``true``
        lets you share with individual AWS accounts that are not in your
        organization. A value of ``false`` only has meaning if your account is a
        member of an AWS Organization.

        In order for an account to be auto discovered it must be part of the same
        CDK application. It must also be an explicitly defined environment and not
        environment agnostic.

        :see: `CDK Environments <https://docs.aws.amazon.com/cdk/v2/guide/environments.html>`_
        :group: Inputs
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "allowExternalPrincipals"))


@jsii.data_type(
    jsii_type="cdk-extensions.ram.ResourceShareAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "resource_share_arn": "resourceShareArn",
        "resource_share_id": "resourceShareId",
    },
)
class ResourceShareAttributes:
    def __init__(
        self,
        *,
        resource_share_arn: typing.Optional[builtins.str] = None,
        resource_share_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration for importing an existing RAM resource share.

        :param resource_share_arn: The Amazon Resource Name (ARN) of the RAM resource share.
        :param resource_share_id: The ID generated by AWS for the RAM resource share.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ac40e2f1fdf186c33063bf9f362920ff43b1e0af2163644b30465aa52e0111)
            check_type(argname="argument resource_share_arn", value=resource_share_arn, expected_type=type_hints["resource_share_arn"])
            check_type(argname="argument resource_share_id", value=resource_share_id, expected_type=type_hints["resource_share_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if resource_share_arn is not None:
            self._values["resource_share_arn"] = resource_share_arn
        if resource_share_id is not None:
            self._values["resource_share_id"] = resource_share_id

    @builtins.property
    def resource_share_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the RAM resource share.'''
        result = self._values.get("resource_share_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_share_id(self) -> typing.Optional[builtins.str]:
        '''The ID generated by AWS for the RAM resource share.'''
        result = self._values.get("resource_share_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceShareAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-extensions.ram.ResourceShareProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "allow_external_principals": "allowExternalPrincipals",
        "auto_discover_accounts": "autoDiscoverAccounts",
        "name": "name",
        "principals": "principals",
        "resources": "resources",
    },
)
class ResourceShareProps(_aws_cdk_ceddda9d.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        allow_external_principals: typing.Optional[builtins.bool] = None,
        auto_discover_accounts: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        principals: typing.Optional[typing.Sequence[ISharedPrincipal]] = None,
        resources: typing.Optional[typing.Sequence[ISharable]] = None,
    ) -> None:
        '''Configuration for ResourceShare resource.

        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param allow_external_principals: Specifies whether principals outside your organization in AWS Organizations can be associated with a resource share. A value of ``true`` lets you share with individual AWS accounts that are not in your organization. A value of ``false`` only has meaning if your account is a member of an AWS Organization. Default: true
        :param auto_discover_accounts: Controls whether the resource share should attempt to search for AWS accounts that are part of the same CDK application. Any accounts is finds will be added to the resource automatically and will be able to use the shared resources.
        :param name: Specifies the name of the resource share.
        :param principals: Specifies a list of one or more principals to associate with the resource share.
        :param resources: Specifies a list of AWS resources to share with the configured principal accounts and organizations.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb62df34d5bde1bdc947c6a54e24ebe4fcec362448ebb919d16c7795e296004)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument environment_from_arn", value=environment_from_arn, expected_type=type_hints["environment_from_arn"])
            check_type(argname="argument physical_name", value=physical_name, expected_type=type_hints["physical_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument allow_external_principals", value=allow_external_principals, expected_type=type_hints["allow_external_principals"])
            check_type(argname="argument auto_discover_accounts", value=auto_discover_accounts, expected_type=type_hints["auto_discover_accounts"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument principals", value=principals, expected_type=type_hints["principals"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if allow_external_principals is not None:
            self._values["allow_external_principals"] = allow_external_principals
        if auto_discover_accounts is not None:
            self._values["auto_discover_accounts"] = auto_discover_accounts
        if name is not None:
            self._values["name"] = name
        if principals is not None:
            self._values["principals"] = principals
        if resources is not None:
            self._values["resources"] = resources

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
    def allow_external_principals(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether principals outside your organization in AWS Organizations can be associated with a resource share.

        A value of ``true``
        lets you share with individual AWS accounts that are not in your
        organization. A value of ``false`` only has meaning if your account is a
        member of an AWS Organization.

        :default: true

        :see: `ResourceShare.AllowExternalPrinicpals <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-allowexternalprincipals>`_
        '''
        result = self._values.get("allow_external_principals")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_discover_accounts(self) -> typing.Optional[builtins.bool]:
        '''Controls whether the resource share should attempt to search for AWS accounts that are part of the same CDK application.

        Any accounts is finds
        will be added to the resource automatically and will be able to use the
        shared resources.
        '''
        result = self._values.get("auto_discover_accounts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the resource share.

        :see: `ResourceShare.Name <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-name>`_
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principals(self) -> typing.Optional[typing.List[ISharedPrincipal]]:
        '''Specifies a list of one or more principals to associate with the resource share.

        :see: `ResourceShare.Prinicipals <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-principals>`_
        '''
        result = self._values.get("principals")
        return typing.cast(typing.Optional[typing.List[ISharedPrincipal]], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[ISharable]]:
        '''Specifies a list of AWS resources to share with the configured principal accounts and organizations.

        :see: `ResourceShare.ResourceArns <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ram-resourceshare.html#cfn-ram-resourceshare-resourcearns>`_
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[ISharable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceShareProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISharedPrincipal)
class SharedPrincipal(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.ram.SharedPrincipal",
):
    @jsii.member(jsii_name="fromAccountId")
    @builtins.classmethod
    def from_account_id(cls, account: builtins.str) -> "SharedPrincipal":
        '''
        :param account: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90897854504bc9e9c937d7cccbae157c28ff738f739581ccdb0d7f9376de8fca)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromAccountId", [account]))

    @jsii.member(jsii_name="fromConstruct")
    @builtins.classmethod
    def from_construct(
        cls,
        construct: _constructs_77d1e7e8.IConstruct,
    ) -> "SharedPrincipal":
        '''
        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b46d20e57463b481fca96ab2c6ce1bd47507958d01e4d1f58dcebbe5e32b51d)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromConstruct", [construct]))

    @jsii.member(jsii_name="fromOrganizationalUnitArn")
    @builtins.classmethod
    def from_organizational_unit_arn(cls, arn: builtins.str) -> "SharedPrincipal":
        '''
        :param arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f910dddc5daeef82a97392f59e3ff874b9d0943f63fc3c4a769d5a753cd37da)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromOrganizationalUnitArn", [arn]))

    @jsii.member(jsii_name="fromOrganizationArn")
    @builtins.classmethod
    def from_organization_arn(cls, arn: builtins.str) -> "SharedPrincipal":
        '''
        :param arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26c107d132055290a7bccb032ca3e3046ded15737663e5554111f04b5b0f77cf)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromOrganizationArn", [arn]))

    @jsii.member(jsii_name="fromRole")
    @builtins.classmethod
    def from_role(cls, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> "SharedPrincipal":
        '''
        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eabde238082e347fdf798c93ca8ac885a4395c785d3b39bc0099374d23c725a2)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromRole", [role]))

    @jsii.member(jsii_name="fromStage")
    @builtins.classmethod
    def from_stage(cls, stage: _aws_cdk_ceddda9d.Stage) -> "SharedPrincipal":
        '''
        :param stage: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0426e584cdb97f8aee8e426a8c4f9cc115d26888e09a1dea286fc658d9aadaee)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromStage", [stage]))

    @jsii.member(jsii_name="fromUser")
    @builtins.classmethod
    def from_user(cls, user: _aws_cdk_aws_iam_ceddda9d.IUser) -> "SharedPrincipal":
        '''
        :param user: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__718dfe239150f6aa3b77c4ebfb9d54f1d6dc121bfb5c06b1520526f929f274cd)
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
        return typing.cast("SharedPrincipal", jsii.sinvoke(cls, "fromUser", [user]))

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''
        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad779f97340c272a7ebd6573c0d73056599eca1a424bc83a90a0c04fc883cb76)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(builtins.str, jsii.invoke(self, "bind", [_scope]))


__all__ = [
    "IResourceShare",
    "ISharable",
    "ISharedPrincipal",
    "ResourceShare",
    "ResourceShareAttributes",
    "ResourceShareProps",
    "SharedPrincipal",
]

publication.publish()

def _typecheckingstub__68c8b639eb94527586d9d176da9a63029ea8e58967aa01158dfe2f74674d502f(
    principal: ISharedPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be22743d8e2c78d6ea83ddd9575473468c95e1be8ecd7f17aa5ab3538a54477(
    resource: ISharable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb281a56c708e0bd3a7d012e40c232a2e15687212f795a42c8e0d138b544bdf8(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca72ec807b061d878f303339b081f503422720973adb273b601ddcd8837323e5(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b89945094c7aec402867b1ed7520f94687bad190e661891b7c1898124b67b3c8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    allow_external_principals: typing.Optional[builtins.bool] = None,
    auto_discover_accounts: typing.Optional[builtins.bool] = None,
    name: typing.Optional[builtins.str] = None,
    principals: typing.Optional[typing.Sequence[ISharedPrincipal]] = None,
    resources: typing.Optional[typing.Sequence[ISharable]] = None,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88128eec4703a4c5efee5fff5a5dc3ce1d302e98a357a770f84947748566b98b(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    resource_share_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac9771317d76c9329bed60d3fd242a81dc33abbd82e3a406b6f45e87fc07e9fa(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    *,
    resource_share_arn: typing.Optional[builtins.str] = None,
    resource_share_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ef793e59307e13cfc654aa867438f0369edaa2f4ed7119c7ed1b349d4bc4303(
    scope: _constructs_77d1e7e8.IConstruct,
    id: builtins.str,
    resource_share_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10317648344034fd5b5ca01d87cb09e1b4640473e70368a712092954fc9194d9(
    principal: ISharedPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37b07cbe6529ca7b8e8636fff5847d57fae2861e37fd631f972b1d71c6ffe532(
    resource: ISharable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ac40e2f1fdf186c33063bf9f362920ff43b1e0af2163644b30465aa52e0111(
    *,
    resource_share_arn: typing.Optional[builtins.str] = None,
    resource_share_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb62df34d5bde1bdc947c6a54e24ebe4fcec362448ebb919d16c7795e296004(
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    allow_external_principals: typing.Optional[builtins.bool] = None,
    auto_discover_accounts: typing.Optional[builtins.bool] = None,
    name: typing.Optional[builtins.str] = None,
    principals: typing.Optional[typing.Sequence[ISharedPrincipal]] = None,
    resources: typing.Optional[typing.Sequence[ISharable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90897854504bc9e9c937d7cccbae157c28ff738f739581ccdb0d7f9376de8fca(
    account: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b46d20e57463b481fca96ab2c6ce1bd47507958d01e4d1f58dcebbe5e32b51d(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f910dddc5daeef82a97392f59e3ff874b9d0943f63fc3c4a769d5a753cd37da(
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c107d132055290a7bccb032ca3e3046ded15737663e5554111f04b5b0f77cf(
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eabde238082e347fdf798c93ca8ac885a4395c785d3b39bc0099374d23c725a2(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0426e584cdb97f8aee8e426a8c4f9cc115d26888e09a1dea286fc658d9aadaee(
    stage: _aws_cdk_ceddda9d.Stage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__718dfe239150f6aa3b77c4ebfb9d54f1d6dc121bfb5c06b1520526f929f274cd(
    user: _aws_cdk_aws_iam_ceddda9d.IUser,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad779f97340c272a7ebd6573c0d73056599eca1a424bc83a90a0c04fc883cb76(
    _scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass
