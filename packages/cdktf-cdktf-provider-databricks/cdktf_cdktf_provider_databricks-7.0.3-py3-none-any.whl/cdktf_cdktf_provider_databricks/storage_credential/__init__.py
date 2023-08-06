'''
# `databricks_storage_credential`

Refer to the Terraform Registory for docs: [`databricks_storage_credential`](https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class StorageCredential(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredential",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential databricks_storage_credential}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        aws_iam_role: typing.Optional[typing.Union["StorageCredentialAwsIamRole", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_managed_identity: typing.Optional[typing.Union["StorageCredentialAzureManagedIdentity", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_principal: typing.Optional[typing.Union["StorageCredentialAzureServicePrincipal", typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        databricks_gcp_service_account: typing.Optional[typing.Union["StorageCredentialDatabricksGcpServiceAccount", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_service_account_key: typing.Optional[typing.Union["StorageCredentialGcpServiceAccountKey", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential databricks_storage_credential} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#name StorageCredential#name}.
        :param aws_iam_role: aws_iam_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#aws_iam_role StorageCredential#aws_iam_role}
        :param azure_managed_identity: azure_managed_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_managed_identity StorageCredential#azure_managed_identity}
        :param azure_service_principal: azure_service_principal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_service_principal StorageCredential#azure_service_principal}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#comment StorageCredential#comment}.
        :param databricks_gcp_service_account: databricks_gcp_service_account block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#databricks_gcp_service_account StorageCredential#databricks_gcp_service_account}
        :param gcp_service_account_key: gcp_service_account_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#gcp_service_account_key StorageCredential#gcp_service_account_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#id StorageCredential#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#metastore_id StorageCredential#metastore_id}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#owner StorageCredential#owner}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bdd26ff65606f3edb61ee876fb84b3ad5faa4452705bc0737f9d0d5a65e33de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = StorageCredentialConfig(
            name=name,
            aws_iam_role=aws_iam_role,
            azure_managed_identity=azure_managed_identity,
            azure_service_principal=azure_service_principal,
            comment=comment,
            databricks_gcp_service_account=databricks_gcp_service_account,
            gcp_service_account_key=gcp_service_account_key,
            id=id,
            metastore_id=metastore_id,
            owner=owner,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putAwsIamRole")
    def put_aws_iam_role(self, *, role_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#role_arn StorageCredential#role_arn}.
        '''
        value = StorageCredentialAwsIamRole(role_arn=role_arn)

        return typing.cast(None, jsii.invoke(self, "putAwsIamRole", [value]))

    @jsii.member(jsii_name="putAzureManagedIdentity")
    def put_azure_managed_identity(self, *, access_connector_id: builtins.str) -> None:
        '''
        :param access_connector_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#access_connector_id StorageCredential#access_connector_id}.
        '''
        value = StorageCredentialAzureManagedIdentity(
            access_connector_id=access_connector_id
        )

        return typing.cast(None, jsii.invoke(self, "putAzureManagedIdentity", [value]))

    @jsii.member(jsii_name="putAzureServicePrincipal")
    def put_azure_service_principal(
        self,
        *,
        application_id: builtins.str,
        client_secret: builtins.str,
        directory_id: builtins.str,
    ) -> None:
        '''
        :param application_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#application_id StorageCredential#application_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#client_secret StorageCredential#client_secret}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#directory_id StorageCredential#directory_id}.
        '''
        value = StorageCredentialAzureServicePrincipal(
            application_id=application_id,
            client_secret=client_secret,
            directory_id=directory_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAzureServicePrincipal", [value]))

    @jsii.member(jsii_name="putDatabricksGcpServiceAccount")
    def put_databricks_gcp_service_account(
        self,
        *,
        email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.
        '''
        value = StorageCredentialDatabricksGcpServiceAccount(email=email)

        return typing.cast(None, jsii.invoke(self, "putDatabricksGcpServiceAccount", [value]))

    @jsii.member(jsii_name="putGcpServiceAccountKey")
    def put_gcp_service_account_key(
        self,
        *,
        email: builtins.str,
        private_key: builtins.str,
        private_key_id: builtins.str,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key StorageCredential#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key_id StorageCredential#private_key_id}.
        '''
        value = StorageCredentialGcpServiceAccountKey(
            email=email, private_key=private_key, private_key_id=private_key_id
        )

        return typing.cast(None, jsii.invoke(self, "putGcpServiceAccountKey", [value]))

    @jsii.member(jsii_name="resetAwsIamRole")
    def reset_aws_iam_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsIamRole", []))

    @jsii.member(jsii_name="resetAzureManagedIdentity")
    def reset_azure_managed_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureManagedIdentity", []))

    @jsii.member(jsii_name="resetAzureServicePrincipal")
    def reset_azure_service_principal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureServicePrincipal", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetDatabricksGcpServiceAccount")
    def reset_databricks_gcp_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksGcpServiceAccount", []))

    @jsii.member(jsii_name="resetGcpServiceAccountKey")
    def reset_gcp_service_account_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpServiceAccountKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMetastoreId")
    def reset_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetastoreId", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="awsIamRole")
    def aws_iam_role(self) -> "StorageCredentialAwsIamRoleOutputReference":
        return typing.cast("StorageCredentialAwsIamRoleOutputReference", jsii.get(self, "awsIamRole"))

    @builtins.property
    @jsii.member(jsii_name="azureManagedIdentity")
    def azure_managed_identity(
        self,
    ) -> "StorageCredentialAzureManagedIdentityOutputReference":
        return typing.cast("StorageCredentialAzureManagedIdentityOutputReference", jsii.get(self, "azureManagedIdentity"))

    @builtins.property
    @jsii.member(jsii_name="azureServicePrincipal")
    def azure_service_principal(
        self,
    ) -> "StorageCredentialAzureServicePrincipalOutputReference":
        return typing.cast("StorageCredentialAzureServicePrincipalOutputReference", jsii.get(self, "azureServicePrincipal"))

    @builtins.property
    @jsii.member(jsii_name="databricksGcpServiceAccount")
    def databricks_gcp_service_account(
        self,
    ) -> "StorageCredentialDatabricksGcpServiceAccountOutputReference":
        return typing.cast("StorageCredentialDatabricksGcpServiceAccountOutputReference", jsii.get(self, "databricksGcpServiceAccount"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKey")
    def gcp_service_account_key(
        self,
    ) -> "StorageCredentialGcpServiceAccountKeyOutputReference":
        return typing.cast("StorageCredentialGcpServiceAccountKeyOutputReference", jsii.get(self, "gcpServiceAccountKey"))

    @builtins.property
    @jsii.member(jsii_name="awsIamRoleInput")
    def aws_iam_role_input(self) -> typing.Optional["StorageCredentialAwsIamRole"]:
        return typing.cast(typing.Optional["StorageCredentialAwsIamRole"], jsii.get(self, "awsIamRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="azureManagedIdentityInput")
    def azure_managed_identity_input(
        self,
    ) -> typing.Optional["StorageCredentialAzureManagedIdentity"]:
        return typing.cast(typing.Optional["StorageCredentialAzureManagedIdentity"], jsii.get(self, "azureManagedIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="azureServicePrincipalInput")
    def azure_service_principal_input(
        self,
    ) -> typing.Optional["StorageCredentialAzureServicePrincipal"]:
        return typing.cast(typing.Optional["StorageCredentialAzureServicePrincipal"], jsii.get(self, "azureServicePrincipalInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksGcpServiceAccountInput")
    def databricks_gcp_service_account_input(
        self,
    ) -> typing.Optional["StorageCredentialDatabricksGcpServiceAccount"]:
        return typing.cast(typing.Optional["StorageCredentialDatabricksGcpServiceAccount"], jsii.get(self, "databricksGcpServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKeyInput")
    def gcp_service_account_key_input(
        self,
    ) -> typing.Optional["StorageCredentialGcpServiceAccountKey"]:
        return typing.cast(typing.Optional["StorageCredentialGcpServiceAccountKey"], jsii.get(self, "gcpServiceAccountKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreIdInput")
    def metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b66462c30d00b3b26723bf736efbacc0f6a76ad55686e6c351e6fa00c7b66d14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aed65ab0f3b26f9c50016006c75138bdd292c5c9fa4cbc9790e1d98992c4ccc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8acf1a74430abd149b7925cd6d6525fe0d0ea078776b8ad900b9da770f70f3f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6598623a227a569070c1f1fb1a51e7cb40df2b19abb2c7e636dfc16e1d7c4141)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4589f74dd4feba7639fd427de7fbd0f86629f7e65105f12e2952dff67760b15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "owner", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAwsIamRole",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn"},
)
class StorageCredentialAwsIamRole:
    def __init__(self, *, role_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#role_arn StorageCredential#role_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b39db04e1ae816423b6b56857f9615b1a9c3a233cdedea8574295fba1c41876)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_arn": role_arn,
        }

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#role_arn StorageCredential#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialAwsIamRole(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCredentialAwsIamRoleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAwsIamRoleOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88cbe7f013199419b1fdda34e7520a8c1dce8e63cd1f8702d4c5086569585fe3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce732c986f2f6daeb15a0809313fc79156138e96c95dbfe5e5fede83add79324)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageCredentialAwsIamRole]:
        return typing.cast(typing.Optional[StorageCredentialAwsIamRole], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StorageCredentialAwsIamRole],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5099b4c818198017c54c8c0419096aebf3bcafb7db1aac74018616695426ea27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAzureManagedIdentity",
    jsii_struct_bases=[],
    name_mapping={"access_connector_id": "accessConnectorId"},
)
class StorageCredentialAzureManagedIdentity:
    def __init__(self, *, access_connector_id: builtins.str) -> None:
        '''
        :param access_connector_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#access_connector_id StorageCredential#access_connector_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d72ae04b95e66639f9e557a405f651e58561e71e34dbc132beac9ae3fe236586)
            check_type(argname="argument access_connector_id", value=access_connector_id, expected_type=type_hints["access_connector_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_connector_id": access_connector_id,
        }

    @builtins.property
    def access_connector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#access_connector_id StorageCredential#access_connector_id}.'''
        result = self._values.get("access_connector_id")
        assert result is not None, "Required property 'access_connector_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialAzureManagedIdentity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCredentialAzureManagedIdentityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAzureManagedIdentityOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fc11135f7e70eee3bb73a1dc121a19e09c3b5ee278542743a2453eeda97d338)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="accessConnectorIdInput")
    def access_connector_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessConnectorIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessConnectorId")
    def access_connector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessConnectorId"))

    @access_connector_id.setter
    def access_connector_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18440622c5e09b3b7e2f9bb5a14fe5860a0548d4dd70e2d6664ed975e9978c1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessConnectorId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageCredentialAzureManagedIdentity]:
        return typing.cast(typing.Optional[StorageCredentialAzureManagedIdentity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StorageCredentialAzureManagedIdentity],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2f1241b1cdbe49b780995aecec6e0045ad323c0d98ffb3eb1baf729e7d9b1fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAzureServicePrincipal",
    jsii_struct_bases=[],
    name_mapping={
        "application_id": "applicationId",
        "client_secret": "clientSecret",
        "directory_id": "directoryId",
    },
)
class StorageCredentialAzureServicePrincipal:
    def __init__(
        self,
        *,
        application_id: builtins.str,
        client_secret: builtins.str,
        directory_id: builtins.str,
    ) -> None:
        '''
        :param application_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#application_id StorageCredential#application_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#client_secret StorageCredential#client_secret}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#directory_id StorageCredential#directory_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bebfa1ea08ea92f2c67108ad7f85120961800fc9cf0c88d43da264c5996ac438)
            check_type(argname="argument application_id", value=application_id, expected_type=type_hints["application_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument directory_id", value=directory_id, expected_type=type_hints["directory_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_id": application_id,
            "client_secret": client_secret,
            "directory_id": directory_id,
        }

    @builtins.property
    def application_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#application_id StorageCredential#application_id}.'''
        result = self._values.get("application_id")
        assert result is not None, "Required property 'application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#client_secret StorageCredential#client_secret}.'''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def directory_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#directory_id StorageCredential#directory_id}.'''
        result = self._values.get("directory_id")
        assert result is not None, "Required property 'directory_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialAzureServicePrincipal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCredentialAzureServicePrincipalOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialAzureServicePrincipalOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62a9df0ad1dc0d66f9c3f28a88b90b2ff12083f23019480964600e7ddbae6520)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="applicationIdInput")
    def application_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @application_id.setter
    def application_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1928d01f2098c3708ca93604016b2794e67523162219afebaae7327d9186a796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80bd9aca42fbb1e0894a90e51e477ec5aeabd0ad7332a4d6235fe1125e88e3d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94153dd673c5fcf28eeb661b3b44490df7c25cd66463a9772c8894f35c89e03a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageCredentialAzureServicePrincipal]:
        return typing.cast(typing.Optional[StorageCredentialAzureServicePrincipal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StorageCredentialAzureServicePrincipal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae122a1307fd520af7f6c12a550f45baf89cc7f8ef7c1a15608b0bc38c0f489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "aws_iam_role": "awsIamRole",
        "azure_managed_identity": "azureManagedIdentity",
        "azure_service_principal": "azureServicePrincipal",
        "comment": "comment",
        "databricks_gcp_service_account": "databricksGcpServiceAccount",
        "gcp_service_account_key": "gcpServiceAccountKey",
        "id": "id",
        "metastore_id": "metastoreId",
        "owner": "owner",
    },
)
class StorageCredentialConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: builtins.str,
        aws_iam_role: typing.Optional[typing.Union[StorageCredentialAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_managed_identity: typing.Optional[typing.Union[StorageCredentialAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_principal: typing.Optional[typing.Union[StorageCredentialAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
        comment: typing.Optional[builtins.str] = None,
        databricks_gcp_service_account: typing.Optional[typing.Union["StorageCredentialDatabricksGcpServiceAccount", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_service_account_key: typing.Optional[typing.Union["StorageCredentialGcpServiceAccountKey", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        metastore_id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#name StorageCredential#name}.
        :param aws_iam_role: aws_iam_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#aws_iam_role StorageCredential#aws_iam_role}
        :param azure_managed_identity: azure_managed_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_managed_identity StorageCredential#azure_managed_identity}
        :param azure_service_principal: azure_service_principal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_service_principal StorageCredential#azure_service_principal}
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#comment StorageCredential#comment}.
        :param databricks_gcp_service_account: databricks_gcp_service_account block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#databricks_gcp_service_account StorageCredential#databricks_gcp_service_account}
        :param gcp_service_account_key: gcp_service_account_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#gcp_service_account_key StorageCredential#gcp_service_account_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#id StorageCredential#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#metastore_id StorageCredential#metastore_id}.
        :param owner: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#owner StorageCredential#owner}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aws_iam_role, dict):
            aws_iam_role = StorageCredentialAwsIamRole(**aws_iam_role)
        if isinstance(azure_managed_identity, dict):
            azure_managed_identity = StorageCredentialAzureManagedIdentity(**azure_managed_identity)
        if isinstance(azure_service_principal, dict):
            azure_service_principal = StorageCredentialAzureServicePrincipal(**azure_service_principal)
        if isinstance(databricks_gcp_service_account, dict):
            databricks_gcp_service_account = StorageCredentialDatabricksGcpServiceAccount(**databricks_gcp_service_account)
        if isinstance(gcp_service_account_key, dict):
            gcp_service_account_key = StorageCredentialGcpServiceAccountKey(**gcp_service_account_key)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ce735be4882046cb41edad11b5e96cb330fbcffcdf5c0bb299e38ff9305273)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument aws_iam_role", value=aws_iam_role, expected_type=type_hints["aws_iam_role"])
            check_type(argname="argument azure_managed_identity", value=azure_managed_identity, expected_type=type_hints["azure_managed_identity"])
            check_type(argname="argument azure_service_principal", value=azure_service_principal, expected_type=type_hints["azure_service_principal"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument databricks_gcp_service_account", value=databricks_gcp_service_account, expected_type=type_hints["databricks_gcp_service_account"])
            check_type(argname="argument gcp_service_account_key", value=gcp_service_account_key, expected_type=type_hints["gcp_service_account_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if aws_iam_role is not None:
            self._values["aws_iam_role"] = aws_iam_role
        if azure_managed_identity is not None:
            self._values["azure_managed_identity"] = azure_managed_identity
        if azure_service_principal is not None:
            self._values["azure_service_principal"] = azure_service_principal
        if comment is not None:
            self._values["comment"] = comment
        if databricks_gcp_service_account is not None:
            self._values["databricks_gcp_service_account"] = databricks_gcp_service_account
        if gcp_service_account_key is not None:
            self._values["gcp_service_account_key"] = gcp_service_account_key
        if id is not None:
            self._values["id"] = id
        if metastore_id is not None:
            self._values["metastore_id"] = metastore_id
        if owner is not None:
            self._values["owner"] = owner

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#name StorageCredential#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_iam_role(self) -> typing.Optional[StorageCredentialAwsIamRole]:
        '''aws_iam_role block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#aws_iam_role StorageCredential#aws_iam_role}
        '''
        result = self._values.get("aws_iam_role")
        return typing.cast(typing.Optional[StorageCredentialAwsIamRole], result)

    @builtins.property
    def azure_managed_identity(
        self,
    ) -> typing.Optional[StorageCredentialAzureManagedIdentity]:
        '''azure_managed_identity block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_managed_identity StorageCredential#azure_managed_identity}
        '''
        result = self._values.get("azure_managed_identity")
        return typing.cast(typing.Optional[StorageCredentialAzureManagedIdentity], result)

    @builtins.property
    def azure_service_principal(
        self,
    ) -> typing.Optional[StorageCredentialAzureServicePrincipal]:
        '''azure_service_principal block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#azure_service_principal StorageCredential#azure_service_principal}
        '''
        result = self._values.get("azure_service_principal")
        return typing.cast(typing.Optional[StorageCredentialAzureServicePrincipal], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#comment StorageCredential#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_gcp_service_account(
        self,
    ) -> typing.Optional["StorageCredentialDatabricksGcpServiceAccount"]:
        '''databricks_gcp_service_account block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#databricks_gcp_service_account StorageCredential#databricks_gcp_service_account}
        '''
        result = self._values.get("databricks_gcp_service_account")
        return typing.cast(typing.Optional["StorageCredentialDatabricksGcpServiceAccount"], result)

    @builtins.property
    def gcp_service_account_key(
        self,
    ) -> typing.Optional["StorageCredentialGcpServiceAccountKey"]:
        '''gcp_service_account_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#gcp_service_account_key StorageCredential#gcp_service_account_key}
        '''
        result = self._values.get("gcp_service_account_key")
        return typing.cast(typing.Optional["StorageCredentialGcpServiceAccountKey"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#id StorageCredential#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#metastore_id StorageCredential#metastore_id}.'''
        result = self._values.get("metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#owner StorageCredential#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialDatabricksGcpServiceAccount",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class StorageCredentialDatabricksGcpServiceAccount:
    def __init__(self, *, email: typing.Optional[builtins.str] = None) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d458103063a53f693f0f80a0297dff74eee8271cdf02cde78333bbb4553c7ee)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialDatabricksGcpServiceAccount(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCredentialDatabricksGcpServiceAccountOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialDatabricksGcpServiceAccountOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fedbca74657fb2ac9203596325c957e3ede1c3ad0d7ab864dc2952a82675f1b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEmail")
    def reset_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmail", []))

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bf77f844bcb051aefc066f558dc9a253b2b7f194ce54405336834670c39e815)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StorageCredentialDatabricksGcpServiceAccount]:
        return typing.cast(typing.Optional[StorageCredentialDatabricksGcpServiceAccount], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StorageCredentialDatabricksGcpServiceAccount],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f730025266947fef13c8f5af51de5507f8ab727def8d73432b172e1b2774c37c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialGcpServiceAccountKey",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "private_key": "privateKey",
        "private_key_id": "privateKeyId",
    },
)
class StorageCredentialGcpServiceAccountKey:
    def __init__(
        self,
        *,
        email: builtins.str,
        private_key: builtins.str,
        private_key_id: builtins.str,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key StorageCredential#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key_id StorageCredential#private_key_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68d52ec6822b6085cb1b0d384b351a0a271bd9f17d7633d29f97930671482bf7)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument private_key_id", value=private_key_id, expected_type=type_hints["private_key_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "private_key": private_key,
            "private_key_id": private_key_id,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#email StorageCredential#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key StorageCredential#private_key}.'''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/storage_credential#private_key_id StorageCredential#private_key_id}.'''
        result = self._values.get("private_key_id")
        assert result is not None, "Required property 'private_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageCredentialGcpServiceAccountKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCredentialGcpServiceAccountKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.storageCredential.StorageCredentialGcpServiceAccountKeyOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28f32f1195b7beede8fdc5fbd83621b8324a7c993824f5d16440d48fccacaf4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyIdInput")
    def private_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__137e3ecf7416bc246ff5519d2a4a1247044069370adaaf25bb47fb9c95069ea8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c36c613e4b76371b4503e941b5aac0dee760d919065f9fda3cd5e7b4e86fac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value)

    @builtins.property
    @jsii.member(jsii_name="privateKeyId")
    def private_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyId"))

    @private_key_id.setter
    def private_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd21287a4b90a8ae58db5c6df4520d90f9eb75d3c1758cc366c58ce044c87b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageCredentialGcpServiceAccountKey]:
        return typing.cast(typing.Optional[StorageCredentialGcpServiceAccountKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StorageCredentialGcpServiceAccountKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2faa49a404f2b849256ab29f4306a723ba81a612f6ecdde26a5314459393cc0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "StorageCredential",
    "StorageCredentialAwsIamRole",
    "StorageCredentialAwsIamRoleOutputReference",
    "StorageCredentialAzureManagedIdentity",
    "StorageCredentialAzureManagedIdentityOutputReference",
    "StorageCredentialAzureServicePrincipal",
    "StorageCredentialAzureServicePrincipalOutputReference",
    "StorageCredentialConfig",
    "StorageCredentialDatabricksGcpServiceAccount",
    "StorageCredentialDatabricksGcpServiceAccountOutputReference",
    "StorageCredentialGcpServiceAccountKey",
    "StorageCredentialGcpServiceAccountKeyOutputReference",
]

publication.publish()

def _typecheckingstub__9bdd26ff65606f3edb61ee876fb84b3ad5faa4452705bc0737f9d0d5a65e33de(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    aws_iam_role: typing.Optional[typing.Union[StorageCredentialAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_managed_identity: typing.Optional[typing.Union[StorageCredentialAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_principal: typing.Optional[typing.Union[StorageCredentialAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    databricks_gcp_service_account: typing.Optional[typing.Union[StorageCredentialDatabricksGcpServiceAccount, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_service_account_key: typing.Optional[typing.Union[StorageCredentialGcpServiceAccountKey, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b66462c30d00b3b26723bf736efbacc0f6a76ad55686e6c351e6fa00c7b66d14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aed65ab0f3b26f9c50016006c75138bdd292c5c9fa4cbc9790e1d98992c4ccc7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8acf1a74430abd149b7925cd6d6525fe0d0ea078776b8ad900b9da770f70f3f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6598623a227a569070c1f1fb1a51e7cb40df2b19abb2c7e636dfc16e1d7c4141(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4589f74dd4feba7639fd427de7fbd0f86629f7e65105f12e2952dff67760b15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b39db04e1ae816423b6b56857f9615b1a9c3a233cdedea8574295fba1c41876(
    *,
    role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88cbe7f013199419b1fdda34e7520a8c1dce8e63cd1f8702d4c5086569585fe3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce732c986f2f6daeb15a0809313fc79156138e96c95dbfe5e5fede83add79324(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5099b4c818198017c54c8c0419096aebf3bcafb7db1aac74018616695426ea27(
    value: typing.Optional[StorageCredentialAwsIamRole],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d72ae04b95e66639f9e557a405f651e58561e71e34dbc132beac9ae3fe236586(
    *,
    access_connector_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc11135f7e70eee3bb73a1dc121a19e09c3b5ee278542743a2453eeda97d338(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18440622c5e09b3b7e2f9bb5a14fe5860a0548d4dd70e2d6664ed975e9978c1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f1241b1cdbe49b780995aecec6e0045ad323c0d98ffb3eb1baf729e7d9b1fe(
    value: typing.Optional[StorageCredentialAzureManagedIdentity],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bebfa1ea08ea92f2c67108ad7f85120961800fc9cf0c88d43da264c5996ac438(
    *,
    application_id: builtins.str,
    client_secret: builtins.str,
    directory_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62a9df0ad1dc0d66f9c3f28a88b90b2ff12083f23019480964600e7ddbae6520(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1928d01f2098c3708ca93604016b2794e67523162219afebaae7327d9186a796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80bd9aca42fbb1e0894a90e51e477ec5aeabd0ad7332a4d6235fe1125e88e3d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94153dd673c5fcf28eeb661b3b44490df7c25cd66463a9772c8894f35c89e03a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae122a1307fd520af7f6c12a550f45baf89cc7f8ef7c1a15608b0bc38c0f489(
    value: typing.Optional[StorageCredentialAzureServicePrincipal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ce735be4882046cb41edad11b5e96cb330fbcffcdf5c0bb299e38ff9305273(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    aws_iam_role: typing.Optional[typing.Union[StorageCredentialAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_managed_identity: typing.Optional[typing.Union[StorageCredentialAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_principal: typing.Optional[typing.Union[StorageCredentialAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
    comment: typing.Optional[builtins.str] = None,
    databricks_gcp_service_account: typing.Optional[typing.Union[StorageCredentialDatabricksGcpServiceAccount, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_service_account_key: typing.Optional[typing.Union[StorageCredentialGcpServiceAccountKey, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    metastore_id: typing.Optional[builtins.str] = None,
    owner: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d458103063a53f693f0f80a0297dff74eee8271cdf02cde78333bbb4553c7ee(
    *,
    email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fedbca74657fb2ac9203596325c957e3ede1c3ad0d7ab864dc2952a82675f1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bf77f844bcb051aefc066f558dc9a253b2b7f194ce54405336834670c39e815(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f730025266947fef13c8f5af51de5507f8ab727def8d73432b172e1b2774c37c(
    value: typing.Optional[StorageCredentialDatabricksGcpServiceAccount],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68d52ec6822b6085cb1b0d384b351a0a271bd9f17d7633d29f97930671482bf7(
    *,
    email: builtins.str,
    private_key: builtins.str,
    private_key_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28f32f1195b7beede8fdc5fbd83621b8324a7c993824f5d16440d48fccacaf4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__137e3ecf7416bc246ff5519d2a4a1247044069370adaaf25bb47fb9c95069ea8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c36c613e4b76371b4503e941b5aac0dee760d919065f9fda3cd5e7b4e86fac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd21287a4b90a8ae58db5c6df4520d90f9eb75d3c1758cc366c58ce044c87b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2faa49a404f2b849256ab29f4306a723ba81a612f6ecdde26a5314459393cc0b(
    value: typing.Optional[StorageCredentialGcpServiceAccountKey],
) -> None:
    """Type checking stubs"""
    pass
