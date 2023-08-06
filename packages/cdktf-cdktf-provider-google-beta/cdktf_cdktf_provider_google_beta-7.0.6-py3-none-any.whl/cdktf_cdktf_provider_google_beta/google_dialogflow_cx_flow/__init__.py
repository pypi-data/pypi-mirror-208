'''
# `google_dialogflow_cx_flow`

Refer to the Terraform Registory for docs: [`google_dialogflow_cx_flow`](https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow).
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


class GoogleDialogflowCxFlow(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlow",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow google_dialogflow_cx_flow}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        display_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowEventHandlers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        language_code: typing.Optional[builtins.str] = None,
        nlu_settings: typing.Optional[typing.Union["GoogleDialogflowCxFlowNluSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        parent: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxFlowTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow google_dialogflow_cx_flow} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: The human-readable name of the flow. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#display_name GoogleDialogflowCxFlow#display_name}
        :param description: The description of the flow. The maximum length is 500 characters. If exceeded, the request is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#description GoogleDialogflowCxFlow#description}
        :param event_handlers: event_handlers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#event_handlers GoogleDialogflowCxFlow#event_handlers}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#id GoogleDialogflowCxFlow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param language_code: The language of the following fields in flow: Flow.event_handlers.trigger_fulfillment.messages Flow.event_handlers.trigger_fulfillment.conditional_cases Flow.transition_routes.trigger_fulfillment.messages Flow.transition_routes.trigger_fulfillment.conditional_cases If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#language_code GoogleDialogflowCxFlow#language_code}
        :param nlu_settings: nlu_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#nlu_settings GoogleDialogflowCxFlow#nlu_settings}
        :param parent: The agent to create a flow for. Format: projects//locations//agents/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#parent GoogleDialogflowCxFlow#parent}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#timeouts GoogleDialogflowCxFlow#timeouts}
        :param transition_route_groups: A flow's transition route group serve two purposes: They are responsible for matching the user's first utterances in the flow. They are inherited by every page's [transition route groups][Page.transition_route_groups]. Transition route groups defined in the page have higher priority than those defined in the flow. Format:projects//locations//agents//flows//transitionRouteGroups/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_route_groups GoogleDialogflowCxFlow#transition_route_groups}
        :param transition_routes: transition_routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_routes GoogleDialogflowCxFlow#transition_routes}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ddc1c9bd1aaab871a2b80768c2bc499e93a36227c2ec26b6797aac6fac61ceb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleDialogflowCxFlowConfig(
            display_name=display_name,
            description=description,
            event_handlers=event_handlers,
            id=id,
            language_code=language_code,
            nlu_settings=nlu_settings,
            parent=parent,
            timeouts=timeouts,
            transition_route_groups=transition_route_groups,
            transition_routes=transition_routes,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putEventHandlers")
    def put_event_handlers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowEventHandlers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d5763a95f2a19a20a2cee1cd63b8e22e995b6ccdda0bc67f0a8ba7c9afea462)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEventHandlers", [value]))

    @jsii.member(jsii_name="putNluSettings")
    def put_nlu_settings(
        self,
        *,
        classification_threshold: typing.Optional[jsii.Number] = None,
        model_training_mode: typing.Optional[builtins.str] = None,
        model_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param classification_threshold: To filter out false positive results and still get variety in matched natural language inputs for your agent, you can tune the machine learning classification threshold. If the returned score value is less than the threshold value, then a no-match event will be triggered. The score values range from 0.0 (completely uncertain) to 1.0 (completely certain). If set to 0.0, the default of 0.3 is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#classification_threshold GoogleDialogflowCxFlow#classification_threshold}
        :param model_training_mode: Indicates NLU model training mode. MODEL_TRAINING_MODE_AUTOMATIC: NLU model training is automatically triggered when a flow gets modified. User can also manually trigger model training in this mode. MODEL_TRAINING_MODE_MANUAL: User needs to manually trigger NLU model training. Best for large flows whose models take long time to train. Possible values: ["MODEL_TRAINING_MODE_AUTOMATIC", "MODEL_TRAINING_MODE_MANUAL"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_training_mode GoogleDialogflowCxFlow#model_training_mode}
        :param model_type: Indicates the type of NLU model. MODEL_TYPE_STANDARD: Use standard NLU model. MODEL_TYPE_ADVANCED: Use advanced NLU model. Possible values: ["MODEL_TYPE_STANDARD", "MODEL_TYPE_ADVANCED"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_type GoogleDialogflowCxFlow#model_type}
        '''
        value = GoogleDialogflowCxFlowNluSettings(
            classification_threshold=classification_threshold,
            model_training_mode=model_training_mode,
            model_type=model_type,
        )

        return typing.cast(None, jsii.invoke(self, "putNluSettings", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#create GoogleDialogflowCxFlow#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#delete GoogleDialogflowCxFlow#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#update GoogleDialogflowCxFlow#update}.
        '''
        value = GoogleDialogflowCxFlowTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTransitionRoutes")
    def put_transition_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f67d14e084641d1578e154aed126fcf46d108e0c8f21351b034db072abbe3b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTransitionRoutes", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEventHandlers")
    def reset_event_handlers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventHandlers", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLanguageCode")
    def reset_language_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanguageCode", []))

    @jsii.member(jsii_name="resetNluSettings")
    def reset_nlu_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNluSettings", []))

    @jsii.member(jsii_name="resetParent")
    def reset_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParent", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTransitionRouteGroups")
    def reset_transition_route_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransitionRouteGroups", []))

    @jsii.member(jsii_name="resetTransitionRoutes")
    def reset_transition_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransitionRoutes", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="eventHandlers")
    def event_handlers(self) -> "GoogleDialogflowCxFlowEventHandlersList":
        return typing.cast("GoogleDialogflowCxFlowEventHandlersList", jsii.get(self, "eventHandlers"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="nluSettings")
    def nlu_settings(self) -> "GoogleDialogflowCxFlowNluSettingsOutputReference":
        return typing.cast("GoogleDialogflowCxFlowNluSettingsOutputReference", jsii.get(self, "nluSettings"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleDialogflowCxFlowTimeoutsOutputReference":
        return typing.cast("GoogleDialogflowCxFlowTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="transitionRoutes")
    def transition_routes(self) -> "GoogleDialogflowCxFlowTransitionRoutesList":
        return typing.cast("GoogleDialogflowCxFlowTransitionRoutesList", jsii.get(self, "transitionRoutes"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="eventHandlersInput")
    def event_handlers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlers"]]], jsii.get(self, "eventHandlersInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="languageCodeInput")
    def language_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "languageCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="nluSettingsInput")
    def nlu_settings_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowNluSettings"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowNluSettings"], jsii.get(self, "nluSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["GoogleDialogflowCxFlowTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["GoogleDialogflowCxFlowTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="transitionRouteGroupsInput")
    def transition_route_groups_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "transitionRouteGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="transitionRoutesInput")
    def transition_routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutes"]]], jsii.get(self, "transitionRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7564a7905ff3d080ec73fd5b3674d80316185888f34b793426007f2891348fc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d57e353ea4e0c1dbefde806a99b8c916a02fa1ed2fdd994823bfcf5422e9934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab5ec690ece1ff9fa75d59b2a15d2b7ececfba9a83206cd737e9f2f7198cb5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="languageCode")
    def language_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "languageCode"))

    @language_code.setter
    def language_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb70b48e85ea80ce1f103a0c05a4b3466c57a382c528c7a81ce07b3b8df410ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "languageCode", value)

    @builtins.property
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a48c675e5612a9b38a6595f66082b141506e7336639e253e7d20e4b003a2e87d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parent", value)

    @builtins.property
    @jsii.member(jsii_name="transitionRouteGroups")
    def transition_route_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "transitionRouteGroups"))

    @transition_route_groups.setter
    def transition_route_groups(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8b9d2da6f549846ac8b8c3ea7bb8b102639d483550c7cb5ff7fa1924d572b11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transitionRouteGroups", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "display_name": "displayName",
        "description": "description",
        "event_handlers": "eventHandlers",
        "id": "id",
        "language_code": "languageCode",
        "nlu_settings": "nluSettings",
        "parent": "parent",
        "timeouts": "timeouts",
        "transition_route_groups": "transitionRouteGroups",
        "transition_routes": "transitionRoutes",
    },
)
class GoogleDialogflowCxFlowConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        display_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowEventHandlers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        language_code: typing.Optional[builtins.str] = None,
        nlu_settings: typing.Optional[typing.Union["GoogleDialogflowCxFlowNluSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        parent: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxFlowTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: The human-readable name of the flow. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#display_name GoogleDialogflowCxFlow#display_name}
        :param description: The description of the flow. The maximum length is 500 characters. If exceeded, the request is rejected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#description GoogleDialogflowCxFlow#description}
        :param event_handlers: event_handlers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#event_handlers GoogleDialogflowCxFlow#event_handlers}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#id GoogleDialogflowCxFlow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param language_code: The language of the following fields in flow: Flow.event_handlers.trigger_fulfillment.messages Flow.event_handlers.trigger_fulfillment.conditional_cases Flow.transition_routes.trigger_fulfillment.messages Flow.transition_routes.trigger_fulfillment.conditional_cases If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#language_code GoogleDialogflowCxFlow#language_code}
        :param nlu_settings: nlu_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#nlu_settings GoogleDialogflowCxFlow#nlu_settings}
        :param parent: The agent to create a flow for. Format: projects//locations//agents/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#parent GoogleDialogflowCxFlow#parent}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#timeouts GoogleDialogflowCxFlow#timeouts}
        :param transition_route_groups: A flow's transition route group serve two purposes: They are responsible for matching the user's first utterances in the flow. They are inherited by every page's [transition route groups][Page.transition_route_groups]. Transition route groups defined in the page have higher priority than those defined in the flow. Format:projects//locations//agents//flows//transitionRouteGroups/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_route_groups GoogleDialogflowCxFlow#transition_route_groups}
        :param transition_routes: transition_routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_routes GoogleDialogflowCxFlow#transition_routes}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(nlu_settings, dict):
            nlu_settings = GoogleDialogflowCxFlowNluSettings(**nlu_settings)
        if isinstance(timeouts, dict):
            timeouts = GoogleDialogflowCxFlowTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5b6d22821ccb6c1261edc07f6bc6656e98299156ae0eaee2da8542a3e22cb90)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_handlers", value=event_handlers, expected_type=type_hints["event_handlers"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument language_code", value=language_code, expected_type=type_hints["language_code"])
            check_type(argname="argument nlu_settings", value=nlu_settings, expected_type=type_hints["nlu_settings"])
            check_type(argname="argument parent", value=parent, expected_type=type_hints["parent"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument transition_route_groups", value=transition_route_groups, expected_type=type_hints["transition_route_groups"])
            check_type(argname="argument transition_routes", value=transition_routes, expected_type=type_hints["transition_routes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "display_name": display_name,
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
        if event_handlers is not None:
            self._values["event_handlers"] = event_handlers
        if id is not None:
            self._values["id"] = id
        if language_code is not None:
            self._values["language_code"] = language_code
        if nlu_settings is not None:
            self._values["nlu_settings"] = nlu_settings
        if parent is not None:
            self._values["parent"] = parent
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if transition_route_groups is not None:
            self._values["transition_route_groups"] = transition_route_groups
        if transition_routes is not None:
            self._values["transition_routes"] = transition_routes

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
    def display_name(self) -> builtins.str:
        '''The human-readable name of the flow.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#display_name GoogleDialogflowCxFlow#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the flow. The maximum length is 500 characters. If exceeded, the request is rejected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#description GoogleDialogflowCxFlow#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_handlers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlers"]]]:
        '''event_handlers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#event_handlers GoogleDialogflowCxFlow#event_handlers}
        '''
        result = self._values.get("event_handlers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlers"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#id GoogleDialogflowCxFlow#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def language_code(self) -> typing.Optional[builtins.str]:
        '''The language of the following fields in flow: Flow.event_handlers.trigger_fulfillment.messages Flow.event_handlers.trigger_fulfillment.conditional_cases Flow.transition_routes.trigger_fulfillment.messages Flow.transition_routes.trigger_fulfillment.conditional_cases If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#language_code GoogleDialogflowCxFlow#language_code}
        '''
        result = self._values.get("language_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nlu_settings(self) -> typing.Optional["GoogleDialogflowCxFlowNluSettings"]:
        '''nlu_settings block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#nlu_settings GoogleDialogflowCxFlow#nlu_settings}
        '''
        result = self._values.get("nlu_settings")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowNluSettings"], result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''The agent to create a flow for. Format: projects//locations//agents/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#parent GoogleDialogflowCxFlow#parent}
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleDialogflowCxFlowTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#timeouts GoogleDialogflowCxFlow#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowTimeouts"], result)

    @builtins.property
    def transition_route_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A flow's transition route group serve two purposes: They are responsible for matching the user's first utterances in the flow.

        They are inherited by every page's [transition route groups][Page.transition_route_groups]. Transition route groups defined in the page have higher priority than those defined in the flow.
        Format:projects//locations//agents//flows//transitionRouteGroups/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_route_groups GoogleDialogflowCxFlow#transition_route_groups}
        '''
        result = self._values.get("transition_route_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def transition_routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutes"]]]:
        '''transition_routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#transition_routes GoogleDialogflowCxFlow#transition_routes}
        '''
        result = self._values.get("transition_routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlers",
    jsii_struct_bases=[],
    name_mapping={
        "event": "event",
        "target_flow": "targetFlow",
        "target_page": "targetPage",
        "trigger_fulfillment": "triggerFulfillment",
    },
)
class GoogleDialogflowCxFlowEventHandlers:
    def __init__(
        self,
        *,
        event: typing.Optional[builtins.str] = None,
        target_flow: typing.Optional[builtins.str] = None,
        target_page: typing.Optional[builtins.str] = None,
        trigger_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxFlowEventHandlersTriggerFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param event: The name of the event to handle. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#event GoogleDialogflowCxFlow#event}
        :param target_flow: The target flow to transition to. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_flow GoogleDialogflowCxFlow#target_flow}
        :param target_page: The target page to transition to. Format: projects//locations//agents//flows//pages/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_page GoogleDialogflowCxFlow#target_page}
        :param trigger_fulfillment: trigger_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#trigger_fulfillment GoogleDialogflowCxFlow#trigger_fulfillment}
        '''
        if isinstance(trigger_fulfillment, dict):
            trigger_fulfillment = GoogleDialogflowCxFlowEventHandlersTriggerFulfillment(**trigger_fulfillment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98d6b437f59c96e369e9a65e8cba23f38e57df796929bbd75224bcedc388b721)
            check_type(argname="argument event", value=event, expected_type=type_hints["event"])
            check_type(argname="argument target_flow", value=target_flow, expected_type=type_hints["target_flow"])
            check_type(argname="argument target_page", value=target_page, expected_type=type_hints["target_page"])
            check_type(argname="argument trigger_fulfillment", value=trigger_fulfillment, expected_type=type_hints["trigger_fulfillment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if event is not None:
            self._values["event"] = event
        if target_flow is not None:
            self._values["target_flow"] = target_flow
        if target_page is not None:
            self._values["target_page"] = target_page
        if trigger_fulfillment is not None:
            self._values["trigger_fulfillment"] = trigger_fulfillment

    @builtins.property
    def event(self) -> typing.Optional[builtins.str]:
        '''The name of the event to handle.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#event GoogleDialogflowCxFlow#event}
        '''
        result = self._values.get("event")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_flow(self) -> typing.Optional[builtins.str]:
        '''The target flow to transition to. Format: projects//locations//agents//flows/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_flow GoogleDialogflowCxFlow#target_flow}
        '''
        result = self._values.get("target_flow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_page(self) -> typing.Optional[builtins.str]:
        '''The target page to transition to. Format: projects//locations//agents//flows//pages/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_page GoogleDialogflowCxFlow#target_page}
        '''
        result = self._values.get("target_page")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillment"]:
        '''trigger_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#trigger_fulfillment GoogleDialogflowCxFlow#trigger_fulfillment}
        '''
        result = self._values.get("trigger_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillment"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowEventHandlers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowEventHandlersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ea6d2385130136ba9ba2449229da1e1d3e391e41dfafc4c8ca3bb1631d4ce14)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxFlowEventHandlersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b72692e2f83b58047d9ef491b2c6b8d6d65b1d0576f01c8e029ece54d7ca94a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxFlowEventHandlersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10e47925b00e47f983de73bfa202626a1e3135e199f22fe97d586dabb330c1f3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a87ff1ba2605882bab6a41459482a8d5ce15d04140c213017f7aa60d0f1f8cd4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__797650aaec31e7ca6bb8bc45d5cb90e35913ad807f256a34b97189d1d969d736)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__550686a1780bbee4f9f8564add05760636a98a28cf7e02f3c02b086103f5e3dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowEventHandlersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0b49a2bf192f63cb5a72c1bd7cdffb07f5cdb45767d0977c9c0af70fe72a68a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTriggerFulfillment")
    def put_trigger_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        value = GoogleDialogflowCxFlowEventHandlersTriggerFulfillment(
            messages=messages,
            return_partial_responses=return_partial_responses,
            tag=tag,
            webhook=webhook,
        )

        return typing.cast(None, jsii.invoke(self, "putTriggerFulfillment", [value]))

    @jsii.member(jsii_name="resetEvent")
    def reset_event(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvent", []))

    @jsii.member(jsii_name="resetTargetFlow")
    def reset_target_flow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetFlow", []))

    @jsii.member(jsii_name="resetTargetPage")
    def reset_target_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetPage", []))

    @jsii.member(jsii_name="resetTriggerFulfillment")
    def reset_trigger_fulfillment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggerFulfillment", []))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="triggerFulfillment")
    def trigger_fulfillment(
        self,
    ) -> "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentOutputReference":
        return typing.cast("GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentOutputReference", jsii.get(self, "triggerFulfillment"))

    @builtins.property
    @jsii.member(jsii_name="eventInput")
    def event_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventInput"))

    @builtins.property
    @jsii.member(jsii_name="targetFlowInput")
    def target_flow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetFlowInput"))

    @builtins.property
    @jsii.member(jsii_name="targetPageInput")
    def target_page_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetPageInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerFulfillmentInput")
    def trigger_fulfillment_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillment"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillment"], jsii.get(self, "triggerFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="event")
    def event(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "event"))

    @event.setter
    def event(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b6f23d473fdfa3616c5c573a6311ed0c64ca67237e5fc371844d19be8d4b06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "event", value)

    @builtins.property
    @jsii.member(jsii_name="targetFlow")
    def target_flow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetFlow"))

    @target_flow.setter
    def target_flow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8232a76d7dd21a85014f51ee2b25961374daa0e33aba5d27aed553abf55ee0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetFlow", value)

    @builtins.property
    @jsii.member(jsii_name="targetPage")
    def target_page(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetPage"))

    @target_page.setter
    def target_page(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6d60b11ea63adf1c7be2210f0b5cecc0c0346fad1ab06f7f78bd60d2f16a37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPage", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlers, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlers, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlers, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b10706871c1d1f665ef2d90bd0d58a208650af42514f7be1dca25fb9f02432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxFlowEventHandlersTriggerFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2b0b5e0e8e08564eff12bc1e01fd9807cb7a628d58f0aa0ac775e881f69e3fe)
            check_type(argname="argument messages", value=messages, expected_type=type_hints["messages"])
            check_type(argname="argument return_partial_responses", value=return_partial_responses, expected_type=type_hints["return_partial_responses"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if messages is not None:
            self._values["messages"] = messages
        if return_partial_responses is not None:
            self._values["return_partial_responses"] = return_partial_responses
        if tag is not None:
            self._values["tag"] = tag
        if webhook is not None:
            self._values["webhook"] = webhook

    @builtins.property
    def messages(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowEventHandlersTriggerFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47cf1b77ff3ec061bdddb90036c33368f3e5b8f584b5d70cb6c8d6c442148a4f)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91a30f242e5ea4183f4a388675dae2a39a85ebb559121c69b38971a70ae0259b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef209c5de032bddd5d5f68a59e2625324e8d419c75f45bb6c212f1afcdcf5337)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fb9eaee16e8332e5d899c05745620e138957c5e96c41b0be100922470cea560)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8df20db12f6bf4a2136b74d845969b82f6c72d29f3160edf5aaf3e9607405c84)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc59802a7434cb11ca69be912e59b031a4a61b4c64c7c3877cf2b86eedfb6dc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66fc6f716cf1db773623fff9494d38d2fd97eaa1964cbad881bf5cb7c48ed834)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a5d7394da129220d20cf2d3e9de1e4a8bc97cf36ff80f93157bd345d447f814)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putText")
    def put_text(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        value = GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText(
            text=text
        )

        return typing.cast(None, jsii.invoke(self, "putText", [value]))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(
        self,
    ) -> "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33fd52d5aee1abc2af7510c2d810adabcf29a9323ff8a75fac9e0e5a9b3d8e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caf968656644d2b99fc0f819ca3a16b23f096995475b7b3a6e08e5c1c1358318)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4ec1e46f38dd2a469bcfc5e0b204a6b11595e08e119b7981575105910d8c78d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @builtins.property
    @jsii.member(jsii_name="allowPlaybackInterruption")
    def allow_playback_interruption(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowPlaybackInterruption"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "text"))

    @text.setter
    def text(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__037aec295bb472f589ea596cbfebb45456ce81962af528f351d6b6e616e3b242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__479b59249a9dfb3608d4dc0fed24b0337e07fe844e83827b6f943b301566db71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bad15ed6b01e2d0546b46b152ea04c1371cb3c7d4324e188ef4e47b66fade90)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42f5acfd4c64d5ac63b8f15f48c10d2fd9d8bc9b56ae86ee6bab6d18e6328278)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMessages", [value]))

    @jsii.member(jsii_name="resetMessages")
    def reset_messages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessages", []))

    @jsii.member(jsii_name="resetReturnPartialResponses")
    def reset_return_partial_responses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReturnPartialResponses", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetWebhook")
    def reset_webhook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhook", []))

    @builtins.property
    @jsii.member(jsii_name="messages")
    def messages(
        self,
    ) -> GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]], jsii.get(self, "messagesInput"))

    @builtins.property
    @jsii.member(jsii_name="returnPartialResponsesInput")
    def return_partial_responses_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "returnPartialResponsesInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookInput")
    def webhook_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookInput"))

    @builtins.property
    @jsii.member(jsii_name="returnPartialResponses")
    def return_partial_responses(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "returnPartialResponses"))

    @return_partial_responses.setter
    def return_partial_responses(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b357e6f9c60440207ddaad42c083f61899fd2ca2bcace2737949eb6ea6851467)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05e50fe901dbf61aa635a56e265013a777da162a618815e4ec01998dc21f697c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91bf4cce913b48aa52137ae8d78dc55d18dccf652b6d505fed4dc622a5a91a55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3744515a4e7ffc4c34a960ba8fd725e26afa66704674a5e14177efa17342c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowNluSettings",
    jsii_struct_bases=[],
    name_mapping={
        "classification_threshold": "classificationThreshold",
        "model_training_mode": "modelTrainingMode",
        "model_type": "modelType",
    },
)
class GoogleDialogflowCxFlowNluSettings:
    def __init__(
        self,
        *,
        classification_threshold: typing.Optional[jsii.Number] = None,
        model_training_mode: typing.Optional[builtins.str] = None,
        model_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param classification_threshold: To filter out false positive results and still get variety in matched natural language inputs for your agent, you can tune the machine learning classification threshold. If the returned score value is less than the threshold value, then a no-match event will be triggered. The score values range from 0.0 (completely uncertain) to 1.0 (completely certain). If set to 0.0, the default of 0.3 is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#classification_threshold GoogleDialogflowCxFlow#classification_threshold}
        :param model_training_mode: Indicates NLU model training mode. MODEL_TRAINING_MODE_AUTOMATIC: NLU model training is automatically triggered when a flow gets modified. User can also manually trigger model training in this mode. MODEL_TRAINING_MODE_MANUAL: User needs to manually trigger NLU model training. Best for large flows whose models take long time to train. Possible values: ["MODEL_TRAINING_MODE_AUTOMATIC", "MODEL_TRAINING_MODE_MANUAL"] Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_training_mode GoogleDialogflowCxFlow#model_training_mode}
        :param model_type: Indicates the type of NLU model. MODEL_TYPE_STANDARD: Use standard NLU model. MODEL_TYPE_ADVANCED: Use advanced NLU model. Possible values: ["MODEL_TYPE_STANDARD", "MODEL_TYPE_ADVANCED"]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_type GoogleDialogflowCxFlow#model_type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e11d2415d17184287951f07c3c59b5989b582c6777731b857475cbefa2994ab9)
            check_type(argname="argument classification_threshold", value=classification_threshold, expected_type=type_hints["classification_threshold"])
            check_type(argname="argument model_training_mode", value=model_training_mode, expected_type=type_hints["model_training_mode"])
            check_type(argname="argument model_type", value=model_type, expected_type=type_hints["model_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if classification_threshold is not None:
            self._values["classification_threshold"] = classification_threshold
        if model_training_mode is not None:
            self._values["model_training_mode"] = model_training_mode
        if model_type is not None:
            self._values["model_type"] = model_type

    @builtins.property
    def classification_threshold(self) -> typing.Optional[jsii.Number]:
        '''To filter out false positive results and still get variety in matched natural language inputs for your agent, you can tune the machine learning classification threshold.

        If the returned score value is less than the threshold value, then a no-match event will be triggered. The score values range from 0.0 (completely uncertain) to 1.0 (completely certain). If set to 0.0, the default of 0.3 is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#classification_threshold GoogleDialogflowCxFlow#classification_threshold}
        '''
        result = self._values.get("classification_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model_training_mode(self) -> typing.Optional[builtins.str]:
        '''Indicates NLU model training mode.

        MODEL_TRAINING_MODE_AUTOMATIC: NLU model training is automatically triggered when a flow gets modified. User can also manually trigger model training in this mode.
        MODEL_TRAINING_MODE_MANUAL: User needs to manually trigger NLU model training. Best for large flows whose models take long time to train. Possible values: ["MODEL_TRAINING_MODE_AUTOMATIC", "MODEL_TRAINING_MODE_MANUAL"]

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_training_mode GoogleDialogflowCxFlow#model_training_mode}
        '''
        result = self._values.get("model_training_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def model_type(self) -> typing.Optional[builtins.str]:
        '''Indicates the type of NLU model. MODEL_TYPE_STANDARD: Use standard NLU model. MODEL_TYPE_ADVANCED: Use advanced NLU model. Possible values: ["MODEL_TYPE_STANDARD", "MODEL_TYPE_ADVANCED"].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#model_type GoogleDialogflowCxFlow#model_type}
        '''
        result = self._values.get("model_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowNluSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowNluSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowNluSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98d9f3909bba7513ded942dd49ab4eff31602cdb034f4a4e1475a92d9195e3cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetClassificationThreshold")
    def reset_classification_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClassificationThreshold", []))

    @jsii.member(jsii_name="resetModelTrainingMode")
    def reset_model_training_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelTrainingMode", []))

    @jsii.member(jsii_name="resetModelType")
    def reset_model_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModelType", []))

    @builtins.property
    @jsii.member(jsii_name="classificationThresholdInput")
    def classification_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "classificationThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="modelTrainingModeInput")
    def model_training_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelTrainingModeInput"))

    @builtins.property
    @jsii.member(jsii_name="modelTypeInput")
    def model_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="classificationThreshold")
    def classification_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "classificationThreshold"))

    @classification_threshold.setter
    def classification_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45305366a1d242576564cf317b03d1a334294e16921345b493918e93aecceff7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "classificationThreshold", value)

    @builtins.property
    @jsii.member(jsii_name="modelTrainingMode")
    def model_training_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelTrainingMode"))

    @model_training_mode.setter
    def model_training_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__536cbd1264bd06bfdfe3cee75d9622418afef8311158512d4f56b6ab9158e3f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelTrainingMode", value)

    @builtins.property
    @jsii.member(jsii_name="modelType")
    def model_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelType"))

    @model_type.setter
    def model_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe96da0683e88b188041d7de4c92fed18d30c2e19f30792d01ac81a7e8fc06f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDialogflowCxFlowNluSettings]:
        return typing.cast(typing.Optional[GoogleDialogflowCxFlowNluSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxFlowNluSettings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524f25a80f58940c6773cd38d1d4a7c6ddb98c11023b57dd08686d71d4bec644)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleDialogflowCxFlowTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#create GoogleDialogflowCxFlow#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#delete GoogleDialogflowCxFlow#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#update GoogleDialogflowCxFlow#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0210a03cea17a8ef6bb6c8d12573cd1b0d7140688721c228c725071420680dd6)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#create GoogleDialogflowCxFlow#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#delete GoogleDialogflowCxFlow#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#update GoogleDialogflowCxFlow#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0e68db04b76164173d2591ddd75bb1b9b052a340e3f358976041e891232cfc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c8fa4d3bd2d4d417cd91617f1a451745bf4aaf04d58d7966be4fba2c6597fe3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d5975630e9faa60ef9b199ec40a0b2873f5df8a921e7f852dabdc8a78073309)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e778f648906def1b0b98d5164ec361e201a715e15a0d72467b7788a670fc5c4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86c6d5b814a990c8b13a0674f1e520f123196a9fc67d10ff966cfed6d664ab5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutes",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "intent": "intent",
        "target_flow": "targetFlow",
        "target_page": "targetPage",
        "trigger_fulfillment": "triggerFulfillment",
    },
)
class GoogleDialogflowCxFlowTransitionRoutes:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        intent: typing.Optional[builtins.str] = None,
        target_flow: typing.Optional[builtins.str] = None,
        target_page: typing.Optional[builtins.str] = None,
        trigger_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: The condition to evaluate against form parameters or session parameters. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#condition GoogleDialogflowCxFlow#condition}
        :param intent: The unique identifier of an Intent. Format: projects//locations//agents//intents/. Indicates that the transition can only happen when the given intent is matched. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#intent GoogleDialogflowCxFlow#intent}
        :param target_flow: The target flow to transition to. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_flow GoogleDialogflowCxFlow#target_flow}
        :param target_page: The target page to transition to. Format: projects//locations//agents//flows//pages/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_page GoogleDialogflowCxFlow#target_page}
        :param trigger_fulfillment: trigger_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#trigger_fulfillment GoogleDialogflowCxFlow#trigger_fulfillment}
        '''
        if isinstance(trigger_fulfillment, dict):
            trigger_fulfillment = GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment(**trigger_fulfillment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d1a18960d79eb590c9d5bf3e090bd2e010515560266b7c63ff53264e0f013b1)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument intent", value=intent, expected_type=type_hints["intent"])
            check_type(argname="argument target_flow", value=target_flow, expected_type=type_hints["target_flow"])
            check_type(argname="argument target_page", value=target_page, expected_type=type_hints["target_page"])
            check_type(argname="argument trigger_fulfillment", value=trigger_fulfillment, expected_type=type_hints["trigger_fulfillment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if intent is not None:
            self._values["intent"] = intent
        if target_flow is not None:
            self._values["target_flow"] = target_flow
        if target_page is not None:
            self._values["target_page"] = target_page
        if trigger_fulfillment is not None:
            self._values["trigger_fulfillment"] = trigger_fulfillment

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''The condition to evaluate against form parameters or session parameters.

        At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#condition GoogleDialogflowCxFlow#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def intent(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of an Intent.

        Format: projects//locations//agents//intents/. Indicates that the transition can only happen when the given intent is matched. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#intent GoogleDialogflowCxFlow#intent}
        '''
        result = self._values.get("intent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_flow(self) -> typing.Optional[builtins.str]:
        '''The target flow to transition to. Format: projects//locations//agents//flows/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_flow GoogleDialogflowCxFlow#target_flow}
        '''
        result = self._values.get("target_flow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_page(self) -> typing.Optional[builtins.str]:
        '''The target page to transition to. Format: projects//locations//agents//flows//pages/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#target_page GoogleDialogflowCxFlow#target_page}
        '''
        result = self._values.get("target_page")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment"]:
        '''trigger_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#trigger_fulfillment GoogleDialogflowCxFlow#trigger_fulfillment}
        '''
        result = self._values.get("trigger_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowTransitionRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowTransitionRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c658a26b791ed47c005526f0d203bf77af0ce5f404c11ebc43fd87ecac58b40b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxFlowTransitionRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3785a2a26b46925c4961926dbf735621325bd370269361e64e4cae714adf64c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxFlowTransitionRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72390c857e2ae72ecbbe1a54bb412b4ff281d146112ca0926eef1c03e9ab9c40)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bef78f412e276f63bb4c9db73a3c134a65b4d12146688888d6a4695ad3ac274b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__be10637d5d8fa7172423bd8f96a2561a939265c1e9b1d560cbb735def4faa7a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4831c1a17de10c1ab5840826b85ccb8471666de0b3bafe39b6002b027cc2f31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowTransitionRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__48ac555298c8903d2371e18de384242e6abe071a26c75bfecc87cdb684fc1f5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTriggerFulfillment")
    def put_trigger_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        value = GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment(
            messages=messages,
            return_partial_responses=return_partial_responses,
            tag=tag,
            webhook=webhook,
        )

        return typing.cast(None, jsii.invoke(self, "putTriggerFulfillment", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetIntent")
    def reset_intent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntent", []))

    @jsii.member(jsii_name="resetTargetFlow")
    def reset_target_flow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetFlow", []))

    @jsii.member(jsii_name="resetTargetPage")
    def reset_target_page(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetPage", []))

    @jsii.member(jsii_name="resetTriggerFulfillment")
    def reset_trigger_fulfillment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggerFulfillment", []))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="triggerFulfillment")
    def trigger_fulfillment(
        self,
    ) -> "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentOutputReference":
        return typing.cast("GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentOutputReference", jsii.get(self, "triggerFulfillment"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="intentInput")
    def intent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intentInput"))

    @builtins.property
    @jsii.member(jsii_name="targetFlowInput")
    def target_flow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetFlowInput"))

    @builtins.property
    @jsii.member(jsii_name="targetPageInput")
    def target_page_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetPageInput"))

    @builtins.property
    @jsii.member(jsii_name="triggerFulfillmentInput")
    def trigger_fulfillment_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment"], jsii.get(self, "triggerFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76e46873b24a3efeb8ec6f6a61f81217f1e21900852c2da220810827b27be97d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value)

    @builtins.property
    @jsii.member(jsii_name="intent")
    def intent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intent"))

    @intent.setter
    def intent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7bbd5463bb362fe073852100eb5bc655db95f2128105531a3af0073f278523b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intent", value)

    @builtins.property
    @jsii.member(jsii_name="targetFlow")
    def target_flow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetFlow"))

    @target_flow.setter
    def target_flow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d249e51248c27f926d6d592e9b4877379d8f9d5c09d9cc691e3dc24dab1974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetFlow", value)

    @builtins.property
    @jsii.member(jsii_name="targetPage")
    def target_page(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetPage"))

    @target_page.setter
    def target_page(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ec782606f320f8dceb8e53942677095abfe92dc2acf5f176bf57abeb0a5f8ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPage", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c71428de0494ae2981349f4c2a95e9ba77bf5b1e6a1b3ec8c23594a99918944a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944315f63373bd1968029dfa9b00946a674228d84fcc82289742d14c69a9a569)
            check_type(argname="argument messages", value=messages, expected_type=type_hints["messages"])
            check_type(argname="argument return_partial_responses", value=return_partial_responses, expected_type=type_hints["return_partial_responses"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if messages is not None:
            self._values["messages"] = messages
        if return_partial_responses is not None:
            self._values["return_partial_responses"] = return_partial_responses
        if tag is not None:
            self._values["tag"] = tag
        if webhook is not None:
            self._values["webhook"] = webhook

    @builtins.property
    def messages(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#messages GoogleDialogflowCxFlow#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#return_partial_responses GoogleDialogflowCxFlow#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#tag GoogleDialogflowCxFlow#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#webhook GoogleDialogflowCxFlow#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65436ee4b59d66753768513811493c2a9d9e47b34fd247b3f479f85953b0e120)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7435871870af685282002420434c13db7b6579027b6925f2e68d8de4a5c3fc9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be189241fff7bf38c1fca21ad4f28dc6cccdf2f4f554aaea715de229737a76e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae7d59f0511c56d7eb840244429c79966ee48fc81349d5f84f2319907031903)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9a46f9994035fdfbc69bb83a7a8c239a963e6e9eecfe39d1df33a45f82ec229)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3eda6061a4d7d2bdf6484af0aac95aaeab9ba650ee6cb0480fade59673b8fade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a4af56b921e555a8e66e8345e3e8709927bd080ce8209d365603fa341a6b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e09d82d13a056100809df1747e9032e7cff75fcd0fd2e85fd7cac7fe514183f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putText")
    def put_text(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        value = GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText(
            text=text
        )

        return typing.cast(None, jsii.invoke(self, "putText", [value]))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(
        self,
    ) -> "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453d82510f9adc9db614143cd517ba4f565b2a6db300b9f8a6faedcdb1372282)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0153409442fb161b628945747122cdf8ddc6e15a3d6d3a0948bc10c7a26885f6)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_flow#text GoogleDialogflowCxFlow#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a06dd4513f065ad9309d0a96051645e8a1e25667073f4ca1e04b988bc1877e2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @builtins.property
    @jsii.member(jsii_name="allowPlaybackInterruption")
    def allow_playback_interruption(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "allowPlaybackInterruption"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "text"))

    @text.setter
    def text(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4129b5304583b960d5f0beec820380ae650c062c078679046d54b3e60db3a84c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50f2da856a359f6e13479ee354302498446f8687051668ea56ea87c957f0b2cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxFlow.GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7dbb19ced0b6c9b1d22198ba4a7f0983290defd105af87f66c03662cda69e461)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b0b934ff43ca7625a4f7b3d2b74223683bab64ed983cdb10e1e244620b05270)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMessages", [value]))

    @jsii.member(jsii_name="resetMessages")
    def reset_messages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessages", []))

    @jsii.member(jsii_name="resetReturnPartialResponses")
    def reset_return_partial_responses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReturnPartialResponses", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetWebhook")
    def reset_webhook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhook", []))

    @builtins.property
    @jsii.member(jsii_name="messages")
    def messages(
        self,
    ) -> GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]], jsii.get(self, "messagesInput"))

    @builtins.property
    @jsii.member(jsii_name="returnPartialResponsesInput")
    def return_partial_responses_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "returnPartialResponsesInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookInput")
    def webhook_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookInput"))

    @builtins.property
    @jsii.member(jsii_name="returnPartialResponses")
    def return_partial_responses(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "returnPartialResponses"))

    @return_partial_responses.setter
    def return_partial_responses(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bc3ed29a6fe1a6c56df7a77a6dafca943bcfc091afa8b6d48041ad775e8b814)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9f70849da3e966fdf6b96ed7433d72b3121157e46ef03cb37bcc66ac4dd2b01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeee2472db9caa2d47a89521789e8b35f36e94f69faeb5e8e3a183a96628c091)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__220977d5a118b7da09035631babbb52080bd1f81cc737ffa8743eebdfbed6d4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleDialogflowCxFlow",
    "GoogleDialogflowCxFlowConfig",
    "GoogleDialogflowCxFlowEventHandlers",
    "GoogleDialogflowCxFlowEventHandlersList",
    "GoogleDialogflowCxFlowEventHandlersOutputReference",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillment",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesList",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentOutputReference",
    "GoogleDialogflowCxFlowNluSettings",
    "GoogleDialogflowCxFlowNluSettingsOutputReference",
    "GoogleDialogflowCxFlowTimeouts",
    "GoogleDialogflowCxFlowTimeoutsOutputReference",
    "GoogleDialogflowCxFlowTransitionRoutes",
    "GoogleDialogflowCxFlowTransitionRoutesList",
    "GoogleDialogflowCxFlowTransitionRoutesOutputReference",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesList",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentOutputReference",
]

publication.publish()

def _typecheckingstub__8ddc1c9bd1aaab871a2b80768c2bc499e93a36227c2ec26b6797aac6fac61ceb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    display_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    language_code: typing.Optional[builtins.str] = None,
    nlu_settings: typing.Optional[typing.Union[GoogleDialogflowCxFlowNluSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    parent: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__7d5763a95f2a19a20a2cee1cd63b8e22e995b6ccdda0bc67f0a8ba7c9afea462(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f67d14e084641d1578e154aed126fcf46d108e0c8f21351b034db072abbe3b8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7564a7905ff3d080ec73fd5b3674d80316185888f34b793426007f2891348fc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d57e353ea4e0c1dbefde806a99b8c916a02fa1ed2fdd994823bfcf5422e9934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab5ec690ece1ff9fa75d59b2a15d2b7ececfba9a83206cd737e9f2f7198cb5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb70b48e85ea80ce1f103a0c05a4b3466c57a382c528c7a81ce07b3b8df410ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a48c675e5612a9b38a6595f66082b141506e7336639e253e7d20e4b003a2e87d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8b9d2da6f549846ac8b8c3ea7bb8b102639d483550c7cb5ff7fa1924d572b11(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b6d22821ccb6c1261edc07f6bc6656e98299156ae0eaee2da8542a3e22cb90(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    language_code: typing.Optional[builtins.str] = None,
    nlu_settings: typing.Optional[typing.Union[GoogleDialogflowCxFlowNluSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    parent: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98d6b437f59c96e369e9a65e8cba23f38e57df796929bbd75224bcedc388b721(
    *,
    event: typing.Optional[builtins.str] = None,
    target_flow: typing.Optional[builtins.str] = None,
    target_page: typing.Optional[builtins.str] = None,
    trigger_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ea6d2385130136ba9ba2449229da1e1d3e391e41dfafc4c8ca3bb1631d4ce14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b72692e2f83b58047d9ef491b2c6b8d6d65b1d0576f01c8e029ece54d7ca94a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10e47925b00e47f983de73bfa202626a1e3135e199f22fe97d586dabb330c1f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87ff1ba2605882bab6a41459482a8d5ce15d04140c213017f7aa60d0f1f8cd4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797650aaec31e7ca6bb8bc45d5cb90e35913ad807f256a34b97189d1d969d736(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550686a1780bbee4f9f8564add05760636a98a28cf7e02f3c02b086103f5e3dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b49a2bf192f63cb5a72c1bd7cdffb07f5cdb45767d0977c9c0af70fe72a68a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b6f23d473fdfa3616c5c573a6311ed0c64ca67237e5fc371844d19be8d4b06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8232a76d7dd21a85014f51ee2b25961374daa0e33aba5d27aed553abf55ee0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6d60b11ea63adf1c7be2210f0b5cecc0c0346fad1ab06f7f78bd60d2f16a37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b10706871c1d1f665ef2d90bd0d58a208650af42514f7be1dca25fb9f02432(
    value: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlers, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2b0b5e0e8e08564eff12bc1e01fd9807cb7a628d58f0aa0ac775e881f69e3fe(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47cf1b77ff3ec061bdddb90036c33368f3e5b8f584b5d70cb6c8d6c442148a4f(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a30f242e5ea4183f4a388675dae2a39a85ebb559121c69b38971a70ae0259b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef209c5de032bddd5d5f68a59e2625324e8d419c75f45bb6c212f1afcdcf5337(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb9eaee16e8332e5d899c05745620e138957c5e96c41b0be100922470cea560(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8df20db12f6bf4a2136b74d845969b82f6c72d29f3160edf5aaf3e9607405c84(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc59802a7434cb11ca69be912e59b031a4a61b4c64c7c3877cf2b86eedfb6dc5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66fc6f716cf1db773623fff9494d38d2fd97eaa1964cbad881bf5cb7c48ed834(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5d7394da129220d20cf2d3e9de1e4a8bc97cf36ff80f93157bd345d447f814(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33fd52d5aee1abc2af7510c2d810adabcf29a9323ff8a75fac9e0e5a9b3d8e2(
    value: typing.Optional[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caf968656644d2b99fc0f819ca3a16b23f096995475b7b3a6e08e5c1c1358318(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4ec1e46f38dd2a469bcfc5e0b204a6b11595e08e119b7981575105910d8c78d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__037aec295bb472f589ea596cbfebb45456ce81962af528f351d6b6e616e3b242(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__479b59249a9dfb3608d4dc0fed24b0337e07fe844e83827b6f943b301566db71(
    value: typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bad15ed6b01e2d0546b46b152ea04c1371cb3c7d4324e188ef4e47b66fade90(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42f5acfd4c64d5ac63b8f15f48c10d2fd9d8bc9b56ae86ee6bab6d18e6328278(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b357e6f9c60440207ddaad42c083f61899fd2ca2bcace2737949eb6ea6851467(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e50fe901dbf61aa635a56e265013a777da162a618815e4ec01998dc21f697c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bf4cce913b48aa52137ae8d78dc55d18dccf652b6d505fed4dc622a5a91a55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3744515a4e7ffc4c34a960ba8fd725e26afa66704674a5e14177efa17342c58(
    value: typing.Optional[GoogleDialogflowCxFlowEventHandlersTriggerFulfillment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e11d2415d17184287951f07c3c59b5989b582c6777731b857475cbefa2994ab9(
    *,
    classification_threshold: typing.Optional[jsii.Number] = None,
    model_training_mode: typing.Optional[builtins.str] = None,
    model_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98d9f3909bba7513ded942dd49ab4eff31602cdb034f4a4e1475a92d9195e3cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45305366a1d242576564cf317b03d1a334294e16921345b493918e93aecceff7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__536cbd1264bd06bfdfe3cee75d9622418afef8311158512d4f56b6ab9158e3f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe96da0683e88b188041d7de4c92fed18d30c2e19f30792d01ac81a7e8fc06f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524f25a80f58940c6773cd38d1d4a7c6ddb98c11023b57dd08686d71d4bec644(
    value: typing.Optional[GoogleDialogflowCxFlowNluSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0210a03cea17a8ef6bb6c8d12573cd1b0d7140688721c228c725071420680dd6(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e68db04b76164173d2591ddd75bb1b9b052a340e3f358976041e891232cfc2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c8fa4d3bd2d4d417cd91617f1a451745bf4aaf04d58d7966be4fba2c6597fe3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d5975630e9faa60ef9b199ec40a0b2873f5df8a921e7f852dabdc8a78073309(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e778f648906def1b0b98d5164ec361e201a715e15a0d72467b7788a670fc5c4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86c6d5b814a990c8b13a0674f1e520f123196a9fc67d10ff966cfed6d664ab5a(
    value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1a18960d79eb590c9d5bf3e090bd2e010515560266b7c63ff53264e0f013b1(
    *,
    condition: typing.Optional[builtins.str] = None,
    intent: typing.Optional[builtins.str] = None,
    target_flow: typing.Optional[builtins.str] = None,
    target_page: typing.Optional[builtins.str] = None,
    trigger_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c658a26b791ed47c005526f0d203bf77af0ce5f404c11ebc43fd87ecac58b40b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3785a2a26b46925c4961926dbf735621325bd370269361e64e4cae714adf64c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72390c857e2ae72ecbbe1a54bb412b4ff281d146112ca0926eef1c03e9ab9c40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef78f412e276f63bb4c9db73a3c134a65b4d12146688888d6a4695ad3ac274b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be10637d5d8fa7172423bd8f96a2561a939265c1e9b1d560cbb735def4faa7a2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4831c1a17de10c1ab5840826b85ccb8471666de0b3bafe39b6002b027cc2f31(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ac555298c8903d2371e18de384242e6abe071a26c75bfecc87cdb684fc1f5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76e46873b24a3efeb8ec6f6a61f81217f1e21900852c2da220810827b27be97d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7bbd5463bb362fe073852100eb5bc655db95f2128105531a3af0073f278523b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d249e51248c27f926d6d592e9b4877379d8f9d5c09d9cc691e3dc24dab1974(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec782606f320f8dceb8e53942677095abfe92dc2acf5f176bf57abeb0a5f8ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c71428de0494ae2981349f4c2a95e9ba77bf5b1e6a1b3ec8c23594a99918944a(
    value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutes, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944315f63373bd1968029dfa9b00946a674228d84fcc82289742d14c69a9a569(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65436ee4b59d66753768513811493c2a9d9e47b34fd247b3f479f85953b0e120(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7435871870af685282002420434c13db7b6579027b6925f2e68d8de4a5c3fc9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be189241fff7bf38c1fca21ad4f28dc6cccdf2f4f554aaea715de229737a76e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae7d59f0511c56d7eb840244429c79966ee48fc81349d5f84f2319907031903(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9a46f9994035fdfbc69bb83a7a8c239a963e6e9eecfe39d1df33a45f82ec229(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eda6061a4d7d2bdf6484af0aac95aaeab9ba650ee6cb0480fade59673b8fade(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a4af56b921e555a8e66e8345e3e8709927bd080ce8209d365603fa341a6b54(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e09d82d13a056100809df1747e9032e7cff75fcd0fd2e85fd7cac7fe514183f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453d82510f9adc9db614143cd517ba4f565b2a6db300b9f8a6faedcdb1372282(
    value: typing.Optional[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0153409442fb161b628945747122cdf8ddc6e15a3d6d3a0948bc10c7a26885f6(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a06dd4513f065ad9309d0a96051645e8a1e25667073f4ca1e04b988bc1877e2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4129b5304583b960d5f0beec820380ae650c062c078679046d54b3e60db3a84c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50f2da856a359f6e13479ee354302498446f8687051668ea56ea87c957f0b2cb(
    value: typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dbb19ced0b6c9b1d22198ba4a7f0983290defd105af87f66c03662cda69e461(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b0b934ff43ca7625a4f7b3d2b74223683bab64ed983cdb10e1e244620b05270(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bc3ed29a6fe1a6c56df7a77a6dafca943bcfc091afa8b6d48041ad775e8b814(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9f70849da3e966fdf6b96ed7433d72b3121157e46ef03cb37bcc66ac4dd2b01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeee2472db9caa2d47a89521789e8b35f36e94f69faeb5e8e3a183a96628c091(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__220977d5a118b7da09035631babbb52080bd1f81cc737ffa8743eebdfbed6d4b(
    value: typing.Optional[GoogleDialogflowCxFlowTransitionRoutesTriggerFulfillment],
) -> None:
    """Type checking stubs"""
    pass
