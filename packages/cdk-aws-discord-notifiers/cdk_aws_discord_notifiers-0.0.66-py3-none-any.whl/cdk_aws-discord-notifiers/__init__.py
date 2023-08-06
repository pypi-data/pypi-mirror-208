'''
# AWS CDK Discord Notifier Constructs

This is a CDK construct library the vends constructs used to notify via discord about resources in your CDK stack.

## Constructs

Currently a single construct is available, `MonthlyCostNotifier`. This construct will notify a discord webhook of the monthly billing for the account.

## Available Packages

This provider is built for the following languages:

* Javascript/Typescript
* Python
* C#

Details on how to find these packages are below and on [ConstructHub](https://constructs.dev/packages/@awlsring/cdk-aws-discord-notifiers)

### NPM

Javascript/Typescript package is available on NPM.

The npm package is viewable at https://www.npmjs.com/package/@awlsring/cdk-aws-discord-notifiers

```bash
npm install @awlsring/cdk-aws-discord-notifiers
```

### PyPi

Python package is available on PyPi.

The pypi package is viewable at https://pypi.org/project/cdk-aws-discord-notifiers/

```bash
pip install cdk-aws-discord-notifiers
```

### Nuget

C# package is available on Nuget.

The nuget package is viewable at https://www.nuget.org/packages/awlsring.CdkAwsDiscordNotifiers/

```bash
dotnet add package awlsring.CdkAwsDiscordNotifiers
```
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

import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="@awlsring/cdk-aws-discord-notifiers.LogLevel")
class LogLevel(enum.Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class MonthlyCostNotifier(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@awlsring/cdk-aws-discord-notifiers.MonthlyCostNotifier",
):
    '''A construct that creates a lambda function bundled with the 'monthly-notifier-lambda' code This is trigger via eventbridge on a schedule to post to a discord webhook for the monthly costts  WARNING: This lambda uses a pay per request API.

    Each call to cost explorer costs $0.01 USD.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        webhook: builtins.str,
        lambda_architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        lambda_log_level: typing.Optional[LogLevel] = None,
        lambda_name: typing.Optional[builtins.str] = None,
        lambda_role_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy] = None,
        rule_name: typing.Optional[builtins.str] = None,
        rule_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_id: The accountId this is being deployed to.
        :param webhook: The webhook to post to.
        :param lambda_architecture: The lambda architecture. Default: ARM_64
        :param lambda_log_level: The lambda log level. Default: MonthlyCostNotifier
        :param lambda_name: The lambda name. Default: MonthlyCostNotifier
        :param lambda_role_policy: An additional policy to attach to the lambda. Default: none
        :param rule_name: The eventbridge rule name. Default: MonthlyCostNotifierRule
        :param rule_schedule: The eventbridge rule schedule. Default: - { minute: '0', hour: '15', day: '1', month: '*', year: '*' }
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f750ebf7ff2f6b9cbfa79e41efe824c83dc3479df4530a0de50e14a6967283b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MonthlyCostNotifierProps(
            account_id=account_id,
            webhook=webhook,
            lambda_architecture=lambda_architecture,
            lambda_log_level=lambda_log_level,
            lambda_name=lambda_name,
            lambda_role_policy=lambda_role_policy,
            rule_name=rule_name,
            rule_schedule=rule_schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@awlsring/cdk-aws-discord-notifiers.MonthlyCostNotifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "webhook": "webhook",
        "lambda_architecture": "lambdaArchitecture",
        "lambda_log_level": "lambdaLogLevel",
        "lambda_name": "lambdaName",
        "lambda_role_policy": "lambdaRolePolicy",
        "rule_name": "ruleName",
        "rule_schedule": "ruleSchedule",
    },
)
class MonthlyCostNotifierProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        webhook: builtins.str,
        lambda_architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
        lambda_log_level: typing.Optional[LogLevel] = None,
        lambda_name: typing.Optional[builtins.str] = None,
        lambda_role_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy] = None,
        rule_name: typing.Optional[builtins.str] = None,
        rule_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''Properties for a MonthlyCostNotifier.

        :param account_id: The accountId this is being deployed to.
        :param webhook: The webhook to post to.
        :param lambda_architecture: The lambda architecture. Default: ARM_64
        :param lambda_log_level: The lambda log level. Default: MonthlyCostNotifier
        :param lambda_name: The lambda name. Default: MonthlyCostNotifier
        :param lambda_role_policy: An additional policy to attach to the lambda. Default: none
        :param rule_name: The eventbridge rule name. Default: MonthlyCostNotifierRule
        :param rule_schedule: The eventbridge rule schedule. Default: - { minute: '0', hour: '15', day: '1', month: '*', year: '*' }
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bcc77056382af1b2846479834ff3db4561c9852d8270e6f0b11bee4f0c88845)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument lambda_architecture", value=lambda_architecture, expected_type=type_hints["lambda_architecture"])
            check_type(argname="argument lambda_log_level", value=lambda_log_level, expected_type=type_hints["lambda_log_level"])
            check_type(argname="argument lambda_name", value=lambda_name, expected_type=type_hints["lambda_name"])
            check_type(argname="argument lambda_role_policy", value=lambda_role_policy, expected_type=type_hints["lambda_role_policy"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument rule_schedule", value=rule_schedule, expected_type=type_hints["rule_schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "webhook": webhook,
        }
        if lambda_architecture is not None:
            self._values["lambda_architecture"] = lambda_architecture
        if lambda_log_level is not None:
            self._values["lambda_log_level"] = lambda_log_level
        if lambda_name is not None:
            self._values["lambda_name"] = lambda_name
        if lambda_role_policy is not None:
            self._values["lambda_role_policy"] = lambda_role_policy
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if rule_schedule is not None:
            self._values["rule_schedule"] = rule_schedule

    @builtins.property
    def account_id(self) -> builtins.str:
        '''The accountId this is being deployed to.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def webhook(self) -> builtins.str:
        '''The webhook to post to.'''
        result = self._values.get("webhook")
        assert result is not None, "Required property 'webhook' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture]:
        '''The lambda architecture.

        :default: ARM_64
        '''
        result = self._values.get("lambda_architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture], result)

    @builtins.property
    def lambda_log_level(self) -> typing.Optional[LogLevel]:
        '''The lambda log level.

        :default: MonthlyCostNotifier
        '''
        result = self._values.get("lambda_log_level")
        return typing.cast(typing.Optional[LogLevel], result)

    @builtins.property
    def lambda_name(self) -> typing.Optional[builtins.str]:
        '''The lambda name.

        :default: MonthlyCostNotifier
        '''
        result = self._values.get("lambda_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_role_policy(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy]:
        '''An additional policy to attach to the lambda.

        :default: none
        '''
        result = self._values.get("lambda_role_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''The eventbridge rule name.

        :default: MonthlyCostNotifierRule
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule_schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The eventbridge rule schedule.

        :default: - { minute: '0', hour: '15', day: '1', month: '*', year: '*' }
        '''
        result = self._values.get("rule_schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MonthlyCostNotifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LogLevel",
    "MonthlyCostNotifier",
    "MonthlyCostNotifierProps",
]

publication.publish()

def _typecheckingstub__5f750ebf7ff2f6b9cbfa79e41efe824c83dc3479df4530a0de50e14a6967283b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    webhook: builtins.str,
    lambda_architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    lambda_log_level: typing.Optional[LogLevel] = None,
    lambda_name: typing.Optional[builtins.str] = None,
    lambda_role_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy] = None,
    rule_name: typing.Optional[builtins.str] = None,
    rule_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bcc77056382af1b2846479834ff3db4561c9852d8270e6f0b11bee4f0c88845(
    *,
    account_id: builtins.str,
    webhook: builtins.str,
    lambda_architecture: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.Architecture] = None,
    lambda_log_level: typing.Optional[LogLevel] = None,
    lambda_name: typing.Optional[builtins.str] = None,
    lambda_role_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Policy] = None,
    rule_name: typing.Optional[builtins.str] = None,
    rule_schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass
