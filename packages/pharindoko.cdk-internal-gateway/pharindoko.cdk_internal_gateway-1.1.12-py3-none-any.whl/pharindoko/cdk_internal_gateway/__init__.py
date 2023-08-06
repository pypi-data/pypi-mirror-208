'''
[![npm version](https://badge.fury.io/js/cdk-internal-gateway.svg)](https://badge.fury.io/js/cdk-internal-gateway)
[![PyPI version](https://badge.fury.io/py/pharindoko.cdk-internal-gateway.svg)](https://badge.fury.io/py/pharindoko.cdk-internal-gateway)
[![Release](https://github.com/pharindoko/cdk-internal-gateway/actions/workflows/release.yml/badge.svg)](https://github.com/pharindoko/cdk-internal-gateway/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/pharindoko/cdk-internal-gateway/blob/main/LICENSE)

# CDK Internal Gateway

Use this CDK construct to create **internal serverless applications**.

Useful for larger companies to create internal  serverless applications that are not exposed to the internet and only accessible from the internal network.

## Installation

Using Typescript for aws cdk

```bash
npm i cdk-internal-gateway
```

Using Python for aws cdk

```bash
pip install pharindoko.cdk-internal-gateway
```

## Architecture

![cdk-internal-gateway-architecture](cdk-internal-gateway.drawio.png)

### Technical Details

Modularized approach with separate constructs

* attach multiple InternalApiGateway and InternalWebsite constructs to the same Internal Service to save costs and keep flexibility

**Internal Service Construct (mandatory construct):**

* creates an internal application loadbalancer

  * forwards traffic to VPC endpoint for execute-api
  * redirect http to https
* generates custom domains for the API Gateway
* generates certificates for the loadbalancer listener

**Internal Api Gateway Construct:**

* provides a securely configured apigateway resource out of the box

  * attach your aws components to the internal apigateway resource
  * sets api gateway to PRIVATE mode
  * sets resource policies to only allow traffic from vpc endpoint
* attaches custom domains to the API Gateway
* attaches certificates to the the API Gateway and the loadbalancer

**Internal Website Construct:**

* makes your website internally accessible
* redeploys your website with a single cdk deploy
* provides a securely configured private s3 bucket out of box
* works with SPA applications (written with Vue, Angular) and static websites
* is an extension of the InternalApiGateway Construct

## Requirements

* CDK V2 (2.46.0)
* A VPC
* A VPC Endpoint for execute-api
* A Hosted Zone
* Internally accessible subnets (for the load balancer)

## Usage

> Let`s assume we create a simple internal api for our company and start with a single lambda function...

1. Create a file called `/lib/my-new-stack.ts`

   ```python
   import { aws_apigateway as apigateway, aws_ec2 as ec2, aws_lambda as lambda, aws_route53 as route53, Stack, StackProps } from 'aws-cdk-lib';
   import { HttpMethod } from 'aws-cdk-lib/aws-events';
   import { InternalApiGateway, InternalApiGatewayProps, InternalService } from 'cdk-internal-gateway';
   import { Construct } from 'constructs';
   import * as path from 'path';

   // Create a new stack that inherits from the InternalApiGateway Construct
   export class ServerlessStack extends InternalApiGateway {
       constructor(scope: Construct, id: string, props: InternalApiGatewayProps) {
           super(scope, id, props);

           // The internal api gateway is available as member variable
           // Attach your lambda function to the this.apiGateway
           const defaultLambdaJavascript = this.apiGateway.root.resourceForPath("hey-js");
           const defaultHandlerJavascript = new lambda.Function(
               this,
               `backendLambdaJavascript`,
               {
                   functionName: `js-lambda`,
                   runtime: lambda.Runtime.NODEJS_14_X,
                   handler: "index.handler",
                   code: lambda.Code.fromAsset(path.join(__dirname, "../src")),
               }
           );

           defaultLambdaJavascript.addMethod(
               HttpMethod.GET,
               new apigateway.LambdaIntegration(defaultHandlerJavascript)
           );
       }
   }

   // Create a new stack that contains the whole service with all nested stacks
   export class ServiceStack extends Stack {
       constructor(scope: Construct, id: string, props: StackProps) {
           super(scope, id, props);

           // get all parameters to create the internal service stack
           const vpc = ec2.Vpc.fromLookup(this, 'vpcLookup', { vpcId: 'vpc-1234567890' });
           const subnetSelection = {
               subnets: ['subnet-0b1e1c6c7d8e9f0a2', 'subnet-0b1e1c6c7d8e9f0a3'].map((ip, index) =>
                   ec2.Subnet.fromSubnetId(this, `Subnet${index}`, ip),
               ),
           };
           const hostedZone = route53.HostedZone.fromLookup(this, 'hostedzone', {
               domainName: 'test.aws1234.com',
               privateZone: true,
               vpcId: vpc.vpcId,
           });
           const vpcEndpoint =
               ec2.InterfaceVpcEndpoint.fromInterfaceVpcEndpointAttributes(
                   this,
                   'vpcEndpoint',
                   {
                       port: 443,
                       vpcEndpointId: 'vpce-1234567890',
                   },
               );

           // create the internal service stack
           const serviceStack = new InternalService(this, 'InternalServiceStack', {
               hostedZone: hostedZone,
               subnetSelection: subnetSelection,
               vpcEndpointIPAddresses: ['192.168.2.1', '192.168.2.2'],
               vpc: vpc,
               subjectAlternativeNames: ['internal.example.com'],
               subDomain: "internal-service"
           })

           // create your stack that inherits from the InternalApiGateway
           new ServerlessStack(this, 'MyProjectStack', {
               domains: serviceStack.domains,
               stage: "dev",
               vpcEndpoint: vpcEndpoint,
           })

           // create another stack that inherits from the InternalApiGateway
           ...
           ...
       }
   }
   ```
2. Reference the newly created `ServiceStack` in the default `/bin/{project}.ts` file e.g. like this

   ```python
   new ServiceStack(app, 'MyProjectStack', {
   env:
   {
       account: process.env.CDK_DEPLOY_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT,
       region: process.env.CDK_DEPLOY_REGION || process.env.CDK_DEFAULT_REGION
   }
   ```

## Costs

You have to expect basic infra costs for 2 components in this setup:

| Count |  Type |  Estimated Costs |
|---|---|---|
|1 x| application load balancer  | 20 $  |
|2 x| network interfaces for the vpc endpoint  | 16 $  |

A shared vpc can lower the costs as vpc endpoint and their network interfaces can be used together...
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
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class InternalApiGateway(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-internal-gateway.InternalApiGateway",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
        stage: builtins.str,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        api_base_path_mapping_path: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domains: List of custom domains names to be used for the API Gateway.
        :param stage: Stage name used for all cloudformation resource names and internal aws resource names.
        :param vpc_endpoint: VPC endpoint id of execute-api vpc endpoint. This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        :param api_base_path_mapping_path: Path for custom domain base path mapping that will be attached to the api gateway.
        :param binary_media_types: Binary media types for the internal api gateway.
        :param minimum_compression_size: minimum compression size for the internal api gateway.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9ae54245009148c66f767401f5250017b64fe5bce1d826b5a4ab5f903630362)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InternalApiGatewayProps(
            domains=domains,
            stage=stage,
            vpc_endpoint=vpc_endpoint,
            api_base_path_mapping_path=api_base_path_mapping_path,
            binary_media_types=binary_media_types,
            minimum_compression_size=minimum_compression_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def _api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.LambdaRestApi:
        '''Internal API Gateway This private api gateway is used to serve internal solutions (websites, apis, applications).

        Attach your methods to this api gateway.
        It is not exposed to the internet.
        It is only accessible from the load balancer`s target group.
        '''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.LambdaRestApi, jsii.get(self, "apiGateway"))


class _InternalApiGatewayProxy(InternalApiGateway):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, InternalApiGateway).__jsii_proxy_class__ = lambda : _InternalApiGatewayProxy


@jsii.data_type(
    jsii_type="cdk-internal-gateway.InternalApiGatewayProps",
    jsii_struct_bases=[],
    name_mapping={
        "domains": "domains",
        "stage": "stage",
        "vpc_endpoint": "vpcEndpoint",
        "api_base_path_mapping_path": "apiBasePathMappingPath",
        "binary_media_types": "binaryMediaTypes",
        "minimum_compression_size": "minimumCompressionSize",
    },
)
class InternalApiGatewayProps:
    def __init__(
        self,
        *,
        domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
        stage: builtins.str,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        api_base_path_mapping_path: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for ApiGateway.

        :param domains: List of custom domains names to be used for the API Gateway.
        :param stage: Stage name used for all cloudformation resource names and internal aws resource names.
        :param vpc_endpoint: VPC endpoint id of execute-api vpc endpoint. This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        :param api_base_path_mapping_path: Path for custom domain base path mapping that will be attached to the api gateway.
        :param binary_media_types: Binary media types for the internal api gateway.
        :param minimum_compression_size: minimum compression size for the internal api gateway.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d09850aa6d812c4e31fc3d6e1747f6fd2cd0e17db65131fb04491c03f3d23f9)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument vpc_endpoint", value=vpc_endpoint, expected_type=type_hints["vpc_endpoint"])
            check_type(argname="argument api_base_path_mapping_path", value=api_base_path_mapping_path, expected_type=type_hints["api_base_path_mapping_path"])
            check_type(argname="argument binary_media_types", value=binary_media_types, expected_type=type_hints["binary_media_types"])
            check_type(argname="argument minimum_compression_size", value=minimum_compression_size, expected_type=type_hints["minimum_compression_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
            "stage": stage,
            "vpc_endpoint": vpc_endpoint,
        }
        if api_base_path_mapping_path is not None:
            self._values["api_base_path_mapping_path"] = api_base_path_mapping_path
        if binary_media_types is not None:
            self._values["binary_media_types"] = binary_media_types
        if minimum_compression_size is not None:
            self._values["minimum_compression_size"] = minimum_compression_size

    @builtins.property
    def domains(self) -> typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName]:
        '''List of custom domains names to be used for the API Gateway.'''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName], result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''Stage name  used for all cloudformation resource names and internal aws resource names.'''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint:
        '''VPC endpoint id of execute-api vpc endpoint.

        This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        '''
        result = self._values.get("vpc_endpoint")
        assert result is not None, "Required property 'vpc_endpoint' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint, result)

    @builtins.property
    def api_base_path_mapping_path(self) -> typing.Optional[builtins.str]:
        '''Path for custom domain base path mapping that will be attached to the api gateway.'''
        result = self._values.get("api_base_path_mapping_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def binary_media_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Binary media types for the internal api gateway.'''
        result = self._values.get("binary_media_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def minimum_compression_size(self) -> typing.Optional[jsii.Number]:
        '''minimum compression size for the internal api gateway.'''
        result = self._values.get("minimum_compression_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InternalApiGatewayProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InternalService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-internal-gateway.InternalService",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        sub_domain: builtins.str,
        subject_alternative_names: typing.Sequence[builtins.str],
        subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_endpoint_ip_addresses: typing.Sequence[builtins.str],
        custom_domain_ssl_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
        load_balancer_listener_ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: Hosted zone that will be used for the custom domain.
        :param sub_domain: Subdomain attached to hosted zone name.
        :param subject_alternative_names: List of alternative domains attached to the solution.
        :param subnet_selection: Subnets attached to the application load balancer.
        :param vpc: VPC attached to the application load balancer.
        :param vpc_endpoint_ip_addresses: VPC endpoint ip addresses attached to the load balancer`s target group.
        :param custom_domain_ssl_policy: SSLPolicy attached to the apigateway custom domain. Default: apigateway.SslPolicy.TLS_1_2
        :param load_balancer_listener_ssl_policy: SSLPolicy attached to the load balancer listener. Default: elb.SslPolicy.FORWARD_SECRECY_TLS12_RES_GCM
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c6fdb0604ec77d74f01c7b51d0cc12d16e1d2a8b65e1698a885908e24dec96a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InternalServiceProps(
            hosted_zone=hosted_zone,
            sub_domain=sub_domain,
            subject_alternative_names=subject_alternative_names,
            subnet_selection=subnet_selection,
            vpc=vpc,
            vpc_endpoint_ip_addresses=vpc_endpoint_ip_addresses,
            custom_domain_ssl_policy=custom_domain_ssl_policy,
            load_balancer_listener_ssl_policy=load_balancer_listener_ssl_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="domains")
    def domains(self) -> typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName]:
        '''List of domains created by the internal service stack and shared with the api gateway stack.'''
        return typing.cast(typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName], jsii.get(self, "domains"))


