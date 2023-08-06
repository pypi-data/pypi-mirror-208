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

import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


class PythonApiIngestToS3(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.apilambda.PythonApiIngestToS3",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        code_source: builtins.str,
        handler: builtins.str,
        ingest_bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
        env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
        secrets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code_source: 
        :param handler: 
        :param ingest_bucket: 
        :param env_vars: 
        :param runtime: 
        :param secrets: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b037af8ae9a2fae4590a5cf7e9778bae33d8bd82c90841d9550e6f9f32e473d9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PythonApiIngestToS3Props(
            code_source=code_source,
            handler=handler,
            ingest_bucket=ingest_bucket,
            env_vars=env_vars,
            runtime=runtime,
            secrets=secrets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, jsii.get(self, "function"))

    @function.setter
    def function(self, value: _aws_cdk_aws_lambda_ceddda9d.Function) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2d2fe726fee319d5de9872d529d6f7235145322c2f9de239dc552643ce585f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "function", value)


@jsii.data_type(
    jsii_type="raindancers-network.apilambda.PythonApiIngestToS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "code_source": "codeSource",
        "handler": "handler",
        "ingest_bucket": "ingestBucket",
        "env_vars": "envVars",
        "runtime": "runtime",
        "secrets": "secrets",
    },
)
class PythonApiIngestToS3Props:
    def __init__(
        self,
        *,
        code_source: builtins.str,
        handler: builtins.str,
        ingest_bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
        env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
        secrets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]] = None,
    ) -> None:
        '''
        :param code_source: 
        :param handler: 
        :param ingest_bucket: 
        :param env_vars: 
        :param runtime: 
        :param secrets: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea76e6607745f3de9eac39b86e443cf7cce7f91be35c6c80ec26669da9ef273)
            check_type(argname="argument code_source", value=code_source, expected_type=type_hints["code_source"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument ingest_bucket", value=ingest_bucket, expected_type=type_hints["ingest_bucket"])
            check_type(argname="argument env_vars", value=env_vars, expected_type=type_hints["env_vars"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code_source": code_source,
            "handler": handler,
            "ingest_bucket": ingest_bucket,
        }
        if env_vars is not None:
            self._values["env_vars"] = env_vars
        if runtime is not None:
            self._values["runtime"] = runtime
        if secrets is not None:
            self._values["secrets"] = secrets

    @builtins.property
    def code_source(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("code_source")
        assert result is not None, "Required property 'code_source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ingest_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingest_bucket")
        assert result is not None, "Required property 'ingest_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

    @builtins.property
    def env_vars(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def runtime(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime]:
        '''
        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.List[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonApiIngestToS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PythonApiIngestToS3",
    "PythonApiIngestToS3Props",
]

publication.publish()

def _typecheckingstub__b037af8ae9a2fae4590a5cf7e9778bae33d8bd82c90841d9550e6f9f32e473d9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    code_source: builtins.str,
    handler: builtins.str,
    ingest_bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
    env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
    secrets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d2fe726fee319d5de9872d529d6f7235145322c2f9de239dc552643ce585f8(
    value: _aws_cdk_aws_lambda_ceddda9d.Function,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea76e6607745f3de9eac39b86e443cf7cce7f91be35c6c80ec26669da9ef273(
    *,
    code_source: builtins.str,
    handler: builtins.str,
    ingest_bucket: _aws_cdk_aws_s3_ceddda9d.Bucket,
    env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    runtime: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Runtime] = None,
    secrets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, _aws_cdk_aws_secretsmanager_ceddda9d.Secret]]] = None,
) -> None:
    """Type checking stubs"""
    pass
