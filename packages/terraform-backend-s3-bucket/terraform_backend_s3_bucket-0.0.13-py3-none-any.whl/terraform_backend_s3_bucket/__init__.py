'''
# Terraform Backend S3 Bucket

Provides a CDK construct for Terraform state management. The construct consists
of

* S3 bucket
* DynamoDB table.

## Features

* Versioning is enabled
  [[S3.14] S3 buckets should use versioning](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-14)
* All public access is blocked
  [[S3.1] S3 Block Public Access setting should be enabled](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-1)
* Enforce SSL for requests
  [[S3.5] S3 buckets should require requests to use Secure Socket Layer](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-1)
* A lifecycle policy for non-current versions of objects
  [[S3.10] S3 buckets with versioning enabled should have lifecycle policies configured
  ](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-10)
* Enforcing that the bucket owner owns every object in the bucket.

## Links

* [Amazon Simple Storage Service controls](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html)
* [Controlling ownership of objects and disabling ACLs for your bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html)
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

import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class TerraformStateBackend(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="terraform-backend-s3-bucket.TerraformStateBackend",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: 
        :param table_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83bbb44712bab4215c0c079313514a4fafb1a8c25b8b3bff9e816e6d0ec53d3c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TerraformStateBackendProperties(
            bucket_name=bucket_name, table_name=table_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        '''
        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, jsii.get(self, "table"))


@jsii.data_type(
    jsii_type="terraform-backend-s3-bucket.TerraformStateBackendProperties",
    jsii_struct_bases=[],
    name_mapping={"bucket_name": "bucketName", "table_name": "tableName"},
)
class TerraformStateBackendProperties:
    def __init__(self, *, bucket_name: builtins.str, table_name: builtins.str) -> None:
        '''
        :param bucket_name: 
        :param table_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab43988013da6b34677c29733476fd212fa82e21bdf835a483d12aacbecd7ce7)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_name": bucket_name,
            "table_name": table_name,
        }

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TerraformStateBackendProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TerraformStateBackend",
    "TerraformStateBackendProperties",
]

publication.publish()

def _typecheckingstub__83bbb44712bab4215c0c079313514a4fafb1a8c25b8b3bff9e816e6d0ec53d3c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: builtins.str,
    table_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab43988013da6b34677c29733476fd212fa82e21bdf835a483d12aacbecd7ce7(
    *,
    bucket_name: builtins.str,
    table_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
