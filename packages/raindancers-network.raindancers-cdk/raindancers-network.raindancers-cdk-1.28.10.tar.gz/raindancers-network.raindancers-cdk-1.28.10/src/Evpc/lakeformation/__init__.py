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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8
from ..glue import GlueDataBase as _GlueDataBase_2c1b8f84


@jsii.data_type(
    jsii_type="raindancers-network.lakeformation.AddDatabaseProps",
    jsii_struct_bases=[],
    name_mapping={"database_name": "databaseName"},
)
class AddDatabaseProps:
    def __init__(self, *, database_name: builtins.str) -> None:
        '''(experimental) Glue Database that holds ingest Tables.

        :param database_name: (experimental) Name for database.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080053bab475964f15db7c6110a63479ca961e49c580c493be161552911f4deb)
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database_name": database_name,
        }

    @builtins.property
    def database_name(self) -> builtins.str:
        '''(experimental) Name for database.

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
        return "AddDatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="raindancers-network.lakeformation.AddNewBucketToLakeFormationProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "lifecycle_rules": "lifecycleRules", "role": "role"},
)
class AddNewBucketToLakeFormationProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param name: (experimental) Name of Bucket.
        :param lifecycle_rules: (experimental) Lifecycle Rules for objects that are stored in the Bucket. This will default to lifeccyle pattern that will eventually move unused obejects to glacier.
        :param role: (experimental) and optional role to use to join the Lake. This will default the the standard Service rule, if not specified, which is the recommended approach.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79532d49976958f40ea207b82e2730ddb43b3cff0cd53f6ee9fe8302ee894a5b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of Bucket.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]]:
        '''(experimental) Lifecycle Rules for objects that are stored in the Bucket.

        This will default to lifeccyle pattern that will
        eventually move unused obejects to glacier.

        :stability: experimental
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''(experimental) and optional role to use to join the Lake.

        This will default the the standard Service rule, if not
        specified, which is the recommended approach.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddNewBucketToLakeFormationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LakeFormation(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.lakeformation.LakeFormation",
):
    '''(experimental) Create a Class for the methods the methods that we use to operate on our 'Datalake'.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        make_cdk_exec_role_lake_admin: typing.Optional[builtins.bool] = None,
        nonproduction: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param make_cdk_exec_role_lake_admin: (experimental) The cdk exec role will be creating Datalake Objects so will require permission. Default: true
        :param nonproduction: (experimental) Opt out of Mechanisms for high data protection, that are appropriate for production. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1eadc78e3b2921cf3a834362415d38031d400a0a4aa2764ee5a3448bc8dd5d2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LakeFormationProps(
            make_cdk_exec_role_lake_admin=make_cdk_exec_role_lake_admin,
            nonproduction=nonproduction,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDatabase")
    def add_database(self, *, database_name: builtins.str) -> _GlueDataBase_2c1b8f84:
        '''
        :param database_name: (experimental) Name for database.

        :return: gluedatabase.GlueDataBase

        :stability: experimental
        '''
        props = AddDatabaseProps(database_name=database_name)

        return typing.cast(_GlueDataBase_2c1b8f84, jsii.invoke(self, "addDatabase", [props]))

    @jsii.member(jsii_name="addNewBucketToLakeFormation")
    def add_new_bucket_to_lake_formation(
        self,
        *,
        name: builtins.str,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) Create a new bucket and associate it to the the Lakeformation.

        :param name: (experimental) Name of Bucket.
        :param lifecycle_rules: (experimental) Lifecycle Rules for objects that are stored in the Bucket. This will default to lifeccyle pattern that will eventually move unused obejects to glacier.
        :param role: (experimental) and optional role to use to join the Lake. This will default the the standard Service rule, if not specified, which is the recommended approach.

        :return: s3.Bucket

        :stability: experimental
        '''
        props = AddNewBucketToLakeFormationProps(
            name=name, lifecycle_rules=lifecycle_rules, role=role
        )

        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.invoke(self, "addNewBucketToLakeFormation", [props]))

    @builtins.property
    @jsii.member(jsii_name="nonproduction")
    def nonproduction(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Used to determine if buckets are backedup, and protected from Stack Destruction.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "nonproduction"))

    @nonproduction.setter
    def nonproduction(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3a1bf435abef738e8f8ddd245b1e2ff9f54ecdff73c1e9626a78e3d20cf2b76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nonproduction", value)


@jsii.data_type(
    jsii_type="raindancers-network.lakeformation.LakeFormationProps",
    jsii_struct_bases=[],
    name_mapping={
        "make_cdk_exec_role_lake_admin": "makeCdkExecRoleLakeAdmin",
        "nonproduction": "nonproduction",
    },
)
class LakeFormationProps:
    def __init__(
        self,
        *,
        make_cdk_exec_role_lake_admin: typing.Optional[builtins.bool] = None,
        nonproduction: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param make_cdk_exec_role_lake_admin: (experimental) The cdk exec role will be creating Datalake Objects so will require permission. Default: true
        :param nonproduction: (experimental) Opt out of Mechanisms for high data protection, that are appropriate for production. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc70f2df22c68006edf39903411dcce76d913d85472e2ee40e6a3827e8a4a70a)
            check_type(argname="argument make_cdk_exec_role_lake_admin", value=make_cdk_exec_role_lake_admin, expected_type=type_hints["make_cdk_exec_role_lake_admin"])
            check_type(argname="argument nonproduction", value=nonproduction, expected_type=type_hints["nonproduction"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if make_cdk_exec_role_lake_admin is not None:
            self._values["make_cdk_exec_role_lake_admin"] = make_cdk_exec_role_lake_admin
        if nonproduction is not None:
            self._values["nonproduction"] = nonproduction

    @builtins.property
    def make_cdk_exec_role_lake_admin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The cdk exec role will be creating Datalake Objects so will require permission.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("make_cdk_exec_role_lake_admin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def nonproduction(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Opt out of Mechanisms for high data protection, that are appropriate for production.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("nonproduction")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LakeFormationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="raindancers-network.lakeformation.Permissions")
class Permissions(enum.Enum):
    '''(experimental) Permissions that can be used as part of a LakeFormation Permissions refer https://docs.aws.amazon.com/lake-formation/latest/APIReference/API_GrantPermissions.html.

    :stability: experimental
    '''

    ALL = "ALL"
    '''
    :stability: experimental
    '''
    SELECT = "SELECT"
    '''
    :stability: experimental
    '''
    ALTER = "ALTER"
    '''
    :stability: experimental
    '''
    DROP = "DROP"
    '''
    :stability: experimental
    '''
    DELETE = "DELETE"
    '''
    :stability: experimental
    '''
    INSERT = "INSERT"
    '''
    :stability: experimental
    '''
    DESCRIBE = "DESCRIBE"
    '''
    :stability: experimental
    '''
    CREATE_DATABASE = "CREATE_DATABASE"
    '''
    :stability: experimental
    '''
    CREATE_TABLE = "CREATE_TABLE"
    '''
    :stability: experimental
    '''
    DATA_LOCATION_ACCESS = "DATA_LOCATION_ACCESS"
    '''
    :stability: experimental
    '''
    CREATE_TAG = "CREATE_TAG"
    '''
    :stability: experimental
    '''
    ASSOCIATE = "ASSOCIATE"
    '''
    :stability: experimental
    '''
    CREATE_TABLE_READ_WRITE = "CREATE_TABLE_READ_WRITE"
    '''
    :stability: experimental
    '''


__all__ = [
    "AddDatabaseProps",
    "AddNewBucketToLakeFormationProps",
    "LakeFormation",
    "LakeFormationProps",
    "Permissions",
]

publication.publish()

def _typecheckingstub__080053bab475964f15db7c6110a63479ca961e49c580c493be161552911f4deb(
    *,
    database_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79532d49976958f40ea207b82e2730ddb43b3cff0cd53f6ee9fe8302ee894a5b(
    *,
    name: builtins.str,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1eadc78e3b2921cf3a834362415d38031d400a0a4aa2764ee5a3448bc8dd5d2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    make_cdk_exec_role_lake_admin: typing.Optional[builtins.bool] = None,
    nonproduction: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3a1bf435abef738e8f8ddd245b1e2ff9f54ecdff73c1e9626a78e3d20cf2b76(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc70f2df22c68006edf39903411dcce76d913d85472e2ee40e6a3827e8a4a70a(
    *,
    make_cdk_exec_role_lake_admin: typing.Optional[builtins.bool] = None,
    nonproduction: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
