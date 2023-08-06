'''
# `google_artifact_registry_repository`

Refer to the Terraform Registory for docs: [`google_artifact_registry_repository`](https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository).
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


class GoogleArtifactRegistryRepository(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepository",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository google_artifact_registry_repository}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        format: builtins.str,
        repository_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        docker_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryDockerConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        kms_key_name: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        location: typing.Optional[builtins.str] = None,
        maven_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryMavenConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        mode: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        remote_repository_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        virtual_repository_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository google_artifact_registry_repository} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param format: The format of packages that are stored in the repository. Supported formats can be found `here <https://cloud.google.com/artifact-registry/docs/supported-formats>`_. You can only create alpha formats if you are a member of the `alpha user group <https://cloud.google.com/artifact-registry/docs/supported-formats#alpha-access>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#format GoogleArtifactRegistryRepository#format}
        :param repository_id: The last part of the repository name, for example: "repo1". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#repository_id GoogleArtifactRegistryRepository#repository_id}
        :param description: The user-provided description of the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        :param docker_config: docker_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_config GoogleArtifactRegistryRepository#docker_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#id GoogleArtifactRegistryRepository#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kms_key_name: The Cloud KMS resource name of the customer managed encryption key that’s used to encrypt the contents of the Repository. Has the form: 'projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key'. This value may not be changed after the Repository has been created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#kms_key_name GoogleArtifactRegistryRepository#kms_key_name}
        :param labels: Labels with user-defined metadata. This field may contain up to 64 entries. Label keys and values may be no longer than 63 characters. Label keys must begin with a lowercase letter and may only contain lowercase letters, numeric characters, underscores, and dashes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#labels GoogleArtifactRegistryRepository#labels}
        :param location: The name of the location this repository is located in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#location GoogleArtifactRegistryRepository#location}
        :param maven_config: maven_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_config GoogleArtifactRegistryRepository#maven_config}
        :param mode: The mode configures the repository to serve artifacts from different sources. Default value: "STANDARD_REPOSITORY" Possible values: ["STANDARD_REPOSITORY", "VIRTUAL_REPOSITORY", "REMOTE_REPOSITORY"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#mode GoogleArtifactRegistryRepository#mode}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#project GoogleArtifactRegistryRepository#project}.
        :param remote_repository_config: remote_repository_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#remote_repository_config GoogleArtifactRegistryRepository#remote_repository_config}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#timeouts GoogleArtifactRegistryRepository#timeouts}
        :param virtual_repository_config: virtual_repository_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#virtual_repository_config GoogleArtifactRegistryRepository#virtual_repository_config}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a11e2122d6664017242aeafd4c93d9fa52129b0712698eca09688c82b13de3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleArtifactRegistryRepositoryConfig(
            format=format,
            repository_id=repository_id,
            description=description,
            docker_config=docker_config,
            id=id,
            kms_key_name=kms_key_name,
            labels=labels,
            location=location,
            maven_config=maven_config,
            mode=mode,
            project=project,
            remote_repository_config=remote_repository_config,
            timeouts=timeouts,
            virtual_repository_config=virtual_repository_config,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putDockerConfig")
    def put_docker_config(
        self,
        *,
        immutable_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param immutable_tags: The repository which enabled this flag prevents all tags from being modified, moved or deleted. This does not prevent tags from being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#immutable_tags GoogleArtifactRegistryRepository#immutable_tags}
        '''
        value = GoogleArtifactRegistryRepositoryDockerConfig(
            immutable_tags=immutable_tags
        )

        return typing.cast(None, jsii.invoke(self, "putDockerConfig", [value]))

    @jsii.member(jsii_name="putMavenConfig")
    def put_maven_config(
        self,
        *,
        allow_snapshot_overwrites: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_snapshot_overwrites: The repository with this flag will allow publishing the same snapshot versions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#allow_snapshot_overwrites GoogleArtifactRegistryRepository#allow_snapshot_overwrites}
        :param version_policy: Version policy defines the versions that the registry will accept. Default value: "VERSION_POLICY_UNSPECIFIED" Possible values: ["VERSION_POLICY_UNSPECIFIED", "RELEASE", "SNAPSHOT"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#version_policy GoogleArtifactRegistryRepository#version_policy}
        '''
        value = GoogleArtifactRegistryRepositoryMavenConfig(
            allow_snapshot_overwrites=allow_snapshot_overwrites,
            version_policy=version_policy,
        )

        return typing.cast(None, jsii.invoke(self, "putMavenConfig", [value]))

    @jsii.member(jsii_name="putRemoteRepositoryConfig")
    def put_remote_repository_config(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        docker_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        maven_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        npm_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        python_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param description: The description of the remote source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        :param docker_repository: docker_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_repository GoogleArtifactRegistryRepository#docker_repository}
        :param maven_repository: maven_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_repository GoogleArtifactRegistryRepository#maven_repository}
        :param npm_repository: npm_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#npm_repository GoogleArtifactRegistryRepository#npm_repository}
        :param python_repository: python_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#python_repository GoogleArtifactRegistryRepository#python_repository}
        '''
        value = GoogleArtifactRegistryRepositoryRemoteRepositoryConfig(
            description=description,
            docker_repository=docker_repository,
            maven_repository=maven_repository,
            npm_repository=npm_repository,
            python_repository=python_repository,
        )

        return typing.cast(None, jsii.invoke(self, "putRemoteRepositoryConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#create GoogleArtifactRegistryRepository#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#delete GoogleArtifactRegistryRepository#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#update GoogleArtifactRegistryRepository#update}.
        '''
        value = GoogleArtifactRegistryRepositoryTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putVirtualRepositoryConfig")
    def put_virtual_repository_config(
        self,
        *,
        upstream_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param upstream_policies: upstream_policies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#upstream_policies GoogleArtifactRegistryRepository#upstream_policies}
        '''
        value = GoogleArtifactRegistryRepositoryVirtualRepositoryConfig(
            upstream_policies=upstream_policies
        )

        return typing.cast(None, jsii.invoke(self, "putVirtualRepositoryConfig", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDockerConfig")
    def reset_docker_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKmsKeyName")
    def reset_kms_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyName", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @jsii.member(jsii_name="resetMavenConfig")
    def reset_maven_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMavenConfig", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetProject")
    def reset_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProject", []))

    @jsii.member(jsii_name="resetRemoteRepositoryConfig")
    def reset_remote_repository_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteRepositoryConfig", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVirtualRepositoryConfig")
    def reset_virtual_repository_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualRepositoryConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property
    @jsii.member(jsii_name="dockerConfig")
    def docker_config(
        self,
    ) -> "GoogleArtifactRegistryRepositoryDockerConfigOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryDockerConfigOutputReference", jsii.get(self, "dockerConfig"))

    @builtins.property
    @jsii.member(jsii_name="mavenConfig")
    def maven_config(
        self,
    ) -> "GoogleArtifactRegistryRepositoryMavenConfigOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryMavenConfigOutputReference", jsii.get(self, "mavenConfig"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="remoteRepositoryConfig")
    def remote_repository_config(
        self,
    ) -> "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryRemoteRepositoryConfigOutputReference", jsii.get(self, "remoteRepositoryConfig"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleArtifactRegistryRepositoryTimeoutsOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="updateTime")
    def update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateTime"))

    @builtins.property
    @jsii.member(jsii_name="virtualRepositoryConfig")
    def virtual_repository_config(
        self,
    ) -> "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryVirtualRepositoryConfigOutputReference", jsii.get(self, "virtualRepositoryConfig"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="dockerConfigInput")
    def docker_config_input(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryDockerConfig"]:
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryDockerConfig"], jsii.get(self, "dockerConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyNameInput")
    def kms_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyNameInput"))

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
    @jsii.member(jsii_name="mavenConfigInput")
    def maven_config_input(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryMavenConfig"]:
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryMavenConfig"], jsii.get(self, "mavenConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteRepositoryConfigInput")
    def remote_repository_config_input(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig"]:
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig"], jsii.get(self, "remoteRepositoryConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryIdInput")
    def repository_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualRepositoryConfigInput")
    def virtual_repository_config_input(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig"]:
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig"], jsii.get(self, "virtualRepositoryConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a884f9ba44c40a4418e193fc168692418b837dc57d71f179490ba11b5fa40d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1acfe2b5cf2b91d73928a9e731c2cfd069bbac29dcbc52da978ca527d69737d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b587ab17be38890794c093824080b4e454003e1198e375724cdfc3178057854)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="kmsKeyName")
    def kms_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyName"))

    @kms_key_name.setter
    def kms_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec0ed70e3829cbc8930c8fbc32c7fbbafecab184eda9d737a892486619fadcad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__535062de7b2c2b2db5c98c29f5e9ac5025367fbe810e81c83ad59ef15835eaa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87602acbfc2bd41a8fb9eff6b22fb5c6b2ab9113e61fcbc5705497bd380eb496)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb2ba84f604e1ab673edb088edec27614d9b6b6e5aef7daa40830753dbb93af3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value)

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5a0e374397384da479f77b5ea8afb599619865d041cba21a07f3b4eec030e5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value)

    @builtins.property
    @jsii.member(jsii_name="repositoryId")
    def repository_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryId"))

    @repository_id.setter
    def repository_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__755a1bd588113c26c00d7dd30beaceb0cb1af32b57a2fc7059cfce92eb73a939)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "format": "format",
        "repository_id": "repositoryId",
        "description": "description",
        "docker_config": "dockerConfig",
        "id": "id",
        "kms_key_name": "kmsKeyName",
        "labels": "labels",
        "location": "location",
        "maven_config": "mavenConfig",
        "mode": "mode",
        "project": "project",
        "remote_repository_config": "remoteRepositoryConfig",
        "timeouts": "timeouts",
        "virtual_repository_config": "virtualRepositoryConfig",
    },
)
class GoogleArtifactRegistryRepositoryConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        format: builtins.str,
        repository_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        docker_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryDockerConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        kms_key_name: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        location: typing.Optional[builtins.str] = None,
        maven_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryMavenConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        mode: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        remote_repository_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        virtual_repository_config: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param format: The format of packages that are stored in the repository. Supported formats can be found `here <https://cloud.google.com/artifact-registry/docs/supported-formats>`_. You can only create alpha formats if you are a member of the `alpha user group <https://cloud.google.com/artifact-registry/docs/supported-formats#alpha-access>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#format GoogleArtifactRegistryRepository#format}
        :param repository_id: The last part of the repository name, for example: "repo1". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#repository_id GoogleArtifactRegistryRepository#repository_id}
        :param description: The user-provided description of the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        :param docker_config: docker_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_config GoogleArtifactRegistryRepository#docker_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#id GoogleArtifactRegistryRepository#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kms_key_name: The Cloud KMS resource name of the customer managed encryption key that’s used to encrypt the contents of the Repository. Has the form: 'projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key'. This value may not be changed after the Repository has been created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#kms_key_name GoogleArtifactRegistryRepository#kms_key_name}
        :param labels: Labels with user-defined metadata. This field may contain up to 64 entries. Label keys and values may be no longer than 63 characters. Label keys must begin with a lowercase letter and may only contain lowercase letters, numeric characters, underscores, and dashes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#labels GoogleArtifactRegistryRepository#labels}
        :param location: The name of the location this repository is located in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#location GoogleArtifactRegistryRepository#location}
        :param maven_config: maven_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_config GoogleArtifactRegistryRepository#maven_config}
        :param mode: The mode configures the repository to serve artifacts from different sources. Default value: "STANDARD_REPOSITORY" Possible values: ["STANDARD_REPOSITORY", "VIRTUAL_REPOSITORY", "REMOTE_REPOSITORY"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#mode GoogleArtifactRegistryRepository#mode}
        :param project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#project GoogleArtifactRegistryRepository#project}.
        :param remote_repository_config: remote_repository_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#remote_repository_config GoogleArtifactRegistryRepository#remote_repository_config}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#timeouts GoogleArtifactRegistryRepository#timeouts}
        :param virtual_repository_config: virtual_repository_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#virtual_repository_config GoogleArtifactRegistryRepository#virtual_repository_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(docker_config, dict):
            docker_config = GoogleArtifactRegistryRepositoryDockerConfig(**docker_config)
        if isinstance(maven_config, dict):
            maven_config = GoogleArtifactRegistryRepositoryMavenConfig(**maven_config)
        if isinstance(remote_repository_config, dict):
            remote_repository_config = GoogleArtifactRegistryRepositoryRemoteRepositoryConfig(**remote_repository_config)
        if isinstance(timeouts, dict):
            timeouts = GoogleArtifactRegistryRepositoryTimeouts(**timeouts)
        if isinstance(virtual_repository_config, dict):
            virtual_repository_config = GoogleArtifactRegistryRepositoryVirtualRepositoryConfig(**virtual_repository_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5088d0d29bb6061ed8033079146f76ffd8db624253986f4fa50416e123b6414)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument repository_id", value=repository_id, expected_type=type_hints["repository_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument docker_config", value=docker_config, expected_type=type_hints["docker_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kms_key_name", value=kms_key_name, expected_type=type_hints["kms_key_name"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument maven_config", value=maven_config, expected_type=type_hints["maven_config"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument remote_repository_config", value=remote_repository_config, expected_type=type_hints["remote_repository_config"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument virtual_repository_config", value=virtual_repository_config, expected_type=type_hints["virtual_repository_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "format": format,
            "repository_id": repository_id,
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
        if docker_config is not None:
            self._values["docker_config"] = docker_config
        if id is not None:
            self._values["id"] = id
        if kms_key_name is not None:
            self._values["kms_key_name"] = kms_key_name
        if labels is not None:
            self._values["labels"] = labels
        if location is not None:
            self._values["location"] = location
        if maven_config is not None:
            self._values["maven_config"] = maven_config
        if mode is not None:
            self._values["mode"] = mode
        if project is not None:
            self._values["project"] = project
        if remote_repository_config is not None:
            self._values["remote_repository_config"] = remote_repository_config
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if virtual_repository_config is not None:
            self._values["virtual_repository_config"] = virtual_repository_config

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
    def format(self) -> builtins.str:
        '''The format of packages that are stored in the repository.

        Supported formats
        can be found `here <https://cloud.google.com/artifact-registry/docs/supported-formats>`_.
        You can only create alpha formats if you are a member of the
        `alpha user group <https://cloud.google.com/artifact-registry/docs/supported-formats#alpha-access>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#format GoogleArtifactRegistryRepository#format}
        '''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_id(self) -> builtins.str:
        '''The last part of the repository name, for example: "repo1".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#repository_id GoogleArtifactRegistryRepository#repository_id}
        '''
        result = self._values.get("repository_id")
        assert result is not None, "Required property 'repository_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The user-provided description of the repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_config(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryDockerConfig"]:
        '''docker_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_config GoogleArtifactRegistryRepository#docker_config}
        '''
        result = self._values.get("docker_config")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryDockerConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#id GoogleArtifactRegistryRepository#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_name(self) -> typing.Optional[builtins.str]:
        '''The Cloud KMS resource name of the customer managed encryption key that’s used to encrypt the contents of the Repository.

        Has the form:
        'projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key'.
        This value may not be changed after the Repository has been created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#kms_key_name GoogleArtifactRegistryRepository#kms_key_name}
        '''
        result = self._values.get("kms_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Labels with user-defined metadata.

        This field may contain up to 64 entries. Label keys and values may be no
        longer than 63 characters. Label keys must begin with a lowercase letter
        and may only contain lowercase letters, numeric characters, underscores,
        and dashes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#labels GoogleArtifactRegistryRepository#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''The name of the location this repository is located in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#location GoogleArtifactRegistryRepository#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_config(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryMavenConfig"]:
        '''maven_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_config GoogleArtifactRegistryRepository#maven_config}
        '''
        result = self._values.get("maven_config")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryMavenConfig"], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The mode configures the repository to serve artifacts from different sources. Default value: "STANDARD_REPOSITORY" Possible values: ["STANDARD_REPOSITORY", "VIRTUAL_REPOSITORY", "REMOTE_REPOSITORY"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#mode GoogleArtifactRegistryRepository#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#project GoogleArtifactRegistryRepository#project}.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_repository_config(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig"]:
        '''remote_repository_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#remote_repository_config GoogleArtifactRegistryRepository#remote_repository_config}
        '''
        result = self._values.get("remote_repository_config")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfig"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleArtifactRegistryRepositoryTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#timeouts GoogleArtifactRegistryRepository#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryTimeouts"], result)

    @builtins.property
    def virtual_repository_config(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig"]:
        '''virtual_repository_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#virtual_repository_config GoogleArtifactRegistryRepository#virtual_repository_config}
        '''
        result = self._values.get("virtual_repository_config")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryVirtualRepositoryConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryDockerConfig",
    jsii_struct_bases=[],
    name_mapping={"immutable_tags": "immutableTags"},
)
class GoogleArtifactRegistryRepositoryDockerConfig:
    def __init__(
        self,
        *,
        immutable_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param immutable_tags: The repository which enabled this flag prevents all tags from being modified, moved or deleted. This does not prevent tags from being created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#immutable_tags GoogleArtifactRegistryRepository#immutable_tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77f5546da03f0a36d2ba2086fd28a4f0bedd4adcb91d34687fd23ec31d9340c6)
            check_type(argname="argument immutable_tags", value=immutable_tags, expected_type=type_hints["immutable_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if immutable_tags is not None:
            self._values["immutable_tags"] = immutable_tags

    @builtins.property
    def immutable_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The repository which enabled this flag prevents all tags from being modified, moved or deleted.

        This does not prevent tags from being created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#immutable_tags GoogleArtifactRegistryRepository#immutable_tags}
        '''
        result = self._values.get("immutable_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryDockerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryDockerConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryDockerConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ebae7feb9192fe8276f41f9914268b82fa1ad588fb88562d165287aaa8c24fc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetImmutableTags")
    def reset_immutable_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImmutableTags", []))

    @builtins.property
    @jsii.member(jsii_name="immutableTagsInput")
    def immutable_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "immutableTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="immutableTags")
    def immutable_tags(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "immutableTags"))

    @immutable_tags.setter
    def immutable_tags(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de4b4341d3cbb36cdaba4fd0cc3b01937bbe2e5f10051bdcbffbe09f4ec7b57d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "immutableTags", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryDockerConfig]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryDockerConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryDockerConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__278ef6879dfe25305d05e7f7de36e073f7669109bf4f13ece6d479c470068aa2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryMavenConfig",
    jsii_struct_bases=[],
    name_mapping={
        "allow_snapshot_overwrites": "allowSnapshotOverwrites",
        "version_policy": "versionPolicy",
    },
)
class GoogleArtifactRegistryRepositoryMavenConfig:
    def __init__(
        self,
        *,
        allow_snapshot_overwrites: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        version_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_snapshot_overwrites: The repository with this flag will allow publishing the same snapshot versions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#allow_snapshot_overwrites GoogleArtifactRegistryRepository#allow_snapshot_overwrites}
        :param version_policy: Version policy defines the versions that the registry will accept. Default value: "VERSION_POLICY_UNSPECIFIED" Possible values: ["VERSION_POLICY_UNSPECIFIED", "RELEASE", "SNAPSHOT"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#version_policy GoogleArtifactRegistryRepository#version_policy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b86106113cd2326dfa091d75b12f264666750a8e018f6f9dd440d5671916a28f)
            check_type(argname="argument allow_snapshot_overwrites", value=allow_snapshot_overwrites, expected_type=type_hints["allow_snapshot_overwrites"])
            check_type(argname="argument version_policy", value=version_policy, expected_type=type_hints["version_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_snapshot_overwrites is not None:
            self._values["allow_snapshot_overwrites"] = allow_snapshot_overwrites
        if version_policy is not None:
            self._values["version_policy"] = version_policy

    @builtins.property
    def allow_snapshot_overwrites(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The repository with this flag will allow publishing the same snapshot versions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#allow_snapshot_overwrites GoogleArtifactRegistryRepository#allow_snapshot_overwrites}
        '''
        result = self._values.get("allow_snapshot_overwrites")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def version_policy(self) -> typing.Optional[builtins.str]:
        '''Version policy defines the versions that the registry will accept. Default value: "VERSION_POLICY_UNSPECIFIED" Possible values: ["VERSION_POLICY_UNSPECIFIED", "RELEASE", "SNAPSHOT"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#version_policy GoogleArtifactRegistryRepository#version_policy}
        '''
        result = self._values.get("version_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryMavenConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryMavenConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryMavenConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbf716c7ee8f7e3708ae13c4a5ed91553e2752a5a2dc59bcabdb0955a5350231)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowSnapshotOverwrites")
    def reset_allow_snapshot_overwrites(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSnapshotOverwrites", []))

    @jsii.member(jsii_name="resetVersionPolicy")
    def reset_version_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionPolicy", []))

    @builtins.property
    @jsii.member(jsii_name="allowSnapshotOverwritesInput")
    def allow_snapshot_overwrites_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowSnapshotOverwritesInput"))

    @builtins.property
    @jsii.member(jsii_name="versionPolicyInput")
    def version_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="allowSnapshotOverwrites")
    def allow_snapshot_overwrites(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowSnapshotOverwrites"))

    @allow_snapshot_overwrites.setter
    def allow_snapshot_overwrites(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b444a1b5f285427c2eab3b45eaf064e7331ea489897b86ae9d7be87d33b10a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowSnapshotOverwrites", value)

    @builtins.property
    @jsii.member(jsii_name="versionPolicy")
    def version_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionPolicy"))

    @version_policy.setter
    def version_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1b51472012f31563968da9a4298b224009dce64b3e481bb595e29aaed363681)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionPolicy", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryMavenConfig]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryMavenConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryMavenConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55ec6ac288c11e20f2f29ea7e5ac0c01034509432a7fd1eb1d38a1c98a11c6cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfig",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "docker_repository": "dockerRepository",
        "maven_repository": "mavenRepository",
        "npm_repository": "npmRepository",
        "python_repository": "pythonRepository",
    },
)
class GoogleArtifactRegistryRepositoryRemoteRepositoryConfig:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        docker_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        maven_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        npm_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository", typing.Dict[builtins.str, typing.Any]]] = None,
        python_repository: typing.Optional[typing.Union["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param description: The description of the remote source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        :param docker_repository: docker_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_repository GoogleArtifactRegistryRepository#docker_repository}
        :param maven_repository: maven_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_repository GoogleArtifactRegistryRepository#maven_repository}
        :param npm_repository: npm_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#npm_repository GoogleArtifactRegistryRepository#npm_repository}
        :param python_repository: python_repository block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#python_repository GoogleArtifactRegistryRepository#python_repository}
        '''
        if isinstance(docker_repository, dict):
            docker_repository = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository(**docker_repository)
        if isinstance(maven_repository, dict):
            maven_repository = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository(**maven_repository)
        if isinstance(npm_repository, dict):
            npm_repository = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository(**npm_repository)
        if isinstance(python_repository, dict):
            python_repository = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository(**python_repository)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3124b5f04fe207fe7b9f7e70d5948dd0cc5b9ac58ea072a6c9b8ad38fa12ec7)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument docker_repository", value=docker_repository, expected_type=type_hints["docker_repository"])
            check_type(argname="argument maven_repository", value=maven_repository, expected_type=type_hints["maven_repository"])
            check_type(argname="argument npm_repository", value=npm_repository, expected_type=type_hints["npm_repository"])
            check_type(argname="argument python_repository", value=python_repository, expected_type=type_hints["python_repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if docker_repository is not None:
            self._values["docker_repository"] = docker_repository
        if maven_repository is not None:
            self._values["maven_repository"] = maven_repository
        if npm_repository is not None:
            self._values["npm_repository"] = npm_repository
        if python_repository is not None:
            self._values["python_repository"] = python_repository

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the remote source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#description GoogleArtifactRegistryRepository#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_repository(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository"]:
        '''docker_repository block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#docker_repository GoogleArtifactRegistryRepository#docker_repository}
        '''
        result = self._values.get("docker_repository")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository"], result)

    @builtins.property
    def maven_repository(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository"]:
        '''maven_repository block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#maven_repository GoogleArtifactRegistryRepository#maven_repository}
        '''
        result = self._values.get("maven_repository")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository"], result)

    @builtins.property
    def npm_repository(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository"]:
        '''npm_repository block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#npm_repository GoogleArtifactRegistryRepository#npm_repository}
        '''
        result = self._values.get("npm_repository")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository"], result)

    @builtins.property
    def python_repository(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository"]:
        '''python_repository block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#python_repository GoogleArtifactRegistryRepository#python_repository}
        '''
        result = self._values.get("python_repository")
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryRemoteRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository",
    jsii_struct_bases=[],
    name_mapping={"public_repository": "publicRepository"},
)
class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository:
    def __init__(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "DOCKER_HUB" Possible values: ["DOCKER_HUB"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fe2c5a77bb1705dcdf629eeb965b6991604a2b6f152a4c0c81a4ac531d86c63)
            check_type(argname="argument public_repository", value=public_repository, expected_type=type_hints["public_repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if public_repository is not None:
            self._values["public_repository"] = public_repository

    @builtins.property
    def public_repository(self) -> typing.Optional[builtins.str]:
        '''Address of the remote repository. Default value: "DOCKER_HUB" Possible values: ["DOCKER_HUB"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        result = self._values.get("public_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepositoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepositoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__040cbeb20e8cafcadf2397a94e2cd6b4428dcc5af0ba3f7eb8d0c27b1078e8d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPublicRepository")
    def reset_public_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicRepository", []))

    @builtins.property
    @jsii.member(jsii_name="publicRepositoryInput")
    def public_repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="publicRepository")
    def public_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicRepository"))

    @public_repository.setter
    def public_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66d2feabb5f4c368b27b272540662a1a9503442d86b2461a00d56e4ec2c9d8a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicRepository", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6583a2160ab7438cb3c884ba152391468a61b2e6724b19345ee684f8c205cea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository",
    jsii_struct_bases=[],
    name_mapping={"public_repository": "publicRepository"},
)
class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository:
    def __init__(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "MAVEN_CENTRAL" Possible values: ["MAVEN_CENTRAL"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__173b40bd336c8fb892b551bfee1c08ea8e99b0d47cea7fa9c4c0f1a9ee0b07a3)
            check_type(argname="argument public_repository", value=public_repository, expected_type=type_hints["public_repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if public_repository is not None:
            self._values["public_repository"] = public_repository

    @builtins.property
    def public_repository(self) -> typing.Optional[builtins.str]:
        '''Address of the remote repository. Default value: "MAVEN_CENTRAL" Possible values: ["MAVEN_CENTRAL"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        result = self._values.get("public_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepositoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepositoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__68d46c3562237d2564056f8672c0d6b01221c22fd9ca4cda640c2e486943f111)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPublicRepository")
    def reset_public_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicRepository", []))

    @builtins.property
    @jsii.member(jsii_name="publicRepositoryInput")
    def public_repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="publicRepository")
    def public_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicRepository"))

    @public_repository.setter
    def public_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79f760049bd8b335982e2099781703d0498c3d08e1dc5d08ac5a9415b0c72ee3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicRepository", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__054fb94a56443fc8592c59b979b942bae9fb051f0c0bc09ce2fc26aedb68969a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository",
    jsii_struct_bases=[],
    name_mapping={"public_repository": "publicRepository"},
)
class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository:
    def __init__(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "NPMJS" Possible values: ["NPMJS"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f16c15d1e8c7e326bece8c32c34f84fadf77ae1818e4134d6e2e230f9f6f96a3)
            check_type(argname="argument public_repository", value=public_repository, expected_type=type_hints["public_repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if public_repository is not None:
            self._values["public_repository"] = public_repository

    @builtins.property
    def public_repository(self) -> typing.Optional[builtins.str]:
        '''Address of the remote repository. Default value: "NPMJS" Possible values: ["NPMJS"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        result = self._values.get("public_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepositoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepositoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a1f724e4e99864d72be51c8b3f7c82578696934893ddf257b6b71773d0cf95c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPublicRepository")
    def reset_public_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicRepository", []))

    @builtins.property
    @jsii.member(jsii_name="publicRepositoryInput")
    def public_repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="publicRepository")
    def public_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicRepository"))

    @public_repository.setter
    def public_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e0f119341719bd3ab10524a043e74d6e1dd5d244588b0b3436d2febc13252e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicRepository", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36862856d4d641184221e86d78090b9211efb3dfa061e1469d9a97fd8fe2ca80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9316ff569fd0ec931a3c0c169b1d986bd6bca28e03205e7f1af06ab55df0002)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDockerRepository")
    def put_docker_repository(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "DOCKER_HUB" Possible values: ["DOCKER_HUB"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        value = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository(
            public_repository=public_repository
        )

        return typing.cast(None, jsii.invoke(self, "putDockerRepository", [value]))

    @jsii.member(jsii_name="putMavenRepository")
    def put_maven_repository(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "MAVEN_CENTRAL" Possible values: ["MAVEN_CENTRAL"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        value = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository(
            public_repository=public_repository
        )

        return typing.cast(None, jsii.invoke(self, "putMavenRepository", [value]))

    @jsii.member(jsii_name="putNpmRepository")
    def put_npm_repository(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "NPMJS" Possible values: ["NPMJS"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        value = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository(
            public_repository=public_repository
        )

        return typing.cast(None, jsii.invoke(self, "putNpmRepository", [value]))

    @jsii.member(jsii_name="putPythonRepository")
    def put_python_repository(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "PYPI" Possible values: ["PYPI"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        value = GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository(
            public_repository=public_repository
        )

        return typing.cast(None, jsii.invoke(self, "putPythonRepository", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDockerRepository")
    def reset_docker_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerRepository", []))

    @jsii.member(jsii_name="resetMavenRepository")
    def reset_maven_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMavenRepository", []))

    @jsii.member(jsii_name="resetNpmRepository")
    def reset_npm_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNpmRepository", []))

    @jsii.member(jsii_name="resetPythonRepository")
    def reset_python_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPythonRepository", []))

    @builtins.property
    @jsii.member(jsii_name="dockerRepository")
    def docker_repository(
        self,
    ) -> GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepositoryOutputReference:
        return typing.cast(GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepositoryOutputReference, jsii.get(self, "dockerRepository"))

    @builtins.property
    @jsii.member(jsii_name="mavenRepository")
    def maven_repository(
        self,
    ) -> GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepositoryOutputReference:
        return typing.cast(GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepositoryOutputReference, jsii.get(self, "mavenRepository"))

    @builtins.property
    @jsii.member(jsii_name="npmRepository")
    def npm_repository(
        self,
    ) -> GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepositoryOutputReference:
        return typing.cast(GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepositoryOutputReference, jsii.get(self, "npmRepository"))

    @builtins.property
    @jsii.member(jsii_name="pythonRepository")
    def python_repository(
        self,
    ) -> "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepositoryOutputReference":
        return typing.cast("GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepositoryOutputReference", jsii.get(self, "pythonRepository"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="dockerRepositoryInput")
    def docker_repository_input(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository], jsii.get(self, "dockerRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="mavenRepositoryInput")
    def maven_repository_input(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository], jsii.get(self, "mavenRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="npmRepositoryInput")
    def npm_repository_input(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository], jsii.get(self, "npmRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="pythonRepositoryInput")
    def python_repository_input(
        self,
    ) -> typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository"]:
        return typing.cast(typing.Optional["GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository"], jsii.get(self, "pythonRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eb3ac6e429dd4a3f62e133f393354fd6cb3a2e16178dce77ebeeb71df894d9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a082f76f9b86582156aaf335a4794349c334590ada0f5a25d5e0148b16fed8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository",
    jsii_struct_bases=[],
    name_mapping={"public_repository": "publicRepository"},
)
class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository:
    def __init__(
        self,
        *,
        public_repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param public_repository: Address of the remote repository. Default value: "PYPI" Possible values: ["PYPI"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcedad75dd35d3e74b7b914ae965942796cb8fa6c7deb708aa85708a47c37177)
            check_type(argname="argument public_repository", value=public_repository, expected_type=type_hints["public_repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if public_repository is not None:
            self._values["public_repository"] = public_repository

    @builtins.property
    def public_repository(self) -> typing.Optional[builtins.str]:
        '''Address of the remote repository. Default value: "PYPI" Possible values: ["PYPI"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#public_repository GoogleArtifactRegistryRepository#public_repository}
        '''
        result = self._values.get("public_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepositoryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepositoryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__679eca298cb94d2743453452bb35fea34ee385f91713f8e96c7b4c16accdd0ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPublicRepository")
    def reset_public_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicRepository", []))

    @builtins.property
    @jsii.member(jsii_name="publicRepositoryInput")
    def public_repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="publicRepository")
    def public_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicRepository"))

    @public_repository.setter
    def public_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2609820a6e299fb709facee2c41f3500c071b31e61b1839a71dda0d9dbe6092c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicRepository", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fa9e73c0d1d6d6979517d73c4729a948f408b4e641903d432ba88b932f1457c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleArtifactRegistryRepositoryTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#create GoogleArtifactRegistryRepository#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#delete GoogleArtifactRegistryRepository#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#update GoogleArtifactRegistryRepository#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a87291b666e4d5e7af926365b36a8b7d1dfc8e95b71a557f90667e16421eb3e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#create GoogleArtifactRegistryRepository#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#delete GoogleArtifactRegistryRepository#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#update GoogleArtifactRegistryRepository#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f9e60276f250dee72221e798b3a1b240878877ff9c27f907b9b597f015dada1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0aa0860854dc79f4343a966d7f5de3a49053660ceda9374eb8992aecfd3e4bf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09b5ab646bffdd4ec7073552b8f5393a01749492441a3641fe7e52e15ac10132)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adece7ca2fe14e03b7b625d88e202a376ba1ae5990e2616c20fa077e8ac04b33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2a02c475f86c7c41e49eca96b1298ce6d21b640896b93c2aa2f8d083f4bfb52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryVirtualRepositoryConfig",
    jsii_struct_bases=[],
    name_mapping={"upstream_policies": "upstreamPolicies"},
)
class GoogleArtifactRegistryRepositoryVirtualRepositoryConfig:
    def __init__(
        self,
        *,
        upstream_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param upstream_policies: upstream_policies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#upstream_policies GoogleArtifactRegistryRepository#upstream_policies}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7412e9b1a0ff648494d7a4c082c89fc7466c9b14504d0e412ef8908402210284)
            check_type(argname="argument upstream_policies", value=upstream_policies, expected_type=type_hints["upstream_policies"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if upstream_policies is not None:
            self._values["upstream_policies"] = upstream_policies

    @builtins.property
    def upstream_policies(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies"]]]:
        '''upstream_policies block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#upstream_policies GoogleArtifactRegistryRepository#upstream_policies}
        '''
        result = self._values.get("upstream_policies")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryVirtualRepositoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryVirtualRepositoryConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryVirtualRepositoryConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6839fd5d86d895f50a70cd13ee94ede11b78387e4c88b60190c892573a68625d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putUpstreamPolicies")
    def put_upstream_policies(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c4a34f8cfba67be353027ee0ebe29b5ad1737cf0c6ea9093c96d94599a58dda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUpstreamPolicies", [value]))

    @jsii.member(jsii_name="resetUpstreamPolicies")
    def reset_upstream_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpstreamPolicies", []))

    @builtins.property
    @jsii.member(jsii_name="upstreamPolicies")
    def upstream_policies(
        self,
    ) -> "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesList":
        return typing.cast("GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesList", jsii.get(self, "upstreamPolicies"))

    @builtins.property
    @jsii.member(jsii_name="upstreamPoliciesInput")
    def upstream_policies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies"]]], jsii.get(self, "upstreamPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig]:
        return typing.cast(typing.Optional[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a7fca719d728d30c290c916bbb6da0917d128ea63b4071843c9aaf76519c5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "priority": "priority", "repository": "repository"},
)
class GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies:
    def __init__(
        self,
        *,
        id: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: The user-provided ID of the upstream policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#id GoogleArtifactRegistryRepository#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param priority: Entries with a greater priority value take precedence in the pull order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#priority GoogleArtifactRegistryRepository#priority}
        :param repository: A reference to the repository resource, for example: "projects/p1/locations/us-central1/repository/repo1". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#repository GoogleArtifactRegistryRepository#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed8b0c183eb7336d234999f54eb5166c437a9c201e0e0acdccca0d04b09ab542)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id
        if priority is not None:
            self._values["priority"] = priority
        if repository is not None:
            self._values["repository"] = repository

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''The user-provided ID of the upstream policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#id GoogleArtifactRegistryRepository#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Entries with a greater priority value take precedence in the pull order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#priority GoogleArtifactRegistryRepository#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''A reference to the repository resource, for example: "projects/p1/locations/us-central1/repository/repo1".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_artifact_registry_repository#repository GoogleArtifactRegistryRepository#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64d9db7fad960feabf307fcff51ab73cd564ead3c1a01187f90707e1fb275493)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__775e377a799fe0324be9efb13bf88edbeac0b9c5819a30b3db7aca9b41a26166)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db41e9509d65dcfa9905552fcccbd8a5e0d34b6870d59627166c1c9e1fe54c0a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__64b3cc3426cf2f2789fb720ade71725d470d4e99ee89a0bb259df8201cee0730)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbef3d9e60f2b124d860a8d641cacc690a5eb9056ea8262a1e2a41a3cded4400)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be00d25c3d0a71bdd3db4bc7876e4a58df4e2db640a7e6d20fdac654f816a6c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleArtifactRegistryRepository.GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a44f8cbd508ad15d3e907ec55902d9ea95acaf1de5f5ef10a4cf0828b7aedb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetRepository")
    def reset_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepository", []))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07479d6c97e79c08475a12929020494b5f446814fa39ecbfb3f67f110c572b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__868ca268dde619b18cc1cd5a3a4a2826dce37a05198fa3ec545aa9d86c4f7376)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value)

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4375bac19d6c97b6a487a463d787012b076278c4020bb8b147c66c33975e31df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffbbe263087a0149562f8947819dd59242d3e41361bfad35f633bbdd8238eae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleArtifactRegistryRepository",
    "GoogleArtifactRegistryRepositoryConfig",
    "GoogleArtifactRegistryRepositoryDockerConfig",
    "GoogleArtifactRegistryRepositoryDockerConfigOutputReference",
    "GoogleArtifactRegistryRepositoryMavenConfig",
    "GoogleArtifactRegistryRepositoryMavenConfigOutputReference",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfig",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepositoryOutputReference",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepositoryOutputReference",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepositoryOutputReference",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigOutputReference",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository",
    "GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepositoryOutputReference",
    "GoogleArtifactRegistryRepositoryTimeouts",
    "GoogleArtifactRegistryRepositoryTimeoutsOutputReference",
    "GoogleArtifactRegistryRepositoryVirtualRepositoryConfig",
    "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigOutputReference",
    "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies",
    "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesList",
    "GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPoliciesOutputReference",
]

publication.publish()

def _typecheckingstub__67a11e2122d6664017242aeafd4c93d9fa52129b0712698eca09688c82b13de3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    format: builtins.str,
    repository_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    docker_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryDockerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    kms_key_name: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    location: typing.Optional[builtins.str] = None,
    maven_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryMavenConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    mode: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    remote_repository_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    virtual_repository_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__74a884f9ba44c40a4418e193fc168692418b837dc57d71f179490ba11b5fa40d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1acfe2b5cf2b91d73928a9e731c2cfd069bbac29dcbc52da978ca527d69737d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b587ab17be38890794c093824080b4e454003e1198e375724cdfc3178057854(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec0ed70e3829cbc8930c8fbc32c7fbbafecab184eda9d737a892486619fadcad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__535062de7b2c2b2db5c98c29f5e9ac5025367fbe810e81c83ad59ef15835eaa9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87602acbfc2bd41a8fb9eff6b22fb5c6b2ab9113e61fcbc5705497bd380eb496(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb2ba84f604e1ab673edb088edec27614d9b6b6e5aef7daa40830753dbb93af3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5a0e374397384da479f77b5ea8afb599619865d041cba21a07f3b4eec030e5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__755a1bd588113c26c00d7dd30beaceb0cb1af32b57a2fc7059cfce92eb73a939(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5088d0d29bb6061ed8033079146f76ffd8db624253986f4fa50416e123b6414(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    format: builtins.str,
    repository_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    docker_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryDockerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    kms_key_name: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    location: typing.Optional[builtins.str] = None,
    maven_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryMavenConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    mode: typing.Optional[builtins.str] = None,
    project: typing.Optional[builtins.str] = None,
    remote_repository_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    virtual_repository_config: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f5546da03f0a36d2ba2086fd28a4f0bedd4adcb91d34687fd23ec31d9340c6(
    *,
    immutable_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ebae7feb9192fe8276f41f9914268b82fa1ad588fb88562d165287aaa8c24fc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de4b4341d3cbb36cdaba4fd0cc3b01937bbe2e5f10051bdcbffbe09f4ec7b57d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__278ef6879dfe25305d05e7f7de36e073f7669109bf4f13ece6d479c470068aa2(
    value: typing.Optional[GoogleArtifactRegistryRepositoryDockerConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b86106113cd2326dfa091d75b12f264666750a8e018f6f9dd440d5671916a28f(
    *,
    allow_snapshot_overwrites: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    version_policy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf716c7ee8f7e3708ae13c4a5ed91553e2752a5a2dc59bcabdb0955a5350231(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b444a1b5f285427c2eab3b45eaf064e7331ea489897b86ae9d7be87d33b10a5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1b51472012f31563968da9a4298b224009dce64b3e481bb595e29aaed363681(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ec6ac288c11e20f2f29ea7e5ac0c01034509432a7fd1eb1d38a1c98a11c6cf(
    value: typing.Optional[GoogleArtifactRegistryRepositoryMavenConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3124b5f04fe207fe7b9f7e70d5948dd0cc5b9ac58ea072a6c9b8ad38fa12ec7(
    *,
    description: typing.Optional[builtins.str] = None,
    docker_repository: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository, typing.Dict[builtins.str, typing.Any]]] = None,
    maven_repository: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository, typing.Dict[builtins.str, typing.Any]]] = None,
    npm_repository: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository, typing.Dict[builtins.str, typing.Any]]] = None,
    python_repository: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fe2c5a77bb1705dcdf629eeb965b6991604a2b6f152a4c0c81a4ac531d86c63(
    *,
    public_repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__040cbeb20e8cafcadf2397a94e2cd6b4428dcc5af0ba3f7eb8d0c27b1078e8d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66d2feabb5f4c368b27b272540662a1a9503442d86b2461a00d56e4ec2c9d8a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6583a2160ab7438cb3c884ba152391468a61b2e6724b19345ee684f8c205cea9(
    value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigDockerRepository],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173b40bd336c8fb892b551bfee1c08ea8e99b0d47cea7fa9c4c0f1a9ee0b07a3(
    *,
    public_repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68d46c3562237d2564056f8672c0d6b01221c22fd9ca4cda640c2e486943f111(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79f760049bd8b335982e2099781703d0498c3d08e1dc5d08ac5a9415b0c72ee3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__054fb94a56443fc8592c59b979b942bae9fb051f0c0bc09ce2fc26aedb68969a(
    value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigMavenRepository],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f16c15d1e8c7e326bece8c32c34f84fadf77ae1818e4134d6e2e230f9f6f96a3(
    *,
    public_repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a1f724e4e99864d72be51c8b3f7c82578696934893ddf257b6b71773d0cf95c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e0f119341719bd3ab10524a043e74d6e1dd5d244588b0b3436d2febc13252e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36862856d4d641184221e86d78090b9211efb3dfa061e1469d9a97fd8fe2ca80(
    value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigNpmRepository],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9316ff569fd0ec931a3c0c169b1d986bd6bca28e03205e7f1af06ab55df0002(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb3ac6e429dd4a3f62e133f393354fd6cb3a2e16178dce77ebeeb71df894d9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a082f76f9b86582156aaf335a4794349c334590ada0f5a25d5e0148b16fed8e(
    value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcedad75dd35d3e74b7b914ae965942796cb8fa6c7deb708aa85708a47c37177(
    *,
    public_repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679eca298cb94d2743453452bb35fea34ee385f91713f8e96c7b4c16accdd0ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2609820a6e299fb709facee2c41f3500c071b31e61b1839a71dda0d9dbe6092c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fa9e73c0d1d6d6979517d73c4729a948f408b4e641903d432ba88b932f1457c(
    value: typing.Optional[GoogleArtifactRegistryRepositoryRemoteRepositoryConfigPythonRepository],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a87291b666e4d5e7af926365b36a8b7d1dfc8e95b71a557f90667e16421eb3e(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9e60276f250dee72221e798b3a1b240878877ff9c27f907b9b597f015dada1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0aa0860854dc79f4343a966d7f5de3a49053660ceda9374eb8992aecfd3e4bf8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09b5ab646bffdd4ec7073552b8f5393a01749492441a3641fe7e52e15ac10132(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adece7ca2fe14e03b7b625d88e202a376ba1ae5990e2616c20fa077e8ac04b33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2a02c475f86c7c41e49eca96b1298ce6d21b640896b93c2aa2f8d083f4bfb52(
    value: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7412e9b1a0ff648494d7a4c082c89fc7466c9b14504d0e412ef8908402210284(
    *,
    upstream_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6839fd5d86d895f50a70cd13ee94ede11b78387e4c88b60190c892573a68625d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4a34f8cfba67be353027ee0ebe29b5ad1737cf0c6ea9093c96d94599a58dda(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a7fca719d728d30c290c916bbb6da0917d128ea63b4071843c9aaf76519c5d(
    value: typing.Optional[GoogleArtifactRegistryRepositoryVirtualRepositoryConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed8b0c183eb7336d234999f54eb5166c437a9c201e0e0acdccca0d04b09ab542(
    *,
    id: typing.Optional[builtins.str] = None,
    priority: typing.Optional[jsii.Number] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64d9db7fad960feabf307fcff51ab73cd564ead3c1a01187f90707e1fb275493(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__775e377a799fe0324be9efb13bf88edbeac0b9c5819a30b3db7aca9b41a26166(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db41e9509d65dcfa9905552fcccbd8a5e0d34b6870d59627166c1c9e1fe54c0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64b3cc3426cf2f2789fb720ade71725d470d4e99ee89a0bb259df8201cee0730(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbef3d9e60f2b124d860a8d641cacc690a5eb9056ea8262a1e2a41a3cded4400(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be00d25c3d0a71bdd3db4bc7876e4a58df4e2db640a7e6d20fdac654f816a6c2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a44f8cbd508ad15d3e907ec55902d9ea95acaf1de5f5ef10a4cf0828b7aedb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07479d6c97e79c08475a12929020494b5f446814fa39ecbfb3f67f110c572b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__868ca268dde619b18cc1cd5a3a4a2826dce37a05198fa3ec545aa9d86c4f7376(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4375bac19d6c97b6a487a463d787012b076278c4020bb8b147c66c33975e31df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffbbe263087a0149562f8947819dd59242d3e41361bfad35f633bbdd8238eae8(
    value: typing.Optional[typing.Union[GoogleArtifactRegistryRepositoryVirtualRepositoryConfigUpstreamPolicies, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
