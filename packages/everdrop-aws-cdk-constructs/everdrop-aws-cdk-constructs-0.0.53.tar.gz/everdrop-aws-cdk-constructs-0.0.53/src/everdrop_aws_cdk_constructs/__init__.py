'''
# replace this
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

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import constructs as _constructs_77d1e7e8


class ApiGatewayToSqsToLambda(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="everdrop-aws-cdk-constructs.ApiGatewayToSqsToLambda",
):
    '''
    :summary:

    The ApiGatewayToSqsToLambda class. Class is very opinionated and does not allow for existing queues or lambdas.
    Class assumes a pulic domain should be created and the corresponding alias in route53 shall be created
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        domain_cert_arn: builtins.str,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.Function,
        route53_hosted_zone_id: builtins.str,
        service_name: builtins.str,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param domain: 
        :param domain_cert_arn: 
        :param lambda_function: 
        :param route53_hosted_zone_id: 
        :param service_name: 
        :param deploy_dead_letter_queue: 

        :summary: Constructs a new instance of the ApiGatewayToSqsToLambda class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e32f7e5b9e8e3dcf2607de8ba181ec5a6da53f93964833813dacdeed410616f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayToSqsToLambdaProps(
            domain=domain,
            domain_cert_arn=domain_cert_arn,
            lambda_function=lambda_function,
            route53_hosted_zone_id=route53_hosted_zone_id,
            service_name=service_name,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayRole")
    def api_gateway_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "apiGatewayRole"))

    @builtins.property
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> _aws_cdk_aws_sqs_ceddda9d.Queue:
        return typing.cast(_aws_cdk_aws_sqs_ceddda9d.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue]:
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_ceddda9d.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))


@jsii.data_type(
    jsii_type="everdrop-aws-cdk-constructs.ApiGatewayToSqsToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "domain_cert_arn": "domainCertArn",
        "lambda_function": "lambdaFunction",
        "route53_hosted_zone_id": "route53HostedZoneId",
        "service_name": "serviceName",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
    },
)
class ApiGatewayToSqsToLambdaProps:
    def __init__(
        self,
        *,
        domain: builtins.str,
        domain_cert_arn: builtins.str,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.Function,
        route53_hosted_zone_id: builtins.str,
        service_name: builtins.str,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param domain: 
        :param domain_cert_arn: 
        :param lambda_function: 
        :param route53_hosted_zone_id: 
        :param service_name: 
        :param deploy_dead_letter_queue: 

        :summary: The properties for the ApiGatewayToSqsToLambdaProps class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eec4217ce9deb2487d9364b8357d62ad532b9e09fb9de32b6f41c1f612986fb)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument domain_cert_arn", value=domain_cert_arn, expected_type=type_hints["domain_cert_arn"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument route53_hosted_zone_id", value=route53_hosted_zone_id, expected_type=type_hints["route53_hosted_zone_id"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument deploy_dead_letter_queue", value=deploy_dead_letter_queue, expected_type=type_hints["deploy_dead_letter_queue"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "domain_cert_arn": domain_cert_arn,
            "lambda_function": lambda_function,
            "route53_hosted_zone_id": route53_hosted_zone_id,
            "service_name": service_name,
        }
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue

    @builtins.property
    def domain(self) -> builtins.str:
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_cert_arn(self) -> builtins.str:
        result = self._values.get("domain_cert_arn")
        assert result is not None, "Required property 'domain_cert_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, result)

    @builtins.property
    def route53_hosted_zone_id(self) -> builtins.str:
        result = self._values.get("route53_hosted_zone_id")
        assert result is not None, "Required property 'route53_hosted_zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToSqsToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToSqsToLambda",
    "ApiGatewayToSqsToLambdaProps",
]

publication.publish()

def _typecheckingstub__5e32f7e5b9e8e3dcf2607de8ba181ec5a6da53f93964833813dacdeed410616f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: builtins.str,
    domain_cert_arn: builtins.str,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.Function,
    route53_hosted_zone_id: builtins.str,
    service_name: builtins.str,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eec4217ce9deb2487d9364b8357d62ad532b9e09fb9de32b6f41c1f612986fb(
    *,
    domain: builtins.str,
    domain_cert_arn: builtins.str,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.Function,
    route53_hosted_zone_id: builtins.str,
    service_name: builtins.str,
    deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
