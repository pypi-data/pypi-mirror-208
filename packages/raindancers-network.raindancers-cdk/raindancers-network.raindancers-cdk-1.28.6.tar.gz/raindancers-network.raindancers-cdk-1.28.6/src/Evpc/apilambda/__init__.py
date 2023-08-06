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

import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_secretsmanager
import constructs


class PythonApiIngestToS3(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.apilambda.PythonApiIngestToS3",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        code_source: builtins.str,
        handler: builtins.str,
        ingest_bucket: aws_cdk.aws_s3.Bucket,
        env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
        secrets: typing.Optional[typing.Sequence[typing.Union[aws_cdk.aws_secretsmanager.ISecret, aws_cdk.aws_secretsmanager.Secret]]] = None,
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
            type_hints = typing.get_type_hints(PythonApiIngestToS3.__init__)
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
    def function(self) -> aws_cdk.aws_lambda.Function:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "function"))

    @function.setter
    def function(self, value: aws_cdk.aws_lambda.Function) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(PythonApiIngestToS3, "function").fset)
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
        ingest_bucket: aws_cdk.aws_s3.Bucket,
        env_vars: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
        secrets: typing.Optional[typing.Sequence[typing.Union[aws_cdk.aws_secretsmanager.ISecret, aws_cdk.aws_secretsmanager.Secret]]] = None,
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
            type_hints = typing.get_type_hints(PythonApiIngestToS3Props.__init__)
            check_type(argname="argument code_source", value=code_source, expected_type=type_hints["code_source"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument ingest_bucket", value=ingest_bucket, expected_type=type_hints["ingest_bucket"])
            check_type(argname="argument env_vars", value=env_vars, expected_type=type_hints["env_vars"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
        self._values: typing.Dict[str, typing.Any] = {
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
    def ingest_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("ingest_bucket")
        assert result is not None, "Required property 'ingest_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def env_vars(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def runtime(self) -> typing.Optional[aws_cdk.aws_lambda.Runtime]:
        '''
        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Runtime], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.List[typing.Union[aws_cdk.aws_secretsmanager.ISecret, aws_cdk.aws_secretsmanager.Secret]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.List[typing.Union[aws_cdk.aws_secretsmanager.ISecret, aws_cdk.aws_secretsmanager.Secret]]], result)

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
