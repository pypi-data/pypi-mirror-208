'''
# Raindancers Network Construct Library...

The raindancers network package contains  constructs that construct to provide easy to use abstractions, particually for using in an enterprise network, with Transit Gateways, Cloudwan, Network Firewalls.

Note: This Construct Library is functional, but there is no promise thate that breaking changes could occur.    While this construct is highly opinionated, it seeks to solve a wide set of scenerios that its author has faced, and problems that others have described.   The author of this construct encourages and welcome PR's.  Please raise an issue to start

The EnterpriseVPC provides addtional methods from the standard ec2.Vpc construct, while maintaining compatiblity, so it can be used with other constructs that use the ec2.Vpc

A getting started example provides guidence in using the constructs in typescript cdk

* [Getting Started](./docs/gettingstarted.md)
* [Deploying VPC with Cloudwan](./docs/deployVpcts.md)
* [Create A shared Egress VPC, using AWS Network Firewalls](./docs/egress.md)
* [Transit Gateways and IPSec over DX](./docs/transitgateway.md)

Slack:  A good way to to get help with this construct, is to join the [cdk.dev] (https://cdk.dev/) slack channel.

This construct is published as a ready to import module for both typescript and python, via npm and pypi. Look here for details [constructs.dev](https://constructs.dev/packages/raindancers-network)
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_networkfirewall as _aws_cdk_aws_networkfirewall_ceddda9d
import aws_cdk.aws_networkmanager as _aws_cdk_aws_networkmanager_ceddda9d
import aws_cdk.aws_redshift_alpha as _aws_cdk_aws_redshift_alpha_9727f5af
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_route53resolver as _aws_cdk_aws_route53resolver_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sso as _aws_cdk_aws_sso_ceddda9d
import aws_cdk.custom_resources as _aws_cdk_custom_resources_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="raindancers-network.AddAwsServiceEndPointsProps",
    jsii_struct_bases=[],
    name_mapping={
        "services": "services",
        "subnet_group": "subnetGroup",
        "dynamo_db_gateway": "dynamoDbGateway",
        "s3_gateway_interface": "s3GatewayInterface",
    },
)
class AddAwsServiceEndPointsProps:
    def __init__(
        self,
        *,
        services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
        subnet_group: "SubnetGroup",
        dynamo_db_gateway: typing.Optional[builtins.bool] = None,
        s3_gateway_interface: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param services: 
        :param subnet_group: 
        :param dynamo_db_gateway: 
        :param s3_gateway_interface: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2cc1384bdc954b012b4ee9cbd2dc7b0d1f0c17055601fe2f3df5391ee1cbbc)
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument dynamo_db_gateway", value=dynamo_db_gateway, expected_type=type_hints["dynamo_db_gateway"])
            check_type(argname="argument s3_gateway_interface", value=s3_gateway_interface, expected_type=type_hints["s3_gateway_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "services": services,
            "subnet_group": subnet_group,
        }
        if dynamo_db_gateway is not None:
            self._values["dynamo_db_gateway"] = dynamo_db_gateway
        if s3_gateway_interface is not None:
            self._values["s3_gateway_interface"] = s3_gateway_interface

    @builtins.property
    def services(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]:
        '''
        :stability: experimental
        '''
        result = self._values.get("services")
        assert result is not None, "Required property 'services' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService], result)

    @builtins.property
    def subnet_group(self) -> "SubnetGroup":
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast("SubnetGroup", result)

    @builtins.property
    def dynamo_db_gateway(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("dynamo_db_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_gateway_interface(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_gateway_interface")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddAwsServiceEndPointsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddCoreRoutesProps",
    jsii_struct_bases=[],
    name_mapping={
        "attachment_id": "attachmentId",
        "core_name": "coreName",
        "description": "description",
        "destination_cidr_blocks": "destinationCidrBlocks",
        "policy_table_arn": "policyTableArn",
        "segments": "segments",
    },
)
class AddCoreRoutesProps:
    def __init__(
        self,
        *,
        attachment_id: builtins.str,
        core_name: builtins.str,
        description: builtins.str,
        destination_cidr_blocks: typing.Sequence[builtins.str],
        policy_table_arn: builtins.str,
        segments: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param attachment_id: 
        :param core_name: 
        :param description: 
        :param destination_cidr_blocks: 
        :param policy_table_arn: 
        :param segments: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8f4daaa6aed14129a681e485c910e5042db7338e8b5dcc6f76e78e3ca80885)
            check_type(argname="argument attachment_id", value=attachment_id, expected_type=type_hints["attachment_id"])
            check_type(argname="argument core_name", value=core_name, expected_type=type_hints["core_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument destination_cidr_blocks", value=destination_cidr_blocks, expected_type=type_hints["destination_cidr_blocks"])
            check_type(argname="argument policy_table_arn", value=policy_table_arn, expected_type=type_hints["policy_table_arn"])
            check_type(argname="argument segments", value=segments, expected_type=type_hints["segments"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attachment_id": attachment_id,
            "core_name": core_name,
            "description": description,
            "destination_cidr_blocks": destination_cidr_blocks,
            "policy_table_arn": policy_table_arn,
            "segments": segments,
        }

    @builtins.property
    def attachment_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("attachment_id")
        assert result is not None, "Required property 'attachment_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def core_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("core_name")
        assert result is not None, "Required property 'core_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_cidr_blocks(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_cidr_blocks")
        assert result is not None, "Required property 'destination_cidr_blocks' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def policy_table_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("policy_table_arn")
        assert result is not None, "Required property 'policy_table_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def segments(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("segments")
        assert result is not None, "Required property 'segments' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddCoreRoutesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddEnterprizeZoneProps",
    jsii_struct_bases=[],
    name_mapping={
        "domainname": "domainname",
        "hub_vpcs": "hubVpcs",
        "is_hub_vpc": "isHubVpc",
    },
)
class AddEnterprizeZoneProps:
    def __init__(
        self,
        *,
        domainname: builtins.str,
        hub_vpcs: typing.Sequence[typing.Union["HubVpc", typing.Dict[builtins.str, typing.Any]]],
        is_hub_vpc: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param domainname: 
        :param hub_vpcs: 
        :param is_hub_vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013fa385be66a7ab1fdaf16408736a597092b20533f6f8f18fdb0e0cf1a1fe8b)
            check_type(argname="argument domainname", value=domainname, expected_type=type_hints["domainname"])
            check_type(argname="argument hub_vpcs", value=hub_vpcs, expected_type=type_hints["hub_vpcs"])
            check_type(argname="argument is_hub_vpc", value=is_hub_vpc, expected_type=type_hints["is_hub_vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domainname": domainname,
            "hub_vpcs": hub_vpcs,
        }
        if is_hub_vpc is not None:
            self._values["is_hub_vpc"] = is_hub_vpc

    @builtins.property
    def domainname(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("domainname")
        assert result is not None, "Required property 'domainname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hub_vpcs(self) -> typing.List["HubVpc"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hub_vpcs")
        assert result is not None, "Required property 'hub_vpcs' is missing"
        return typing.cast(typing.List["HubVpc"], result)

    @builtins.property
    def is_hub_vpc(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("is_hub_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddEnterprizeZoneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddR53ZoneProps",
    jsii_struct_bases=[],
    name_mapping={"zone": "zone", "central_vpc": "centralVpc"},
)
class AddR53ZoneProps:
    def __init__(
        self,
        *,
        zone: builtins.str,
        central_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''
        :param zone: 
        :param central_vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53e9d3cadea14460a1ee6ecbb2d70b4538efae7cd8d786e6ccabc0a8ed3cd6fe)
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument central_vpc", value=central_vpc, expected_type=type_hints["central_vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "zone": zone,
        }
        if central_vpc is not None:
            self._values["central_vpc"] = central_vpc

    @builtins.property
    def zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def central_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("central_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddR53ZoneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddRoutesProps",
    jsii_struct_bases=[],
    name_mapping={
        "cidr": "cidr",
        "description": "description",
        "destination": "destination",
        "subnet_groups": "subnetGroups",
        "cloudwan_name": "cloudwanName",
        "network_firewall_arn": "networkFirewallArn",
    },
)
class AddRoutesProps:
    def __init__(
        self,
        *,
        cidr: typing.Sequence[builtins.str],
        description: builtins.str,
        destination: "Destination",
        subnet_groups: typing.Sequence[builtins.str],
        cloudwan_name: typing.Optional[builtins.str] = None,
        network_firewall_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Propertys for Adding Routes in VPC.

        :param cidr: 
        :param description: 
        :param destination: 
        :param subnet_groups: 
        :param cloudwan_name: 
        :param network_firewall_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8caa7ea9992a583a226f2a016e499bd005c8a4d98f8b16c728ed2d3b24a6caf)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument subnet_groups", value=subnet_groups, expected_type=type_hints["subnet_groups"])
            check_type(argname="argument cloudwan_name", value=cloudwan_name, expected_type=type_hints["cloudwan_name"])
            check_type(argname="argument network_firewall_arn", value=network_firewall_arn, expected_type=type_hints["network_firewall_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr": cidr,
            "description": description,
            "destination": destination,
            "subnet_groups": subnet_groups,
        }
        if cloudwan_name is not None:
            self._values["cloudwan_name"] = cloudwan_name
        if network_firewall_arn is not None:
            self._values["network_firewall_arn"] = network_firewall_arn

    @builtins.property
    def cidr(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination(self) -> "Destination":
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("Destination", result)

    @builtins.property
    def subnet_groups(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_groups")
        assert result is not None, "Required property 'subnet_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cloudwan_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cloudwan_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_firewall_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("network_firewall_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddRoutesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddStatefulRulesProps",
    jsii_struct_bases=[],
    name_mapping={"aws_managed_rules": "awsManagedRules"},
)
class AddStatefulRulesProps:
    def __init__(
        self,
        *,
        aws_managed_rules: typing.Sequence["ManagedAwsFirewallRules"],
    ) -> None:
        '''
        :param aws_managed_rules: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427ae99d97748b5c424729df449196fc4c1f2fc7265a24ffcadc57c85265c911)
            check_type(argname="argument aws_managed_rules", value=aws_managed_rules, expected_type=type_hints["aws_managed_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aws_managed_rules": aws_managed_rules,
        }

    @builtins.property
    def aws_managed_rules(self) -> typing.List["ManagedAwsFirewallRules"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("aws_managed_rules")
        assert result is not None, "Required property 'aws_managed_rules' is missing"
        return typing.cast(typing.List["ManagedAwsFirewallRules"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddStatefulRulesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AddStatelessRulesProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "group_name": "groupName",
        "rules": "rules",
    },
)
class AddStatelessRulesProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        group_name: builtins.str,
        rules: typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param description: 
        :param group_name: 
        :param rules: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a97874b1f84366909c00c07fab79e125790b203b8f0c095a88429dd5062f0bda)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "group_name": group_name,
            "rules": rules,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rules(
        self,
    ) -> typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("rules")
        assert result is not None, "Required property 'rules' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddStatelessRulesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.ApplianceMode")
