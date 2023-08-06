'''
# `databricks_recipient`

Refer to the Terraform Registory for docs: [`databricks_recipient`](https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient).
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


class Recipient(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.recipient.Recipient",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient databricks_recipient}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        authentication_type: builtins.str,
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        data_recipient_global_metastore_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_access_list: typing.Optional[typing.Union["RecipientIpAccessList", typing.Dict[builtins.str, typing.Any]]] = None,
        sharing_code: typing.Optional[builtins.str] = None,
        tokens: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RecipientTokens", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient databricks_recipient} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authentication_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#authentication_type Recipient#authentication_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#name Recipient#name}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#comment Recipient#comment}.
        :param data_recipient_global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#data_recipient_global_metastore_id Recipient#data_recipient_global_metastore_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#id Recipient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_access_list: ip_access_list block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#ip_access_list Recipient#ip_access_list}
        :param sharing_code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#sharing_code Recipient#sharing_code}.
        :param tokens: tokens block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#tokens Recipient#tokens}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c69c9064d8c4521e195e0afe3dfb4c49cec373fcb74f7129cac7e8bd03216e86)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RecipientConfig(
            authentication_type=authentication_type,
            name=name,
            comment=comment,
            data_recipient_global_metastore_id=data_recipient_global_metastore_id,
            id=id,
            ip_access_list=ip_access_list,
            sharing_code=sharing_code,
            tokens=tokens,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putIpAccessList")
    def put_ip_access_list(
        self,
        *,
        allowed_ip_addresses: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param allowed_ip_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#allowed_ip_addresses Recipient#allowed_ip_addresses}.
        '''
        value = RecipientIpAccessList(allowed_ip_addresses=allowed_ip_addresses)

        return typing.cast(None, jsii.invoke(self, "putIpAccessList", [value]))

    @jsii.member(jsii_name="putTokens")
    def put_tokens(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RecipientTokens", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01d927cbcd67170e19a62ab4082d4e46938bb952fd9f28e013e3ca880acbac0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTokens", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetDataRecipientGlobalMetastoreId")
    def reset_data_recipient_global_metastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataRecipientGlobalMetastoreId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpAccessList")
    def reset_ip_access_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAccessList", []))

    @jsii.member(jsii_name="resetSharingCode")
    def reset_sharing_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSharingCode", []))

    @jsii.member(jsii_name="resetTokens")
    def reset_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokens", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="ipAccessList")
    def ip_access_list(self) -> "RecipientIpAccessListOutputReference":
        return typing.cast("RecipientIpAccessListOutputReference", jsii.get(self, "ipAccessList"))

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> "RecipientTokensList":
        return typing.cast("RecipientTokensList", jsii.get(self, "tokens"))

    @builtins.property
    @jsii.member(jsii_name="authenticationTypeInput")
    def authentication_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="dataRecipientGlobalMetastoreIdInput")
    def data_recipient_global_metastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataRecipientGlobalMetastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipAccessListInput")
    def ip_access_list_input(self) -> typing.Optional["RecipientIpAccessList"]:
        return typing.cast(typing.Optional["RecipientIpAccessList"], jsii.get(self, "ipAccessListInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="sharingCodeInput")
    def sharing_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sharingCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="tokensInput")
    def tokens_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RecipientTokens"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RecipientTokens"]]], jsii.get(self, "tokensInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationType"))

    @authentication_type.setter
    def authentication_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac30220cda6363a86c401b31c463bd2edb8779421fe3bb66cd2e3b92c0a73d55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationType", value)

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b275bbadbbdc6064186ed34a3e3a015340810c981e31766b2583aac636bad952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value)

    @builtins.property
    @jsii.member(jsii_name="dataRecipientGlobalMetastoreId")
    def data_recipient_global_metastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataRecipientGlobalMetastoreId"))

    @data_recipient_global_metastore_id.setter
    def data_recipient_global_metastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e884f70dc2239b46273716c865ba2a0bd4194df48ae27bc18828a7c523b76986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataRecipientGlobalMetastoreId", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23cad6e26417ee0affceaa6edf526af2a46b3205bf7eed7617eb290db240c542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2adfff981a777ade2b23b56fcdea1fcdc14aa6291b04d6851064d5df036ae74b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="sharingCode")
    def sharing_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sharingCode"))

    @sharing_code.setter
    def sharing_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c82ceb47d75b6dbd865a985b5f54afbecc9e4c89798538db8ff24bb1fca2aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sharingCode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.recipient.RecipientConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "authentication_type": "authenticationType",
        "name": "name",
        "comment": "comment",
        "data_recipient_global_metastore_id": "dataRecipientGlobalMetastoreId",
        "id": "id",
        "ip_access_list": "ipAccessList",
        "sharing_code": "sharingCode",
        "tokens": "tokens",
    },
)
class RecipientConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        authentication_type: builtins.str,
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        data_recipient_global_metastore_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_access_list: typing.Optional[typing.Union["RecipientIpAccessList", typing.Dict[builtins.str, typing.Any]]] = None,
        sharing_code: typing.Optional[builtins.str] = None,
        tokens: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RecipientTokens", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param authentication_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#authentication_type Recipient#authentication_type}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#name Recipient#name}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#comment Recipient#comment}.
        :param data_recipient_global_metastore_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#data_recipient_global_metastore_id Recipient#data_recipient_global_metastore_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#id Recipient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_access_list: ip_access_list block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#ip_access_list Recipient#ip_access_list}
        :param sharing_code: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#sharing_code Recipient#sharing_code}.
        :param tokens: tokens block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#tokens Recipient#tokens}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ip_access_list, dict):
            ip_access_list = RecipientIpAccessList(**ip_access_list)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888161899cc76467ddd758ecd507df0ab5bbdd287fd1ebdaf5dca83f24496baf)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument authentication_type", value=authentication_type, expected_type=type_hints["authentication_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument data_recipient_global_metastore_id", value=data_recipient_global_metastore_id, expected_type=type_hints["data_recipient_global_metastore_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_access_list", value=ip_access_list, expected_type=type_hints["ip_access_list"])
            check_type(argname="argument sharing_code", value=sharing_code, expected_type=type_hints["sharing_code"])
            check_type(argname="argument tokens", value=tokens, expected_type=type_hints["tokens"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authentication_type": authentication_type,
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
        if comment is not None:
            self._values["comment"] = comment
        if data_recipient_global_metastore_id is not None:
            self._values["data_recipient_global_metastore_id"] = data_recipient_global_metastore_id
        if id is not None:
            self._values["id"] = id
        if ip_access_list is not None:
            self._values["ip_access_list"] = ip_access_list
        if sharing_code is not None:
            self._values["sharing_code"] = sharing_code
        if tokens is not None:
            self._values["tokens"] = tokens

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
    def authentication_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#authentication_type Recipient#authentication_type}.'''
        result = self._values.get("authentication_type")
        assert result is not None, "Required property 'authentication_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#name Recipient#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#comment Recipient#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_recipient_global_metastore_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#data_recipient_global_metastore_id Recipient#data_recipient_global_metastore_id}.'''
        result = self._values.get("data_recipient_global_metastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#id Recipient#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_access_list(self) -> typing.Optional["RecipientIpAccessList"]:
        '''ip_access_list block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#ip_access_list Recipient#ip_access_list}
        '''
        result = self._values.get("ip_access_list")
        return typing.cast(typing.Optional["RecipientIpAccessList"], result)

    @builtins.property
    def sharing_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#sharing_code Recipient#sharing_code}.'''
        result = self._values.get("sharing_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RecipientTokens"]]]:
        '''tokens block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#tokens Recipient#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RecipientTokens"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecipientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.recipient.RecipientIpAccessList",
    jsii_struct_bases=[],
    name_mapping={"allowed_ip_addresses": "allowedIpAddresses"},
)
class RecipientIpAccessList:
    def __init__(self, *, allowed_ip_addresses: typing.Sequence[builtins.str]) -> None:
        '''
        :param allowed_ip_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#allowed_ip_addresses Recipient#allowed_ip_addresses}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16b6633f50a092016db6cb585fb6a7205b7b063ae4383813a132f887e3036805)
            check_type(argname="argument allowed_ip_addresses", value=allowed_ip_addresses, expected_type=type_hints["allowed_ip_addresses"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allowed_ip_addresses": allowed_ip_addresses,
        }

    @builtins.property
    def allowed_ip_addresses(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#allowed_ip_addresses Recipient#allowed_ip_addresses}.'''
        result = self._values.get("allowed_ip_addresses")
        assert result is not None, "Required property 'allowed_ip_addresses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecipientIpAccessList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RecipientIpAccessListOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.recipient.RecipientIpAccessListOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1305185a5a8442405e37486409a6d3cc6846467f41bb5584a2da89b48bded34)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="allowedIpAddressesInput")
    def allowed_ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedIpAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedIpAddresses")
    def allowed_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedIpAddresses"))

    @allowed_ip_addresses.setter
    def allowed_ip_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__952b08cd64d09fa3ab561b2e2b4305ec2f241168615932eb5c7817a34492ba79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedIpAddresses", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RecipientIpAccessList]:
        return typing.cast(typing.Optional[RecipientIpAccessList], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RecipientIpAccessList]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__825ba27613764acb1315e0f5053ab52463ff580329697bec38fd960dfa4f1cd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.recipient.RecipientTokens",
    jsii_struct_bases=[],
    name_mapping={
        "activation_url": "activationUrl",
        "created_at": "createdAt",
        "created_by": "createdBy",
        "expiration_time": "expirationTime",
        "id": "id",
        "updated_at": "updatedAt",
        "updated_by": "updatedBy",
    },
)
class RecipientTokens:
    def __init__(
        self,
        *,
        activation_url: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[jsii.Number] = None,
        created_by: typing.Optional[builtins.str] = None,
        expiration_time: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[jsii.Number] = None,
        updated_by: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param activation_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#activation_url Recipient#activation_url}.
        :param created_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#created_at Recipient#created_at}.
        :param created_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#created_by Recipient#created_by}.
        :param expiration_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#expiration_time Recipient#expiration_time}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#id Recipient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param updated_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#updated_at Recipient#updated_at}.
        :param updated_by: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#updated_by Recipient#updated_by}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42ac5a80329dcd8dfc6a8de5d96858835f89c6ee809af5f79a0a83fb48061c69)
            check_type(argname="argument activation_url", value=activation_url, expected_type=type_hints["activation_url"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument expiration_time", value=expiration_time, expected_type=type_hints["expiration_time"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
            check_type(argname="argument updated_by", value=updated_by, expected_type=type_hints["updated_by"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if activation_url is not None:
            self._values["activation_url"] = activation_url
        if created_at is not None:
            self._values["created_at"] = created_at
        if created_by is not None:
            self._values["created_by"] = created_by
        if expiration_time is not None:
            self._values["expiration_time"] = expiration_time
        if id is not None:
            self._values["id"] = id
        if updated_at is not None:
            self._values["updated_at"] = updated_at
        if updated_by is not None:
            self._values["updated_by"] = updated_by

    @builtins.property
    def activation_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#activation_url Recipient#activation_url}.'''
        result = self._values.get("activation_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#created_at Recipient#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#created_by Recipient#created_by}.'''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#expiration_time Recipient#expiration_time}.'''
        result = self._values.get("expiration_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#id Recipient#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#updated_at Recipient#updated_at}.'''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def updated_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/resources/recipient#updated_by Recipient#updated_by}.'''
        result = self._values.get("updated_by")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecipientTokens(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RecipientTokensList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.recipient.RecipientTokensList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8004342fb8f139119f5897dab63b63ff047b38d30851964dc5ce0b0b70a5782)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RecipientTokensOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0c5aec59eb56544504605f70d8865c3726e88fd37576455beeebbcfa0b0b384)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RecipientTokensOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32c34dbee664458b20755da803a4ca363bca010464adcc551c3c00a6580a299e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6e525094de84a257f3646ea1a35d84da8db499b344a4ff1b415e420eb0ca40f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a798b5b2b9a0e34aa21a81f613a42ea34f98a830226587fad5c6672ee6c232c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RecipientTokens]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RecipientTokens]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RecipientTokens]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ff9256cc3df61ea558a51726ff7dc374572d5b8e1f1f3f621f1ecf7852056e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class RecipientTokensOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.recipient.RecipientTokensOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2569a65fefebc93cca3f61629987fe7b55be2628565c96f1afa2b03d7e803153)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetActivationUrl")
    def reset_activation_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActivationUrl", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetExpirationTime")
    def reset_expiration_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationTime", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetUpdatedAt")
    def reset_updated_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAt", []))

    @jsii.member(jsii_name="resetUpdatedBy")
    def reset_updated_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBy", []))

    @builtins.property
    @jsii.member(jsii_name="activationUrlInput")
    def activation_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "activationUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "createdAtInput"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationTimeInput")
    def expiration_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expirationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAtInput")
    def updated_at_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "updatedAtInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedByInput")
    def updated_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="activationUrl")
    def activation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "activationUrl"))

    @activation_url.setter
    def activation_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef2a693aae88c01067bc377b9c3c09ca5d425ba88d82484cb3a5057a695b054f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activationUrl", value)

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d133a69ccfe74b4fa5698bff310be7a566a7779aaed12689b70e35ab13fca9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value)

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a6f7affe81f2ea0894e1608e7ab66948a0d3878fc5d4869c064f5a7e109811)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value)

    @builtins.property
    @jsii.member(jsii_name="expirationTime")
    def expiration_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expirationTime"))

    @expiration_time.setter
    def expiration_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0688940752e73b1b2e93039e28a12aa01f176306b9e3339c842bfb5ab0df56b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationTime", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6447b95f0244c4ceac6fe870ed4ba9b49448b18bf2b43178183876546cd846f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "updatedAt"))

    @updated_at.setter
    def updated_at(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f632a15c47d0692066d043dda2890b19866657cfaeb5cd139c7b3199fc63d94f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAt", value)

    @builtins.property
    @jsii.member(jsii_name="updatedBy")
    def updated_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBy"))

    @updated_by.setter
    def updated_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e1a90b299f0e0b9ed9ed183dcc2188b0f3dc23648ced9213e12321c717a66fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBy", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[RecipientTokens, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[RecipientTokens, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[RecipientTokens, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2168c4faf732bfd43c81930e2b55111493649414163e6b0d5486fe339b5f15b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "Recipient",
    "RecipientConfig",
    "RecipientIpAccessList",
    "RecipientIpAccessListOutputReference",
    "RecipientTokens",
    "RecipientTokensList",
    "RecipientTokensOutputReference",
]

