'''
# CDK Library for AWS SSO

[![build](https://github.com/RenovoSolutions/cdk-library-aws-sso/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-aws-sso/actions/workflows/build.yml)

**Note: This construct library is currently being developed and requires more tests, but fundamentally it should work.**

This CDK library provides L2 constructs for the AWS SSO CfnPermissionSet and CfnAssignment. Assignment is not consumed by other resources so it's attributes and properties are minimal, but a L2 construct makes it easier to interact with and allows providing a more fully featured construct for the Permission Set and assignment requires.

## Features

* L2 Construct for `PermissionSet` including importing from ARN and granting the permission
* L2 Construct for `Assignment`
* Some enums to provide valid inputs for certain properties

## API Doc

See [API](API.md)

## Examples

### PermissionSet

```python
import { PermissionSet, Assignment, PrincipalTypes } from '@renovosolutions/cdk-library-aws-sso';
import {
  App,
  Stack,
  StackProps,
  aws_sso as sso,
  aws_iam as iam,
  Duration,
} from 'aws-cdk-lib';

// create a permission set
const permissionSetExample = new PermissionSet(this, 'permissionSet', {
  ssoInstanceArn: 'arn:aws:sso:::instance/ssoins-1234567891234567',
  name: 'ExamplePermissionSet',
  description: 'Example permission set with some policies',
  awsManagedPolicies:  [
    iam.ManagedPolicy.fromAwsManagedPolicyName('job-function/ViewOnlyAccess'),
  ],
  customerManagedPolicyReferences: [
    {
      name: 'someServiceLogRead', // must exist in the target account
      path: '/',
    }
  ],
  relayStateType: 'https://us-east-1.console.aws.amazon.com/cloudwatch/home'
})

// assign it to an account/principal with an Assignment
new Assignment(this, 'ExampleAssignment', {
  permissionSet: permissionSetExample,
  principal: {
    principalId: '25750630-0ae9-479a-97c2-0afc2d5b4eac,
    principalType: PrincipalTypes.GROUP,
  },
  targetId: '124567890123456',
});

// assign it to something else with a grant
permissionSetExample.grant('permissionSetExampleAssignment', {
  principal: {
    principalId: '12350630-0ae9-479a-97c2-0afc2d5b4eac',
    principalType: PrincipalTypes.GROUP,
  },
  targetId: '344567890123456',
});

// import an existing permission set
const existingPermissionSetExample = PermissionSet.fromPermissionSetArn(this, 'existingPermissionSetExample', 'arn:aws:sso:::permissionSet/ssoins-1234567891234567/ps-55a5555a5a55ab55');
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_sso as _aws_cdk_aws_sso_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-sso.AssignmentAttributes",
    jsii_struct_bases=[],
    name_mapping={},
)
class AssignmentAttributes:
    def __init__(self) -> None:
        '''Attributes for an assignment of which there are none.'''
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
    jsii_type="@renovosolutions/cdk-library-aws-sso.AssignmentOptions",
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
        '''The options for creating an assignment.

        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        '''
        if isinstance(principal, dict):
            principal = PrincipalProperty(**principal)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae439f39faaa114233bc0b1a16b1904736952c8fbf1932dc6475eed1f3d817a)
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
        '''The principal to assign the permission set to.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast("PrincipalProperty", result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''The target id the permission set will be assigned to.'''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> typing.Optional["TargetTypes"]:
        '''The entity type for which the assignment will be created.

        :default: TargetTypes.AWS_ACCOUNT
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
    jsii_type="@renovosolutions/cdk-library-aws-sso.AssignmentProps",
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
        '''The properties of a new assignment.

        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        :param permission_set: The permission set to assign to the principal.
        '''
        if isinstance(principal, dict):
            principal = PrincipalProperty(**principal)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3677dd84d66e98c8bbf6b4b630ea271a32c589d1f12d4383871d2614207cad7b)
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
        '''The principal to assign the permission set to.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast("PrincipalProperty", result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''The target id the permission set will be assigned to.'''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> typing.Optional["TargetTypes"]:
        '''The entity type for which the assignment will be created.

        :default: TargetTypes.AWS_ACCOUNT
        '''
        result = self._values.get("target_type")
        return typing.cast(typing.Optional["TargetTypes"], result)

    @builtins.property
    def permission_set(self) -> "IPermissionSet":
        '''The permission set to assign to the principal.'''
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


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-sso.CustomerManagedPolicyReference",
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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d76e58f544c6bf87eb4ed6045f0b6948c3216099d824187a7cc57942e89eb9fe)
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