class ApplianceMode(enum.Enum):
    '''(experimental) Propertys for Appliance Mode.

    :stability: experimental
    '''

    ENABLED = "ENABLED"
    '''(experimental) enable Connecting VPC to TransitGateway in Appliance Mode.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.AssignmentAttributes",
    jsii_struct_bases=[],
    name_mapping={},
)
class AssignmentAttributes:
    def __init__(self) -> None:
        '''(experimental) Attributes for an assignment of which there are none.

        :stability: experimental
        '''
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssignmentAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AssignmentOptions",
    jsii_struct_bases=[],
    name_mapping={
        "principal": "principal",
        "target_id": "targetId",
        "target_type": "targetType",
    },
)
class AssignmentOptions:
    def __init__(
        self,
        *,
        principal: typing.Union["PrincipalProperty", typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional["TargetTypes"] = None,
    ) -> None:
        '''(experimental) The options for creating an assignment.

        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        if isinstance(principal, dict):
            principal = PrincipalProperty(**principal)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ea70b6b68927c926c03c2b997826b441c2601f5dbbd2fc437f9e73dda895545)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "principal": principal,
            "target_id": target_id,
        }
        if target_type is not None:
            self._values["target_type"] = target_type

    @builtins.property
    def principal(self) -> "PrincipalProperty":
        '''(experimental) The principal to assign the permission set to.

        :stability: experimental
        '''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast("PrincipalProperty", result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''(experimental) The target id the permission set will be assigned to.

        :stability: experimental
        '''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> typing.Optional["TargetTypes"]:
        '''(experimental) The entity type for which the assignment will be created.

        :default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        result = self._values.get("target_type")
        return typing.cast(typing.Optional["TargetTypes"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssignmentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AssignmentProps",
    jsii_struct_bases=[AssignmentOptions],
    name_mapping={
        "principal": "principal",
        "target_id": "targetId",
        "target_type": "targetType",
        "permission_set": "permissionSet",
    },
)
class AssignmentProps(AssignmentOptions):
    def __init__(
        self,
        *,
        principal: typing.Union["PrincipalProperty", typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional["TargetTypes"] = None,
        permission_set: "IPermissionSet",
    ) -> None:
        '''(experimental) The properties of a new assignment.

        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        :param permission_set: (experimental) The permission set to assign to the principal.

        :stability: experimental
        '''
        if isinstance(principal, dict):
            principal = PrincipalProperty(**principal)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2974dcb321c18d62191df7e7fca3d2abc1db70278ba6d1257acc8ad0dd3b5278)
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
            check_type(argname="argument permission_set", value=permission_set, expected_type=type_hints["permission_set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "principal": principal,
            "target_id": target_id,
            "permission_set": permission_set,
        }
        if target_type is not None:
            self._values["target_type"] = target_type

    @builtins.property
    def principal(self) -> "PrincipalProperty":
        '''(experimental) The principal to assign the permission set to.

        :stability: experimental
        '''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast("PrincipalProperty", result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''(experimental) The target id the permission set will be assigned to.

        :stability: experimental
        '''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> typing.Optional["TargetTypes"]:
        '''(experimental) The entity type for which the assignment will be created.

        :default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        result = self._values.get("target_type")
        return typing.cast(typing.Optional["TargetTypes"], result)

    @builtins.property
    def permission_set(self) -> "IPermissionSet":
        '''(experimental) The permission set to assign to the principal.

        :stability: experimental
        '''
        result = self._values.get("permission_set")
        assert result is not None, "Required property 'permission_set' is missing"
        return typing.cast("IPermissionSet", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssignmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AssociateSharedResolverRule(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.AssociateSharedResolverRule",
):
    '''(experimental) Associate a resolver rule that has been shared to this account.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_names: typing.Sequence[builtins.str],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_names: (experimental) domainNames which are to be associated.
        :param vpc: (experimental) The VPC which will be assocaited with the ResolverRules.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe2f05a522631dcde421bc7a12ed88dd269841faf2a1011fca3219a3036f747)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AssociateSharedResolverRuleProps(domain_names=domain_names, vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.AssociateSharedResolverRuleProps",
    jsii_struct_bases=[],
    name_mapping={"domain_names": "domainNames", "vpc": "vpc"},
)
class AssociateSharedResolverRuleProps:
    def __init__(
        self,
        *,
        domain_names: typing.Sequence[builtins.str],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param domain_names: (experimental) domainNames which are to be associated.
        :param vpc: (experimental) The VPC which will be assocaited with the ResolverRules.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a800dc7ac62dffed3914b02d40756c231878518e5ff905efd1627f5adbdab30)
            check_type(argname="argument domain_names", value=domain_names, expected_type=type_hints["domain_names"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_names": domain_names,
            "vpc": vpc,
        }

    @builtins.property
    def domain_names(self) -> typing.List[builtins.str]:
        '''(experimental) domainNames which are to be associated.

        :stability: experimental
        '''
        result = self._values.get("domain_names")
        assert result is not None, "Required property 'domain_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) The VPC which will be assocaited with the ResolverRules.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssociateSharedResolverRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.AssociationMethod")
class AssociationMethod(enum.Enum):
    '''(experimental) Association Methods.

    :stability: experimental
    '''

    CONSTANT = "CONSTANT"
    '''
    :stability: experimental
    '''
    TAG = "TAG"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.AttachToCloudWanProps",
    jsii_struct_bases=[],
    name_mapping={
        "core_network_name": "coreNetworkName",
        "segment_name": "segmentName",
        "appliance_mode": "applianceMode",
        "attachment_subnet_group": "attachmentSubnetGroup",
    },
)
class AttachToCloudWanProps:
    def __init__(
        self,
        *,
        core_network_name: builtins.str,
        segment_name: builtins.str,
        appliance_mode: typing.Optional[builtins.bool] = None,
        attachment_subnet_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Propertys for Attaching to a Cloudwan Core Network.

        :param core_network_name: (experimental) corenetworkName.
        :param segment_name: 
        :param appliance_mode: 
        :param attachment_subnet_group: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c50631041fbe2ac8aeab9261d67d56d19e35dfc4b66c6474ea616c1b4b5c2c77)
            check_type(argname="argument core_network_name", value=core_network_name, expected_type=type_hints["core_network_name"])
            check_type(argname="argument segment_name", value=segment_name, expected_type=type_hints["segment_name"])
            check_type(argname="argument appliance_mode", value=appliance_mode, expected_type=type_hints["appliance_mode"])
            check_type(argname="argument attachment_subnet_group", value=attachment_subnet_group, expected_type=type_hints["attachment_subnet_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "core_network_name": core_network_name,
            "segment_name": segment_name,
        }
        if appliance_mode is not None:
            self._values["appliance_mode"] = appliance_mode
        if attachment_subnet_group is not None:
            self._values["attachment_subnet_group"] = attachment_subnet_group

    @builtins.property
    def core_network_name(self) -> builtins.str:
        '''(experimental) corenetworkName.

        :stability: experimental
        '''
        result = self._values.get("core_network_name")
        assert result is not None, "Required property 'core_network_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def segment_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("segment_name")
        assert result is not None, "Required property 'segment_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def appliance_mode(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("appliance_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def attachment_subnet_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("attachment_subnet_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachToCloudWanProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AttachToTransitGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "transit_gateway": "transitGateway",
        "applicance_mode": "applicanceMode",
        "attachment_subnet_group": "attachmentSubnetGroup",
    },
)
class AttachToTransitGatewayProps:
    def __init__(
        self,
        *,
        transit_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway,
        applicance_mode: typing.Optional[ApplianceMode] = None,
        attachment_subnet_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Propertys to attach the Vpc To Transit Gateway.

        :param transit_gateway: (experimental) the TransitGateway to connect to.
        :param applicance_mode: (experimental) Will this be connected in appliance mode ( used if you have Network Firewalls ).
        :param attachment_subnet_group: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ea4110bef21c88d23180cffa72e93a9cbcc40f39f7b0347527f0873a351dac)
            check_type(argname="argument transit_gateway", value=transit_gateway, expected_type=type_hints["transit_gateway"])
            check_type(argname="argument applicance_mode", value=applicance_mode, expected_type=type_hints["applicance_mode"])
            check_type(argname="argument attachment_subnet_group", value=attachment_subnet_group, expected_type=type_hints["attachment_subnet_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "transit_gateway": transit_gateway,
        }
        if applicance_mode is not None:
            self._values["applicance_mode"] = applicance_mode
        if attachment_subnet_group is not None:
            self._values["attachment_subnet_group"] = attachment_subnet_group

    @builtins.property
    def transit_gateway(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway:
        '''(experimental) the TransitGateway to connect to.

        :stability: experimental
        '''
        result = self._values.get("transit_gateway")
        assert result is not None, "Required property 'transit_gateway' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway, result)

    @builtins.property
    def applicance_mode(self) -> typing.Optional[ApplianceMode]:
        '''(experimental) Will this be connected in appliance mode ( used if you have Network Firewalls ).

        :stability: experimental
        '''
        result = self._values.get("applicance_mode")
        return typing.cast(typing.Optional[ApplianceMode], result)

    @builtins.property
    def attachment_subnet_group(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("attachment_subnet_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachToTransitGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.AttachmentCondition")
class AttachmentCondition(enum.Enum):
    '''(experimental) Attachment Conditions.

    :stability: experimental
    '''

    ANY = "ANY"
    '''
    :stability: experimental
    '''
    RESOURCE_ID = "RESOURCE_ID"
    '''
    :stability: experimental
    '''
    ACCOUNT_ID = "ACCOUNT_ID"
    '''
    :stability: experimental
    '''
    REGION = "REGION"
    '''
    :stability: experimental
    '''
    ATTACHMENT_TYPE = "ATTACHMENT_TYPE"
    '''
    :stability: experimental
    '''
    TAG_EXISTS = "TAG_EXISTS"
    '''
    :stability: experimental
    '''
    TAG_VALUE = "TAG_VALUE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.AttachmentConditions",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "key": "key",
        "operator": "operator",
        "value": "value",
    },
)
class AttachmentConditions:
    def __init__(
        self,
        *,
        type: AttachmentCondition,
        key: typing.Optional[builtins.str] = None,
        operator: typing.Optional["Operators"] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) an attachmentconditions.

        :param type: 
        :param key: 
        :param operator: 
        :param value: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5656f7cf3af493453fb7cd73bb01af8aa61698a67ee1da580a06b8992b3cb7bb)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if key is not None:
            self._values["key"] = key
        if operator is not None:
            self._values["operator"] = operator
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def type(self) -> AttachmentCondition:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(AttachmentCondition, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional["Operators"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional["Operators"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachmentConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AttachmentPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "conditions": "conditions",
        "rule_number": "ruleNumber",
        "condition_logic": "conditionLogic",
        "description": "description",
    },
)
class AttachmentPolicy:
    def __init__(
        self,
        *,
        action: typing.Union["AttachmentPolicyAction", typing.Dict[builtins.str, typing.Any]],
        conditions: typing.Sequence[typing.Union[AttachmentConditions, typing.Dict[builtins.str, typing.Any]]],
        rule_number: jsii.Number,
        condition_logic: typing.Optional["ConditionLogic"] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) an attachment policy.

        :param action: 
        :param conditions: 
        :param rule_number: 
        :param condition_logic: 
        :param description: 

        :stability: experimental
        '''
        if isinstance(action, dict):
            action = AttachmentPolicyAction(**action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78d7306a292c43a1d00323d5e298f6e6d7d86dd1bd56a81371f7ca98fadbfde8)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument conditions", value=conditions, expected_type=type_hints["conditions"])
            check_type(argname="argument rule_number", value=rule_number, expected_type=type_hints["rule_number"])
            check_type(argname="argument condition_logic", value=condition_logic, expected_type=type_hints["condition_logic"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "conditions": conditions,
            "rule_number": rule_number,
        }
        if condition_logic is not None:
            self._values["condition_logic"] = condition_logic
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def action(self) -> "AttachmentPolicyAction":
        '''
        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast("AttachmentPolicyAction", result)

    @builtins.property
    def conditions(self) -> typing.List[AttachmentConditions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast(typing.List[AttachmentConditions], result)

    @builtins.property
    def rule_number(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("rule_number")
        assert result is not None, "Required property 'rule_number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def condition_logic(self) -> typing.Optional["ConditionLogic"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("condition_logic")
        return typing.cast(typing.Optional["ConditionLogic"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachmentPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.AttachmentPolicyAction",
    jsii_struct_bases=[],
    name_mapping={"association_method": "associationMethod", "segment": "segment"},
)
class AttachmentPolicyAction:
    def __init__(
        self,
        *,
        association_method: AssociationMethod,
        segment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attachment Policy Action.

        :param association_method: (experimental) The Assocation Method.
        :param segment: (experimental) The Segment this applies to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9918da80216c2f729d8c021ce398f10448c1da901e5f407303774b4acae3df)
            check_type(argname="argument association_method", value=association_method, expected_type=type_hints["association_method"])
            check_type(argname="argument segment", value=segment, expected_type=type_hints["segment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "association_method": association_method,
        }
        if segment is not None:
            self._values["segment"] = segment

    @builtins.property
    def association_method(self) -> AssociationMethod:
        '''(experimental) The Assocation Method.

        :stability: experimental
        '''
        result = self._values.get("association_method")
        assert result is not None, "Required property 'association_method' is missing"
        return typing.cast(AssociationMethod, result)

    @builtins.property
    def segment(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Segment this applies to.

        :stability: experimental
        '''
        result = self._values.get("segment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttachmentPolicyAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsManagedDNSFirewallRuleGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.AwsManagedDNSFirewallRuleGroup",
):
    '''
    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__295ac7c5386853c57aa011ef974b13862e08a4e8a24367c9355299fcf8438a42)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="resolverRuleId")
    def resolver_rule_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "resolverRuleId"))

    @resolver_rule_id.setter
    def resolver_rule_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df36a7c74d6d2d1f168216bdf55f5b9c6699edad44965470a30eea7983786132)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resolverRuleId", value)


@jsii.enum(jsii_type="raindancers-network.AwsRegions")
class AwsRegions(enum.Enum):
    '''
    :stability: experimental
    '''

    US_EAST_1 = "US_EAST_1"
    '''
    :stability: experimental
    '''
    US_EAST_2 = "US_EAST_2"
    '''
    :stability: experimental
    '''
    US_WEST_1 = "US_WEST_1"
    '''
    :stability: experimental
    '''
    US_WEST_2 = "US_WEST_2"
    '''
    :stability: experimental
    '''
    AF_SOUTH_1 = "AF_SOUTH_1"
    '''
    :stability: experimental
    '''
    AP_EAST_1 = "AP_EAST_1"
    '''
    :stability: experimental
    '''
    AP_SOUTH_1 = "AP_SOUTH_1"
    '''
    :stability: experimental
    '''
    AP_SOUTH_2 = "AP_SOUTH_2"
    '''
    :stability: experimental
    '''
    AP_SOUTHEAST_1 = "AP_SOUTHEAST_1"
    '''
    :stability: experimental
    '''
    AP_SOUTHEAST_2 = "AP_SOUTHEAST_2"
    '''
    :stability: experimental
    '''
    AP_SOUTHEAST_3 = "AP_SOUTHEAST_3"
    '''
    :stability: experimental
    '''
    AP_SOUTHEAST_4 = "AP_SOUTHEAST_4"
    '''
    :stability: experimental
    '''
    AP_NORTHEAST_1 = "AP_NORTHEAST_1"
    '''
    :stability: experimental
    '''
    AP_NORTHEAST_2 = "AP_NORTHEAST_2"
    '''
    :stability: experimental
    '''
    AP_NORTHEAST_3 = "AP_NORTHEAST_3"
    '''
    :stability: experimental
    '''
    CA_CENTRAL_1 = "CA_CENTRAL_1"
    '''
    :stability: experimental
    '''
    EU_SOUTH_1 = "EU_SOUTH_1"
    '''
    :stability: experimental
    '''
    EU_WEST_1 = "EU_WEST_1"
    '''
    :stability: experimental
    '''
    EU_WEST_2 = "EU_WEST_2"
    '''
    :stability: experimental
    '''
    EU_WEST_3 = "EU_WEST_3"
    '''
    :stability: experimental
    '''
    EU_SOUTH_2 = "EU_SOUTH_2"
    '''
    :stability: experimental
    '''
    EU_NORTH_1 = "EU_NORTH_1"
    '''
    :stability: experimental
    '''
    EU_CENTRAL_1 = "EU_CENTRAL_1"
    '''
    :stability: experimental
    '''
    EU_CENTRAL_2 = "EU_CENTRAL_2"
    '''
    :stability: experimental
    '''
    ME_SOUTH_1 = "ME_SOUTH_1"
    '''
    :stability: experimental
    '''
    ME_CENTRAL = "ME_CENTRAL"
    '''
    :stability: experimental
    '''
    SA_EAST_1 = "SA_EAST_1"
    '''
    :stability: experimental
    '''


class AwsServiceEndPoints(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.AwsServiceEndPoints",
):
    '''(experimental) Provisions a set of AWS Service Endpoints in a VPC.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        dynamo_db_gateway_interface: typing.Optional[builtins.bool] = None,
        s3_gateway_interface: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: The scope that this construct is created in.
        :param id: Id for the construct.
        :param services: (experimental) An arry of InterfaceVPCEndpoints.
        :param subnet_group: (experimental) Subnet Group in which to create the service. Typically a subnet Dedicated to the task
        :param vpc: (experimental) The vpc in which the service is created.
        :param dynamo_db_gateway_interface: (experimental) indicate true for a Dynamo Gateway Interface.
        :param s3_gateway_interface: (experimental) indicate true for a S3 Gateway Interface.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f970033413b65cd5ea91ac0d063fd19875e9d066694dcb983b74553243f5f7d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AwsServiceEndPointsProps(
            services=services,
            subnet_group=subnet_group,
            vpc=vpc,
            dynamo_db_gateway_interface=dynamo_db_gateway_interface,
            s3_gateway_interface=s3_gateway_interface,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.AwsServiceEndPointsProps",
    jsii_struct_bases=[],
    name_mapping={
        "services": "services",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "dynamo_db_gateway_interface": "dynamoDBGatewayInterface",
        "s3_gateway_interface": "s3GatewayInterface",
    },
)
class AwsServiceEndPointsProps:
    def __init__(
        self,
        *,
        services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        dynamo_db_gateway_interface: typing.Optional[builtins.bool] = None,
        s3_gateway_interface: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties to create a set of AWS service Endpoints.

        :param services: (experimental) An arry of InterfaceVPCEndpoints.
        :param subnet_group: (experimental) Subnet Group in which to create the service. Typically a subnet Dedicated to the task
        :param vpc: (experimental) The vpc in which the service is created.
        :param dynamo_db_gateway_interface: (experimental) indicate true for a Dynamo Gateway Interface.
        :param s3_gateway_interface: (experimental) indicate true for a S3 Gateway Interface.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1db27ca13d06e1bdec88c7fe57e45dab839525425fd9867066af33785516dfd3)
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument dynamo_db_gateway_interface", value=dynamo_db_gateway_interface, expected_type=type_hints["dynamo_db_gateway_interface"])
            check_type(argname="argument s3_gateway_interface", value=s3_gateway_interface, expected_type=type_hints["s3_gateway_interface"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "services": services,
            "subnet_group": subnet_group,
            "vpc": vpc,
        }
        if dynamo_db_gateway_interface is not None:
            self._values["dynamo_db_gateway_interface"] = dynamo_db_gateway_interface
        if s3_gateway_interface is not None:
            self._values["s3_gateway_interface"] = s3_gateway_interface

    @builtins.property
    def services(
        self,
    ) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService]:
        '''(experimental) An arry of InterfaceVPCEndpoints.

        :stability: experimental
        '''
        result = self._values.get("services")
        assert result is not None, "Required property 'services' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService], result)

    @builtins.property
    def subnet_group(self) -> builtins.str:
        '''(experimental) Subnet Group in which to create the service.

        Typically a subnet Dedicated to the task

        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) The vpc in which the service is created.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def dynamo_db_gateway_interface(self) -> typing.Optional[builtins.bool]:
        '''(experimental) indicate true for a Dynamo Gateway Interface.

        :stability: experimental
        '''
        result = self._values.get("dynamo_db_gateway_interface")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_gateway_interface(self) -> typing.Optional[builtins.bool]:
        '''(experimental) indicate true for a S3 Gateway Interface.

        :stability: experimental
        '''
        result = self._values.get("s3_gateway_interface")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsServiceEndPointsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CentralAccountAssnRole(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CentralAccountAssnRole",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        org_id: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param org_id: 
        :param vpc: 
        :param role_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b72ccaa8adb0b093daefe827dfeaaabcacbafb19a06a9c5e0ac5a11938a0302)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CentralAccountAssnRoleProps(
            org_id=org_id, vpc=vpc, role_name=role_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="assnRole")
    def assn_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "assnRole"))


@jsii.data_type(
    jsii_type="raindancers-network.CentralAccountAssnRoleProps",
    jsii_struct_bases=[],
    name_mapping={"org_id": "orgId", "vpc": "vpc", "role_name": "roleName"},
)
class CentralAccountAssnRoleProps:
    def __init__(
        self,
        *,
        org_id: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param org_id: 
        :param vpc: 
        :param role_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0764ca0676ca4e5b53724b53e8505a9aa92aaa3d13a4c4a8097d5d063c130fb)
            check_type(argname="argument org_id", value=org_id, expected_type=type_hints["org_id"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "org_id": org_id,
            "vpc": vpc,
        }
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def org_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("org_id")
        assert result is not None, "Required property 'org_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CentralAccountAssnRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CentralResolverRules(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CentralResolverRules",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domains: typing.Sequence[builtins.str],
        resolvers: "R53Resolverendpoints",
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domains: 
        :param resolvers: 
        :param vpc: 
        :param vpc_search_tag: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eefe32aca0c0c27b7a0521a3ee4b00641400743736777fb3defce6acbaf6e482)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CentralResolverRulesProps(
            domains=domains,
            resolvers=resolvers,
            vpc=vpc,
            vpc_search_tag=vpc_search_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.CentralResolverRulesProps",
    jsii_struct_bases=[],
    name_mapping={
        "domains": "domains",
        "resolvers": "resolvers",
        "vpc": "vpc",
        "vpc_search_tag": "vpcSearchTag",
    },
)
class CentralResolverRulesProps:
    def __init__(
        self,
        *,
        domains: typing.Sequence[builtins.str],
        resolvers: "R53Resolverendpoints",
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
    ) -> None:
        '''
        :param domains: 
        :param resolvers: 
        :param vpc: 
        :param vpc_search_tag: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff0976b8e2c7097d1f5dc6b7644236dc11eb8d5644975ed7d88524fd8fbccde2)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument resolvers", value=resolvers, expected_type=type_hints["resolvers"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_search_tag", value=vpc_search_tag, expected_type=type_hints["vpc_search_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
            "resolvers": resolvers,
            "vpc": vpc,
        }
        if vpc_search_tag is not None:
            self._values["vpc_search_tag"] = vpc_search_tag

    @builtins.property
    def domains(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def resolvers(self) -> "R53Resolverendpoints":
        '''
        :stability: experimental
        '''
        result = self._values.get("resolvers")
        assert result is not None, "Required property 'resolvers' is missing"
        return typing.cast("R53Resolverendpoints", result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def vpc_search_tag(self) -> typing.Optional[_aws_cdk_ceddda9d.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_search_tag")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CentralResolverRulesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.CloudWanRoutingProtocolProps",
    jsii_struct_bases=[],
    name_mapping={
        "subnet_groups": "subnetGroups",
        "accept_route_filter": "acceptRouteFilter",
        "deny_route_filter": "denyRouteFilter",
    },
)
class CloudWanRoutingProtocolProps:
    def __init__(
        self,
        *,
        subnet_groups: typing.Sequence[builtins.str],
        accept_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param subnet_groups: 
        :param accept_route_filter: 
        :param deny_route_filter: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37f3a4e0c0f78aa85706cbccf62ee78c015085c09ce18d7e3171779b4f115c3e)
            check_type(argname="argument subnet_groups", value=subnet_groups, expected_type=type_hints["subnet_groups"])
            check_type(argname="argument accept_route_filter", value=accept_route_filter, expected_type=type_hints["accept_route_filter"])
            check_type(argname="argument deny_route_filter", value=deny_route_filter, expected_type=type_hints["deny_route_filter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subnet_groups": subnet_groups,
        }
        if accept_route_filter is not None:
            self._values["accept_route_filter"] = accept_route_filter
        if deny_route_filter is not None:
            self._values["deny_route_filter"] = deny_route_filter

    @builtins.property
    def subnet_groups(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_groups")
        assert result is not None, "Required property 'subnet_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def accept_route_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("accept_route_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deny_route_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("deny_route_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudWanRoutingProtocolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudWanTGW(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CloudWanTGW",
):
    '''(experimental) Create a TransitGateway That is attached to Cloudwan.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        amazon_side_asn: builtins.str,
        attachment_segment: builtins.str,
        cloudwan: "CoreNetwork",
        description: builtins.str,
        cloud_wan_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_route_in_segments: typing.Optional[typing.Sequence[builtins.str]] = None,
        tg_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: scope in which the resource is c.
        :param id: -
        :param amazon_side_asn: 
        :param attachment_segment: 
        :param cloudwan: 
        :param description: 
        :param cloud_wan_cidr: 
        :param default_route_in_segments: 
        :param tg_cidr: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb29b77f94b56b505b6c2c5885a56172e7ca09a17cfb0c14ba33808dbcea3425)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TGWOnCloudWanProps(
            amazon_side_asn=amazon_side_asn,
            attachment_segment=attachment_segment,
            cloudwan=cloudwan,
            description=description,
            cloud_wan_cidr=cloud_wan_cidr,
            default_route_in_segments=default_route_in_segments,
            tg_cidr=tg_cidr,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDXGateway")
    def add_dx_gateway(
        self,
        dxgatewayname: builtins.str,
        dxgateway_asn: jsii.Number,
    ) -> builtins.str:
        '''(experimental) provision a DX Gateway and attach it to the transit gateway.

        :param dxgatewayname: The name of the dxgateway.
        :param dxgateway_asn: An ASN for the Dxgateway.

        :return: Direct Connect gatewayId

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a749f884289c3b1b00cfed1607d4ab9219948805b406babba0241b61a66980)
            check_type(argname="argument dxgatewayname", value=dxgatewayname, expected_type=type_hints["dxgatewayname"])
            check_type(argname="argument dxgateway_asn", value=dxgateway_asn, expected_type=type_hints["dxgateway_asn"])
        return typing.cast(builtins.str, jsii.invoke(self, "addDXGateway", [dxgatewayname, dxgateway_asn]))

    @jsii.member(jsii_name="adds2sVPN")
    def adds2s_vpn(
        self,
        name: builtins.str,
        *,
        customer_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway,
        vpnspec: typing.Union["VpnSpecProps", typing.Dict[builtins.str, typing.Any]],
        sampleconfig: typing.Optional[typing.Union["SampleConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        tunnel_inside_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_ipam_pool: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool] = None,
    ) -> None:
        '''(experimental) Creates a Site To Site IPSec VPN between the Transit Gateway and Customer Gateway, using a defined set of VPn Properties.

        :param name: A name to identify the vpn.
        :param customer_gateway: (experimental) The customer gateway where the vpn will terminate.
        :param vpnspec: (experimental) a VPN specification for the VPN.
        :param sampleconfig: (experimental) Optionally provide a sampleconfig specification.
        :param tunnel_inside_cidr: (experimental) Specify a pair of concrete Cidr's for the tunnel. Only use one of tunnelInsideCidr or tunnelIpmamPool
        :param tunnel_ipam_pool: (experimental) Specify an ipam pool to allocated the tunnel address's from. Use only one of tunnelInsideCidr or tunnelIpamPool

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a582a3310b9d9bbcd8a7bd02e249755b178189dcb43fab2184c04d9f52288287)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        vpnprops = VpnProps(
            customer_gateway=customer_gateway,
            vpnspec=vpnspec,
            sampleconfig=sampleconfig,
            tunnel_inside_cidr=tunnel_inside_cidr,
            tunnel_ipam_pool=tunnel_ipam_pool,
        )

        return typing.cast(None, jsii.invoke(self, "adds2sVPN", [name, vpnprops]))

    @jsii.member(jsii_name="createDirectConnectGatewayAssociation")
    def create_direct_connect_gateway_association(
        self,
        dxgateway_id: builtins.str,
    ) -> builtins.str:
        '''
        :param dxgateway_id: Id of a DX gateway that.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e39e0dbcc76625bee417f01cedc235a6a125d94888fb2d473ea145ed6e23cc71)
            check_type(argname="argument dxgateway_id", value=dxgateway_id, expected_type=type_hints["dxgateway_id"])
        return typing.cast(builtins.str, jsii.invoke(self, "createDirectConnectGatewayAssociation", [dxgateway_id]))

    @builtins.property
    @jsii.member(jsii_name="cloudwanTgAttachmentId")
    def cloudwan_tg_attachment_id(self) -> builtins.str:
        '''(experimental) the AttachmentId between the Transit Gateway and the cloudwan.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "cloudwanTgAttachmentId"))

    @builtins.property
    @jsii.member(jsii_name="transitGateway")
    def transit_gateway(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway:
        '''(experimental) The created Transit Gateway.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway, jsii.get(self, "transitGateway"))

    @builtins.property
    @jsii.member(jsii_name="tgcidr")
    def tgcidr(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The Cidr Ranges assigned to the transit Gateway.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tgcidr"))

    @builtins.property
    @jsii.member(jsii_name="tgDXattachmentId")
    def tg_d_xattachment_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) the AttachmentId between the Transit Gateway and DX ( if any ).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tgDXattachmentId"))

    @tg_d_xattachment_id.setter
    def tg_d_xattachment_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35903c80af58b933a9eb6be3b8f3d0a16c92d48809d6788f9db10d1999916d3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tgDXattachmentId", value)


@jsii.enum(jsii_type="raindancers-network.ConditionLogic")
class ConditionLogic(enum.Enum):
    '''(experimental) Conditon Logic.

    :stability: experimental
    '''

    AND = "AND"
    '''
    :stability: experimental
    '''
    OR = "OR"
    '''
    :stability: experimental
    '''


class ConditionalForwarder(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.ConditionalForwarder",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        forwarding_rules: typing.Sequence[typing.Union["OutboundForwardingRule", typing.Dict[builtins.str, typing.Any]]],
        inbound_resolver_targets: typing.Sequence[typing.Union[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty, typing.Dict[builtins.str, typing.Any]]],
        outbound_resolver: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param forwarding_rules: 
        :param inbound_resolver_targets: 
        :param outbound_resolver: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab56d42d34969c2bd9f2d0c0dfd933a8f1ced07a1155adc2777f3acca95c52ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ConditionalForwarderProps(
            forwarding_rules=forwarding_rules,
            inbound_resolver_targets=inbound_resolver_targets,
            outbound_resolver=outbound_resolver,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.ConditionalForwarderProps",
    jsii_struct_bases=[],
    name_mapping={
        "forwarding_rules": "forwardingRules",
        "inbound_resolver_targets": "inboundResolverTargets",
        "outbound_resolver": "outboundResolver",
        "vpc": "vpc",
    },
)
class ConditionalForwarderProps:
    def __init__(
        self,
        *,
        forwarding_rules: typing.Sequence[typing.Union["OutboundForwardingRule", typing.Dict[builtins.str, typing.Any]]],
        inbound_resolver_targets: typing.Sequence[typing.Union[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty, typing.Dict[builtins.str, typing.Any]]],
        outbound_resolver: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param forwarding_rules: 
        :param inbound_resolver_targets: 
        :param outbound_resolver: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb9f43082cc19789437ca0b32ac0dee01dabe6b5e810370a064ac78784f0bab5)
            check_type(argname="argument forwarding_rules", value=forwarding_rules, expected_type=type_hints["forwarding_rules"])
            check_type(argname="argument inbound_resolver_targets", value=inbound_resolver_targets, expected_type=type_hints["inbound_resolver_targets"])
            check_type(argname="argument outbound_resolver", value=outbound_resolver, expected_type=type_hints["outbound_resolver"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "forwarding_rules": forwarding_rules,
            "inbound_resolver_targets": inbound_resolver_targets,
            "outbound_resolver": outbound_resolver,
            "vpc": vpc,
        }

    @builtins.property
    def forwarding_rules(self) -> typing.List["OutboundForwardingRule"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("forwarding_rules")
        assert result is not None, "Required property 'forwarding_rules' is missing"
        return typing.cast(typing.List["OutboundForwardingRule"], result)

    @builtins.property
    def inbound_resolver_targets(
        self,
    ) -> typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("inbound_resolver_targets")
        assert result is not None, "Required property 'inbound_resolver_targets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty], result)

    @builtins.property
    def outbound_resolver(
        self,
    ) -> _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint:
        '''
        :stability: experimental
        '''
        result = self._values.get("outbound_resolver")
        assert result is not None, "Required property 'outbound_resolver' is missing"
        return typing.cast(_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConditionalForwarderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CoreNetwork(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CoreNetwork",
):
    '''(experimental) Create a CoreNework for a Cloudwan.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asn_ranges: typing.Sequence[builtins.str],
        core_name: builtins.str,
        edge_locations: typing.Sequence[typing.Mapping[typing.Any, typing.Any]],
        global_network: _aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork,
        policy_description: builtins.str,
        inside_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        non_production: typing.Optional[builtins.bool] = None,
        vpn_ecmp_support: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param asn_ranges: (experimental) a list of of asn's that can be used.
        :param core_name: (experimental) core name.
        :param edge_locations: (experimental) list of edgeLocaitons.
        :param global_network: (experimental) Which Global Network.
        :param policy_description: (experimental) a decription for the policy Document.
        :param inside_cidr_blocks: (experimental) List of InsideCidr Blocks.
        :param non_production: (experimental) If this is a non production stack, backups will not be made.
        :param vpn_ecmp_support: (experimental) support VpnECmp.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d69f0d4ac1dd4d32be48193e8657e6e603a0da7f16ae2060f00bceb211d237ea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CoreNetworkProps(
            asn_ranges=asn_ranges,
            core_name=core_name,
            edge_locations=edge_locations,
            global_network=global_network,
            policy_description=policy_description,
            inside_cidr_blocks=inside_cidr_blocks,
            non_production=non_production,
            vpn_ecmp_support=vpn_ecmp_support,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addSegment")
    def add_segment(
        self,
        *,
        name: builtins.str,
        allow_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        edge_locations: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
        isolate_attachments: typing.Optional[builtins.bool] = None,
        require_attachment_acceptance: typing.Optional[builtins.bool] = None,
    ) -> "CoreNetworkSegment":
        '''(experimental) Add a segment to the core network.

        :param name: (experimental) Name of the Segment.
        :param allow_filter: (experimental) A list of denys.
        :param deny_filter: (experimental) a List of denys.
        :param description: (experimental) A description of the of the segement.
        :param edge_locations: (experimental) A list of edge locations where the segement will be avaialble. Not that the locations must also be included in the core network edge ( CNE )
        :param isolate_attachments: (experimental) Set true if attached VPCS are isolated from each other.
        :param require_attachment_acceptance: (experimental) Set true if the attachment needs approval for connection. Currently not supported and requires an automation step

        :stability: experimental
        '''
        props = Segment(
            name=name,
            allow_filter=allow_filter,
            deny_filter=deny_filter,
            description=description,
            edge_locations=edge_locations,
            isolate_attachments=isolate_attachments,
            require_attachment_acceptance=require_attachment_acceptance,
        )

        return typing.cast("CoreNetworkSegment", jsii.invoke(self, "addSegment", [props]))

    @jsii.member(jsii_name="share")
    def share(
        self,
        *,
        allow_external_principals: builtins.bool,
        principals: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Tag]] = None,
    ) -> None:
        '''(experimental) Create a CoreNetwork Sharing.

        :param allow_external_principals: 
        :param principals: 
        :param tags: 

        :stability: experimental
        '''
        props = CoreNetworkShare(
            allow_external_principals=allow_external_principals,
            principals=principals,
            tags=tags,
        )

        return typing.cast(None, jsii.invoke(self, "share", [props]))

    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> None:
        '''(experimental) Update the corewan policy after actions, segments are added.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "updatePolicy", []))

    @builtins.property
    @jsii.member(jsii_name="cfnCoreNetwork")
    def cfn_core_network(self) -> _aws_cdk_aws_networkmanager_ceddda9d.CfnCoreNetwork:
        '''(experimental) The corenetwork object.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_networkmanager_ceddda9d.CfnCoreNetwork, jsii.get(self, "cfnCoreNetwork"))

    @builtins.property
    @jsii.member(jsii_name="coreName")
    def core_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "coreName"))

    @builtins.property
    @jsii.member(jsii_name="policyTable")
    def policy_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        '''(experimental) THe dynamo table holding the policy.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "policyTable"))

    @builtins.property
    @jsii.member(jsii_name="policyTableName")
    def policy_table_name(self) -> builtins.str:
        '''(experimental) Name of the Dynamo Table holding the policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTableName"))

    @builtins.property
    @jsii.member(jsii_name="policyTableServiceToken")
    def policy_table_service_token(self) -> builtins.str:
        '''(experimental) The policyTable Lamba's Service Token.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTableServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="updateProviderToken")
    def update_provider_token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "updateProviderToken"))

    @update_provider_token.setter
    def update_provider_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e154261c8d8ada3b98f2138184a44fefc2492e5d175f2b644c9dcbff0a5cbff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateProviderToken", value)


@jsii.data_type(
    jsii_type="raindancers-network.CoreNetworkProps",
    jsii_struct_bases=[],
    name_mapping={
        "asn_ranges": "asnRanges",
        "core_name": "coreName",
        "edge_locations": "edgeLocations",
        "global_network": "globalNetwork",
        "policy_description": "policyDescription",
        "inside_cidr_blocks": "insideCidrBlocks",
        "non_production": "nonProduction",
        "vpn_ecmp_support": "vpnEcmpSupport",
    },
)
class CoreNetworkProps:
    def __init__(
        self,
        *,
        asn_ranges: typing.Sequence[builtins.str],
        core_name: builtins.str,
        edge_locations: typing.Sequence[typing.Mapping[typing.Any, typing.Any]],
        global_network: _aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork,
        policy_description: builtins.str,
        inside_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        non_production: typing.Optional[builtins.bool] = None,
        vpn_ecmp_support: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) CoreNetwork Properties.

        :param asn_ranges: (experimental) a list of of asn's that can be used.
        :param core_name: (experimental) core name.
        :param edge_locations: (experimental) list of edgeLocaitons.
        :param global_network: (experimental) Which Global Network.
        :param policy_description: (experimental) a decription for the policy Document.
        :param inside_cidr_blocks: (experimental) List of InsideCidr Blocks.
        :param non_production: (experimental) If this is a non production stack, backups will not be made.
        :param vpn_ecmp_support: (experimental) support VpnECmp.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d8d9d78df11641cadacc6be41ae118118eda35deb292c8b7ba3d97901aa39ed)
            check_type(argname="argument asn_ranges", value=asn_ranges, expected_type=type_hints["asn_ranges"])
            check_type(argname="argument core_name", value=core_name, expected_type=type_hints["core_name"])
            check_type(argname="argument edge_locations", value=edge_locations, expected_type=type_hints["edge_locations"])
            check_type(argname="argument global_network", value=global_network, expected_type=type_hints["global_network"])
            check_type(argname="argument policy_description", value=policy_description, expected_type=type_hints["policy_description"])
            check_type(argname="argument inside_cidr_blocks", value=inside_cidr_blocks, expected_type=type_hints["inside_cidr_blocks"])
            check_type(argname="argument non_production", value=non_production, expected_type=type_hints["non_production"])
            check_type(argname="argument vpn_ecmp_support", value=vpn_ecmp_support, expected_type=type_hints["vpn_ecmp_support"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asn_ranges": asn_ranges,
            "core_name": core_name,
            "edge_locations": edge_locations,
            "global_network": global_network,
            "policy_description": policy_description,
        }
        if inside_cidr_blocks is not None:
            self._values["inside_cidr_blocks"] = inside_cidr_blocks
        if non_production is not None:
            self._values["non_production"] = non_production
        if vpn_ecmp_support is not None:
            self._values["vpn_ecmp_support"] = vpn_ecmp_support

    @builtins.property
    def asn_ranges(self) -> typing.List[builtins.str]:
        '''(experimental) a list of of asn's that can be used.

        :stability: experimental
        '''
        result = self._values.get("asn_ranges")
        assert result is not None, "Required property 'asn_ranges' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def core_name(self) -> builtins.str:
        '''(experimental) core name.

        :stability: experimental
        '''
        result = self._values.get("core_name")
        assert result is not None, "Required property 'core_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def edge_locations(self) -> typing.List[typing.Mapping[typing.Any, typing.Any]]:
        '''(experimental) list of edgeLocaitons.

        :stability: experimental
        '''
        result = self._values.get("edge_locations")
        assert result is not None, "Required property 'edge_locations' is missing"
        return typing.cast(typing.List[typing.Mapping[typing.Any, typing.Any]], result)

    @builtins.property
    def global_network(self) -> _aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork:
        '''(experimental) Which Global Network.

        :stability: experimental
        '''
        result = self._values.get("global_network")
        assert result is not None, "Required property 'global_network' is missing"
        return typing.cast(_aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork, result)

    @builtins.property
    def policy_description(self) -> builtins.str:
        '''(experimental) a decription for the policy Document.

        :stability: experimental
        '''
        result = self._values.get("policy_description")
        assert result is not None, "Required property 'policy_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inside_cidr_blocks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of InsideCidr Blocks.

        :stability: experimental
        '''
        result = self._values.get("inside_cidr_blocks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def non_production(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If this is a non production stack, backups will not be made.

        :stability: experimental
        '''
        result = self._values.get("non_production")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpn_ecmp_support(self) -> typing.Optional[builtins.bool]:
        '''(experimental) support VpnECmp.

        :stability: experimental
        '''
        result = self._values.get("vpn_ecmp_support")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CoreNetworkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CoreNetworkSegment(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CoreNetworkSegment",
):
    '''(experimental) Create a Network Segment in a core network.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "ICoreNetworkSegmentProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aad58423dfd9c9282af79c2ce35fe1789b6efc72243a5fc6c2e901753748c92)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAttachmentPolicy")
    def add_attachment_policy(
        self,
        *,
        action: typing.Union[AttachmentPolicyAction, typing.Dict[builtins.str, typing.Any]],
        conditions: typing.Sequence[typing.Union[AttachmentConditions, typing.Dict[builtins.str, typing.Any]]],
        rule_number: jsii.Number,
        condition_logic: typing.Optional[ConditionLogic] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add an AttachmentPolicy to a segment.

        :param action: 
        :param conditions: 
        :param rule_number: 
        :param condition_logic: 
        :param description: 

        :stability: experimental
        '''
        props = AttachmentPolicy(
            action=action,
            conditions=conditions,
            rule_number=rule_number,
            condition_logic=condition_logic,
            description=description,
        )

        return typing.cast(None, jsii.invoke(self, "addAttachmentPolicy", [props]))

    @jsii.member(jsii_name="addSegmentAction")
    def add_segment_action(
        self,
        *,
        action: "SegmentActionType",
        description: builtins.str,
        destination_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        destinations: typing.Optional[typing.Sequence[builtins.str]] = None,
        except_: typing.Optional[typing.Sequence[builtins.str]] = None,
        mode: typing.Optional["SegmentActionMode"] = None,
        share_with: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
    ) -> None:
        '''(experimental) Add an Action to the Segment, ( Share or Route ).

        :param action: 
        :param description: 
        :param destination_cidr_blocks: 
        :param destinations: 
        :param except_: 
        :param mode: 
        :param share_with: 

        :stability: experimental
        '''
        props = SegmentAction(
            action=action,
            description=description,
            destination_cidr_blocks=destination_cidr_blocks,
            destinations=destinations,
            except_=except_,
            mode=mode,
            share_with=share_with,
        )

        return typing.cast(None, jsii.invoke(self, "addSegmentAction", [props]))

    @jsii.member(jsii_name="addSimpleAttachmentPolicy")
    def add_simple_attachment_policy(
        self,
        *,
        rule_number: jsii.Number,
        account: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rule_number: 
        :param account: 

        :stability: experimental
        '''
        props = SimpleAttachmentPolicyProps(rule_number=rule_number, account=account)

        return typing.cast(None, jsii.invoke(self, "addSimpleAttachmentPolicy", [props]))

    @jsii.member(jsii_name="addSimpleShareAction")
    def add_simple_share_action(
        self,
        *,
        description: builtins.str,
        share_with: typing.Union[builtins.str, typing.Sequence["CoreNetworkSegment"]],
    ) -> None:
        '''
        :param description: 
        :param share_with: 

        :stability: experimental
        '''
        props = SimpleShareActionProps(description=description, share_with=share_with)

        return typing.cast(None, jsii.invoke(self, "addSimpleShareAction", [props]))

    @builtins.property
    @jsii.member(jsii_name="policyTableServiceToken")
    def policy_table_service_token(self) -> builtins.str:
        '''(experimental) Service token for.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTableServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="segmentName")
    def segment_name(self) -> builtins.str:
        '''(experimental) the name for the segment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "segmentName"))


@jsii.data_type(
    jsii_type="raindancers-network.CoreNetworkShare",
    jsii_struct_bases=[],
    name_mapping={
        "allow_external_principals": "allowExternalPrincipals",
        "principals": "principals",
        "tags": "tags",
    },
)
class CoreNetworkShare:
    def __init__(
        self,
        *,
        allow_external_principals: builtins.bool,
        principals: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Tag]] = None,
    ) -> None:
        '''(experimental) CoreNetworkShare.

        :param allow_external_principals: 
        :param principals: 
        :param tags: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51cfde600436c072d891cab49866b9f2ee7f2642180d23d5e2c852838f036b0e)
            check_type(argname="argument allow_external_principals", value=allow_external_principals, expected_type=type_hints["allow_external_principals"])
            check_type(argname="argument principals", value=principals, expected_type=type_hints["principals"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allow_external_principals": allow_external_principals,
            "principals": principals,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def allow_external_principals(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        result = self._values.get("allow_external_principals")
        assert result is not None, "Required property 'allow_external_principals' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def principals(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("principals")
        assert result is not None, "Required property 'principals' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.Tag]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.Tag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CoreNetworkShare(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.CrossAccountProps",
    jsii_struct_bases=[],
    name_mapping={"account_id": "accountId", "role_name": "roleName"},
)
class CrossAccountProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: 
        :param role_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15d475e1dfe6143decefea037f09f52430679483d15c8667d92f99470a428279)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
        }
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def account_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrossRegionParameterReader(
    _aws_cdk_custom_resources_ceddda9d.AwsCustomResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrossRegionParameterReader",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        name: builtins.str,
        *,
        parameter_name: builtins.str,
        region: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param parameter_name: 
        :param region: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de865a5997bc56fe43d8ce21d028b11240580380c9b95cec1f20db1fb5d0fc36)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        props = CrossRegionParameterReaderProps(
            parameter_name=parameter_name, region=region
        )

        jsii.create(self.__class__, self, [scope, name, props])

    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "parameterValue", []))


@jsii.data_type(
    jsii_type="raindancers-network.CrossRegionParameterReaderProps",
    jsii_struct_bases=[],
    name_mapping={"parameter_name": "parameterName", "region": "region"},
)
class CrossRegionParameterReaderProps:
    def __init__(self, *, parameter_name: builtins.str, region: builtins.str) -> None:
        '''
        :param parameter_name: 
        :param region: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b35276fef9aaadf334d01c1bda2534679412d73d2ef32e2a051fe134bda71b3)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "parameter_name": parameter_name,
            "region": region,
        }

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossRegionParameterReaderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrossRegionParameterWriter(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrossRegionParameterWriter",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: builtins.str,
        parameter_name: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: 
        :param parameter_name: 
        :param value: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec477d468b63ff52e7327d9699d8f84bbb43365503e15a5175ee369d1d9c5e5a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrossRegionParameterWriterProps(
            description=description, parameter_name=parameter_name, value=value
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.CrossRegionParameterWriterProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "parameter_name": "parameterName",
        "value": "value",
    },
)
class CrossRegionParameterWriterProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        parameter_name: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param description: 
        :param parameter_name: 
        :param value: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc56bfcf424dfe9d100d1563d89f74d4a3839f6febe702c27e8170a1c9beeee)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "parameter_name": parameter_name,
            "value": value,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossRegionParameterWriterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.CrowdStrikeCloud")
class CrowdStrikeCloud(enum.Enum):
    '''
    :stability: experimental
    '''

    US1 = "US1"
    '''
    :stability: experimental
    '''
    US2 = "US2"
    '''
    :stability: experimental
    '''
    EU1 = "EU1"
    '''
    :stability: experimental
    '''


class CrowdStrikeExtendedEndpoint(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrowdStrikeExtendedEndpoint",
):
    '''(experimental) This will.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        crowdstrike_cloud: CrowdStrikeCloud,
        peering_vpc: typing.Optional[typing.Union["VpcRegionId", typing.Dict[builtins.str, typing.Any]]] = None,
        use_elb_in_peered_vpc: typing.Optional[builtins.bool] = None,
        vpccidr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param crowdstrike_cloud: (experimental) aws The EC2 Instance that will be udpated.
        :param peering_vpc: 
        :param use_elb_in_peered_vpc: 
        :param vpccidr: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffebcb42a0726f006998f99544c3ede9b4099ae03b234ab0394f33c3137b7c5f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrowdStrikeExtendedEndpointProps(
            crowdstrike_cloud=crowdstrike_cloud,
            peering_vpc=peering_vpc,
            use_elb_in_peered_vpc=use_elb_in_peered_vpc,
            vpccidr=vpccidr,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "download"))

    @builtins.property
    @jsii.member(jsii_name="downloadZone")
    def download_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "downloadZone"))

    @builtins.property
    @jsii.member(jsii_name="downloadZoneName")
    def download_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "downloadZoneName"))

    @builtins.property
    @jsii.member(jsii_name="proxy")
    def proxy(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxy"))

    @builtins.property
    @jsii.member(jsii_name="proxyZone")
    def proxy_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxyZone"))

    @builtins.property
    @jsii.member(jsii_name="proxyZoneName")
    def proxy_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxyZoneName"))


@jsii.data_type(
    jsii_type="raindancers-network.CrowdStrikeExtendedEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "crowdstrike_cloud": "crowdstrikeCloud",
        "peering_vpc": "peeringVpc",
        "use_elb_in_peered_vpc": "useELBInPeeredVpc",
        "vpccidr": "vpccidr",
    },
)
class CrowdStrikeExtendedEndpointProps:
    def __init__(
        self,
        *,
        crowdstrike_cloud: CrowdStrikeCloud,
        peering_vpc: typing.Optional[typing.Union["VpcRegionId", typing.Dict[builtins.str, typing.Any]]] = None,
        use_elb_in_peered_vpc: typing.Optional[builtins.bool] = None,
        vpccidr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param crowdstrike_cloud: (experimental) aws The EC2 Instance that will be udpated.
        :param peering_vpc: 
        :param use_elb_in_peered_vpc: 
        :param vpccidr: 

        :stability: experimental
        '''
        if isinstance(peering_vpc, dict):
            peering_vpc = VpcRegionId(**peering_vpc)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4bc1edb40dd5c6bb20b33a2c5745db6e1638fec1fc54372ced20d15e9ce1b3f)
            check_type(argname="argument crowdstrike_cloud", value=crowdstrike_cloud, expected_type=type_hints["crowdstrike_cloud"])
            check_type(argname="argument peering_vpc", value=peering_vpc, expected_type=type_hints["peering_vpc"])
            check_type(argname="argument use_elb_in_peered_vpc", value=use_elb_in_peered_vpc, expected_type=type_hints["use_elb_in_peered_vpc"])
            check_type(argname="argument vpccidr", value=vpccidr, expected_type=type_hints["vpccidr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "crowdstrike_cloud": crowdstrike_cloud,
        }
        if peering_vpc is not None:
            self._values["peering_vpc"] = peering_vpc
        if use_elb_in_peered_vpc is not None:
            self._values["use_elb_in_peered_vpc"] = use_elb_in_peered_vpc
        if vpccidr is not None:
            self._values["vpccidr"] = vpccidr

    @builtins.property
    def crowdstrike_cloud(self) -> CrowdStrikeCloud:
        '''(experimental) aws The EC2 Instance that will be udpated.

        :stability: experimental
        '''
        result = self._values.get("crowdstrike_cloud")
        assert result is not None, "Required property 'crowdstrike_cloud' is missing"
        return typing.cast(CrowdStrikeCloud, result)

    @builtins.property
    def peering_vpc(self) -> typing.Optional["VpcRegionId"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("peering_vpc")
        return typing.cast(typing.Optional["VpcRegionId"], result)

    @builtins.property
    def use_elb_in_peered_vpc(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("use_elb_in_peered_vpc")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpccidr(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpccidr")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikeExtendedEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrowdStrikeNLB(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrowdStrikeNLB",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        crowdstrike_region: CrowdStrikeCloud,
        download: builtins.str,
        downloadhosted_zone: builtins.str,
        downloadhosted_zone_name: builtins.str,
        proxy: builtins.str,
        proxyhosted_zone: builtins.str,
        proxyhosted_zone_name: builtins.str,
        region: builtins.str,
        routeresolver_endpoints: "R53Resolverendpoints",
        subnet_group_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param crowdstrike_region: 
        :param download: 
        :param downloadhosted_zone: 
        :param downloadhosted_zone_name: 
        :param proxy: 
        :param proxyhosted_zone: 
        :param proxyhosted_zone_name: 
        :param region: 
        :param routeresolver_endpoints: 
        :param subnet_group_name: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa94e43c8721e381721a04fc4958c7ff8eb7d938b3d41752557e9133dde32243)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrowdStrikeNLBProps(
            crowdstrike_region=crowdstrike_region,
            download=download,
            downloadhosted_zone=downloadhosted_zone,
            downloadhosted_zone_name=downloadhosted_zone_name,
            proxy=proxy,
            proxyhosted_zone=proxyhosted_zone,
            proxyhosted_zone_name=proxyhosted_zone_name,
            region=region,
            routeresolver_endpoints=routeresolver_endpoints,
            subnet_group_name=subnet_group_name,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.CrowdStrikeNLBProps",
    jsii_struct_bases=[],
    name_mapping={
        "crowdstrike_region": "crowdstrikeRegion",
        "download": "download",
        "downloadhosted_zone": "downloadhostedZone",
        "downloadhosted_zone_name": "downloadhostedZoneName",
        "proxy": "proxy",
        "proxyhosted_zone": "proxyhostedZone",
        "proxyhosted_zone_name": "proxyhostedZoneName",
        "region": "region",
        "routeresolver_endpoints": "routeresolverEndpoints",
        "subnet_group_name": "subnetGroupName",
        "vpc": "vpc",
    },
)
class CrowdStrikeNLBProps:
    def __init__(
        self,
        *,
        crowdstrike_region: CrowdStrikeCloud,
        download: builtins.str,
        downloadhosted_zone: builtins.str,
        downloadhosted_zone_name: builtins.str,
        proxy: builtins.str,
        proxyhosted_zone: builtins.str,
        proxyhosted_zone_name: builtins.str,
        region: builtins.str,
        routeresolver_endpoints: "R53Resolverendpoints",
        subnet_group_name: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param crowdstrike_region: 
        :param download: 
        :param downloadhosted_zone: 
        :param downloadhosted_zone_name: 
        :param proxy: 
        :param proxyhosted_zone: 
        :param proxyhosted_zone_name: 
        :param region: 
        :param routeresolver_endpoints: 
        :param subnet_group_name: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31bf94f415dccb4fff277aab10a278965f63a87bb3b9378ee0debcf0201d9c07)
            check_type(argname="argument crowdstrike_region", value=crowdstrike_region, expected_type=type_hints["crowdstrike_region"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument downloadhosted_zone", value=downloadhosted_zone, expected_type=type_hints["downloadhosted_zone"])
            check_type(argname="argument downloadhosted_zone_name", value=downloadhosted_zone_name, expected_type=type_hints["downloadhosted_zone_name"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument proxyhosted_zone", value=proxyhosted_zone, expected_type=type_hints["proxyhosted_zone"])
            check_type(argname="argument proxyhosted_zone_name", value=proxyhosted_zone_name, expected_type=type_hints["proxyhosted_zone_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument routeresolver_endpoints", value=routeresolver_endpoints, expected_type=type_hints["routeresolver_endpoints"])
            check_type(argname="argument subnet_group_name", value=subnet_group_name, expected_type=type_hints["subnet_group_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "crowdstrike_region": crowdstrike_region,
            "download": download,
            "downloadhosted_zone": downloadhosted_zone,
            "downloadhosted_zone_name": downloadhosted_zone_name,
            "proxy": proxy,
            "proxyhosted_zone": proxyhosted_zone,
            "proxyhosted_zone_name": proxyhosted_zone_name,
            "region": region,
            "routeresolver_endpoints": routeresolver_endpoints,
            "subnet_group_name": subnet_group_name,
            "vpc": vpc,
        }

    @builtins.property
    def crowdstrike_region(self) -> CrowdStrikeCloud:
        '''
        :stability: experimental
        '''
        result = self._values.get("crowdstrike_region")
        assert result is not None, "Required property 'crowdstrike_region' is missing"
        return typing.cast(CrowdStrikeCloud, result)

    @builtins.property
    def download(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("download")
        assert result is not None, "Required property 'download' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def downloadhosted_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("downloadhosted_zone")
        assert result is not None, "Required property 'downloadhosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def downloadhosted_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("downloadhosted_zone_name")
        assert result is not None, "Required property 'downloadhosted_zone_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proxy(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("proxy")
        assert result is not None, "Required property 'proxy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proxyhosted_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("proxyhosted_zone")
        assert result is not None, "Required property 'proxyhosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proxyhosted_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("proxyhosted_zone_name")
        assert result is not None, "Required property 'proxyhosted_zone_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def routeresolver_endpoints(self) -> "R53Resolverendpoints":
        '''
        :stability: experimental
        '''
        result = self._values.get("routeresolver_endpoints")
        assert result is not None, "Required property 'routeresolver_endpoints' is missing"
        return typing.cast("R53Resolverendpoints", result)

    @builtins.property
    def subnet_group_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_group_name")
        assert result is not None, "Required property 'subnet_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikeNLBProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrowdStrikePrivateLink(
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrowdStrikePrivateLink",
):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="EU1")
    def EU1(cls) -> "CrowdStrikePrivateLink":
        '''
        :stability: experimental
        '''
        return typing.cast("CrowdStrikePrivateLink", jsii.sget(cls, "EU1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="US1")
    def US1(cls) -> "CrowdStrikePrivateLink":
        '''
        :stability: experimental
        '''
        return typing.cast("CrowdStrikePrivateLink", jsii.sget(cls, "US1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="US2")
    def US2(cls) -> "CrowdStrikePrivateLink":
        '''
        :stability: experimental
        '''
        return typing.cast("CrowdStrikePrivateLink", jsii.sget(cls, "US2"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> "CrowdStrikeServices":
        '''
        :stability: experimental
        '''
        return typing.cast("CrowdStrikeServices", jsii.get(self, "value"))


class CrowdStrikePrivateLinkEndpoint(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.CrowdStrikePrivateLinkEndpoint",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        crowd_strike_cloud: CrowdStrikeCloud,
        subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        peeredwith_nlb: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param crowd_strike_cloud: 
        :param subnets: 
        :param vpc: (experimental) The EC2 Instance that will be udpated.
        :param peeredwith_nlb: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef063a79cf88ea36bb3eae03b4dcf95e11322ae142c55a90853abe504833fa1f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrowdStrikePrivateLinkEndpointProps(
            crowd_strike_cloud=crowd_strike_cloud,
            subnets=subnets,
            vpc=vpc,
            peeredwith_nlb=peeredwith_nlb,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "download"))

    @download.setter
    def download(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__101a5de77d7995d965c3dd27954a1bc313383831fa78f60d7477a160b1455dbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value)

    @builtins.property
    @jsii.member(jsii_name="downloadhostedZone")
    def downloadhosted_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "downloadhostedZone"))

    @downloadhosted_zone.setter
    def downloadhosted_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__762d57b647a8727640ef0a995696d6dbefa635f2d763282d959e1b53d29770ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "downloadhostedZone", value)

    @builtins.property
    @jsii.member(jsii_name="downloadhostedZoneName")
    def downloadhosted_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "downloadhostedZoneName"))

    @downloadhosted_zone_name.setter
    def downloadhosted_zone_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c30e6e377907e1959384d313cc5be24ea9842b7740c5130caf72c94186d10d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "downloadhostedZoneName", value)

    @builtins.property
    @jsii.member(jsii_name="proxy")
    def proxy(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxy"))

    @proxy.setter
    def proxy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eb5937738f1214afd9753148e64c8a28555093cf0307af743c04f39ddd773ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxy", value)

    @builtins.property
    @jsii.member(jsii_name="proxyhostedZone")
    def proxyhosted_zone(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxyhostedZone"))

    @proxyhosted_zone.setter
    def proxyhosted_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3477df0425028aaee09618274f1d539f801795c4c38b6f17bde652101919a23e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyhostedZone", value)

    @builtins.property
    @jsii.member(jsii_name="proxyhostedZoneName")
    def proxyhosted_zone_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "proxyhostedZoneName"))

    @proxyhosted_zone_name.setter
    def proxyhosted_zone_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3fff76ea406ed95e68b875bf14c36653d990524981d3a8667fa254b5aac8756)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyhostedZoneName", value)


@jsii.data_type(
    jsii_type="raindancers-network.CrowdStrikePrivateLinkEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "crowd_strike_cloud": "crowdStrikeCloud",
        "subnets": "subnets",
        "vpc": "vpc",
        "peeredwith_nlb": "peeredwithNLB",
    },
)
class CrowdStrikePrivateLinkEndpointProps:
    def __init__(
        self,
        *,
        crowd_strike_cloud: CrowdStrikeCloud,
        subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        peeredwith_nlb: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param crowd_strike_cloud: 
        :param subnets: 
        :param vpc: (experimental) The EC2 Instance that will be udpated.
        :param peeredwith_nlb: 

        :stability: experimental
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acb41629822375b876405c2e97949aeae0b5e4cd893b29dd65ab99428118420b)
            check_type(argname="argument crowd_strike_cloud", value=crowd_strike_cloud, expected_type=type_hints["crowd_strike_cloud"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument peeredwith_nlb", value=peeredwith_nlb, expected_type=type_hints["peeredwith_nlb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "crowd_strike_cloud": crowd_strike_cloud,
            "subnets": subnets,
            "vpc": vpc,
        }
        if peeredwith_nlb is not None:
            self._values["peeredwith_nlb"] = peeredwith_nlb

    @builtins.property
    def crowd_strike_cloud(self) -> CrowdStrikeCloud:
        '''
        :stability: experimental
        '''
        result = self._values.get("crowd_strike_cloud")
        assert result is not None, "Required property 'crowd_strike_cloud' is missing"
        return typing.cast(CrowdStrikeCloud, result)

    @builtins.property
    def subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) The EC2 Instance that will be udpated.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def peeredwith_nlb(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("peeredwith_nlb")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikePrivateLinkEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.CrowdStrikeRegion")
class CrowdStrikeRegion(enum.Enum):
    '''
    :stability: experimental
    '''

    US_WEST_1 = "US_WEST_1"
    '''
    :stability: experimental
    '''
    US_WEST_2 = "US_WEST_2"
    '''
    :stability: experimental
    '''
    EU_CENTRAL_1 = "EU_CENTRAL_1"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.CrowdStrikeServices",
    jsii_struct_bases=[],
    name_mapping={
        "aws_region": "awsRegion",
        "download_server": "downloadServer",
        "sensor_proxy": "sensorProxy",
    },
)
class CrowdStrikeServices:
    def __init__(
        self,
        *,
        aws_region: CrowdStrikeRegion,
        download_server: typing.Union["Endpoint", typing.Dict[builtins.str, typing.Any]],
        sensor_proxy: typing.Union["Endpoint", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param aws_region: 
        :param download_server: 
        :param sensor_proxy: 

        :stability: experimental
        '''
        if isinstance(download_server, dict):
            download_server = Endpoint(**download_server)
        if isinstance(sensor_proxy, dict):
            sensor_proxy = Endpoint(**sensor_proxy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e09c7128ef3c527e4e481fc7777416d58ff6626f2d6af1b1863ecac308cac38)
            check_type(argname="argument aws_region", value=aws_region, expected_type=type_hints["aws_region"])
            check_type(argname="argument download_server", value=download_server, expected_type=type_hints["download_server"])
            check_type(argname="argument sensor_proxy", value=sensor_proxy, expected_type=type_hints["sensor_proxy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aws_region": aws_region,
            "download_server": download_server,
            "sensor_proxy": sensor_proxy,
        }

    @builtins.property
    def aws_region(self) -> CrowdStrikeRegion:
        '''
        :stability: experimental
        '''
        result = self._values.get("aws_region")
        assert result is not None, "Required property 'aws_region' is missing"
        return typing.cast(CrowdStrikeRegion, result)

    @builtins.property
    def download_server(self) -> "Endpoint":
        '''
        :stability: experimental
        '''
        result = self._values.get("download_server")
        assert result is not None, "Required property 'download_server' is missing"
        return typing.cast("Endpoint", result)

    @builtins.property
    def sensor_proxy(self) -> "Endpoint":
        '''
        :stability: experimental
        '''
        result = self._values.get("sensor_proxy")
        assert result is not None, "Required property 'sensor_proxy' is missing"
        return typing.cast("Endpoint", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrowdStrikeServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.CustomerManagedPolicyReference",
    jsii_struct_bases=[
        _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty
    ],
    name_mapping={"name": "name", "path": "path"},
)
class CustomerManagedPolicyReference(
    _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty,
):
    def __init__(
        self,
        *,
        name: builtins.str,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the IAM policy that you have configured in each account where you want to deploy your permission set.
        :param path: The path to the IAM policy that you have configured in each account where you want to deploy your permission set. The default is ``/`` . For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* .

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2dea084fa06e88b853d7f1933973fc231cbd4910f6bf4c20e1e9f6a7fc677cf)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the IAM policy that you have configured in each account where you want to deploy your permission set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sso-permissionset-customermanagedpolicyreference.html#cfn-sso-permissionset-customermanagedpolicyreference-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path to the IAM policy that you have configured in each account where you want to deploy your permission set.

        The default is ``/`` . For more information, see `Friendly names and paths <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-friendly-names>`_ in the *IAM User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sso-permissionset-customermanagedpolicyreference.html#cfn-sso-permissionset-customermanagedpolicyreference-path
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomerManagedPolicyReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.DNSFirewallActions")
class DNSFirewallActions(enum.Enum):
    '''
    :stability: experimental
    '''

    ALLOW = "ALLOW"
    '''
    :stability: experimental
    '''
    BLOCK = "BLOCK"
    '''
    :stability: experimental
    '''
    ALERT = "ALERT"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.DNSFirewallBlockResponse")
class DNSFirewallBlockResponse(enum.Enum):
    '''
    :stability: experimental
    '''

    NODATA = "NODATA"
    '''
    :stability: experimental
    '''
    NXDOMAIN = "NXDOMAIN"
    '''
    :stability: experimental
    '''
    OVERRIDE = "OVERRIDE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.DPDTimeoutAction")
class DPDTimeoutAction(enum.Enum):
    '''(experimental) Dead Peer Detection Timeout Actions.

    :stability: experimental
    '''

    CLEAR = "CLEAR"
    '''(experimental) Clear the Session.

    :stability: experimental
    '''
    NONE = "NONE"
    '''(experimental) Do nothing.

    :stability: experimental
    '''
    RESTART = "RESTART"
    '''(experimental) Restart The Session.

    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Destination")
class Destination(enum.Enum):
    '''(experimental) The Destinations for Adding Routes.

    :stability: experimental
    '''

    CLOUDWAN = "CLOUDWAN"
    '''(experimental) route to the cloudwan that the vpc is attached to.

    :stability: experimental
    '''
    TRANSITGATEWAY = "TRANSITGATEWAY"
    '''(experimental) route to the transitGateway that the vpc is attached to.

    :stability: experimental
    '''
    NWFIREWALL = "NWFIREWALL"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Direction")
class Direction(enum.Enum):
    '''
    :stability: experimental
    '''

    OUTBOUND = "OUTBOUND"
    '''(experimental) Traffic allowed from Src to destination only.

    :stability: experimental
    '''
    BOTH = "BOTH"
    '''(experimental) Traffic allowed in both directions.

    :stability: experimental
    '''


class DynamicTagResourceGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.DynamicTagResourceGroup",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 
        :param description: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3610da9d5b891a4e6b0a8366a67b956c293ea9cb1f0f5192031aa4c1f275de7e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DynamicTagResourceGroupProps(name=name, description=description)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTagFilter")
    def add_tag_filter(
        self,
        *,
        key: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: 
        :param values: 

        :stability: experimental
        '''
        props = TagFilter(key=key, values=values)

        return typing.cast(None, jsii.invoke(self, "addTagFilter", [props]))

    @builtins.property
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "groupArn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a6447b9db09c3ca16635723dcd1c3dd8484df4227e85933c8b5c7ed0b86b387)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="raindancers-network.DynamicTagResourceGroupProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description"},
)
class DynamicTagResourceGroupProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param description: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9564509b247284681687a116db4d26261741dec040bb86ed1888d7db69fb4dd)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicTagResourceGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.DynamicTagResourceGroupSet",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "name": "name"},
)
class DynamicTagResourceGroupSet:
    def __init__(self, *, arn: builtins.str, name: builtins.str) -> None:
        '''
        :param arn: 
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14f22444b4e77cb1262a6ec0d54a52802126e90fe5803f035cfd951f34a443a4)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arn": arn,
            "name": name,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicTagResourceGroupSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.ESubnetGroup",
    jsii_struct_bases=[],
    name_mapping={
        "cidr_mask": "cidrMask",
        "name": "name",
        "subnet_type": "subnetType",
    },
)
class ESubnetGroup:
    def __init__(
        self,
        *,
        cidr_mask: jsii.Number,
        name: builtins.str,
        subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
    ) -> None:
        '''
        :param cidr_mask: 
        :param name: 
        :param subnet_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9778d1e2bd39762ff9a481ba772e5cf6ea7fd9a18b2029efbe29a55ab4fbe49)
            check_type(argname="argument cidr_mask", value=cidr_mask, expected_type=type_hints["cidr_mask"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument subnet_type", value=subnet_type, expected_type=type_hints["subnet_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr_mask": cidr_mask,
            "name": name,
            "subnet_type": subnet_type,
        }

    @builtins.property
    def cidr_mask(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr_mask")
        assert result is not None, "Required property 'cidr_mask' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_type(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetType:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_type")
        assert result is not None, "Required property 'subnet_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ESubnetGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.ESubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "cidr_mask": "cidrMask",
        "name": "name",
        "subnet_type": "subnetType",
    },
)
class ESubnetGroupProps:
    def __init__(
        self,
        *,
        cidr_mask: jsii.Number,
        name: builtins.str,
        subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
    ) -> None:
        '''
        :param cidr_mask: 
        :param name: 
        :param subnet_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c52b59ab47a2338bcbeefa82be24348493edae2775e4f23b3235bfa2f01e071)
            check_type(argname="argument cidr_mask", value=cidr_mask, expected_type=type_hints["cidr_mask"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument subnet_type", value=subnet_type, expected_type=type_hints["subnet_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr_mask": cidr_mask,
            "name": name,
            "subnet_type": subnet_type,
        }

    @builtins.property
    def cidr_mask(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr_mask")
        assert result is not None, "Required property 'cidr_mask' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_type(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetType:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_type")
        assert result is not None, "Required property 'subnet_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ESubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.Endpoint",
    jsii_struct_bases=[],
    name_mapping={"dns_name": "dnsName", "vpc_endpoint_name": "vpcEndpointName"},
)
class Endpoint:
    def __init__(
        self,
        *,
        dns_name: builtins.str,
        vpc_endpoint_name: builtins.str,
    ) -> None:
        '''
        :param dns_name: 
        :param vpc_endpoint_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__818e82f2f3642febbe23ff995a92b8a16542fcff3868a7dcd520321ea9e2615e)
            check_type(argname="argument dns_name", value=dns_name, expected_type=type_hints["dns_name"])
            check_type(argname="argument vpc_endpoint_name", value=vpc_endpoint_name, expected_type=type_hints["vpc_endpoint_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dns_name": dns_name,
            "vpc_endpoint_name": vpc_endpoint_name,
        }

    @builtins.property
    def dns_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("dns_name")
        assert result is not None, "Required property 'dns_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_endpoint_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_endpoint_name")
        assert result is not None, "Required property 'vpc_endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Endpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnforceImdsv2(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.EnforceImdsv2",
):
    '''(experimental) Enforces the use of IMDSv2, without causing replacement of the Instance.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instances: typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.Instance]],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instances: (experimental) ec2 Instance or Instances.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__361675112f01ab7162d06b299e2fcc929aca509564dc016bac71d2055c809f52)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EnforceImdsv2Props(instances=instances)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.EnforceImdsv2Props",
    jsii_struct_bases=[],
    name_mapping={"instances": "instances"},
)
class EnforceImdsv2Props:
    def __init__(
        self,
        *,
        instances: typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.Instance]],
    ) -> None:
        '''
        :param instances: (experimental) ec2 Instance or Instances.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f04124053150c2636978544b5a82d349f2146ce45774c3c74a75545559df5e1)
            check_type(argname="argument instances", value=instances, expected_type=type_hints["instances"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instances": instances,
        }

    @builtins.property
    def instances(
        self,
    ) -> typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.List[_aws_cdk_aws_ec2_ceddda9d.Instance]]:
        '''(experimental) ec2 Instance or Instances.

        :stability: experimental
        '''
        result = self._values.get("instances")
        assert result is not None, "Required property 'instances' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.List[_aws_cdk_aws_ec2_ceddda9d.Instance]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnforceImdsv2Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnterpriseVpc(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.EnterpriseVpc",
):
    '''(experimental) Enteprise VPC's take the stock ec2.Vpc and provide numerous convience methods primarly related to connecting to internal networks.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        evpc: typing.Optional[typing.Union["EvpcProps", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param evpc: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdc1ab7ca620afda18c8e46c55dea88e3fd0a922041aced408cd57b8c51012dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EnterpriseVpcProps(evpc=evpc, vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCentralResolverRules")
    def add_central_resolver_rules(
        self,
        domains: typing.Sequence[builtins.str],
        search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
    ) -> None:
        '''
        :param domains: -
        :param search_tag: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d011cebb642eca028febd2f25247291ba13e5813177bfa2e8ce2135ec9db51bc)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument search_tag", value=search_tag, expected_type=type_hints["search_tag"])
        return typing.cast(None, jsii.invoke(self, "addCentralResolverRules", [domains, search_tag]))

    @jsii.member(jsii_name="addConditionalFowardingRules")
    def add_conditional_fowarding_rules(
        self,
        forwarding_rules: typing.Sequence[typing.Union["OutboundForwardingRule", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param forwarding_rules: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34631fdbeb7b93146107b6c0dffe233263a5ba32febb8343cca95be1639dbfd7)
            check_type(argname="argument forwarding_rules", value=forwarding_rules, expected_type=type_hints["forwarding_rules"])
        return typing.cast(None, jsii.invoke(self, "addConditionalFowardingRules", [forwarding_rules]))

    @jsii.member(jsii_name="addCoreRoutes")
    def add_core_routes(
        self,
        *,
        attachment_id: builtins.str,
        core_name: builtins.str,
        description: builtins.str,
        destination_cidr_blocks: typing.Sequence[builtins.str],
        policy_table_arn: builtins.str,
        segments: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param attachment_id: 
        :param core_name: 
        :param description: 
        :param destination_cidr_blocks: 
        :param policy_table_arn: 
        :param segments: 

        :stability: experimental
        '''
        props = AddCoreRoutesProps(
            attachment_id=attachment_id,
            core_name=core_name,
            description=description,
            destination_cidr_blocks=destination_cidr_blocks,
            policy_table_arn=policy_table_arn,
            segments=segments,
        )

        return typing.cast(None, jsii.invoke(self, "addCoreRoutes", [props]))

    @jsii.member(jsii_name="addCrossAccountR53AssociationRole")
    def add_cross_account_r53_association_role(
        self,
        rolename: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rolename: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04de5cec5fe4406cb3d639b8c9bd46012b982148ad5767e8fce8764de2f0dd6e)
            check_type(argname="argument rolename", value=rolename, expected_type=type_hints["rolename"])
        return typing.cast(None, jsii.invoke(self, "addCrossAccountR53AssociationRole", [rolename]))

    @jsii.member(jsii_name="addNetworkFirewall")
    def add_network_firewall(
        self,
        firewall_name: builtins.str,
        firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
        subnet: "SubnetGroup",
    ) -> None:
        '''
        :param firewall_name: -
        :param firewall_policy: -
        :param subnet: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c22df7393382e68ea1bc7dd6e832123e65d420e84bb886668b2891fa6e24fb2)
            check_type(argname="argument firewall_name", value=firewall_name, expected_type=type_hints["firewall_name"])
            check_type(argname="argument firewall_policy", value=firewall_policy, expected_type=type_hints["firewall_policy"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        return typing.cast(None, jsii.invoke(self, "addNetworkFirewall", [firewall_name, firewall_policy, subnet]))

    @jsii.member(jsii_name="addPrivateHostedZone")
    def add_private_hosted_zone(
        self,
        zonename: builtins.str,
    ) -> _aws_cdk_aws_route53_ceddda9d.HostedZone:
        '''
        :param zonename: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026fa0ce348808ebb0b9a13b4ea23512d9c3141bf4689b47faedb69c76605f51)
            check_type(argname="argument zonename", value=zonename, expected_type=type_hints["zonename"])
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.HostedZone, jsii.invoke(self, "addPrivateHostedZone", [zonename]))

    @jsii.member(jsii_name="addR53Resolvers")
    def add_r53_resolvers(self, subnet: "SubnetGroup") -> "R53Resolverendpoints":
        '''
        :param subnet: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9fb5804364c12d2abceab3cf5edd4b0259eaf88a27ca12924c87bc94c757203)
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        return typing.cast("R53Resolverendpoints", jsii.invoke(self, "addR53Resolvers", [subnet]))

    @jsii.member(jsii_name="addR53Zone")
    def add_r53_zone(
        self,
        *,
        zone: builtins.str,
        central_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''
        :param zone: 
        :param central_vpc: 

        :stability: experimental
        '''
        props = AddR53ZoneProps(zone=zone, central_vpc=central_vpc)

        return typing.cast(None, jsii.invoke(self, "addR53Zone", [props]))

    @jsii.member(jsii_name="addRoutes")
    def add_routes(
        self,
        *,
        cidr: typing.Sequence[builtins.str],
        description: builtins.str,
        destination: Destination,
        subnet_groups: typing.Sequence[builtins.str],
        cloudwan_name: typing.Optional[builtins.str] = None,
        network_firewall_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add routes to SubnetGroups ( by implication their routing tables ).

        :param cidr: 
        :param description: 
        :param destination: 
        :param subnet_groups: 
        :param cloudwan_name: 
        :param network_firewall_arn: 

        :stability: experimental
        '''
        props = AddRoutesProps(
            cidr=cidr,
            description=description,
            destination=destination,
            subnet_groups=subnet_groups,
            cloudwan_name=cloudwan_name,
            network_firewall_arn=network_firewall_arn,
        )

        return typing.cast(None, jsii.invoke(self, "addRoutes", [props]))

    @jsii.member(jsii_name="addServiceEndpoints")
    def add_service_endpoints(
        self,
        *,
        services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
        subnet_group: "SubnetGroup",
        dynamo_db_gateway: typing.Optional[builtins.bool] = None,
        s3_gateway_interface: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Add a collection of service endpopints to the VPC.

        :param services: 
        :param subnet_group: 
        :param dynamo_db_gateway: 
        :param s3_gateway_interface: 

        :stability: experimental
        '''
        props = AddAwsServiceEndPointsProps(
            services=services,
            subnet_group=subnet_group,
            dynamo_db_gateway=dynamo_db_gateway,
            s3_gateway_interface=s3_gateway_interface,
        )

        return typing.cast(None, jsii.invoke(self, "addServiceEndpoints", [props]))

    @jsii.member(jsii_name="associateSharedResolverRules")
    def associate_shared_resolver_rules(
        self,
        domain_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param domain_names: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97a4cbf25e8de5c9938ee88e6ca31447095567e59faff8056131f03d703cb380)
            check_type(argname="argument domain_names", value=domain_names, expected_type=type_hints["domain_names"])
        return typing.cast(None, jsii.invoke(self, "associateSharedResolverRules", [domain_names]))

    @jsii.member(jsii_name="attachAWSManagedDNSFirewallRules")
    def attach_aws_managed_dns_firewall_rules(self) -> None:
        '''
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "attachAWSManagedDNSFirewallRules", []))

    @jsii.member(jsii_name="attachToCloudWan")
    def attach_to_cloud_wan(
        self,
        *,
        core_network_name: builtins.str,
        segment_name: builtins.str,
        appliance_mode: typing.Optional[builtins.bool] = None,
        attachment_subnet_group: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''(experimental) attachToCloudWan will attach a VPC to CloudWan, in a particular Segment.

        :param core_network_name: (experimental) corenetworkName.
        :param segment_name: 
        :param appliance_mode: 
        :param attachment_subnet_group: 

        :stability: experimental
        '''
        props = AttachToCloudWanProps(
            core_network_name=core_network_name,
            segment_name=segment_name,
            appliance_mode=appliance_mode,
            attachment_subnet_group=attachment_subnet_group,
        )

        return typing.cast(builtins.str, jsii.invoke(self, "attachToCloudWan", [props]))

    @jsii.member(jsii_name="attachToTransitGateway")
    def attach_to_transit_gateway(
        self,
        *,
        transit_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway,
        applicance_mode: typing.Optional[ApplianceMode] = None,
        attachment_subnet_group: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''(experimental) Attach a vpc to a transit gateway, possibly in appliance mode Its intended purpose is provide a.

        :param transit_gateway: (experimental) the TransitGateway to connect to.
        :param applicance_mode: (experimental) Will this be connected in appliance mode ( used if you have Network Firewalls ).
        :param attachment_subnet_group: 

        :stability: experimental
        '''
        props = AttachToTransitGatewayProps(
            transit_gateway=transit_gateway,
            applicance_mode=applicance_mode,
            attachment_subnet_group=attachment_subnet_group,
        )

        return typing.cast(builtins.str, jsii.invoke(self, "attachToTransitGateway", [props]))

    @jsii.member(jsii_name="cloudWanRoutingProtocol")
    def cloud_wan_routing_protocol(
        self,
        *,
        subnet_groups: typing.Sequence[builtins.str],
        accept_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Enable CloudWanRoutingProtocol.

        :param subnet_groups: 
        :param accept_route_filter: 
        :param deny_route_filter: 

        :stability: experimental
        '''
        props = CloudWanRoutingProtocolProps(
            subnet_groups=subnet_groups,
            accept_route_filter=accept_route_filter,
            deny_route_filter=deny_route_filter,
        )

        return typing.cast(None, jsii.invoke(self, "cloudWanRoutingProtocol", [props]))

    @jsii.member(jsii_name="createAndAttachR53EnterprizeZone")
    def create_and_attach_r53_enterprize_zone(
        self,
        *,
        domainname: builtins.str,
        hub_vpcs: typing.Sequence[typing.Union["HubVpc", typing.Dict[builtins.str, typing.Any]]],
        is_hub_vpc: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone:
        '''
        :param domainname: 
        :param hub_vpcs: 
        :param is_hub_vpc: 

        :stability: experimental
        '''
        props = AddEnterprizeZoneProps(
            domainname=domainname, hub_vpcs=hub_vpcs, is_hub_vpc=is_hub_vpc
        )

        return typing.cast(_aws_cdk_aws_route53_ceddda9d.PrivateHostedZone, jsii.invoke(self, "createAndAttachR53EnterprizeZone", [props]))

    @jsii.member(jsii_name="createAndAttachR53PrivateZone")
    def create_and_attach_r53_private_zone(
        self,
        zone_name: builtins.str,
    ) -> _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone:
        '''
        :param zone_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c1eee126bd092a7ed622b6bc5daf117333f0764d8ddfa3c179eb4aebd36477)
            check_type(argname="argument zone_name", value=zone_name, expected_type=type_hints["zone_name"])
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.PrivateHostedZone, jsii.invoke(self, "createAndAttachR53PrivateZone", [zone_name]))

    @jsii.member(jsii_name="createAndShareSubnetPrefixList")
    def create_and_share_subnet_prefix_list(
        self,
        name: builtins.str,
        subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        org_arn: builtins.str,
    ) -> _aws_cdk_aws_ec2_ceddda9d.CfnPrefixList:
        '''
        :param name: -
        :param subnets: -
        :param org_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a66129ead079a49202db8526d78b98ac50a7eec35ca2146722f07276f325a957)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument org_arn", value=org_arn, expected_type=type_hints["org_arn"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnPrefixList, jsii.invoke(self, "createAndShareSubnetPrefixList", [name, subnets, org_arn]))

    @jsii.member(jsii_name="createFlowLog")
    def create_flow_log(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        local_athena_querys: typing.Optional[builtins.bool] = None,
        one_minute_flow_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Create Enterprise VPC Flow Logs (to central log account) and advanced diagnostics with Athena Querys.

        :param bucket: (experimental) the central s3 location for enterprise flow logs.
        :param local_athena_querys: (experimental) create in Account Athena Querys for flow logs.
        :param one_minute_flow_logs: (experimental) 1 minute resolution.

        :stability: experimental
        '''
        props = FlowLogProps(
            bucket=bucket,
            local_athena_querys=local_athena_querys,
            one_minute_flow_logs=one_minute_flow_logs,
        )

        return typing.cast(None, jsii.invoke(self, "createFlowLog", [props]))

    @jsii.member(jsii_name="router")
    def router(
        self,
        router_groups: typing.Sequence[typing.Union["RouterGroup", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''(experimental) This is a convience method to present the routing for the Vpc in a simpler format, than the addRoutes Method, which it calls.

        :param router_groups: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcaa6f55ea2178f5d30e58a2b4cf75cdb6c8e9597e3e5a6774752de6502b2db9)
            check_type(argname="argument router_groups", value=router_groups, expected_type=type_hints["router_groups"])
        return typing.cast(None, jsii.invoke(self, "router", [router_groups]))

    @jsii.member(jsii_name="shareSubnetGroup")
    def share_subnet_group(
        self,
        *,
        account: builtins.str,
        subnet_groups: typing.Sequence[builtins.str],
    ) -> None:
        '''(experimental) Share a subnetGroup with another AWS Account.

        :param account: 
        :param subnet_groups: 

        :stability: experimental
        '''
        props = ShareSubnetGroupProps(account=account, subnet_groups=subnet_groups)

        return typing.cast(None, jsii.invoke(self, "shareSubnetGroup", [props]))

    @builtins.property
    @jsii.member(jsii_name="addRoutesProvider")
    def add_routes_provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "addRoutesProvider"))

    @builtins.property
    @jsii.member(jsii_name="attachToCloudwanProvider")
    def attach_to_cloudwan_provider(
        self,
    ) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "attachToCloudwanProvider"))

    @builtins.property
    @jsii.member(jsii_name="tgWaiterProvider")
    def tg_waiter_provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "tgWaiterProvider"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) the ec2.Vpc that is passed in as property.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="subnetConfiguration")
    def subnet_configuration(self) -> typing.List["SubnetGroup"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["SubnetGroup"], jsii.get(self, "subnetConfiguration"))

    @subnet_configuration.setter
    def subnet_configuration(self, value: typing.List["SubnetGroup"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9173e9273f1a33d7c93f62cec389e335b569fe20db79ed3bd461319d6de473ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="cloudWanCoreId")
    def cloud_wan_core_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWanCoreId"))

    @cloud_wan_core_id.setter
    def cloud_wan_core_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41133eb7dbe9e312de9fc8e86158aa46045e32f46a96137d19e38414710389e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudWanCoreId", value)

    @builtins.property
    @jsii.member(jsii_name="cloudWanName")
    def cloud_wan_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) the Name of the cloudwan that the VPC is attached to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWanName"))

    @cloud_wan_name.setter
    def cloud_wan_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d031450a64b3312e6d41ff8a3fd8dd4d89d2e443f14b459f50f55104e44734c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudWanName", value)

    @builtins.property
    @jsii.member(jsii_name="cloudWanSegment")
    def cloud_wan_segment(self) -> typing.Optional[builtins.str]:
        '''(experimental) the Name of the Cloudwan segment that the vpc is attached to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWanSegment"))

    @cloud_wan_segment.setter
    def cloud_wan_segment(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee15e42b6d9794a2c135f02d160d2104b488c3f0468ecbc2f26146b8f4fd6e60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudWanSegment", value)

    @builtins.property
    @jsii.member(jsii_name="cloudWanVpcAttachmentId")
    def cloud_wan_vpc_attachment_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) AttachmentId when the vpc is attached to a Cloudwan.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudWanVpcAttachmentId"))

    @cloud_wan_vpc_attachment_id.setter
    def cloud_wan_vpc_attachment_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaba029615705f209a5105315a32273fba7fcf8f610587d51aa016e1d03eaeab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudWanVpcAttachmentId", value)

    @builtins.property
    @jsii.member(jsii_name="firewallArn")
    def firewall_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallArn"))

    @firewall_arn.setter
    def firewall_arn(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__832c7caf59e0d9f05ac7e78ea6fb51e11e62e93883f61adab1ff709a73d8cb20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallArn", value)

    @builtins.property
    @jsii.member(jsii_name="r53endpointResolvers")
    def r53endpoint_resolvers(self) -> typing.Optional["R53Resolverendpoints"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["R53Resolverendpoints"], jsii.get(self, "r53endpointResolvers"))

    @r53endpoint_resolvers.setter
    def r53endpoint_resolvers(
        self,
        value: typing.Optional["R53Resolverendpoints"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c77f9b016ba3a9508037ef698fb3ebc7e084dd4ba557480d635f6a76cf3615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "r53endpointResolvers", value)

    @builtins.property
    @jsii.member(jsii_name="transitGWAttachmentID")
    def transit_gw_attachment_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) AttachmentId when the vpc is attached to a transitGateway.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "transitGWAttachmentID"))

    @transit_gw_attachment_id.setter
    def transit_gw_attachment_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cad7d61f378dbe6a4150f8261ada78d5df85573aeac9c3a5b188d73cae14b83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transitGWAttachmentID", value)

    @builtins.property
    @jsii.member(jsii_name="transitGWID")
    def transit_gwid(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Id of the transitgateway that the VPC is attached to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "transitGWID"))

    @transit_gwid.setter
    def transit_gwid(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60a740df0241049f39779114886dc0376d5b8baecee696d9da10f6f69b2eb2d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transitGWID", value)

    @builtins.property
    @jsii.member(jsii_name="vpcAttachmentCR")
    def vpc_attachment_cr(self) -> typing.Optional[_aws_cdk_ceddda9d.CustomResource]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.CustomResource], jsii.get(self, "vpcAttachmentCR"))

    @vpc_attachment_cr.setter
    def vpc_attachment_cr(
        self,
        value: typing.Optional[_aws_cdk_ceddda9d.CustomResource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ebffe131fe32db4dffe841056a993a780810db780b119f65dcf0876c338178d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcAttachmentCR", value)

    @builtins.property
    @jsii.member(jsii_name="vpcAttachmentId")
    def vpc_attachment_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcAttachmentId"))

    @vpc_attachment_id.setter
    def vpc_attachment_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a5c5d6650d11694c0dc1b772e361f6ea204401cb9978a4f1c11aaf6bb2e99ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcAttachmentId", value)

    @builtins.property
    @jsii.member(jsii_name="vpcAttachmentSegmentName")
    def vpc_attachment_segment_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcAttachmentSegmentName"))

    @vpc_attachment_segment_name.setter
    def vpc_attachment_segment_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df2b5419ea609f9b0e6e4898ace5dc2a5298dfb0e2e399f6bcc24b3984b20e98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcAttachmentSegmentName", value)


class EnterpriseVpcLambda(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.EnterpriseVpcLambda",
):
    '''
    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05dbb65456686ae87770a91158ef46250fddd6acb2a66551f63e13c9986e4950)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="addRoutesProvider")
    def add_routes_provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''(experimental) A custom resource to use for adding routes.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "addRoutesProvider"))

    @builtins.property
    @jsii.member(jsii_name="attachToCloudwanProvider")
    def attach_to_cloudwan_provider(
        self,
    ) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''(experimental) attach to cloudwan with a water.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "attachToCloudwanProvider"))

    @builtins.property
    @jsii.member(jsii_name="tgWaiterProvider")
    def tg_waiter_provider(self) -> _aws_cdk_custom_resources_ceddda9d.Provider:
        '''(experimental) A check to see if transitgateway is ready to route to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_custom_resources_ceddda9d.Provider, jsii.get(self, "tgWaiterProvider"))


@jsii.data_type(
    jsii_type="raindancers-network.EnterpriseVpcProps",
    jsii_struct_bases=[],
    name_mapping={"evpc": "evpc", "vpc": "vpc"},
)
class EnterpriseVpcProps:
    def __init__(
        self,
        *,
        evpc: typing.Optional[typing.Union["EvpcProps", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
    ) -> None:
        '''(experimental) Propertys for an Enterprise VPC.

        :param evpc: 
        :param vpc: 

        :stability: experimental
        '''
        if isinstance(evpc, dict):
            evpc = EvpcProps(**evpc)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afca2bdc03f3a5195c7af4eefa5474a6146c184f16de07e31ec2870f77042189)
            check_type(argname="argument evpc", value=evpc, expected_type=type_hints["evpc"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if evpc is not None:
            self._values["evpc"] = evpc
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def evpc(self) -> typing.Optional["EvpcProps"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("evpc")
        return typing.cast(typing.Optional["EvpcProps"], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnterpriseVpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnterpriseZone(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.EnterpriseZone",
):
    '''(experimental) create forwarding rules and associate them with a vpc.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        enterprise_domain_name: builtins.str,
        local_vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        hub_vpcs: typing.Optional[typing.Sequence[typing.Union["HubVpc", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param enterprise_domain_name: 
        :param local_vpc: 
        :param hub_vpcs: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1738f5f8156456fa14dee204ef76e7aeac25f6d6ba479fff6ba44343dbe45e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EnterpriseZoneProps(
            enterprise_domain_name=enterprise_domain_name,
            local_vpc=local_vpc,
            hub_vpcs=hub_vpcs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="privateZone")
    def private_zone(self) -> _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.PrivateHostedZone, jsii.get(self, "privateZone"))


@jsii.data_type(
    jsii_type="raindancers-network.EnterpriseZoneProps",
    jsii_struct_bases=[],
    name_mapping={
        "enterprise_domain_name": "enterpriseDomainName",
        "local_vpc": "localVpc",
        "hub_vpcs": "hubVpcs",
    },
)
class EnterpriseZoneProps:
    def __init__(
        self,
        *,
        enterprise_domain_name: builtins.str,
        local_vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        hub_vpcs: typing.Optional[typing.Sequence[typing.Union["HubVpc", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param enterprise_domain_name: 
        :param local_vpc: 
        :param hub_vpcs: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7e104e76bcc3465a5d6e5e975bb4878d75e482d7980320daba8ba9bc733682f)
            check_type(argname="argument enterprise_domain_name", value=enterprise_domain_name, expected_type=type_hints["enterprise_domain_name"])
            check_type(argname="argument local_vpc", value=local_vpc, expected_type=type_hints["local_vpc"])
            check_type(argname="argument hub_vpcs", value=hub_vpcs, expected_type=type_hints["hub_vpcs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enterprise_domain_name": enterprise_domain_name,
            "local_vpc": local_vpc,
        }
        if hub_vpcs is not None:
            self._values["hub_vpcs"] = hub_vpcs

    @builtins.property
    def enterprise_domain_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("enterprise_domain_name")
        assert result is not None, "Required property 'enterprise_domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def local_vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("local_vpc")
        assert result is not None, "Required property 'local_vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def hub_vpcs(self) -> typing.Optional[typing.List["HubVpc"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hub_vpcs")
        return typing.cast(typing.Optional[typing.List["HubVpc"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnterpriseZoneProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.EvpcProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.VpcProps],
    name_mapping={
        "availability_zones": "availabilityZones",
        "cidr": "cidr",
        "default_instance_tenancy": "defaultInstanceTenancy",
        "enable_dns_hostnames": "enableDnsHostnames",
        "enable_dns_support": "enableDnsSupport",
        "flow_logs": "flowLogs",
        "gateway_endpoints": "gatewayEndpoints",
        "ip_addresses": "ipAddresses",
        "max_azs": "maxAzs",
        "nat_gateway_provider": "natGatewayProvider",
        "nat_gateways": "natGateways",
        "nat_gateway_subnets": "natGatewaySubnets",
        "reserved_azs": "reservedAzs",
        "restrict_default_security_group": "restrictDefaultSecurityGroup",
        "subnet_configuration": "subnetConfiguration",
        "vpc_name": "vpcName",
        "vpn_connections": "vpnConnections",
        "vpn_gateway": "vpnGateway",
        "vpn_gateway_asn": "vpnGatewayAsn",
        "vpn_route_propagation": "vpnRoutePropagation",
        "subnet_groups": "subnetGroups",
    },
)
class EvpcProps(_aws_cdk_aws_ec2_ceddda9d.VpcProps):
    def __init__(
        self,
        *,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        cidr: typing.Optional[builtins.str] = None,
        default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        reserved_azs: typing.Optional[jsii.Number] = None,
        restrict_default_security_group: typing.Optional[builtins.bool] = None,
        subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpc_name: typing.Optional[builtins.str] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        subnet_groups: typing.Optional[typing.Sequence["SubnetGroup"]] = None,
    ) -> None:
        '''
        :param availability_zones: Availability zones this VPC spans. Specify this option only if you do not specify ``maxAzs``. Default: - a subset of AZs of the stack
        :param cidr: (deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param ip_addresses: The Provider to use to allocate IP Space to your VPC. Options include static allocation or from a pool. Default: ec2.IpAddresses.cidr
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Specify this option only if you do not specify ``availabilityZones``. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param reserved_azs: Define the number of AZs to reserve. When specified, the IP space is reserved for the azs but no actual resources are provisioned. Default: 0
        :param restrict_default_security_group: If set to true then the default inbound & outbound rules will be removed from the default security group. Default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpc_name: The VPC name. Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag Default: this.node.path
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.
        :param subnet_groups: 

        :stability: experimental
        '''
        if isinstance(nat_gateway_subnets, dict):
            nat_gateway_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**nat_gateway_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c71f8ffee31b0d69c71d1de6da5d0dac06c4cd197e90f7039f904e7efb5583e)
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument default_instance_tenancy", value=default_instance_tenancy, expected_type=type_hints["default_instance_tenancy"])
            check_type(argname="argument enable_dns_hostnames", value=enable_dns_hostnames, expected_type=type_hints["enable_dns_hostnames"])
            check_type(argname="argument enable_dns_support", value=enable_dns_support, expected_type=type_hints["enable_dns_support"])
            check_type(argname="argument flow_logs", value=flow_logs, expected_type=type_hints["flow_logs"])
            check_type(argname="argument gateway_endpoints", value=gateway_endpoints, expected_type=type_hints["gateway_endpoints"])
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument max_azs", value=max_azs, expected_type=type_hints["max_azs"])
            check_type(argname="argument nat_gateway_provider", value=nat_gateway_provider, expected_type=type_hints["nat_gateway_provider"])
            check_type(argname="argument nat_gateways", value=nat_gateways, expected_type=type_hints["nat_gateways"])
            check_type(argname="argument nat_gateway_subnets", value=nat_gateway_subnets, expected_type=type_hints["nat_gateway_subnets"])
            check_type(argname="argument reserved_azs", value=reserved_azs, expected_type=type_hints["reserved_azs"])
            check_type(argname="argument restrict_default_security_group", value=restrict_default_security_group, expected_type=type_hints["restrict_default_security_group"])
            check_type(argname="argument subnet_configuration", value=subnet_configuration, expected_type=type_hints["subnet_configuration"])
            check_type(argname="argument vpc_name", value=vpc_name, expected_type=type_hints["vpc_name"])
            check_type(argname="argument vpn_connections", value=vpn_connections, expected_type=type_hints["vpn_connections"])
            check_type(argname="argument vpn_gateway", value=vpn_gateway, expected_type=type_hints["vpn_gateway"])
            check_type(argname="argument vpn_gateway_asn", value=vpn_gateway_asn, expected_type=type_hints["vpn_gateway_asn"])
            check_type(argname="argument vpn_route_propagation", value=vpn_route_propagation, expected_type=type_hints["vpn_route_propagation"])
            check_type(argname="argument subnet_groups", value=subnet_groups, expected_type=type_hints["subnet_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cidr is not None:
            self._values["cidr"] = cidr
        if default_instance_tenancy is not None:
            self._values["default_instance_tenancy"] = default_instance_tenancy
        if enable_dns_hostnames is not None:
            self._values["enable_dns_hostnames"] = enable_dns_hostnames
        if enable_dns_support is not None:
            self._values["enable_dns_support"] = enable_dns_support
        if flow_logs is not None:
            self._values["flow_logs"] = flow_logs
        if gateway_endpoints is not None:
            self._values["gateway_endpoints"] = gateway_endpoints
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if max_azs is not None:
            self._values["max_azs"] = max_azs
        if nat_gateway_provider is not None:
            self._values["nat_gateway_provider"] = nat_gateway_provider
        if nat_gateways is not None:
            self._values["nat_gateways"] = nat_gateways
        if nat_gateway_subnets is not None:
            self._values["nat_gateway_subnets"] = nat_gateway_subnets
        if reserved_azs is not None:
            self._values["reserved_azs"] = reserved_azs
        if restrict_default_security_group is not None:
            self._values["restrict_default_security_group"] = restrict_default_security_group
        if subnet_configuration is not None:
            self._values["subnet_configuration"] = subnet_configuration
        if vpc_name is not None:
            self._values["vpc_name"] = vpc_name
        if vpn_connections is not None:
            self._values["vpn_connections"] = vpn_connections
        if vpn_gateway is not None:
            self._values["vpn_gateway"] = vpn_gateway
        if vpn_gateway_asn is not None:
            self._values["vpn_gateway_asn"] = vpn_gateway_asn
        if vpn_route_propagation is not None:
            self._values["vpn_route_propagation"] = vpn_route_propagation
        if subnet_groups is not None:
            self._values["subnet_groups"] = subnet_groups

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Availability zones this VPC spans.

        Specify this option only if you do not specify ``maxAzs``.

        :default: - a subset of AZs of the stack
        '''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The CIDR range to use for the VPC, e.g. '10.0.0.0/16'.

        Should be a minimum of /28 and maximum size of /16. The range will be
        split across all subnets per Availability Zone.

        :default: Vpc.DEFAULT_CIDR_RANGE

        :deprecated: Use ipAddresses instead

        :stability: deprecated
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_instance_tenancy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy]:
        '''The default tenancy of instances launched into the VPC.

        By setting this to dedicated tenancy, instances will be launched on
        hardware dedicated to a single AWS customer, unless specifically specified
        at instance launch time. Please note, not all instance types are usable
        with Dedicated tenancy.

        :default: DefaultInstanceTenancy.Default (shared) tenancy
        '''
        result = self._values.get("default_instance_tenancy")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy], result)

    @builtins.property
    def enable_dns_hostnames(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instances launched in the VPC get public DNS hostnames.

        If this attribute is true, instances in the VPC get public DNS hostnames,
        but only if the enableDnsSupport attribute is also set to true.

        :default: true
        '''
        result = self._values.get("enable_dns_hostnames")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_dns_support(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DNS resolution is supported for the VPC.

        If this attribute is false, the Amazon-provided DNS server in the VPC that
        resolves public DNS hostnames to IP addresses is not enabled. If this
        attribute is true, queries to the Amazon provided DNS server at the
        169.254.169.253 IP address, or the reserved IP address at the base of the
        VPC IPv4 network range plus two will succeed.

        :default: true
        '''
        result = self._values.get("enable_dns_support")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flow_logs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]]:
        '''Flow logs to add to this VPC.

        :default: - No flow logs.
        '''
        result = self._values.get("flow_logs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.FlowLogOptions]], result)

    @builtins.property
    def gateway_endpoints(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]]:
        '''Gateway endpoints to add to this VPC.

        :default: - None.
        '''
        result = self._values.get("gateway_endpoints")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions]], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses]:
        '''The Provider to use to allocate IP Space to your VPC.

        Options include static allocation or from a pool.

        :default: ec2.IpAddresses.cidr
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses], result)

    @builtins.property
    def max_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the maximum number of AZs to use in this region.

        If the region has more AZs than you want to use (for example, because of
        EIP limits), pick a lower number here. The AZs will be sorted and picked
        from the start of the list.

        If you pick a higher number than the number of AZs in the region, all AZs
        in the region will be selected. To use "all AZs" available to your
        account, use a high number (such as 99).

        Be aware that environment-agnostic stacks will be created with access to
        only 2 AZs, so to use more than 2 AZs, be sure to specify the account and
        region on your stack.

        Specify this option only if you do not specify ``availabilityZones``.

        :default: 3
        '''
        result = self._values.get("max_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_provider(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider]:
        '''What type of NAT provider to use.

        Select between NAT gateways or NAT instances. NAT gateways
        may not be available in all AWS regions.

        :default: NatProvider.gateway()
        '''
        result = self._values.get("nat_gateway_provider")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider], result)

    @builtins.property
    def nat_gateways(self) -> typing.Optional[jsii.Number]:
        '''The number of NAT Gateways/Instances to create.

        The type of NAT gateway or instance will be determined by the
        ``natGatewayProvider`` parameter.

        You can set this number lower than the number of Availability Zones in your
        VPC in order to save on NAT cost. Be aware you may be charged for
        cross-AZ data traffic instead.

        :default: - One NAT gateway/instance per Availability Zone
        '''
        result = self._values.get("nat_gateways")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nat_gateway_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Configures the subnets which will have NAT Gateways/Instances.

        You can pick a specific group of subnets by specifying the group name;
        the picked subnets must be public subnets.

        Only necessary if you have more than one public subnet group.

        :default: - All public subnets.
        '''
        result = self._values.get("nat_gateway_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def reserved_azs(self) -> typing.Optional[jsii.Number]:
        '''Define the number of AZs to reserve.

        When specified, the IP space is reserved for the azs but no actual
        resources are provisioned.

        :default: 0
        '''
        result = self._values.get("reserved_azs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def restrict_default_security_group(self) -> typing.Optional[builtins.bool]:
        '''If set to true then the default inbound & outbound rules will be removed from the default security group.

        :default: true if '@aws-cdk/aws-ec2:restrictDefaultSecurityGroup' is enabled, false otherwise
        '''
        result = self._values.get("restrict_default_security_group")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_configuration(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]]:
        '''Configure the subnets to build for each AZ.

        Each entry in this list configures a Subnet Group; each group will contain a
        subnet for each Availability Zone.

        For example, if you want 1 public subnet, 1 private subnet, and 1 isolated
        subnet in each AZ provide the following::

           new ec2.Vpc(this, 'VPC', {
             subnetConfiguration: [
                {
                  cidrMask: 24,
                  name: 'ingress',
                  subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                  cidrMask: 24,
                  name: 'application',
                  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                },
                {
                  cidrMask: 28,
                  name: 'rds',
                  subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
                }
             ]
           });

        :default:

        - The VPC CIDR will be evenly divided between 1 public and 1
        private subnet per AZ.
        '''
        result = self._values.get("subnet_configuration")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration]], result)

    @builtins.property
    def vpc_name(self) -> typing.Optional[builtins.str]:
        '''The VPC name.

        Since the VPC resource doesn't support providing a physical name, the value provided here will be recorded in the ``Name`` tag

        :default: this.node.path
        '''
        result = self._values.get("vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpn_connections(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]]:
        '''VPN connections to this VPC.

        :default: - No connections.
        '''
        result = self._values.get("vpn_connections")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions]], result)

    @builtins.property
    def vpn_gateway(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether a VPN gateway should be created and attached to this VPC.

        :default: - true when vpnGatewayAsn or vpnConnections is specified
        '''
        result = self._values.get("vpn_gateway")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpn_gateway_asn(self) -> typing.Optional[jsii.Number]:
        '''The private Autonomous System Number (ASN) for the VPN gateway.

        :default: - Amazon default ASN.
        '''
        result = self._values.get("vpn_gateway_asn")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpn_route_propagation(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''Where to propagate VPN routes.

        :default:

        - On the route tables associated with private subnets. If no
        private subnets exists, isolated subnets are used. If no isolated subnets
        exists, public subnets are used.
        '''
        result = self._values.get("vpn_route_propagation")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def subnet_groups(self) -> typing.Optional[typing.List["SubnetGroup"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_groups")
        return typing.cast(typing.Optional[typing.List["SubnetGroup"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EvpcProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FQDNStatefulRule(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.FQDNStatefulRule",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        fqdn: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
        rules_database: typing.Optional["StatefulRuleDatabase"] = None,
        action: "StatefulAction",
        destination: typing.Union[builtins.str, "PrefixList", DynamicTagResourceGroup],
        dest_port: builtins.str,
        direction: Direction,
        name: builtins.str,
        protocol: "FWProtocol",
        source: typing.Union[builtins.str, "PrefixList", DynamicTagResourceGroup],
        src_port: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param fqdn: 
        :param priority: 
        :param rules_database: 
        :param action: 
        :param destination: 
        :param dest_port: 
        :param direction: 
        :param name: 
        :param protocol: 
        :param source: 
        :param src_port: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71a1c56f02739823263b092ff943772c7f2f3391bbd9942383cc59c28445c85)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FQDNStatefulRuleProps(
            fqdn=fqdn,
            priority=priority,
            rules_database=rules_database,
            action=action,
            destination=destination,
            dest_port=dest_port,
            direction=direction,
            name=name,
            protocol=protocol,
            source=source,
            src_port=src_port,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="prefixListSet")
    def prefix_list_set(self) -> typing.List["PrefixListSetInterface"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["PrefixListSetInterface"], jsii.get(self, "prefixListSet"))

    @prefix_list_set.setter
    def prefix_list_set(self, value: typing.List["PrefixListSetInterface"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1dc98d03f57fd069d01e4d62cb4521f4fff2753c6c297e602bcf52009e8f815)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefixListSet", value)

    @builtins.property
    @jsii.member(jsii_name="resourceGroupSets")
    def resource_group_sets(self) -> typing.List[DynamicTagResourceGroupSet]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[DynamicTagResourceGroupSet], jsii.get(self, "resourceGroupSets"))

    @resource_group_sets.setter
    def resource_group_sets(
        self,
        value: typing.List[DynamicTagResourceGroupSet],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9835146b6489851a86a445db60d09fabc4f10c8520b89ee215a5ba579ba743b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupSets", value)

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4646f6ea85d216f3e1001ae364c19dcb179116d463a950aab77e0ab75de4874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value)


@jsii.enum(jsii_type="raindancers-network.FWProtocol")
class FWProtocol(enum.Enum):
    '''
    :stability: experimental
    '''

    TCP = "TCP"
    '''
    :stability: experimental
    '''
    UPD = "UPD"
    '''
    :stability: experimental
    '''
    ICMP = "ICMP"
    '''
    :stability: experimental
    '''
    IP = "IP"
    '''
    :stability: experimental
    '''
    HTTP = "HTTP"
    '''
    :stability: experimental
    '''
    TLS = "TLS"
    '''
    :stability: experimental
    '''


class FindPrefixList(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.FindPrefixList",
):
    '''(experimental) Enforces the use of IMDSv2, without causing replacement of the Instance.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        prefix_list_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param prefix_list_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__403c3d7329242d2884e1364b9b347b4ae549506aa47a47265328d234cb688ae6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FindPrefixListProps(prefix_list_name=prefix_list_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="prefixListId")
    def prefix_list_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "prefixListId"))

    @prefix_list_id.setter
    def prefix_list_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__988f77e5525890d84b5195080d891f202ad0be409e970f2722d1fe604d9a224e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefixListId", value)


@jsii.data_type(
    jsii_type="raindancers-network.FindPrefixListProps",
    jsii_struct_bases=[],
    name_mapping={"prefix_list_name": "prefixListName"},
)
class FindPrefixListProps:
    def __init__(self, *, prefix_list_name: builtins.str) -> None:
        '''
        :param prefix_list_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__277873ef1815cd4375f45230f8c14cdfacebbf62958d5b95d9171fbc0e95c5c7)
            check_type(argname="argument prefix_list_name", value=prefix_list_name, expected_type=type_hints["prefix_list_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "prefix_list_name": prefix_list_name,
        }

    @builtins.property
    def prefix_list_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("prefix_list_name")
        assert result is not None, "Required property 'prefix_list_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FindPrefixListProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirewallPolicy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.FirewallPolicy",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        policy_name: builtins.str,
        stateless_default_actions: typing.Sequence["StatelessActions"],
        stateless_fragment_default_actions: typing.Sequence["StatelessActions"],
        stateful_engine_options: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param policy_name: 
        :param stateless_default_actions: 
        :param stateless_fragment_default_actions: 
        :param stateful_engine_options: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06a8230a8020f69654e71e875cdb4a008df6c2aedff4e5c47d086c06f7aeb4ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FirewallPolicyProps(
            policy_name=policy_name,
            stateless_default_actions=stateless_default_actions,
            stateless_fragment_default_actions=stateless_fragment_default_actions,
            stateful_engine_options=stateful_engine_options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addManagedStatefulRules")
    def add_managed_stateful_rules(
        self,
        *,
        aws_managed_rules: typing.Sequence["ManagedAwsFirewallRules"],
    ) -> None:
        '''
        :param aws_managed_rules: 

        :stability: experimental
        '''
        props = AddStatefulRulesProps(aws_managed_rules=aws_managed_rules)

        return typing.cast(None, jsii.invoke(self, "addManagedStatefulRules", [props]))

    @jsii.member(jsii_name="addStatelessRuleGroup")
    def add_stateless_rule_group(
        self,
        *,
        description: builtins.str,
        group_name: builtins.str,
        rules: typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty, typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param description: 
        :param group_name: 
        :param rules: 

        :stability: experimental
        '''
        props = AddStatelessRulesProps(
            description=description, group_name=group_name, rules=rules
        )

        return typing.cast(None, jsii.invoke(self, "addStatelessRuleGroup", [props]))

    @builtins.property
    @jsii.member(jsii_name="firewallpolicy")
    def firewallpolicy(self) -> _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy, jsii.get(self, "firewallpolicy"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> "IFirewallPolicyProperty":
        '''
        :stability: experimental
        '''
        return typing.cast("IFirewallPolicyProperty", jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: "IFirewallPolicyProperty") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9cfb4f0f86bbf9c98d004a456d22f8297a5b16955ddc4b98897f84b2ccad1cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="raindancers-network.FirewallPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "policy_name": "policyName",
        "stateless_default_actions": "statelessDefaultActions",
        "stateless_fragment_default_actions": "statelessFragmentDefaultActions",
        "stateful_engine_options": "statefulEngineOptions",
    },
)
class FirewallPolicyProps:
    def __init__(
        self,
        *,
        policy_name: builtins.str,
        stateless_default_actions: typing.Sequence["StatelessActions"],
        stateless_fragment_default_actions: typing.Sequence["StatelessActions"],
        stateful_engine_options: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param policy_name: 
        :param stateless_default_actions: 
        :param stateless_fragment_default_actions: 
        :param stateful_engine_options: 

        :stability: experimental
        '''
        if isinstance(stateful_engine_options, dict):
            stateful_engine_options = _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty(**stateful_engine_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9bc423a66b0b183dffcf44586b486d0a85effb8f2d8e036e9a75bccd5243de)
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
            check_type(argname="argument stateless_default_actions", value=stateless_default_actions, expected_type=type_hints["stateless_default_actions"])
            check_type(argname="argument stateless_fragment_default_actions", value=stateless_fragment_default_actions, expected_type=type_hints["stateless_fragment_default_actions"])
            check_type(argname="argument stateful_engine_options", value=stateful_engine_options, expected_type=type_hints["stateful_engine_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "policy_name": policy_name,
            "stateless_default_actions": stateless_default_actions,
            "stateless_fragment_default_actions": stateless_fragment_default_actions,
        }
        if stateful_engine_options is not None:
            self._values["stateful_engine_options"] = stateful_engine_options

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stateless_default_actions(self) -> typing.List["StatelessActions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("stateless_default_actions")
        assert result is not None, "Required property 'stateless_default_actions' is missing"
        return typing.cast(typing.List["StatelessActions"], result)

    @builtins.property
    def stateless_fragment_default_actions(self) -> typing.List["StatelessActions"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("stateless_fragment_default_actions")
        assert result is not None, "Required property 'stateless_fragment_default_actions' is missing"
        return typing.cast(typing.List["StatelessActions"], result)

    @builtins.property
    def stateful_engine_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty]:
        '''
        :stability: experimental
        '''
        result = self._values.get("stateful_engine_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.FlowLogProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "local_athena_querys": "localAthenaQuerys",
        "one_minute_flow_logs": "oneMinuteFlowLogs",
    },
)
class FlowLogProps:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        local_athena_querys: typing.Optional[builtins.bool] = None,
        one_minute_flow_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for flow logs *.

        :param bucket: (experimental) the central s3 location for enterprise flow logs.
        :param local_athena_querys: (experimental) create in Account Athena Querys for flow logs.
        :param one_minute_flow_logs: (experimental) 1 minute resolution.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42834d58702d51be011948142d606971c35a7a6253e4a9c471a8d22a3ac06620)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument local_athena_querys", value=local_athena_querys, expected_type=type_hints["local_athena_querys"])
            check_type(argname="argument one_minute_flow_logs", value=one_minute_flow_logs, expected_type=type_hints["one_minute_flow_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if local_athena_querys is not None:
            self._values["local_athena_querys"] = local_athena_querys
        if one_minute_flow_logs is not None:
            self._values["one_minute_flow_logs"] = one_minute_flow_logs

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) the central s3 location for enterprise flow logs.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def local_athena_querys(self) -> typing.Optional[builtins.bool]:
        '''(experimental) create in Account Athena Querys for flow logs.

        :stability: experimental
        '''
        result = self._values.get("local_athena_querys")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def one_minute_flow_logs(self) -> typing.Optional[builtins.bool]:
        '''(experimental) 1 minute resolution.

        :stability: experimental
        '''
        result = self._values.get("one_minute_flow_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FlowLogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ForwardingRules(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.ForwardingRules",
):
    '''(experimental) create forwarding rules and associate them with a vpc.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domains: typing.Sequence[builtins.str],
        resolver_id: builtins.str,
        resolver_ip: typing.Sequence[builtins.str],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domains: 
        :param resolver_id: 
        :param resolver_ip: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05890aaf0a6855cc0a67fa9b2b36f753278d6fa228bcb7ac4009cac06f0f999c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ForwardingRulesProps(
            domains=domains, resolver_id=resolver_id, resolver_ip=resolver_ip, vpc=vpc
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.ForwardingRulesProps",
    jsii_struct_bases=[],
    name_mapping={
        "domains": "domains",
        "resolver_id": "resolverId",
        "resolver_ip": "resolverIP",
        "vpc": "vpc",
    },
)
class ForwardingRulesProps:
    def __init__(
        self,
        *,
        domains: typing.Sequence[builtins.str],
        resolver_id: builtins.str,
        resolver_ip: typing.Sequence[builtins.str],
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param domains: 
        :param resolver_id: 
        :param resolver_ip: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c36a2f748867f71db259c42e27b1a718cd12b8ad5db77c5db873f54d5c0535)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument resolver_id", value=resolver_id, expected_type=type_hints["resolver_id"])
            check_type(argname="argument resolver_ip", value=resolver_ip, expected_type=type_hints["resolver_ip"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
            "resolver_id": resolver_id,
            "resolver_ip": resolver_ip,
            "vpc": vpc,
        }

    @builtins.property
    def domains(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def resolver_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("resolver_id")
        assert result is not None, "Required property 'resolver_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resolver_ip(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("resolver_ip")
        assert result is not None, "Required property 'resolver_ip' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ForwardingRulesProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GetTunnelAddressPair(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.GetTunnelAddressPair",
):
    '''(experimental) Allocate a pair of /30 networks CIDRS for use in Ipsec VPN Tunnels.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ipam_pool_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param scope: scope in which this resource is created.
        :param id: scope id of the resoruce.
        :param ipam_pool_id: (experimental) The IPAM Pool Id from which the assginment will be made from.
        :param name: (experimental) The Name used by IPAM to record the allocation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d9a4b1d87dfaf4886011b85a178d769c4555464180743d2dfc0f4bc299fcad0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GetTunnelAddressPairProps(ipam_pool_id=ipam_pool_id, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="assignedCidrPair")
    def assigned_cidr_pair(self) -> typing.List[builtins.str]:
        '''(experimental) returns 2 cidr blocks as an array to be used by an IPsec Tunnel.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "assignedCidrPair"))


@jsii.data_type(
    jsii_type="raindancers-network.GetTunnelAddressPairProps",
    jsii_struct_bases=[],
    name_mapping={"ipam_pool_id": "ipamPoolId", "name": "name"},
)
class GetTunnelAddressPairProps:
    def __init__(self, *, ipam_pool_id: builtins.str, name: builtins.str) -> None:
        '''(experimental) Properties for obtaining an IPAM assigned address pair for use on IPsec VPN Tunnels.

        :param ipam_pool_id: (experimental) The IPAM Pool Id from which the assginment will be made from.
        :param name: (experimental) The Name used by IPAM to record the allocation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1e460b06579855f3c47c23ff63809c00e4ebf1d00a865a6ced39224341a328c)
            check_type(argname="argument ipam_pool_id", value=ipam_pool_id, expected_type=type_hints["ipam_pool_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ipam_pool_id": ipam_pool_id,
            "name": name,
        }

    @builtins.property
    def ipam_pool_id(self) -> builtins.str:
        '''(experimental) The IPAM Pool Id from which the assginment will be made from.

        :stability: experimental
        '''
        result = self._values.get("ipam_pool_id")
        assert result is not None, "Required property 'ipam_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The Name used by IPAM to record the allocation.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GetTunnelAddressPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.HubVpc",
    jsii_struct_bases=[],
    name_mapping={
        "region": "region",
        "cross_account": "crossAccount",
        "vpc_search_tag": "vpcSearchTag",
    },
)
class HubVpc:
    def __init__(
        self,
        *,
        region: builtins.str,
        cross_account: typing.Optional[typing.Union[CrossAccountProps, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
    ) -> None:
        '''
        :param region: (experimental) what region is the central account in.
        :param cross_account: 
        :param vpc_search_tag: 

        :stability: experimental
        '''
        if isinstance(cross_account, dict):
            cross_account = CrossAccountProps(**cross_account)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adf25443d7eab2a79bd6c7aff8feceed1186079a3ebf8236907e6c136b15e59b)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument cross_account", value=cross_account, expected_type=type_hints["cross_account"])
            check_type(argname="argument vpc_search_tag", value=vpc_search_tag, expected_type=type_hints["vpc_search_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "region": region,
        }
        if cross_account is not None:
            self._values["cross_account"] = cross_account
        if vpc_search_tag is not None:
            self._values["vpc_search_tag"] = vpc_search_tag

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) what region is the central account in.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account(self) -> typing.Optional[CrossAccountProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cross_account")
        return typing.cast(typing.Optional[CrossAccountProps], result)

    @builtins.property
    def vpc_search_tag(self) -> typing.Optional[_aws_cdk_ceddda9d.Tag]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_search_tag")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubVpc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="raindancers-network.IAssignment")
class IAssignment(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) The resource interface for an AWS SSO assignment.

    This interface has no attributes because the resulting resource has none.

    :stability: experimental
    '''

    pass


class _IAssignmentProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) The resource interface for an AWS SSO assignment.

    This interface has no attributes because the resulting resource has none.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.IAssignment"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAssignment).__jsii_proxy_class__ = lambda : _IAssignmentProxy


@jsii.interface(jsii_type="raindancers-network.ICoreNetworkSegmentProps")
class ICoreNetworkSegmentProps(typing_extensions.Protocol):
    '''(experimental) Properties creating a Corenetwork Segment.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="policyTableServiceToken")
    def policy_table_service_token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="segmentName")
    def segment_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="updateDependsOn")
    def update_depends_on(self) -> typing.List[_aws_cdk_ceddda9d.CustomResource]:
        '''
        :stability: experimental
        '''
        ...

    @update_depends_on.setter
    def update_depends_on(
        self,
        value: typing.List[_aws_cdk_ceddda9d.CustomResource],
    ) -> None:
        ...


class _ICoreNetworkSegmentPropsProxy:
    '''(experimental) Properties creating a Corenetwork Segment.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.ICoreNetworkSegmentProps"

    @builtins.property
    @jsii.member(jsii_name="policyTableServiceToken")
    def policy_table_service_token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyTableServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="segmentName")
    def segment_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "segmentName"))

    @builtins.property
    @jsii.member(jsii_name="updateDependsOn")
    def update_depends_on(self) -> typing.List[_aws_cdk_ceddda9d.CustomResource]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.CustomResource], jsii.get(self, "updateDependsOn"))

    @update_depends_on.setter
    def update_depends_on(
        self,
        value: typing.List[_aws_cdk_ceddda9d.CustomResource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e84973a37cf83d7492090bb53b8deefc4986415f2da11b0d0e2b7881bb92c53f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateDependsOn", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICoreNetworkSegmentProps).__jsii_proxy_class__ = lambda : _ICoreNetworkSegmentPropsProxy


@jsii.interface(jsii_type="raindancers-network.IFirewallPolicyProperty")
class IFirewallPolicyProperty(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="statelessDefaultActions")
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @stateless_default_actions.setter
    def stateless_default_actions(self, value: typing.List[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statelessFragmentDefaultActions")
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @stateless_fragment_default_actions.setter
    def stateless_fragment_default_actions(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statefulDefaultActions")
    def stateful_default_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @stateful_default_actions.setter
    def stateful_default_actions(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statefulEngineOptions")
    def stateful_engine_options(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]]:
        '''
        :stability: experimental
        '''
        ...

    @stateful_engine_options.setter
    def stateful_engine_options(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statefulRuleGroupReferences")
    def stateful_rule_group_references(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]]:
        '''
        :stability: experimental
        '''
        ...

    @stateful_rule_group_references.setter
    def stateful_rule_group_references(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statelessCustomActions")
    def stateless_custom_actions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]]:
        '''
        :stability: experimental
        '''
        ...

    @stateless_custom_actions.setter
    def stateless_custom_actions(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statelessRuleGroupReferences")
    def stateless_rule_group_references(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]]:
        '''
        :stability: experimental
        '''
        ...

    @stateless_rule_group_references.setter
    def stateless_rule_group_references(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]],
    ) -> None:
        ...


class _IFirewallPolicyPropertyProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.IFirewallPolicyProperty"

    @builtins.property
    @jsii.member(jsii_name="statelessDefaultActions")
    def stateless_default_actions(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessDefaultActions"))

    @stateless_default_actions.setter
    def stateless_default_actions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f7c75ef9e439a56d4b8da713118abcac8949ac40e6ba091b109a83d67cc7ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessDefaultActions", value)

    @builtins.property
    @jsii.member(jsii_name="statelessFragmentDefaultActions")
    def stateless_fragment_default_actions(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "statelessFragmentDefaultActions"))

    @stateless_fragment_default_actions.setter
    def stateless_fragment_default_actions(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c21b8c7634a7f7d7f04c33b8cf21a647e090125acde48fcdc7efee9f1319425c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessFragmentDefaultActions", value)

    @builtins.property
    @jsii.member(jsii_name="statefulDefaultActions")
    def stateful_default_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "statefulDefaultActions"))

    @stateful_default_actions.setter
    def stateful_default_actions(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574771ee94345404b780f607457fdbe3c9ddb8405af72572ebea18d3f410950b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statefulDefaultActions", value)

    @builtins.property
    @jsii.member(jsii_name="statefulEngineOptions")
    def stateful_engine_options(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]], jsii.get(self, "statefulEngineOptions"))

    @stateful_engine_options.setter
    def stateful_engine_options(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13a73f54a1bc47ccf1e89e86b9c4d2b74aed4d6f297a0a3c3e3895cd67fdcf8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statefulEngineOptions", value)

    @builtins.property
    @jsii.member(jsii_name="statefulRuleGroupReferences")
    def stateful_rule_group_references(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]], jsii.get(self, "statefulRuleGroupReferences"))

    @stateful_rule_group_references.setter
    def stateful_rule_group_references(
        self,
        value: typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a996a5fccf377d9772c5038a84b997ceaab893d90c242c6452bbda7460ba9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statefulRuleGroupReferences", value)

    @builtins.property
    @jsii.member(jsii_name="statelessCustomActions")
    def stateless_custom_actions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]], jsii.get(self, "statelessCustomActions"))

    @stateless_custom_actions.setter
    def stateless_custom_actions(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7399cfadc4a3f8b69e62521388a0187a8b9c9b61920bb79299e881873be77a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessCustomActions", value)

    @builtins.property
    @jsii.member(jsii_name="statelessRuleGroupReferences")
    def stateless_rule_group_references(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]], jsii.get(self, "statelessRuleGroupReferences"))

    @stateless_rule_group_references.setter
    def stateless_rule_group_references(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e4c3089492574d56eab5f4795bea81c48cae99888ebe75c61768b6b03adb0af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statelessRuleGroupReferences", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFirewallPolicyProperty).__jsii_proxy_class__ = lambda : _IFirewallPolicyPropertyProxy


@jsii.enum(jsii_type="raindancers-network.IPAddressFamily")
class IPAddressFamily(enum.Enum):
    '''
    :stability: experimental
    '''

    IPV4 = "IPV4"
    '''
    :stability: experimental
    '''
    IPV6 = "IPV6"
    '''
    :stability: experimental
    '''


@jsii.interface(jsii_type="raindancers-network.IPermissionSet")
class IPermissionSet(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) The resource interface for an AWS SSO permission set.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''(experimental) The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''(experimental) The SSO instance ARN of the permission set.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        id: builtins.str,
        *,
        principal: typing.Union["PrincipalProperty", typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional["TargetTypes"] = None,
    ) -> "Assignment":
        '''(experimental) Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        ...


class _IPermissionSetProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) The resource interface for an AWS SSO permission set.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.IPermissionSet"

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''(experimental) The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "permissionSetArn"))

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''(experimental) The SSO instance ARN of the permission set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ssoInstanceArn"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        id: builtins.str,
        *,
        principal: typing.Union["PrincipalProperty", typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional["TargetTypes"] = None,
    ) -> "Assignment":
        '''(experimental) Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1118d4d354617e43640c6b4bd183c4c195e6f81259f0ea2b97cf9dc4d328f606)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        assignment_options = AssignmentOptions(
            principal=principal, target_id=target_id, target_type=target_type
        )

        return typing.cast("Assignment", jsii.invoke(self, "grant", [id, assignment_options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPermissionSet).__jsii_proxy_class__ = lambda : _IPermissionSetProxy


@jsii.enum(jsii_type="raindancers-network.IkeVersion")
class IkeVersion(enum.Enum):
    '''(experimental) Ike Version for S2S VPN.

    :stability: experimental
    '''

    IKEV1 = "IKEV1"
    '''(experimental) Use IKEv1.

    :stability: experimental
    '''
    IKEV2 = "IKEV2"
    '''(experimental) Use IKEv2.

    :stability: experimental
    '''


class IpsecTunnelPool(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.IpsecTunnelPool",
):
    '''(experimental) Creates an IPAM pool to assign address's for IPsec VPNS.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cidr: builtins.str,
        description: builtins.str,
        ipam_scope_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param scope: scope in which this resource is defined.
        :param id: id of the resource.
        :param cidr: (experimental) The Cidr range for pools to be created from eg, 169.254.100.0/27 The cidr must be in the 169.254.0.0/16 range and must be a minimum of a /29 and a maximum of /24. It must also not overlap the AWS reserved ranges. T
        :param description: (experimental) the description used by IPAM to describe the pool.
        :param ipam_scope_id: (experimental) The IPAM Scope Id to use to create the Pool.
        :param name: (experimental) the name used by IPAM to identify the pool.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2aaf7e1f5b48a4247dd1cd4403833674cf827fafc31994ee21767cc61a5e272)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IpsecTunnelPoolProps(
            cidr=cidr, description=description, ipam_scope_id=ipam_scope_id, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="ipampool")
    def ipampool(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool:
        '''(experimental) returns the created ipam Pool.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool, jsii.get(self, "ipampool"))


@jsii.data_type(
    jsii_type="raindancers-network.IpsecTunnelPoolProps",
    jsii_struct_bases=[],
    name_mapping={
        "cidr": "cidr",
        "description": "description",
        "ipam_scope_id": "ipamScopeId",
        "name": "name",
    },
)
class IpsecTunnelPoolProps:
    def __init__(
        self,
        *,
        cidr: builtins.str,
        description: builtins.str,
        ipam_scope_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''(experimental) Properties for defining a IPAM Pool specifically for IPSec VPN Tunnels.

        :param cidr: (experimental) The Cidr range for pools to be created from eg, 169.254.100.0/27 The cidr must be in the 169.254.0.0/16 range and must be a minimum of a /29 and a maximum of /24. It must also not overlap the AWS reserved ranges. T
        :param description: (experimental) the description used by IPAM to describe the pool.
        :param ipam_scope_id: (experimental) The IPAM Scope Id to use to create the Pool.
        :param name: (experimental) the name used by IPAM to identify the pool.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc6656dde547b7812a67b8afd3478eff13a118f6c465867fdf0e627743454480)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument ipam_scope_id", value=ipam_scope_id, expected_type=type_hints["ipam_scope_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr": cidr,
            "description": description,
            "ipam_scope_id": ipam_scope_id,
            "name": name,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''(experimental) The Cidr range for pools to be created from    eg, 169.254.100.0/27 The cidr must be in the 169.254.0.0/16 range and must be a minimum of a /29 and a maximum of /24.

        It must also not overlap the AWS reserved ranges. T

        :stability: experimental
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''(experimental) the description used by IPAM to describe the pool.

        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ipam_scope_id(self) -> builtins.str:
        '''(experimental) The IPAM Scope Id to use to create the Pool.

        :stability: experimental
        '''
        result = self._values.get("ipam_scope_id")
        assert result is not None, "Required property 'ipam_scope_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) the name used by IPAM to identify the pool.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IpsecTunnelPoolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.ManagedAwsFirewallRules")
class ManagedAwsFirewallRules(enum.Enum):
    '''
    :stability: experimental
    '''

    ABUSED_LEGIT_MALWARE_DOMAINS_ACTION_ORDER = "ABUSED_LEGIT_MALWARE_DOMAINS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    ABUSED_LEGIT_BOTNET_COMMAND_AND_CONTROL_DOMAINS_ACTION_ORDER = "ABUSED_LEGIT_BOTNET_COMMAND_AND_CONTROL_DOMAINS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    MALWARE_DOMAINS_ACTION_ORDER = "MALWARE_DOMAINS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    BOTNET_COMMAND_AND_CONTROL_DOMAINS_ACTION_ORDER = "BOTNET_COMMAND_AND_CONTROL_DOMAINS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_BOTNET_ACTION_ORDER = "THREAT_SIGNATURES_BOTNET_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_BOTNET_WEB_ACTION_ORDER = "THREAT_SIGNATURES_BOTNET_WEB_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_BOTNET_WINDOWS_ACTION_ODER = "THREAT_SIGNATURES_BOTNET_WINDOWS_ACTION_ODER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_DOS_ACTION_ORDER = "THREAT_SIGNATURES_DOS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_EMERGING_EVENTS_ACTION_ORDER = "THREAT_SIGNATURES_EMERGING_EVENTS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_EXPLOITS_ACTION_ORDER = "THREAT_SIGNATURES_EXPLOITS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_FUP_ACTION_ORDER = "THREAT_SIGNATURES_FUP_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_IOC_ACTION_ORDER = "THREAT_SIGNATURES_IOC_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_MALWARE_ACTION_ORDER = "THREAT_SIGNATURES_MALWARE_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_MALWARE_COIN_MINING_ACTION_ORDER = "THREAT_SIGNATURES_MALWARE_COIN_MINING_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_MAWLARE_WEB_ACTION_ORDER = "THREAT_SIGNATURES_MAWLARE_WEB_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_MALWARE_MOBILE_ACTION_ORDER = "THREAT_SIGNATURES_MALWARE_MOBILE_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_PHISHING_ACTION_ORDER = "THREAT_SIGNATURES_PHISHING_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_SCANNERS_ACTION_ORDER = "THREAT_SIGNATURES_SCANNERS_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_SUSPECT_ACTION_ORDER = "THREAT_SIGNATURES_SUSPECT_ACTION_ORDER"
    '''
    :stability: experimental
    '''
    THREAT_SIGNATURES_WEB_ATTACKS_ACTION_ORDER = "THREAT_SIGNATURES_WEB_ATTACKS_ACTION_ORDER"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.NWFWRulesEngine",
    jsii_struct_bases=[],
    name_mapping={
        "firewall_account": "firewallAccount",
        "rules_database": "rulesDatabase",
    },
)
class NWFWRulesEngine:
    def __init__(
        self,
        *,
        firewall_account: builtins.str,
        rules_database: "StatefulRuleDatabase",
    ) -> None:
        '''
        :param firewall_account: 
        :param rules_database: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8a4759ed6da59dfe209afa270ab624cb3b7ed696873d8361484494e28760740)
            check_type(argname="argument firewall_account", value=firewall_account, expected_type=type_hints["firewall_account"])
            check_type(argname="argument rules_database", value=rules_database, expected_type=type_hints["rules_database"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "firewall_account": firewall_account,
            "rules_database": rules_database,
        }

    @builtins.property
    def firewall_account(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("firewall_account")
        assert result is not None, "Required property 'firewall_account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rules_database(self) -> "StatefulRuleDatabase":
        '''
        :stability: experimental
        '''
        result = self._values.get("rules_database")
        assert result is not None, "Required property 'rules_database' is missing"
        return typing.cast("StatefulRuleDatabase", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NWFWRulesEngine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkFirewall(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.NetworkFirewall",
):
    '''(experimental) Creates Network Firewalls.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        firewall_name: builtins.str,
        firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''
        :param scope: Scope.
        :param id: id.
        :param firewall_name: (experimental) the name that will be given to the firewall.
        :param firewall_policy: (experimental) the firewalls policy.
        :param subnet_group: (experimental) the subnetGroup where the firewall will be created.
        :param vpc: (experimental) the the vpc where the Network firewall is placed.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90e35ceefff152d766401263c5496665d99299ecc4a08284c72f966fc3a26061)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NetworkFirewallProps(
            firewall_name=firewall_name,
            firewall_policy=firewall_policy,
            subnet_group=subnet_group,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="endPointIds")
    def end_point_ids(self) -> typing.List[builtins.str]:
        '''(experimental) Gateway Endpoints for the Firewalls.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "endPointIds"))

    @builtins.property
    @jsii.member(jsii_name="firewallArn")
    def firewall_arn(self) -> builtins.str:
        '''(experimental) Arn of the firewall.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallArn"))

    @builtins.property
    @jsii.member(jsii_name="firewallId")
    def firewall_id(self) -> builtins.str:
        '''(experimental) Firewall ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallId"))


@jsii.data_type(
    jsii_type="raindancers-network.NetworkFirewallProps",
    jsii_struct_bases=[],
    name_mapping={
        "firewall_name": "firewallName",
        "firewall_policy": "firewallPolicy",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
    },
)
class NetworkFirewallProps:
    def __init__(
        self,
        *,
        firewall_name: builtins.str,
        firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    ) -> None:
        '''(experimental) Propertys of a Network Firewall.

        :param firewall_name: (experimental) the name that will be given to the firewall.
        :param firewall_policy: (experimental) the firewalls policy.
        :param subnet_group: (experimental) the subnetGroup where the firewall will be created.
        :param vpc: (experimental) the the vpc where the Network firewall is placed.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b952a7d66418ce35108e0ba18fa17ae61dc5002414285789b9fe315d7bbd14)
            check_type(argname="argument firewall_name", value=firewall_name, expected_type=type_hints["firewall_name"])
            check_type(argname="argument firewall_policy", value=firewall_policy, expected_type=type_hints["firewall_policy"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "firewall_name": firewall_name,
            "firewall_policy": firewall_policy,
            "subnet_group": subnet_group,
            "vpc": vpc,
        }

    @builtins.property
    def firewall_name(self) -> builtins.str:
        '''(experimental) the name that will be given to the firewall.

        :stability: experimental
        '''
        result = self._values.get("firewall_name")
        assert result is not None, "Required property 'firewall_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def firewall_policy(
        self,
    ) -> _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy:
        '''(experimental) the firewalls policy.

        :stability: experimental
        '''
        result = self._values.get("firewall_policy")
        assert result is not None, "Required property 'firewall_policy' is missing"
        return typing.cast(_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy, result)

    @builtins.property
    def subnet_group(self) -> builtins.str:
        '''(experimental) the subnetGroup where the firewall will be created.

        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) the the vpc where the Network firewall is placed.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkFirewallProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.Operators")
class Operators(enum.Enum):
    '''(experimental) Operatior COnditons for Attachments.

    :stability: experimental
    '''

    EQUALS = "EQUALS"
    '''
    :stability: experimental
    '''
    NOTEQUALS = "NOTEQUALS"
    '''
    :stability: experimental
    '''
    CONTAINS = "CONTAINS"
    '''
    :stability: experimental
    '''
    BEGINS_WITH = "BEGINS_WITH"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.OutboundForwardingRule",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "forward_to": "forwardTo"},
)
class OutboundForwardingRule:
    def __init__(
        self,
        *,
        domain: builtins.str,
        forward_to: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param domain: (experimental) domain to forward.
        :param forward_to: (experimental) array of ip address's to forward request to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25fb206bba170d97d44c14aa6140b1abeeb3b05e10f9c01397d9333eee473895)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument forward_to", value=forward_to, expected_type=type_hints["forward_to"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "forward_to": forward_to,
        }

    @builtins.property
    def domain(self) -> builtins.str:
        '''(experimental) domain to forward.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def forward_to(self) -> typing.List[builtins.str]:
        '''(experimental) array of ip address's to forward request to.

        :stability: experimental
        '''
        result = self._values.get("forward_to")
        assert result is not None, "Required property 'forward_to' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OutboundForwardingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.OutsideIpAddressType")
class OutsideIpAddressType(enum.Enum):
    '''(experimental) Specify the use of public or private IP address's for Site to Site VPN.

    :stability: experimental
    '''

    PRIVATE = "PRIVATE"
    '''(experimental) Use Private IPv4 Address from the Transit Gateways IP address Pool.

    :stability: experimental
    '''
    PUBLIC = "PUBLIC"
    '''(experimental) Use Public IPv4 Address Assigned by AWS.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.PermissionBoundary",
    jsii_struct_bases=[
        _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.PermissionsBoundaryProperty
    ],
    name_mapping={
        "customer_managed_policy_reference": "customerManagedPolicyReference",
        "managed_policy_arn": "managedPolicyArn",
    },
)
class PermissionBoundary(
    _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.PermissionsBoundaryProperty,
):
    def __init__(
        self,
        *,
        customer_managed_policy_reference: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        managed_policy_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param customer_managed_policy_reference: Specifies the name and path of a customer managed policy. You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set.
        :param managed_policy_arn: The AWS managed policy ARN that you want to attach to a permission set as a permissions boundary.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb1e9939d4c5b3a8591615d5d424abfaa69ffea061adb163568b47041ce8a5f)
            check_type(argname="argument customer_managed_policy_reference", value=customer_managed_policy_reference, expected_type=type_hints["customer_managed_policy_reference"])
            check_type(argname="argument managed_policy_arn", value=managed_policy_arn, expected_type=type_hints["managed_policy_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if customer_managed_policy_reference is not None:
            self._values["customer_managed_policy_reference"] = customer_managed_policy_reference
        if managed_policy_arn is not None:
            self._values["managed_policy_arn"] = managed_policy_arn

    @builtins.property
    def customer_managed_policy_reference(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty]]:
        '''Specifies the name and path of a customer managed policy.

        You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sso-permissionset-permissionsboundary.html#cfn-sso-permissionset-permissionsboundary-customermanagedpolicyreference
        '''
        result = self._values.get("customer_managed_policy_reference")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty]], result)

    @builtins.property
    def managed_policy_arn(self) -> typing.Optional[builtins.str]:
        '''The AWS managed policy ARN that you want to attach to a permission set as a permissions boundary.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sso-permissionset-permissionsboundary.html#cfn-sso-permissionset-permissionsboundary-managedpolicyarn
        '''
        result = self._values.get("managed_policy_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionBoundary(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPermissionSet)
class PermissionSet(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.PermissionSet",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        sso_instance_arn: builtins.str,
        aws_managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        customer_managed_policy_references: typing.Optional[typing.Sequence[typing.Union[CustomerManagedPolicyReference, typing.Dict[builtins.str, typing.Any]]]] = None,
        description: typing.Optional[builtins.str] = None,
        inline_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        permissions_boundary: typing.Optional[typing.Union[PermissionBoundary, typing.Dict[builtins.str, typing.Any]]] = None,
        relay_state_type: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: (experimental) The name of the permission set.
        :param sso_instance_arn: (experimental) The ARN of the SSO instance under which the operation will be executed.
        :param aws_managed_policies: (experimental) The AWS managed policies to attach to the ``PermissionSet``. Default: - No AWS managed policies
        :param customer_managed_policy_references: (experimental) Specifies the names and paths of a customer managed policy. You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set. Default: - No customer managed policies
        :param description: (experimental) The description of the ``PermissionSet``. Default: - No description
        :param inline_policy: (experimental) The IAM inline policy that is attached to the permission set. Default: - No inline policy
        :param permissions_boundary: (experimental) Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary. Specify either customerManagedPolicyReference to use the name and path of a customer managed policy, or managedPolicy to use the ARN of an AWS managed policy. A permissions boundary represents the maximum permissions that any policy can grant your role. For more information, see Permissions boundaries for IAM entities in the AWS Identity and Access Management User Guide. Default: - No permissions boundary
        :param relay_state_type: (experimental) Used to redirect users within the application during the federation authentication process. By default, when a user signs into the AWS access portal, chooses an account, and then chooses the role that AWS creates from the assigned permission set, IAM Identity Center redirects the user’s browser to the AWS Management Console. You can change this behavior by setting the relay state to a different console URL. Setting the relay state enables you to provide the user with quick access to the console that is most appropriate for their role. For example, you can set the relay state to the Amazon EC2 console URL (https://console.aws.amazon.com/ec2/) to redirect the user to that console when they choose the Amazon EC2 administrator role. Default: - No redirection
        :param session_duration: (experimental) The length of time that the application user sessions are valid for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55253cce89aed4d791e68500efad03101987a1350cdc0288c493507ad21311fc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PermissionSetProps(
            name=name,
            sso_instance_arn=sso_instance_arn,
            aws_managed_policies=aws_managed_policies,
            customer_managed_policy_references=customer_managed_policy_references,
            description=description,
            inline_policy=inline_policy,
            permissions_boundary=permissions_boundary,
            relay_state_type=relay_state_type,
            session_duration=session_duration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPermissionSetArn")
    @builtins.classmethod
    def from_permission_set_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        permission_set_arn: builtins.str,
    ) -> IPermissionSet:
        '''(experimental) Reference an existing permission set by ARN.

        :param scope: -
        :param id: -
        :param permission_set_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6b6b6c2440db4f7b8a3cb442c56736e3021a34e9b531a8a1adec0439743d59)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument permission_set_arn", value=permission_set_arn, expected_type=type_hints["permission_set_arn"])
        return typing.cast(IPermissionSet, jsii.sinvoke(cls, "fromPermissionSetArn", [scope, id, permission_set_arn]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        id: builtins.str,
        *,
        principal: typing.Union["PrincipalProperty", typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional["TargetTypes"] = None,
    ) -> "Assignment":
        '''(experimental) Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__868cb80778e19f4cab4d55459564ed396dbd5de0744627121f66f543566be074)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        assignment_options = AssignmentOptions(
            principal=principal, target_id=target_id, target_type=target_type
        )

        return typing.cast("Assignment", jsii.invoke(self, "grant", [id, assignment_options]))

    @builtins.property
    @jsii.member(jsii_name="cfnPermissionSet")
    def cfn_permission_set(self) -> _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet:
        '''(experimental) The underlying CfnPermissionSet resource.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sso_ceddda9d.CfnPermissionSet, jsii.get(self, "cfnPermissionSet"))

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''(experimental) The permission set ARN of the permission set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "permissionSetArn"))

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''(experimental) The SSO instance the permission set belongs to.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ssoInstanceArn"))


@jsii.data_type(
    jsii_type="raindancers-network.PermissionSetAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "permission_set_arn": "permissionSetArn",
        "sso_instance_arn": "ssoInstanceArn",
    },
)
class PermissionSetAttributes:
    def __init__(
        self,
        *,
        permission_set_arn: builtins.str,
        sso_instance_arn: builtins.str,
    ) -> None:
        '''(experimental) Attributes for a permission set.

        :param permission_set_arn: (experimental) The permission set ARN of the permission set. Such as ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.
        :param sso_instance_arn: (experimental) The SSO instance ARN of the permission set.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350881e30013374e8d1acb6de938add1675e4e75ed5513d851cf42784422d7d8)
            check_type(argname="argument permission_set_arn", value=permission_set_arn, expected_type=type_hints["permission_set_arn"])
            check_type(argname="argument sso_instance_arn", value=sso_instance_arn, expected_type=type_hints["sso_instance_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission_set_arn": permission_set_arn,
            "sso_instance_arn": sso_instance_arn,
        }

    @builtins.property
    def permission_set_arn(self) -> builtins.str:
        '''(experimental) The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.

        :stability: experimental
        '''
        result = self._values.get("permission_set_arn")
        assert result is not None, "Required property 'permission_set_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_instance_arn(self) -> builtins.str:
        '''(experimental) The SSO instance ARN of the permission set.

        :stability: experimental
        '''
        result = self._values.get("sso_instance_arn")
        assert result is not None, "Required property 'sso_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionSetAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.PermissionSetProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "sso_instance_arn": "ssoInstanceArn",
        "aws_managed_policies": "awsManagedPolicies",
        "customer_managed_policy_references": "customerManagedPolicyReferences",
        "description": "description",
        "inline_policy": "inlinePolicy",
        "permissions_boundary": "permissionsBoundary",
        "relay_state_type": "relayStateType",
        "session_duration": "sessionDuration",
    },
)
class PermissionSetProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        sso_instance_arn: builtins.str,
        aws_managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        customer_managed_policy_references: typing.Optional[typing.Sequence[typing.Union[CustomerManagedPolicyReference, typing.Dict[builtins.str, typing.Any]]]] = None,
        description: typing.Optional[builtins.str] = None,
        inline_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        permissions_boundary: typing.Optional[typing.Union[PermissionBoundary, typing.Dict[builtins.str, typing.Any]]] = None,
        relay_state_type: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The properties of a new permission set.

        :param name: (experimental) The name of the permission set.
        :param sso_instance_arn: (experimental) The ARN of the SSO instance under which the operation will be executed.
        :param aws_managed_policies: (experimental) The AWS managed policies to attach to the ``PermissionSet``. Default: - No AWS managed policies
        :param customer_managed_policy_references: (experimental) Specifies the names and paths of a customer managed policy. You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set. Default: - No customer managed policies
        :param description: (experimental) The description of the ``PermissionSet``. Default: - No description
        :param inline_policy: (experimental) The IAM inline policy that is attached to the permission set. Default: - No inline policy
        :param permissions_boundary: (experimental) Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary. Specify either customerManagedPolicyReference to use the name and path of a customer managed policy, or managedPolicy to use the ARN of an AWS managed policy. A permissions boundary represents the maximum permissions that any policy can grant your role. For more information, see Permissions boundaries for IAM entities in the AWS Identity and Access Management User Guide. Default: - No permissions boundary
        :param relay_state_type: (experimental) Used to redirect users within the application during the federation authentication process. By default, when a user signs into the AWS access portal, chooses an account, and then chooses the role that AWS creates from the assigned permission set, IAM Identity Center redirects the user’s browser to the AWS Management Console. You can change this behavior by setting the relay state to a different console URL. Setting the relay state enables you to provide the user with quick access to the console that is most appropriate for their role. For example, you can set the relay state to the Amazon EC2 console URL (https://console.aws.amazon.com/ec2/) to redirect the user to that console when they choose the Amazon EC2 administrator role. Default: - No redirection
        :param session_duration: (experimental) The length of time that the application user sessions are valid for.

        :stability: experimental
        '''
        if isinstance(permissions_boundary, dict):
            permissions_boundary = PermissionBoundary(**permissions_boundary)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a171a9c43dcfb724cd216f311b8aa6bfa79e5b715facf56cb81f9a24d48f300)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument sso_instance_arn", value=sso_instance_arn, expected_type=type_hints["sso_instance_arn"])
            check_type(argname="argument aws_managed_policies", value=aws_managed_policies, expected_type=type_hints["aws_managed_policies"])
            check_type(argname="argument customer_managed_policy_references", value=customer_managed_policy_references, expected_type=type_hints["customer_managed_policy_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument inline_policy", value=inline_policy, expected_type=type_hints["inline_policy"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument relay_state_type", value=relay_state_type, expected_type=type_hints["relay_state_type"])
            check_type(argname="argument session_duration", value=session_duration, expected_type=type_hints["session_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "sso_instance_arn": sso_instance_arn,
        }
        if aws_managed_policies is not None:
            self._values["aws_managed_policies"] = aws_managed_policies
        if customer_managed_policy_references is not None:
            self._values["customer_managed_policy_references"] = customer_managed_policy_references
        if description is not None:
            self._values["description"] = description
        if inline_policy is not None:
            self._values["inline_policy"] = inline_policy
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if relay_state_type is not None:
            self._values["relay_state_type"] = relay_state_type
        if session_duration is not None:
            self._values["session_duration"] = session_duration

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the permission set.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the SSO instance under which the operation will be executed.

        :stability: experimental
        '''
        result = self._values.get("sso_instance_arn")
        assert result is not None, "Required property 'sso_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''(experimental) The AWS managed policies to attach to the ``PermissionSet``.

        :default: - No AWS managed policies

        :stability: experimental
        '''
        result = self._values.get("aws_managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def customer_managed_policy_references(
        self,
    ) -> typing.Optional[typing.List[CustomerManagedPolicyReference]]:
        '''(experimental) Specifies the names and paths of a customer managed policy.

        You must have an IAM policy that matches the name and path in each
        AWS account where you want to deploy your permission set.

        :default: - No customer managed policies

        :stability: experimental
        '''
        result = self._values.get("customer_managed_policy_references")
        return typing.cast(typing.Optional[typing.List[CustomerManagedPolicyReference]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the ``PermissionSet``.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inline_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM inline policy that is attached to the permission set.

        :default: - No inline policy

        :stability: experimental
        '''
        result = self._values.get("inline_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def permissions_boundary(self) -> typing.Optional[PermissionBoundary]:
        '''(experimental) Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary.

        Specify either
        customerManagedPolicyReference to use the name and path of a customer
        managed policy, or managedPolicy to use the ARN of an AWS managed
        policy.

        A permissions boundary represents the maximum permissions that any
        policy can grant your role. For more information, see Permissions boundaries
        for IAM entities in the AWS Identity and Access Management User Guide.

        :default: - No permissions boundary

        :see: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        :stability: experimental
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[PermissionBoundary], result)

    @builtins.property
    def relay_state_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used to redirect users within the application during the federation authentication process.

        By default, when a user signs into the AWS access portal, chooses an account,
        and then chooses the role that AWS creates from the assigned permission set,
        IAM Identity Center redirects the user’s browser to the AWS Management Console.

        You can change this behavior by setting the relay state to a different console
        URL. Setting the relay state enables you to provide the user with quick access
        to the console that is most appropriate for their role. For example, you can
        set the relay state to the Amazon EC2 console URL (https://console.aws.amazon.com/ec2/)
        to redirect the user to that console when they choose the Amazon EC2
        administrator role.

        :default: - No redirection

        :see: https://docs.aws.amazon.com/singlesignon/latest/userguide/howtopermrelaystate.html
        :stability: experimental
        '''
        result = self._values.get("relay_state_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The length of time that the application user sessions are valid for.

        :stability: experimental
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PermissionSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.Phase1DHGroupNumbers")
class Phase1DHGroupNumbers(enum.Enum):
    '''
    :stability: experimental
    '''

    DH2 = "DH2"
    '''
    :stability: experimental
    '''
    DH14 = "DH14"
    '''
    :stability: experimental
    '''
    DH15 = "DH15"
    '''
    :stability: experimental
    '''
    DH16 = "DH16"
    '''
    :stability: experimental
    '''
    DH17 = "DH17"
    '''
    :stability: experimental
    '''
    DH18 = "DH18"
    '''
    :stability: experimental
    '''
    DH19 = "DH19"
    '''
    :stability: experimental
    '''
    DH20 = "DH20"
    '''
    :stability: experimental
    '''
    DH21 = "DH21"
    '''
    :stability: experimental
    '''
    DH22 = "DH22"
    '''
    :stability: experimental
    '''
    DH23 = "DH23"
    '''
    :stability: experimental
    '''
    DH24 = "DH24"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Phase1EncryptionAlgorithms")
class Phase1EncryptionAlgorithms(enum.Enum):
    '''
    :stability: experimental
    '''

    AES128 = "AES128"
    '''
    :stability: experimental
    '''
    AES256 = "AES256"
    '''
    :stability: experimental
    '''
    AES128_GCM_16 = "AES128_GCM_16"
    '''
    :stability: experimental
    '''
    AES256_GCM_16 = "AES256_GCM_16"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Phase1IntegrityAlgorithms")
class Phase1IntegrityAlgorithms(enum.Enum):
    '''
    :stability: experimental
    '''

    SHA1 = "SHA1"
    '''
    :stability: experimental
    '''
    SHA2_256 = "SHA2_256"
    '''
    :stability: experimental
    '''
    SHA2_384 = "SHA2_384"
    '''
    :stability: experimental
    '''
    SHA2_512 = "SHA2_512"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Phase2DHGroupNumbers")
class Phase2DHGroupNumbers(enum.Enum):
    '''
    :stability: experimental
    '''

    DH2 = "DH2"
    '''
    :stability: experimental
    '''
    DH5 = "DH5"
    '''
    :stability: experimental
    '''
    DH14 = "DH14"
    '''
    :stability: experimental
    '''
    DH15 = "DH15"
    '''
    :stability: experimental
    '''
    DH16 = "DH16"
    '''
    :stability: experimental
    '''
    DH17 = "DH17"
    '''
    :stability: experimental
    '''
    DH18 = "DH18"
    '''
    :stability: experimental
    '''
    DH19 = "DH19"
    '''
    :stability: experimental
    '''
    DH20 = "DH20"
    '''
    :stability: experimental
    '''
    DH21 = "DH21"
    '''
    :stability: experimental
    '''
    DH22 = "DH22"
    '''
    :stability: experimental
    '''
    DH23 = "DH23"
    '''
    :stability: experimental
    '''
    DH24 = "DH24"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Phase2EncryptionAlgorithms")
class Phase2EncryptionAlgorithms(enum.Enum):
    '''
    :stability: experimental
    '''

    AES128 = "AES128"
    '''
    :stability: experimental
    '''
    AES256 = "AES256"
    '''
    :stability: experimental
    '''
    AES128_GCM_16 = "AES128_GCM_16"
    '''
    :stability: experimental
    '''
    AES256_GCM_16 = "AES256_GCM_16"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.Phase2IntegrityAlgorithms")
class Phase2IntegrityAlgorithms(enum.Enum):
    '''
    :stability: experimental
    '''

    SHA1 = "SHA1"
    '''
    :stability: experimental
    '''
    SHA2_256 = "SHA2_256"
    '''
    :stability: experimental
    '''
    SHA2_384 = "SHA2_384"
    '''
    :stability: experimental
    '''
    SHA2_512 = "SHA2_512"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.PowerBIGateway",
    jsii_struct_bases=[],
    name_mapping={
        "cfg_secret_arn": "cfgSecretArn",
        "hostname": "hostname",
        "instancetype": "instancetype",
    },
)
class PowerBIGateway:
    def __init__(
        self,
        *,
        cfg_secret_arn: builtins.str,
        hostname: builtins.str,
        instancetype: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    ) -> None:
        '''
        :param cfg_secret_arn: 
        :param hostname: 
        :param instancetype: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1027a4c14c05a475930afecf6876d01e3fbe3447efb9f4e196f1030fa725ad2d)
            check_type(argname="argument cfg_secret_arn", value=cfg_secret_arn, expected_type=type_hints["cfg_secret_arn"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument instancetype", value=instancetype, expected_type=type_hints["instancetype"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cfg_secret_arn": cfg_secret_arn,
            "hostname": hostname,
            "instancetype": instancetype,
        }

    @builtins.property
    def cfg_secret_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cfg_secret_arn")
        assert result is not None, "Required property 'cfg_secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instancetype(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''
        :stability: experimental
        '''
        result = self._values.get("instancetype")
        assert result is not None, "Required property 'instancetype' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PowerBIGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PowerBIGatewayZoo(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.PowerBIGatewayZoo",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        deploy_assets_path: builtins.str,
        gateways: typing.Sequence[typing.Union[PowerBIGateway, typing.Dict[builtins.str, typing.Any]]],
        initscript: builtins.str,
        r53zone_id: builtins.str,
        subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
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
        :param deploy_assets_path: 
        :param gateways: 
        :param initscript: 
        :param r53zone_id: 
        :param subnet: 
        :param vpc: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f89944edffc01c967540f85f7ac38259e4b21036b25b5012f0aad955b75c8fd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PowerBIGatewayZooProps(
            deploy_assets_path=deploy_assets_path,
            gateways=gateways,
            initscript=initscript,
            r53zone_id=r53zone_id,
            subnet=subnet,
            vpc=vpc,
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


@jsii.data_type(
    jsii_type="raindancers-network.PowerBIGatewayZooProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
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
        "deploy_assets_path": "deployAssetsPath",
        "gateways": "gateways",
        "initscript": "initscript",
        "r53zone_id": "r53zoneID",
        "subnet": "subnet",
        "vpc": "vpc",
    },
)
class PowerBIGatewayZooProps(_aws_cdk_ceddda9d.StackProps):
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
        deploy_assets_path: builtins.str,
        gateways: typing.Sequence[typing.Union[PowerBIGateway, typing.Dict[builtins.str, typing.Any]]],
        initscript: builtins.str,
        r53zone_id: builtins.str,
        subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
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
        :param deploy_assets_path: 
        :param gateways: 
        :param initscript: 
        :param r53zone_id: 
        :param subnet: 
        :param vpc: 

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if isinstance(subnet, dict):
            subnet = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90fb8c74ac7da5988587941a44a3c862f5cab40e8f8d8b3800e3bae005c7a96d)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument deploy_assets_path", value=deploy_assets_path, expected_type=type_hints["deploy_assets_path"])
            check_type(argname="argument gateways", value=gateways, expected_type=type_hints["gateways"])
            check_type(argname="argument initscript", value=initscript, expected_type=type_hints["initscript"])
            check_type(argname="argument r53zone_id", value=r53zone_id, expected_type=type_hints["r53zone_id"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deploy_assets_path": deploy_assets_path,
            "gateways": gateways,
            "initscript": initscript,
            "r53zone_id": r53zone_id,
            "subnet": subnet,
            "vpc": vpc,
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
    def deploy_assets_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("deploy_assets_path")
        assert result is not None, "Required property 'deploy_assets_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateways(self) -> typing.List[PowerBIGateway]:
        '''
        :stability: experimental
        '''
        result = self._values.get("gateways")
        assert result is not None, "Required property 'gateways' is missing"
        return typing.cast(typing.List[PowerBIGateway], result)

    @builtins.property
    def initscript(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("initscript")
        assert result is not None, "Required property 'initscript' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def r53zone_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("r53zone_id")
        assert result is not None, "Required property 'r53zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet")
        assert result is not None, "Required property 'subnet' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(
        self,
    ) -> typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PowerBIGatewayZooProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PowerBiGateway(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.PowerBiGateway",
):
    '''(experimental) * Creates an Instance of a Power BI Gateway.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cfg_secret: typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret],
        hostname: builtins.str,
        initscript: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.WindowsImage,
        power_b_igateway_setup_script: typing.Union[_aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions, typing.Dict[builtins.str, typing.Any]],
        subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
        zone: typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cfg_secret: 
        :param hostname: 
        :param initscript: 
        :param instance_type: 
        :param machine_image: 
        :param power_b_igateway_setup_script: 
        :param subnet: 
        :param vpc: 
        :param zone: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f169631dc3f57446cf71bb645416a8b2fee1b90ba4c396b0f77b600a2cf29bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PowerBiGatewayProps(
            cfg_secret=cfg_secret,
            hostname=hostname,
            initscript=initscript,
            instance_type=instance_type,
            machine_image=machine_image,
            power_b_igateway_setup_script=power_b_igateway_setup_script,
            subnet=subnet,
            vpc=vpc,
            zone=zone,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addEgressRule")
    def add_egress_rule(
        self,
        peer: _aws_cdk_aws_ec2_ceddda9d.IPeer,
        connection: _aws_cdk_aws_ec2_ceddda9d.Port,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param peer: -
        :param connection: -
        :param description: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__329a72072a289b2419e9e9d6bc8e1677899a79f28543dcb5b4550781bc9b657c)
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast(None, jsii.invoke(self, "addEgressRule", [peer, connection, description]))

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> _aws_cdk_aws_ec2_ceddda9d.Instance:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Instance, jsii.get(self, "instance"))


@jsii.data_type(
    jsii_type="raindancers-network.PowerBiGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "cfg_secret": "cfgSecret",
        "hostname": "hostname",
        "initscript": "initscript",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "power_b_igateway_setup_script": "powerBIgatewaySetupScript",
        "subnet": "subnet",
        "vpc": "vpc",
        "zone": "zone",
    },
)
class PowerBiGatewayProps:
    def __init__(
        self,
        *,
        cfg_secret: typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret],
        hostname: builtins.str,
        initscript: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.WindowsImage,
        power_b_igateway_setup_script: typing.Union[_aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions, typing.Dict[builtins.str, typing.Any]],
        subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
        zone: typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone],
    ) -> None:
        '''
        :param cfg_secret: 
        :param hostname: 
        :param initscript: 
        :param instance_type: 
        :param machine_image: 
        :param power_b_igateway_setup_script: 
        :param subnet: 
        :param vpc: 
        :param zone: 

        :stability: experimental
        '''
        if isinstance(power_b_igateway_setup_script, dict):
            power_b_igateway_setup_script = _aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions(**power_b_igateway_setup_script)
        if isinstance(subnet, dict):
            subnet = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6695eb397954dd29a8cdb2221d08682e5bb89ef4d00d2f48a43ab1953e3c830)
            check_type(argname="argument cfg_secret", value=cfg_secret, expected_type=type_hints["cfg_secret"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument initscript", value=initscript, expected_type=type_hints["initscript"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
            check_type(argname="argument power_b_igateway_setup_script", value=power_b_igateway_setup_script, expected_type=type_hints["power_b_igateway_setup_script"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cfg_secret": cfg_secret,
            "hostname": hostname,
            "initscript": initscript,
            "instance_type": instance_type,
            "machine_image": machine_image,
            "power_b_igateway_setup_script": power_b_igateway_setup_script,
            "subnet": subnet,
            "vpc": vpc,
            "zone": zone,
        }

    @builtins.property
    def cfg_secret(
        self,
    ) -> typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cfg_secret")
        assert result is not None, "Required property 'cfg_secret' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret], result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def initscript(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("initscript")
        assert result is not None, "Required property 'initscript' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def machine_image(self) -> _aws_cdk_aws_ec2_ceddda9d.WindowsImage:
        '''
        :stability: experimental
        '''
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.WindowsImage, result)

    @builtins.property
    def power_b_igateway_setup_script(
        self,
    ) -> _aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions:
        '''
        :stability: experimental
        '''
        result = self._values.get("power_b_igateway_setup_script")
        assert result is not None, "Required property 'power_b_igateway_setup_script' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions, result)

    @builtins.property
    def subnet(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet")
        assert result is not None, "Required property 'subnet' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(
        self,
    ) -> typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    @builtins.property
    def zone(
        self,
    ) -> typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone]:
        '''
        :stability: experimental
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PowerBiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.PrefixCidr",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr"},
)
class PrefixCidr:
    def __init__(self, *, cidr: builtins.str) -> None:
        '''
        :param cidr: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed8b8c6139156db2a5c5a13578d5f943fdaec6daac0c2da4516a1dd3451486b)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr": cidr,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrefixCidr(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrefixList(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.PrefixList",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address_family: IPAddressFamily,
        max_entries: jsii.Number,
        prefix_list_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param address_family: 
        :param max_entries: 
        :param prefix_list_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd452c9798c65e7389eec7752fffd8000fafdfff9d32ae97511b6850d0d22257)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PrefixListProps(
            address_family=address_family,
            max_entries=max_entries,
            prefix_list_name=prefix_list_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addEC2Instance")
    def add_ec2_instance(self, props: _aws_cdk_aws_ec2_ceddda9d.Instance) -> None:
        '''
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd9e5fb6cfe99ba47d1330567500f1c9c1dafc2a1a646ab68c81600d9d05a82)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(None, jsii.invoke(self, "addEC2Instance", [props]))

    @builtins.property
    @jsii.member(jsii_name="prefixlist")
    def prefixlist(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnPrefixList:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnPrefixList, jsii.get(self, "prefixlist"))

    @builtins.property
    @jsii.member(jsii_name="prefixlistArn")
    def prefixlist_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "prefixlistArn"))

    @builtins.property
    @jsii.member(jsii_name="prefixListSet")
    def prefix_list_set(self) -> "PrefixListSetInterface":
        '''
        :stability: experimental
        '''
        return typing.cast("PrefixListSetInterface", jsii.get(self, "prefixListSet"))