publication.publish()

def _typecheckingstub__c69c9064d8c4521e195e0afe3dfb4c49cec373fcb74f7129cac7e8bd03216e86(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    authentication_type: builtins.str,
    name: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    data_recipient_global_metastore_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_access_list: typing.Optional[typing.Union[RecipientIpAccessList, typing.Dict[builtins.str, typing.Any]]] = None,
    sharing_code: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RecipientTokens, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__b01d927cbcd67170e19a62ab4082d4e46938bb952fd9f28e013e3ca880acbac0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RecipientTokens, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac30220cda6363a86c401b31c463bd2edb8779421fe3bb66cd2e3b92c0a73d55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b275bbadbbdc6064186ed34a3e3a015340810c981e31766b2583aac636bad952(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e884f70dc2239b46273716c865ba2a0bd4194df48ae27bc18828a7c523b76986(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23cad6e26417ee0affceaa6edf526af2a46b3205bf7eed7617eb290db240c542(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2adfff981a777ade2b23b56fcdea1fcdc14aa6291b04d6851064d5df036ae74b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c82ceb47d75b6dbd865a985b5f54afbecc9e4c89798538db8ff24bb1fca2aee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888161899cc76467ddd758ecd507df0ab5bbdd287fd1ebdaf5dca83f24496baf(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    authentication_type: builtins.str,
    name: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    data_recipient_global_metastore_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_access_list: typing.Optional[typing.Union[RecipientIpAccessList, typing.Dict[builtins.str, typing.Any]]] = None,
    sharing_code: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RecipientTokens, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b6633f50a092016db6cb585fb6a7205b7b063ae4383813a132f887e3036805(
    *,
    allowed_ip_addresses: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1305185a5a8442405e37486409a6d3cc6846467f41bb5584a2da89b48bded34(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__952b08cd64d09fa3ab561b2e2b4305ec2f241168615932eb5c7817a34492ba79(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__825ba27613764acb1315e0f5053ab52463ff580329697bec38fd960dfa4f1cd9(
    value: typing.Optional[RecipientIpAccessList],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42ac5a80329dcd8dfc6a8de5d96858835f89c6ee809af5f79a0a83fb48061c69(
    *,
    activation_url: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[jsii.Number] = None,
    created_by: typing.Optional[builtins.str] = None,
    expiration_time: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[jsii.Number] = None,
    updated_by: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8004342fb8f139119f5897dab63b63ff047b38d30851964dc5ce0b0b70a5782(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c5aec59eb56544504605f70d8865c3726e88fd37576455beeebbcfa0b0b384(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32c34dbee664458b20755da803a4ca363bca010464adcc551c3c00a6580a299e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6e525094de84a257f3646ea1a35d84da8db499b344a4ff1b415e420eb0ca40f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a798b5b2b9a0e34aa21a81f613a42ea34f98a830226587fad5c6672ee6c232c9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ff9256cc3df61ea558a51726ff7dc374572d5b8e1f1f3f621f1ecf7852056e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RecipientTokens]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2569a65fefebc93cca3f61629987fe7b55be2628565c96f1afa2b03d7e803153(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef2a693aae88c01067bc377b9c3c09ca5d425ba88d82484cb3a5057a695b054f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d133a69ccfe74b4fa5698bff310be7a566a7779aaed12689b70e35ab13fca9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a6f7affe81f2ea0894e1608e7ab66948a0d3878fc5d4869c064f5a7e109811(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0688940752e73b1b2e93039e28a12aa01f176306b9e3339c842bfb5ab0df56b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6447b95f0244c4ceac6fe870ed4ba9b49448b18bf2b43178183876546cd846f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f632a15c47d0692066d043dda2890b19866657cfaeb5cd139c7b3199fc63d94f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e1a90b299f0e0b9ed9ed183dcc2188b0f3dc23648ced9213e12321c717a66fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2168c4faf732bfd43c81930e2b55111493649414163e6b0d5486fe339b5f15b(
    value: typing.Optional[typing.Union[RecipientTokens, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
