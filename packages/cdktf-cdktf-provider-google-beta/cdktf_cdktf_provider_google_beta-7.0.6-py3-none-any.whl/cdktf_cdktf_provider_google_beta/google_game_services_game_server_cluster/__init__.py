'''
# `google_game_services_game_server_cluster`

Refer to the Terraform Registory for docs: [`google_game_services_game_server_cluster`](https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster).
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


class GoogleGameServicesGameServerCluster(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerCluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster google_game_services_game_server_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        connection_info: typing.Union["GoogleGameServicesGameServerClusterConnectionInfo", typing.Dict[builtins.str, typing.Any]],
        realm_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        location: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleGameServicesGameServerClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster google_game_services_game_server_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Required. The resource name of the game server cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster_id GoogleGameServicesGameServerCluster#cluster_id}
        :param connection_info: connection_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#connection_info GoogleGameServicesGameServerCluster#connection_info}
        :param realm_id: The realm id of the game server realm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#realm_id GoogleGameServicesGameServerCluster#realm_id}
        :param description: Human readable description of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#description GoogleGameServicesGameServerCluster#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#id GoogleGameServicesGameServerCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: The labels associated with this game server cluster. Each label is a key-value pair. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#labels GoogleGameServicesGameServerCluster#labels}
        :param location: Location of the Cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#location GoogleGameServicesGameServerCluster#location}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#project GoogleGameServicesGameServerCluster#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#timeouts GoogleGameServicesGameServerCluster#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eda1ea17ba7ec4cb4fb374c7c78456e2e02732745a79a5739e4a92e893040a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleGameServicesGameServerClusterConfig(
            cluster_id=cluster_id,
            connection_info=connection_info,
            realm_id=realm_id,
            description=description,
            id=id,
            labels=labels,
            location=location,
            project=project,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putConnectionInfo")
    def put_connection_info(
        self,
        *,
        gke_cluster_reference: typing.Union["GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference", typing.Dict[builtins.str, typing.Any]],
        namespace: builtins.str,
    ) -> None:
        '''
        :param gke_cluster_reference: gke_cluster_reference block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#gke_cluster_reference GoogleGameServicesGameServerCluster#gke_cluster_reference}
        :param namespace: Namespace designated on the game server cluster where the game server instances will be created. The namespace existence will be validated during creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#namespace GoogleGameServicesGameServerCluster#namespace}
        '''
        value = GoogleGameServicesGameServerClusterConnectionInfo(
            gke_cluster_reference=gke_cluster_reference, namespace=namespace
        )

        return typing.cast(None, jsii.invoke(self, "putConnectionInfo", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#create GoogleGameServicesGameServerCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#delete GoogleGameServicesGameServerCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#update GoogleGameServicesGameServerCluster#update}.
        '''
        value = GoogleGameServicesGameServerClusterTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="connectionInfo")
    def connection_info(
        self,
    ) -> "GoogleGameServicesGameServerClusterConnectionInfoOutputReference":
        return typing.cast("GoogleGameServicesGameServerClusterConnectionInfoOutputReference", jsii.get(self, "connectionInfo"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleGameServicesGameServerClusterTimeoutsOutputReference":
        return typing.cast("GoogleGameServicesGameServerClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionInfoInput")
    def connection_info_input(
        self,
    ) -> typing.Optional["GoogleGameServicesGameServerClusterConnectionInfo"]:
        return typing.cast(typing.Optional["GoogleGameServicesGameServerClusterConnectionInfo"], jsii.get(self, "connectionInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="realmIdInput")
    def realm_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realmIdInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["GoogleGameServicesGameServerClusterTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["GoogleGameServicesGameServerClusterTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f097304b59739de87bbbecef22b722435c08f9708dbd3318af1783703831f4c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__557b36dbcddea48ccc425524656fb8e4974e7641574d210e736fc14c6b79dc6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd211e98101948a61907834fc7748f149959f39b12f8b4a3f7c1a624d2e1b31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088a08b70f52f61037eb5fafabc5baa186d7557e4308894b39181c8d5fc7b962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d189dd164eea4ed21460cd5ce96ba9c8beb66ba5a4352e58b907c65f09de99a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3307277c5356733b19ffaaedd7731042033accb7f5e2b08ea5ad71083e1c430)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)

    @builtins.property
    @jsii.member(jsii_name="realmId")
    def realm_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "realmId"))

    @realm_id.setter
    def realm_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b1dc77e91d4fbc6032397e3af9aef8acc8af745a18718f39af15af31a60ee17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realmId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_id": "clusterId",
        "connection_info": "connectionInfo",
        "realm_id": "realmId",
        "description": "description",
        "id": "id",
        "labels": "labels",
        "location": "location",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class GoogleGameServicesGameServerClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_id: builtins.str,
        connection_info: typing.Union["GoogleGameServicesGameServerClusterConnectionInfo", typing.Dict[builtins.str, typing.Any]],
        realm_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        location: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleGameServicesGameServerClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Required. The resource name of the game server cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster_id GoogleGameServicesGameServerCluster#cluster_id}
        :param connection_info: connection_info block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#connection_info GoogleGameServicesGameServerCluster#connection_info}
        :param realm_id: The realm id of the game server realm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#realm_id GoogleGameServicesGameServerCluster#realm_id}
        :param description: Human readable description of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#description GoogleGameServicesGameServerCluster#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#id GoogleGameServicesGameServerCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: The labels associated with this game server cluster. Each label is a key-value pair. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#labels GoogleGameServicesGameServerCluster#labels}
        :param location: Location of the Cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#location GoogleGameServicesGameServerCluster#location}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#project GoogleGameServicesGameServerCluster#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#timeouts GoogleGameServicesGameServerCluster#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(connection_info, dict):
            connection_info = GoogleGameServicesGameServerClusterConnectionInfo(**connection_info)
        if isinstance(timeouts, dict):
            timeouts = GoogleGameServicesGameServerClusterTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5dd1603984257b6ef53fc7bcb869550700ec998a898ba8fbfc5f31539114d0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument connection_info", value=connection_info, expected_type=type_hints["connection_info"])
            check_type(argname="argument realm_id", value=realm_id, expected_type=type_hints["realm_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_id": cluster_id,
            "connection_info": connection_info,
            "realm_id": realm_id,
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if labels is not None:
            self._values["labels"] = labels
        if location is not None:
            self._values["location"] = location
        if project is not None:
            self._values["project"] = project
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def cluster_id(self) -> builtins.str:
        '''Required. The resource name of the game server cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster_id GoogleGameServicesGameServerCluster#cluster_id}
        '''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_info(self) -> "GoogleGameServicesGameServerClusterConnectionInfo":
        '''connection_info block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#connection_info GoogleGameServicesGameServerCluster#connection_info}
        '''
        result = self._values.get("connection_info")
        assert result is not None, "Required property 'connection_info' is missing"
        return typing.cast("GoogleGameServicesGameServerClusterConnectionInfo", result)

    @builtins.property
    def realm_id(self) -> builtins.str:
        '''The realm id of the game server realm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#realm_id GoogleGameServicesGameServerCluster#realm_id}
        '''
        result = self._values.get("realm_id")
        assert result is not None, "Required property 'realm_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human readable description of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#description GoogleGameServicesGameServerCluster#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#id GoogleGameServicesGameServerCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The labels associated with this game server cluster. Each label is a key-value pair.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#labels GoogleGameServicesGameServerCluster#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''Location of the Cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#location GoogleGameServicesGameServerCluster#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#project GoogleGameServicesGameServerCluster#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(
        self,
    ) -> typing.Optional["GoogleGameServicesGameServerClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#timeouts GoogleGameServicesGameServerCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleGameServicesGameServerClusterTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterConnectionInfo",
    jsii_struct_bases=[],
    name_mapping={
        "gke_cluster_reference": "gkeClusterReference",
        "namespace": "namespace",
    },
)
class GoogleGameServicesGameServerClusterConnectionInfo:
    def __init__(
        self,
        *,
        gke_cluster_reference: typing.Union["GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference", typing.Dict[builtins.str, typing.Any]],
        namespace: builtins.str,
    ) -> None:
        '''
        :param gke_cluster_reference: gke_cluster_reference block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#gke_cluster_reference GoogleGameServicesGameServerCluster#gke_cluster_reference}
        :param namespace: Namespace designated on the game server cluster where the game server instances will be created. The namespace existence will be validated during creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#namespace GoogleGameServicesGameServerCluster#namespace}
        '''
        if isinstance(gke_cluster_reference, dict):
            gke_cluster_reference = GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference(**gke_cluster_reference)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4dbe9e2b81c7eac0018e38f2582df1578885de3e05594bf3b3493ab8b188202)
            check_type(argname="argument gke_cluster_reference", value=gke_cluster_reference, expected_type=type_hints["gke_cluster_reference"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gke_cluster_reference": gke_cluster_reference,
            "namespace": namespace,
        }

    @builtins.property
    def gke_cluster_reference(
        self,
    ) -> "GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference":
        '''gke_cluster_reference block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#gke_cluster_reference GoogleGameServicesGameServerCluster#gke_cluster_reference}
        '''
        result = self._values.get("gke_cluster_reference")
        assert result is not None, "Required property 'gke_cluster_reference' is missing"
        return typing.cast("GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference", result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Namespace designated on the game server cluster where the game server instances will be created.

        The namespace existence will be validated
        during creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#namespace GoogleGameServicesGameServerCluster#namespace}
        '''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerClusterConnectionInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster"},
)
class GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference:
    def __init__(self, *, cluster: builtins.str) -> None:
        '''
        :param cluster: The full or partial name of a GKE cluster, using one of the following forms:. 'projects/{project_id}/locations/{location}/clusters/{cluster_id}' 'locations/{location}/clusters/{cluster_id}' '{cluster_id}' If project and location are not specified, the project and location of the GameServerCluster resource are used to generate the full name of the GKE cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster GoogleGameServicesGameServerCluster#cluster}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c377babff559548328058c72322a18eacf722f1aaa0b85fe1e2fcd47351ba5c)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
        }

    @builtins.property
    def cluster(self) -> builtins.str:
        '''The full or partial name of a GKE cluster, using one of the following forms:.

        'projects/{project_id}/locations/{location}/clusters/{cluster_id}'
        'locations/{location}/clusters/{cluster_id}'
        '{cluster_id}'

        If project and location are not specified, the project and location of the
        GameServerCluster resource are used to generate the full name of the
        GKE cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster GoogleGameServicesGameServerCluster#cluster}
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReferenceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReferenceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9a0dc56d90e4946715a7cc0b2afce258523d2b400c9e43dbfb9ca0844e7c46c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="clusterInput")
    def cluster_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterInput"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1db1cb1c4285b6ba48ae656d5573a69c2b29ed1f1f0af2de471ec540d55d20d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cluster", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference]:
        return typing.cast(typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6c1a154f2db9fa73d1cc072776169286c5ab2af9051da47849e93e90cf568da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleGameServicesGameServerClusterConnectionInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterConnectionInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fef4e73f69044c784fc2d6d46580ea01ea95ca0b06343f5c9f955e281f71715)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putGkeClusterReference")
    def put_gke_cluster_reference(self, *, cluster: builtins.str) -> None:
        '''
        :param cluster: The full or partial name of a GKE cluster, using one of the following forms:. 'projects/{project_id}/locations/{location}/clusters/{cluster_id}' 'locations/{location}/clusters/{cluster_id}' '{cluster_id}' If project and location are not specified, the project and location of the GameServerCluster resource are used to generate the full name of the GKE cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#cluster GoogleGameServicesGameServerCluster#cluster}
        '''
        value = GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference(
            cluster=cluster
        )

        return typing.cast(None, jsii.invoke(self, "putGkeClusterReference", [value]))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterReference")
    def gke_cluster_reference(
        self,
    ) -> GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReferenceOutputReference:
        return typing.cast(GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReferenceOutputReference, jsii.get(self, "gkeClusterReference"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterReferenceInput")
    def gke_cluster_reference_input(
        self,
    ) -> typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference]:
        return typing.cast(typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference], jsii.get(self, "gkeClusterReferenceInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9704ce0c0963f5ace7f3397d0b852bd673c9543ef572ad7551a86d3c619a853)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleGameServicesGameServerClusterConnectionInfo]:
        return typing.cast(typing.Optional[GoogleGameServicesGameServerClusterConnectionInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleGameServicesGameServerClusterConnectionInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__389e469bb03736f13e9bc498e8e0d874cabdbaaa02b38864328fa8ebe4a74fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleGameServicesGameServerClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#create GoogleGameServicesGameServerCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#delete GoogleGameServicesGameServerCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#update GoogleGameServicesGameServerCluster#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e972f55fe6657e90c058ff4e2c73d825e4756d0c14719ff5da1f080b9305c857)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#create GoogleGameServicesGameServerCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#delete GoogleGameServicesGameServerCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_cluster#update GoogleGameServicesGameServerCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleGameServicesGameServerClusterTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerCluster.GoogleGameServicesGameServerClusterTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__774b6f6cb352178139cf54f8c5117677a3537d0e4e04a5c949d814cbc9bd41b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22fe62da04b6f02c0080fceeeef11bffc984be14ecf246efc3e0d74732ba4560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea7aedadfb1d0a3c7679b027811e96c24d88d1aaf9333da97d0ef40cea0198c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dca70006433509e9c2b8f0765e7c0e010049e7139bea6d9da1926187fea8ed1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5846b2d0ec80eb160d8a9a0edefc6db2132b6f125a5af85033e22bcefb43679)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleGameServicesGameServerCluster",
    "GoogleGameServicesGameServerClusterConfig",
    "GoogleGameServicesGameServerClusterConnectionInfo",
    "GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference",
    "GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReferenceOutputReference",
    "GoogleGameServicesGameServerClusterConnectionInfoOutputReference",
    "GoogleGameServicesGameServerClusterTimeouts",
    "GoogleGameServicesGameServerClusterTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__5eda1ea17ba7ec4cb4fb374c7c78456e2e02732745a79a5739e4a92e893040a3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    connection_info: typing.Union[GoogleGameServicesGameServerClusterConnectionInfo, typing.Dict[builtins.str, typing.Any]],
    realm_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    location: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__f097304b59739de87bbbecef22b722435c08f9708dbd3318af1783703831f4c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__557b36dbcddea48ccc425524656fb8e4974e7641574d210e736fc14c6b79dc6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd211e98101948a61907834fc7748f149959f39b12f8b4a3f7c1a624d2e1b31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__088a08b70f52f61037eb5fafabc5baa186d7557e4308894b39181c8d5fc7b962(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d189dd164eea4ed21460cd5ce96ba9c8beb66ba5a4352e58b907c65f09de99a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3307277c5356733b19ffaaedd7731042033accb7f5e2b08ea5ad71083e1c430(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b1dc77e91d4fbc6032397e3af9aef8acc8af745a18718f39af15af31a60ee17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5dd1603984257b6ef53fc7bcb869550700ec998a898ba8fbfc5f31539114d0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    connection_info: typing.Union[GoogleGameServicesGameServerClusterConnectionInfo, typing.Dict[builtins.str, typing.Any]],
    realm_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    location: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4dbe9e2b81c7eac0018e38f2582df1578885de3e05594bf3b3493ab8b188202(
    *,
    gke_cluster_reference: typing.Union[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference, typing.Dict[builtins.str, typing.Any]],
    namespace: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c377babff559548328058c72322a18eacf722f1aaa0b85fe1e2fcd47351ba5c(
    *,
    cluster: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a0dc56d90e4946715a7cc0b2afce258523d2b400c9e43dbfb9ca0844e7c46c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db1cb1c4285b6ba48ae656d5573a69c2b29ed1f1f0af2de471ec540d55d20d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6c1a154f2db9fa73d1cc072776169286c5ab2af9051da47849e93e90cf568da(
    value: typing.Optional[GoogleGameServicesGameServerClusterConnectionInfoGkeClusterReference],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fef4e73f69044c784fc2d6d46580ea01ea95ca0b06343f5c9f955e281f71715(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9704ce0c0963f5ace7f3397d0b852bd673c9543ef572ad7551a86d3c619a853(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__389e469bb03736f13e9bc498e8e0d874cabdbaaa02b38864328fa8ebe4a74fcb(
    value: typing.Optional[GoogleGameServicesGameServerClusterConnectionInfo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e972f55fe6657e90c058ff4e2c73d825e4756d0c14719ff5da1f080b9305c857(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__774b6f6cb352178139cf54f8c5117677a3537d0e4e04a5c949d814cbc9bd41b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22fe62da04b6f02c0080fceeeef11bffc984be14ecf246efc3e0d74732ba4560(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea7aedadfb1d0a3c7679b027811e96c24d88d1aaf9333da97d0ef40cea0198c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dca70006433509e9c2b8f0765e7c0e010049e7139bea6d9da1926187fea8ed1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5846b2d0ec80eb160d8a9a0edefc6db2132b6f125a5af85033e22bcefb43679(
    value: typing.Optional[typing.Union[GoogleGameServicesGameServerClusterTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
