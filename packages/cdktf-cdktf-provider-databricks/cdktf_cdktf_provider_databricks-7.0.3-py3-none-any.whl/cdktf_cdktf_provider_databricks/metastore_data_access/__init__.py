'''
# `databricks_metastore_data_access`

Refer to the Terraform Registory for docs: [`databricks_metastore_data_access`](https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access).
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


class MetastoreDataAccess(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccess",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access databricks_metastore_data_access}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        metastore_id: builtins.str,
        name: builtins.str,
        aws_iam_role: typing.Optional[typing.Union["MetastoreDataAccessAwsIamRole", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_managed_identity: typing.Optional[typing.Union["MetastoreDataAccessAzureManagedIdentity", typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_principal: typing.Optional[typing.Union["MetastoreDataAccessAzureServicePrincipal", typing.Dict[builtins.str, typing.Any]]] = None,
        configuration_type: typing.Optional[builtins.str] = None,
        databricks_gcp_service_account: typing.Optional[typing.Union["MetastoreDataAccessDatabricksGcpServiceAccount", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_service_account_key: typing.Optional[typing.Union["MetastoreDataAccessGcpServiceAccountKey", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access databricks_metastore_data_access} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#metastore_id MetastoreDataAccess#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#name MetastoreDataAccess#name}.
        :param aws_iam_role: aws_iam_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#aws_iam_role MetastoreDataAccess#aws_iam_role}
        :param azure_managed_identity: azure_managed_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_managed_identity MetastoreDataAccess#azure_managed_identity}
        :param azure_service_principal: azure_service_principal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_service_principal MetastoreDataAccess#azure_service_principal}
        :param configuration_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#configuration_type MetastoreDataAccess#configuration_type}.
        :param databricks_gcp_service_account: databricks_gcp_service_account block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#databricks_gcp_service_account MetastoreDataAccess#databricks_gcp_service_account}
        :param gcp_service_account_key: gcp_service_account_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#gcp_service_account_key MetastoreDataAccess#gcp_service_account_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#id MetastoreDataAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#is_default MetastoreDataAccess#is_default}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d5d20596cb075c8d47b42557162ebea7c61970a3fd2059be34d8308bd8b18cf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MetastoreDataAccessConfig(
            metastore_id=metastore_id,
            name=name,
            aws_iam_role=aws_iam_role,
            azure_managed_identity=azure_managed_identity,
            azure_service_principal=azure_service_principal,
            configuration_type=configuration_type,
            databricks_gcp_service_account=databricks_gcp_service_account,
            gcp_service_account_key=gcp_service_account_key,
            id=id,
            is_default=is_default,
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
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#role_arn MetastoreDataAccess#role_arn}.
        '''
        value = MetastoreDataAccessAwsIamRole(role_arn=role_arn)

        return typing.cast(None, jsii.invoke(self, "putAwsIamRole", [value]))

    @jsii.member(jsii_name="putAzureManagedIdentity")
    def put_azure_managed_identity(self, *, access_connector_id: builtins.str) -> None:
        '''
        :param access_connector_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#access_connector_id MetastoreDataAccess#access_connector_id}.
        '''
        value = MetastoreDataAccessAzureManagedIdentity(
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
        :param application_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#application_id MetastoreDataAccess#application_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#client_secret MetastoreDataAccess#client_secret}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#directory_id MetastoreDataAccess#directory_id}.
        '''
        value = MetastoreDataAccessAzureServicePrincipal(
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
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.
        '''
        value = MetastoreDataAccessDatabricksGcpServiceAccount(email=email)

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
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key MetastoreDataAccess#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key_id MetastoreDataAccess#private_key_id}.
        '''
        value = MetastoreDataAccessGcpServiceAccountKey(
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

    @jsii.member(jsii_name="resetConfigurationType")
    def reset_configuration_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationType", []))

    @jsii.member(jsii_name="resetDatabricksGcpServiceAccount")
    def reset_databricks_gcp_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabricksGcpServiceAccount", []))

    @jsii.member(jsii_name="resetGcpServiceAccountKey")
    def reset_gcp_service_account_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpServiceAccountKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsDefault")
    def reset_is_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDefault", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="awsIamRole")
    def aws_iam_role(self) -> "MetastoreDataAccessAwsIamRoleOutputReference":
        return typing.cast("MetastoreDataAccessAwsIamRoleOutputReference", jsii.get(self, "awsIamRole"))

    @builtins.property
    @jsii.member(jsii_name="azureManagedIdentity")
    def azure_managed_identity(
        self,
    ) -> "MetastoreDataAccessAzureManagedIdentityOutputReference":
        return typing.cast("MetastoreDataAccessAzureManagedIdentityOutputReference", jsii.get(self, "azureManagedIdentity"))

    @builtins.property
    @jsii.member(jsii_name="azureServicePrincipal")
    def azure_service_principal(
        self,
    ) -> "MetastoreDataAccessAzureServicePrincipalOutputReference":
        return typing.cast("MetastoreDataAccessAzureServicePrincipalOutputReference", jsii.get(self, "azureServicePrincipal"))

    @builtins.property
    @jsii.member(jsii_name="databricksGcpServiceAccount")
    def databricks_gcp_service_account(
        self,
    ) -> "MetastoreDataAccessDatabricksGcpServiceAccountOutputReference":
        return typing.cast("MetastoreDataAccessDatabricksGcpServiceAccountOutputReference", jsii.get(self, "databricksGcpServiceAccount"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKey")
    def gcp_service_account_key(
        self,
    ) -> "MetastoreDataAccessGcpServiceAccountKeyOutputReference":
        return typing.cast("MetastoreDataAccessGcpServiceAccountKeyOutputReference", jsii.get(self, "gcpServiceAccountKey"))

    @builtins.property
    @jsii.member(jsii_name="awsIamRoleInput")
    def aws_iam_role_input(self) -> typing.Optional["MetastoreDataAccessAwsIamRole"]:
        return typing.cast(typing.Optional["MetastoreDataAccessAwsIamRole"], jsii.get(self, "awsIamRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="azureManagedIdentityInput")
    def azure_managed_identity_input(
        self,
    ) -> typing.Optional["MetastoreDataAccessAzureManagedIdentity"]:
        return typing.cast(typing.Optional["MetastoreDataAccessAzureManagedIdentity"], jsii.get(self, "azureManagedIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="azureServicePrincipalInput")
    def azure_service_principal_input(
        self,
    ) -> typing.Optional["MetastoreDataAccessAzureServicePrincipal"]:
        return typing.cast(typing.Optional["MetastoreDataAccessAzureServicePrincipal"], jsii.get(self, "azureServicePrincipalInput"))

    @builtins.property
    @jsii.member(jsii_name="configurationTypeInput")
    def configuration_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="databricksGcpServiceAccountInput")
    def databricks_gcp_service_account_input(
        self,
    ) -> typing.Optional["MetastoreDataAccessDatabricksGcpServiceAccount"]:
        return typing.cast(typing.Optional["MetastoreDataAccessDatabricksGcpServiceAccount"], jsii.get(self, "databricksGcpServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKeyInput")
    def gcp_service_account_key_input(
        self,
    ) -> typing.Optional["MetastoreDataAccessGcpServiceAccountKey"]:
        return typing.cast(typing.Optional["MetastoreDataAccessGcpServiceAccountKey"], jsii.get(self, "gcpServiceAccountKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="isDefaultInput")
    def is_default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="metastoreIdInput")
    def metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="configurationType")
    def configuration_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationType"))

    @configuration_type.setter
    def configuration_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ad0779772f0375365a53f555dbdc09412b1aa0a6f51a73af1ec196d69172e54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configurationType", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85050d44c2f1bf7086e6df674d4304962b70137b314d75d0c52715d136ec53b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDefault"))

    @is_default.setter
    def is_default(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a83264ca93184ace71b17a0305976c6864bab8a25fa9774d21683836a701e484)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDefault", value)

    @builtins.property
    @jsii.member(jsii_name="metastoreId")
    def metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metastoreId"))

    @metastore_id.setter
    def metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d933fb5eae4d4b12b821aa35005bb2a0b9ffa58a83bc5a2ecee4b7f3bf9f9630)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metastoreId", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd45e03caaa6df5fb22424a63c41a6d2e81ce7dd55b01be2c3db14dbe769f77f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAwsIamRole",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn"},
)
class MetastoreDataAccessAwsIamRole:
    def __init__(self, *, role_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#role_arn MetastoreDataAccess#role_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__345636d8d661973093527b0dcc71514018eddd75dffff29253742d8d6faa2679)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_arn": role_arn,
        }

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#role_arn MetastoreDataAccess#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessAwsIamRole(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetastoreDataAccessAwsIamRoleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAwsIamRoleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d264cf380bcfc1409bf43d329b3fd36358a77810a8b2fdfa0374754c71907ff4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__194ea1e1220f54910ff8bad47879972ea68fa470c7273070528a705a82d3fb4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MetastoreDataAccessAwsIamRole]:
        return typing.cast(typing.Optional[MetastoreDataAccessAwsIamRole], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MetastoreDataAccessAwsIamRole],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b71683822509884d3144d742269ca7bd79b84e2326b519ae963c00a538b384d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAzureManagedIdentity",
    jsii_struct_bases=[],
    name_mapping={"access_connector_id": "accessConnectorId"},
)
class MetastoreDataAccessAzureManagedIdentity:
    def __init__(self, *, access_connector_id: builtins.str) -> None:
        '''
        :param access_connector_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#access_connector_id MetastoreDataAccess#access_connector_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f330917c816dbcc8c1569bb6fd3e8f10f622bf398a09f46a7d41e87d2b0c21b)
            check_type(argname="argument access_connector_id", value=access_connector_id, expected_type=type_hints["access_connector_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_connector_id": access_connector_id,
        }

    @builtins.property
    def access_connector_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#access_connector_id MetastoreDataAccess#access_connector_id}.'''
        result = self._values.get("access_connector_id")
        assert result is not None, "Required property 'access_connector_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessAzureManagedIdentity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetastoreDataAccessAzureManagedIdentityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAzureManagedIdentityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8515bd3476a90b6cc220dfcd28259214bd6e1dbf7bef01362e6c68990aed9b3c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__baf0b3531d95c8b9bbb2da5fe792511406713c345745a3c4d3686b92263ca08d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessConnectorId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MetastoreDataAccessAzureManagedIdentity]:
        return typing.cast(typing.Optional[MetastoreDataAccessAzureManagedIdentity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MetastoreDataAccessAzureManagedIdentity],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0334463a477b9cc6e81b410ad9dd585540b67b1ef5e57fdb24e7c68f5a957c43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAzureServicePrincipal",
    jsii_struct_bases=[],
    name_mapping={
        "application_id": "applicationId",
        "client_secret": "clientSecret",
        "directory_id": "directoryId",
    },
)
class MetastoreDataAccessAzureServicePrincipal:
    def __init__(
        self,
        *,
        application_id: builtins.str,
        client_secret: builtins.str,
        directory_id: builtins.str,
    ) -> None:
        '''
        :param application_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#application_id MetastoreDataAccess#application_id}.
        :param client_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#client_secret MetastoreDataAccess#client_secret}.
        :param directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#directory_id MetastoreDataAccess#directory_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dbeae502c6a81954e5120eb95b4643b07ab1be81e7db40a768a7807df506a84)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#application_id MetastoreDataAccess#application_id}.'''
        result = self._values.get("application_id")
        assert result is not None, "Required property 'application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#client_secret MetastoreDataAccess#client_secret}.'''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def directory_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#directory_id MetastoreDataAccess#directory_id}.'''
        result = self._values.get("directory_id")
        assert result is not None, "Required property 'directory_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessAzureServicePrincipal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetastoreDataAccessAzureServicePrincipalOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessAzureServicePrincipalOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4dfd25f064e32f0f0323a5eb3f09b52c7a80fed27a697778d76881b8877d68c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__20bcf76f5f2c2aee71df541ce932e0eafde6e8b0e6a0c6ba9d622182ed93e26e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a0312469f2011c3a28652bb160ee049c22b30785a02c301d10bf595a2fc6237)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__638b3231d401a02f1ce897c6690a6f883e59be49ebf9912629437e5a726ce395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directoryId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MetastoreDataAccessAzureServicePrincipal]:
        return typing.cast(typing.Optional[MetastoreDataAccessAzureServicePrincipal], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MetastoreDataAccessAzureServicePrincipal],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8797efe179ee05ce91df0bd364b8e718a171149903c7ffb2a1003ec533f0346)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "metastore_id": "metastoreId",
        "name": "name",
        "aws_iam_role": "awsIamRole",
        "azure_managed_identity": "azureManagedIdentity",
        "azure_service_principal": "azureServicePrincipal",
        "configuration_type": "configurationType",
        "databricks_gcp_service_account": "databricksGcpServiceAccount",
        "gcp_service_account_key": "gcpServiceAccountKey",
        "id": "id",
        "is_default": "isDefault",
    },
)
class MetastoreDataAccessConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        metastore_id: builtins.str,
        name: builtins.str,
        aws_iam_role: typing.Optional[typing.Union[MetastoreDataAccessAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_managed_identity: typing.Optional[typing.Union[MetastoreDataAccessAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
        azure_service_principal: typing.Optional[typing.Union[MetastoreDataAccessAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
        configuration_type: typing.Optional[builtins.str] = None,
        databricks_gcp_service_account: typing.Optional[typing.Union["MetastoreDataAccessDatabricksGcpServiceAccount", typing.Dict[builtins.str, typing.Any]]] = None,
        gcp_service_account_key: typing.Optional[typing.Union["MetastoreDataAccessGcpServiceAccountKey", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#metastore_id MetastoreDataAccess#metastore_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#name MetastoreDataAccess#name}.
        :param aws_iam_role: aws_iam_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#aws_iam_role MetastoreDataAccess#aws_iam_role}
        :param azure_managed_identity: azure_managed_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_managed_identity MetastoreDataAccess#azure_managed_identity}
        :param azure_service_principal: azure_service_principal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_service_principal MetastoreDataAccess#azure_service_principal}
        :param configuration_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#configuration_type MetastoreDataAccess#configuration_type}.
        :param databricks_gcp_service_account: databricks_gcp_service_account block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#databricks_gcp_service_account MetastoreDataAccess#databricks_gcp_service_account}
        :param gcp_service_account_key: gcp_service_account_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#gcp_service_account_key MetastoreDataAccess#gcp_service_account_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#id MetastoreDataAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#is_default MetastoreDataAccess#is_default}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aws_iam_role, dict):
            aws_iam_role = MetastoreDataAccessAwsIamRole(**aws_iam_role)
        if isinstance(azure_managed_identity, dict):
            azure_managed_identity = MetastoreDataAccessAzureManagedIdentity(**azure_managed_identity)
        if isinstance(azure_service_principal, dict):
            azure_service_principal = MetastoreDataAccessAzureServicePrincipal(**azure_service_principal)
        if isinstance(databricks_gcp_service_account, dict):
            databricks_gcp_service_account = MetastoreDataAccessDatabricksGcpServiceAccount(**databricks_gcp_service_account)
        if isinstance(gcp_service_account_key, dict):
            gcp_service_account_key = MetastoreDataAccessGcpServiceAccountKey(**gcp_service_account_key)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca0b77608b3be2e9c3e288df50be50e0853f74f19588d104e348a8e0dc462a4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument metastore_id", value=metastore_id, expected_type=type_hints["metastore_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument aws_iam_role", value=aws_iam_role, expected_type=type_hints["aws_iam_role"])
            check_type(argname="argument azure_managed_identity", value=azure_managed_identity, expected_type=type_hints["azure_managed_identity"])
            check_type(argname="argument azure_service_principal", value=azure_service_principal, expected_type=type_hints["azure_service_principal"])
            check_type(argname="argument configuration_type", value=configuration_type, expected_type=type_hints["configuration_type"])
            check_type(argname="argument databricks_gcp_service_account", value=databricks_gcp_service_account, expected_type=type_hints["databricks_gcp_service_account"])
            check_type(argname="argument gcp_service_account_key", value=gcp_service_account_key, expected_type=type_hints["gcp_service_account_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument is_default", value=is_default, expected_type=type_hints["is_default"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metastore_id": metastore_id,
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
        if configuration_type is not None:
            self._values["configuration_type"] = configuration_type
        if databricks_gcp_service_account is not None:
            self._values["databricks_gcp_service_account"] = databricks_gcp_service_account
        if gcp_service_account_key is not None:
            self._values["gcp_service_account_key"] = gcp_service_account_key
        if id is not None:
            self._values["id"] = id
        if is_default is not None:
            self._values["is_default"] = is_default

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
    def metastore_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#metastore_id MetastoreDataAccess#metastore_id}.'''
        result = self._values.get("metastore_id")
        assert result is not None, "Required property 'metastore_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#name MetastoreDataAccess#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_iam_role(self) -> typing.Optional[MetastoreDataAccessAwsIamRole]:
        '''aws_iam_role block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#aws_iam_role MetastoreDataAccess#aws_iam_role}
        '''
        result = self._values.get("aws_iam_role")
        return typing.cast(typing.Optional[MetastoreDataAccessAwsIamRole], result)

    @builtins.property
    def azure_managed_identity(
        self,
    ) -> typing.Optional[MetastoreDataAccessAzureManagedIdentity]:
        '''azure_managed_identity block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_managed_identity MetastoreDataAccess#azure_managed_identity}
        '''
        result = self._values.get("azure_managed_identity")
        return typing.cast(typing.Optional[MetastoreDataAccessAzureManagedIdentity], result)

    @builtins.property
    def azure_service_principal(
        self,
    ) -> typing.Optional[MetastoreDataAccessAzureServicePrincipal]:
        '''azure_service_principal block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#azure_service_principal MetastoreDataAccess#azure_service_principal}
        '''
        result = self._values.get("azure_service_principal")
        return typing.cast(typing.Optional[MetastoreDataAccessAzureServicePrincipal], result)

    @builtins.property
    def configuration_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#configuration_type MetastoreDataAccess#configuration_type}.'''
        result = self._values.get("configuration_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databricks_gcp_service_account(
        self,
    ) -> typing.Optional["MetastoreDataAccessDatabricksGcpServiceAccount"]:
        '''databricks_gcp_service_account block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#databricks_gcp_service_account MetastoreDataAccess#databricks_gcp_service_account}
        '''
        result = self._values.get("databricks_gcp_service_account")
        return typing.cast(typing.Optional["MetastoreDataAccessDatabricksGcpServiceAccount"], result)

    @builtins.property
    def gcp_service_account_key(
        self,
    ) -> typing.Optional["MetastoreDataAccessGcpServiceAccountKey"]:
        '''gcp_service_account_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#gcp_service_account_key MetastoreDataAccess#gcp_service_account_key}
        '''
        result = self._values.get("gcp_service_account_key")
        return typing.cast(typing.Optional["MetastoreDataAccessGcpServiceAccountKey"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#id MetastoreDataAccess#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#is_default MetastoreDataAccess#is_default}.'''
        result = self._values.get("is_default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessDatabricksGcpServiceAccount",
    jsii_struct_bases=[],
    name_mapping={"email": "email"},
)
class MetastoreDataAccessDatabricksGcpServiceAccount:
    def __init__(self, *, email: typing.Optional[builtins.str] = None) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3dc45e556d238ebd000414fba094a904ac62c4fce9b1a14a073e19cd42d3bd5)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessDatabricksGcpServiceAccount(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetastoreDataAccessDatabricksGcpServiceAccountOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessDatabricksGcpServiceAccountOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28fffa398504a4ec3871aac07ba40c4ac07f65a7cabf01789d39dff6b153df05)
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
            type_hints = typing.get_type_hints(_typecheckingstub__359593fb60ef2aa68df2e8649b461be31198942076aa3bbab8ac35eb78841441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MetastoreDataAccessDatabricksGcpServiceAccount]:
        return typing.cast(typing.Optional[MetastoreDataAccessDatabricksGcpServiceAccount], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MetastoreDataAccessDatabricksGcpServiceAccount],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd2e76cad4b2ecf204deae0ef2e4c205f924534a03a8ba67f2a7b7683fcf1f19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessGcpServiceAccountKey",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "private_key": "privateKey",
        "private_key_id": "privateKeyId",
    },
)
class MetastoreDataAccessGcpServiceAccountKey:
    def __init__(
        self,
        *,
        email: builtins.str,
        private_key: builtins.str,
        private_key_id: builtins.str,
    ) -> None:
        '''
        :param email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key MetastoreDataAccess#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key_id MetastoreDataAccess#private_key_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__757fa27e0892ae0f6b0304363060408c75c648ce3aab754f0fe39df196f45644)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#email MetastoreDataAccess#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key MetastoreDataAccess#private_key}.'''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/metastore_data_access#private_key_id MetastoreDataAccess#private_key_id}.'''
        result = self._values.get("private_key_id")
        assert result is not None, "Required property 'private_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetastoreDataAccessGcpServiceAccountKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MetastoreDataAccessGcpServiceAccountKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.metastoreDataAccess.MetastoreDataAccessGcpServiceAccountKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__359e3d2d504efd44cc27946d1c8f380e633948895abe456b15650fa2f3cc1aea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ab04a4ff26136b08a8c2f7dc15a18583529893ad194ad5e1aa840acf155d686)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value)

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7058fe0cacd57f6bbf858aa262095914fbcf37755b87bc5d5807dce6073e265)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value)

    @builtins.property
    @jsii.member(jsii_name="privateKeyId")
    def private_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyId"))

    @private_key_id.setter
    def private_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7afb7acfa29cc7d19f45e4dc608959903e3a972f4901540b87e41a9b3c395fd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MetastoreDataAccessGcpServiceAccountKey]:
        return typing.cast(typing.Optional[MetastoreDataAccessGcpServiceAccountKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MetastoreDataAccessGcpServiceAccountKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f9d98083d0239275dc2d9d452e18da3ed7403f0ff5b7a165f6746f3a2d425c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "MetastoreDataAccess",
    "MetastoreDataAccessAwsIamRole",
    "MetastoreDataAccessAwsIamRoleOutputReference",
    "MetastoreDataAccessAzureManagedIdentity",
    "MetastoreDataAccessAzureManagedIdentityOutputReference",
    "MetastoreDataAccessAzureServicePrincipal",
    "MetastoreDataAccessAzureServicePrincipalOutputReference",
    "MetastoreDataAccessConfig",
    "MetastoreDataAccessDatabricksGcpServiceAccount",
    "MetastoreDataAccessDatabricksGcpServiceAccountOutputReference",
    "MetastoreDataAccessGcpServiceAccountKey",
    "MetastoreDataAccessGcpServiceAccountKeyOutputReference",
]

publication.publish()

def _typecheckingstub__1d5d20596cb075c8d47b42557162ebea7c61970a3fd2059be34d8308bd8b18cf(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    metastore_id: builtins.str,
    name: builtins.str,
    aws_iam_role: typing.Optional[typing.Union[MetastoreDataAccessAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_managed_identity: typing.Optional[typing.Union[MetastoreDataAccessAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_principal: typing.Optional[typing.Union[MetastoreDataAccessAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
    configuration_type: typing.Optional[builtins.str] = None,
    databricks_gcp_service_account: typing.Optional[typing.Union[MetastoreDataAccessDatabricksGcpServiceAccount, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_service_account_key: typing.Optional[typing.Union[MetastoreDataAccessGcpServiceAccountKey, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__4ad0779772f0375365a53f555dbdc09412b1aa0a6f51a73af1ec196d69172e54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85050d44c2f1bf7086e6df674d4304962b70137b314d75d0c52715d136ec53b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a83264ca93184ace71b17a0305976c6864bab8a25fa9774d21683836a701e484(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d933fb5eae4d4b12b821aa35005bb2a0b9ffa58a83bc5a2ecee4b7f3bf9f9630(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd45e03caaa6df5fb22424a63c41a6d2e81ce7dd55b01be2c3db14dbe769f77f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__345636d8d661973093527b0dcc71514018eddd75dffff29253742d8d6faa2679(
    *,
    role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d264cf380bcfc1409bf43d329b3fd36358a77810a8b2fdfa0374754c71907ff4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__194ea1e1220f54910ff8bad47879972ea68fa470c7273070528a705a82d3fb4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b71683822509884d3144d742269ca7bd79b84e2326b519ae963c00a538b384d(
    value: typing.Optional[MetastoreDataAccessAwsIamRole],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f330917c816dbcc8c1569bb6fd3e8f10f622bf398a09f46a7d41e87d2b0c21b(
    *,
    access_connector_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8515bd3476a90b6cc220dfcd28259214bd6e1dbf7bef01362e6c68990aed9b3c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf0b3531d95c8b9bbb2da5fe792511406713c345745a3c4d3686b92263ca08d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0334463a477b9cc6e81b410ad9dd585540b67b1ef5e57fdb24e7c68f5a957c43(
    value: typing.Optional[MetastoreDataAccessAzureManagedIdentity],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dbeae502c6a81954e5120eb95b4643b07ab1be81e7db40a768a7807df506a84(
    *,
    application_id: builtins.str,
    client_secret: builtins.str,
    directory_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dfd25f064e32f0f0323a5eb3f09b52c7a80fed27a697778d76881b8877d68c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20bcf76f5f2c2aee71df541ce932e0eafde6e8b0e6a0c6ba9d622182ed93e26e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a0312469f2011c3a28652bb160ee049c22b30785a02c301d10bf595a2fc6237(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__638b3231d401a02f1ce897c6690a6f883e59be49ebf9912629437e5a726ce395(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8797efe179ee05ce91df0bd364b8e718a171149903c7ffb2a1003ec533f0346(
    value: typing.Optional[MetastoreDataAccessAzureServicePrincipal],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca0b77608b3be2e9c3e288df50be50e0853f74f19588d104e348a8e0dc462a4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    metastore_id: builtins.str,
    name: builtins.str,
    aws_iam_role: typing.Optional[typing.Union[MetastoreDataAccessAwsIamRole, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_managed_identity: typing.Optional[typing.Union[MetastoreDataAccessAzureManagedIdentity, typing.Dict[builtins.str, typing.Any]]] = None,
    azure_service_principal: typing.Optional[typing.Union[MetastoreDataAccessAzureServicePrincipal, typing.Dict[builtins.str, typing.Any]]] = None,
    configuration_type: typing.Optional[builtins.str] = None,
    databricks_gcp_service_account: typing.Optional[typing.Union[MetastoreDataAccessDatabricksGcpServiceAccount, typing.Dict[builtins.str, typing.Any]]] = None,
    gcp_service_account_key: typing.Optional[typing.Union[MetastoreDataAccessGcpServiceAccountKey, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3dc45e556d238ebd000414fba094a904ac62c4fce9b1a14a073e19cd42d3bd5(
    *,
    email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28fffa398504a4ec3871aac07ba40c4ac07f65a7cabf01789d39dff6b153df05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__359593fb60ef2aa68df2e8649b461be31198942076aa3bbab8ac35eb78841441(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd2e76cad4b2ecf204deae0ef2e4c205f924534a03a8ba67f2a7b7683fcf1f19(
    value: typing.Optional[MetastoreDataAccessDatabricksGcpServiceAccount],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__757fa27e0892ae0f6b0304363060408c75c648ce3aab754f0fe39df196f45644(
    *,
    email: builtins.str,
    private_key: builtins.str,
    private_key_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__359e3d2d504efd44cc27946d1c8f380e633948895abe456b15650fa2f3cc1aea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ab04a4ff26136b08a8c2f7dc15a18583529893ad194ad5e1aa840acf155d686(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7058fe0cacd57f6bbf858aa262095914fbcf37755b87bc5d5807dce6073e265(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7afb7acfa29cc7d19f45e4dc608959903e3a972f4901540b87e41a9b3c395fd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f9d98083d0239275dc2d9d452e18da3ed7403f0ff5b7a165f6746f3a2d425c0(
    value: typing.Optional[MetastoreDataAccessGcpServiceAccountKey],
) -> None:
    """Type checking stubs"""
    pass
