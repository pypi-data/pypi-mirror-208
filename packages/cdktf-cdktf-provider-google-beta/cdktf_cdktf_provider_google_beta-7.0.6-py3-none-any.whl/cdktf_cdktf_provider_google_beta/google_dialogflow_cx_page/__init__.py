'''
# `google_dialogflow_cx_page`

Refer to the Terraform Registory for docs: [`google_dialogflow_cx_page`](https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page).
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


class GoogleDialogflowCxPage(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPage",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page google_dialogflow_cx_page}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        display_name: builtins.str,
        entry_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxPageEntryFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
        event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEventHandlers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        form: typing.Optional[typing.Union["GoogleDialogflowCxPageForm", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        language_code: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxPageTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page google_dialogflow_cx_page} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: The human-readable name of the page, unique within the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#display_name GoogleDialogflowCxPage#display_name}
        :param entry_fulfillment: entry_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#entry_fulfillment GoogleDialogflowCxPage#entry_fulfillment}
        :param event_handlers: event_handlers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#event_handlers GoogleDialogflowCxPage#event_handlers}
        :param form: form block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#form GoogleDialogflowCxPage#form}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#id GoogleDialogflowCxPage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param language_code: The language of the following fields in page:. Page.entry_fulfillment.messages Page.entry_fulfillment.conditional_cases Page.event_handlers.trigger_fulfillment.messages Page.event_handlers.trigger_fulfillment.conditional_cases Page.form.parameters.fill_behavior.initial_prompt_fulfillment.messages Page.form.parameters.fill_behavior.initial_prompt_fulfillment.conditional_cases Page.form.parameters.fill_behavior.reprompt_event_handlers.messages Page.form.parameters.fill_behavior.reprompt_event_handlers.conditional_cases Page.transition_routes.trigger_fulfillment.messages Page.transition_routes.trigger_fulfillment.conditional_cases If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#language_code GoogleDialogflowCxPage#language_code}
        :param parent: The flow to create a page for. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parent GoogleDialogflowCxPage#parent}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#timeouts GoogleDialogflowCxPage#timeouts}
        :param transition_route_groups: Ordered list of TransitionRouteGroups associated with the page. Transition route groups must be unique within a page. If multiple transition routes within a page scope refer to the same intent, then the precedence order is: page's transition route -> page's transition route group -> flow's transition routes. If multiple transition route groups within a page contain the same intent, then the first group in the ordered list takes precedence. Format:projects//locations//agents//flows//transitionRouteGroups/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_route_groups GoogleDialogflowCxPage#transition_route_groups}
        :param transition_routes: transition_routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_routes GoogleDialogflowCxPage#transition_routes}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa27d49efbba1ea00521a9f443109dcd28de42f5b59cb6d6f0ce8b25ff7c268b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GoogleDialogflowCxPageConfig(
            display_name=display_name,
            entry_fulfillment=entry_fulfillment,
            event_handlers=event_handlers,
            form=form,
            id=id,
            language_code=language_code,
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

    @jsii.member(jsii_name="putEntryFulfillment")
    def put_entry_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEntryFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        value = GoogleDialogflowCxPageEntryFulfillment(
            messages=messages,
            return_partial_responses=return_partial_responses,
            tag=tag,
            webhook=webhook,
        )

        return typing.cast(None, jsii.invoke(self, "putEntryFulfillment", [value]))

    @jsii.member(jsii_name="putEventHandlers")
    def put_event_handlers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEventHandlers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ba3517d64fdf2fca2e47918a776b4443953ec591b16c78b2b7a95f3fedcfcc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEventHandlers", [value]))

    @jsii.member(jsii_name="putForm")
    def put_form(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageFormParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parameters GoogleDialogflowCxPage#parameters}
        '''
        value = GoogleDialogflowCxPageForm(parameters=parameters)

        return typing.cast(None, jsii.invoke(self, "putForm", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#create GoogleDialogflowCxPage#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#delete GoogleDialogflowCxPage#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#update GoogleDialogflowCxPage#update}.
        '''
        value = GoogleDialogflowCxPageTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTransitionRoutes")
    def put_transition_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__433b11e31597d90610c123ee594d153071015353b70bd429f648501f9d66fad4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTransitionRoutes", [value]))

    @jsii.member(jsii_name="resetEntryFulfillment")
    def reset_entry_fulfillment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntryFulfillment", []))

    @jsii.member(jsii_name="resetEventHandlers")
    def reset_event_handlers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventHandlers", []))

    @jsii.member(jsii_name="resetForm")
    def reset_form(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForm", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLanguageCode")
    def reset_language_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLanguageCode", []))

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
    @jsii.member(jsii_name="entryFulfillment")
    def entry_fulfillment(
        self,
    ) -> "GoogleDialogflowCxPageEntryFulfillmentOutputReference":
        return typing.cast("GoogleDialogflowCxPageEntryFulfillmentOutputReference", jsii.get(self, "entryFulfillment"))

    @builtins.property
    @jsii.member(jsii_name="eventHandlers")
    def event_handlers(self) -> "GoogleDialogflowCxPageEventHandlersList":
        return typing.cast("GoogleDialogflowCxPageEventHandlersList", jsii.get(self, "eventHandlers"))

    @builtins.property
    @jsii.member(jsii_name="form")
    def form(self) -> "GoogleDialogflowCxPageFormOutputReference":
        return typing.cast("GoogleDialogflowCxPageFormOutputReference", jsii.get(self, "form"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "GoogleDialogflowCxPageTimeoutsOutputReference":
        return typing.cast("GoogleDialogflowCxPageTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="transitionRoutes")
    def transition_routes(self) -> "GoogleDialogflowCxPageTransitionRoutesList":
        return typing.cast("GoogleDialogflowCxPageTransitionRoutesList", jsii.get(self, "transitionRoutes"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entryFulfillmentInput")
    def entry_fulfillment_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEntryFulfillment"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEntryFulfillment"], jsii.get(self, "entryFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="eventHandlersInput")
    def event_handlers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlers"]]], jsii.get(self, "eventHandlersInput"))

    @builtins.property
    @jsii.member(jsii_name="formInput")
    def form_input(self) -> typing.Optional["GoogleDialogflowCxPageForm"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageForm"], jsii.get(self, "formInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="languageCodeInput")
    def language_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "languageCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="parentInput")
    def parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["GoogleDialogflowCxPageTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["GoogleDialogflowCxPageTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutes"]]], jsii.get(self, "transitionRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3095fff2a743e43f1affedfc686528c1f19ba2a42226bafd22f8482350ad0b63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088098a68266cce8a55a3350e6b414b25d68438ef3422b866d3e1cf44c2a1839)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="languageCode")
    def language_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "languageCode"))

    @language_code.setter
    def language_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888ad87da498a4d8bbbe5610f2418bf09f5bd4c54e4a4f3ae466c48a88122b5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "languageCode", value)

    @builtins.property
    @jsii.member(jsii_name="parent")
    def parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parent"))

    @parent.setter
    def parent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45ed949c20a7ff8204168d0a97e07df974844fb0ff6f5bec1bcb84183ed55e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parent", value)

    @builtins.property
    @jsii.member(jsii_name="transitionRouteGroups")
    def transition_route_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "transitionRouteGroups"))

    @transition_route_groups.setter
    def transition_route_groups(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b13bef55feb004f0225337ebe385076dd52cd950027e158572491ff1bd41db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transitionRouteGroups", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageConfig",
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
        "entry_fulfillment": "entryFulfillment",
        "event_handlers": "eventHandlers",
        "form": "form",
        "id": "id",
        "language_code": "languageCode",
        "parent": "parent",
        "timeouts": "timeouts",
        "transition_route_groups": "transitionRouteGroups",
        "transition_routes": "transitionRoutes",
    },
)
class GoogleDialogflowCxPageConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        entry_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxPageEntryFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
        event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEventHandlers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        form: typing.Optional[typing.Union["GoogleDialogflowCxPageForm", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        language_code: typing.Optional[builtins.str] = None,
        parent: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["GoogleDialogflowCxPageTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageTransitionRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: The human-readable name of the page, unique within the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#display_name GoogleDialogflowCxPage#display_name}
        :param entry_fulfillment: entry_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#entry_fulfillment GoogleDialogflowCxPage#entry_fulfillment}
        :param event_handlers: event_handlers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#event_handlers GoogleDialogflowCxPage#event_handlers}
        :param form: form block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#form GoogleDialogflowCxPage#form}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#id GoogleDialogflowCxPage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param language_code: The language of the following fields in page:. Page.entry_fulfillment.messages Page.entry_fulfillment.conditional_cases Page.event_handlers.trigger_fulfillment.messages Page.event_handlers.trigger_fulfillment.conditional_cases Page.form.parameters.fill_behavior.initial_prompt_fulfillment.messages Page.form.parameters.fill_behavior.initial_prompt_fulfillment.conditional_cases Page.form.parameters.fill_behavior.reprompt_event_handlers.messages Page.form.parameters.fill_behavior.reprompt_event_handlers.conditional_cases Page.transition_routes.trigger_fulfillment.messages Page.transition_routes.trigger_fulfillment.conditional_cases If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#language_code GoogleDialogflowCxPage#language_code}
        :param parent: The flow to create a page for. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parent GoogleDialogflowCxPage#parent}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#timeouts GoogleDialogflowCxPage#timeouts}
        :param transition_route_groups: Ordered list of TransitionRouteGroups associated with the page. Transition route groups must be unique within a page. If multiple transition routes within a page scope refer to the same intent, then the precedence order is: page's transition route -> page's transition route group -> flow's transition routes. If multiple transition route groups within a page contain the same intent, then the first group in the ordered list takes precedence. Format:projects//locations//agents//flows//transitionRouteGroups/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_route_groups GoogleDialogflowCxPage#transition_route_groups}
        :param transition_routes: transition_routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_routes GoogleDialogflowCxPage#transition_routes}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(entry_fulfillment, dict):
            entry_fulfillment = GoogleDialogflowCxPageEntryFulfillment(**entry_fulfillment)
        if isinstance(form, dict):
            form = GoogleDialogflowCxPageForm(**form)
        if isinstance(timeouts, dict):
            timeouts = GoogleDialogflowCxPageTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e190216301b9a66ee192fdcf3b68b107ad73e910e04fff2054a96fba6e81c41)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument entry_fulfillment", value=entry_fulfillment, expected_type=type_hints["entry_fulfillment"])
            check_type(argname="argument event_handlers", value=event_handlers, expected_type=type_hints["event_handlers"])
            check_type(argname="argument form", value=form, expected_type=type_hints["form"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument language_code", value=language_code, expected_type=type_hints["language_code"])
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
        if entry_fulfillment is not None:
            self._values["entry_fulfillment"] = entry_fulfillment
        if event_handlers is not None:
            self._values["event_handlers"] = event_handlers
        if form is not None:
            self._values["form"] = form
        if id is not None:
            self._values["id"] = id
        if language_code is not None:
            self._values["language_code"] = language_code
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
        '''The human-readable name of the page, unique within the agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#display_name GoogleDialogflowCxPage#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entry_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEntryFulfillment"]:
        '''entry_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#entry_fulfillment GoogleDialogflowCxPage#entry_fulfillment}
        '''
        result = self._values.get("entry_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEntryFulfillment"], result)

    @builtins.property
    def event_handlers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlers"]]]:
        '''event_handlers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#event_handlers GoogleDialogflowCxPage#event_handlers}
        '''
        result = self._values.get("event_handlers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlers"]]], result)

    @builtins.property
    def form(self) -> typing.Optional["GoogleDialogflowCxPageForm"]:
        '''form block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#form GoogleDialogflowCxPage#form}
        '''
        result = self._values.get("form")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageForm"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#id GoogleDialogflowCxPage#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def language_code(self) -> typing.Optional[builtins.str]:
        '''The language of the following fields in page:.

        Page.entry_fulfillment.messages
        Page.entry_fulfillment.conditional_cases
        Page.event_handlers.trigger_fulfillment.messages
        Page.event_handlers.trigger_fulfillment.conditional_cases
        Page.form.parameters.fill_behavior.initial_prompt_fulfillment.messages
        Page.form.parameters.fill_behavior.initial_prompt_fulfillment.conditional_cases
        Page.form.parameters.fill_behavior.reprompt_event_handlers.messages
        Page.form.parameters.fill_behavior.reprompt_event_handlers.conditional_cases
        Page.transition_routes.trigger_fulfillment.messages
        Page.transition_routes.trigger_fulfillment.conditional_cases
        If not specified, the agent's default language is used. Many languages are supported. Note: languages must be enabled in the agent before they can be used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#language_code GoogleDialogflowCxPage#language_code}
        '''
        result = self._values.get("language_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[builtins.str]:
        '''The flow to create a page for. Format: projects//locations//agents//flows/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parent GoogleDialogflowCxPage#parent}
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["GoogleDialogflowCxPageTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#timeouts GoogleDialogflowCxPage#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageTimeouts"], result)

    @builtins.property
    def transition_route_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Ordered list of TransitionRouteGroups associated with the page.

        Transition route groups must be unique within a page.
        If multiple transition routes within a page scope refer to the same intent, then the precedence order is: page's transition route -> page's transition route group -> flow's transition routes.
        If multiple transition route groups within a page contain the same intent, then the first group in the ordered list takes precedence.
        Format:projects//locations//agents//flows//transitionRouteGroups/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_route_groups GoogleDialogflowCxPage#transition_route_groups}
        '''
        result = self._values.get("transition_route_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def transition_routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutes"]]]:
        '''transition_routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#transition_routes GoogleDialogflowCxPage#transition_routes}
        '''
        result = self._values.get("transition_routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxPageEntryFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEntryFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0b73091e737da317e34c5bca8984fdf93e62409d2f14c4c112539e1e8b64dc5)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEntryFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEntryFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEntryFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageEntryFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxPageEntryFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxPageEntryFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86e20728251b5c9506750b1f72693859053bdee38af1e580fac20726773f62e9)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEntryFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEntryFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEntryFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageEntryFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__44e23fb479d4bd41a454b39e772584c49139a30cb07177d75c683053187b3617)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageEntryFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72fc016b4c334b92b04943186faf28b30f5dbbfa051fc70fe1f6c2403410ddb5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageEntryFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df13f56691dd4636f8aab4f38183e5da2884777366e141ad7a2efcdba4178436)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e6a12b6c8b7252d78ec48ec901f0342c3bd53df14f3c576f08b02114087f528)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6321a7bfa3173ce68995c950cb3ced651536260bc9ef239957d047a5d2c9cfc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22eac4222953992540930346a469c6b55afd6e8155e01bb89b7512c9915dbd99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageEntryFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__832d5becff6de69ccb7f7d6bfd5f39cd3238a4f3fe57de44f17ae04d3ad18017)
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
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        value = GoogleDialogflowCxPageEntryFulfillmentMessagesText(text=text)

        return typing.cast(None, jsii.invoke(self, "putText", [value]))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(
        self,
    ) -> "GoogleDialogflowCxPageEntryFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxPageEntryFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEntryFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEntryFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aff1ce5daa27ff6c6ead7111fb4415dc2b1caad103ae46dc12c8d9d45e8e2b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageEntryFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9736b737f1c77b18a75fa73271f9c8fc1f7993ea87adc4ee4e7554f2c56d337)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEntryFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageEntryFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9e0526b3075dcf62b1bf428c7c8f2c79a1adc52b907ddaeacad4297f12733bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02b0d7a5b507e534b9792a3691508a191598deac1fab9aa6ea7665c6fe9e9021)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageEntryFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageEntryFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageEntryFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bba4df31c7cda5c0b3949adbb26c6ab3b4e3e50ed3c83c8f4a097a1d9afddd13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageEntryFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEntryFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67e27da1dbe65ca13164e3d3c2283db2f707c486e81e60cde81a59d58848eb0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c05818242c22c1f42ce7084df6c4216ed06d18025b07035918499a5eca65ec4)
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
    def messages(self) -> GoogleDialogflowCxPageEntryFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxPageEntryFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]], jsii.get(self, "messagesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3cb41ca47ddfa5e79efcafb77df1eb01a65670e28e557f5ad0ad9dea79684a26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61fab9fe54be530051aae26df29e1b39d6790ef09dec439a0d22fd11bb93f827)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b88ff346dddc6c3e9448a32f09e4f680e2c554ff32c61b4bd9784849ba0d9da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDialogflowCxPageEntryFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageEntryFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageEntryFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b91dd584e57906c390a2de6d692de17d0bd9e06a00e87afbb410847f91015bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlers",
    jsii_struct_bases=[],
    name_mapping={
        "event": "event",
        "target_flow": "targetFlow",
        "target_page": "targetPage",
        "trigger_fulfillment": "triggerFulfillment",
    },
)
class GoogleDialogflowCxPageEventHandlers:
    def __init__(
        self,
        *,
        event: typing.Optional[builtins.str] = None,
        target_flow: typing.Optional[builtins.str] = None,
        target_page: typing.Optional[builtins.str] = None,
        trigger_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxPageEventHandlersTriggerFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param event: The name of the event to handle. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#event GoogleDialogflowCxPage#event}
        :param target_flow: The target flow to transition to. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_flow GoogleDialogflowCxPage#target_flow}
        :param target_page: The target page to transition to. Format: projects//locations//agents//flows//pages/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_page GoogleDialogflowCxPage#target_page}
        :param trigger_fulfillment: trigger_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#trigger_fulfillment GoogleDialogflowCxPage#trigger_fulfillment}
        '''
        if isinstance(trigger_fulfillment, dict):
            trigger_fulfillment = GoogleDialogflowCxPageEventHandlersTriggerFulfillment(**trigger_fulfillment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ff18c18cf4061e393a60ccfc54d911a2bb6de09973c06cb6c7c83908275cc48)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#event GoogleDialogflowCxPage#event}
        '''
        result = self._values.get("event")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_flow(self) -> typing.Optional[builtins.str]:
        '''The target flow to transition to. Format: projects//locations//agents//flows/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_flow GoogleDialogflowCxPage#target_flow}
        '''
        result = self._values.get("target_flow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_page(self) -> typing.Optional[builtins.str]:
        '''The target page to transition to. Format: projects//locations//agents//flows//pages/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_page GoogleDialogflowCxPage#target_page}
        '''
        result = self._values.get("target_page")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillment"]:
        '''trigger_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#trigger_fulfillment GoogleDialogflowCxPage#trigger_fulfillment}
        '''
        result = self._values.get("trigger_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillment"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEventHandlers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageEventHandlersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5c63b6d1e4c47d8314ce3851ba51b99c0360b89a9db5bd8b67e46a4161f1eae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageEventHandlersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46b2f8174bfaeef1dfb9272305c94ded1fa661c3810ab84a45fa75c6b88375a9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageEventHandlersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__511484fbb108d08a6c6e4754d6f28a3e712359f6d3292e3665cdf9c02e0515e6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf1a7c681530b1e00a8d7e3a86fd40eeb38b20b6185df5cee37aeb35e0498c61)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd8c5ffd7c899e518c12ac06166272a1bac0093b25d35d2ef7610d19241e5a09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c928199f301add001f36c92fac31171c9828e1cac8772c5b9e82b1c48752fa02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageEventHandlersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f857e39b3c3097fa61102bc496e5637cb3b1b8571e0897a421327bd0e8becf8e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTriggerFulfillment")
    def put_trigger_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        value = GoogleDialogflowCxPageEventHandlersTriggerFulfillment(
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
    ) -> "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentOutputReference":
        return typing.cast("GoogleDialogflowCxPageEventHandlersTriggerFulfillmentOutputReference", jsii.get(self, "triggerFulfillment"))

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
    ) -> typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillment"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillment"], jsii.get(self, "triggerFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="event")
    def event(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "event"))

    @event.setter
    def event(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee9f9ea81f57f7f7254f649bf8ec886510060fb6601b410faefe43b4f67cd1dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "event", value)

    @builtins.property
    @jsii.member(jsii_name="targetFlow")
    def target_flow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetFlow"))

    @target_flow.setter
    def target_flow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae9e14859beed73e4ccec2f206f96b0dbfd75d222d4567712693eb137e39b5b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetFlow", value)

    @builtins.property
    @jsii.member(jsii_name="targetPage")
    def target_page(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetPage"))

    @target_page.setter
    def target_page(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a78c634cfb159e200a3ef32ee98fb93957d0adf9c4de662b649655ba0454b56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPage", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlers, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlers, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlers, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a46bd04ce82936f0541334d237cceb4f282eab56ab04ee55fbd4a7bb4f5d1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxPageEventHandlersTriggerFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__904446ec80c449fff0fb11c43806b378c10913301c2e9ad31f1041785c29aaeb)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEventHandlersTriggerFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea264e4bd815329d6815f2eefb5b59e96a036090385099b557374047dc07d45f)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d05e63615b0d8428662b53194b977b7f824bf91d1ac48f76fd8fe3044e65b74)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a87ab211a66e4af310cab1dd8e7498ce5b5044a417904f12c9faf0d12fb5d30d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__358a29301bd516f2291707116b14e637892eb0bd1b7679bfde652390b4d4cfc8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fce91e7de564bc5e85f9233d974a2aff2d79c5dad2a47b7cb263ab7502d61603)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21d822417dcfeee9ec9199e03e246771ac234940c98cca078c228ca5c7a294f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842194151669fd02c980733e2286bc6ce152f1ab600198738c3b4b63a33135e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f45be4bfec12024c0bd2d94316bd508958399a8d5e0ab1c7d7fc7174d0ce27bb)
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
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        value = GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText(
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
    ) -> "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c79169043da4442fbd92cff7ad9e1f40e56b19b112daf1ab6954fe1e0058cbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e1a69d011edd7f47a6101bd0ac1a50edf48ef341c208f2bf5db72e37c74c328)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__41a7fe81ed01786aaf222fd97ab048170a9b3a9a26d62c7552e3d823cd5597de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1eb18f756155ddd5bc644fecfd049186490c42ff0cca856163eeeec2060c6627)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba4b6c0164b98b2d83c9e8ba2e85edd4fa75e1ec73f4995823ca6bb8402f7183)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageEventHandlersTriggerFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageEventHandlersTriggerFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f6c522cfbe94177f08962e94d3ddf1ea6e3fd1a1f5ae79f029c81d9ecd83002)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7193193f5e497ec52055e8280ec779c11a7346342549ba13b058c4a70bdc6709)
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
    ) -> GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]], jsii.get(self, "messagesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0dcd8a07547f8fb685465859174791dc51fdb98839e298a79f32a06715e40fb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3d2208872eecb4c323a5bbe72b07d06319769ee65438e1567d2fa2408cfd65d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__099111708bbc06286f5b613d19f4e951e1348cd4050fe0215b529696a0340efe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49cacfbbbaf2033837ac798a8b0d02c959335400b5db6420dcf947430d116bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageForm",
    jsii_struct_bases=[],
    name_mapping={"parameters": "parameters"},
)
class GoogleDialogflowCxPageForm:
    def __init__(
        self,
        *,
        parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageFormParameters", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parameters GoogleDialogflowCxPage#parameters}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b200beef4f0f71997235ebf1440bd2ab98b551fea8e27cb83062cf08fc33e5da)
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def parameters(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParameters"]]]:
        '''parameters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#parameters GoogleDialogflowCxPage#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParameters"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageForm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageFormOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d1530cbddc377e2437d6b509471040877996a32910c311216c05ab0323d003b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageFormParameters", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afdbdb778df88bfdb3d16760b5aec220d9e3f6464622acb2897aac6d0e8be8f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "GoogleDialogflowCxPageFormParametersList":
        return typing.cast("GoogleDialogflowCxPageFormParametersList", jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParameters"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParameters"]]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GoogleDialogflowCxPageForm]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageForm], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageForm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7c438d15c683090beacc931e1e82bc2f87285fb3292f91d8e9105b91640f72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParameters",
    jsii_struct_bases=[],
    name_mapping={
        "display_name": "displayName",
        "entity_type": "entityType",
        "fill_behavior": "fillBehavior",
        "is_list": "isList",
        "redact": "redact",
        "required": "required",
    },
)
class GoogleDialogflowCxPageFormParameters:
    def __init__(
        self,
        *,
        display_name: typing.Optional[builtins.str] = None,
        entity_type: typing.Optional[builtins.str] = None,
        fill_behavior: typing.Optional[typing.Union["GoogleDialogflowCxPageFormParametersFillBehavior", typing.Dict[builtins.str, typing.Any]]] = None,
        is_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        redact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param display_name: The human-readable name of the parameter, unique within the form. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#display_name GoogleDialogflowCxPage#display_name}
        :param entity_type: The entity type of the parameter. Format: projects/-/locations/-/agents/-/entityTypes/ for system entity types (for example, projects/-/locations/-/agents/-/entityTypes/sys.date), or projects//locations//agents//entityTypes/ for developer entity types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#entity_type GoogleDialogflowCxPage#entity_type}
        :param fill_behavior: fill_behavior block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#fill_behavior GoogleDialogflowCxPage#fill_behavior}
        :param is_list: Indicates whether the parameter represents a list of values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#is_list GoogleDialogflowCxPage#is_list}
        :param redact: Indicates whether the parameter content should be redacted in log. If redaction is enabled, the parameter content will be replaced by parameter name during logging. Note: the parameter content is subject to redaction if either parameter level redaction or entity type level redaction is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#redact GoogleDialogflowCxPage#redact}
        :param required: Indicates whether the parameter is required. Optional parameters will not trigger prompts; however, they are filled if the user specifies them. Required parameters must be filled before form filling concludes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#required GoogleDialogflowCxPage#required}
        '''
        if isinstance(fill_behavior, dict):
            fill_behavior = GoogleDialogflowCxPageFormParametersFillBehavior(**fill_behavior)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92d63234623f762ea846796300e932968b8668174f4576ff78d60d9ac099c2c6)
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument entity_type", value=entity_type, expected_type=type_hints["entity_type"])
            check_type(argname="argument fill_behavior", value=fill_behavior, expected_type=type_hints["fill_behavior"])
            check_type(argname="argument is_list", value=is_list, expected_type=type_hints["is_list"])
            check_type(argname="argument redact", value=redact, expected_type=type_hints["redact"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if display_name is not None:
            self._values["display_name"] = display_name
        if entity_type is not None:
            self._values["entity_type"] = entity_type
        if fill_behavior is not None:
            self._values["fill_behavior"] = fill_behavior
        if is_list is not None:
            self._values["is_list"] = is_list
        if redact is not None:
            self._values["redact"] = redact
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''The human-readable name of the parameter, unique within the form.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#display_name GoogleDialogflowCxPage#display_name}
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_type(self) -> typing.Optional[builtins.str]:
        '''The entity type of the parameter.

        Format: projects/-/locations/-/agents/-/entityTypes/ for system entity types (for example, projects/-/locations/-/agents/-/entityTypes/sys.date), or projects//locations//agents//entityTypes/ for developer entity types.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#entity_type GoogleDialogflowCxPage#entity_type}
        '''
        result = self._values.get("entity_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fill_behavior(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageFormParametersFillBehavior"]:
        '''fill_behavior block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#fill_behavior GoogleDialogflowCxPage#fill_behavior}
        '''
        result = self._values.get("fill_behavior")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageFormParametersFillBehavior"], result)

    @builtins.property
    def is_list(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the parameter represents a list of values.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#is_list GoogleDialogflowCxPage#is_list}
        '''
        result = self._values.get("is_list")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def redact(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the parameter content should be redacted in log.

        If redaction is enabled, the parameter content will be replaced by parameter name during logging. Note: the parameter content is subject to redaction if either parameter level redaction or entity type level redaction is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#redact GoogleDialogflowCxPage#redact}
        '''
        result = self._values.get("redact")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the parameter is required.

        Optional parameters will not trigger prompts; however, they are filled if the user specifies them.
        Required parameters must be filled before form filling concludes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#required GoogleDialogflowCxPage#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageFormParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehavior",
    jsii_struct_bases=[],
    name_mapping={"initial_prompt_fulfillment": "initialPromptFulfillment"},
)
class GoogleDialogflowCxPageFormParametersFillBehavior:
    def __init__(
        self,
        *,
        initial_prompt_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param initial_prompt_fulfillment: initial_prompt_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#initial_prompt_fulfillment GoogleDialogflowCxPage#initial_prompt_fulfillment}
        '''
        if isinstance(initial_prompt_fulfillment, dict):
            initial_prompt_fulfillment = GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment(**initial_prompt_fulfillment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3282069c49297fd6ae0476beab84e9cb2582a17824cf80c8e6c38f31276738bf)
            check_type(argname="argument initial_prompt_fulfillment", value=initial_prompt_fulfillment, expected_type=type_hints["initial_prompt_fulfillment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if initial_prompt_fulfillment is not None:
            self._values["initial_prompt_fulfillment"] = initial_prompt_fulfillment

    @builtins.property
    def initial_prompt_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment"]:
        '''initial_prompt_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#initial_prompt_fulfillment GoogleDialogflowCxPage#initial_prompt_fulfillment}
        '''
        result = self._values.get("initial_prompt_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageFormParametersFillBehavior(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c89a58f1d05ca386a89bde202b3ac9aad70a17812e5f835f7d0b1c5236b5ff8e)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13dca645fc322714f96b1675dd944f68f57bc91c95ac4792f84e4d259e6df7ea)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__621117b009b9327a126b8da80ec3278d351da4201760c4f04f32df612202ba18)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d3c0add56baf8d1299c9195ef7fbed1e1e6b2e7f5aad4c9a6a77f63cd41342f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4bf764f19f19b44cd539ad9121ed73ec324f71744217a5a610980169f5276d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70d7cfeefad5392082159fd8ef3eaabdac12564ecce58be1d394c4c67117ff29)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df93dc2155fbfe2fea43a7cc762f1ae3006d9c7c0f3daeb5e7aabe3aba4dc9dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e40a4aa412d0fc49452157242e14b2c3a8f630d23294fca7d8d876723b9ff0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c076e9ff96c4443270ab00d554ef1a8adbd800aa199d48f73fcb3cc2c4a0ddeb)
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
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        value = GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText(
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
    ) -> "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7db989aa1e50e1721b78d68eaa5fd8c19a2d77d15c47d969c86f7533c76d7b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4422cbaed69eb787ab3f9fe8b5d49a0a245542dc2fc3f6c801ee78cb3ca33732)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40a6a85d47524fe844efb05239a11599fb5647173beb0619b6bd9365f707aa6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18bc96a6ae53e45fc5f34fc9d2069dc0c443d3fea8b33018f67613499dca9347)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__230499f67c026b25d63279ab21bf6af5d75fc5c62bcfbea0ab40e12faefecf38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd151e2c864891c5857f3478ed7715f11e7e561c8b001a4d5013fa9e744d9425)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9da9b877f50a7de24b9ebc7ecfe7700cc33cc251315c9c7c7466e9d82d80978a)
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
    ) -> GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]], jsii.get(self, "messagesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__a81022bad6e037adff64f6e8f957b582c41aeafffea7aa2d6506026533f8a3ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a3d140040f3f5424f023720a9a97f2f730cee663159ef6354d6b65b6de460f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ea708b308fccf499a85ed3a9366f467a614758b18c0fd67da5cf43ff24d9f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__950044c8a91bbbe041cfd61f3c74b8da54c316b2c12a78dd0af2414d8fea5514)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageFormParametersFillBehaviorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersFillBehaviorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__911a5baafd3828c6228aba925f0099f41d2d14e3a8452a7203ccc3a0fbe0f885)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putInitialPromptFulfillment")
    def put_initial_prompt_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        value = GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment(
            messages=messages,
            return_partial_responses=return_partial_responses,
            tag=tag,
            webhook=webhook,
        )

        return typing.cast(None, jsii.invoke(self, "putInitialPromptFulfillment", [value]))

    @jsii.member(jsii_name="resetInitialPromptFulfillment")
    def reset_initial_prompt_fulfillment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitialPromptFulfillment", []))

    @builtins.property
    @jsii.member(jsii_name="initialPromptFulfillment")
    def initial_prompt_fulfillment(
        self,
    ) -> GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentOutputReference:
        return typing.cast(GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentOutputReference, jsii.get(self, "initialPromptFulfillment"))

    @builtins.property
    @jsii.member(jsii_name="initialPromptFulfillmentInput")
    def initial_prompt_fulfillment_input(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment], jsii.get(self, "initialPromptFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf28855c9218e51829b51d71dc53a1d05bee83aadd277efdc274ed7ca7f9842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageFormParametersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0508a1c6636361cd153bd21cd5d794e7ac11400784a1ec9afb0b8fe9bb4d618e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageFormParametersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9329146099088c92e3a6e1c7050ca7d5f138b9d8f9cfb52cae0b33b878cebb5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageFormParametersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d866df6245cc86622ecf96869ec5798491c297d6258926edf448b8c068ae7e88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__94a8937a9e887af24bcdbbbe7f0d8372f73ebe2259d2394c1f2273c34c058cba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60b614ef78a07f047d38ffd7d029a9b0e18a66b93a1f43e80986272f8ff7d718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParameters]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParameters]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParameters]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd2ddea2fecd5bb13a2b0e0eec414d29a02da783a155fec598f1de1befa2087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageFormParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageFormParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a12f79dab109863b9379834b53f59fa98749c71c7f1644bd35f10c722938508a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFillBehavior")
    def put_fill_behavior(
        self,
        *,
        initial_prompt_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param initial_prompt_fulfillment: initial_prompt_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#initial_prompt_fulfillment GoogleDialogflowCxPage#initial_prompt_fulfillment}
        '''
        value = GoogleDialogflowCxPageFormParametersFillBehavior(
            initial_prompt_fulfillment=initial_prompt_fulfillment
        )

        return typing.cast(None, jsii.invoke(self, "putFillBehavior", [value]))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetEntityType")
    def reset_entity_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityType", []))

    @jsii.member(jsii_name="resetFillBehavior")
    def reset_fill_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFillBehavior", []))

    @jsii.member(jsii_name="resetIsList")
    def reset_is_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsList", []))

    @jsii.member(jsii_name="resetRedact")
    def reset_redact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedact", []))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="fillBehavior")
    def fill_behavior(
        self,
    ) -> GoogleDialogflowCxPageFormParametersFillBehaviorOutputReference:
        return typing.cast(GoogleDialogflowCxPageFormParametersFillBehaviorOutputReference, jsii.get(self, "fillBehavior"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityTypeInput")
    def entity_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="fillBehaviorInput")
    def fill_behavior_input(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior], jsii.get(self, "fillBehaviorInput"))

    @builtins.property
    @jsii.member(jsii_name="isListInput")
    def is_list_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isListInput"))

    @builtins.property
    @jsii.member(jsii_name="redactInput")
    def redact_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "redactInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6e1c8c2e9222065c239fa8b436faf2995d501ab42114254684e5a4b0bb5d470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value)

    @builtins.property
    @jsii.member(jsii_name="entityType")
    def entity_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityType"))

    @entity_type.setter
    def entity_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4441d3541de006b9448d445abf9d3e96bc4a441d50b3537bb79f25b0950469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityType", value)

    @builtins.property
    @jsii.member(jsii_name="isList")
    def is_list(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isList"))

    @is_list.setter
    def is_list(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f9c830a5333d7044c9979dfb1b107ad1a44d5948f281b9fb169fae76bf767c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isList", value)

    @builtins.property
    @jsii.member(jsii_name="redact")
    def redact(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "redact"))

    @redact.setter
    def redact(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fe42de499c2c962aec8424fb00f15fb639a84ad3e544128333db1eef0eab6ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redact", value)

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aef677e0e1238125f516ced034367e330a0eae20e9dccd03684083afab0ae317)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageFormParameters, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageFormParameters, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParameters, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c41df8879f72bd59dd7af061d5c71a66b402d335b1a012f3c7fe8e5ca859da00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class GoogleDialogflowCxPageTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#create GoogleDialogflowCxPage#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#delete GoogleDialogflowCxPage#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#update GoogleDialogflowCxPage#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__876905772bc4d2e7d59731cb283d554ebee024f72a8eb7f8ff748d1de477e00e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#create GoogleDialogflowCxPage#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#delete GoogleDialogflowCxPage#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#update GoogleDialogflowCxPage#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__196c7206d9c119cff8e589e19c9bdd72f9aa9f1082e3249aa8fade43a7e80a00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b815753f2069b089fe57addcd590834be9ad89d28be3f9edcc26a4644c362167)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c16fceeb245820fead4197b4f691f3e5aa9979057415e650e1e4ccb6a08839f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aedae3215f64d103065e24572dca4ce5b44419524cb4e13d823ce74ab5c33cfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__583a2086c5e5972d3107e3c8f1e03b23732932633e59858c18964633b6c2620c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutes",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "intent": "intent",
        "target_flow": "targetFlow",
        "target_page": "targetPage",
        "trigger_fulfillment": "triggerFulfillment",
    },
)
class GoogleDialogflowCxPageTransitionRoutes:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        intent: typing.Optional[builtins.str] = None,
        target_flow: typing.Optional[builtins.str] = None,
        target_page: typing.Optional[builtins.str] = None,
        trigger_fulfillment: typing.Optional[typing.Union["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: The condition to evaluate against form parameters or session parameters. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#condition GoogleDialogflowCxPage#condition}
        :param intent: The unique identifier of an Intent. Format: projects//locations//agents//intents/. Indicates that the transition can only happen when the given intent is matched. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#intent GoogleDialogflowCxPage#intent}
        :param target_flow: The target flow to transition to. Format: projects//locations//agents//flows/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_flow GoogleDialogflowCxPage#target_flow}
        :param target_page: The target page to transition to. Format: projects//locations//agents//flows//pages/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_page GoogleDialogflowCxPage#target_page}
        :param trigger_fulfillment: trigger_fulfillment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#trigger_fulfillment GoogleDialogflowCxPage#trigger_fulfillment}
        '''
        if isinstance(trigger_fulfillment, dict):
            trigger_fulfillment = GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment(**trigger_fulfillment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bdba303ffb3a5ae0cae7a885479cddbeff4a780b39d9bfb48c11eb2e46e219e)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#condition GoogleDialogflowCxPage#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def intent(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of an Intent.

        Format: projects//locations//agents//intents/. Indicates that the transition can only happen when the given intent is matched. At least one of intent or condition must be specified. When both intent and condition are specified, the transition can only happen when both are fulfilled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#intent GoogleDialogflowCxPage#intent}
        '''
        result = self._values.get("intent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_flow(self) -> typing.Optional[builtins.str]:
        '''The target flow to transition to. Format: projects//locations//agents//flows/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_flow GoogleDialogflowCxPage#target_flow}
        '''
        result = self._values.get("target_flow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_page(self) -> typing.Optional[builtins.str]:
        '''The target page to transition to. Format: projects//locations//agents//flows//pages/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#target_page GoogleDialogflowCxPage#target_page}
        '''
        result = self._values.get("target_page")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger_fulfillment(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment"]:
        '''trigger_fulfillment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#trigger_fulfillment GoogleDialogflowCxPage#trigger_fulfillment}
        '''
        result = self._values.get("trigger_fulfillment")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageTransitionRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageTransitionRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fcad1ccd1690a777ec603990e09c68572b548c019611a5167bed8df8972be5d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageTransitionRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b236e3f9344d2b7d9206a0adccead7dca09ceacf6109ded6e7416dfb7e0305c2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageTransitionRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d9b7879ab0be41bd390702b6002d3d38f0b6226f35f917ea3f056585bad161)
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
            type_hints = typing.get_type_hints(_typecheckingstub__528fc146cac0fc1586e9307b0a6f61fde381d8985887bf44b932fba2546a5838)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0a241bc7b6bf62a6c6d5f4353fbdf8f93c8226864ecc9fe01ae78ead5bc71c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3037f47c00fcbc1d674ba694c8fa4dae2fd3a3c9ffb14516b2de32812c6f224f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageTransitionRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0ff8dfe876bd230eb009d84f34c308e05dfe3fcf2f02654fc4ed40ac1d714b6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTriggerFulfillment")
    def put_trigger_fulfillment(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        value = GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment(
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
    ) -> "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentOutputReference":
        return typing.cast("GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentOutputReference", jsii.get(self, "triggerFulfillment"))

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
    ) -> typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment"], jsii.get(self, "triggerFulfillmentInput"))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7da3b8a18f90064175405fe3e93306ff230b7b12c8ee1fe04245701d72942b5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "condition", value)

    @builtins.property
    @jsii.member(jsii_name="intent")
    def intent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intent"))

    @intent.setter
    def intent(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa5249f307c950682b9b9ac75b2e3b6c4ea1fc787685a16a446223398f45c6c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intent", value)

    @builtins.property
    @jsii.member(jsii_name="targetFlow")
    def target_flow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetFlow"))

    @target_flow.setter
    def target_flow(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60bb28468aa90b9930ec011d8ea636224f3796e6d450b8bfd4824ff439016f46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetFlow", value)

    @builtins.property
    @jsii.member(jsii_name="targetPage")
    def target_page(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetPage"))

    @target_page.setter
    def target_page(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b9e772cdcb8a268b71d08906588fb3e8782dd22ddf7402b0757bb51a73d59b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPage", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutes, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutes, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutes, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fbaf17e27fd3029c935810f35ea810e5a2419bbb7e157d0b222c0d401d65c2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment",
    jsii_struct_bases=[],
    name_mapping={
        "messages": "messages",
        "return_partial_responses": "returnPartialResponses",
        "tag": "tag",
        "webhook": "webhook",
    },
)
class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment:
    def __init__(
        self,
        *,
        messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag: typing.Optional[builtins.str] = None,
        webhook: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param messages: messages block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        :param return_partial_responses: Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs. If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        :param tag: The tag used by the webhook to identify which fulfillment is being called. This field is required if webhook is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        :param webhook: The webhook to call. Format: projects//locations//agents//webhooks/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a316694886a01524cb8019ef59a9e0b8930f9dafb570dc9612708a995c1bc07a)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages"]]]:
        '''messages block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#messages GoogleDialogflowCxPage#messages}
        '''
        result = self._values.get("messages")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages"]]], result)

    @builtins.property
    def return_partial_responses(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Dialogflow should return currently queued fulfillment response messages in streaming APIs.

        If a webhook is specified, it happens before Dialogflow invokes webhook. Warning: 1) This flag only affects streaming API. Responses are still queued and returned once in non-streaming API. 2) The flag can be enabled in any fulfillment but only the first 3 partial responses will be returned. You may only want to apply it to fulfillments that have slow webhooks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#return_partial_responses GoogleDialogflowCxPage#return_partial_responses}
        '''
        result = self._values.get("return_partial_responses")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The tag used by the webhook to identify which fulfillment is being called.

        This field is required if webhook is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#tag GoogleDialogflowCxPage#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.str]:
        '''The webhook to call. Format: projects//locations//agents//webhooks/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#webhook GoogleDialogflowCxPage#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Union["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param text: text block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if isinstance(text, dict):
            text = GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText(**text)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52ac2780428e2c00fd753706d2948b221a0fb1114f48449f6235a8af355bbfd6)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText"]:
        '''text block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e7cc5ba1aa62d842918faf33c8800bacf82fb8e7ff44537226e0bf7d9bcbdc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574ad5b337663c95bce4aef3460ab75477d6eb1edce1ef341f73fc5d7e990880)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f6e09150a3d3ed435b615088c06d3551c87557b225b427f3ca9802f47dd41f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__157dda77c11e6da3754da606b4b323ccfd4fdfb24f9d9824f349330f7d9da877)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a402e1f04dcfaaec90f1f60eb8a1442093e08ba77887ff8974906e35d1b8011c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f4e72346a91b536c015b895a8338d3079bdae76a435e4cbba1b9fc2d574d773)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6482e4b570a27bc6b524fd8b6b007d91bab382a7d99d27fbc66048eba38fe300)
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
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        value = GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText(
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
    ) -> "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesTextOutputReference":
        return typing.cast("GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesTextOutputReference", jsii.get(self, "text"))

    @builtins.property
    @jsii.member(jsii_name="textInput")
    def text_input(
        self,
    ) -> typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText"]:
        return typing.cast(typing.Optional["GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText"], jsii.get(self, "textInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70b35bab381880b5efa543830687e229ca026b4a9450e82c6741604bf00dbc1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText",
    jsii_struct_bases=[],
    name_mapping={"text": "text"},
)
class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText:
    def __init__(
        self,
        *,
        text: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param text: A collection of text responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38b3a1c0c7435d5d96729f38134b96ae45ace916b69e9be893324b4b85e4a7a)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if text is not None:
            self._values["text"] = text

    @builtins.property
    def text(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of text responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/google-beta/4.65.2/docs/resources/google_dialogflow_cx_page#text GoogleDialogflowCxPage#text}
        '''
        result = self._values.get("text")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesTextOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesTextOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f3db04f8ef449258ace9f14cc9d1a9d64856dbb845e0f3c016b269709021291)
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
            type_hints = typing.get_type_hints(_typecheckingstub__684b3f22c566cc5c2fabac255e21d408d12f8b315be171d9474d948c2daa0f0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11574cf51692340e2cae4e14498bf419c7e8ba2f79b2027b7836e6c9c865185b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-google-beta.googleDialogflowCxPage.GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c6a9d24ca199089776c22d49293073daefd976437a3df271d6b0e4310cd3896)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMessages")
    def put_messages(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5da5e882870d7a1d55d485ba6c48898c4114110fe826e3e6fa691af8010c067)
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
    ) -> GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesList:
        return typing.cast(GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesList, jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="messagesInput")
    def messages_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]], jsii.get(self, "messagesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__073d56e65ea59f7e368100e36ae4bbd71658e23b11169eb4420d1c1a7290c0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnPartialResponses", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e6668ef2abecdf3db5dec8c1c4b6358e6bcf8bbab853666e9686f8e14a536b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c981bc1cbbb9a1d369e902ca211ca8f40619905c509ff187e2559b9dc141eaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment]:
        return typing.cast(typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bbca2e3cde617d92d1803c7bc65e12fa452f61355d41bbabdfd11771d891a04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "GoogleDialogflowCxPage",
    "GoogleDialogflowCxPageConfig",
    "GoogleDialogflowCxPageEntryFulfillment",
    "GoogleDialogflowCxPageEntryFulfillmentMessages",
    "GoogleDialogflowCxPageEntryFulfillmentMessagesList",
    "GoogleDialogflowCxPageEntryFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxPageEntryFulfillmentMessagesText",
    "GoogleDialogflowCxPageEntryFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxPageEntryFulfillmentOutputReference",
    "GoogleDialogflowCxPageEventHandlers",
    "GoogleDialogflowCxPageEventHandlersList",
    "GoogleDialogflowCxPageEventHandlersOutputReference",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillment",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesList",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxPageEventHandlersTriggerFulfillmentOutputReference",
    "GoogleDialogflowCxPageForm",
    "GoogleDialogflowCxPageFormOutputReference",
    "GoogleDialogflowCxPageFormParameters",
    "GoogleDialogflowCxPageFormParametersFillBehavior",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesList",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentOutputReference",
    "GoogleDialogflowCxPageFormParametersFillBehaviorOutputReference",
    "GoogleDialogflowCxPageFormParametersList",
    "GoogleDialogflowCxPageFormParametersOutputReference",
    "GoogleDialogflowCxPageTimeouts",
    "GoogleDialogflowCxPageTimeoutsOutputReference",
    "GoogleDialogflowCxPageTransitionRoutes",
    "GoogleDialogflowCxPageTransitionRoutesList",
    "GoogleDialogflowCxPageTransitionRoutesOutputReference",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesList",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesOutputReference",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesTextOutputReference",
    "GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentOutputReference",
]

publication.publish()

def _typecheckingstub__fa27d49efbba1ea00521a9f443109dcd28de42f5b59cb6d6f0ce8b25ff7c268b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    display_name: builtins.str,
    entry_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
    event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    form: typing.Optional[typing.Union[GoogleDialogflowCxPageForm, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    language_code: typing.Optional[builtins.str] = None,
    parent: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__0ba3517d64fdf2fca2e47918a776b4443953ec591b16c78b2b7a95f3fedcfcc8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__433b11e31597d90610c123ee594d153071015353b70bd429f648501f9d66fad4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3095fff2a743e43f1affedfc686528c1f19ba2a42226bafd22f8482350ad0b63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__088098a68266cce8a55a3350e6b414b25d68438ef3422b866d3e1cf44c2a1839(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888ad87da498a4d8bbbe5610f2418bf09f5bd4c54e4a4f3ae466c48a88122b5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45ed949c20a7ff8204168d0a97e07df974844fb0ff6f5bec1bcb84183ed55e09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b13bef55feb004f0225337ebe385076dd52cd950027e158572491ff1bd41db(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e190216301b9a66ee192fdcf3b68b107ad73e910e04fff2054a96fba6e81c41(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: builtins.str,
    entry_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
    event_handlers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    form: typing.Optional[typing.Union[GoogleDialogflowCxPageForm, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    language_code: typing.Optional[builtins.str] = None,
    parent: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_route_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    transition_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b73091e737da317e34c5bca8984fdf93e62409d2f14c4c112539e1e8b64dc5(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86e20728251b5c9506750b1f72693859053bdee38af1e580fac20726773f62e9(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44e23fb479d4bd41a454b39e772584c49139a30cb07177d75c683053187b3617(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72fc016b4c334b92b04943186faf28b30f5dbbfa051fc70fe1f6c2403410ddb5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df13f56691dd4636f8aab4f38183e5da2884777366e141ad7a2efcdba4178436(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e6a12b6c8b7252d78ec48ec901f0342c3bd53df14f3c576f08b02114087f528(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6321a7bfa3173ce68995c950cb3ced651536260bc9ef239957d047a5d2c9cfc8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22eac4222953992540930346a469c6b55afd6e8155e01bb89b7512c9915dbd99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEntryFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__832d5becff6de69ccb7f7d6bfd5f39cd3238a4f3fe57de44f17ae04d3ad18017(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aff1ce5daa27ff6c6ead7111fb4415dc2b1caad103ae46dc12c8d9d45e8e2b7(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9736b737f1c77b18a75fa73271f9c8fc1f7993ea87adc4ee4e7554f2c56d337(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9e0526b3075dcf62b1bf428c7c8f2c79a1adc52b907ddaeacad4297f12733bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b0d7a5b507e534b9792a3691508a191598deac1fab9aa6ea7665c6fe9e9021(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bba4df31c7cda5c0b3949adbb26c6ab3b4e3e50ed3c83c8f4a097a1d9afddd13(
    value: typing.Optional[GoogleDialogflowCxPageEntryFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e27da1dbe65ca13164e3d3c2283db2f707c486e81e60cde81a59d58848eb0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c05818242c22c1f42ce7084df6c4216ed06d18025b07035918499a5eca65ec4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEntryFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cb41ca47ddfa5e79efcafb77df1eb01a65670e28e557f5ad0ad9dea79684a26(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61fab9fe54be530051aae26df29e1b39d6790ef09dec439a0d22fd11bb93f827(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b88ff346dddc6c3e9448a32f09e4f680e2c554ff32c61b4bd9784849ba0d9da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b91dd584e57906c390a2de6d692de17d0bd9e06a00e87afbb410847f91015bae(
    value: typing.Optional[GoogleDialogflowCxPageEntryFulfillment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ff18c18cf4061e393a60ccfc54d911a2bb6de09973c06cb6c7c83908275cc48(
    *,
    event: typing.Optional[builtins.str] = None,
    target_flow: typing.Optional[builtins.str] = None,
    target_page: typing.Optional[builtins.str] = None,
    trigger_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c63b6d1e4c47d8314ce3851ba51b99c0360b89a9db5bd8b67e46a4161f1eae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46b2f8174bfaeef1dfb9272305c94ded1fa661c3810ab84a45fa75c6b88375a9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__511484fbb108d08a6c6e4754d6f28a3e712359f6d3292e3665cdf9c02e0515e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf1a7c681530b1e00a8d7e3a86fd40eeb38b20b6185df5cee37aeb35e0498c61(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd8c5ffd7c899e518c12ac06166272a1bac0093b25d35d2ef7610d19241e5a09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c928199f301add001f36c92fac31171c9828e1cac8772c5b9e82b1c48752fa02(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f857e39b3c3097fa61102bc496e5637cb3b1b8571e0897a421327bd0e8becf8e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9f9ea81f57f7f7254f649bf8ec886510060fb6601b410faefe43b4f67cd1dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae9e14859beed73e4ccec2f206f96b0dbfd75d222d4567712693eb137e39b5b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a78c634cfb159e200a3ef32ee98fb93957d0adf9c4de662b649655ba0454b56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a46bd04ce82936f0541334d237cceb4f282eab56ab04ee55fbd4a7bb4f5d1b(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlers, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__904446ec80c449fff0fb11c43806b378c10913301c2e9ad31f1041785c29aaeb(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea264e4bd815329d6815f2eefb5b59e96a036090385099b557374047dc07d45f(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d05e63615b0d8428662b53194b977b7f824bf91d1ac48f76fd8fe3044e65b74(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87ab211a66e4af310cab1dd8e7498ce5b5044a417904f12c9faf0d12fb5d30d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__358a29301bd516f2291707116b14e637892eb0bd1b7679bfde652390b4d4cfc8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fce91e7de564bc5e85f9233d974a2aff2d79c5dad2a47b7cb263ab7502d61603(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21d822417dcfeee9ec9199e03e246771ac234940c98cca078c228ca5c7a294f8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842194151669fd02c980733e2286bc6ce152f1ab600198738c3b4b63a33135e2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f45be4bfec12024c0bd2d94316bd508958399a8d5e0ab1c7d7fc7174d0ce27bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c79169043da4442fbd92cff7ad9e1f40e56b19b112daf1ab6954fe1e0058cbe(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1a69d011edd7f47a6101bd0ac1a50edf48ef341c208f2bf5db72e37c74c328(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a7fe81ed01786aaf222fd97ab048170a9b3a9a26d62c7552e3d823cd5597de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb18f756155ddd5bc644fecfd049186490c42ff0cca856163eeeec2060c6627(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba4b6c0164b98b2d83c9e8ba2e85edd4fa75e1ec73f4995823ca6bb8402f7183(
    value: typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6c522cfbe94177f08962e94d3ddf1ea6e3fd1a1f5ae79f029c81d9ecd83002(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7193193f5e497ec52055e8280ec779c11a7346342549ba13b058c4a70bdc6709(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageEventHandlersTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dcd8a07547f8fb685465859174791dc51fdb98839e298a79f32a06715e40fb4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3d2208872eecb4c323a5bbe72b07d06319769ee65438e1567d2fa2408cfd65d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__099111708bbc06286f5b613d19f4e951e1348cd4050fe0215b529696a0340efe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49cacfbbbaf2033837ac798a8b0d02c959335400b5db6420dcf947430d116bef(
    value: typing.Optional[GoogleDialogflowCxPageEventHandlersTriggerFulfillment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b200beef4f0f71997235ebf1440bd2ab98b551fea8e27cb83062cf08fc33e5da(
    *,
    parameters: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParameters, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d1530cbddc377e2437d6b509471040877996a32910c311216c05ab0323d003b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afdbdb778df88bfdb3d16760b5aec220d9e3f6464622acb2897aac6d0e8be8f0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParameters, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7c438d15c683090beacc931e1e82bc2f87285fb3292f91d8e9105b91640f72(
    value: typing.Optional[GoogleDialogflowCxPageForm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d63234623f762ea846796300e932968b8668174f4576ff78d60d9ac099c2c6(
    *,
    display_name: typing.Optional[builtins.str] = None,
    entity_type: typing.Optional[builtins.str] = None,
    fill_behavior: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehavior, typing.Dict[builtins.str, typing.Any]]] = None,
    is_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    redact: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3282069c49297fd6ae0476beab84e9cb2582a17824cf80c8e6c38f31276738bf(
    *,
    initial_prompt_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c89a58f1d05ca386a89bde202b3ac9aad70a17812e5f835f7d0b1c5236b5ff8e(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13dca645fc322714f96b1675dd944f68f57bc91c95ac4792f84e4d259e6df7ea(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__621117b009b9327a126b8da80ec3278d351da4201760c4f04f32df612202ba18(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d3c0add56baf8d1299c9195ef7fbed1e1e6b2e7f5aad4c9a6a77f63cd41342f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4bf764f19f19b44cd539ad9121ed73ec324f71744217a5a610980169f5276d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d7cfeefad5392082159fd8ef3eaabdac12564ecce58be1d394c4c67117ff29(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df93dc2155fbfe2fea43a7cc762f1ae3006d9c7c0f3daeb5e7aabe3aba4dc9dc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88e40a4aa412d0fc49452157242e14b2c3a8f630d23294fca7d8d876723b9ff0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c076e9ff96c4443270ab00d554ef1a8adbd800aa199d48f73fcb3cc2c4a0ddeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7db989aa1e50e1721b78d68eaa5fd8c19a2d77d15c47d969c86f7533c76d7b9(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4422cbaed69eb787ab3f9fe8b5d49a0a245542dc2fc3f6c801ee78cb3ca33732(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40a6a85d47524fe844efb05239a11599fb5647173beb0619b6bd9365f707aa6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18bc96a6ae53e45fc5f34fc9d2069dc0c443d3fea8b33018f67613499dca9347(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230499f67c026b25d63279ab21bf6af5d75fc5c62bcfbea0ab40e12faefecf38(
    value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd151e2c864891c5857f3478ed7715f11e7e561c8b001a4d5013fa9e744d9425(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9da9b877f50a7de24b9ebc7ecfe7700cc33cc251315c9c7c7466e9d82d80978a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81022bad6e037adff64f6e8f957b582c41aeafffea7aa2d6506026533f8a3ff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a3d140040f3f5424f023720a9a97f2f730cee663159ef6354d6b65b6de460f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ea708b308fccf499a85ed3a9366f467a614758b18c0fd67da5cf43ff24d9f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__950044c8a91bbbe041cfd61f3c74b8da54c316b2c12a78dd0af2414d8fea5514(
    value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehaviorInitialPromptFulfillment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__911a5baafd3828c6228aba925f0099f41d2d14e3a8452a7203ccc3a0fbe0f885(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf28855c9218e51829b51d71dc53a1d05bee83aadd277efdc274ed7ca7f9842(
    value: typing.Optional[GoogleDialogflowCxPageFormParametersFillBehavior],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0508a1c6636361cd153bd21cd5d794e7ac11400784a1ec9afb0b8fe9bb4d618e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9329146099088c92e3a6e1c7050ca7d5f138b9d8f9cfb52cae0b33b878cebb5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d866df6245cc86622ecf96869ec5798491c297d6258926edf448b8c068ae7e88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a8937a9e887af24bcdbbbe7f0d8372f73ebe2259d2394c1f2273c34c058cba(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60b614ef78a07f047d38ffd7d029a9b0e18a66b93a1f43e80986272f8ff7d718(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd2ddea2fecd5bb13a2b0e0eec414d29a02da783a155fec598f1de1befa2087(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageFormParameters]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a12f79dab109863b9379834b53f59fa98749c71c7f1644bd35f10c722938508a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6e1c8c2e9222065c239fa8b436faf2995d501ab42114254684e5a4b0bb5d470(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4441d3541de006b9448d445abf9d3e96bc4a441d50b3537bb79f25b0950469(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f9c830a5333d7044c9979dfb1b107ad1a44d5948f281b9fb169fae76bf767c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fe42de499c2c962aec8424fb00f15fb639a84ad3e544128333db1eef0eab6ce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aef677e0e1238125f516ced034367e330a0eae20e9dccd03684083afab0ae317(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c41df8879f72bd59dd7af061d5c71a66b402d335b1a012f3c7fe8e5ca859da00(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageFormParameters, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__876905772bc4d2e7d59731cb283d554ebee024f72a8eb7f8ff748d1de477e00e(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__196c7206d9c119cff8e589e19c9bdd72f9aa9f1082e3249aa8fade43a7e80a00(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b815753f2069b089fe57addcd590834be9ad89d28be3f9edcc26a4644c362167(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c16fceeb245820fead4197b4f691f3e5aa9979057415e650e1e4ccb6a08839f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aedae3215f64d103065e24572dca4ce5b44419524cb4e13d823ce74ab5c33cfd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583a2086c5e5972d3107e3c8f1e03b23732932633e59858c18964633b6c2620c(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bdba303ffb3a5ae0cae7a885479cddbeff4a780b39d9bfb48c11eb2e46e219e(
    *,
    condition: typing.Optional[builtins.str] = None,
    intent: typing.Optional[builtins.str] = None,
    target_flow: typing.Optional[builtins.str] = None,
    target_page: typing.Optional[builtins.str] = None,
    trigger_fulfillment: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcad1ccd1690a777ec603990e09c68572b548c019611a5167bed8df8972be5d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b236e3f9344d2b7d9206a0adccead7dca09ceacf6109ded6e7416dfb7e0305c2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d9b7879ab0be41bd390702b6002d3d38f0b6226f35f917ea3f056585bad161(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__528fc146cac0fc1586e9307b0a6f61fde381d8985887bf44b932fba2546a5838(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a241bc7b6bf62a6c6d5f4353fbdf8f93c8226864ecc9fe01ae78ead5bc71c1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3037f47c00fcbc1d674ba694c8fa4dae2fd3a3c9ffb14516b2de32812c6f224f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0ff8dfe876bd230eb009d84f34c308e05dfe3fcf2f02654fc4ed40ac1d714b6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7da3b8a18f90064175405fe3e93306ff230b7b12c8ee1fe04245701d72942b5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa5249f307c950682b9b9ac75b2e3b6c4ea1fc787685a16a446223398f45c6c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60bb28468aa90b9930ec011d8ea636224f3796e6d450b8bfd4824ff439016f46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b9e772cdcb8a268b71d08906588fb3e8782dd22ddf7402b0757bb51a73d59b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fbaf17e27fd3029c935810f35ea810e5a2419bbb7e157d0b222c0d401d65c2b(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutes, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a316694886a01524cb8019ef59a9e0b8930f9dafb570dc9612708a995c1bc07a(
    *,
    messages: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    return_partial_responses: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag: typing.Optional[builtins.str] = None,
    webhook: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ac2780428e2c00fd753706d2948b221a0fb1114f48449f6235a8af355bbfd6(
    *,
    text: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7cc5ba1aa62d842918faf33c8800bacf82fb8e7ff44537226e0bf7d9bcbdc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574ad5b337663c95bce4aef3460ab75477d6eb1edce1ef341f73fc5d7e990880(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f6e09150a3d3ed435b615088c06d3551c87557b225b427f3ca9802f47dd41f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__157dda77c11e6da3754da606b4b323ccfd4fdfb24f9d9824f349330f7d9da877(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a402e1f04dcfaaec90f1f60eb8a1442093e08ba77887ff8974906e35d1b8011c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f4e72346a91b536c015b895a8338d3079bdae76a435e4cbba1b9fc2d574d773(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6482e4b570a27bc6b524fd8b6b007d91bab382a7d99d27fbc66048eba38fe300(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b35bab381880b5efa543830687e229ca026b4a9450e82c6741604bf00dbc1d(
    value: typing.Optional[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38b3a1c0c7435d5d96729f38134b96ae45ace916b69e9be893324b4b85e4a7a(
    *,
    text: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f3db04f8ef449258ace9f14cc9d1a9d64856dbb845e0f3c016b269709021291(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__684b3f22c566cc5c2fabac255e21d408d12f8b315be171d9474d948c2daa0f0a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11574cf51692340e2cae4e14498bf419c7e8ba2f79b2027b7836e6c9c865185b(
    value: typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessagesText],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c6a9d24ca199089776c22d49293073daefd976437a3df271d6b0e4310cd3896(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5da5e882870d7a1d55d485ba6c48898c4114110fe826e3e6fa691af8010c067(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillmentMessages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__073d56e65ea59f7e368100e36ae4bbd71658e23b11169eb4420d1c1a7290c0b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e6668ef2abecdf3db5dec8c1c4b6358e6bcf8bbab853666e9686f8e14a536b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c981bc1cbbb9a1d369e902ca211ca8f40619905c509ff187e2559b9dc141eaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bbca2e3cde617d92d1803c7bc65e12fa452f61355d41bbabdfd11771d891a04(
    value: typing.Optional[GoogleDialogflowCxPageTransitionRoutesTriggerFulfillment],
) -> None:
    """Type checking stubs"""
    pass
