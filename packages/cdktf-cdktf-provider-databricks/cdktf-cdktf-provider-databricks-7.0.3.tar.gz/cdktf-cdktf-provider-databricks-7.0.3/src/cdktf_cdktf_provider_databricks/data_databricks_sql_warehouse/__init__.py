'''
# `data_databricks_sql_warehouse`

Refer to the Terraform Registory for docs: [`data_databricks_sql_warehouse`](https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse).
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


class DataDatabricksSqlWarehouse(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouse",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse databricks_sql_warehouse}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        id: builtins.str,
        auto_stop_mins: typing.Optional[jsii.Number] = None,
        channel: typing.Optional[typing.Union["DataDatabricksSqlWarehouseChannel", typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_size: typing.Optional[builtins.str] = None,
        data_source_id: typing.Optional[builtins.str] = None,
        enable_photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_serverless_compute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        jdbc_url: typing.Optional[builtins.str] = None,
        max_num_clusters: typing.Optional[jsii.Number] = None,
        min_num_clusters: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        num_clusters: typing.Optional[jsii.Number] = None,
        odbc_params: typing.Optional[typing.Union["DataDatabricksSqlWarehouseOdbcParams", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_instance_policy: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union["DataDatabricksSqlWarehouseTags", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse databricks_sql_warehouse} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#id DataDatabricksSqlWarehouse#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param auto_stop_mins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#auto_stop_mins DataDatabricksSqlWarehouse#auto_stop_mins}.
        :param channel: channel block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#channel DataDatabricksSqlWarehouse#channel}
        :param cluster_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#cluster_size DataDatabricksSqlWarehouse#cluster_size}.
        :param data_source_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#data_source_id DataDatabricksSqlWarehouse#data_source_id}.
        :param enable_photon: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_photon DataDatabricksSqlWarehouse#enable_photon}.
        :param enable_serverless_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_serverless_compute DataDatabricksSqlWarehouse#enable_serverless_compute}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#instance_profile_arn DataDatabricksSqlWarehouse#instance_profile_arn}.
        :param jdbc_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#jdbc_url DataDatabricksSqlWarehouse#jdbc_url}.
        :param max_num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#max_num_clusters DataDatabricksSqlWarehouse#max_num_clusters}.
        :param min_num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#min_num_clusters DataDatabricksSqlWarehouse#min_num_clusters}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.
        :param num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#num_clusters DataDatabricksSqlWarehouse#num_clusters}.
        :param odbc_params: odbc_params block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#odbc_params DataDatabricksSqlWarehouse#odbc_params}
        :param spot_instance_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#spot_instance_policy DataDatabricksSqlWarehouse#spot_instance_policy}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#state DataDatabricksSqlWarehouse#state}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#tags DataDatabricksSqlWarehouse#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c618d5d01cb5345a9b065cbc5bfed7f8588358c0be98b35906df774ca707e393)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDatabricksSqlWarehouseConfig(
            id=id,
            auto_stop_mins=auto_stop_mins,
            channel=channel,
            cluster_size=cluster_size,
            data_source_id=data_source_id,
            enable_photon=enable_photon,
            enable_serverless_compute=enable_serverless_compute,
            instance_profile_arn=instance_profile_arn,
            jdbc_url=jdbc_url,
            max_num_clusters=max_num_clusters,
            min_num_clusters=min_num_clusters,
            name=name,
            num_clusters=num_clusters,
            odbc_params=odbc_params,
            spot_instance_policy=spot_instance_policy,
            state=state,
            tags=tags,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putChannel")
    def put_channel(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.
        '''
        value = DataDatabricksSqlWarehouseChannel(name=name)

        return typing.cast(None, jsii.invoke(self, "putChannel", [value]))

    @jsii.member(jsii_name="putOdbcParams")
    def put_odbc_params(
        self,
        *,
        path: builtins.str,
        port: jsii.Number,
        protocol: builtins.str,
        host: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#path DataDatabricksSqlWarehouse#path}.
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#port DataDatabricksSqlWarehouse#port}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#protocol DataDatabricksSqlWarehouse#protocol}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#host DataDatabricksSqlWarehouse#host}.
        :param hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#hostname DataDatabricksSqlWarehouse#hostname}.
        '''
        value = DataDatabricksSqlWarehouseOdbcParams(
            path=path, port=port, protocol=protocol, host=host, hostname=hostname
        )

        return typing.cast(None, jsii.invoke(self, "putOdbcParams", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        *,
        custom_tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksSqlWarehouseTagsCustomTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param custom_tags: custom_tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#custom_tags DataDatabricksSqlWarehouse#custom_tags}
        '''
        value = DataDatabricksSqlWarehouseTags(custom_tags=custom_tags)

        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetAutoStopMins")
    def reset_auto_stop_mins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoStopMins", []))

    @jsii.member(jsii_name="resetChannel")
    def reset_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannel", []))

    @jsii.member(jsii_name="resetClusterSize")
    def reset_cluster_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterSize", []))

    @jsii.member(jsii_name="resetDataSourceId")
    def reset_data_source_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceId", []))

    @jsii.member(jsii_name="resetEnablePhoton")
    def reset_enable_photon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnablePhoton", []))

    @jsii.member(jsii_name="resetEnableServerlessCompute")
    def reset_enable_serverless_compute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableServerlessCompute", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetJdbcUrl")
    def reset_jdbc_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJdbcUrl", []))

    @jsii.member(jsii_name="resetMaxNumClusters")
    def reset_max_num_clusters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxNumClusters", []))

    @jsii.member(jsii_name="resetMinNumClusters")
    def reset_min_num_clusters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNumClusters", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNumClusters")
    def reset_num_clusters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumClusters", []))

    @jsii.member(jsii_name="resetOdbcParams")
    def reset_odbc_params(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOdbcParams", []))

    @jsii.member(jsii_name="resetSpotInstancePolicy")
    def reset_spot_instance_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotInstancePolicy", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="channel")
    def channel(self) -> "DataDatabricksSqlWarehouseChannelOutputReference":
        return typing.cast("DataDatabricksSqlWarehouseChannelOutputReference", jsii.get(self, "channel"))

    @builtins.property
    @jsii.member(jsii_name="odbcParams")
    def odbc_params(self) -> "DataDatabricksSqlWarehouseOdbcParamsOutputReference":
        return typing.cast("DataDatabricksSqlWarehouseOdbcParamsOutputReference", jsii.get(self, "odbcParams"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "DataDatabricksSqlWarehouseTagsOutputReference":
        return typing.cast("DataDatabricksSqlWarehouseTagsOutputReference", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="autoStopMinsInput")
    def auto_stop_mins_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoStopMinsInput"))

    @builtins.property
    @jsii.member(jsii_name="channelInput")
    def channel_input(self) -> typing.Optional["DataDatabricksSqlWarehouseChannel"]:
        return typing.cast(typing.Optional["DataDatabricksSqlWarehouseChannel"], jsii.get(self, "channelInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterSizeInput")
    def cluster_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSourceIdInput")
    def data_source_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enablePhotonInput")
    def enable_photon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enablePhotonInput"))

    @builtins.property
    @jsii.member(jsii_name="enableServerlessComputeInput")
    def enable_serverless_compute_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableServerlessComputeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property
    @jsii.member(jsii_name="jdbcUrlInput")
    def jdbc_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jdbcUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxNumClustersInput")
    def max_num_clusters_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxNumClustersInput"))

    @builtins.property
    @jsii.member(jsii_name="minNumClustersInput")
    def min_num_clusters_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNumClustersInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="numClustersInput")
    def num_clusters_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numClustersInput"))

    @builtins.property
    @jsii.member(jsii_name="odbcParamsInput")
    def odbc_params_input(
        self,
    ) -> typing.Optional["DataDatabricksSqlWarehouseOdbcParams"]:
        return typing.cast(typing.Optional["DataDatabricksSqlWarehouseOdbcParams"], jsii.get(self, "odbcParamsInput"))

    @builtins.property
    @jsii.member(jsii_name="spotInstancePolicyInput")
    def spot_instance_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotInstancePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional["DataDatabricksSqlWarehouseTags"]:
        return typing.cast(typing.Optional["DataDatabricksSqlWarehouseTags"], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoStopMins")
    def auto_stop_mins(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoStopMins"))

    @auto_stop_mins.setter
    def auto_stop_mins(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3fe422bcba4c34fe3929901b0cb9637a0047ec1841a9dc4db496826594d36ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoStopMins", value)

    @builtins.property
    @jsii.member(jsii_name="clusterSize")
    def cluster_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterSize"))

    @cluster_size.setter
    def cluster_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d496ba71503b2955e0b73de1f6fcb1cbe5dcff3a17285602d6df6a4822611efd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterSize", value)

    @builtins.property
    @jsii.member(jsii_name="dataSourceId")
    def data_source_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceId"))

    @data_source_id.setter
    def data_source_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66cc8a52ee3c4f897c2b069decc4a3bddd8028d99cba5d95ae45f4730915343b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceId", value)

    @builtins.property
    @jsii.member(jsii_name="enablePhoton")
    def enable_photon(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enablePhoton"))

    @enable_photon.setter
    def enable_photon(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d9a856d773fbf091b123cc75f3bf9d15a92089ce563f0368551b05f8197e78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enablePhoton", value)

    @builtins.property
    @jsii.member(jsii_name="enableServerlessCompute")
    def enable_serverless_compute(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableServerlessCompute"))

    @enable_serverless_compute.setter
    def enable_serverless_compute(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b99f041a8308ab66d22197cea8ed67d7cc0534c3852095d35e9374388320f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableServerlessCompute", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ae203a42bee37e8d7983a3965c7dd493bdd69ee103afbdf557053cf962daa7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf5afbc7c3b1365a22082c05202bb528f5b9ac3ad7531e9f94719791f3f95b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceProfileArn", value)

    @builtins.property
    @jsii.member(jsii_name="jdbcUrl")
    def jdbc_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jdbcUrl"))

    @jdbc_url.setter
    def jdbc_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7e028a3450a7c518e53aff4ef6b22778723728d7300c7d8b2c7f0922c55818a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jdbcUrl", value)

    @builtins.property
    @jsii.member(jsii_name="maxNumClusters")
    def max_num_clusters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxNumClusters"))

    @max_num_clusters.setter
    def max_num_clusters(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2d84115f1090cc74f87d0626fc499fd36a5e1f9bbe7133bc26b5e58fc71e39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxNumClusters", value)

    @builtins.property
    @jsii.member(jsii_name="minNumClusters")
    def min_num_clusters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNumClusters"))

    @min_num_clusters.setter
    def min_num_clusters(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64ac498a996a11306ac1c8522d4de67edb3739922c0af142efd7890a66a7e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minNumClusters", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8d915d838c2323bce7c6f1dc720957d9ff9f6338469e81e5e086ebb9effa8d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="numClusters")
    def num_clusters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numClusters"))

    @num_clusters.setter
    def num_clusters(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363ec79e2863021a5283a409d3a3296e6d878d7030d8093030855f92cbfef1ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numClusters", value)

    @builtins.property
    @jsii.member(jsii_name="spotInstancePolicy")
    def spot_instance_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotInstancePolicy"))

    @spot_instance_policy.setter
    def spot_instance_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c10f8c2912658a7aaa204018b74acece6d8ae333970050c7a51bd0688530d29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotInstancePolicy", value)

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fb34fb76e92286cba8940949de71682af0c71d36de70c89cbc055a2d8ef429e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseChannel",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class DataDatabricksSqlWarehouseChannel:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac31af6360459c9ddfe9e55262698fe20385d5d692f29eece16dda078fad5ac)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksSqlWarehouseChannel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksSqlWarehouseChannelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseChannelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be676716eb170b6da106a0500314f92213479c116a4a256a515592dfc9c0dfc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba7168d688cfa90a9e7c756fdf517e1ac2c434883479a45cb4de78f4859ee90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksSqlWarehouseChannel]:
        return typing.cast(typing.Optional[DataDatabricksSqlWarehouseChannel], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksSqlWarehouseChannel],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39b4c542c8e0974d4fa8b21fe3b2a59d28fe449816cfc82a277f19a73f58dc09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "auto_stop_mins": "autoStopMins",
        "channel": "channel",
        "cluster_size": "clusterSize",
        "data_source_id": "dataSourceId",
        "enable_photon": "enablePhoton",
        "enable_serverless_compute": "enableServerlessCompute",
        "instance_profile_arn": "instanceProfileArn",
        "jdbc_url": "jdbcUrl",
        "max_num_clusters": "maxNumClusters",
        "min_num_clusters": "minNumClusters",
        "name": "name",
        "num_clusters": "numClusters",
        "odbc_params": "odbcParams",
        "spot_instance_policy": "spotInstancePolicy",
        "state": "state",
        "tags": "tags",
    },
)
class DataDatabricksSqlWarehouseConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: builtins.str,
        auto_stop_mins: typing.Optional[jsii.Number] = None,
        channel: typing.Optional[typing.Union[DataDatabricksSqlWarehouseChannel, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_size: typing.Optional[builtins.str] = None,
        data_source_id: typing.Optional[builtins.str] = None,
        enable_photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_serverless_compute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        jdbc_url: typing.Optional[builtins.str] = None,
        max_num_clusters: typing.Optional[jsii.Number] = None,
        min_num_clusters: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        num_clusters: typing.Optional[jsii.Number] = None,
        odbc_params: typing.Optional[typing.Union["DataDatabricksSqlWarehouseOdbcParams", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_instance_policy: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union["DataDatabricksSqlWarehouseTags", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#id DataDatabricksSqlWarehouse#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param auto_stop_mins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#auto_stop_mins DataDatabricksSqlWarehouse#auto_stop_mins}.
        :param channel: channel block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#channel DataDatabricksSqlWarehouse#channel}
        :param cluster_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#cluster_size DataDatabricksSqlWarehouse#cluster_size}.
        :param data_source_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#data_source_id DataDatabricksSqlWarehouse#data_source_id}.
        :param enable_photon: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_photon DataDatabricksSqlWarehouse#enable_photon}.
        :param enable_serverless_compute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_serverless_compute DataDatabricksSqlWarehouse#enable_serverless_compute}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#instance_profile_arn DataDatabricksSqlWarehouse#instance_profile_arn}.
        :param jdbc_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#jdbc_url DataDatabricksSqlWarehouse#jdbc_url}.
        :param max_num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#max_num_clusters DataDatabricksSqlWarehouse#max_num_clusters}.
        :param min_num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#min_num_clusters DataDatabricksSqlWarehouse#min_num_clusters}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.
        :param num_clusters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#num_clusters DataDatabricksSqlWarehouse#num_clusters}.
        :param odbc_params: odbc_params block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#odbc_params DataDatabricksSqlWarehouse#odbc_params}
        :param spot_instance_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#spot_instance_policy DataDatabricksSqlWarehouse#spot_instance_policy}.
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#state DataDatabricksSqlWarehouse#state}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#tags DataDatabricksSqlWarehouse#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(channel, dict):
            channel = DataDatabricksSqlWarehouseChannel(**channel)
        if isinstance(odbc_params, dict):
            odbc_params = DataDatabricksSqlWarehouseOdbcParams(**odbc_params)
        if isinstance(tags, dict):
            tags = DataDatabricksSqlWarehouseTags(**tags)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f09ead21f057d2a9dd8e88fc710270d9cb0c3b64563d187f2ca75403029cd5c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument auto_stop_mins", value=auto_stop_mins, expected_type=type_hints["auto_stop_mins"])
            check_type(argname="argument channel", value=channel, expected_type=type_hints["channel"])
            check_type(argname="argument cluster_size", value=cluster_size, expected_type=type_hints["cluster_size"])
            check_type(argname="argument data_source_id", value=data_source_id, expected_type=type_hints["data_source_id"])
            check_type(argname="argument enable_photon", value=enable_photon, expected_type=type_hints["enable_photon"])
            check_type(argname="argument enable_serverless_compute", value=enable_serverless_compute, expected_type=type_hints["enable_serverless_compute"])
            check_type(argname="argument instance_profile_arn", value=instance_profile_arn, expected_type=type_hints["instance_profile_arn"])
            check_type(argname="argument jdbc_url", value=jdbc_url, expected_type=type_hints["jdbc_url"])
            check_type(argname="argument max_num_clusters", value=max_num_clusters, expected_type=type_hints["max_num_clusters"])
            check_type(argname="argument min_num_clusters", value=min_num_clusters, expected_type=type_hints["min_num_clusters"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument num_clusters", value=num_clusters, expected_type=type_hints["num_clusters"])
            check_type(argname="argument odbc_params", value=odbc_params, expected_type=type_hints["odbc_params"])
            check_type(argname="argument spot_instance_policy", value=spot_instance_policy, expected_type=type_hints["spot_instance_policy"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
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
        if auto_stop_mins is not None:
            self._values["auto_stop_mins"] = auto_stop_mins
        if channel is not None:
            self._values["channel"] = channel
        if cluster_size is not None:
            self._values["cluster_size"] = cluster_size
        if data_source_id is not None:
            self._values["data_source_id"] = data_source_id
        if enable_photon is not None:
            self._values["enable_photon"] = enable_photon
        if enable_serverless_compute is not None:
            self._values["enable_serverless_compute"] = enable_serverless_compute
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if jdbc_url is not None:
            self._values["jdbc_url"] = jdbc_url
        if max_num_clusters is not None:
            self._values["max_num_clusters"] = max_num_clusters
        if min_num_clusters is not None:
            self._values["min_num_clusters"] = min_num_clusters
        if name is not None:
            self._values["name"] = name
        if num_clusters is not None:
            self._values["num_clusters"] = num_clusters
        if odbc_params is not None:
            self._values["odbc_params"] = odbc_params
        if spot_instance_policy is not None:
            self._values["spot_instance_policy"] = spot_instance_policy
        if state is not None:
            self._values["state"] = state
        if tags is not None:
            self._values["tags"] = tags

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
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#id DataDatabricksSqlWarehouse#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_stop_mins(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#auto_stop_mins DataDatabricksSqlWarehouse#auto_stop_mins}.'''
        result = self._values.get("auto_stop_mins")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def channel(self) -> typing.Optional[DataDatabricksSqlWarehouseChannel]:
        '''channel block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#channel DataDatabricksSqlWarehouse#channel}
        '''
        result = self._values.get("channel")
        return typing.cast(typing.Optional[DataDatabricksSqlWarehouseChannel], result)

    @builtins.property
    def cluster_size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#cluster_size DataDatabricksSqlWarehouse#cluster_size}.'''
        result = self._values.get("cluster_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_source_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#data_source_id DataDatabricksSqlWarehouse#data_source_id}.'''
        result = self._values.get("data_source_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_photon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_photon DataDatabricksSqlWarehouse#enable_photon}.'''
        result = self._values.get("enable_photon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_serverless_compute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#enable_serverless_compute DataDatabricksSqlWarehouse#enable_serverless_compute}.'''
        result = self._values.get("enable_serverless_compute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#instance_profile_arn DataDatabricksSqlWarehouse#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jdbc_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#jdbc_url DataDatabricksSqlWarehouse#jdbc_url}.'''
        result = self._values.get("jdbc_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_num_clusters(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#max_num_clusters DataDatabricksSqlWarehouse#max_num_clusters}.'''
        result = self._values.get("max_num_clusters")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_num_clusters(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#min_num_clusters DataDatabricksSqlWarehouse#min_num_clusters}.'''
        result = self._values.get("min_num_clusters")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#name DataDatabricksSqlWarehouse#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_clusters(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#num_clusters DataDatabricksSqlWarehouse#num_clusters}.'''
        result = self._values.get("num_clusters")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def odbc_params(self) -> typing.Optional["DataDatabricksSqlWarehouseOdbcParams"]:
        '''odbc_params block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#odbc_params DataDatabricksSqlWarehouse#odbc_params}
        '''
        result = self._values.get("odbc_params")
        return typing.cast(typing.Optional["DataDatabricksSqlWarehouseOdbcParams"], result)

    @builtins.property
    def spot_instance_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#spot_instance_policy DataDatabricksSqlWarehouse#spot_instance_policy}.'''
        result = self._values.get("spot_instance_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#state DataDatabricksSqlWarehouse#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional["DataDatabricksSqlWarehouseTags"]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#tags DataDatabricksSqlWarehouse#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional["DataDatabricksSqlWarehouseTags"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksSqlWarehouseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseOdbcParams",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "port": "port",
        "protocol": "protocol",
        "host": "host",
        "hostname": "hostname",
    },
)
class DataDatabricksSqlWarehouseOdbcParams:
    def __init__(
        self,
        *,
        path: builtins.str,
        port: jsii.Number,
        protocol: builtins.str,
        host: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#path DataDatabricksSqlWarehouse#path}.
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#port DataDatabricksSqlWarehouse#port}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#protocol DataDatabricksSqlWarehouse#protocol}.
        :param host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#host DataDatabricksSqlWarehouse#host}.
        :param hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#hostname DataDatabricksSqlWarehouse#hostname}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab5d3170a5c0ea982b7941e4d98fdb79474ae182549ffc04e381d3239daecde)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
            "port": port,
            "protocol": protocol,
        }
        if host is not None:
            self._values["host"] = host
        if hostname is not None:
            self._values["hostname"] = hostname

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#path DataDatabricksSqlWarehouse#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#port DataDatabricksSqlWarehouse#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#protocol DataDatabricksSqlWarehouse#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#host DataDatabricksSqlWarehouse#host}.'''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#hostname DataDatabricksSqlWarehouse#hostname}.'''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksSqlWarehouseOdbcParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksSqlWarehouseOdbcParamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseOdbcParamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__816590e78d98d3fdf3a9f22b6f9b58fa100a7e603ccaa826d006c9e00ce28ca1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a647b16c7a343a6a6033c231e31153c1f8ba3dd989517c7766a6ac1bb8477061)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88230c5a0419ff63182f757a0e4aa72440a69b6bb0a677f9870820b0423e1824)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value)

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__522e2e555545ef23df458aaf14ed2fab1596a66f298b3610d4271d5cddeb1b89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e6bca2a3c2fddb50c879a2f601b8e0998b9fbe3d4e4a7781f816899d5b56906)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78bb77f6c323c74bec493c181f99f3b51decf818350419dde1dd30054af5ecd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksSqlWarehouseOdbcParams]:
        return typing.cast(typing.Optional[DataDatabricksSqlWarehouseOdbcParams], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksSqlWarehouseOdbcParams],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__507482471cbb8587505e7366e635eb7bd7153d843d137f888025191b4a813005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseTags",
    jsii_struct_bases=[],
    name_mapping={"custom_tags": "customTags"},
)
class DataDatabricksSqlWarehouseTags:
    def __init__(
        self,
        *,
        custom_tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksSqlWarehouseTagsCustomTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param custom_tags: custom_tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#custom_tags DataDatabricksSqlWarehouse#custom_tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e1542652e27d58355ce84770f03e89364c1e1f5d3cb9b5628c4a67a5c5d80c)
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_tags": custom_tags,
        }

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksSqlWarehouseTagsCustomTags"]]:
        '''custom_tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#custom_tags DataDatabricksSqlWarehouse#custom_tags}
        '''
        result = self._values.get("custom_tags")
        assert result is not None, "Required property 'custom_tags' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksSqlWarehouseTagsCustomTags"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksSqlWarehouseTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseTagsCustomTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataDatabricksSqlWarehouseTagsCustomTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#key DataDatabricksSqlWarehouse#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#value DataDatabricksSqlWarehouse#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__707a32c3fdf5ade2d917b165abaa87ca572d46bfdf0451feae38995c16546d5b)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#key DataDatabricksSqlWarehouse#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.16.1/docs/data-sources/sql_warehouse#value DataDatabricksSqlWarehouse#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksSqlWarehouseTagsCustomTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksSqlWarehouseTagsCustomTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseTagsCustomTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a51a5f576e20df7c2335d982baead902a5d6255bb3c3823a309e8a7a72bf6391)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksSqlWarehouseTagsCustomTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca7f36c11ebb20c98a6876da580c0cee5ac6230fb1a5a708d28eda5ef74f77e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksSqlWarehouseTagsCustomTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b779e0da78a1263a30ae193d41186f88ca7e58fa43cc1e17ef6669fac49e06b1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e114caa892fa64d30342f2bf3e6e43e95c47a18e42b3c83eac59903a95b07544)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f387906ce0799b4f255c2a1adbbfa6671f00a01cd2475c0e9658dca6ee97006a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b25ba9bbd4f7108a99940f248492f2cd212de95d6e7357317f354c55049676c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataDatabricksSqlWarehouseTagsCustomTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseTagsCustomTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b5b29e9effdce94b4f5249790f9f430630a53d846f732f39e5f5af1771467ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf88bd1f054b0d20477fd634b8bba627e7e83578fcedfa4c28302fad34099740)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3d46aac041671b11d4c9b6e7ebbf90ad7aaa6d22b44568e2d60d69835ff72e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62852b9a311c13deae28df033b52bbf6355b2bd209729da7c78b6744bf874d3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataDatabricksSqlWarehouseTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksSqlWarehouse.DataDatabricksSqlWarehouseTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4956a418be558d8a666d6036313ce93511ca3c92309d54b9688dd18f1fe5556b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomTags")
    def put_custom_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__160147ee6bca03d13181970f1ead9a1c934e6a78ca8156f6d4e2a17e5944cd4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomTags", [value]))

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> DataDatabricksSqlWarehouseTagsCustomTagsList:
        return typing.cast(DataDatabricksSqlWarehouseTagsCustomTagsList, jsii.get(self, "customTags"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDatabricksSqlWarehouseTags]:
        return typing.cast(typing.Optional[DataDatabricksSqlWarehouseTags], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksSqlWarehouseTags],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f50bc1821f2e178c07cedb06e72f68b28e074a04b1ba15cc8def041206128e70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataDatabricksSqlWarehouse",
    "DataDatabricksSqlWarehouseChannel",
    "DataDatabricksSqlWarehouseChannelOutputReference",
    "DataDatabricksSqlWarehouseConfig",
    "DataDatabricksSqlWarehouseOdbcParams",
    "DataDatabricksSqlWarehouseOdbcParamsOutputReference",
    "DataDatabricksSqlWarehouseTags",
    "DataDatabricksSqlWarehouseTagsCustomTags",
    "DataDatabricksSqlWarehouseTagsCustomTagsList",
    "DataDatabricksSqlWarehouseTagsCustomTagsOutputReference",
    "DataDatabricksSqlWarehouseTagsOutputReference",
]

publication.publish()

def _typecheckingstub__c618d5d01cb5345a9b065cbc5bfed7f8588358c0be98b35906df774ca707e393(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    id: builtins.str,
    auto_stop_mins: typing.Optional[jsii.Number] = None,
    channel: typing.Optional[typing.Union[DataDatabricksSqlWarehouseChannel, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_size: typing.Optional[builtins.str] = None,
    data_source_id: typing.Optional[builtins.str] = None,
    enable_photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_serverless_compute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    jdbc_url: typing.Optional[builtins.str] = None,
    max_num_clusters: typing.Optional[jsii.Number] = None,
    min_num_clusters: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    num_clusters: typing.Optional[jsii.Number] = None,
    odbc_params: typing.Optional[typing.Union[DataDatabricksSqlWarehouseOdbcParams, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_instance_policy: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[DataDatabricksSqlWarehouseTags, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__f3fe422bcba4c34fe3929901b0cb9637a0047ec1841a9dc4db496826594d36ec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d496ba71503b2955e0b73de1f6fcb1cbe5dcff3a17285602d6df6a4822611efd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66cc8a52ee3c4f897c2b069decc4a3bddd8028d99cba5d95ae45f4730915343b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d9a856d773fbf091b123cc75f3bf9d15a92089ce563f0368551b05f8197e78(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b99f041a8308ab66d22197cea8ed67d7cc0534c3852095d35e9374388320f2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ae203a42bee37e8d7983a3965c7dd493bdd69ee103afbdf557053cf962daa7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf5afbc7c3b1365a22082c05202bb528f5b9ac3ad7531e9f94719791f3f95b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7e028a3450a7c518e53aff4ef6b22778723728d7300c7d8b2c7f0922c55818a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d2d84115f1090cc74f87d0626fc499fd36a5e1f9bbe7133bc26b5e58fc71e39(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64ac498a996a11306ac1c8522d4de67edb3739922c0af142efd7890a66a7e2f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8d915d838c2323bce7c6f1dc720957d9ff9f6338469e81e5e086ebb9effa8d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363ec79e2863021a5283a409d3a3296e6d878d7030d8093030855f92cbfef1ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c10f8c2912658a7aaa204018b74acece6d8ae333970050c7a51bd0688530d29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb34fb76e92286cba8940949de71682af0c71d36de70c89cbc055a2d8ef429e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac31af6360459c9ddfe9e55262698fe20385d5d692f29eece16dda078fad5ac(
    *,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be676716eb170b6da106a0500314f92213479c116a4a256a515592dfc9c0dfc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba7168d688cfa90a9e7c756fdf517e1ac2c434883479a45cb4de78f4859ee90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39b4c542c8e0974d4fa8b21fe3b2a59d28fe449816cfc82a277f19a73f58dc09(
    value: typing.Optional[DataDatabricksSqlWarehouseChannel],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f09ead21f057d2a9dd8e88fc710270d9cb0c3b64563d187f2ca75403029cd5c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: builtins.str,
    auto_stop_mins: typing.Optional[jsii.Number] = None,
    channel: typing.Optional[typing.Union[DataDatabricksSqlWarehouseChannel, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_size: typing.Optional[builtins.str] = None,
    data_source_id: typing.Optional[builtins.str] = None,
    enable_photon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_serverless_compute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    instance_profile_arn: typing.Optional[builtins.str] = None,
    jdbc_url: typing.Optional[builtins.str] = None,
    max_num_clusters: typing.Optional[jsii.Number] = None,
    min_num_clusters: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    num_clusters: typing.Optional[jsii.Number] = None,
    odbc_params: typing.Optional[typing.Union[DataDatabricksSqlWarehouseOdbcParams, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_instance_policy: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[DataDatabricksSqlWarehouseTags, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab5d3170a5c0ea982b7941e4d98fdb79474ae182549ffc04e381d3239daecde(
    *,
    path: builtins.str,
    port: jsii.Number,
    protocol: builtins.str,
    host: typing.Optional[builtins.str] = None,
    hostname: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__816590e78d98d3fdf3a9f22b6f9b58fa100a7e603ccaa826d006c9e00ce28ca1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a647b16c7a343a6a6033c231e31153c1f8ba3dd989517c7766a6ac1bb8477061(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88230c5a0419ff63182f757a0e4aa72440a69b6bb0a677f9870820b0423e1824(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__522e2e555545ef23df458aaf14ed2fab1596a66f298b3610d4271d5cddeb1b89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e6bca2a3c2fddb50c879a2f601b8e0998b9fbe3d4e4a7781f816899d5b56906(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78bb77f6c323c74bec493c181f99f3b51decf818350419dde1dd30054af5ecd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__507482471cbb8587505e7366e635eb7bd7153d843d137f888025191b4a813005(
    value: typing.Optional[DataDatabricksSqlWarehouseOdbcParams],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e1542652e27d58355ce84770f03e89364c1e1f5d3cb9b5628c4a67a5c5d80c(
    *,
    custom_tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__707a32c3fdf5ade2d917b165abaa87ca572d46bfdf0451feae38995c16546d5b(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a51a5f576e20df7c2335d982baead902a5d6255bb3c3823a309e8a7a72bf6391(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca7f36c11ebb20c98a6876da580c0cee5ac6230fb1a5a708d28eda5ef74f77e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b779e0da78a1263a30ae193d41186f88ca7e58fa43cc1e17ef6669fac49e06b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e114caa892fa64d30342f2bf3e6e43e95c47a18e42b3c83eac59903a95b07544(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f387906ce0799b4f255c2a1adbbfa6671f00a01cd2475c0e9658dca6ee97006a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b25ba9bbd4f7108a99940f248492f2cd212de95d6e7357317f354c55049676c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksSqlWarehouseTagsCustomTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b5b29e9effdce94b4f5249790f9f430630a53d846f732f39e5f5af1771467ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf88bd1f054b0d20477fd634b8bba627e7e83578fcedfa4c28302fad34099740(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3d46aac041671b11d4c9b6e7ebbf90ad7aaa6d22b44568e2d60d69835ff72e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62852b9a311c13deae28df033b52bbf6355b2bd209729da7c78b6744bf874d3b(
    value: typing.Optional[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4956a418be558d8a666d6036313ce93511ca3c92309d54b9688dd18f1fe5556b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__160147ee6bca03d13181970f1ead9a1c934e6a78ca8156f6d4e2a17e5944cd4f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksSqlWarehouseTagsCustomTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f50bc1821f2e178c07cedb06e72f68b28e074a04b1ba15cc8def041206128e70(
    value: typing.Optional[DataDatabricksSqlWarehouseTags],
) -> None:
    """Type checking stubs"""
    pass
