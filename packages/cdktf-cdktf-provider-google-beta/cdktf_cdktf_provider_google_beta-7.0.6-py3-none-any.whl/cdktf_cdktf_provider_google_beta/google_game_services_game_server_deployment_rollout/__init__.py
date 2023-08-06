'''
# `google_game_services_game_server_deployment_rollout`

Refer to the Terraform Registory for docs: [`google_game_services_game_server_deployment_rollout`](https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout).
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


class GoogleGameServicesGameServerDeploymentRollout(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRollout",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout google_game_services_game_server_deployment_rollout}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        default_game_server_config: builtins.str,
        deployment_id: builtins.str,
        game_server_config_overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleGameServicesGameServerDeploymentRolloutTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout google_game_services_game_server_deployment_rollout} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_game_server_config: This field points to the game server config that is applied by default to all realms and clusters. For example,. 'projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#default_game_server_config GoogleGameServicesGameServerDeploymentRollout#default_game_server_config}
        :param deployment_id: The deployment to rollout the new config to. Only 1 rollout must be associated with each deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#deployment_id GoogleGameServicesGameServerDeploymentRollout#deployment_id}
        :param game_server_config_overrides: game_server_config_overrides block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#game_server_config_overrides GoogleGameServicesGameServerDeploymentRollout#game_server_config_overrides}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#id GoogleGameServicesGameServerDeploymentRollout#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#project GoogleGameServicesGameServerDeploymentRollout#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#timeouts GoogleGameServicesGameServerDeploymentRollout#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c17a788871d15fc7d26186c86ba4d5b4f835e5035bf9ada4f06904a1d9c37456)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleGameServicesGameServerDeploymentRolloutConfig(
            default_game_server_config=default_game_server_config,
            deployment_id=deployment_id,
            game_server_config_overrides=game_server_config_overrides,
            id=id,
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

    @jsii.member(jsii_name="putGameServerConfigOverrides")
    def put_game_server_config_overrides(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec147291ea9c682c7c3af2e835d6e8fd01f1dcbbdfa8c7c3bd5ad93285d76b44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGameServerConfigOverrides", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#create GoogleGameServicesGameServerDeploymentRollout#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#delete GoogleGameServicesGameServerDeploymentRollout#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#update GoogleGameServicesGameServerDeploymentRollout#update}.
        '''
        value = GoogleGameServicesGameServerDeploymentRolloutTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetGameServerConfigOverrides")
    def reset_game_server_config_overrides(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGameServerConfigOverrides", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="gameServerConfigOverrides")
    def game_server_config_overrides(
        self,
    ) -> "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesList":
        return typing.cast("GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesList", jsii.get(self, "gameServerConfigOverrides"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(
        self,
    ) -> "GoogleGameServicesGameServerDeploymentRolloutTimeoutsOutputReference":
        return typing.cast("GoogleGameServicesGameServerDeploymentRolloutTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="defaultGameServerConfigInput")
    def default_game_server_config_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultGameServerConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentIdInput")
    def deployment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="gameServerConfigOverridesInput")
    def game_server_config_overrides_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides"]]], jsii.get(self, "gameServerConfigOverridesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["GoogleGameServicesGameServerDeploymentRolloutTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["GoogleGameServicesGameServerDeploymentRolloutTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultGameServerConfig")
    def default_game_server_config(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultGameServerConfig"))

    @default_game_server_config.setter
    def default_game_server_config(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4da03cb5fe80d9ae15bf3fc411211c1c1eadc01d0d8aa45afa27622645dc1048)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultGameServerConfig", value)

    @builtins.property
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__556081afed7933e85d3f8a9ad1115982753dfd6c383b035caff6eae107ed9bf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7797b1c4aa04af2748cf971d6f932cbb79909c137a9b924acf1b21acb351ee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e24b7d669d5651238b2168ded5f88ed6ac9cd3f391455b60a87d9a07cfa45483)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "default_game_server_config": "defaultGameServerConfig",
        "deployment_id": "deploymentId",
        "game_server_config_overrides": "gameServerConfigOverrides",
        "id": "id",
        "project": "project",
        "timeouts": "timeouts",
    },
)
class GoogleGameServicesGameServerDeploymentRolloutConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        default_game_server_config: builtins.str,
        deployment_id: builtins.str,
        game_server_config_overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleGameServicesGameServerDeploymentRolloutTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param default_game_server_config: This field points to the game server config that is applied by default to all realms and clusters. For example,. 'projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#default_game_server_config GoogleGameServicesGameServerDeploymentRollout#default_game_server_config}
        :param deployment_id: The deployment to rollout the new config to. Only 1 rollout must be associated with each deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#deployment_id GoogleGameServicesGameServerDeploymentRollout#deployment_id}
        :param game_server_config_overrides: game_server_config_overrides block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#game_server_config_overrides GoogleGameServicesGameServerDeploymentRollout#game_server_config_overrides}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#id GoogleGameServicesGameServerDeploymentRollout#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#project GoogleGameServicesGameServerDeploymentRollout#project}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#timeouts GoogleGameServicesGameServerDeploymentRollout#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = GoogleGameServicesGameServerDeploymentRolloutTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4b9631f70e174f2e440436c0c0966bc89e280446be159f9ca236da93cc132e3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument default_game_server_config", value=default_game_server_config, expected_type=type_hints["default_game_server_config"])
            check_type(argname="argument deployment_id", value=deployment_id, expected_type=type_hints["deployment_id"])
            check_type(argname="argument game_server_config_overrides", value=game_server_config_overrides, expected_type=type_hints["game_server_config_overrides"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "default_game_server_config": default_game_server_config,
            "deployment_id": deployment_id,
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
        if game_server_config_overrides is not None:
            self._values["game_server_config_overrides"] = game_server_config_overrides
        if id is not None:
            self._values["id"] = id
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
    def default_game_server_config(self) -> builtins.str:
        '''This field points to the game server config that is applied by default to all realms and clusters. For example,.

        'projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#default_game_server_config GoogleGameServicesGameServerDeploymentRollout#default_game_server_config}
        '''
        result = self._values.get("default_game_server_config")
        assert result is not None, "Required property 'default_game_server_config' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deployment_id(self) -> builtins.str:
        '''The deployment to rollout the new config to. Only 1 rollout must be associated with each deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#deployment_id GoogleGameServicesGameServerDeploymentRollout#deployment_id}
        '''
        result = self._values.get("deployment_id")
        assert result is not None, "Required property 'deployment_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def game_server_config_overrides(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides"]]]:
        '''game_server_config_overrides block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#game_server_config_overrides GoogleGameServicesGameServerDeploymentRollout#game_server_config_overrides}
        '''
        result = self._values.get("game_server_config_overrides")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#id GoogleGameServicesGameServerDeploymentRollout#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#project GoogleGameServicesGameServerDeploymentRollout#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(
        self,
    ) -> typing.Optional["GoogleGameServicesGameServerDeploymentRolloutTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#timeouts GoogleGameServicesGameServerDeploymentRollout#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleGameServicesGameServerDeploymentRolloutTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerDeploymentRolloutConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides",
    jsii_struct_bases=[],
    name_mapping={
        "config_version": "configVersion",
        "realms_selector": "realmsSelector",
    },
)
class GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides:
    def __init__(
        self,
        *,
        config_version: typing.Optional[builtins.str] = None,
        realms_selector: typing.Optional[typing.Union["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param config_version: Version of the configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#config_version GoogleGameServicesGameServerDeploymentRollout#config_version}
        :param realms_selector: realms_selector block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#realms_selector GoogleGameServicesGameServerDeploymentRollout#realms_selector}
        '''
        if isinstance(realms_selector, dict):
            realms_selector = GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector(**realms_selector)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0712fd731ebdca9513dd9aedf646c8555cd7fcddc7b6c608e508ccf4667ec9c4)
            check_type(argname="argument config_version", value=config_version, expected_type=type_hints["config_version"])
            check_type(argname="argument realms_selector", value=realms_selector, expected_type=type_hints["realms_selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_version is not None:
            self._values["config_version"] = config_version
        if realms_selector is not None:
            self._values["realms_selector"] = realms_selector

    @builtins.property
    def config_version(self) -> typing.Optional[builtins.str]:
        '''Version of the configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#config_version GoogleGameServicesGameServerDeploymentRollout#config_version}
        '''
        result = self._values.get("config_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def realms_selector(
        self,
    ) -> typing.Optional["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector"]:
        '''realms_selector block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#realms_selector GoogleGameServicesGameServerDeploymentRollout#realms_selector}
        '''
        result = self._values.get("realms_selector")
        return typing.cast(typing.Optional["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db2683adcad5f7c4ab8ff393fd0018e13d52e9039871c6a56ff30e251c8bcec4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d516f82494637fd4654696de40d9a38d17f5350de5f0960033f649c2cb46701b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24b7b7a0549e13ae67627a606cd496ffb149bb8f1882f0839f2e3392a1cf4dfb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__312e49ddbca57be53320ba2aea9e9341cb95d0a3e576a7641173a60909a08cc1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a58ca5067665ae96069c53304946405f4d998138ea0b2b0696d9e25e18111ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44a55cf9e5be5ed1a075e00d0b398dde25124359ea03902000b88668c681c845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5dfe3dffd3b92e6dc550d2b082e2c3906ede7e9d5615e13a612959721e24e989)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRealmsSelector")
    def put_realms_selector(
        self,
        *,
        realms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param realms: List of realms to match against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#realms GoogleGameServicesGameServerDeploymentRollout#realms}
        '''
        value = GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector(
            realms=realms
        )

        return typing.cast(None, jsii.invoke(self, "putRealmsSelector", [value]))

    @jsii.member(jsii_name="resetConfigVersion")
    def reset_config_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigVersion", []))

    @jsii.member(jsii_name="resetRealmsSelector")
    def reset_realms_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRealmsSelector", []))

    @builtins.property
    @jsii.member(jsii_name="realmsSelector")
    def realms_selector(
        self,
    ) -> "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelectorOutputReference":
        return typing.cast("GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelectorOutputReference", jsii.get(self, "realmsSelector"))

    @builtins.property
    @jsii.member(jsii_name="configVersionInput")
    def config_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="realmsSelectorInput")
    def realms_selector_input(
        self,
    ) -> typing.Optional["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector"]:
        return typing.cast(typing.Optional["GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector"], jsii.get(self, "realmsSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="configVersion")
    def config_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configVersion"))

    @config_version.setter
    def config_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c33470505d0870f276d1499c9748bbdda85bae40f647509378c5bcae4ccbba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configVersion", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b0ffac6f9e71f6d29130c1ab22e7b071b70e3725453dd30ce7ec59a4ba7c6df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector",
    jsii_struct_bases=[],
    name_mapping={"realms": "realms"},
)
class GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector:
    def __init__(
        self,
        *,
        realms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param realms: List of realms to match against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#realms GoogleGameServicesGameServerDeploymentRollout#realms}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c841f0b6ee9dc33e900db201e8ae9507ec9c470bc07c363603393b063f4933)
            check_type(argname="argument realms", value=realms, expected_type=type_hints["realms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if realms is not None:
            self._values["realms"] = realms

    @builtins.property
    def realms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of realms to match against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#realms GoogleGameServicesGameServerDeploymentRollout#realms}
        '''
        result = self._values.get("realms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelectorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelectorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0a74942ffa89ad99a5c3cf943ee39752016c3b4eac9bf7c85801ec01a357644)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRealms")
    def reset_realms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRealms", []))

    @builtins.property
    @jsii.member(jsii_name="realmsInput")
    def realms_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "realmsInput"))

    @builtins.property
    @jsii.member(jsii_name="realms")
    def realms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "realms"))

    @realms.setter
    def realms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__379ba14335014fabfdefdfc1e566b3b6e3b0c57a5c29333cf90d4e10453cc431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realms", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector]:
        return typing.cast(typing.Optional[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f186eed28c2a0725f0c151b1ab463406eccccf81668d1fff10f52e910f3d088d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleGameServicesGameServerDeploymentRolloutTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#create GoogleGameServicesGameServerDeploymentRollout#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#delete GoogleGameServicesGameServerDeploymentRollout#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#update GoogleGameServicesGameServerDeploymentRollout#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5a39680a7b276471c74b4357fcfe99572d62e6aff45c79256754dfd106e47ec)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#create GoogleGameServicesGameServerDeploymentRollout#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#delete GoogleGameServicesGameServerDeploymentRollout#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_game_services_game_server_deployment_rollout#update GoogleGameServicesGameServerDeploymentRollout#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleGameServicesGameServerDeploymentRolloutTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleGameServicesGameServerDeploymentRolloutTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleGameServicesGameServerDeploymentRollout.GoogleGameServicesGameServerDeploymentRolloutTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cddee96fc7f545753ab2efbcf0d190f1f28b0528cbe44255ddb1d60f7f10c8e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cec0a46ef56166279dda889fd5cc5af8e07c6520e02b5475f32707333c7dd850)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f001f752616add9ddb0211abb5b3290dd2112d5b240864080226f9b73fb7e116)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca2b8758c9d4e02e81ca114cd0d38bedc06d6be63c9ccf2db7b88b12254ee6ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1723b6c01d6db0247c4160804c79ba6ff118ea04e11e46f8f9a3ad73b5ef4f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleGameServicesGameServerDeploymentRollout",
    "GoogleGameServicesGameServerDeploymentRolloutConfig",
    "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides",
    "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesList",
    "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesOutputReference",
    "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector",
    "GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelectorOutputReference",
    "GoogleGameServicesGameServerDeploymentRolloutTimeouts",
    "GoogleGameServicesGameServerDeploymentRolloutTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__c17a788871d15fc7d26186c86ba4d5b4f835e5035bf9ada4f06904a1d9c37456(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    default_game_server_config: builtins.str,
    deployment_id: builtins.str,
    game_server_config_overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__ec147291ea9c682c7c3af2e835d6e8fd01f1dcbbdfa8c7c3bd5ad93285d76b44(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4da03cb5fe80d9ae15bf3fc411211c1c1eadc01d0d8aa45afa27622645dc1048(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__556081afed7933e85d3f8a9ad1115982753dfd6c383b035caff6eae107ed9bf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7797b1c4aa04af2748cf971d6f932cbb79909c137a9b924acf1b21acb351ee9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e24b7d669d5651238b2168ded5f88ed6ac9cd3f391455b60a87d9a07cfa45483(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b9631f70e174f2e440436c0c0966bc89e280446be159f9ca236da93cc132e3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    default_game_server_config: builtins.str,
    deployment_id: builtins.str,
    game_server_config_overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0712fd731ebdca9513dd9aedf646c8555cd7fcddc7b6c608e508ccf4667ec9c4(
    *,
    config_version: typing.Optional[builtins.str] = None,
    realms_selector: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db2683adcad5f7c4ab8ff393fd0018e13d52e9039871c6a56ff30e251c8bcec4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d516f82494637fd4654696de40d9a38d17f5350de5f0960033f649c2cb46701b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24b7b7a0549e13ae67627a606cd496ffb149bb8f1882f0839f2e3392a1cf4dfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312e49ddbca57be53320ba2aea9e9341cb95d0a3e576a7641173a60909a08cc1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a58ca5067665ae96069c53304946405f4d998138ea0b2b0696d9e25e18111ba(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44a55cf9e5be5ed1a075e00d0b398dde25124359ea03902000b88668c681c845(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dfe3dffd3b92e6dc550d2b082e2c3906ede7e9d5615e13a612959721e24e989(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c33470505d0870f276d1499c9748bbdda85bae40f647509378c5bcae4ccbba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b0ffac6f9e71f6d29130c1ab22e7b071b70e3725453dd30ce7ec59a4ba7c6df(
    value: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverrides, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c841f0b6ee9dc33e900db201e8ae9507ec9c470bc07c363603393b063f4933(
    *,
    realms: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a74942ffa89ad99a5c3cf943ee39752016c3b4eac9bf7c85801ec01a357644(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__379ba14335014fabfdefdfc1e566b3b6e3b0c57a5c29333cf90d4e10453cc431(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f186eed28c2a0725f0c151b1ab463406eccccf81668d1fff10f52e910f3d088d(
    value: typing.Optional[GoogleGameServicesGameServerDeploymentRolloutGameServerConfigOverridesRealmsSelector],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5a39680a7b276471c74b4357fcfe99572d62e6aff45c79256754dfd106e47ec(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cddee96fc7f545753ab2efbcf0d190f1f28b0528cbe44255ddb1d60f7f10c8e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cec0a46ef56166279dda889fd5cc5af8e07c6520e02b5475f32707333c7dd850(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f001f752616add9ddb0211abb5b3290dd2112d5b240864080226f9b73fb7e116(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca2b8758c9d4e02e81ca114cd0d38bedc06d6be63c9ccf2db7b88b12254ee6ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1723b6c01d6db0247c4160804c79ba6ff118ea04e11e46f8f9a3ad73b5ef4f4(
    value: typing.Optional[typing.Union[GoogleGameServicesGameServerDeploymentRolloutTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
