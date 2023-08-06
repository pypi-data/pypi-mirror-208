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

import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class Domain(metaclass=jsii.JSIIMeta, jsii_type="cdk-extensions.route53.Domain"):
    def __init__(
        self,
        zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        is_public: builtins.bool,
        *,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        subdomain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param zone: -
        :param is_public: -
        :param certificate: 
        :param subdomain: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf1da44e0e90b58c0358dea218b559affe6ea6dd81d72103d0b6a84ddfa21b8)
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument is_public", value=is_public, expected_type=type_hints["is_public"])
        options = DomainOptions(certificate=certificate, subdomain=subdomain)

        jsii.create(self.__class__, self, [zone, is_public, options])

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''
        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c61aba1cc379140c4e89c20ec315747c83e85638d3c1e44472fd83866088381)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @builtins.property
    @jsii.member(jsii_name="isPublic")
    def is_public(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isPublic"))

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, jsii.get(self, "zone"))

    @builtins.property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="subdomain")
    def subdomain(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subdomain"))


@jsii.enum(jsii_type="cdk-extensions.route53.DomainDiscovery")
class DomainDiscovery(enum.Enum):
    ALL = "ALL"
    NONE = "NONE"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class DomainManager(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-extensions.route53.DomainManager",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="isDnsResolvable")
    @builtins.classmethod
    def is_dns_resolvable(cls, node: _constructs_77d1e7e8.IConstruct) -> builtins.bool:
        '''
        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86170ff6a2b54fc7d7504a11994e1150e2ab9dd7db165610c31b2485f7b898f6)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isDnsResolvable", [node]))


@jsii.data_type(
    jsii_type="cdk-extensions.route53.DomainOptions",
    jsii_struct_bases=[],
    name_mapping={"certificate": "certificate", "subdomain": "subdomain"},
)
class DomainOptions:
    def __init__(
        self,
        *,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        subdomain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param certificate: 
        :param subdomain: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8203735f86b56f3f063b195c355fd5c4504756ff77a90c7c8d5fac7e375c88c1)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate is not None:
            self._values["certificate"] = certificate
        if subdomain is not None:
            self._values["subdomain"] = subdomain

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def subdomain(self) -> typing.Optional[builtins.str]:
        result = self._values.get("subdomain")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Domains(metaclass=jsii.JSIIMeta, jsii_type="cdk-extensions.route53.Domains"):
    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, scope: _constructs_77d1e7e8.IConstruct) -> "Domains":
        '''
        :param scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd268d592409c2809fc1b7c3e38aa86859621550b58f67d1ece29a1dc4115de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("Domains", jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="add")
    def add(
        self,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        is_public: builtins.bool,
        *,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        subdomain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: -
        :param is_public: -
        :param certificate: 
        :param subdomain: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81432a8d00c9ba2bf0459929af8524df07005f90e8aecf9fda142e473b079936)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument is_public", value=is_public, expected_type=type_hints["is_public"])
        options = DomainOptions(certificate=certificate, subdomain=subdomain)

        return typing.cast(None, jsii.invoke(self, "add", [hosted_zone, is_public, options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ROOT")
    def ROOT(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "ROOT"))


@jsii.interface(jsii_type="cdk-extensions.route53.IDnsResolvable")
class IDnsResolvable(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="domainDiscovery")
    def domain_discovery(self) -> DomainDiscovery:
        ...

    @jsii.member(jsii_name="registerDomain")
    def register_domain(self, domain: Domain) -> None:
        '''
        :param domain: -
        '''
        ...


class _IDnsResolvableProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "cdk-extensions.route53.IDnsResolvable"

    @builtins.property
    @jsii.member(jsii_name="domainDiscovery")
    def domain_discovery(self) -> DomainDiscovery:
        return typing.cast(DomainDiscovery, jsii.get(self, "domainDiscovery"))

    @jsii.member(jsii_name="registerDomain")
    def register_domain(self, domain: Domain) -> None:
        '''
        :param domain: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93ac82d5bb4f1367ba14cacba38152e6be390027789f2e894acc6b21a55558cc)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        return typing.cast(None, jsii.invoke(self, "registerDomain", [domain]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDnsResolvable).__jsii_proxy_class__ = lambda : _IDnsResolvableProxy


__all__ = [
    "Domain",
    "DomainDiscovery",
    "DomainManager",
    "DomainOptions",
    "Domains",
    "IDnsResolvable",
]

publication.publish()

def _typecheckingstub__9cf1da44e0e90b58c0358dea218b559affe6ea6dd81d72103d0b6a84ddfa21b8(
    zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    is_public: builtins.bool,
    *,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    subdomain: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c61aba1cc379140c4e89c20ec315747c83e85638d3c1e44472fd83866088381(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86170ff6a2b54fc7d7504a11994e1150e2ab9dd7db165610c31b2485f7b898f6(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8203735f86b56f3f063b195c355fd5c4504756ff77a90c7c8d5fac7e375c88c1(
    *,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    subdomain: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd268d592409c2809fc1b7c3e38aa86859621550b58f67d1ece29a1dc4115de(
    scope: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81432a8d00c9ba2bf0459929af8524df07005f90e8aecf9fda142e473b079936(
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    is_public: builtins.bool,
    *,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    subdomain: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93ac82d5bb4f1367ba14cacba38152e6be390027789f2e894acc6b21a55558cc(
    domain: Domain,
) -> None:
    """Type checking stubs"""
    pass