@jsii.data_type(
    jsii_type="raindancers-network.PrefixListEntry",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr", "description": "description"},
)
class PrefixListEntry:
    def __init__(self, *, cidr: builtins.str, description: builtins.str) -> None:
        '''
        :param cidr: 
        :param description: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66aa03a563701be1ff651f509dd8a52a57e90dd19e274fa135b8f4867ee095f4)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr": cidr,
            "description": description,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrefixListEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.PrefixListProps",
    jsii_struct_bases=[],
    name_mapping={
        "address_family": "addressFamily",
        "max_entries": "maxEntries",
        "prefix_list_name": "prefixListName",
    },
)
class PrefixListProps:
    def __init__(
        self,
        *,
        address_family: IPAddressFamily,
        max_entries: jsii.Number,
        prefix_list_name: builtins.str,
    ) -> None:
        '''
        :param address_family: 
        :param max_entries: 
        :param prefix_list_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73be9a6a017476bdafa3665c291260be5699d37d6b298ca08f9de3c23a8a035f)
            check_type(argname="argument address_family", value=address_family, expected_type=type_hints["address_family"])
            check_type(argname="argument max_entries", value=max_entries, expected_type=type_hints["max_entries"])
            check_type(argname="argument prefix_list_name", value=prefix_list_name, expected_type=type_hints["prefix_list_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address_family": address_family,
            "max_entries": max_entries,
            "prefix_list_name": prefix_list_name,
        }

    @builtins.property
    def address_family(self) -> IPAddressFamily:
        '''
        :stability: experimental
        '''
        result = self._values.get("address_family")
        assert result is not None, "Required property 'address_family' is missing"
        return typing.cast(IPAddressFamily, result)

    @builtins.property
    def max_entries(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_entries")
        assert result is not None, "Required property 'max_entries' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def prefix_list_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("prefix_list_name")
        assert result is not None, "Required property 'prefix_list_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrefixListProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.PrefixListSetInterface",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "name": "name"},
)
class PrefixListSetInterface:
    def __init__(self, *, arn: builtins.str, name: builtins.str) -> None:
        '''
        :param arn: 
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04a6d3404c490595e939d5192d36f2b2b5867056ea39ecec90d8b47a6208f500)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arn": arn,
            "name": name,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrefixListSetInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.PrincipalProperty",
    jsii_struct_bases=[],
    name_mapping={"principal_id": "principalId", "principal_type": "principalType"},
)
class PrincipalProperty:
    def __init__(
        self,
        *,
        principal_id: builtins.str,
        principal_type: "PrincipalTypes",
    ) -> None:
        '''
        :param principal_id: (experimental) The id of the principal.
        :param principal_type: (experimental) The type of the principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e48335e433f0f57ed6b1186775e793bbfd33327a5e3146e1ff9e4663d50e7f6)
            check_type(argname="argument principal_id", value=principal_id, expected_type=type_hints["principal_id"])
            check_type(argname="argument principal_type", value=principal_type, expected_type=type_hints["principal_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "principal_id": principal_id,
            "principal_type": principal_type,
        }

    @builtins.property
    def principal_id(self) -> builtins.str:
        '''(experimental) The id of the principal.

        :stability: experimental
        '''
        result = self._values.get("principal_id")
        assert result is not None, "Required property 'principal_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal_type(self) -> "PrincipalTypes":
        '''(experimental) The type of the principal.

        :stability: experimental
        '''
        result = self._values.get("principal_type")
        assert result is not None, "Required property 'principal_type' is missing"
        return typing.cast("PrincipalTypes", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrincipalProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.PrincipalTypes")
class PrincipalTypes(enum.Enum):
    '''
    :stability: experimental
    '''

    USER = "USER"
    '''
    :stability: experimental
    '''
    GROUP = "GROUP"
    '''
    :stability: experimental
    '''


class PrivateRedshiftCluster(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.PrivateRedshiftCluster",
):
    '''(experimental) * Creates a PrivateRedShiftCluster.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        defaultrole: _aws_cdk_aws_iam_ceddda9d.Role,
        logging: typing.Union[_aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties, typing.Dict[builtins.str, typing.Any]],
        master_user: builtins.str,
        subnet_group: _aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup,
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
        default_db_name: typing.Optional[builtins.str] = None,
        nodes: typing.Optional[jsii.Number] = None,
        node_type: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_name: 
        :param defaultrole: 
        :param logging: 
        :param master_user: 
        :param subnet_group: 
        :param vpc: 
        :param default_db_name: 
        :param nodes: 
        :param node_type: 
        :param parameter_group: 
        :param preferred_maintenance_window: 
        :param removal_policy: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbcee769a1d537b4d2fab00f60f7cb0fa2d3b46cee3a33ffbe164ede042cbf5a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftClusterProps(
            cluster_name=cluster_name,
            defaultrole=defaultrole,
            logging=logging,
            master_user=master_user,
            subnet_group=subnet_group,
            vpc=vpc,
            default_db_name=default_db_name,
            nodes=nodes,
            node_type=node_type,
            parameter_group=parameter_group,
            preferred_maintenance_window=preferred_maintenance_window,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDatabase")
    def add_database(self, database_name: builtins.str) -> "RedShiftDatabase":
        '''
        :param database_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0980a865118e1af6aeeccee986b2101b76fbf35d5847e3615bd01e37ac8d292)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
        return typing.cast("RedShiftDatabase", jsii.invoke(self, "addDatabase", [database_name]))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.Cluster:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.Cluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="clusterParameters")
    def cluster_parameters(
        self,
    ) -> _aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup, jsii.get(self, "clusterParameters"))

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroup")
    def cluster_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.get(self, "clusterSecurityGroup"))