@jsii.interface(jsii_type="@renovosolutions/cdk-library-aws-sso.IAssignment")
class IAssignment(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''The resource interface for an AWS SSO assignment.

    This interface has no attributes because the resulting resource has none.
    '''

    pass


class _IAssignmentProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''The resource interface for an AWS SSO assignment.

    This interface has no attributes because the resulting resource has none.
    '''

    __jsii_type__: typing.ClassVar[str] = "@renovosolutions/cdk-library-aws-sso.IAssignment"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAssignment).__jsii_proxy_class__ = lambda : _IAssignmentProxy


@jsii.interface(jsii_type="@renovosolutions/cdk-library-aws-sso.IPermissionSet")
class IPermissionSet(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''The resource interface for an AWS SSO permission set.'''

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''The SSO instance ARN of the permission set.'''
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
        '''Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        '''
        ...


class _IPermissionSetProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''The resource interface for an AWS SSO permission set.'''

    __jsii_type__: typing.ClassVar[str] = "@renovosolutions/cdk-library-aws-sso.IPermissionSet"

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "permissionSetArn"))

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''The SSO instance ARN of the permission set.'''
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
        '''Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d08775b809b0e566cdb84b9c89847ac6e6605d16d5345595d249a8f665bbbe)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        assignment_options = AssignmentOptions(
            principal=principal, target_id=target_id, target_type=target_type
        )

        return typing.cast("Assignment", jsii.invoke(self, "grant", [id, assignment_options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPermissionSet).__jsii_proxy_class__ = lambda : _IPermissionSetProxy


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-sso.PermissionBoundary",
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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b19ce1fb3e89b904939ce873e787c40e49146fc1e9defc30a9c9e3df0a22c16)
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
    jsii_type="@renovosolutions/cdk-library-aws-sso.PermissionSet",
):
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
        :param name: The name of the permission set.
        :param sso_instance_arn: The ARN of the SSO instance under which the operation will be executed.
        :param aws_managed_policies: The AWS managed policies to attach to the ``PermissionSet``. Default: - No AWS managed policies
        :param customer_managed_policy_references: Specifies the names and paths of a customer managed policy. You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set. Default: - No customer managed policies
        :param description: The description of the ``PermissionSet``. Default: - No description
        :param inline_policy: The IAM inline policy that is attached to the permission set. Default: - No inline policy
        :param permissions_boundary: Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary. Specify either customerManagedPolicyReference to use the name and path of a customer managed policy, or managedPolicy to use the ARN of an AWS managed policy. A permissions boundary represents the maximum permissions that any policy can grant your role. For more information, see Permissions boundaries for IAM entities in the AWS Identity and Access Management User Guide. Default: - No permissions boundary
        :param relay_state_type: Used to redirect users within the application during the federation authentication process. By default, when a user signs into the AWS access portal, chooses an account, and then chooses the role that AWS creates from the assigned permission set, IAM Identity Center redirects the user’s browser to the AWS Management Console. You can change this behavior by setting the relay state to a different console URL. Setting the relay state enables you to provide the user with quick access to the console that is most appropriate for their role. For example, you can set the relay state to the Amazon EC2 console URL (https://console.aws.amazon.com/ec2/) to redirect the user to that console when they choose the Amazon EC2 administrator role. Default: - No redirection
        :param session_duration: The length of time that the application user sessions are valid for.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e1c8a3a6bbb48874bcc41baf50aebc1d5b3c196abd7611f29b515aa6e0683d9)
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
        '''Reference an existing permission set by ARN.

        :param scope: -
        :param id: -
        :param permission_set_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1534cc83982ea2274a4ef806b10a9b22e16bd0a2ac53cb7e2d7d7e7e7f04522a)
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
        '''Grant this permission set to a given principal for a given targetId (AWS account identifier) on a given SSO instance.

        :param id: -
        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cdc85e58620129e7f246a5cfde6e7c38745a843ac7234984317b311e146af34)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        assignment_options = AssignmentOptions(
            principal=principal, target_id=target_id, target_type=target_type
        )

        return typing.cast("Assignment", jsii.invoke(self, "grant", [id, assignment_options]))

    @builtins.property
    @jsii.member(jsii_name="cfnPermissionSet")
    def cfn_permission_set(self) -> _aws_cdk_aws_sso_ceddda9d.CfnPermissionSet:
        '''The underlying CfnPermissionSet resource.'''
        return typing.cast(_aws_cdk_aws_sso_ceddda9d.CfnPermissionSet, jsii.get(self, "cfnPermissionSet"))

    @builtins.property
    @jsii.member(jsii_name="permissionSetArn")
    def permission_set_arn(self) -> builtins.str:
        '''The permission set ARN of the permission set.'''
        return typing.cast(builtins.str, jsii.get(self, "permissionSetArn"))

    @builtins.property
    @jsii.member(jsii_name="ssoInstanceArn")
    def sso_instance_arn(self) -> builtins.str:
        '''The SSO instance the permission set belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "ssoInstanceArn"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-sso.PermissionSetAttributes",
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
        '''Attributes for a permission set.

        :param permission_set_arn: The permission set ARN of the permission set. Such as ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.
        :param sso_instance_arn: The SSO instance ARN of the permission set.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f41d64f11736d4f2d569f1d67bc6cf42babd45687b8f3b4e4f35e92c7ff0fe3)
            check_type(argname="argument permission_set_arn", value=permission_set_arn, expected_type=type_hints["permission_set_arn"])
            check_type(argname="argument sso_instance_arn", value=sso_instance_arn, expected_type=type_hints["sso_instance_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "permission_set_arn": permission_set_arn,
            "sso_instance_arn": sso_instance_arn,
        }

    @builtins.property
    def permission_set_arn(self) -> builtins.str:
        '''The permission set ARN of the permission set.

        Such as
        ``arn:aws:sso:::permissionSet/ins-instanceid/ps-permissionsetid``.
        '''
        result = self._values.get("permission_set_arn")
        assert result is not None, "Required property 'permission_set_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_instance_arn(self) -> builtins.str:
        '''The SSO instance ARN of the permission set.'''
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
    jsii_type="@renovosolutions/cdk-library-aws-sso.PermissionSetProps",
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
        '''The properties of a new permission set.

        :param name: The name of the permission set.
        :param sso_instance_arn: The ARN of the SSO instance under which the operation will be executed.
        :param aws_managed_policies: The AWS managed policies to attach to the ``PermissionSet``. Default: - No AWS managed policies
        :param customer_managed_policy_references: Specifies the names and paths of a customer managed policy. You must have an IAM policy that matches the name and path in each AWS account where you want to deploy your permission set. Default: - No customer managed policies
        :param description: The description of the ``PermissionSet``. Default: - No description
        :param inline_policy: The IAM inline policy that is attached to the permission set. Default: - No inline policy
        :param permissions_boundary: Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary. Specify either customerManagedPolicyReference to use the name and path of a customer managed policy, or managedPolicy to use the ARN of an AWS managed policy. A permissions boundary represents the maximum permissions that any policy can grant your role. For more information, see Permissions boundaries for IAM entities in the AWS Identity and Access Management User Guide. Default: - No permissions boundary
        :param relay_state_type: Used to redirect users within the application during the federation authentication process. By default, when a user signs into the AWS access portal, chooses an account, and then chooses the role that AWS creates from the assigned permission set, IAM Identity Center redirects the user’s browser to the AWS Management Console. You can change this behavior by setting the relay state to a different console URL. Setting the relay state enables you to provide the user with quick access to the console that is most appropriate for their role. For example, you can set the relay state to the Amazon EC2 console URL (https://console.aws.amazon.com/ec2/) to redirect the user to that console when they choose the Amazon EC2 administrator role. Default: - No redirection
        :param session_duration: The length of time that the application user sessions are valid for.
        '''
        if isinstance(permissions_boundary, dict):
            permissions_boundary = PermissionBoundary(**permissions_boundary)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a500faaedc99c37669b04cc4cb3ded8f1161916dab975452e5e55c1cb669f0)
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
        '''The name of the permission set.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sso_instance_arn(self) -> builtins.str:
        '''The ARN of the SSO instance under which the operation will be executed.'''
        result = self._values.get("sso_instance_arn")
        assert result is not None, "Required property 'sso_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''The AWS managed policies to attach to the ``PermissionSet``.

        :default: - No AWS managed policies
        '''
        result = self._values.get("aws_managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def customer_managed_policy_references(
        self,
    ) -> typing.Optional[typing.List[CustomerManagedPolicyReference]]:
        '''Specifies the names and paths of a customer managed policy.

        You must have an IAM policy that matches the name and path in each
        AWS account where you want to deploy your permission set.

        :default: - No customer managed policies
        '''
        result = self._values.get("customer_managed_policy_references")
        return typing.cast(typing.Optional[typing.List[CustomerManagedPolicyReference]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the ``PermissionSet``.

        :default: - No description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inline_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''The IAM inline policy that is attached to the permission set.

        :default: - No inline policy
        '''
        result = self._values.get("inline_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def permissions_boundary(self) -> typing.Optional[PermissionBoundary]:
        '''Specifies the configuration of the AWS managed or customer managed policy that you want to set as a permissions boundary.

        Specify either
        customerManagedPolicyReference to use the name and path of a customer
        managed policy, or managedPolicy to use the ARN of an AWS managed
        policy.

        A permissions boundary represents the maximum permissions that any
        policy can grant your role. For more information, see Permissions boundaries
        for IAM entities in the AWS Identity and Access Management User Guide.

        :default: - No permissions boundary

        :see: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[PermissionBoundary], result)

    @builtins.property
    def relay_state_type(self) -> typing.Optional[builtins.str]:
        '''Used to redirect users within the application during the federation authentication process.

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
        '''
        result = self._values.get("relay_state_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The length of time that the application user sessions are valid for.'''
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


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-sso.PrincipalProperty",
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
        :param principal_id: The id of the principal.
        :param principal_type: The type of the principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5a8b88d8d2941e16b21bcde3962a352b3c0bcdac3ecd7b005ecb7859a601d5)
            check_type(argname="argument principal_id", value=principal_id, expected_type=type_hints["principal_id"])
            check_type(argname="argument principal_type", value=principal_type, expected_type=type_hints["principal_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "principal_id": principal_id,
            "principal_type": principal_type,
        }

    @builtins.property
    def principal_id(self) -> builtins.str:
        '''The id of the principal.'''
        result = self._values.get("principal_id")
        assert result is not None, "Required property 'principal_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal_type(self) -> "PrincipalTypes":
        '''The type of the principal.'''
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


@jsii.enum(jsii_type="@renovosolutions/cdk-library-aws-sso.PrincipalTypes")
class PrincipalTypes(enum.Enum):
    USER = "USER"
    GROUP = "GROUP"


@jsii.enum(jsii_type="@renovosolutions/cdk-library-aws-sso.TargetTypes")
class TargetTypes(enum.Enum):
    AWS_ACCOUNT = "AWS_ACCOUNT"


@jsii.implements(IAssignment)
class Assignment(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-sso.Assignment",
):
    '''The assignment construct.

    Has no import method because there is no attributes to import.
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
        :param permission_set: The permission set to assign to the principal.
        :param principal: The principal to assign the permission set to.
        :param target_id: The target id the permission set will be assigned to.
        :param target_type: The entity type for which the assignment will be created. Default: TargetTypes.AWS_ACCOUNT
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eca7b2cf47acacd3579840411d5aee15f9a9bf2f86aefe69c49c627750efbf7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AssignmentProps(
            permission_set=permission_set,
            principal=principal,
            target_id=target_id,
            target_type=target_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "Assignment",
    "AssignmentAttributes",
    "AssignmentOptions",
    "AssignmentProps",
    "CustomerManagedPolicyReference",
    "IAssignment",
    "IPermissionSet",
    "PermissionBoundary",
    "PermissionSet",
    "PermissionSetAttributes",
    "PermissionSetProps",
    "PrincipalProperty",
    "PrincipalTypes",
    "TargetTypes",
]

publication.publish()

def _typecheckingstub__7ae439f39faaa114233bc0b1a16b1904736952c8fbf1932dc6475eed1f3d817a(
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3677dd84d66e98c8bbf6b4b630ea271a32c589d1f12d4383871d2614207cad7b(
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
    permission_set: IPermissionSet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d76e58f544c6bf87eb4ed6045f0b6948c3216099d824187a7cc57942e89eb9fe(
    *,
    name: builtins.str,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d08775b809b0e566cdb84b9c89847ac6e6605d16d5345595d249a8f665bbbe(
    id: builtins.str,
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b19ce1fb3e89b904939ce873e787c40e49146fc1e9defc30a9c9e3df0a22c16(
    *,
    customer_managed_policy_reference: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_sso_ceddda9d.CfnPermissionSet.CustomerManagedPolicyReferenceProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    managed_policy_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e1c8a3a6bbb48874bcc41baf50aebc1d5b3c196abd7611f29b515aa6e0683d9(
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

def _typecheckingstub__1534cc83982ea2274a4ef806b10a9b22e16bd0a2ac53cb7e2d7d7e7e7f04522a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    permission_set_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cdc85e58620129e7f246a5cfde6e7c38745a843ac7234984317b311e146af34(
    id: builtins.str,
    *,
    principal: typing.Union[PrincipalProperty, typing.Dict[builtins.str, typing.Any]],
    target_id: builtins.str,
    target_type: typing.Optional[TargetTypes] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f41d64f11736d4f2d569f1d67bc6cf42babd45687b8f3b4e4f35e92c7ff0fe3(
    *,
    permission_set_arn: builtins.str,
    sso_instance_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a500faaedc99c37669b04cc4cb3ded8f1161916dab975452e5e55c1cb669f0(
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

def _typecheckingstub__ae5a8b88d8d2941e16b21bcde3962a352b3c0bcdac3ecd7b005ecb7859a601d5(
    *,
    principal_id: builtins.str,
    principal_type: PrincipalTypes,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eca7b2cf47acacd3579840411d5aee15f9a9bf2f86aefe69c49c627750efbf7(
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
