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

import constructs as _constructs_77d1e7e8


class Delay(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="raindancers-network.delay.Delay",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5958d692de8d35dc27baceb2b0016b47e6725c277a31214a0dd69a8042abfc8d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="delayProviderServiceToken")
    def delay_provider_service_token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "delayProviderServiceToken"))

    @delay_provider_service_token.setter
    def delay_provider_service_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae93e2a885ad2f7f634866b0cc198d3522076032d01005298eef297143e6db02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delayProviderServiceToken", value)


__all__ = [
    "Delay",
]

publication.publish()

def _typecheckingstub__5958d692de8d35dc27baceb2b0016b47e6725c277a31214a0dd69a8042abfc8d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae93e2a885ad2f7f634866b0cc198d3522076032d01005298eef297143e6db02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