@jsii.enum(jsii_type="raindancers-network.Protocol")
class Protocol(enum.Enum):
    '''
    :stability: experimental
    '''

    ICMP = "ICMP"
    '''
    :stability: experimental
    '''
    TCP = "TCP"
    '''
    :stability: experimental
    '''
    UDP = "UDP"
    '''
    :stability: experimental
    '''


class R53Resolverendpoints(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.R53Resolverendpoints",
):
    '''(experimental) Create Route53 Resolver Endpoints for MultiVPC and Hybrid DNS Resolution.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        outbound_forwarding_rules: typing.Optional[typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: the scope in which these resources are craeted.
        :param id: the id of the construct.
        :param subnet_group: (experimental) the subnetgroup to place the resolvers in.
        :param vpc: (experimental) the vpc that the resolvers will be placed in.
        :param outbound_forwarding_rules: (experimental) An array of Internal domains that can be centrally resolved in this VPC.
        :param tag_value: (experimental) Value for Sharing.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5939847c42b4e20cba48915b9f96f0f0d824de99a9019d739a6e1c6ad418d1e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = R53ResolverendpointsProps(
            subnet_group=subnet_group,
            vpc=vpc,
            outbound_forwarding_rules=outbound_forwarding_rules,
            tag_value=tag_value,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="inboundResolver")
    def inbound_resolver(
        self,
    ) -> _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint:
        '''(experimental) inbound resolver.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint, jsii.get(self, "inboundResolver"))

    @inbound_resolver.setter
    def inbound_resolver(
        self,
        value: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0369cb0b1f59bc4e06d601fab9254ebc6b2159106022fcbda4d604f4433c0ff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inboundResolver", value)

    @builtins.property
    @jsii.member(jsii_name="inboundResolversIp")
    def inbound_resolvers_ip(
        self,
    ) -> typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty]:
        '''(experimental) list of Resolver IP address's.

        :stability: experimental
        '''
        return typing.cast(typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty], jsii.get(self, "inboundResolversIp"))

    @inbound_resolvers_ip.setter
    def inbound_resolvers_ip(
        self,
        value: typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6123ccfa405042dde0c23c0993ab98efa9931b16d86a50970750d05dfc7e257b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inboundResolversIp", value)

    @builtins.property
    @jsii.member(jsii_name="outboundResolver")
    def outbound_resolver(
        self,
    ) -> _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint:
        '''(experimental) outbound resolver.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint, jsii.get(self, "outboundResolver"))

    @outbound_resolver.setter
    def outbound_resolver(
        self,
        value: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1094063679b17844a9a6bcbe59a18404a43b7557089a05a073489984270839d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outboundResolver", value)


@jsii.data_type(
    jsii_type="raindancers-network.R53ResolverendpointsProps",
    jsii_struct_bases=[],
    name_mapping={
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "outbound_forwarding_rules": "outboundForwardingRules",
        "tag_value": "tagValue",
    },
)
class R53ResolverendpointsProps:
    def __init__(
        self,
        *,
        subnet_group: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
        outbound_forwarding_rules: typing.Optional[typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties to for creating inbound resolvers.

        :param subnet_group: (experimental) the subnetgroup to place the resolvers in.
        :param vpc: (experimental) the vpc that the resolvers will be placed in.
        :param outbound_forwarding_rules: (experimental) An array of Internal domains that can be centrally resolved in this VPC.
        :param tag_value: (experimental) Value for Sharing.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf9a82844ec5ad8d302b61f22d9cd750ccadddd49debf38ba279dadb7aea52a)
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument outbound_forwarding_rules", value=outbound_forwarding_rules, expected_type=type_hints["outbound_forwarding_rules"])
            check_type(argname="argument tag_value", value=tag_value, expected_type=type_hints["tag_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subnet_group": subnet_group,
            "vpc": vpc,
        }
        if outbound_forwarding_rules is not None:
            self._values["outbound_forwarding_rules"] = outbound_forwarding_rules
        if tag_value is not None:
            self._values["tag_value"] = tag_value

    @builtins.property
    def subnet_group(self) -> builtins.str:
        '''(experimental) the subnetgroup to place the resolvers in.

        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.Vpc:
        '''(experimental) the vpc that the resolvers will be placed in.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Vpc, result)

    @builtins.property
    def outbound_forwarding_rules(
        self,
    ) -> typing.Optional[typing.List[OutboundForwardingRule]]:
        '''(experimental) An array of Internal domains that can be centrally resolved in this VPC.

        :stability: experimental
        '''
        result = self._values.get("outbound_forwarding_rules")
        return typing.cast(typing.Optional[typing.List[OutboundForwardingRule]], result)

    @builtins.property
    def tag_value(self) -> typing.Optional[builtins.str]:
        '''(experimental) Value for Sharing.

        :stability: experimental
        '''
        result = self._values.get("tag_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "R53ResolverendpointsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedShiftDatabase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.RedShiftDatabase",
):
    '''(experimental) Create a Database in a Redshift Cluster.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_redshift_alpha_9727f5af.Cluster,
        database_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) which cluster will the database be created in.
        :param database_name: (experimental) A name for the database.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a94085e26e1c181a1169470d94a3f4635801196f4889342d7a947eadab7736f8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedShiftDatabaseProps(cluster=cluster, database_name=database_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="executeSQLStatement")
    def execute_sql_statement(
        self,
        statement_name: builtins.str,
        sql: builtins.str,
    ) -> None:
        '''
        :param statement_name: -
        :param sql: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed403af7888b8b244abfc4d114767dba92ef07c6f6a7ec224f12ffde7cbc6e4c)
            check_type(argname="argument statement_name", value=statement_name, expected_type=type_hints["statement_name"])
            check_type(argname="argument sql", value=sql, expected_type=type_hints["sql"])
        return typing.cast(None, jsii.invoke(self, "executeSQLStatement", [statement_name, sql]))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.Cluster:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.Cluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))


@jsii.data_type(
    jsii_type="raindancers-network.RedShiftDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "database_name": "databaseName"},
)
class RedShiftDatabaseProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_redshift_alpha_9727f5af.Cluster,
        database_name: builtins.str,
    ) -> None:
        '''
        :param cluster: (experimental) which cluster will the database be created in.
        :param database_name: (experimental) A name for the database.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00f4d0ab27b59fa94ebfe40cf8702cd39810625b3e7b24306718a70240c28e56)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "database_name": database_name,
        }

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.Cluster:
        '''(experimental) which cluster will the database be created in.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.Cluster, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''(experimental) A name for the database.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedShiftDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.RedshiftClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "defaultrole": "defaultrole",
        "logging": "logging",
        "master_user": "masterUser",
        "subnet_group": "subnetGroup",
        "vpc": "vpc",
        "default_db_name": "defaultDBName",
        "nodes": "nodes",
        "node_type": "nodeType",
        "parameter_group": "parameterGroup",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "removal_policy": "removalPolicy",
    },
)
class RedshiftClusterProps:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        defaultrole: _aws_cdk_aws_iam_ceddda9d.Role,
        logging: typing.Union[_aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties, typing.Dict[builtins.str, typing.Any]],
        master_user: builtins.str,
        subnet_group: _aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup,
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
        default_db_name: typing.Optional[builtins.str] = None,
        nodes: typing.Optional[jsii.Number] = None,
        node_type: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType] = None,
        parameter_group: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    ) -> None:
        '''
        :param cluster_name: 
        :param defaultrole: 
        :param logging: 
        :param master_user: 
        :param subnet_group: 
        :param vpc: 
        :param default_db_name: 
        :param nodes: 
        :param node_type: 
        :param parameter_group: 
        :param preferred_maintenance_window: 
        :param removal_policy: 

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = _aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties(**logging)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d07540578e6bf37b490f27feaf7c00b4f8d737adec44321a91b208ccda9cd72)
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument defaultrole", value=defaultrole, expected_type=type_hints["defaultrole"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument master_user", value=master_user, expected_type=type_hints["master_user"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument default_db_name", value=default_db_name, expected_type=type_hints["default_db_name"])
            check_type(argname="argument nodes", value=nodes, expected_type=type_hints["nodes"])
            check_type(argname="argument node_type", value=node_type, expected_type=type_hints["node_type"])
            check_type(argname="argument parameter_group", value=parameter_group, expected_type=type_hints["parameter_group"])
            check_type(argname="argument preferred_maintenance_window", value=preferred_maintenance_window, expected_type=type_hints["preferred_maintenance_window"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
            "defaultrole": defaultrole,
            "logging": logging,
            "master_user": master_user,
            "subnet_group": subnet_group,
            "vpc": vpc,
        }
        if default_db_name is not None:
            self._values["default_db_name"] = default_db_name
        if nodes is not None:
            self._values["nodes"] = nodes
        if node_type is not None:
            self._values["node_type"] = node_type
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def defaultrole(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        result = self._values.get("defaultrole")
        assert result is not None, "Required property 'defaultrole' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    @builtins.property
    def logging(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties:
        '''
        :stability: experimental
        '''
        result = self._values.get("logging")
        assert result is not None, "Required property 'logging' is missing"
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties, result)

    @builtins.property
    def master_user(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("master_user")
        assert result is not None, "Required property 'master_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_group(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup, result)

    @builtins.property
    def vpc(
        self,
    ) -> typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    @builtins.property
    def default_db_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("default_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nodes(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def node_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType], result)

    @builtins.property
    def parameter_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''
        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.ReferenceSet",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "name": "name"},
)
class ReferenceSet:
    def __init__(self, *, arn: builtins.str, name: builtins.str) -> None:
        '''
        :param arn: 
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72740c4c9691cb3c03ad9b89a24bedbec9c531d0d6601102d87cb5da92f4dcba)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arn": arn,
            "name": name,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReferenceSet(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResolveSubnetGroupName(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.ResolveSubnetGroupName",
):
    '''(experimental) Creates a period task to update the SSM Agent on an EC2 Instance.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        azcount: jsii.Number,
        subnet_group_name: builtins.str,
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param azcount: 
        :param subnet_group_name: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072ec932aab97c6d455caaf1abbe5d9e3a53b60498ad53c19b2aee522591a016)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ResolveSubnetGroupNameProps(
            azcount=azcount, subnet_group_name=subnet_group_name, vpc=vpc
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="subnetSelection")
    def subnet_selection(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, jsii.get(self, "subnetSelection"))

    @subnet_selection.setter
    def subnet_selection(
        self,
        value: _aws_cdk_aws_ec2_ceddda9d.SubnetSelection,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa629fb86827eb17d4022f193cea09663e900e4be57501176c3da5238b16ea68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetSelection", value)


@jsii.data_type(
    jsii_type="raindancers-network.ResolveSubnetGroupNameProps",
    jsii_struct_bases=[],
    name_mapping={
        "azcount": "azcount",
        "subnet_group_name": "subnetGroupName",
        "vpc": "vpc",
    },
)
class ResolveSubnetGroupNameProps:
    def __init__(
        self,
        *,
        azcount: jsii.Number,
        subnet_group_name: builtins.str,
        vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    ) -> None:
        '''
        :param azcount: 
        :param subnet_group_name: 
        :param vpc: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8799ad0de50ad6006207cdb2d841dbf7fa28646d70c3dcaa7b0a8bc26f4a726a)
            check_type(argname="argument azcount", value=azcount, expected_type=type_hints["azcount"])
            check_type(argname="argument subnet_group_name", value=subnet_group_name, expected_type=type_hints["subnet_group_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "azcount": azcount,
            "subnet_group_name": subnet_group_name,
            "vpc": vpc,
        }

    @builtins.property
    def azcount(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("azcount")
        assert result is not None, "Required property 'azcount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def subnet_group_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_group_name")
        assert result is not None, "Required property 'subnet_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(
        self,
    ) -> typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResolveSubnetGroupNameProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.ResolverDirection")
class ResolverDirection(enum.Enum):
    '''(experimental) Direction of Resolver.

    :stability: experimental
    '''

    INBOUND = "INBOUND"
    '''(experimental) Resolver is Inbound.

    :stability: experimental
    '''
    OUTBOUND = "OUTBOUND"
    '''(experimental) Resolver is outbound.

    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.ResourceGroupQueryTypes")
class ResourceGroupQueryTypes(enum.Enum):
    '''
    :stability: experimental
    '''

    TAG_FILTERS_1_0 = "TAG_FILTERS_1_0"
    '''
    :stability: experimental
    '''
    CLOUDFORMATION_STACK_1_0 = "CLOUDFORMATION_STACK_1_0"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.Route",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "destination": "destination",
        "cidr": "cidr",
        "subnet": "subnet",
    },
)
class Route:
    def __init__(
        self,
        *,
        description: builtins.str,
        destination: Destination,
        cidr: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[typing.Union["SubnetGroup", "SubnetWildCards"]] = None,
    ) -> None:
        '''
        :param description: 
        :param destination: 
        :param cidr: 
        :param subnet: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028e92a3698c6c2059fcc0e0af7aa3f7126cdc27fbf3664c78c792238416923f)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument subnet", value=subnet, expected_type=type_hints["subnet"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "destination": destination,
        }
        if cidr is not None:
            self._values["cidr"] = cidr
        if subnet is not None:
            self._values["subnet"] = subnet

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination(self) -> Destination:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(Destination, result)

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet(self) -> typing.Optional[typing.Union["SubnetGroup", "SubnetWildCards"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[typing.Union["SubnetGroup", "SubnetWildCards"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Route(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.RouterGroup",
    jsii_struct_bases=[],
    name_mapping={"routes": "routes", "subnet_group": "subnetGroup"},
)
class RouterGroup:
    def __init__(
        self,
        *,
        routes: typing.Sequence[typing.Union[Route, typing.Dict[builtins.str, typing.Any]]],
        subnet_group: "SubnetGroup",
    ) -> None:
        '''
        :param routes: 
        :param subnet_group: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc2dbc930d1298014e0060d53c8b233eeb195cad78ae6ab381d9fe994f8a6ca)
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
            check_type(argname="argument subnet_group", value=subnet_group, expected_type=type_hints["subnet_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "routes": routes,
            "subnet_group": subnet_group,
        }

    @builtins.property
    def routes(self) -> typing.List[Route]:
        '''
        :stability: experimental
        '''
        result = self._values.get("routes")
        assert result is not None, "Required property 'routes' is missing"
        return typing.cast(typing.List[Route], result)

    @builtins.property
    def subnet_group(self) -> "SubnetGroup":
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_group")
        assert result is not None, "Required property 'subnet_group' is missing"
        return typing.cast("SubnetGroup", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RouterGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.RuleGroupType")
class RuleGroupType(enum.Enum):
    '''
    :stability: experimental
    '''

    STATEFUL = "STATEFUL"
    '''
    :stability: experimental
    '''
    STATELESS = "STATELESS"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.SampleConfig",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "device_type": "deviceType",
        "ike_version": "ikeVersion",
    },
)
class SampleConfig:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
        device_type: "VpnDeviceType",
        ike_version: IkeVersion,
    ) -> None:
        '''(experimental) An interface that defines a set of Sample Configurations.

        :param bucket: (experimental) The S3 bucket where to place the sample configurations.
        :param device_type: (experimental) the type of device of the customer gateway.
        :param ike_version: (experimental) create configs for IKE1 or IKE2.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1397fe87954af98dd8ce47dc913ba3cd7d91e5a689f568c2cecc68f19a7f35e)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument device_type", value=device_type, expected_type=type_hints["device_type"])
            check_type(argname="argument ike_version", value=ike_version, expected_type=type_hints["ike_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "device_type": device_type,
            "ike_version": ike_version,
        }

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) The S3 bucket where to place the sample configurations.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

    @builtins.property
    def device_type(self) -> "VpnDeviceType":
        '''(experimental) the type of device of the customer gateway.

        :stability: experimental
        '''
        result = self._values.get("device_type")
        assert result is not None, "Required property 'device_type' is missing"
        return typing.cast("VpnDeviceType", result)

    @builtins.property
    def ike_version(self) -> IkeVersion:
        '''(experimental) create configs for IKE1 or IKE2.

        :stability: experimental
        '''
        result = self._values.get("ike_version")
        assert result is not None, "Required property 'ike_version' is missing"
        return typing.cast(IkeVersion, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SampleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.Segment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "allow_filter": "allowFilter",
        "deny_filter": "denyFilter",
        "description": "description",
        "edge_locations": "edgeLocations",
        "isolate_attachments": "isolateAttachments",
        "require_attachment_acceptance": "requireAttachmentAcceptance",
    },
)
class Segment:
    def __init__(
        self,
        *,
        name: builtins.str,
        allow_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        edge_locations: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
        isolate_attachments: typing.Optional[builtins.bool] = None,
        require_attachment_acceptance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Segment Properties.

        :param name: (experimental) Name of the Segment.
        :param allow_filter: (experimental) A list of denys.
        :param deny_filter: (experimental) a List of denys.
        :param description: (experimental) A description of the of the segement.
        :param edge_locations: (experimental) A list of edge locations where the segement will be avaialble. Not that the locations must also be included in the core network edge ( CNE )
        :param isolate_attachments: (experimental) Set true if attached VPCS are isolated from each other.
        :param require_attachment_acceptance: (experimental) Set true if the attachment needs approval for connection. Currently not supported and requires an automation step

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aad73c81de0fdf06b1bc2118a228e935f94d004ca6fa6c015ed53b07d8eda7de)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allow_filter", value=allow_filter, expected_type=type_hints["allow_filter"])
            check_type(argname="argument deny_filter", value=deny_filter, expected_type=type_hints["deny_filter"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument edge_locations", value=edge_locations, expected_type=type_hints["edge_locations"])
            check_type(argname="argument isolate_attachments", value=isolate_attachments, expected_type=type_hints["isolate_attachments"])
            check_type(argname="argument require_attachment_acceptance", value=require_attachment_acceptance, expected_type=type_hints["require_attachment_acceptance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if allow_filter is not None:
            self._values["allow_filter"] = allow_filter
        if deny_filter is not None:
            self._values["deny_filter"] = deny_filter
        if description is not None:
            self._values["description"] = description
        if edge_locations is not None:
            self._values["edge_locations"] = edge_locations
        if isolate_attachments is not None:
            self._values["isolate_attachments"] = isolate_attachments
        if require_attachment_acceptance is not None:
            self._values["require_attachment_acceptance"] = require_attachment_acceptance

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of the Segment.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of denys.

        :stability: experimental
        '''
        result = self._values.get("allow_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deny_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) a List of denys.

        :stability: experimental
        '''
        result = self._values.get("deny_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the of the segement.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def edge_locations(
        self,
    ) -> typing.Optional[typing.List[typing.Mapping[typing.Any, typing.Any]]]:
        '''(experimental) A list of edge locations where the segement will be avaialble.

        Not that the
        locations must also be included in the core network edge ( CNE )

        :stability: experimental
        '''
        result = self._values.get("edge_locations")
        return typing.cast(typing.Optional[typing.List[typing.Mapping[typing.Any, typing.Any]]], result)

    @builtins.property
    def isolate_attachments(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set true if attached VPCS are isolated from each other.

        :stability: experimental
        '''
        result = self._values.get("isolate_attachments")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_attachment_acceptance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set true if the attachment needs approval for connection.

        Currently not supported
        and requires an automation step

        :stability: experimental
        '''
        result = self._values.get("require_attachment_acceptance")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Segment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.SegmentAction",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "description": "description",
        "destination_cidr_blocks": "destinationCidrBlocks",
        "destinations": "destinations",
        "except_": "except",
        "mode": "mode",
        "share_with": "shareWith",
    },
)
class SegmentAction:
    def __init__(
        self,
        *,
        action: "SegmentActionType",
        description: builtins.str,
        destination_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        destinations: typing.Optional[typing.Sequence[builtins.str]] = None,
        except_: typing.Optional[typing.Sequence[builtins.str]] = None,
        mode: typing.Optional["SegmentActionMode"] = None,
        share_with: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
    ) -> None:
        '''(experimental) Segmment ACtions.

        :param action: 
        :param description: 
        :param destination_cidr_blocks: 
        :param destinations: 
        :param except_: 
        :param mode: 
        :param share_with: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f75b795ff910f5f1d933a53230abe6dcd022435de4889f7ac995505c989fbf8e)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument destination_cidr_blocks", value=destination_cidr_blocks, expected_type=type_hints["destination_cidr_blocks"])
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
            check_type(argname="argument except_", value=except_, expected_type=type_hints["except_"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument share_with", value=share_with, expected_type=type_hints["share_with"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "description": description,
        }
        if destination_cidr_blocks is not None:
            self._values["destination_cidr_blocks"] = destination_cidr_blocks
        if destinations is not None:
            self._values["destinations"] = destinations
        if except_ is not None:
            self._values["except_"] = except_
        if mode is not None:
            self._values["mode"] = mode
        if share_with is not None:
            self._values["share_with"] = share_with

    @builtins.property
    def action(self) -> "SegmentActionType":
        '''
        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast("SegmentActionType", result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_cidr_blocks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_cidr_blocks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def destinations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destinations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def except_(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("except_")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def mode(self) -> typing.Optional["SegmentActionMode"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional["SegmentActionMode"], result)

    @builtins.property
    def share_with(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("share_with")
        return typing.cast(typing.Optional[typing.Union[builtins.str, typing.List[builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SegmentAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.SegmentActionMode")
class SegmentActionMode(enum.Enum):
    '''(experimental) Segment Action Mode.

    :stability: experimental
    '''

    ATTACHMENT_ROUTE = "ATTACHMENT_ROUTE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.SegmentActionType")
class SegmentActionType(enum.Enum):
    '''(experimental) Segment Action Type.

    :stability: experimental
    '''

    SHARE = "SHARE"
    '''
    :stability: experimental
    '''
    CREATE_ROUTE = "CREATE_ROUTE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.ShareSubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "subnet_groups": "subnetGroups"},
)
class ShareSubnetGroupProps:
    def __init__(
        self,
        *,
        account: builtins.str,
        subnet_groups: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param account: 
        :param subnet_groups: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8d10fb497781360825742ed92db6bc2fcfef55e9f0384f09e93924bd6c10bb8)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument subnet_groups", value=subnet_groups, expected_type=type_hints["subnet_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "subnet_groups": subnet_groups,
        }

    @builtins.property
    def account(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_groups(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("subnet_groups")
        assert result is not None, "Required property 'subnet_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ShareSubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.SimpleAttachmentPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"rule_number": "ruleNumber", "account": "account"},
)
class SimpleAttachmentPolicyProps:
    def __init__(
        self,
        *,
        rule_number: jsii.Number,
        account: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param rule_number: 
        :param account: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238e5e42f7cdb4a535125371146395c3c0dd23286e1152cf9deb86026e47092f)
            check_type(argname="argument rule_number", value=rule_number, expected_type=type_hints["rule_number"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rule_number": rule_number,
        }
        if account is not None:
            self._values["account"] = account

    @builtins.property
    def rule_number(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("rule_number")
        assert result is not None, "Required property 'rule_number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SimpleAttachmentPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.SimpleShareActionProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "share_with": "shareWith"},
)
class SimpleShareActionProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        share_with: typing.Union[builtins.str, typing.Sequence[CoreNetworkSegment]],
    ) -> None:
        '''
        :param description: 
        :param share_with: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc2d264382f5358f50d91a07bda53386b43a451e7bc0d8b965f7b3844ca683fd)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument share_with", value=share_with, expected_type=type_hints["share_with"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "description": description,
            "share_with": share_with,
        }

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def share_with(self) -> typing.Union[builtins.str, typing.List[CoreNetworkSegment]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("share_with")
        assert result is not None, "Required property 'share_with' is missing"
        return typing.cast(typing.Union[builtins.str, typing.List[CoreNetworkSegment]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SimpleShareActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.StartupAction")
class StartupAction(enum.Enum):
    '''(experimental) Startup Action for S2S VPN.

    :stability: experimental
    '''

    START = "START"
    '''(experimental) AWS end to Intiate Startup.

    :stability: experimental
    '''
    ADD = "ADD"
    '''(experimental) Do not attempt to startup.

    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.StatefulAction")
class StatefulAction(enum.Enum):
    '''
    :stability: experimental
    '''

    PASS = "PASS"
    '''(experimental) Traffic will pass.

    :stability: experimental
    '''
    DROP = "DROP"
    '''(experimental) Traffic will be droped silently.

    Note, When will cause a timeout for TCP, Consider using REJECT

    :stability: experimental
    '''
    REJECT = "REJECT"
    '''(experimental) Traffic will be dropped, and a TCP reset sent to the source.

    :stability: experimental
    '''
    ALERT = "ALERT"
    '''(experimental) Raises an alert according to the firewalls logging/alert.

    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.StatefulDefaultActions")
class StatefulDefaultActions(enum.Enum):
    '''
    :stability: experimental
    '''

    DROP_STRICT = "DROP_STRICT"
    '''
    :stability: experimental
    '''
    DROP_ESTABLISHED = "DROP_ESTABLISHED"
    '''
    :stability: experimental
    '''
    ALERT_STRICT = "ALERT_STRICT"
    '''
    :stability: experimental
    '''
    ALERT_ESTABLISHED = "ALERT_ESTABLISHED"
    '''
    :stability: experimental
    '''


class StatefulRuleDatabase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.StatefulRuleDatabase",
):
    '''
    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6c1a896d83c1544a875e8e1298a81b96efeb6f0b5540511fa527bba9d3a8d57)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="crudServiceToken")
    def crud_service_token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "crudServiceToken"))

    @builtins.property
    @jsii.member(jsii_name="policyTable")
    def policy_table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.Table:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.Table, jsii.get(self, "policyTable"))


@jsii.enum(jsii_type="raindancers-network.StatelessActions")
class StatelessActions(enum.Enum):
    '''
    :stability: experimental
    '''

    PASS = "PASS"
    '''
    :stability: experimental
    '''
    DROP = "DROP"
    '''
    :stability: experimental
    '''
    STATEFUL = "STATEFUL"
    '''
    :stability: experimental
    '''


class StatelessRule(
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.StatelessRule",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        actions: typing.Sequence[StatelessActions],
        priority: jsii.Number,
        destination_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
        destinations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        protocols: typing.Optional[typing.Sequence[Protocol]] = None,
        source_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
        sources: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tcp_flags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.TCPFlagFieldProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param actions: 
        :param priority: 
        :param destination_ports: 
        :param destinations: 
        :param protocols: 
        :param source_ports: 
        :param sources: 
        :param tcp_flags: 

        :stability: experimental
        '''
        props = StatelessRuleProps(
            actions=actions,
            priority=priority,
            destination_ports=destination_ports,
            destinations=destinations,
            protocols=protocols,
            source_ports=source_ports,
            sources=sources,
            tcp_flags=tcp_flags,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="statelessRuleProperty")
    def stateless_rule_property(
        self,
    ) -> _aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty, jsii.get(self, "statelessRuleProperty"))


@jsii.data_type(
    jsii_type="raindancers-network.StatelessRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "priority": "priority",
        "destination_ports": "destinationPorts",
        "destinations": "destinations",
        "protocols": "protocols",
        "source_ports": "sourcePorts",
        "sources": "sources",
        "tcp_flags": "tcpFlags",
    },
)
class StatelessRuleProps:
    def __init__(
        self,
        *,
        actions: typing.Sequence[StatelessActions],
        priority: jsii.Number,
        destination_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
        destinations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        protocols: typing.Optional[typing.Sequence[Protocol]] = None,
        source_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
        sources: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tcp_flags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.TCPFlagFieldProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param actions: 
        :param priority: 
        :param destination_ports: 
        :param destinations: 
        :param protocols: 
        :param source_ports: 
        :param sources: 
        :param tcp_flags: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efea938c2146b49a87f0862a4e98800a2089ce649e7d6d0c193d71fca7838914)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument destination_ports", value=destination_ports, expected_type=type_hints["destination_ports"])
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
            check_type(argname="argument protocols", value=protocols, expected_type=type_hints["protocols"])
            check_type(argname="argument source_ports", value=source_ports, expected_type=type_hints["source_ports"])
            check_type(argname="argument sources", value=sources, expected_type=type_hints["sources"])
            check_type(argname="argument tcp_flags", value=tcp_flags, expected_type=type_hints["tcp_flags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "actions": actions,
            "priority": priority,
        }
        if destination_ports is not None:
            self._values["destination_ports"] = destination_ports
        if destinations is not None:
            self._values["destinations"] = destinations
        if protocols is not None:
            self._values["protocols"] = protocols
        if source_ports is not None:
            self._values["source_ports"] = source_ports
        if sources is not None:
            self._values["sources"] = sources
        if tcp_flags is not None:
            self._values["tcp_flags"] = tcp_flags

    @builtins.property
    def actions(self) -> typing.List[StatelessActions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[StatelessActions], result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def destination_ports(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, jsii.Number]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination_ports")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, jsii.Number]]], result)

    @builtins.property
    def destinations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destinations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty]], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[Protocol]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[Protocol]], result)

    @builtins.property
    def source_ports(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, jsii.Number]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source_ports")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, jsii.Number]]], result)

    @builtins.property
    def sources(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("sources")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty]], result)

    @builtins.property
    def tcp_flags(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.TCPFlagFieldProperty]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tcp_flags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.TCPFlagFieldProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatelessRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SubnetGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.SubnetGroup",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cidr_mask: jsii.Number,
        name: builtins.str,
        subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cidr_mask: 
        :param name: 
        :param subnet_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b4adb8148a3dbe5b310dc297e9c644624cf124b279b233e7f610829a9c177d6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ESubnetGroupProps(
            cidr_mask=cidr_mask, name=name, subnet_type=subnet_type
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> ESubnetGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(ESubnetGroup, jsii.get(self, "subnet"))

    @subnet.setter
    def subnet(self, value: ESubnetGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__822960f47a8a5e3d6de87100b31930f291ea7dc6cfbddec109e2ac0140cbbfb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnet", value)


@jsii.enum(jsii_type="raindancers-network.SubnetWildCards")
class SubnetWildCards(enum.Enum):
    '''
    :stability: experimental
    '''

    ALLSUBNETS = "ALLSUBNETS"
    '''
    :stability: experimental
    '''


class SuricataRuleGroup(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.SuricataRuleGroup",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        capacity: jsii.Number,
        network_firewall_engine: typing.Union[NWFWRulesEngine, typing.Dict[builtins.str, typing.Any]],
        rule_group_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        suricata_rules: typing.Optional[typing.Sequence[FQDNStatefulRule]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param capacity: 
        :param network_firewall_engine: 
        :param rule_group_name: 
        :param description: 
        :param suricata_rules: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5270488f7a763f48e3dbd311971f86ae2d9ceac5a63f56487edc188a73236c6d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SuricataRuleGroupProps(
            capacity=capacity,
            network_firewall_engine=network_firewall_engine,
            rule_group_name=rule_group_name,
            description=description,
            suricata_rules=suricata_rules,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRule")
    def add_rule(
        self,
        *,
        fqdn: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
        rules_database: typing.Optional[StatefulRuleDatabase] = None,
        action: StatefulAction,
        destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        dest_port: builtins.str,
        direction: Direction,
        name: builtins.str,
        protocol: FWProtocol,
        source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        src_port: builtins.str,
    ) -> None:
        '''
        :param fqdn: 
        :param priority: 
        :param rules_database: 
        :param action: 
        :param destination: 
        :param dest_port: 
        :param direction: 
        :param name: 
        :param protocol: 
        :param source: 
        :param src_port: 

        :stability: experimental
        '''
        props = FQDNStatefulRuleProps(
            fqdn=fqdn,
            priority=priority,
            rules_database=rules_database,
            action=action,
            destination=destination,
            dest_port=dest_port,
            direction=direction,
            name=name,
            protocol=protocol,
            source=source,
            src_port=src_port,
        )

        return typing.cast(None, jsii.invoke(self, "addRule", [props]))

    @builtins.property
    @jsii.member(jsii_name="ruleGroupArn")
    def rule_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ruleGroupArn"))

    @rule_group_arn.setter
    def rule_group_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49c44fc3a0863bca3329e1330cf3a4b0820d9a0e24204332b7dcc1f73887a0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleGroupArn", value)


@jsii.data_type(
    jsii_type="raindancers-network.SuricataRuleGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "capacity": "capacity",
        "network_firewall_engine": "networkFirewallEngine",
        "rule_group_name": "ruleGroupName",
        "description": "description",
        "suricata_rules": "suricataRules",
    },
)
class SuricataRuleGroupProps:
    def __init__(
        self,
        *,
        capacity: jsii.Number,
        network_firewall_engine: typing.Union[NWFWRulesEngine, typing.Dict[builtins.str, typing.Any]],
        rule_group_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        suricata_rules: typing.Optional[typing.Sequence[FQDNStatefulRule]] = None,
    ) -> None:
        '''
        :param capacity: 
        :param network_firewall_engine: 
        :param rule_group_name: 
        :param description: 
        :param suricata_rules: 

        :stability: experimental
        '''
        if isinstance(network_firewall_engine, dict):
            network_firewall_engine = NWFWRulesEngine(**network_firewall_engine)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4cb24897969e35bdb98f22dd64ce01688b6cb9f21bc5dbd08611c1194a8549a)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument network_firewall_engine", value=network_firewall_engine, expected_type=type_hints["network_firewall_engine"])
            check_type(argname="argument rule_group_name", value=rule_group_name, expected_type=type_hints["rule_group_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument suricata_rules", value=suricata_rules, expected_type=type_hints["suricata_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capacity": capacity,
            "network_firewall_engine": network_firewall_engine,
            "rule_group_name": rule_group_name,
        }
        if description is not None:
            self._values["description"] = description
        if suricata_rules is not None:
            self._values["suricata_rules"] = suricata_rules

    @builtins.property
    def capacity(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("capacity")
        assert result is not None, "Required property 'capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def network_firewall_engine(self) -> NWFWRulesEngine:
        '''
        :stability: experimental
        '''
        result = self._values.get("network_firewall_engine")
        assert result is not None, "Required property 'network_firewall_engine' is missing"
        return typing.cast(NWFWRulesEngine, result)

    @builtins.property
    def rule_group_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("rule_group_name")
        assert result is not None, "Required property 'rule_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suricata_rules(self) -> typing.Optional[typing.List[FQDNStatefulRule]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("suricata_rules")
        return typing.cast(typing.Optional[typing.List[FQDNStatefulRule]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SuricataRuleGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.SuricataRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "destination": "destination",
        "dest_port": "destPort",
        "direction": "direction",
        "name": "name",
        "protocol": "protocol",
        "source": "source",
        "src_port": "srcPort",
    },
)
class SuricataRuleProps:
    def __init__(
        self,
        *,
        action: StatefulAction,
        destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        dest_port: builtins.str,
        direction: Direction,
        name: builtins.str,
        protocol: FWProtocol,
        source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        src_port: builtins.str,
    ) -> None:
        '''
        :param action: 
        :param destination: 
        :param dest_port: 
        :param direction: 
        :param name: 
        :param protocol: 
        :param source: 
        :param src_port: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc2a8241fae2f5903f2bc83964c0b9d700081541b3baae0202f362619e2eb38)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument dest_port", value=dest_port, expected_type=type_hints["dest_port"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument src_port", value=src_port, expected_type=type_hints["src_port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "destination": destination,
            "dest_port": dest_port,
            "direction": direction,
            "name": name,
            "protocol": protocol,
            "source": source,
            "src_port": src_port,
        }

    @builtins.property
    def action(self) -> StatefulAction:
        '''
        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(StatefulAction, result)

    @builtins.property
    def destination(
        self,
    ) -> typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup], result)

    @builtins.property
    def dest_port(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("dest_port")
        assert result is not None, "Required property 'dest_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> Direction:
        '''
        :stability: experimental
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(Direction, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> FWProtocol:
        '''
        :stability: experimental
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(FWProtocol, result)

    @builtins.property
    def source(self) -> typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup], result)

    @builtins.property
    def src_port(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("src_port")
        assert result is not None, "Required property 'src_port' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SuricataRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.TGWOnCloudWanProps",
    jsii_struct_bases=[],
    name_mapping={
        "amazon_side_asn": "amazonSideAsn",
        "attachment_segment": "attachmentSegment",
        "cloudwan": "cloudwan",
        "description": "description",
        "cloud_wan_cidr": "cloudWanCidr",
        "default_route_in_segments": "defaultRouteInSegments",
        "tg_cidr": "tgCidr",
    },
)
class TGWOnCloudWanProps:
    def __init__(
        self,
        *,
        amazon_side_asn: builtins.str,
        attachment_segment: builtins.str,
        cloudwan: CoreNetwork,
        description: builtins.str,
        cloud_wan_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_route_in_segments: typing.Optional[typing.Sequence[builtins.str]] = None,
        tg_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for a TWGOnCloudWan.

        :param amazon_side_asn: 
        :param attachment_segment: 
        :param cloudwan: 
        :param description: 
        :param cloud_wan_cidr: 
        :param default_route_in_segments: 
        :param tg_cidr: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__633d08ef5b4861ae5b9673dd965b503c073be8e05307e2af9045399d40908c9c)
            check_type(argname="argument amazon_side_asn", value=amazon_side_asn, expected_type=type_hints["amazon_side_asn"])
            check_type(argname="argument attachment_segment", value=attachment_segment, expected_type=type_hints["attachment_segment"])
            check_type(argname="argument cloudwan", value=cloudwan, expected_type=type_hints["cloudwan"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument cloud_wan_cidr", value=cloud_wan_cidr, expected_type=type_hints["cloud_wan_cidr"])
            check_type(argname="argument default_route_in_segments", value=default_route_in_segments, expected_type=type_hints["default_route_in_segments"])
            check_type(argname="argument tg_cidr", value=tg_cidr, expected_type=type_hints["tg_cidr"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "amazon_side_asn": amazon_side_asn,
            "attachment_segment": attachment_segment,
            "cloudwan": cloudwan,
            "description": description,
        }
        if cloud_wan_cidr is not None:
            self._values["cloud_wan_cidr"] = cloud_wan_cidr
        if default_route_in_segments is not None:
            self._values["default_route_in_segments"] = default_route_in_segments
        if tg_cidr is not None:
            self._values["tg_cidr"] = tg_cidr

    @builtins.property
    def amazon_side_asn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("amazon_side_asn")
        assert result is not None, "Required property 'amazon_side_asn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachment_segment(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("attachment_segment")
        assert result is not None, "Required property 'attachment_segment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudwan(self) -> CoreNetwork:
        '''
        :stability: experimental
        '''
        result = self._values.get("cloudwan")
        assert result is not None, "Required property 'cloudwan' is missing"
        return typing.cast(CoreNetwork, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloud_wan_cidr(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cloud_wan_cidr")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_route_in_segments(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("default_route_in_segments")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tg_cidr(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tg_cidr")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TGWOnCloudWanProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.TagFilter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "values": "values"},
)
class TagFilter:
    def __init__(
        self,
        *,
        key: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: 
        :param values: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adad9f7d08060b34c3f11c538bbb13728f5d332abc13880a5250bee153fba4f9)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "values": values,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.TargetTypes")
class TargetTypes(enum.Enum):
    '''
    :stability: experimental
    '''

    AWS_ACCOUNT = "AWS_ACCOUNT"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.TunnelInsideIpVersion")
class TunnelInsideIpVersion(enum.Enum):
    '''(experimental) Determine if this is an IPv4 or IPv6 Tunnel.

    :stability: experimental
    '''

    IPV4 = "IPV4"
    '''(experimental) Use IPv4.

    :stability: experimental
    '''
    IPV6 = "IPV6"
    '''(experimental) Use IPv6.

    :stability: experimental
    '''


class UpdateSSMAgent(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.UpdateSSMAgent",
):
    '''(experimental) Creates a period task to update the SSM Agent on an EC2 Instance.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance: _aws_cdk_aws_ec2_ceddda9d.Instance,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance: (experimental) The EC2 Instance that will be udpated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd5d35fc07ec304ec4d3b76aeab3adb397986e476eb14c4a54c3fc74ff8ba449)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UpdateSSMAgentProps(instance=instance)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.UpdateSSMAgentProps",
    jsii_struct_bases=[],
    name_mapping={"instance": "instance"},
)
class UpdateSSMAgentProps:
    def __init__(self, *, instance: _aws_cdk_aws_ec2_ceddda9d.Instance) -> None:
        '''
        :param instance: (experimental) The EC2 Instance that will be udpated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c4813a20b6f24b88269f6533f4b31e4dfe83b71e1bfe75cdce86f086039cf54)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance": instance,
        }

    @builtins.property
    def instance(self) -> _aws_cdk_aws_ec2_ceddda9d.Instance:
        '''(experimental) The EC2 Instance that will be udpated.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Instance, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UpdateSSMAgentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.VpcRegionId",
    jsii_struct_bases=[],
    name_mapping={
        "peering_vpc_id": "peeringVpcId",
        "peer_vpc_region": "peerVpcRegion",
    },
)
class VpcRegionId:
    def __init__(
        self,
        *,
        peering_vpc_id: builtins.str,
        peer_vpc_region: builtins.str,
    ) -> None:
        '''
        :param peering_vpc_id: 
        :param peer_vpc_region: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6ccdf3daa9eccce5525026206a90b42d3f4858e87368c528c8ec4e3330ea2a6)
            check_type(argname="argument peering_vpc_id", value=peering_vpc_id, expected_type=type_hints["peering_vpc_id"])
            check_type(argname="argument peer_vpc_region", value=peer_vpc_region, expected_type=type_hints["peer_vpc_region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "peering_vpc_id": peering_vpc_id,
            "peer_vpc_region": peer_vpc_region,
        }

    @builtins.property
    def peering_vpc_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("peering_vpc_id")
        assert result is not None, "Required property 'peering_vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def peer_vpc_region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("peer_vpc_region")
        assert result is not None, "Required property 'peer_vpc_region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcRegionId(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.VpnDeviceType")
class VpnDeviceType(enum.Enum):
    '''(experimental) Remote end Device Types.

    :stability: experimental
    '''

    CHECKPOINT_R77_10 = "CHECKPOINT_R77_10"
    '''(experimental) Checkpoint R77_10.

    :stability: experimental
    '''
    CHECKPOINT_R80_10 = "CHECKPOINT_R80_10"
    '''
    :stability: experimental
    '''
    CISCO_ISR_12_4 = "CISCO_ISR_12_4"
    '''
    :stability: experimental
    '''
    CISCO_ASR_12_4 = "CISCO_ASR_12_4"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.VpnProps",
    jsii_struct_bases=[],
    name_mapping={
        "customer_gateway": "customerGateway",
        "vpnspec": "vpnspec",
        "sampleconfig": "sampleconfig",
        "tunnel_inside_cidr": "tunnelInsideCidr",
        "tunnel_ipam_pool": "tunnelIpamPool",
    },
)
class VpnProps:
    def __init__(
        self,
        *,
        customer_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway,
        vpnspec: typing.Union["VpnSpecProps", typing.Dict[builtins.str, typing.Any]],
        sampleconfig: typing.Optional[typing.Union[SampleConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        tunnel_inside_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
        tunnel_ipam_pool: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool] = None,
    ) -> None:
        '''(experimental) Properties for S2S VPN.

        :param customer_gateway: (experimental) The customer gateway where the vpn will terminate.
        :param vpnspec: (experimental) a VPN specification for the VPN.
        :param sampleconfig: (experimental) Optionally provide a sampleconfig specification.
        :param tunnel_inside_cidr: (experimental) Specify a pair of concrete Cidr's for the tunnel. Only use one of tunnelInsideCidr or tunnelIpmamPool
        :param tunnel_ipam_pool: (experimental) Specify an ipam pool to allocated the tunnel address's from. Use only one of tunnelInsideCidr or tunnelIpamPool

        :stability: experimental
        '''
        if isinstance(vpnspec, dict):
            vpnspec = VpnSpecProps(**vpnspec)
        if isinstance(sampleconfig, dict):
            sampleconfig = SampleConfig(**sampleconfig)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1752a38d3e09980986fc9172dcb3fd5eed134672e695a374f4a03eebfa237e)
            check_type(argname="argument customer_gateway", value=customer_gateway, expected_type=type_hints["customer_gateway"])
            check_type(argname="argument vpnspec", value=vpnspec, expected_type=type_hints["vpnspec"])
            check_type(argname="argument sampleconfig", value=sampleconfig, expected_type=type_hints["sampleconfig"])
            check_type(argname="argument tunnel_inside_cidr", value=tunnel_inside_cidr, expected_type=type_hints["tunnel_inside_cidr"])
            check_type(argname="argument tunnel_ipam_pool", value=tunnel_ipam_pool, expected_type=type_hints["tunnel_ipam_pool"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "customer_gateway": customer_gateway,
            "vpnspec": vpnspec,
        }
        if sampleconfig is not None:
            self._values["sampleconfig"] = sampleconfig
        if tunnel_inside_cidr is not None:
            self._values["tunnel_inside_cidr"] = tunnel_inside_cidr
        if tunnel_ipam_pool is not None:
            self._values["tunnel_ipam_pool"] = tunnel_ipam_pool

    @builtins.property
    def customer_gateway(self) -> _aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway:
        '''(experimental) The customer gateway where the vpn will terminate.

        :stability: experimental
        '''
        result = self._values.get("customer_gateway")
        assert result is not None, "Required property 'customer_gateway' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway, result)

    @builtins.property
    def vpnspec(self) -> "VpnSpecProps":
        '''(experimental) a VPN specification for the VPN.

        :stability: experimental
        '''
        result = self._values.get("vpnspec")
        assert result is not None, "Required property 'vpnspec' is missing"
        return typing.cast("VpnSpecProps", result)

    @builtins.property
    def sampleconfig(self) -> typing.Optional[SampleConfig]:
        '''(experimental) Optionally provide a sampleconfig specification.

        :stability: experimental
        '''
        result = self._values.get("sampleconfig")
        return typing.cast(typing.Optional[SampleConfig], result)

    @builtins.property
    def tunnel_inside_cidr(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Specify a pair of concrete Cidr's for the tunnel.

        Only use one of tunnelInsideCidr or tunnelIpmamPool

        :stability: experimental
        '''
        result = self._values.get("tunnel_inside_cidr")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tunnel_ipam_pool(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool]:
        '''(experimental) Specify an ipam pool to allocated the tunnel address's from.

        Use only one of tunnelInsideCidr or tunnelIpamPool

        :stability: experimental
        '''
        result = self._values.get("tunnel_ipam_pool")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.VpnSpecProps",
    jsii_struct_bases=[],
    name_mapping={
        "dpd_timeout_action": "dpdTimeoutAction",
        "dpd_timeout_seconds": "dpdTimeoutSeconds",
        "enable_acceleration": "enableAcceleration",
        "enable_logging": "enableLogging",
        "ike_versions": "ikeVersions",
        "local_ipv4_network_cidr": "localIpv4NetworkCidr",
        "outside_ip_address_type": "outsideIpAddressType",
        "phase1_dh_group_numbers": "phase1DHGroupNumbers",
        "phase1_encryption_algorithms": "phase1EncryptionAlgorithms",
        "phase1_integrity_algorithms": "phase1IntegrityAlgorithms",
        "phase1_lifetime_seconds": "phase1LifetimeSeconds",
        "phase2_dh_group_numbers": "phase2DHGroupNumbers",
        "phase2_encryption_algorithms": "phase2EncryptionAlgorithms",
        "phase2_integrity_algorithms": "phase2IntegrityAlgorithms",
        "phase2_life_time_seconds": "phase2LifeTimeSeconds",
        "rekey_fuzz_percentage": "rekeyFuzzPercentage",
        "rekey_margin_time_seconds": "rekeyMarginTimeSeconds",
        "remote_ipv4_network_cidr": "remoteIpv4NetworkCidr",
        "replay_window_size": "replayWindowSize",
        "startup_action": "startupAction",
        "static_routes_only": "staticRoutesOnly",
        "tunnel_inside_ip_version": "tunnelInsideIpVersion",
    },
)
class VpnSpecProps:
    def __init__(
        self,
        *,
        dpd_timeout_action: typing.Optional[DPDTimeoutAction] = None,
        dpd_timeout_seconds: typing.Optional[jsii.Number] = None,
        enable_acceleration: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        ike_versions: typing.Optional[typing.Sequence[IkeVersion]] = None,
        local_ipv4_network_cidr: typing.Optional[builtins.str] = None,
        outside_ip_address_type: typing.Optional[OutsideIpAddressType] = None,
        phase1_dh_group_numbers: typing.Optional[typing.Sequence[Phase1DHGroupNumbers]] = None,
        phase1_encryption_algorithms: typing.Optional[typing.Sequence[Phase1EncryptionAlgorithms]] = None,
        phase1_integrity_algorithms: typing.Optional[typing.Sequence[Phase1IntegrityAlgorithms]] = None,
        phase1_lifetime_seconds: typing.Optional[jsii.Number] = None,
        phase2_dh_group_numbers: typing.Optional[typing.Sequence[Phase2DHGroupNumbers]] = None,
        phase2_encryption_algorithms: typing.Optional[typing.Sequence[Phase2EncryptionAlgorithms]] = None,
        phase2_integrity_algorithms: typing.Optional[typing.Sequence[Phase2IntegrityAlgorithms]] = None,
        phase2_life_time_seconds: typing.Optional[jsii.Number] = None,
        rekey_fuzz_percentage: typing.Optional[jsii.Number] = None,
        rekey_margin_time_seconds: typing.Optional[jsii.Number] = None,
        remote_ipv4_network_cidr: typing.Optional[builtins.str] = None,
        replay_window_size: typing.Optional[jsii.Number] = None,
        startup_action: typing.Optional[StartupAction] = None,
        static_routes_only: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        tunnel_inside_ip_version: typing.Optional[TunnelInsideIpVersion] = None,
    ) -> None:
        '''(experimental) THe properties for a S2S Ipsec Vpn Connection https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateVpnConnection.html.

        :param dpd_timeout_action: Default: CLEAR The action to take after DPD timeout occurs. Specify restart to restart the IKE initiation. Specify clear to end the IKE session.
        :param dpd_timeout_seconds: Default: 30 The number of seconds after which a DPD timeout occurs.
        :param enable_acceleration: (experimental) Indicate whether to enable acceleration for the VPN connection.
        :param enable_logging: (experimental) Enable CloudwatchLogging for the S2S VPN.
        :param ike_versions: (experimental) The IKE versions that are permitted for the VPN tunnel.
        :param local_ipv4_network_cidr: Default: 0.0.0.0/0 The IPv4 CIDR on the AWS side of the VPN connection.
        :param outside_ip_address_type: Default: PUBLIC The type of IPv4 address assigned to the outside interface of the customer gateway device.
        :param phase1_dh_group_numbers: (experimental) One or more Diffie-Hellman group numbers that are permitted for the VPN tunnel for phase 1 IKE negotiations.
        :param phase1_encryption_algorithms: (experimental) One or more encryption algorithms that are permitted for the VPN tunnel for phase 1 IKE negotiations.
        :param phase1_integrity_algorithms: (experimental) One or more integrity algorithms that are permitted for the VPN tunnel for phase 1 IKE negotiations.
        :param phase1_lifetime_seconds: (experimental) The lifetime for phase 1 of the IKE negotiation, in seconds.
        :param phase2_dh_group_numbers: (experimental) One or more Diffie-Hellman group numbers that are permitted for the VPN tunnel for phase 2 IKE negotiations.
        :param phase2_encryption_algorithms: (experimental) One or more encryption algorithms that are permitted for the VPN tunnel for phase 2 IKE negotiations.
        :param phase2_integrity_algorithms: (experimental) One or more integrity algorithms that are permitted for the VPN tunnel for phase 2 IKE negotiations.
        :param phase2_life_time_seconds: (experimental) The lifetime for phase 2 of the IKE negotiation, in seconds.
        :param rekey_fuzz_percentage: Default: 100 The percentage of the rekey window (determined by RekeyMarginTimeSeconds) during which the rekey time is randomly selected.
        :param rekey_margin_time_seconds: Default: 540 The margin time, in seconds, before the phase 2 lifetime expires, during which the AWS side of the VPN connection performs an IKE rekey. The exact time of the rekey is randomly selected based on the value for RekeyFuzzPercentage.
        :param remote_ipv4_network_cidr: Default: 0.0.0.0/0 The IPv4 CIDR on the Remote side of the VPN connection.
        :param replay_window_size: Default: 1024 The number of packets in an IKE replay window.
        :param startup_action: (experimental) The action to take when the establishing the tunnel for the VPN connection. By default, your customer gateway device must initiate the IKE negotiation and bring up the tunnel. Specify start for AWS to initiate the IKE negotiation.
        :param static_routes_only: (experimental) Indicate if this will only use Static Routes Only.
        :param tunnel_inside_ip_version: Default: IPV4 Indicate whether the VPN tunnels process IPv4 or IPv6 traffic.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3c1da337aa49b63d2d1d5bca7dcc354e04c4bc02bf79fd140d56f6d7c166873)
            check_type(argname="argument dpd_timeout_action", value=dpd_timeout_action, expected_type=type_hints["dpd_timeout_action"])
            check_type(argname="argument dpd_timeout_seconds", value=dpd_timeout_seconds, expected_type=type_hints["dpd_timeout_seconds"])
            check_type(argname="argument enable_acceleration", value=enable_acceleration, expected_type=type_hints["enable_acceleration"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument ike_versions", value=ike_versions, expected_type=type_hints["ike_versions"])
            check_type(argname="argument local_ipv4_network_cidr", value=local_ipv4_network_cidr, expected_type=type_hints["local_ipv4_network_cidr"])
            check_type(argname="argument outside_ip_address_type", value=outside_ip_address_type, expected_type=type_hints["outside_ip_address_type"])
            check_type(argname="argument phase1_dh_group_numbers", value=phase1_dh_group_numbers, expected_type=type_hints["phase1_dh_group_numbers"])
            check_type(argname="argument phase1_encryption_algorithms", value=phase1_encryption_algorithms, expected_type=type_hints["phase1_encryption_algorithms"])
            check_type(argname="argument phase1_integrity_algorithms", value=phase1_integrity_algorithms, expected_type=type_hints["phase1_integrity_algorithms"])
            check_type(argname="argument phase1_lifetime_seconds", value=phase1_lifetime_seconds, expected_type=type_hints["phase1_lifetime_seconds"])
            check_type(argname="argument phase2_dh_group_numbers", value=phase2_dh_group_numbers, expected_type=type_hints["phase2_dh_group_numbers"])
            check_type(argname="argument phase2_encryption_algorithms", value=phase2_encryption_algorithms, expected_type=type_hints["phase2_encryption_algorithms"])
            check_type(argname="argument phase2_integrity_algorithms", value=phase2_integrity_algorithms, expected_type=type_hints["phase2_integrity_algorithms"])
            check_type(argname="argument phase2_life_time_seconds", value=phase2_life_time_seconds, expected_type=type_hints["phase2_life_time_seconds"])
            check_type(argname="argument rekey_fuzz_percentage", value=rekey_fuzz_percentage, expected_type=type_hints["rekey_fuzz_percentage"])
            check_type(argname="argument rekey_margin_time_seconds", value=rekey_margin_time_seconds, expected_type=type_hints["rekey_margin_time_seconds"])
            check_type(argname="argument remote_ipv4_network_cidr", value=remote_ipv4_network_cidr, expected_type=type_hints["remote_ipv4_network_cidr"])
            check_type(argname="argument replay_window_size", value=replay_window_size, expected_type=type_hints["replay_window_size"])
            check_type(argname="argument startup_action", value=startup_action, expected_type=type_hints["startup_action"])
            check_type(argname="argument static_routes_only", value=static_routes_only, expected_type=type_hints["static_routes_only"])
            check_type(argname="argument tunnel_inside_ip_version", value=tunnel_inside_ip_version, expected_type=type_hints["tunnel_inside_ip_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dpd_timeout_action is not None:
            self._values["dpd_timeout_action"] = dpd_timeout_action
        if dpd_timeout_seconds is not None:
            self._values["dpd_timeout_seconds"] = dpd_timeout_seconds
        if enable_acceleration is not None:
            self._values["enable_acceleration"] = enable_acceleration
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if ike_versions is not None:
            self._values["ike_versions"] = ike_versions
        if local_ipv4_network_cidr is not None:
            self._values["local_ipv4_network_cidr"] = local_ipv4_network_cidr
        if outside_ip_address_type is not None:
            self._values["outside_ip_address_type"] = outside_ip_address_type
        if phase1_dh_group_numbers is not None:
            self._values["phase1_dh_group_numbers"] = phase1_dh_group_numbers
        if phase1_encryption_algorithms is not None:
            self._values["phase1_encryption_algorithms"] = phase1_encryption_algorithms
        if phase1_integrity_algorithms is not None:
            self._values["phase1_integrity_algorithms"] = phase1_integrity_algorithms
        if phase1_lifetime_seconds is not None:
            self._values["phase1_lifetime_seconds"] = phase1_lifetime_seconds
        if phase2_dh_group_numbers is not None:
            self._values["phase2_dh_group_numbers"] = phase2_dh_group_numbers
        if phase2_encryption_algorithms is not None:
            self._values["phase2_encryption_algorithms"] = phase2_encryption_algorithms
        if phase2_integrity_algorithms is not None:
            self._values["phase2_integrity_algorithms"] = phase2_integrity_algorithms
        if phase2_life_time_seconds is not None:
            self._values["phase2_life_time_seconds"] = phase2_life_time_seconds
        if rekey_fuzz_percentage is not None:
            self._values["rekey_fuzz_percentage"] = rekey_fuzz_percentage
        if rekey_margin_time_seconds is not None:
            self._values["rekey_margin_time_seconds"] = rekey_margin_time_seconds
        if remote_ipv4_network_cidr is not None:
            self._values["remote_ipv4_network_cidr"] = remote_ipv4_network_cidr
        if replay_window_size is not None:
            self._values["replay_window_size"] = replay_window_size
        if startup_action is not None:
            self._values["startup_action"] = startup_action
        if static_routes_only is not None:
            self._values["static_routes_only"] = static_routes_only
        if tunnel_inside_ip_version is not None:
            self._values["tunnel_inside_ip_version"] = tunnel_inside_ip_version

    @builtins.property
    def dpd_timeout_action(self) -> typing.Optional[DPDTimeoutAction]:
        '''
        :default: CLEAR The action to take after DPD timeout occurs. Specify restart to restart the IKE initiation. Specify clear to end the IKE session.

        :stability: experimental
        '''
        result = self._values.get("dpd_timeout_action")
        return typing.cast(typing.Optional[DPDTimeoutAction], result)

    @builtins.property
    def dpd_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 30 The number of seconds after which a DPD timeout occurs.

        :stability: experimental
        '''
        result = self._values.get("dpd_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_acceleration(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicate whether to enable acceleration for the VPN connection.

        :stability: experimental
        '''
        result = self._values.get("enable_acceleration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable CloudwatchLogging for the S2S VPN.

        :stability: experimental
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ike_versions(self) -> typing.Optional[typing.List[IkeVersion]]:
        '''(experimental) The IKE versions that are permitted for the VPN tunnel.

        :stability: experimental
        '''
        result = self._values.get("ike_versions")
        return typing.cast(typing.Optional[typing.List[IkeVersion]], result)

    @builtins.property
    def local_ipv4_network_cidr(self) -> typing.Optional[builtins.str]:
        '''
        :default: 0.0.0.0/0 The IPv4 CIDR on the AWS side of the VPN connection.

        :stability: experimental
        '''
        result = self._values.get("local_ipv4_network_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outside_ip_address_type(self) -> typing.Optional[OutsideIpAddressType]:
        '''
        :default: PUBLIC The type of IPv4 address assigned to the outside interface of the customer gateway device.

        :stability: experimental
        '''
        result = self._values.get("outside_ip_address_type")
        return typing.cast(typing.Optional[OutsideIpAddressType], result)

    @builtins.property
    def phase1_dh_group_numbers(
        self,
    ) -> typing.Optional[typing.List[Phase1DHGroupNumbers]]:
        '''(experimental) One or more Diffie-Hellman group numbers that are permitted for the VPN tunnel for phase 1 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase1_dh_group_numbers")
        return typing.cast(typing.Optional[typing.List[Phase1DHGroupNumbers]], result)

    @builtins.property
    def phase1_encryption_algorithms(
        self,
    ) -> typing.Optional[typing.List[Phase1EncryptionAlgorithms]]:
        '''(experimental) One or more encryption algorithms that are permitted for the VPN tunnel for phase 1 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase1_encryption_algorithms")
        return typing.cast(typing.Optional[typing.List[Phase1EncryptionAlgorithms]], result)

    @builtins.property
    def phase1_integrity_algorithms(
        self,
    ) -> typing.Optional[typing.List[Phase1IntegrityAlgorithms]]:
        '''(experimental) One or more integrity algorithms that are permitted for the VPN tunnel for phase 1 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase1_integrity_algorithms")
        return typing.cast(typing.Optional[typing.List[Phase1IntegrityAlgorithms]], result)

    @builtins.property
    def phase1_lifetime_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The lifetime for phase 1 of the IKE negotiation, in seconds.

        :stability: experimental
        '''
        result = self._values.get("phase1_lifetime_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def phase2_dh_group_numbers(
        self,
    ) -> typing.Optional[typing.List[Phase2DHGroupNumbers]]:
        '''(experimental) One or more Diffie-Hellman group numbers that are permitted for the VPN tunnel for phase 2 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase2_dh_group_numbers")
        return typing.cast(typing.Optional[typing.List[Phase2DHGroupNumbers]], result)

    @builtins.property
    def phase2_encryption_algorithms(
        self,
    ) -> typing.Optional[typing.List[Phase2EncryptionAlgorithms]]:
        '''(experimental) One or more encryption algorithms that are permitted for the VPN tunnel for phase 2 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase2_encryption_algorithms")
        return typing.cast(typing.Optional[typing.List[Phase2EncryptionAlgorithms]], result)

    @builtins.property
    def phase2_integrity_algorithms(
        self,
    ) -> typing.Optional[typing.List[Phase2IntegrityAlgorithms]]:
        '''(experimental) One or more integrity algorithms that are permitted for the VPN tunnel for phase 2 IKE negotiations.

        :stability: experimental
        '''
        result = self._values.get("phase2_integrity_algorithms")
        return typing.cast(typing.Optional[typing.List[Phase2IntegrityAlgorithms]], result)

    @builtins.property
    def phase2_life_time_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The lifetime for phase 2 of the IKE negotiation, in seconds.

        :stability: experimental
        '''
        result = self._values.get("phase2_life_time_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rekey_fuzz_percentage(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 100 The percentage of the rekey window (determined by RekeyMarginTimeSeconds) during which the rekey time is randomly selected.

        :stability: experimental
        '''
        result = self._values.get("rekey_fuzz_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rekey_margin_time_seconds(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 540 The margin time, in seconds, before the phase 2 lifetime expires, during which the AWS side of the VPN connection performs an IKE rekey. The exact time of the rekey is randomly selected based on the value for RekeyFuzzPercentage.

        :stability: experimental
        '''
        result = self._values.get("rekey_margin_time_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def remote_ipv4_network_cidr(self) -> typing.Optional[builtins.str]:
        '''
        :default: 0.0.0.0/0 The IPv4 CIDR on the Remote side of the VPN connection.

        :stability: experimental
        '''
        result = self._values.get("remote_ipv4_network_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replay_window_size(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 1024 The number of packets in an IKE replay window.

        :stability: experimental
        '''
        result = self._values.get("replay_window_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def startup_action(self) -> typing.Optional[StartupAction]:
        '''(experimental) The action to take when the establishing the tunnel for the VPN connection.

        By default, your customer gateway device must initiate the IKE negotiation and bring up the tunnel. Specify start for AWS to initiate the IKE negotiation.

        :stability: experimental
        '''
        result = self._values.get("startup_action")
        return typing.cast(typing.Optional[StartupAction], result)

    @builtins.property
    def static_routes_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]]:
        '''(experimental) Indicate if this will only use Static Routes Only.

        :stability: experimental
        '''
        result = self._values.get("static_routes_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]], result)

    @builtins.property
    def tunnel_inside_ip_version(self) -> typing.Optional[TunnelInsideIpVersion]:
        '''
        :default: IPV4 Indicate whether the VPN tunnels process IPv4 or IPv6 traffic.

        :stability: experimental
        '''
        result = self._values.get("tunnel_inside_ip_version")
        return typing.cast(typing.Optional[TunnelInsideIpVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnSpecProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.WellKnownPorts")
class WellKnownPorts(enum.Enum):
    '''
    :stability: experimental
    '''

    SSH = "SSH"
    '''
    :stability: experimental
    '''
    HTTP = "HTTP"
    '''
    :stability: experimental
    '''
    HTTPS = "HTTPS"
    '''
    :stability: experimental
    '''
    RDP = "RDP"
    '''
    :stability: experimental
    '''


@jsii.implements(IAssignment)
class Assignment(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.Assignment",
):
    '''(experimental) The assignment construct.

    Has no import method because there is no attributes to import.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        permission_set: IPermissionSet,
        principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
        target_id: builtins.str,
        target_type: typing.Optional[TargetTypes] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param permission_set: (experimental) The permission set to assign to the principal.
        :param principal: (experimental) The principal to assign the permission set to.
        :param target_id: (experimental) The target id the permission set will be assigned to.
        :param target_type: (experimental) The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__591a9551402313c51e363bd419ee497ab58a9f785dffff362a797994dbdd4d4a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AssignmentProps(
            permission_set=permission_set,
            principal=principal,
            target_id=target_id,
            target_type=target_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="raindancers-network.FQDNStatefulRuleProps",
    jsii_struct_bases=[SuricataRuleProps],
    name_mapping={
        "action": "action",
        "destination": "destination",
        "dest_port": "destPort",
        "direction": "direction",
        "name": "name",
        "protocol": "protocol",
        "source": "source",
        "src_port": "srcPort",
        "fqdn": "fqdn",
        "priority": "priority",
        "rules_database": "rulesDatabase",
    },
)
class FQDNStatefulRuleProps(SuricataRuleProps):
    def __init__(
        self,
        *,
        action: StatefulAction,
        destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        dest_port: builtins.str,
        direction: Direction,
        name: builtins.str,
        protocol: FWProtocol,
        source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
        src_port: builtins.str,
        fqdn: builtins.str,
        priority: typing.Optional[jsii.Number] = None,
        rules_database: typing.Optional[StatefulRuleDatabase] = None,
    ) -> None:
        '''
        :param action: 
        :param destination: 
        :param dest_port: 
        :param direction: 
        :param name: 
        :param protocol: 
        :param source: 
        :param src_port: 
        :param fqdn: 
        :param priority: 
        :param rules_database: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a18dedac1fb826fc6ecd1ce96fb2bd0c3e2ddbed84fc63b148ceabf414ab7b67)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument dest_port", value=dest_port, expected_type=type_hints["dest_port"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument src_port", value=src_port, expected_type=type_hints["src_port"])
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument rules_database", value=rules_database, expected_type=type_hints["rules_database"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "destination": destination,
            "dest_port": dest_port,
            "direction": direction,
            "name": name,
            "protocol": protocol,
            "source": source,
            "src_port": src_port,
            "fqdn": fqdn,
        }
        if priority is not None:
            self._values["priority"] = priority
        if rules_database is not None:
            self._values["rules_database"] = rules_database

    @builtins.property
    def action(self) -> StatefulAction:
        '''
        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(StatefulAction, result)

    @builtins.property
    def destination(
        self,
    ) -> typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup], result)

    @builtins.property
    def dest_port(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("dest_port")
        assert result is not None, "Required property 'dest_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> Direction:
        '''
        :stability: experimental
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(Direction, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> FWProtocol:
        '''
        :stability: experimental
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(FWProtocol, result)

    @builtins.property
    def source(self) -> typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup], result)

    @builtins.property
    def src_port(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("src_port")
        assert result is not None, "Required property 'src_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rules_database(self) -> typing.Optional[StatefulRuleDatabase]:
        '''
        :stability: experimental
        '''
        result = self._values.get("rules_database")
        return typing.cast(typing.Optional[StatefulRuleDatabase], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FQDNStatefulRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddAwsServiceEndPointsProps",
    "AddCoreRoutesProps",
    "AddEnterprizeZoneProps",
    "AddR53ZoneProps",
    "AddRoutesProps",
    "AddStatefulRulesProps",
    "AddStatelessRulesProps",
    "ApplianceMode",
    "Assignment",
    "AssignmentAttributes",
    "AssignmentOptions",
    "AssignmentProps",
    "AssociateSharedResolverRule",
    "AssociateSharedResolverRuleProps",
    "AssociationMethod",
    "AttachToCloudWanProps",
    "AttachToTransitGatewayProps",
    "AttachmentCondition",
    "AttachmentConditions",
    "AttachmentPolicy",
    "AttachmentPolicyAction",
    "AwsManagedDNSFirewallRuleGroup",
    "AwsRegions",
    "AwsServiceEndPoints",
    "AwsServiceEndPointsProps",
    "CentralAccountAssnRole",
    "CentralAccountAssnRoleProps",
    "CentralResolverRules",
    "CentralResolverRulesProps",
    "CloudWanRoutingProtocolProps",
    "CloudWanTGW",
    "ConditionLogic",
    "ConditionalForwarder",
    "ConditionalForwarderProps",
    "CoreNetwork",
    "CoreNetworkProps",
    "CoreNetworkSegment",
    "CoreNetworkShare",
    "CrossAccountProps",
    "CrossRegionParameterReader",
    "CrossRegionParameterReaderProps",
    "CrossRegionParameterWriter",
    "CrossRegionParameterWriterProps",
    "CrowdStrikeCloud",
    "CrowdStrikeExtendedEndpoint",
    "CrowdStrikeExtendedEndpointProps",
    "CrowdStrikeNLB",
    "CrowdStrikeNLBProps",
    "CrowdStrikePrivateLink",
    "CrowdStrikePrivateLinkEndpoint",
    "CrowdStrikePrivateLinkEndpointProps",
    "CrowdStrikeRegion",
    "CrowdStrikeServices",
    "CustomerManagedPolicyReference",
    "DNSFirewallActions",
    "DNSFirewallBlockResponse",
    "DPDTimeoutAction",
    "Destination",
    "Direction",
    "DynamicTagResourceGroup",
    "DynamicTagResourceGroupProps",
    "DynamicTagResourceGroupSet",
    "ESubnetGroup",
    "ESubnetGroupProps",
    "Endpoint",
    "EnforceImdsv2",
    "EnforceImdsv2Props",
    "EnterpriseVpc",
    "EnterpriseVpcLambda",
    "EnterpriseVpcProps",
    "EnterpriseZone",
    "EnterpriseZoneProps",
    "EvpcProps",
    "FQDNStatefulRule",
    "FQDNStatefulRuleProps",
    "FWProtocol",
    "FindPrefixList",
    "FindPrefixListProps",
    "FirewallPolicy",
    "FirewallPolicyProps",
    "FlowLogProps",
    "ForwardingRules",
    "ForwardingRulesProps",
    "GetTunnelAddressPair",
    "GetTunnelAddressPairProps",
    "HubVpc",
    "IAssignment",
    "ICoreNetworkSegmentProps",
    "IFirewallPolicyProperty",
    "IPAddressFamily",
    "IPermissionSet",
    "IkeVersion",
    "IpsecTunnelPool",
    "IpsecTunnelPoolProps",
    "ManagedAwsFirewallRules",
    "NWFWRulesEngine",
    "NetworkFirewall",
    "NetworkFirewallProps",
    "Operators",
    "OutboundForwardingRule",
    "OutsideIpAddressType",
    "PermissionBoundary",
    "PermissionSet",
    "PermissionSetAttributes",
    "PermissionSetProps",
    "Phase1DHGroupNumbers",
    "Phase1EncryptionAlgorithms",
    "Phase1IntegrityAlgorithms",
    "Phase2DHGroupNumbers",
    "Phase2EncryptionAlgorithms",
    "Phase2IntegrityAlgorithms",
    "PowerBIGateway",
    "PowerBIGatewayZoo",
    "PowerBIGatewayZooProps",
    "PowerBiGateway",
    "PowerBiGatewayProps",
    "PrefixCidr",
    "PrefixList",
    "PrefixListEntry",
    "PrefixListProps",
    "PrefixListSetInterface",
    "PrincipalProperty",
    "PrincipalTypes",
    "PrivateRedshiftCluster",
    "Protocol",
    "R53Resolverendpoints",
    "R53ResolverendpointsProps",
    "RedShiftDatabase",
    "RedShiftDatabaseProps",
    "RedshiftClusterProps",
    "ReferenceSet",
    "ResolveSubnetGroupName",
    "ResolveSubnetGroupNameProps",
    "ResolverDirection",
    "ResourceGroupQueryTypes",
    "Route",
    "RouterGroup",
    "RuleGroupType",
    "SampleConfig",
    "Segment",
    "SegmentAction",
    "SegmentActionMode",
    "SegmentActionType",
    "ShareSubnetGroupProps",
    "SimpleAttachmentPolicyProps",
    "SimpleShareActionProps",
    "StartupAction",
    "StatefulAction",
    "StatefulDefaultActions",
    "StatefulRuleDatabase",
    "StatelessActions",
    "StatelessRule",
    "StatelessRuleProps",
    "SubnetGroup",
    "SubnetWildCards",
    "SuricataRuleGroup",
    "SuricataRuleGroupProps",
    "SuricataRuleProps",
    "TGWOnCloudWanProps",
    "TagFilter",
    "TargetTypes",
    "TunnelInsideIpVersion",
    "UpdateSSMAgent",
    "UpdateSSMAgentProps",
    "VpcRegionId",
    "VpnDeviceType",
    "VpnProps",
    "VpnSpecProps",
    "WellKnownPorts",
    "apilambda",
    "delay",
    "glue",
    "lakeformation",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import apilambda
from . import delay
from . import glue
from . import lakeformation

def _typecheckingstub__1d2cc1384bdc954b012b4ee9cbd2dc7b0d1f0c17055601fe2f3df5391ee1cbbc(
    *,
    services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
    subnet_group: SubnetGroup,
    dynamo_db_gateway: typing.Optional[builtins.bool] = None,
    s3_gateway_interface: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8f4daaa6aed14129a681e485c910e5042db7338e8b5dcc6f76e78e3ca80885(
    *,
    attachment_id: builtins.str,
    core_name: builtins.str,
    description: builtins.str,
    destination_cidr_blocks: typing.Sequence[builtins.str],
    policy_table_arn: builtins.str,
    segments: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013fa385be66a7ab1fdaf16408736a597092b20533f6f8f18fdb0e0cf1a1fe8b(
    *,
    domainname: builtins.str,
    hub_vpcs: typing.Sequence[typing.Union[HubVpc, typing.Dict[builtins.str, typing.Any]]],
    is_hub_vpc: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53e9d3cadea14460a1ee6ecbb2d70b4538efae7cd8d786e6ccabc0a8ed3cd6fe(
    *,
    zone: builtins.str,
    central_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8caa7ea9992a583a226f2a016e499bd005c8a4d98f8b16c728ed2d3b24a6caf(
    *,
    cidr: typing.Sequence[builtins.str],
    description: builtins.str,
    destination: Destination,
    subnet_groups: typing.Sequence[builtins.str],
    cloudwan_name: typing.Optional[builtins.str] = None,
    network_firewall_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427ae99d97748b5c424729df449196fc4c1f2fc7265a24ffcadc57c85265c911(
    *,
    aws_managed_rules: typing.Sequence[ManagedAwsFirewallRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a97874b1f84366909c00c07fab79e125790b203b8f0c095a88429dd5062f0bda(
    *,
    description: builtins.str,
    group_name: builtins.str,
    rules: typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.StatelessRuleProperty, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ea70b6b68927c926c03c2b997826b441c2601f5dbbd2fc437f9e73dda895545(
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2974dcb321c18d62191df7e7fca3d2abc1db70278ba6d1257acc8ad0dd3b5278(
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
    permission_set: IPermissionSet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe2f05a522631dcde421bc7a12ed88dd269841faf2a1011fca3219a3036f747(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_names: typing.Sequence[builtins.str],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a800dc7ac62dffed3914b02d40756c231878518e5ff905efd1627f5adbdab30(
    *,
    domain_names: typing.Sequence[builtins.str],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50631041fbe2ac8aeab9261d67d56d19e35dfc4b66c6474ea616c1b4b5c2c77(
    *,
    core_network_name: builtins.str,
    segment_name: builtins.str,
    appliance_mode: typing.Optional[builtins.bool] = None,
    attachment_subnet_group: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ea4110bef21c88d23180cffa72e93a9cbcc40f39f7b0347527f0873a351dac(
    *,
    transit_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnTransitGateway,
    applicance_mode: typing.Optional[ApplianceMode] = None,
    attachment_subnet_group: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5656f7cf3af493453fb7cd73bb01af8aa61698a67ee1da580a06b8992b3cb7bb(
    *,
    type: AttachmentCondition,
    key: typing.Optional[builtins.str] = None,
    operator: typing.Optional[Operators] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78d7306a292c43a1d00323d5e298f6e6d7d86dd1bd56a81371f7ca98fadbfde8(
    *,
    action: typing.Union[AttachmentPolicyAction, typing.Dict[builtins.str, typing.Any]],
    conditions: typing.Sequence[typing.Union[AttachmentConditions, typing.Dict[builtins.str, typing.Any]]],
    rule_number: jsii.Number,
    condition_logic: typing.Optional[ConditionLogic] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9918da80216c2f729d8c021ce398f10448c1da901e5f407303774b4acae3df(
    *,
    association_method: AssociationMethod,
    segment: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__295ac7c5386853c57aa011ef974b13862e08a4e8a24367c9355299fcf8438a42(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df36a7c74d6d2d1f168216bdf55f5b9c6699edad44965470a30eea7983786132(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f970033413b65cd5ea91ac0d063fd19875e9d066694dcb983b74553243f5f7d3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    dynamo_db_gateway_interface: typing.Optional[builtins.bool] = None,
    s3_gateway_interface: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db27ca13d06e1bdec88c7fe57e45dab839525425fd9867066af33785516dfd3(
    *,
    services: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InterfaceVpcEndpointAwsService],
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    dynamo_db_gateway_interface: typing.Optional[builtins.bool] = None,
    s3_gateway_interface: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b72ccaa8adb0b093daefe827dfeaaabcacbafb19a06a9c5e0ac5a11938a0302(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    org_id: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0764ca0676ca4e5b53724b53e8505a9aa92aaa3d13a4c4a8097d5d063c130fb(
    *,
    org_id: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eefe32aca0c0c27b7a0521a3ee4b00641400743736777fb3defce6acbaf6e482(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domains: typing.Sequence[builtins.str],
    resolvers: R53Resolverendpoints,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff0976b8e2c7097d1f5dc6b7644236dc11eb8d5644975ed7d88524fd8fbccde2(
    *,
    domains: typing.Sequence[builtins.str],
    resolvers: R53Resolverendpoints,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37f3a4e0c0f78aa85706cbccf62ee78c015085c09ce18d7e3171779b4f115c3e(
    *,
    subnet_groups: typing.Sequence[builtins.str],
    accept_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    deny_route_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb29b77f94b56b505b6c2c5885a56172e7ca09a17cfb0c14ba33808dbcea3425(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    amazon_side_asn: builtins.str,
    attachment_segment: builtins.str,
    cloudwan: CoreNetwork,
    description: builtins.str,
    cloud_wan_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_route_in_segments: typing.Optional[typing.Sequence[builtins.str]] = None,
    tg_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a749f884289c3b1b00cfed1607d4ab9219948805b406babba0241b61a66980(
    dxgatewayname: builtins.str,
    dxgateway_asn: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a582a3310b9d9bbcd8a7bd02e249755b178189dcb43fab2184c04d9f52288287(
    name: builtins.str,
    *,
    customer_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway,
    vpnspec: typing.Union[VpnSpecProps, typing.Dict[builtins.str, typing.Any]],
    sampleconfig: typing.Optional[typing.Union[SampleConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    tunnel_inside_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    tunnel_ipam_pool: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e39e0dbcc76625bee417f01cedc235a6a125d94888fb2d473ea145ed6e23cc71(
    dxgateway_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35903c80af58b933a9eb6be3b8f3d0a16c92d48809d6788f9db10d1999916d3f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab56d42d34969c2bd9f2d0c0dfd933a8f1ced07a1155adc2777f3acca95c52ec(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    forwarding_rules: typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]],
    inbound_resolver_targets: typing.Sequence[typing.Union[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty, typing.Dict[builtins.str, typing.Any]]],
    outbound_resolver: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb9f43082cc19789437ca0b32ac0dee01dabe6b5e810370a064ac78784f0bab5(
    *,
    forwarding_rules: typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]],
    inbound_resolver_targets: typing.Sequence[typing.Union[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty, typing.Dict[builtins.str, typing.Any]]],
    outbound_resolver: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d69f0d4ac1dd4d32be48193e8657e6e603a0da7f16ae2060f00bceb211d237ea(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asn_ranges: typing.Sequence[builtins.str],
    core_name: builtins.str,
    edge_locations: typing.Sequence[typing.Mapping[typing.Any, typing.Any]],
    global_network: _aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork,
    policy_description: builtins.str,
    inside_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    non_production: typing.Optional[builtins.bool] = None,
    vpn_ecmp_support: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e154261c8d8ada3b98f2138184a44fefc2492e5d175f2b644c9dcbff0a5cbff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d8d9d78df11641cadacc6be41ae118118eda35deb292c8b7ba3d97901aa39ed(
    *,
    asn_ranges: typing.Sequence[builtins.str],
    core_name: builtins.str,
    edge_locations: typing.Sequence[typing.Mapping[typing.Any, typing.Any]],
    global_network: _aws_cdk_aws_networkmanager_ceddda9d.CfnGlobalNetwork,
    policy_description: builtins.str,
    inside_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    non_production: typing.Optional[builtins.bool] = None,
    vpn_ecmp_support: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aad58423dfd9c9282af79c2ce35fe1789b6efc72243a5fc6c2e901753748c92(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: ICoreNetworkSegmentProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51cfde600436c072d891cab49866b9f2ee7f2642180d23d5e2c852838f036b0e(
    *,
    allow_external_principals: builtins.bool,
    principals: typing.Sequence[builtins.str],
    tags: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Tag]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15d475e1dfe6143decefea037f09f52430679483d15c8667d92f99470a428279(
    *,
    account_id: builtins.str,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de865a5997bc56fe43d8ce21d028b11240580380c9b95cec1f20db1fb5d0fc36(
    scope: _constructs_77d1e7e8.Construct,
    name: builtins.str,
    *,
    parameter_name: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b35276fef9aaadf334d01c1bda2534679412d73d2ef32e2a051fe134bda71b3(
    *,
    parameter_name: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec477d468b63ff52e7327d9699d8f84bbb43365503e15a5175ee369d1d9c5e5a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: builtins.str,
    parameter_name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc56bfcf424dfe9d100d1563d89f74d4a3839f6febe702c27e8170a1c9beeee(
    *,
    description: builtins.str,
    parameter_name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffebcb42a0726f006998f99544c3ede9b4099ae03b234ab0394f33c3137b7c5f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    crowdstrike_cloud: CrowdStrikeCloud,
    peering_vpc: typing.Optional[typing.Union[VpcRegionId, typing.Dict[builtins.str, typing.Any]]] = None,
    use_elb_in_peered_vpc: typing.Optional[builtins.bool] = None,
    vpccidr: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4bc1edb40dd5c6bb20b33a2c5745db6e1638fec1fc54372ced20d15e9ce1b3f(
    *,
    crowdstrike_cloud: CrowdStrikeCloud,
    peering_vpc: typing.Optional[typing.Union[VpcRegionId, typing.Dict[builtins.str, typing.Any]]] = None,
    use_elb_in_peered_vpc: typing.Optional[builtins.bool] = None,
    vpccidr: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa94e43c8721e381721a04fc4958c7ff8eb7d938b3d41752557e9133dde32243(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    crowdstrike_region: CrowdStrikeCloud,
    download: builtins.str,
    downloadhosted_zone: builtins.str,
    downloadhosted_zone_name: builtins.str,
    proxy: builtins.str,
    proxyhosted_zone: builtins.str,
    proxyhosted_zone_name: builtins.str,
    region: builtins.str,
    routeresolver_endpoints: R53Resolverendpoints,
    subnet_group_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31bf94f415dccb4fff277aab10a278965f63a87bb3b9378ee0debcf0201d9c07(
    *,
    crowdstrike_region: CrowdStrikeCloud,
    download: builtins.str,
    downloadhosted_zone: builtins.str,
    downloadhosted_zone_name: builtins.str,
    proxy: builtins.str,
    proxyhosted_zone: builtins.str,
    proxyhosted_zone_name: builtins.str,
    region: builtins.str,
    routeresolver_endpoints: R53Resolverendpoints,
    subnet_group_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef063a79cf88ea36bb3eae03b4dcf95e11322ae142c55a90853abe504833fa1f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    crowd_strike_cloud: CrowdStrikeCloud,
    subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    peeredwith_nlb: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101a5de77d7995d965c3dd27954a1bc313383831fa78f60d7477a160b1455dbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__762d57b647a8727640ef0a995696d6dbefa635f2d763282d959e1b53d29770ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c30e6e377907e1959384d313cc5be24ea9842b7740c5130caf72c94186d10d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eb5937738f1214afd9753148e64c8a28555093cf0307af743c04f39ddd773ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3477df0425028aaee09618274f1d539f801795c4c38b6f17bde652101919a23e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3fff76ea406ed95e68b875bf14c36653d990524981d3a8667fa254b5aac8756(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acb41629822375b876405c2e97949aeae0b5e4cd893b29dd65ab99428118420b(
    *,
    crowd_strike_cloud: CrowdStrikeCloud,
    subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    peeredwith_nlb: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e09c7128ef3c527e4e481fc7777416d58ff6626f2d6af1b1863ecac308cac38(
    *,
    aws_region: CrowdStrikeRegion,
    download_server: typing.Union[Endpoint, typing.Dict[builtins.str, typing.Any]],
    sensor_proxy: typing.Union[Endpoint, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2dea084fa06e88b853d7f1933973fc231cbd4910f6bf4c20e1e9f6a7fc677cf(
    *,
    name: builtins.str,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3610da9d5b891a4e6b0a8366a67b956c293ea9cb1f0f5192031aa4c1f275de7e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a6447b9db09c3ca16635723dcd1c3dd8484df4227e85933c8b5c7ed0b86b387(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9564509b247284681687a116db4d26261741dec040bb86ed1888d7db69fb4dd(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f22444b4e77cb1262a6ec0d54a52802126e90fe5803f035cfd951f34a443a4(
    *,
    arn: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9778d1e2bd39762ff9a481ba772e5cf6ea7fd9a18b2029efbe29a55ab4fbe49(
    *,
    cidr_mask: jsii.Number,
    name: builtins.str,
    subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c52b59ab47a2338bcbeefa82be24348493edae2775e4f23b3235bfa2f01e071(
    *,
    cidr_mask: jsii.Number,
    name: builtins.str,
    subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__818e82f2f3642febbe23ff995a92b8a16542fcff3868a7dcd520321ea9e2615e(
    *,
    dns_name: builtins.str,
    vpc_endpoint_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__361675112f01ab7162d06b299e2fcc929aca509564dc016bac71d2055c809f52(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instances: typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.Instance]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f04124053150c2636978544b5a82d349f2146ce45774c3c74a75545559df5e1(
    *,
    instances: typing.Union[_aws_cdk_aws_ec2_ceddda9d.Instance, typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.Instance]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdc1ab7ca620afda18c8e46c55dea88e3fd0a922041aced408cd57b8c51012dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    evpc: typing.Optional[typing.Union[EvpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d011cebb642eca028febd2f25247291ba13e5813177bfa2e8ce2135ec9db51bc(
    domains: typing.Sequence[builtins.str],
    search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34631fdbeb7b93146107b6c0dffe233263a5ba32febb8343cca95be1639dbfd7(
    forwarding_rules: typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04de5cec5fe4406cb3d639b8c9bd46012b982148ad5767e8fce8764de2f0dd6e(
    rolename: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c22df7393382e68ea1bc7dd6e832123e65d420e84bb886668b2891fa6e24fb2(
    firewall_name: builtins.str,
    firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
    subnet: SubnetGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026fa0ce348808ebb0b9a13b4ea23512d9c3141bf4689b47faedb69c76605f51(
    zonename: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9fb5804364c12d2abceab3cf5edd4b0259eaf88a27ca12924c87bc94c757203(
    subnet: SubnetGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97a4cbf25e8de5c9938ee88e6ca31447095567e59faff8056131f03d703cb380(
    domain_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c1eee126bd092a7ed622b6bc5daf117333f0764d8ddfa3c179eb4aebd36477(
    zone_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a66129ead079a49202db8526d78b98ac50a7eec35ca2146722f07276f325a957(
    name: builtins.str,
    subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    org_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcaa6f55ea2178f5d30e58a2b4cf75cdb6c8e9597e3e5a6774752de6502b2db9(
    router_groups: typing.Sequence[typing.Union[RouterGroup, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9173e9273f1a33d7c93f62cec389e335b569fe20db79ed3bd461319d6de473ac(
    value: typing.List[SubnetGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41133eb7dbe9e312de9fc8e86158aa46045e32f46a96137d19e38414710389e1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d031450a64b3312e6d41ff8a3fd8dd4d89d2e443f14b459f50f55104e44734c9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee15e42b6d9794a2c135f02d160d2104b488c3f0468ecbc2f26146b8f4fd6e60(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaba029615705f209a5105315a32273fba7fcf8f610587d51aa016e1d03eaeab(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__832c7caf59e0d9f05ac7e78ea6fb51e11e62e93883f61adab1ff709a73d8cb20(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c77f9b016ba3a9508037ef698fb3ebc7e084dd4ba557480d635f6a76cf3615(
    value: typing.Optional[R53Resolverendpoints],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cad7d61f378dbe6a4150f8261ada78d5df85573aeac9c3a5b188d73cae14b83(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60a740df0241049f39779114886dc0376d5b8baecee696d9da10f6f69b2eb2d3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ebffe131fe32db4dffe841056a993a780810db780b119f65dcf0876c338178d(
    value: typing.Optional[_aws_cdk_ceddda9d.CustomResource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a5c5d6650d11694c0dc1b772e361f6ea204401cb9978a4f1c11aaf6bb2e99ae(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df2b5419ea609f9b0e6e4898ace5dc2a5298dfb0e2e399f6bcc24b3984b20e98(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05dbb65456686ae87770a91158ef46250fddd6acb2a66551f63e13c9986e4950(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afca2bdc03f3a5195c7af4eefa5474a6146c184f16de07e31ec2870f77042189(
    *,
    evpc: typing.Optional[typing.Union[EvpcProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Vpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1738f5f8156456fa14dee204ef76e7aeac25f6d6ba479fff6ba44343dbe45e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    enterprise_domain_name: builtins.str,
    local_vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    hub_vpcs: typing.Optional[typing.Sequence[typing.Union[HubVpc, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7e104e76bcc3465a5d6e5e975bb4878d75e482d7980320daba8ba9bc733682f(
    *,
    enterprise_domain_name: builtins.str,
    local_vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    hub_vpcs: typing.Optional[typing.Sequence[typing.Union[HubVpc, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c71f8ffee31b0d69c71d1de6da5d0dac06c4cd197e90f7039f904e7efb5583e(
    *,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    cidr: typing.Optional[builtins.str] = None,
    default_instance_tenancy: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.DefaultInstanceTenancy] = None,
    enable_dns_hostnames: typing.Optional[builtins.bool] = None,
    enable_dns_support: typing.Optional[builtins.bool] = None,
    flow_logs: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.FlowLogOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.GatewayVpcEndpointOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    ip_addresses: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IIpAddresses] = None,
    max_azs: typing.Optional[jsii.Number] = None,
    nat_gateway_provider: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.NatProvider] = None,
    nat_gateways: typing.Optional[jsii.Number] = None,
    nat_gateway_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    reserved_azs: typing.Optional[jsii.Number] = None,
    restrict_default_security_group: typing.Optional[builtins.bool] = None,
    subnet_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_name: typing.Optional[builtins.str] = None,
    vpn_connections: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_ec2_ceddda9d.VpnConnectionOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpn_gateway: typing.Optional[builtins.bool] = None,
    vpn_gateway_asn: typing.Optional[jsii.Number] = None,
    vpn_route_propagation: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    subnet_groups: typing.Optional[typing.Sequence[SubnetGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71a1c56f02739823263b092ff943772c7f2f3391bbd9942383cc59c28445c85(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    fqdn: builtins.str,
    priority: typing.Optional[jsii.Number] = None,
    rules_database: typing.Optional[StatefulRuleDatabase] = None,
    action: StatefulAction,
    destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    dest_port: builtins.str,
    direction: Direction,
    name: builtins.str,
    protocol: FWProtocol,
    source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    src_port: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1dc98d03f57fd069d01e4d62cb4521f4fff2753c6c297e602bcf52009e8f815(
    value: typing.List[PrefixListSetInterface],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9835146b6489851a86a445db60d09fabc4f10c8520b89ee215a5ba579ba743b0(
    value: typing.List[DynamicTagResourceGroupSet],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4646f6ea85d216f3e1001ae364c19dcb179116d463a950aab77e0ab75de4874(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__403c3d7329242d2884e1364b9b347b4ae549506aa47a47265328d234cb688ae6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    prefix_list_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__988f77e5525890d84b5195080d891f202ad0be409e970f2722d1fe604d9a224e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__277873ef1815cd4375f45230f8c14cdfacebbf62958d5b95d9171fbc0e95c5c7(
    *,
    prefix_list_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a8230a8020f69654e71e875cdb4a008df6c2aedff4e5c47d086c06f7aeb4ca(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    policy_name: builtins.str,
    stateless_default_actions: typing.Sequence[StatelessActions],
    stateless_fragment_default_actions: typing.Sequence[StatelessActions],
    stateful_engine_options: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9cfb4f0f86bbf9c98d004a456d22f8297a5b16955ddc4b98897f84b2ccad1cf(
    value: IFirewallPolicyProperty,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9bc423a66b0b183dffcf44586b486d0a85effb8f2d8e036e9a75bccd5243de(
    *,
    policy_name: builtins.str,
    stateless_default_actions: typing.Sequence[StatelessActions],
    stateless_fragment_default_actions: typing.Sequence[StatelessActions],
    stateful_engine_options: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42834d58702d51be011948142d606971c35a7a6253e4a9c471a8d22a3ac06620(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    local_athena_querys: typing.Optional[builtins.bool] = None,
    one_minute_flow_logs: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05890aaf0a6855cc0a67fa9b2b36f753278d6fa228bcb7ac4009cac06f0f999c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domains: typing.Sequence[builtins.str],
    resolver_id: builtins.str,
    resolver_ip: typing.Sequence[builtins.str],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c36a2f748867f71db259c42e27b1a718cd12b8ad5db77c5db873f54d5c0535(
    *,
    domains: typing.Sequence[builtins.str],
    resolver_id: builtins.str,
    resolver_ip: typing.Sequence[builtins.str],
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d9a4b1d87dfaf4886011b85a178d769c4555464180743d2dfc0f4bc299fcad0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ipam_pool_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e460b06579855f3c47c23ff63809c00e4ebf1d00a865a6ced39224341a328c(
    *,
    ipam_pool_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adf25443d7eab2a79bd6c7aff8feceed1186079a3ebf8236907e6c136b15e59b(
    *,
    region: builtins.str,
    cross_account: typing.Optional[typing.Union[CrossAccountProps, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_search_tag: typing.Optional[_aws_cdk_ceddda9d.Tag] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e84973a37cf83d7492090bb53b8deefc4986415f2da11b0d0e2b7881bb92c53f(
    value: typing.List[_aws_cdk_ceddda9d.CustomResource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f7c75ef9e439a56d4b8da713118abcac8949ac40e6ba091b109a83d67cc7ad5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c21b8c7634a7f7d7f04c33b8cf21a647e090125acde48fcdc7efee9f1319425c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574771ee94345404b780f607457fdbe3c9ddb8405af72572ebea18d3f410950b(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a73f54a1bc47ccf1e89e86b9c4d2b74aed4d6f297a0a3c3e3895cd67fdcf8e(
    value: typing.Optional[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulEngineOptionsProperty, _aws_cdk_ceddda9d.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a996a5fccf377d9772c5038a84b997ceaab893d90c242c6452bbda7460ba9f(
    value: typing.Optional[typing.List[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7399cfadc4a3f8b69e62521388a0187a8b9c9b61920bb79299e881873be77a(
    value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.CustomActionProperty, _aws_cdk_ceddda9d.IResolvable]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e4c3089492574d56eab5f4795bea81c48cae99888ebe75c61768b6b03adb0af(
    value: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.List[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy.StatelessRuleGroupReferenceProperty, _aws_cdk_ceddda9d.IResolvable]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1118d4d354617e43640c6b4bd183c4c195e6f81259f0ea2b97cf9dc4d328f606(
    id: builtins.str,
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2aaf7e1f5b48a4247dd1cd4403833674cf827fafc31994ee21767cc61a5e272(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cidr: builtins.str,
    description: builtins.str,
    ipam_scope_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc6656dde547b7812a67b8afd3478eff13a118f6c465867fdf0e627743454480(
    *,
    cidr: builtins.str,
    description: builtins.str,
    ipam_scope_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8a4759ed6da59dfe209afa270ab624cb3b7ed696873d8361484494e28760740(
    *,
    firewall_account: builtins.str,
    rules_database: StatefulRuleDatabase,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90e35ceefff152d766401263c5496665d99299ecc4a08284c72f966fc3a26061(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    firewall_name: builtins.str,
    firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4b952a7d66418ce35108e0ba18fa17ae61dc5002414285789b9fe315d7bbd14(
    *,
    firewall_name: builtins.str,
    firewall_policy: _aws_cdk_aws_networkfirewall_ceddda9d.CfnFirewallPolicy,
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25fb206bba170d97d44c14aa6140b1abeeb3b05e10f9c01397d9333eee473895(
    *,
    domain: builtins.str,
    forward_to: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb1e9939d4c5b3a8591615d5d424abfaa69ffea061adb163568b47041ce8a5f(
    *,
    customer_managed_policy_reference: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    managed_policy_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55253cce89aed4d791e68500efad03101987a1350cdc0288c493507ad21311fc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    sso_instance_arn: builtins.str,
    aws_managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    customer_managed_policy_references: typing.Optional[typing.Sequence[typing.Union[CustomerManagedPolicyReference, typing.Dict[builtins.str, typing.Any]]]] = None,
    description: typing.Optional[builtins.str] = None,
    inline_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    permissions_boundary: typing.Optional[typing.Union[PermissionBoundary, typing.Dict[builtins.str, typing.Any]]] = None,
    relay_state_type: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6b6b6c2440db4f7b8a3cb442c56736e3021a34e9b531a8a1adec0439743d59(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    permission_set_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__868cb80778e19f4cab4d55459564ed396dbd5de0744627121f66f543566be074(
    id: builtins.str,
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350881e30013374e8d1acb6de938add1675e4e75ed5513d851cf42784422d7d8(
    *,
    permission_set_arn: builtins.str,
    sso_instance_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a171a9c43dcfb724cd216f311b8aa6bfa79e5b715facf56cb81f9a24d48f300(
    *,
    name: builtins.str,
    sso_instance_arn: builtins.str,
    aws_managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    customer_managed_policy_references: typing.Optional[typing.Sequence[typing.Union[CustomerManagedPolicyReference, typing.Dict[builtins.str, typing.Any]]]] = None,
    description: typing.Optional[builtins.str] = None,
    inline_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    permissions_boundary: typing.Optional[typing.Union[PermissionBoundary, typing.Dict[builtins.str, typing.Any]]] = None,
    relay_state_type: typing.Optional[builtins.str] = None,
    session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1027a4c14c05a475930afecf6876d01e3fbe3447efb9f4e196f1030fa725ad2d(
    *,
    cfg_secret_arn: builtins.str,
    hostname: builtins.str,
    instancetype: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f89944edffc01c967540f85f7ac38259e4b21036b25b5012f0aad955b75c8fd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    deploy_assets_path: builtins.str,
    gateways: typing.Sequence[typing.Union[PowerBIGateway, typing.Dict[builtins.str, typing.Any]]],
    initscript: builtins.str,
    r53zone_id: builtins.str,
    subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
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

def _typecheckingstub__90fb8c74ac7da5988587941a44a3c862f5cab40e8f8d8b3800e3bae005c7a96d(
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
    deploy_assets_path: builtins.str,
    gateways: typing.Sequence[typing.Union[PowerBIGateway, typing.Dict[builtins.str, typing.Any]]],
    initscript: builtins.str,
    r53zone_id: builtins.str,
    subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f169631dc3f57446cf71bb645416a8b2fee1b90ba4c396b0f77b600a2cf29bf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cfg_secret: typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret],
    hostname: builtins.str,
    initscript: builtins.str,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.WindowsImage,
    power_b_igateway_setup_script: typing.Union[_aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions, typing.Dict[builtins.str, typing.Any]],
    subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    zone: typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__329a72072a289b2419e9e9d6bc8e1677899a79f28543dcb5b4550781bc9b657c(
    peer: _aws_cdk_aws_ec2_ceddda9d.IPeer,
    connection: _aws_cdk_aws_ec2_ceddda9d.Port,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6695eb397954dd29a8cdb2221d08682e5bb89ef4d00d2f48a43ab1953e3c830(
    *,
    cfg_secret: typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret],
    hostname: builtins.str,
    initscript: builtins.str,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.WindowsImage,
    power_b_igateway_setup_script: typing.Union[_aws_cdk_aws_ec2_ceddda9d.S3DownloadOptions, typing.Dict[builtins.str, typing.Any]],
    subnet: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    zone: typing.Union[_aws_cdk_aws_route53_ceddda9d.IPrivateHostedZone, _aws_cdk_aws_route53_ceddda9d.PrivateHostedZone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed8b8c6139156db2a5c5a13578d5f943fdaec6daac0c2da4516a1dd3451486b(
    *,
    cidr: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd452c9798c65e7389eec7752fffd8000fafdfff9d32ae97511b6850d0d22257(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address_family: IPAddressFamily,
    max_entries: jsii.Number,
    prefix_list_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd9e5fb6cfe99ba47d1330567500f1c9c1dafc2a1a646ab68c81600d9d05a82(
    props: _aws_cdk_aws_ec2_ceddda9d.Instance,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66aa03a563701be1ff651f509dd8a52a57e90dd19e274fa135b8f4867ee095f4(
    *,
    cidr: builtins.str,
    description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73be9a6a017476bdafa3665c291260be5699d37d6b298ca08f9de3c23a8a035f(
    *,
    address_family: IPAddressFamily,
    max_entries: jsii.Number,
    prefix_list_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a6d3404c490595e939d5192d36f2b2b5867056ea39ecec90d8b47a6208f500(
    *,
    arn: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e48335e433f0f57ed6b1186775e793bbfd33327a5e3146e1ff9e4663d50e7f6(
    *,
    principal_id: builtins.str,
    principal_type: PrincipalTypes,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbcee769a1d537b4d2fab00f60f7cb0fa2d3b46cee3a33ffbe164ede042cbf5a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster_name: builtins.str,
    defaultrole: _aws_cdk_aws_iam_ceddda9d.Role,
    logging: typing.Union[_aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties, typing.Dict[builtins.str, typing.Any]],
    master_user: builtins.str,
    subnet_group: _aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup,
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    default_db_name: typing.Optional[builtins.str] = None,
    nodes: typing.Optional[jsii.Number] = None,
    node_type: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0980a865118e1af6aeeccee986b2101b76fbf35d5847e3615bd01e37ac8d292(
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5939847c42b4e20cba48915b9f96f0f0d824de99a9019d739a6e1c6ad418d1e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    outbound_forwarding_rules: typing.Optional[typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    tag_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0369cb0b1f59bc4e06d601fab9254ebc6b2159106022fcbda4d604f4433c0ff5(
    value: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6123ccfa405042dde0c23c0993ab98efa9931b16d86a50970750d05dfc7e257b(
    value: typing.List[_aws_cdk_aws_route53resolver_ceddda9d.CfnResolverRule.TargetAddressProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1094063679b17844a9a6bcbe59a18404a43b7557089a05a073489984270839d1(
    value: _aws_cdk_aws_route53resolver_ceddda9d.CfnResolverEndpoint,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf9a82844ec5ad8d302b61f22d9cd750ccadddd49debf38ba279dadb7aea52a(
    *,
    subnet_group: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.Vpc,
    outbound_forwarding_rules: typing.Optional[typing.Sequence[typing.Union[OutboundForwardingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    tag_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a94085e26e1c181a1169470d94a3f4635801196f4889342d7a947eadab7736f8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_redshift_alpha_9727f5af.Cluster,
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed403af7888b8b244abfc4d114767dba92ef07c6f6a7ec224f12ffde7cbc6e4c(
    statement_name: builtins.str,
    sql: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f4d0ab27b59fa94ebfe40cf8702cd39810625b3e7b24306718a70240c28e56(
    *,
    cluster: _aws_cdk_aws_redshift_alpha_9727f5af.Cluster,
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d07540578e6bf37b490f27feaf7c00b4f8d737adec44321a91b208ccda9cd72(
    *,
    cluster_name: builtins.str,
    defaultrole: _aws_cdk_aws_iam_ceddda9d.Role,
    logging: typing.Union[_aws_cdk_aws_redshift_alpha_9727f5af.LoggingProperties, typing.Dict[builtins.str, typing.Any]],
    master_user: builtins.str,
    subnet_group: _aws_cdk_aws_redshift_alpha_9727f5af.ClusterSubnetGroup,
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
    default_db_name: typing.Optional[builtins.str] = None,
    nodes: typing.Optional[jsii.Number] = None,
    node_type: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.NodeType] = None,
    parameter_group: typing.Optional[_aws_cdk_aws_redshift_alpha_9727f5af.ClusterParameterGroup] = None,
    preferred_maintenance_window: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72740c4c9691cb3c03ad9b89a24bedbec9c531d0d6601102d87cb5da92f4dcba(
    *,
    arn: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072ec932aab97c6d455caaf1abbe5d9e3a53b60498ad53c19b2aee522591a016(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    azcount: jsii.Number,
    subnet_group_name: builtins.str,
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa629fb86827eb17d4022f193cea09663e900e4be57501176c3da5238b16ea68(
    value: _aws_cdk_aws_ec2_ceddda9d.SubnetSelection,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8799ad0de50ad6006207cdb2d841dbf7fa28646d70c3dcaa7b0a8bc26f4a726a(
    *,
    azcount: jsii.Number,
    subnet_group_name: builtins.str,
    vpc: typing.Union[_aws_cdk_aws_ec2_ceddda9d.IVpc, _aws_cdk_aws_ec2_ceddda9d.Vpc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028e92a3698c6c2059fcc0e0af7aa3f7126cdc27fbf3664c78c792238416923f(
    *,
    description: builtins.str,
    destination: Destination,
    cidr: typing.Optional[builtins.str] = None,
    subnet: typing.Optional[typing.Union[SubnetGroup, SubnetWildCards]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc2dbc930d1298014e0060d53c8b233eeb195cad78ae6ab381d9fe994f8a6ca(
    *,
    routes: typing.Sequence[typing.Union[Route, typing.Dict[builtins.str, typing.Any]]],
    subnet_group: SubnetGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1397fe87954af98dd8ce47dc913ba3cd7d91e5a689f568c2cecc68f19a7f35e(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
    device_type: VpnDeviceType,
    ike_version: IkeVersion,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad73c81de0fdf06b1bc2118a228e935f94d004ca6fa6c015ed53b07d8eda7de(
    *,
    name: builtins.str,
    allow_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    deny_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    edge_locations: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
    isolate_attachments: typing.Optional[builtins.bool] = None,
    require_attachment_acceptance: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f75b795ff910f5f1d933a53230abe6dcd022435de4889f7ac995505c989fbf8e(
    *,
    action: SegmentActionType,
    description: builtins.str,
    destination_cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    destinations: typing.Optional[typing.Sequence[builtins.str]] = None,
    except_: typing.Optional[typing.Sequence[builtins.str]] = None,
    mode: typing.Optional[SegmentActionMode] = None,
    share_with: typing.Optional[typing.Union[builtins.str, typing.Sequence[builtins.str]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8d10fb497781360825742ed92db6bc2fcfef55e9f0384f09e93924bd6c10bb8(
    *,
    account: builtins.str,
    subnet_groups: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238e5e42f7cdb4a535125371146395c3c0dd23286e1152cf9deb86026e47092f(
    *,
    rule_number: jsii.Number,
    account: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc2d264382f5358f50d91a07bda53386b43a451e7bc0d8b965f7b3844ca683fd(
    *,
    description: builtins.str,
    share_with: typing.Union[builtins.str, typing.Sequence[CoreNetworkSegment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c1a896d83c1544a875e8e1298a81b96efeb6f0b5540511fa527bba9d3a8d57(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efea938c2146b49a87f0862a4e98800a2089ce649e7d6d0c193d71fca7838914(
    *,
    actions: typing.Sequence[StatelessActions],
    priority: jsii.Number,
    destination_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
    destinations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    protocols: typing.Optional[typing.Sequence[Protocol]] = None,
    source_ports: typing.Optional[typing.Sequence[typing.Union[builtins.str, jsii.Number]]] = None,
    sources: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.AddressProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tcp_flags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_networkfirewall_ceddda9d.CfnRuleGroup.TCPFlagFieldProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b4adb8148a3dbe5b310dc297e9c644624cf124b279b233e7f610829a9c177d6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cidr_mask: jsii.Number,
    name: builtins.str,
    subnet_type: _aws_cdk_aws_ec2_ceddda9d.SubnetType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__822960f47a8a5e3d6de87100b31930f291ea7dc6cfbddec109e2ac0140cbbfb7(
    value: ESubnetGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5270488f7a763f48e3dbd311971f86ae2d9ceac5a63f56487edc188a73236c6d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    capacity: jsii.Number,
    network_firewall_engine: typing.Union[NWFWRulesEngine, typing.Dict[builtins.str, typing.Any]],
    rule_group_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    suricata_rules: typing.Optional[typing.Sequence[FQDNStatefulRule]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49c44fc3a0863bca3329e1330cf3a4b0820d9a0e24204332b7dcc1f73887a0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4cb24897969e35bdb98f22dd64ce01688b6cb9f21bc5dbd08611c1194a8549a(
    *,
    capacity: jsii.Number,
    network_firewall_engine: typing.Union[NWFWRulesEngine, typing.Dict[builtins.str, typing.Any]],
    rule_group_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    suricata_rules: typing.Optional[typing.Sequence[FQDNStatefulRule]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc2a8241fae2f5903f2bc83964c0b9d700081541b3baae0202f362619e2eb38(
    *,
    action: StatefulAction,
    destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    dest_port: builtins.str,
    direction: Direction,
    name: builtins.str,
    protocol: FWProtocol,
    source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    src_port: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__633d08ef5b4861ae5b9673dd965b503c073be8e05307e2af9045399d40908c9c(
    *,
    amazon_side_asn: builtins.str,
    attachment_segment: builtins.str,
    cloudwan: CoreNetwork,
    description: builtins.str,
    cloud_wan_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_route_in_segments: typing.Optional[typing.Sequence[builtins.str]] = None,
    tg_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adad9f7d08060b34c3f11c538bbb13728f5d332abc13880a5250bee153fba4f9(
    *,
    key: builtins.str,
    values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5d35fc07ec304ec4d3b76aeab3adb397986e476eb14c4a54c3fc74ff8ba449(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance: _aws_cdk_aws_ec2_ceddda9d.Instance,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c4813a20b6f24b88269f6533f4b31e4dfe83b71e1bfe75cdce86f086039cf54(
    *,
    instance: _aws_cdk_aws_ec2_ceddda9d.Instance,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6ccdf3daa9eccce5525026206a90b42d3f4858e87368c528c8ec4e3330ea2a6(
    *,
    peering_vpc_id: builtins.str,
    peer_vpc_region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1752a38d3e09980986fc9172dcb3fd5eed134672e695a374f4a03eebfa237e(
    *,
    customer_gateway: _aws_cdk_aws_ec2_ceddda9d.CfnCustomerGateway,
    vpnspec: typing.Union[VpnSpecProps, typing.Dict[builtins.str, typing.Any]],
    sampleconfig: typing.Optional[typing.Union[SampleConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    tunnel_inside_cidr: typing.Optional[typing.Sequence[builtins.str]] = None,
    tunnel_ipam_pool: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CfnIPAMPool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c1da337aa49b63d2d1d5bca7dcc354e04c4bc02bf79fd140d56f6d7c166873(
    *,
    dpd_timeout_action: typing.Optional[DPDTimeoutAction] = None,
    dpd_timeout_seconds: typing.Optional[jsii.Number] = None,
    enable_acceleration: typing.Optional[builtins.bool] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    ike_versions: typing.Optional[typing.Sequence[IkeVersion]] = None,
    local_ipv4_network_cidr: typing.Optional[builtins.str] = None,
    outside_ip_address_type: typing.Optional[OutsideIpAddressType] = None,
    phase1_dh_group_numbers: typing.Optional[typing.Sequence[Phase1DHGroupNumbers]] = None,
    phase1_encryption_algorithms: typing.Optional[typing.Sequence[Phase1EncryptionAlgorithms]] = None,
    phase1_integrity_algorithms: typing.Optional[typing.Sequence[Phase1IntegrityAlgorithms]] = None,
    phase1_lifetime_seconds: typing.Optional[jsii.Number] = None,
    phase2_dh_group_numbers: typing.Optional[typing.Sequence[Phase2DHGroupNumbers]] = None,
    phase2_encryption_algorithms: typing.Optional[typing.Sequence[Phase2EncryptionAlgorithms]] = None,
    phase2_integrity_algorithms: typing.Optional[typing.Sequence[Phase2IntegrityAlgorithms]] = None,
    phase2_life_time_seconds: typing.Optional[jsii.Number] = None,
    rekey_fuzz_percentage: typing.Optional[jsii.Number] = None,
    rekey_margin_time_seconds: typing.Optional[jsii.Number] = None,
    remote_ipv4_network_cidr: typing.Optional[builtins.str] = None,
    replay_window_size: typing.Optional[jsii.Number] = None,
    startup_action: typing.Optional[StartupAction] = None,
    static_routes_only: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    tunnel_inside_ip_version: typing.Optional[TunnelInsideIpVersion] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__591a9551402313c51e363bd419ee497ab58a9f785dffff362a797994dbdd4d4a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    permission_set: IPermissionSet,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a18dedac1fb826fc6ecd1ce96fb2bd0c3e2ddbed84fc63b148ceabf414ab7b67(
    *,
    action: StatefulAction,
    destination: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    dest_port: builtins.str,
    direction: Direction,
    name: builtins.str,
    protocol: FWProtocol,
    source: typing.Union[builtins.str, PrefixList, DynamicTagResourceGroup],
    src_port: builtins.str,
    fqdn: builtins.str,
    priority: typing.Optional[jsii.Number] = None,
    rules_database: typing.Optional[StatefulRuleDatabase] = None,
) -> None:
    """Type checking stubs"""
    pass