@jsii.data_type(
    jsii_type="cdk-internal-gateway.InternalServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "sub_domain": "subDomain",
        "subject_alternative_names": "subjectAlternativeNames",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
        "vpc_endpoint_ip_addresses": "vpcEndpointIPAddresses",
        "custom_domain_ssl_policy": "customDomainSSLPolicy",
        "load_balancer_listener_ssl_policy": "loadBalancerListenerSSLPolicy",
    },
)
class InternalServiceProps:
    def __init__(
        self,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        sub_domain: builtins.str,
        subject_alternative_names: typing.Sequence[builtins.str],
        subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_endpoint_ip_addresses: typing.Sequence[builtins.str],
        custom_domain_ssl_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
        load_balancer_listener_ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    ) -> None:
        '''Properties for InternalService.

        :param hosted_zone: Hosted zone that will be used for the custom domain.
        :param sub_domain: Subdomain attached to hosted zone name.
        :param subject_alternative_names: List of alternative domains attached to the solution.
        :param subnet_selection: Subnets attached to the application load balancer.
        :param vpc: VPC attached to the application load balancer.
        :param vpc_endpoint_ip_addresses: VPC endpoint ip addresses attached to the load balancer`s target group.
        :param custom_domain_ssl_policy: SSLPolicy attached to the apigateway custom domain. Default: apigateway.SslPolicy.TLS_1_2
        :param load_balancer_listener_ssl_policy: SSLPolicy attached to the load balancer listener. Default: elb.SslPolicy.FORWARD_SECRECY_TLS12_RES_GCM
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc10cdccafe7b9adef536e2eb7718e1b504c653f343e7e2cbb0c9201b00217a7)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument sub_domain", value=sub_domain, expected_type=type_hints["sub_domain"])
            check_type(argname="argument subject_alternative_names", value=subject_alternative_names, expected_type=type_hints["subject_alternative_names"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_endpoint_ip_addresses", value=vpc_endpoint_ip_addresses, expected_type=type_hints["vpc_endpoint_ip_addresses"])
            check_type(argname="argument custom_domain_ssl_policy", value=custom_domain_ssl_policy, expected_type=type_hints["custom_domain_ssl_policy"])
            check_type(argname="argument load_balancer_listener_ssl_policy", value=load_balancer_listener_ssl_policy, expected_type=type_hints["load_balancer_listener_ssl_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "sub_domain": sub_domain,
            "subject_alternative_names": subject_alternative_names,
            "subnet_selection": subnet_selection,
            "vpc": vpc,
            "vpc_endpoint_ip_addresses": vpc_endpoint_ip_addresses,
        }
        if custom_domain_ssl_policy is not None:
            self._values["custom_domain_ssl_policy"] = custom_domain_ssl_policy
        if load_balancer_listener_ssl_policy is not None:
            self._values["load_balancer_listener_ssl_policy"] = load_balancer_listener_ssl_policy

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''Hosted zone that will be used for the custom domain.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def sub_domain(self) -> builtins.str:
        '''Subdomain attached to hosted zone name.'''
        result = self._values.get("sub_domain")
        assert result is not None, "Required property 'sub_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject_alternative_names(self) -> typing.List[builtins.str]:
        '''List of alternative domains attached to the solution.'''
        result = self._values.get("subject_alternative_names")
        assert result is not None, "Required property 'subject_alternative_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnet_selection(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''Subnets attached to the application load balancer.'''
        result = self._values.get("subnet_selection")
        assert result is not None, "Required property 'subnet_selection' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC attached to the application load balancer.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def vpc_endpoint_ip_addresses(self) -> typing.List[builtins.str]:
        '''VPC endpoint ip addresses attached to the load balancer`s target group.'''
        result = self._values.get("vpc_endpoint_ip_addresses")
        assert result is not None, "Required property 'vpc_endpoint_ip_addresses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def custom_domain_ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy]:
        '''SSLPolicy attached to the apigateway custom domain.

        :default: apigateway.SslPolicy.TLS_1_2
        '''
        result = self._values.get("custom_domain_ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy], result)

    @builtins.property
    def load_balancer_listener_ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy]:
        '''SSLPolicy attached to the load balancer listener.

        :default: elb.SslPolicy.FORWARD_SECRECY_TLS12_RES_GCM
        '''
        result = self._values.get("load_balancer_listener_ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InternalServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InternalWebsite(
    InternalApiGateway,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-internal-gateway.InternalWebsite",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        source_path: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
        stage: builtins.str,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        api_base_path_mapping_path: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param source_path: Path of website folder containing the website`s sources.
        :param bucket_name: Name of s3 bucket to use for the website deployment.
        :param website_index_document: Name of html index document used for the website. Default: index.html
        :param domains: List of custom domains names to be used for the API Gateway.
        :param stage: Stage name used for all cloudformation resource names and internal aws resource names.
        :param vpc_endpoint: VPC endpoint id of execute-api vpc endpoint. This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        :param api_base_path_mapping_path: Path for custom domain base path mapping that will be attached to the api gateway.
        :param binary_media_types: Binary media types for the internal api gateway.
        :param minimum_compression_size: minimum compression size for the internal api gateway.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d516b7187660b534cf465c6154956083e900ca2144209c0ad2326e2da9610ff6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InternalWebsiteProps(
            source_path=source_path,
            bucket_name=bucket_name,
            website_index_document=website_index_document,
            domains=domains,
            stage=stage,
            vpc_endpoint=vpc_endpoint,
            api_base_path_mapping_path=api_base_path_mapping_path,
            binary_media_types=binary_media_types,
            minimum_compression_size=minimum_compression_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-internal-gateway.InternalWebsiteProps",
    jsii_struct_bases=[InternalApiGatewayProps],
    name_mapping={
        "domains": "domains",
        "stage": "stage",
        "vpc_endpoint": "vpcEndpoint",
        "api_base_path_mapping_path": "apiBasePathMappingPath",
        "binary_media_types": "binaryMediaTypes",
        "minimum_compression_size": "minimumCompressionSize",
        "source_path": "sourcePath",
        "bucket_name": "bucketName",
        "website_index_document": "websiteIndexDocument",
    },
)
class InternalWebsiteProps(InternalApiGatewayProps):
    def __init__(
        self,
        *,
        domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
        stage: builtins.str,
        vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
        api_base_path_mapping_path: typing.Optional[builtins.str] = None,
        binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        minimum_compression_size: typing.Optional[jsii.Number] = None,
        source_path: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for InternalService.

        :param domains: List of custom domains names to be used for the API Gateway.
        :param stage: Stage name used for all cloudformation resource names and internal aws resource names.
        :param vpc_endpoint: VPC endpoint id of execute-api vpc endpoint. This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        :param api_base_path_mapping_path: Path for custom domain base path mapping that will be attached to the api gateway.
        :param binary_media_types: Binary media types for the internal api gateway.
        :param minimum_compression_size: minimum compression size for the internal api gateway.
        :param source_path: Path of website folder containing the website`s sources.
        :param bucket_name: Name of s3 bucket to use for the website deployment.
        :param website_index_document: Name of html index document used for the website. Default: index.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5870defbfb19b1259aa25bc8864db1000e3c69b24aac88f8bdae9a291ecfa658)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument vpc_endpoint", value=vpc_endpoint, expected_type=type_hints["vpc_endpoint"])
            check_type(argname="argument api_base_path_mapping_path", value=api_base_path_mapping_path, expected_type=type_hints["api_base_path_mapping_path"])
            check_type(argname="argument binary_media_types", value=binary_media_types, expected_type=type_hints["binary_media_types"])
            check_type(argname="argument minimum_compression_size", value=minimum_compression_size, expected_type=type_hints["minimum_compression_size"])
            check_type(argname="argument source_path", value=source_path, expected_type=type_hints["source_path"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument website_index_document", value=website_index_document, expected_type=type_hints["website_index_document"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
            "stage": stage,
            "vpc_endpoint": vpc_endpoint,
            "source_path": source_path,
        }
        if api_base_path_mapping_path is not None:
            self._values["api_base_path_mapping_path"] = api_base_path_mapping_path
        if binary_media_types is not None:
            self._values["binary_media_types"] = binary_media_types
        if minimum_compression_size is not None:
            self._values["minimum_compression_size"] = minimum_compression_size
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document

    @builtins.property
    def domains(self) -> typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName]:
        '''List of custom domains names to be used for the API Gateway.'''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_apigateway_ceddda9d.IDomainName], result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''Stage name  used for all cloudformation resource names and internal aws resource names.'''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_endpoint(self) -> _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint:
        '''VPC endpoint id of execute-api vpc endpoint.

        This endpoint will be used to forward requests from the load balancer`s target group to the api gateway.
        '''
        result = self._values.get("vpc_endpoint")
        assert result is not None, "Required property 'vpc_endpoint' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint, result)

    @builtins.property
    def api_base_path_mapping_path(self) -> typing.Optional[builtins.str]:
        '''Path for custom domain base path mapping that will be attached to the api gateway.'''
        result = self._values.get("api_base_path_mapping_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def binary_media_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Binary media types for the internal api gateway.'''
        result = self._values.get("binary_media_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def minimum_compression_size(self) -> typing.Optional[jsii.Number]:
        '''minimum compression size for the internal api gateway.'''
        result = self._values.get("minimum_compression_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source_path(self) -> builtins.str:
        '''Path of website folder containing the website`s sources.'''
        result = self._values.get("source_path")
        assert result is not None, "Required property 'source_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Name of s3 bucket to use for the website deployment.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''Name of html index document used for the website.

        :default: index.html
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InternalWebsiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "InternalApiGateway",
    "InternalApiGatewayProps",
    "InternalService",
    "InternalServiceProps",
    "InternalWebsite",
    "InternalWebsiteProps",
]

publication.publish()

def _typecheckingstub__d9ae54245009148c66f767401f5250017b64fe5bce1d826b5a4ab5f903630362(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
    stage: builtins.str,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    api_base_path_mapping_path: typing.Optional[builtins.str] = None,
    binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    minimum_compression_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d09850aa6d812c4e31fc3d6e1747f6fd2cd0e17db65131fb04491c03f3d23f9(
    *,
    domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
    stage: builtins.str,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    api_base_path_mapping_path: typing.Optional[builtins.str] = None,
    binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    minimum_compression_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c6fdb0604ec77d74f01c7b51d0cc12d16e1d2a8b65e1698a885908e24dec96a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    sub_domain: builtins.str,
    subject_alternative_names: typing.Sequence[builtins.str],
    subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_endpoint_ip_addresses: typing.Sequence[builtins.str],
    custom_domain_ssl_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
    load_balancer_listener_ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc10cdccafe7b9adef536e2eb7718e1b504c653f343e7e2cbb0c9201b00217a7(
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    sub_domain: builtins.str,
    subject_alternative_names: typing.Sequence[builtins.str],
    subnet_selection: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_endpoint_ip_addresses: typing.Sequence[builtins.str],
    custom_domain_ssl_policy: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.SecurityPolicy] = None,
    load_balancer_listener_ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d516b7187660b534cf465c6154956083e900ca2144209c0ad2326e2da9610ff6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    source_path: builtins.str,
    bucket_name: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
    stage: builtins.str,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    api_base_path_mapping_path: typing.Optional[builtins.str] = None,
    binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    minimum_compression_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5870defbfb19b1259aa25bc8864db1000e3c69b24aac88f8bdae9a291ecfa658(
    *,
    domains: typing.Sequence[_aws_cdk_aws_apigateway_ceddda9d.IDomainName],
    stage: builtins.str,
    vpc_endpoint: _aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint,
    api_base_path_mapping_path: typing.Optional[builtins.str] = None,
    binary_media_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    minimum_compression_size: typing.Optional[jsii.Number] = None,
    source_path: builtins.str,
    bucket_name: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
