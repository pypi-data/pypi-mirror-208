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

import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="raindancers-network.glue.AddClassifiersProps",
    jsii_struct_bases=[],
    name_mapping={"classifiers": "classifiers"},
)
class AddClassifiersProps:
    def __init__(self, *, classifiers: typing.Sequence["GlueClassifier"]) -> None:
        '''
        :param classifiers: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21bbbeeed6dd43a2cf896ceb23cfb33f3eba5c2423aecc629c97d1b31b01bac4)
            check_type(argname="argument classifiers", value=classifiers, expected_type=type_hints["classifiers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "classifiers": classifiers,
        }

    @builtins.property
    def classifiers(self) -> typing.List["GlueClassifier"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        assert result is not None, "Required property 'classifiers' is missing"
        return typing.cast(typing.List["GlueClassifier"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddClassifiersProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.glue.AddCrawlerProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "role": "role",
        "description": "description",
        "jdbc_targets": "jdbcTargets",
        "s3_targets": "s3Targets",
    },
)
class AddCrawlerProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
        description: typing.Optional[builtins.str] = None,
        jdbc_targets: typing.Optional[typing.Sequence["JDBCTarget"]] = None,
        s3_targets: typing.Optional[typing.Sequence["S3Target"]] = None,
    ) -> None:
        '''
        :param name: 
        :param role: 
        :param description: 
        :param jdbc_targets: 
        :param s3_targets: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c54d67af7bc0c0ead4ce28fe5e791441c0043c05c8aafecb7a82b50695e1fa)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument jdbc_targets", value=jdbc_targets, expected_type=type_hints["jdbc_targets"])
            check_type(argname="argument s3_targets", value=s3_targets, expected_type=type_hints["s3_targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "role": role,
        }
        if description is not None:
            self._values["description"] = description
        if jdbc_targets is not None:
            self._values["jdbc_targets"] = jdbc_targets
        if s3_targets is not None:
            self._values["s3_targets"] = s3_targets

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jdbc_targets(self) -> typing.Optional[typing.List["JDBCTarget"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("jdbc_targets")
        return typing.cast(typing.Optional[typing.List["JDBCTarget"]], result)

    @builtins.property
    def s3_targets(self) -> typing.Optional[typing.List["S3Target"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_targets")
        return typing.cast(typing.Optional[typing.List["S3Target"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddCrawlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Crawler(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.Crawler",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        database_name: builtins.str,
        name: builtins.str,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
        description: typing.Optional[builtins.str] = None,
        jdbc_targets: typing.Optional[typing.Sequence["JDBCTarget"]] = None,
        s3_targets: typing.Optional[typing.Sequence["S3Target"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param database_name: 
        :param name: 
        :param role: 
        :param description: 
        :param jdbc_targets: 
        :param s3_targets: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1d4627038270ea9efe3d960074a2b397eca10d627bb53c4f73af365ddfa92ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrawlerProps(
            database_name=database_name,
            name=name,
            role=role,
            description=description,
            jdbc_targets=jdbc_targets,
            s3_targets=s3_targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addClassifiers")
    def add_classifiers(
        self,
        *,
        classifiers: typing.Sequence["GlueClassifier"],
    ) -> None:
        '''(experimental) This will add classifers to the crawler.

        :param classifiers: 

        :stability: experimental
        '''
        props = AddClassifiersProps(classifiers=classifiers)

        return typing.cast(None, jsii.invoke(self, "addClassifiers", [props]))

    @jsii.member(jsii_name="addConfiguration")
    def add_configuration(self, configuration: builtins.str) -> None:
        '''(experimental) set crawler Configuration.

        :param configuration: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19192e432e8ae4a027ab2aec2ea86232bd39bcbcec304ffe89d3e4fc17f17779)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        return typing.cast(None, jsii.invoke(self, "addConfiguration", [configuration]))

    @jsii.member(jsii_name="addCrawlerSecurityConfiguration")
    def add_crawler_security_configuration(self, configuration: builtins.str) -> None:
        '''(experimental) add CrawlerSecurity Configuration.

        :param configuration: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0f7528a75405226f0c275289b194694046f754701a6293e266232646a8b692)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        return typing.cast(None, jsii.invoke(self, "addCrawlerSecurityConfiguration", [configuration]))

    @jsii.member(jsii_name="addRecrawlBehaviour")
    def add_recrawl_behaviour(self, *, recrawl_behavior: "RecrawlBehavior") -> None:
        '''(experimental) Set the recall  policy for the crawler.

        :param recrawl_behavior: 

        :return: void

        :stability: experimental
        '''
        recallpolicy = RecrawlPolicy(recrawl_behavior=recrawl_behavior)

        return typing.cast(None, jsii.invoke(self, "addRecrawlBehaviour", [recallpolicy]))

    @jsii.member(jsii_name="addSchedule")
    def add_schedule(self, schedule: builtins.str) -> None:
        '''(experimental) add schedule for the crawler.

        :param schedule: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ce18613ead649af1397475a817f939b80357cbc624f94971a0c0d9292e394ea)
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        return typing.cast(None, jsii.invoke(self, "addSchedule", [schedule]))

    @jsii.member(jsii_name="addSchemaChangePolicy")
    def add_schema_change_policy(
        self,
        *,
        delete_behavior: "DeleteBehavior",
        update_behavior: "UpdateBehavior",
    ) -> None:
        '''(experimental) Enable SchemaChangPolicy.

        :param delete_behavior: 
        :param update_behavior: 

        :stability: experimental
        '''
        schema_change_policy = SchemaChangePolicy(
            delete_behavior=delete_behavior, update_behavior=update_behavior
        )

        return typing.cast(None, jsii.invoke(self, "addSchemaChangePolicy", [schema_change_policy]))

    @jsii.member(jsii_name="addTablePrefix")
    def add_table_prefix(self, table_prefix: builtins.str) -> None:
        '''(experimental) add table prefix for the crawler.

        :param table_prefix: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4715028e9119ae6122e7fb027229192a5fabfc809c7e8c6126157aa6d6ede32e)
            check_type(argname="argument table_prefix", value=table_prefix, expected_type=type_hints["table_prefix"])
        return typing.cast(None, jsii.invoke(self, "addTablePrefix", [table_prefix]))

    @jsii.member(jsii_name="enableLineage")
    def enable_lineage(self, lineage: "CrawlerLineageSettings") -> None:
        '''(experimental) Enable Lineage for the Crawler.

        :param lineage: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0f30c1de962e69032c7589db15586c0b52b872f001a096a9864591762d7db6f)
            check_type(argname="argument lineage", value=lineage, expected_type=type_hints["lineage"])
        return typing.cast(None, jsii.invoke(self, "enableLineage", [lineage]))

    @jsii.member(jsii_name="useWithLakeFormation")
    def use_with_lake_formation(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        use_lake_formation_credentials: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Use the crawler with lakeFormation Permissions.

        :param account_id: 
        :param use_lake_formation_credentials: 

        :return: void

        :stability: experimental
        '''
        props = LakeFormationConfiguration(
            account_id=account_id,
            use_lake_formation_credentials=use_lake_formation_credentials,
        )

        return typing.cast(None, jsii.invoke(self, "useWithLakeFormation", [props]))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1946b83c65a6a83aba8cbfa67e871bdf3576f3f4d3227a31bff1091e585b451c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value)


@jsii.enum(jsii_type="raindancers-network.glue.CrawlerLineageSettings")
class CrawlerLineageSettings(enum.Enum):
    '''
    :stability: experimental
    '''

    ENABLE = "ENABLE"
    '''
    :stability: experimental
    '''
    DISABLE = "DISABLE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.glue.CrawlerProps",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "name": "name",
        "role": "role",
        "description": "description",
        "jdbc_targets": "jdbcTargets",
        "s3_targets": "s3Targets",
    },
)
class CrawlerProps:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        name: builtins.str,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
        description: typing.Optional[builtins.str] = None,
        jdbc_targets: typing.Optional[typing.Sequence["JDBCTarget"]] = None,
        s3_targets: typing.Optional[typing.Sequence["S3Target"]] = None,
    ) -> None:
        '''
        :param database_name: 
        :param name: 
        :param role: 
        :param description: 
        :param jdbc_targets: 
        :param s3_targets: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__081a5f652d1629273fb923009614e878c27dae3640b5793d42cb68c6e6085d72)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument jdbc_targets", value=jdbc_targets, expected_type=type_hints["jdbc_targets"])
            check_type(argname="argument s3_targets", value=s3_targets, expected_type=type_hints["s3_targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
            "name": name,
            "role": role,
        }
        if description is not None:
            self._values["description"] = description
        if jdbc_targets is not None:
            self._values["jdbc_targets"] = jdbc_targets
        if s3_targets is not None:
            self._values["s3_targets"] = s3_targets

    @builtins.property
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jdbc_targets(self) -> typing.Optional[typing.List["JDBCTarget"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("jdbc_targets")
        return typing.cast(typing.Optional[typing.List["JDBCTarget"]], result)

    @builtins.property
    def s3_targets(self) -> typing.Optional[typing.List["S3Target"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("s3_targets")
        return typing.cast(typing.Optional[typing.List["S3Target"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrawlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrawlerRole(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.CrawlerRole",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a9569c7781805cb4f0cb773aad2ed0166848fc7f32519d87dc505afc8d65e9d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "role"))

    @role.setter
    def role(self, value: _aws_cdk_aws_iam_ceddda9d.Role) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc6e24fe5b07b386be458d3bb83d9056e484eff77e81377029df96fbb96d57b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value)


@jsii.data_type(
    jsii_type="raindancers-network.glue.DataBaseProps",
    jsii_struct_bases=[],
    name_mapping={"database_name": "databaseName"},
)
class DataBaseProps:
    def __init__(self, *, database_name: builtins.str) -> None:
        '''
        :param database_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a64546ea453b2e66a93998f49ab38e7b74a4f1a0a1231397200cdd9ba3b65e)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
        }

    @builtins.property
    def database_name(self) -> builtins.str:
        '''
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
        return "DataBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.glue.DeleteBehavior")
class DeleteBehavior(enum.Enum):
    '''
    :stability: experimental
    '''

    LOG = "LOG"
    '''
    :stability: experimental
    '''
    DELETE_FROM_DATABASE = "DELETE_FROM_DATABASE"
    '''
    :stability: experimental
    '''
    DEPRECATE_IN_DATABASE = "DEPRECATE_IN_DATABASE"
    '''
    :stability: experimental
    '''


class GlueClassifier(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.GlueClassifier",
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
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__369c63f131b4e5ee09c74cf0ffe559ff2ff9cc8ee40c2869a65c4383d0121805)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GlueClassifierProps(name=name)

        jsii.create(self.__class__, self, [scope, id, props])

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
            type_hints = typing.get_type_hints(_typecheckingstub__b056345e977d4461c7bd1a8b597f9f7f5147b0b8fa003e1b2f801be99921d3be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="raindancers-network.glue.GlueClassifierProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class GlueClassifierProps:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32be144502d2a49bd3ac657ce033295bfd6b65e1bb2f62637440567eef277062)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }

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
        return "GlueClassifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlueDataBase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.GlueDataBase",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        database_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param database_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec0c0cd5fa376b56fd4dcd2347a98cb0cc1c33c26864da975c5550d96d02446)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DataBaseProps(database_name=database_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCrawler")
    def add_crawler(
        self,
        *,
        name: builtins.str,
        role: _aws_cdk_aws_iam_ceddda9d.Role,
        description: typing.Optional[builtins.str] = None,
        jdbc_targets: typing.Optional[typing.Sequence["JDBCTarget"]] = None,
        s3_targets: typing.Optional[typing.Sequence["S3Target"]] = None,
    ) -> Crawler:
        '''
        :param name: 
        :param role: 
        :param description: 
        :param jdbc_targets: 
        :param s3_targets: 

        :stability: experimental
        '''
        props = AddCrawlerProps(
            name=name,
            role=role,
            description=description,
            jdbc_targets=jdbc_targets,
            s3_targets=s3_targets,
        )

        return typing.cast(Crawler, jsii.invoke(self, "addCrawler", [props]))

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> _aws_cdk_aws_glue_ceddda9d.CfnDatabase:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnDatabase, jsii.get(self, "database"))

    @database.setter
    def database(self, value: _aws_cdk_aws_glue_ceddda9d.CfnDatabase) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c582ed254de5e814500ef29ec00737236acec5e64813c5a15cfc81ffd9c8a148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value)

    @builtins.property
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__067a1352d050f3bbff88a8948acb0727603f4cd0f7886a06bedd112d43c89292)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseName", value)


@jsii.interface(jsii_type="raindancers-network.glue.IJDBCTargetObject")
class IJDBCTargetObject(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @connection_name.setter
    def connection_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="enableAdditionalMetadata")
    def enable_additional_metadata(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @enable_additional_metadata.setter
    def enable_additional_metadata(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @exclusions.setter
    def exclusions(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @path.setter
    def path(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IJDBCTargetObjectProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.glue.IJDBCTargetObject"

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18c4b2034cb41f1776f9e8b3586ceceb93d944edcb8ff5e2bff59dd7146bb555)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value)

    @builtins.property
    @jsii.member(jsii_name="enableAdditionalMetadata")
    def enable_additional_metadata(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enableAdditionalMetadata"))

    @enable_additional_metadata.setter
    def enable_additional_metadata(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8143053bed19b9e22b0969822941966273079385e7ce50cbae1ad8c95d8ed501)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAdditionalMetadata", value)

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclusions"))

    @exclusions.setter
    def exclusions(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453bb9ce1fc0c2e221b86fc64dc980eb339f50f1d507220b002660cd1ffbaa6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclusions", value)

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))

    @path.setter
    def path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__933271b526d254e7ef08ed35c47982fc767d88191c963feee9616a0ff32a8588)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJDBCTargetObject).__jsii_proxy_class__ = lambda : _IJDBCTargetObjectProxy


@jsii.interface(jsii_type="raindancers-network.glue.IS3TargetObject")
class IS3TargetObject(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @path.setter
    def path(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @connection_name.setter
    def connection_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="dlqEventQueueArn")
    def dlq_event_queue_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @dlq_event_queue_arn.setter
    def dlq_event_queue_arn(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="eventQueueArn")
    def event_queue_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        ...

    @event_queue_arn.setter
    def event_queue_arn(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        ...

    @exclusions.setter
    def exclusions(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sampleSize")
    def sample_size(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        ...

    @sample_size.setter
    def sample_size(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IS3TargetObjectProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "raindancers-network.glue.IS3TargetObject"

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea045137173c1127fe27580766d4b7d400fc336594d3888f037c6e7db5cb8224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b05b3aac36645ab01b48afb86215a10fe0a9d11648e22801d238f1286b2632ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value)

    @builtins.property
    @jsii.member(jsii_name="dlqEventQueueArn")
    def dlq_event_queue_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dlqEventQueueArn"))

    @dlq_event_queue_arn.setter
    def dlq_event_queue_arn(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__314cebbc4279f08d358f0c7bc1b8c6fac50cb8e3672fc03058302b608639e223)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dlqEventQueueArn", value)

    @builtins.property
    @jsii.member(jsii_name="eventQueueArn")
    def event_queue_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventQueueArn"))

    @event_queue_arn.setter
    def event_queue_arn(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf57e5d32b5e11925d1dbf6a475a8276203946319811023e8a31eb316837e38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventQueueArn", value)

    @builtins.property
    @jsii.member(jsii_name="exclusions")
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "exclusions"))

    @exclusions.setter
    def exclusions(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__803b7956937dda62121461e9e6b4370763c2ea0bf3bb556bfa4a78a046a0f3b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exclusions", value)

    @builtins.property
    @jsii.member(jsii_name="sampleSize")
    def sample_size(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sampleSize"))

    @sample_size.setter
    def sample_size(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3735ebc2bbcb2c99404c10de1f7f973d93d89afd6ecb34818b1ad61a44f7d380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sampleSize", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IS3TargetObject).__jsii_proxy_class__ = lambda : _IS3TargetObjectProxy


class JDBCTarget(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.JDBCTarget",
):
    '''(experimental) This class is incomplete.

    It will not run. the Class needs to exisit
    so, as the add crawler method requires it.
    TODO:

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7cc10d0a1f821d7efea9b0dff972a0fdf083acca512aab97128b20ce5239b04)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> IJDBCTargetObject:
        '''
        :stability: experimental
        '''
        return typing.cast(IJDBCTargetObject, jsii.get(self, "target"))

    @target.setter
    def target(self, value: IJDBCTargetObject) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__099298c6bfdc5ef1bd0c41bda70923a4826a181b5fd748caecdd2941ddd9028d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)


@jsii.data_type(
    jsii_type="raindancers-network.glue.JDBCTargetProps",
    jsii_struct_bases=[],
    name_mapping={
        "enable_additional_metadata": "enableAdditionalMetadata",
        "connection_name": "connectionName",
        "exclusions": "exclusions",
    },
)
class JDBCTargetProps:
    def __init__(
        self,
        *,
        enable_additional_metadata: typing.Sequence["MetaDataTypes"],
        connection_name: typing.Optional[builtins.str] = None,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param enable_additional_metadata: 
        :param connection_name: 
        :param exclusions: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9370ed5ab33a67d789ddbbfa20c2baa9d18e664daedf913a7545b0be5e27d663)
            check_type(argname="argument enable_additional_metadata", value=enable_additional_metadata, expected_type=type_hints["enable_additional_metadata"])
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument exclusions", value=exclusions, expected_type=type_hints["exclusions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enable_additional_metadata": enable_additional_metadata,
        }
        if connection_name is not None:
            self._values["connection_name"] = connection_name
        if exclusions is not None:
            self._values["exclusions"] = exclusions

    @builtins.property
    def enable_additional_metadata(self) -> typing.List["MetaDataTypes"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enable_additional_metadata")
        assert result is not None, "Required property 'enable_additional_metadata' is missing"
        return typing.cast(typing.List["MetaDataTypes"], result)

    @builtins.property
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exclusions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JDBCTargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.glue.LakeFormationConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "use_lake_formation_credentials": "useLakeFormationCredentials",
    },
)
class LakeFormationConfiguration:
    def __init__(
        self,
        *,
        account_id: typing.Optional[builtins.str] = None,
        use_lake_formation_credentials: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param account_id: 
        :param use_lake_formation_credentials: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43eb7624a675c26f53f6de1cacb38ab07a6fc5b08aed488c0c26a21dd65038ff)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument use_lake_formation_credentials", value=use_lake_formation_credentials, expected_type=type_hints["use_lake_formation_credentials"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account_id is not None:
            self._values["account_id"] = account_id
        if use_lake_formation_credentials is not None:
            self._values["use_lake_formation_credentials"] = use_lake_formation_credentials

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_lake_formation_credentials(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("use_lake_formation_credentials")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LakeFormationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.glue.LineageConfiguration",
    jsii_struct_bases=[],
    name_mapping={"crawler_lineage_settings": "crawlerLineageSettings"},
)
class LineageConfiguration:
    def __init__(self, *, crawler_lineage_settings: CrawlerLineageSettings) -> None:
        '''
        :param crawler_lineage_settings: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba4fbe9cae4556ad2c058065c0e5b9b8b7b451c05f4c6f86c00788eaed6062ae)
            check_type(argname="argument crawler_lineage_settings", value=crawler_lineage_settings, expected_type=type_hints["crawler_lineage_settings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "crawler_lineage_settings": crawler_lineage_settings,
        }

    @builtins.property
    def crawler_lineage_settings(self) -> CrawlerLineageSettings:
        '''
        :stability: experimental
        '''
        result = self._values.get("crawler_lineage_settings")
        assert result is not None, "Required property 'crawler_lineage_settings' is missing"
        return typing.cast(CrawlerLineageSettings, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LineageConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.glue.MetaDataTypes")
class MetaDataTypes(enum.Enum):
    '''
    :stability: experimental
    '''

    COMMENTS = "COMMENTS"
    '''
    :stability: experimental
    '''
    RAWTYPES = "RAWTYPES"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="raindancers-network.glue.RecrawlBehavior")
class RecrawlBehavior(enum.Enum):
    '''
    :stability: experimental
    '''

    CRAWL_EVERYTHING = "CRAWL_EVERYTHING"
    '''
    :stability: experimental
    '''
    CRAWL_NEW_FOLDERS_ONLY = "CRAWL_NEW_FOLDERS_ONLY"
    '''
    :stability: experimental
    '''
    CRAWL_EVENT_MODE = "CRAWL_EVENT_MODE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="raindancers-network.glue.RecrawlPolicy",
    jsii_struct_bases=[],
    name_mapping={"recrawl_behavior": "recrawlBehavior"},
)
class RecrawlPolicy:
    def __init__(self, *, recrawl_behavior: RecrawlBehavior) -> None:
        '''
        :param recrawl_behavior: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e41883b3383e667963955f5fa70bd8f1b83abbc55585d9dd3a9ef00ceebe116)
            check_type(argname="argument recrawl_behavior", value=recrawl_behavior, expected_type=type_hints["recrawl_behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "recrawl_behavior": recrawl_behavior,
        }

    @builtins.property
    def recrawl_behavior(self) -> RecrawlBehavior:
        '''
        :stability: experimental
        '''
        result = self._values.get("recrawl_behavior")
        assert result is not None, "Required property 'recrawl_behavior' is missing"
        return typing.cast(RecrawlBehavior, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecrawlPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.glue.S3Path",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "path": "path"},
)
class S3Path:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
        path: builtins.str,
    ) -> None:
        '''
        :param bucket: 
        :param path: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c24ab81f280b23693595cd3c4f21d35d2e3825da13fcf94ec0c914940564f91)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "path": path,
        }

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Path(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3Target(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.glue.S3Target",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        path: typing.Union[S3Path, typing.Dict[builtins.str, typing.Any]],
        connection_name: typing.Optional[builtins.str] = None,
        dlq_event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param path: 
        :param connection_name: 
        :param dlq_event_queue: 
        :param event_queue: 
        :param exclusions: 
        :param sample_size: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcf3035d12efd2d69558a693ac0ccf192d89544e781a5df96e5a2cdc1f3879d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = S3TargetProps(
            path=path,
            connection_name=connection_name,
            dlq_event_queue=dlq_event_queue,
            event_queue=event_queue,
            exclusions=exclusions,
            sample_size=sample_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="s3Arn")
    def s3_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "s3Arn"))

    @s3_arn.setter
    def s3_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__870de47416e3f6e920226f4fb7a8be5ca6287645f3097219bbab32924fabe3ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3Arn", value)

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> IS3TargetObject:
        '''
        :stability: experimental
        '''
        return typing.cast(IS3TargetObject, jsii.get(self, "target"))

    @target.setter
    def target(self, value: IS3TargetObject) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5ffbdbeed5dbd87a64178d84ecc66c06acce3ba9ebec474e80e24b88928dfa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value)


@jsii.data_type(
    jsii_type="raindancers-network.glue.S3TargetProps",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "connection_name": "connectionName",
        "dlq_event_queue": "dlqEventQueue",
        "event_queue": "eventQueue",
        "exclusions": "exclusions",
        "sample_size": "sampleSize",
    },
)
class S3TargetProps:
    def __init__(
        self,
        *,
        path: typing.Union[S3Path, typing.Dict[builtins.str, typing.Any]],
        connection_name: typing.Optional[builtins.str] = None,
        dlq_event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
        exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param path: 
        :param connection_name: 
        :param dlq_event_queue: 
        :param event_queue: 
        :param exclusions: 
        :param sample_size: 

        :stability: experimental
        '''
        if isinstance(path, dict):
            path = S3Path(**path)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddbb21e41162e4dc14199425af5f28f1b46e6b4321b51cd9081453c099c5a606)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument dlq_event_queue", value=dlq_event_queue, expected_type=type_hints["dlq_event_queue"])
            check_type(argname="argument event_queue", value=event_queue, expected_type=type_hints["event_queue"])
            check_type(argname="argument exclusions", value=exclusions, expected_type=type_hints["exclusions"])
            check_type(argname="argument sample_size", value=sample_size, expected_type=type_hints["sample_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }
        if connection_name is not None:
            self._values["connection_name"] = connection_name
        if dlq_event_queue is not None:
            self._values["dlq_event_queue"] = dlq_event_queue
        if event_queue is not None:
            self._values["event_queue"] = event_queue
        if exclusions is not None:
            self._values["exclusions"] = exclusions
        if sample_size is not None:
            self._values["sample_size"] = sample_size

    @builtins.property
    def path(self) -> S3Path:
        '''
        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(S3Path, result)

    @builtins.property
    def connection_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dlq_event_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("dlq_event_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def event_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("event_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue], result)

    @builtins.property
    def exclusions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exclusions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sample_size(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("sample_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3TargetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.glue.SchemaChangePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "delete_behavior": "deleteBehavior",
        "update_behavior": "updateBehavior",
    },
)
class SchemaChangePolicy:
    def __init__(
        self,
        *,
        delete_behavior: DeleteBehavior,
        update_behavior: "UpdateBehavior",
    ) -> None:
        '''
        :param delete_behavior: 
        :param update_behavior: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__428a1756d41d42c415ada7e6e63bf2f95ce3a4eedb34d2ad686d4d7aeada018c)
            check_type(argname="argument delete_behavior", value=delete_behavior, expected_type=type_hints["delete_behavior"])
            check_type(argname="argument update_behavior", value=update_behavior, expected_type=type_hints["update_behavior"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delete_behavior": delete_behavior,
            "update_behavior": update_behavior,
        }

    @builtins.property
    def delete_behavior(self) -> DeleteBehavior:
        '''
        :stability: experimental
        '''
        result = self._values.get("delete_behavior")
        assert result is not None, "Required property 'delete_behavior' is missing"
        return typing.cast(DeleteBehavior, result)

    @builtins.property
    def update_behavior(self) -> "UpdateBehavior":
        '''
        :stability: experimental
        '''
        result = self._values.get("update_behavior")
        assert result is not None, "Required property 'update_behavior' is missing"
        return typing.cast("UpdateBehavior", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SchemaChangePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.glue.UpdateBehavior")
class UpdateBehavior(enum.Enum):
    '''
    :stability: experimental
    '''

    LOG = "LOG"
    '''
    :stability: experimental
    '''
    UPDATE_IN_DATABASE = "UPDATE_IN_DATABASE"
    '''
    :stability: experimental
    '''


__all__ = [
    "AddClassifiersProps",
    "AddCrawlerProps",
    "Crawler",
    "CrawlerLineageSettings",
    "CrawlerProps",
    "CrawlerRole",
    "DataBaseProps",
    "DeleteBehavior",
    "GlueClassifier",
    "GlueClassifierProps",
    "GlueDataBase",
    "IJDBCTargetObject",
    "IS3TargetObject",
    "JDBCTarget",
    "JDBCTargetProps",
    "LakeFormationConfiguration",
    "LineageConfiguration",
    "MetaDataTypes",
    "RecrawlBehavior",
    "RecrawlPolicy",
    "S3Path",
    "S3Target",
    "S3TargetProps",
    "SchemaChangePolicy",
    "UpdateBehavior",
]

publication.publish()

def _typecheckingstub__21bbbeeed6dd43a2cf896ceb23cfb33f3eba5c2423aecc629c97d1b31b01bac4(
    *,
    classifiers: typing.Sequence[GlueClassifier],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c54d67af7bc0c0ead4ce28fe5e791441c0043c05c8aafecb7a82b50695e1fa(
    *,
    name: builtins.str,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
    description: typing.Optional[builtins.str] = None,
    jdbc_targets: typing.Optional[typing.Sequence[JDBCTarget]] = None,
    s3_targets: typing.Optional[typing.Sequence[S3Target]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1d4627038270ea9efe3d960074a2b397eca10d627bb53c4f73af365ddfa92ef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    database_name: builtins.str,
    name: builtins.str,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
    description: typing.Optional[builtins.str] = None,
    jdbc_targets: typing.Optional[typing.Sequence[JDBCTarget]] = None,
    s3_targets: typing.Optional[typing.Sequence[S3Target]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19192e432e8ae4a027ab2aec2ea86232bd39bcbcec304ffe89d3e4fc17f17779(
    configuration: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0f7528a75405226f0c275289b194694046f754701a6293e266232646a8b692(
    configuration: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ce18613ead649af1397475a817f939b80357cbc624f94971a0c0d9292e394ea(
    schedule: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4715028e9119ae6122e7fb027229192a5fabfc809c7e8c6126157aa6d6ede32e(
    table_prefix: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0f30c1de962e69032c7589db15586c0b52b872f001a096a9864591762d7db6f(
    lineage: CrawlerLineageSettings,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1946b83c65a6a83aba8cbfa67e871bdf3576f3f4d3227a31bff1091e585b451c(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__081a5f652d1629273fb923009614e878c27dae3640b5793d42cb68c6e6085d72(
    *,
    database_name: builtins.str,
    name: builtins.str,
    role: _aws_cdk_aws_iam_ceddda9d.Role,
    description: typing.Optional[builtins.str] = None,
    jdbc_targets: typing.Optional[typing.Sequence[JDBCTarget]] = None,
    s3_targets: typing.Optional[typing.Sequence[S3Target]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9569c7781805cb4f0cb773aad2ed0166848fc7f32519d87dc505afc8d65e9d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc6e24fe5b07b386be458d3bb83d9056e484eff77e81377029df96fbb96d57b(
    value: _aws_cdk_aws_iam_ceddda9d.Role,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a64546ea453b2e66a93998f49ab38e7b74a4f1a0a1231397200cdd9ba3b65e(
    *,
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__369c63f131b4e5ee09c74cf0ffe559ff2ff9cc8ee40c2869a65c4383d0121805(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b056345e977d4461c7bd1a8b597f9f7f5147b0b8fa003e1b2f801be99921d3be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32be144502d2a49bd3ac657ce033295bfd6b65e1bb2f62637440567eef277062(
    *,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec0c0cd5fa376b56fd4dcd2347a98cb0cc1c33c26864da975c5550d96d02446(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c582ed254de5e814500ef29ec00737236acec5e64813c5a15cfc81ffd9c8a148(
    value: _aws_cdk_aws_glue_ceddda9d.CfnDatabase,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__067a1352d050f3bbff88a8948acb0727603f4cd0f7886a06bedd112d43c89292(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18c4b2034cb41f1776f9e8b3586ceceb93d944edcb8ff5e2bff59dd7146bb555(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8143053bed19b9e22b0969822941966273079385e7ce50cbae1ad8c95d8ed501(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453bb9ce1fc0c2e221b86fc64dc980eb339f50f1d507220b002660cd1ffbaa6b(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__933271b526d254e7ef08ed35c47982fc767d88191c963feee9616a0ff32a8588(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea045137173c1127fe27580766d4b7d400fc336594d3888f037c6e7db5cb8224(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b05b3aac36645ab01b48afb86215a10fe0a9d11648e22801d238f1286b2632ff(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__314cebbc4279f08d358f0c7bc1b8c6fac50cb8e3672fc03058302b608639e223(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf57e5d32b5e11925d1dbf6a475a8276203946319811023e8a31eb316837e38(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__803b7956937dda62121461e9e6b4370763c2ea0bf3bb556bfa4a78a046a0f3b8(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3735ebc2bbcb2c99404c10de1f7f973d93d89afd6ecb34818b1ad61a44f7d380(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7cc10d0a1f821d7efea9b0dff972a0fdf083acca512aab97128b20ce5239b04(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099298c6bfdc5ef1bd0c41bda70923a4826a181b5fd748caecdd2941ddd9028d(
    value: IJDBCTargetObject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9370ed5ab33a67d789ddbbfa20c2baa9d18e664daedf913a7545b0be5e27d663(
    *,
    enable_additional_metadata: typing.Sequence[MetaDataTypes],
    connection_name: typing.Optional[builtins.str] = None,
    exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43eb7624a675c26f53f6de1cacb38ab07a6fc5b08aed488c0c26a21dd65038ff(
    *,
    account_id: typing.Optional[builtins.str] = None,
    use_lake_formation_credentials: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba4fbe9cae4556ad2c058065c0e5b9b8b7b451c05f4c6f86c00788eaed6062ae(
    *,
    crawler_lineage_settings: CrawlerLineageSettings,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e41883b3383e667963955f5fa70bd8f1b83abbc55585d9dd3a9ef00ceebe116(
    *,
    recrawl_behavior: RecrawlBehavior,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c24ab81f280b23693595cd3c4f21d35d2e3825da13fcf94ec0c914940564f91(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcf3035d12efd2d69558a693ac0ccf192d89544e781a5df96e5a2cdc1f3879d4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    path: typing.Union[S3Path, typing.Dict[builtins.str, typing.Any]],
    connection_name: typing.Optional[builtins.str] = None,
    dlq_event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    sample_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__870de47416e3f6e920226f4fb7a8be5ca6287645f3097219bbab32924fabe3ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ffbdbeed5dbd87a64178d84ecc66c06acce3ba9ebec474e80e24b88928dfa1(
    value: IS3TargetObject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddbb21e41162e4dc14199425af5f28f1b46e6b4321b51cd9081453c099c5a606(
    *,
    path: typing.Union[S3Path, typing.Dict[builtins.str, typing.Any]],
    connection_name: typing.Optional[builtins.str] = None,
    dlq_event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    event_queue: typing.Optional[_aws_cdk_aws_sqs_ceddda9d.Queue] = None,
    exclusions: typing.Optional[typing.Sequence[builtins.str]] = None,
    sample_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__428a1756d41d42c415ada7e6e63bf2f95ce3a4eedb34d2ad686d4d7aeada018c(
    *,
    delete_behavior: DeleteBehavior,
    update_behavior: UpdateBehavior,
) -> None:
    """Type checking stubs"""
    pass
