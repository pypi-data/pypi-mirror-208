'''
# `azurerm_media_streaming_policy`

Refer to the Terraform Registory for docs: [`azurerm_media_streaming_policy`](https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy).
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


class MediaStreamingPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy azurerm_media_streaming_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        media_services_account_name: builtins.str,
        name: builtins.str,
        resource_group_name: builtins.str,
        common_encryption_cbcs: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcs", typing.Dict[builtins.str, typing.Any]]] = None,
        common_encryption_cenc: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCenc", typing.Dict[builtins.str, typing.Any]]] = None,
        default_content_key_policy_name: typing.Optional[builtins.str] = None,
        envelope_encryption: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        no_encryption_enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyNoEncryptionEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["MediaStreamingPolicyTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy azurerm_media_streaming_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param media_services_account_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#media_services_account_name MediaStreamingPolicy#media_services_account_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#name MediaStreamingPolicy#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#resource_group_name MediaStreamingPolicy#resource_group_name}.
        :param common_encryption_cbcs: common_encryption_cbcs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cbcs MediaStreamingPolicy#common_encryption_cbcs}
        :param common_encryption_cenc: common_encryption_cenc block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cenc MediaStreamingPolicy#common_encryption_cenc}
        :param default_content_key_policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key_policy_name MediaStreamingPolicy#default_content_key_policy_name}.
        :param envelope_encryption: envelope_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#envelope_encryption MediaStreamingPolicy#envelope_encryption}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#id MediaStreamingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param no_encryption_enabled_protocols: no_encryption_enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#no_encryption_enabled_protocols MediaStreamingPolicy#no_encryption_enabled_protocols}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#timeouts MediaStreamingPolicy#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16257c9d0eb4ef2573bad9116d8bb571c21ba680834a3edd53f19a45ea21697c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MediaStreamingPolicyConfig(
            media_services_account_name=media_services_account_name,
            name=name,
            resource_group_name=resource_group_name,
            common_encryption_cbcs=common_encryption_cbcs,
            common_encryption_cenc=common_encryption_cenc,
            default_content_key_policy_name=default_content_key_policy_name,
            envelope_encryption=envelope_encryption,
            id=id,
            no_encryption_enabled_protocols=no_encryption_enabled_protocols,
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

    @jsii.member(jsii_name="putCommonEncryptionCbcs")
    def put_common_encryption_cbcs(
        self,
        *,
        clear_key_encryption: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_fairplay: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay", typing.Dict[builtins.str, typing.Any]]] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param clear_key_encryption: clear_key_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param drm_fairplay: drm_fairplay block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_fairplay MediaStreamingPolicy#drm_fairplay}
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        value = MediaStreamingPolicyCommonEncryptionCbcs(
            clear_key_encryption=clear_key_encryption,
            default_content_key=default_content_key,
            drm_fairplay=drm_fairplay,
            enabled_protocols=enabled_protocols,
        )

        return typing.cast(None, jsii.invoke(self, "putCommonEncryptionCbcs", [value]))

    @jsii.member(jsii_name="putCommonEncryptionCenc")
    def put_common_encryption_cenc(
        self,
        *,
        clear_key_encryption: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        clear_track: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencClearTrack", typing.Dict[builtins.str, typing.Any]]]]] = None,
        content_key_to_track_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_playready: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencDrmPlayready", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_widevine_custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param clear_key_encryption: clear_key_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        :param clear_track: clear_track block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_track MediaStreamingPolicy#clear_track}
        :param content_key_to_track_mapping: content_key_to_track_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#content_key_to_track_mapping MediaStreamingPolicy#content_key_to_track_mapping}
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param drm_playready: drm_playready block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_playready MediaStreamingPolicy#drm_playready}
        :param drm_widevine_custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_widevine_custom_license_acquisition_url_template MediaStreamingPolicy#drm_widevine_custom_license_acquisition_url_template}.
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        value = MediaStreamingPolicyCommonEncryptionCenc(
            clear_key_encryption=clear_key_encryption,
            clear_track=clear_track,
            content_key_to_track_mapping=content_key_to_track_mapping,
            default_content_key=default_content_key,
            drm_playready=drm_playready,
            drm_widevine_custom_license_acquisition_url_template=drm_widevine_custom_license_acquisition_url_template,
            enabled_protocols=enabled_protocols,
        )

        return typing.cast(None, jsii.invoke(self, "putCommonEncryptionCenc", [value]))

    @jsii.member(jsii_name="putEnvelopeEncryption")
    def put_envelope_encryption(
        self,
        *,
        custom_keys_acquisition_url_template: typing.Optional[builtins.str] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        value = MediaStreamingPolicyEnvelopeEncryption(
            custom_keys_acquisition_url_template=custom_keys_acquisition_url_template,
            default_content_key=default_content_key,
            enabled_protocols=enabled_protocols,
        )

        return typing.cast(None, jsii.invoke(self, "putEnvelopeEncryption", [value]))

    @jsii.member(jsii_name="putNoEncryptionEnabledProtocols")
    def put_no_encryption_enabled_protocols(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        value = MediaStreamingPolicyNoEncryptionEnabledProtocols(
            dash=dash, download=download, hls=hls, smooth_streaming=smooth_streaming
        )

        return typing.cast(None, jsii.invoke(self, "putNoEncryptionEnabledProtocols", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#create MediaStreamingPolicy#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#delete MediaStreamingPolicy#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#read MediaStreamingPolicy#read}.
        '''
        value = MediaStreamingPolicyTimeouts(create=create, delete=delete, read=read)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCommonEncryptionCbcs")
    def reset_common_encryption_cbcs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonEncryptionCbcs", []))

    @jsii.member(jsii_name="resetCommonEncryptionCenc")
    def reset_common_encryption_cenc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonEncryptionCenc", []))

    @jsii.member(jsii_name="resetDefaultContentKeyPolicyName")
    def reset_default_content_key_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultContentKeyPolicyName", []))

    @jsii.member(jsii_name="resetEnvelopeEncryption")
    def reset_envelope_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvelopeEncryption", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNoEncryptionEnabledProtocols")
    def reset_no_encryption_enabled_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoEncryptionEnabledProtocols", []))

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
    @jsii.member(jsii_name="commonEncryptionCbcs")
    def common_encryption_cbcs(
        self,
    ) -> "MediaStreamingPolicyCommonEncryptionCbcsOutputReference":
        return typing.cast("MediaStreamingPolicyCommonEncryptionCbcsOutputReference", jsii.get(self, "commonEncryptionCbcs"))

    @builtins.property
    @jsii.member(jsii_name="commonEncryptionCenc")
    def common_encryption_cenc(
        self,
    ) -> "MediaStreamingPolicyCommonEncryptionCencOutputReference":
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencOutputReference", jsii.get(self, "commonEncryptionCenc"))

    @builtins.property
    @jsii.member(jsii_name="envelopeEncryption")
    def envelope_encryption(
        self,
    ) -> "MediaStreamingPolicyEnvelopeEncryptionOutputReference":
        return typing.cast("MediaStreamingPolicyEnvelopeEncryptionOutputReference", jsii.get(self, "envelopeEncryption"))

    @builtins.property
    @jsii.member(jsii_name="noEncryptionEnabledProtocols")
    def no_encryption_enabled_protocols(
        self,
    ) -> "MediaStreamingPolicyNoEncryptionEnabledProtocolsOutputReference":
        return typing.cast("MediaStreamingPolicyNoEncryptionEnabledProtocolsOutputReference", jsii.get(self, "noEncryptionEnabledProtocols"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MediaStreamingPolicyTimeoutsOutputReference":
        return typing.cast("MediaStreamingPolicyTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="commonEncryptionCbcsInput")
    def common_encryption_cbcs_input(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCbcs"]:
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCbcs"], jsii.get(self, "commonEncryptionCbcsInput"))

    @builtins.property
    @jsii.member(jsii_name="commonEncryptionCencInput")
    def common_encryption_cenc_input(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCenc"]:
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCenc"], jsii.get(self, "commonEncryptionCencInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKeyPolicyNameInput")
    def default_content_key_policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultContentKeyPolicyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="envelopeEncryptionInput")
    def envelope_encryption_input(
        self,
    ) -> typing.Optional["MediaStreamingPolicyEnvelopeEncryption"]:
        return typing.cast(typing.Optional["MediaStreamingPolicyEnvelopeEncryption"], jsii.get(self, "envelopeEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mediaServicesAccountNameInput")
    def media_services_account_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mediaServicesAccountNameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="noEncryptionEnabledProtocolsInput")
    def no_encryption_enabled_protocols_input(
        self,
    ) -> typing.Optional["MediaStreamingPolicyNoEncryptionEnabledProtocols"]:
        return typing.cast(typing.Optional["MediaStreamingPolicyNoEncryptionEnabledProtocols"], jsii.get(self, "noEncryptionEnabledProtocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["MediaStreamingPolicyTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["MediaStreamingPolicyTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKeyPolicyName")
    def default_content_key_policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultContentKeyPolicyName"))

    @default_content_key_policy_name.setter
    def default_content_key_policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__badf15e349fea53ef2d71af9be9e08e1d57078eba7ad82a37537c9ad9e35e289)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultContentKeyPolicyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff0b82166f2e3cc5b8a19afc3ad1c2953313cd570160adc319cc9f2938e42cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="mediaServicesAccountName")
    def media_services_account_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mediaServicesAccountName"))

    @media_services_account_name.setter
    def media_services_account_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ef24ac8e44129183e202d3955033b3db5d2e961074bccd7c531c7b4de79f4ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mediaServicesAccountName", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1817cf563292950dd7674c6e5943446c3ae92dabcada03aa91a431160cb1913)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2343a6be28faf7afc420b5544b2d2a12504c3003edac9bd7d75e2d1e31b3b2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcs",
    jsii_struct_bases=[],
    name_mapping={
        "clear_key_encryption": "clearKeyEncryption",
        "default_content_key": "defaultContentKey",
        "drm_fairplay": "drmFairplay",
        "enabled_protocols": "enabledProtocols",
    },
)
class MediaStreamingPolicyCommonEncryptionCbcs:
    def __init__(
        self,
        *,
        clear_key_encryption: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_fairplay: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay", typing.Dict[builtins.str, typing.Any]]] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param clear_key_encryption: clear_key_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param drm_fairplay: drm_fairplay block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_fairplay MediaStreamingPolicy#drm_fairplay}
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        if isinstance(clear_key_encryption, dict):
            clear_key_encryption = MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption(**clear_key_encryption)
        if isinstance(default_content_key, dict):
            default_content_key = MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey(**default_content_key)
        if isinstance(drm_fairplay, dict):
            drm_fairplay = MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay(**drm_fairplay)
        if isinstance(enabled_protocols, dict):
            enabled_protocols = MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols(**enabled_protocols)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f2f0b8c5454c08c0821875d5ee9a811693b5af751cf21119b10a0a410a401e)
            check_type(argname="argument clear_key_encryption", value=clear_key_encryption, expected_type=type_hints["clear_key_encryption"])
            check_type(argname="argument default_content_key", value=default_content_key, expected_type=type_hints["default_content_key"])
            check_type(argname="argument drm_fairplay", value=drm_fairplay, expected_type=type_hints["drm_fairplay"])
            check_type(argname="argument enabled_protocols", value=enabled_protocols, expected_type=type_hints["enabled_protocols"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if clear_key_encryption is not None:
            self._values["clear_key_encryption"] = clear_key_encryption
        if default_content_key is not None:
            self._values["default_content_key"] = default_content_key
        if drm_fairplay is not None:
            self._values["drm_fairplay"] = drm_fairplay
        if enabled_protocols is not None:
            self._values["enabled_protocols"] = enabled_protocols

    @builtins.property
    def clear_key_encryption(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption"]:
        '''clear_key_encryption block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        '''
        result = self._values.get("clear_key_encryption")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption"], result)

    @builtins.property
    def default_content_key(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey"]:
        '''default_content_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        '''
        result = self._values.get("default_content_key")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey"], result)

    @builtins.property
    def drm_fairplay(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay"]:
        '''drm_fairplay block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_fairplay MediaStreamingPolicy#drm_fairplay}
        '''
        result = self._values.get("drm_fairplay")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay"], result)

    @builtins.property
    def enabled_protocols(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols"]:
        '''enabled_protocols block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        result = self._values.get("enabled_protocols")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCbcs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption",
    jsii_struct_bases=[],
    name_mapping={
        "custom_keys_acquisition_url_template": "customKeysAcquisitionUrlTemplate",
    },
)
class MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption:
    def __init__(self, *, custom_keys_acquisition_url_template: builtins.str) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__316cd40e5e113548b4dd05a2290c1561e088dacc488ddb7d75478f37e91631e9)
            check_type(argname="argument custom_keys_acquisition_url_template", value=custom_keys_acquisition_url_template, expected_type=type_hints["custom_keys_acquisition_url_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_keys_acquisition_url_template": custom_keys_acquisition_url_template,
        }

    @builtins.property
    def custom_keys_acquisition_url_template(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.'''
        result = self._values.get("custom_keys_acquisition_url_template")
        assert result is not None, "Required property 'custom_keys_acquisition_url_template' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c125f731846ffcf68c97d67938a51f3a82299eedf9fdbdaef7c5bd324fe2a1c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplateInput")
    def custom_keys_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customKeysAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplate")
    def custom_keys_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customKeysAcquisitionUrlTemplate"))

    @custom_keys_acquisition_url_template.setter
    def custom_keys_acquisition_url_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__001165656b581fc1a8a0af1c4e34385f9b353528d0371adc71acec43585447f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customKeysAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddec1ba4603f1fb73d0918c23197bacddd65f6b36bdc4a060c2cc8145eef27d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "policy_name": "policyName"},
)
class MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey:
    def __init__(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ede7ee0570a9ddbb9ba5a5caef594fa2f4159fb46e0a51f5d0b9e09adc2370db)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if label is not None:
            self._values["label"] = label
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5b5e607ad30a9be53e0b83067853e5b2f214f011af2f66e2b09b662dde3290e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5229cfd5cd24821db6983663746c27a69d3f094ed8ede51ced1b86c50cda2bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1036a6fad843a59ada93c3d43b1a3e21c891d7e362e29a33f9e6e8919d45521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7ca0fdc5283ee78c87188f8ed20d4dbe611d81dcfda261877001c3f673ecb6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay",
    jsii_struct_bases=[],
    name_mapping={
        "allow_persistent_license": "allowPersistentLicense",
        "custom_license_acquisition_url_template": "customLicenseAcquisitionUrlTemplate",
    },
)
class MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay:
    def __init__(
        self,
        *,
        allow_persistent_license: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_persistent_license: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#allow_persistent_license MediaStreamingPolicy#allow_persistent_license}.
        :param custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7174b584ea9a9539ddac7668b51f26c8039cc313b13b9be2302fd9f6bf6efe70)
            check_type(argname="argument allow_persistent_license", value=allow_persistent_license, expected_type=type_hints["allow_persistent_license"])
            check_type(argname="argument custom_license_acquisition_url_template", value=custom_license_acquisition_url_template, expected_type=type_hints["custom_license_acquisition_url_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_persistent_license is not None:
            self._values["allow_persistent_license"] = allow_persistent_license
        if custom_license_acquisition_url_template is not None:
            self._values["custom_license_acquisition_url_template"] = custom_license_acquisition_url_template

    @builtins.property
    def allow_persistent_license(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#allow_persistent_license MediaStreamingPolicy#allow_persistent_license}.'''
        result = self._values.get("allow_persistent_license")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_license_acquisition_url_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.'''
        result = self._values.get("custom_license_acquisition_url_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCbcsDrmFairplayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsDrmFairplayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c4bdcfacaea39711c881a5a7b1df0a28f2c923be9926d2c357e26f4e09cd7c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowPersistentLicense")
    def reset_allow_persistent_license(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowPersistentLicense", []))

    @jsii.member(jsii_name="resetCustomLicenseAcquisitionUrlTemplate")
    def reset_custom_license_acquisition_url_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLicenseAcquisitionUrlTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="allowPersistentLicenseInput")
    def allow_persistent_license_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowPersistentLicenseInput"))

    @builtins.property
    @jsii.member(jsii_name="customLicenseAcquisitionUrlTemplateInput")
    def custom_license_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLicenseAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="allowPersistentLicense")
    def allow_persistent_license(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowPersistentLicense"))

    @allow_persistent_license.setter
    def allow_persistent_license(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b8d44f09612e02d6504bca4a6d5c4bac69b728992ca8012c1cdbe31f11dab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPersistentLicense", value)

    @builtins.property
    @jsii.member(jsii_name="customLicenseAcquisitionUrlTemplate")
    def custom_license_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLicenseAcquisitionUrlTemplate"))

    @custom_license_acquisition_url_template.setter
    def custom_license_acquisition_url_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b0640991de63328e9e26599b124c108242e36cc0af810c79669cac1201d5fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLicenseAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f39d4bc20f79fb2b9feac05ea89512168f7722552b1094672ed6681638844a0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols",
    jsii_struct_bases=[],
    name_mapping={
        "dash": "dash",
        "download": "download",
        "hls": "hls",
        "smooth_streaming": "smoothStreaming",
    },
)
class MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols:
    def __init__(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bfb76a64ab70b7fa8dbb552b01c261074be771e95eb8b70f0c350d035d993f1)
            check_type(argname="argument dash", value=dash, expected_type=type_hints["dash"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument hls", value=hls, expected_type=type_hints["hls"])
            check_type(argname="argument smooth_streaming", value=smooth_streaming, expected_type=type_hints["smooth_streaming"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dash is not None:
            self._values["dash"] = dash
        if download is not None:
            self._values["download"] = download
        if hls is not None:
            self._values["hls"] = hls
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming

    @builtins.property
    def dash(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.'''
        result = self._values.get("dash")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.'''
        result = self._values.get("download")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.'''
        result = self._values.get("hls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocolsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocolsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36a7dba195f8b13866dccb21db829241f95a19d59c337faa123ead142d4bc3cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDash")
    def reset_dash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDash", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetHls")
    def reset_hls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHls", []))

    @jsii.member(jsii_name="resetSmoothStreaming")
    def reset_smooth_streaming(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmoothStreaming", []))

    @builtins.property
    @jsii.member(jsii_name="dashInput")
    def dash_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dashInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="hlsInput")
    def hls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hlsInput"))

    @builtins.property
    @jsii.member(jsii_name="smoothStreamingInput")
    def smooth_streaming_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "smoothStreamingInput"))

    @builtins.property
    @jsii.member(jsii_name="dash")
    def dash(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dash"))

    @dash.setter
    def dash(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16dc9c4d20b9742b29840125966dc4d14be4c069d4dd25bfafea21f1bf7351f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dash", value)

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "download"))

    @download.setter
    def download(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35e2afb95a5e576459b1bdb5d4458fa6cbc29abe27c58158f7a3108d18c2148a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value)

    @builtins.property
    @jsii.member(jsii_name="hls")
    def hls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hls"))

    @hls.setter
    def hls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b1518de1a2d5493cb51432ea461754bb7fab40bd017b85dfbe6ca8793a2202)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hls", value)

    @builtins.property
    @jsii.member(jsii_name="smoothStreaming")
    def smooth_streaming(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "smoothStreaming"))

    @smooth_streaming.setter
    def smooth_streaming(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb87cbdc0363e774765dc7994a0dcafa629f1477bbf6d82e502b0e84de53c7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smoothStreaming", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e516a5b4e7e65edd93a26dc50caf0c01de1f5862601b15452ff5be4adae5610f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCbcsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCbcsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d1f1b13db911520be88377e7a65308d43898860c66ba03d141aa2c83c663337)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putClearKeyEncryption")
    def put_clear_key_encryption(
        self,
        *,
        custom_keys_acquisition_url_template: builtins.str,
    ) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption(
            custom_keys_acquisition_url_template=custom_keys_acquisition_url_template
        )

        return typing.cast(None, jsii.invoke(self, "putClearKeyEncryption", [value]))

    @jsii.member(jsii_name="putDefaultContentKey")
    def put_default_content_key(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey(
            label=label, policy_name=policy_name
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultContentKey", [value]))

    @jsii.member(jsii_name="putDrmFairplay")
    def put_drm_fairplay(
        self,
        *,
        allow_persistent_license: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_persistent_license: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#allow_persistent_license MediaStreamingPolicy#allow_persistent_license}.
        :param custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay(
            allow_persistent_license=allow_persistent_license,
            custom_license_acquisition_url_template=custom_license_acquisition_url_template,
        )

        return typing.cast(None, jsii.invoke(self, "putDrmFairplay", [value]))

    @jsii.member(jsii_name="putEnabledProtocols")
    def put_enabled_protocols(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols(
            dash=dash, download=download, hls=hls, smooth_streaming=smooth_streaming
        )

        return typing.cast(None, jsii.invoke(self, "putEnabledProtocols", [value]))

    @jsii.member(jsii_name="resetClearKeyEncryption")
    def reset_clear_key_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClearKeyEncryption", []))

    @jsii.member(jsii_name="resetDefaultContentKey")
    def reset_default_content_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultContentKey", []))

    @jsii.member(jsii_name="resetDrmFairplay")
    def reset_drm_fairplay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrmFairplay", []))

    @jsii.member(jsii_name="resetEnabledProtocols")
    def reset_enabled_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledProtocols", []))

    @builtins.property
    @jsii.member(jsii_name="clearKeyEncryption")
    def clear_key_encryption(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryptionOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryptionOutputReference, jsii.get(self, "clearKeyEncryption"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKey")
    def default_content_key(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKeyOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKeyOutputReference, jsii.get(self, "defaultContentKey"))

    @builtins.property
    @jsii.member(jsii_name="drmFairplay")
    def drm_fairplay(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCbcsDrmFairplayOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCbcsDrmFairplayOutputReference, jsii.get(self, "drmFairplay"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocols")
    def enabled_protocols(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocolsOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocolsOutputReference, jsii.get(self, "enabledProtocols"))

    @builtins.property
    @jsii.member(jsii_name="clearKeyEncryptionInput")
    def clear_key_encryption_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption], jsii.get(self, "clearKeyEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKeyInput")
    def default_content_key_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey], jsii.get(self, "defaultContentKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="drmFairplayInput")
    def drm_fairplay_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay], jsii.get(self, "drmFairplayInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocolsInput")
    def enabled_protocols_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols], jsii.get(self, "enabledProtocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc579000a5aa76493f51ea936530d93c896241a795afb830eaebf1658e2cab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCenc",
    jsii_struct_bases=[],
    name_mapping={
        "clear_key_encryption": "clearKeyEncryption",
        "clear_track": "clearTrack",
        "content_key_to_track_mapping": "contentKeyToTrackMapping",
        "default_content_key": "defaultContentKey",
        "drm_playready": "drmPlayready",
        "drm_widevine_custom_license_acquisition_url_template": "drmWidevineCustomLicenseAcquisitionUrlTemplate",
        "enabled_protocols": "enabledProtocols",
    },
)
class MediaStreamingPolicyCommonEncryptionCenc:
    def __init__(
        self,
        *,
        clear_key_encryption: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        clear_track: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencClearTrack", typing.Dict[builtins.str, typing.Any]]]]] = None,
        content_key_to_track_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_playready: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencDrmPlayready", typing.Dict[builtins.str, typing.Any]]] = None,
        drm_widevine_custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyCommonEncryptionCencEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param clear_key_encryption: clear_key_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        :param clear_track: clear_track block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_track MediaStreamingPolicy#clear_track}
        :param content_key_to_track_mapping: content_key_to_track_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#content_key_to_track_mapping MediaStreamingPolicy#content_key_to_track_mapping}
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param drm_playready: drm_playready block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_playready MediaStreamingPolicy#drm_playready}
        :param drm_widevine_custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_widevine_custom_license_acquisition_url_template MediaStreamingPolicy#drm_widevine_custom_license_acquisition_url_template}.
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        if isinstance(clear_key_encryption, dict):
            clear_key_encryption = MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption(**clear_key_encryption)
        if isinstance(default_content_key, dict):
            default_content_key = MediaStreamingPolicyCommonEncryptionCencDefaultContentKey(**default_content_key)
        if isinstance(drm_playready, dict):
            drm_playready = MediaStreamingPolicyCommonEncryptionCencDrmPlayready(**drm_playready)
        if isinstance(enabled_protocols, dict):
            enabled_protocols = MediaStreamingPolicyCommonEncryptionCencEnabledProtocols(**enabled_protocols)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df29267f26859d504dd3a49915c66d747218279c77bb061c01f0e4915caeb732)
            check_type(argname="argument clear_key_encryption", value=clear_key_encryption, expected_type=type_hints["clear_key_encryption"])
            check_type(argname="argument clear_track", value=clear_track, expected_type=type_hints["clear_track"])
            check_type(argname="argument content_key_to_track_mapping", value=content_key_to_track_mapping, expected_type=type_hints["content_key_to_track_mapping"])
            check_type(argname="argument default_content_key", value=default_content_key, expected_type=type_hints["default_content_key"])
            check_type(argname="argument drm_playready", value=drm_playready, expected_type=type_hints["drm_playready"])
            check_type(argname="argument drm_widevine_custom_license_acquisition_url_template", value=drm_widevine_custom_license_acquisition_url_template, expected_type=type_hints["drm_widevine_custom_license_acquisition_url_template"])
            check_type(argname="argument enabled_protocols", value=enabled_protocols, expected_type=type_hints["enabled_protocols"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if clear_key_encryption is not None:
            self._values["clear_key_encryption"] = clear_key_encryption
        if clear_track is not None:
            self._values["clear_track"] = clear_track
        if content_key_to_track_mapping is not None:
            self._values["content_key_to_track_mapping"] = content_key_to_track_mapping
        if default_content_key is not None:
            self._values["default_content_key"] = default_content_key
        if drm_playready is not None:
            self._values["drm_playready"] = drm_playready
        if drm_widevine_custom_license_acquisition_url_template is not None:
            self._values["drm_widevine_custom_license_acquisition_url_template"] = drm_widevine_custom_license_acquisition_url_template
        if enabled_protocols is not None:
            self._values["enabled_protocols"] = enabled_protocols

    @builtins.property
    def clear_key_encryption(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption"]:
        '''clear_key_encryption block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_key_encryption MediaStreamingPolicy#clear_key_encryption}
        '''
        result = self._values.get("clear_key_encryption")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption"], result)

    @builtins.property
    def clear_track(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencClearTrack"]]]:
        '''clear_track block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#clear_track MediaStreamingPolicy#clear_track}
        '''
        result = self._values.get("clear_track")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencClearTrack"]]], result)

    @builtins.property
    def content_key_to_track_mapping(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping"]]]:
        '''content_key_to_track_mapping block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#content_key_to_track_mapping MediaStreamingPolicy#content_key_to_track_mapping}
        '''
        result = self._values.get("content_key_to_track_mapping")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping"]]], result)

    @builtins.property
    def default_content_key(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCencDefaultContentKey"]:
        '''default_content_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        '''
        result = self._values.get("default_content_key")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCencDefaultContentKey"], result)

    @builtins.property
    def drm_playready(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCencDrmPlayready"]:
        '''drm_playready block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_playready MediaStreamingPolicy#drm_playready}
        '''
        result = self._values.get("drm_playready")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCencDrmPlayready"], result)

    @builtins.property
    def drm_widevine_custom_license_acquisition_url_template(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#drm_widevine_custom_license_acquisition_url_template MediaStreamingPolicy#drm_widevine_custom_license_acquisition_url_template}.'''
        result = self._values.get("drm_widevine_custom_license_acquisition_url_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled_protocols(
        self,
    ) -> typing.Optional["MediaStreamingPolicyCommonEncryptionCencEnabledProtocols"]:
        '''enabled_protocols block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        result = self._values.get("enabled_protocols")
        return typing.cast(typing.Optional["MediaStreamingPolicyCommonEncryptionCencEnabledProtocols"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCenc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption",
    jsii_struct_bases=[],
    name_mapping={
        "custom_keys_acquisition_url_template": "customKeysAcquisitionUrlTemplate",
    },
)
class MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption:
    def __init__(self, *, custom_keys_acquisition_url_template: builtins.str) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11904a44b651475f69b30d59a1c896edf1f07c0ffa08806bf6f25fb75a1b2105)
            check_type(argname="argument custom_keys_acquisition_url_template", value=custom_keys_acquisition_url_template, expected_type=type_hints["custom_keys_acquisition_url_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_keys_acquisition_url_template": custom_keys_acquisition_url_template,
        }

    @builtins.property
    def custom_keys_acquisition_url_template(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.'''
        result = self._values.get("custom_keys_acquisition_url_template")
        assert result is not None, "Required property 'custom_keys_acquisition_url_template' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencClearKeyEncryptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearKeyEncryptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d7095a5425f0e0fdda98f4c421e44126dbb6403ab9a79983a867cd54ecea6cf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplateInput")
    def custom_keys_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customKeysAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplate")
    def custom_keys_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customKeysAcquisitionUrlTemplate"))

    @custom_keys_acquisition_url_template.setter
    def custom_keys_acquisition_url_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06fd3a85017e4e1e227dd1466b6283f0cece8e8e9f3ea56a307f7772bfa3868d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customKeysAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b02ab6f18842f49657f6d5a26473bcce5c129c96de4eed847f6e76b84fbda3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrack",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition"},
)
class MediaStreamingPolicyCommonEncryptionCencClearTrack:
    def __init__(
        self,
        *,
        condition: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencClearTrackCondition", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#condition MediaStreamingPolicy#condition}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0303e613494f1839a8887ffe87a3463a9e908fad8004e7189bac71923282510e)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "condition": condition,
        }

    @builtins.property
    def condition(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencClearTrackCondition"]]:
        '''condition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#condition MediaStreamingPolicy#condition}
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencClearTrackCondition"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencClearTrack(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrackCondition",
    jsii_struct_bases=[],
    name_mapping={"operation": "operation", "property": "property", "value": "value"},
)
class MediaStreamingPolicyCommonEncryptionCencClearTrackCondition:
    def __init__(
        self,
        *,
        operation: builtins.str,
        property: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param operation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#operation MediaStreamingPolicy#operation}.
        :param property: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#property MediaStreamingPolicy#property}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#value MediaStreamingPolicy#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5dec3b34520e5def1df53acfa25ba44490a4c6cfbd869c53465ccb4be558781)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument property", value=property, expected_type=type_hints["property"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operation": operation,
            "property": property,
            "value": value,
        }

    @builtins.property
    def operation(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#operation MediaStreamingPolicy#operation}.'''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def property(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#property MediaStreamingPolicy#property}.'''
        result = self._values.get("property")
        assert result is not None, "Required property 'property' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#value MediaStreamingPolicy#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencClearTrackCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencClearTrackConditionList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrackConditionList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a11ab4499b63736092e806525298da8aa62d944bedcbd36870b9aec84dfc0808)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaStreamingPolicyCommonEncryptionCencClearTrackConditionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524c41dc24d4861b1edb572d7a5279c53894d9240ec3d1642dbb885f6101527b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencClearTrackConditionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__836fb480937cd060ad8841c3ac13182c260cc941041226570cdb1ac2b07f3460)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee4de28939926676f46cc8f1aae6db98e234c77b77d38be79d2ff794893f8341)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1dc5b33e718fc9140dc9358c3adc650a6244995cdb1341394431344eae2f4e24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce4f64e846f3e17776b0ae8b06d1df395f4d3d2a860bc9c7c7bad6f7045262f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencClearTrackConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrackConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c5210c14b6c6dd62c52dfe273cf433a61918ea4af72dcbc6978a267e2a69d0e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="operationInput")
    def operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationInput"))

    @builtins.property
    @jsii.member(jsii_name="propertyInput")
    def property_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operation")
    def operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operation"))

    @operation.setter
    def operation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89cb58d148ecf84fcab20851caa44496dc76eaedee52e3083990912115ba39fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operation", value)

    @builtins.property
    @jsii.member(jsii_name="property")
    def property(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "property"))

    @property.setter
    def property(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bf7e710c1a74badd2339121f58f46a68efac1136c537b5f726c9aa025e14629)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "property", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd5cfee3d02610008ccd725debea90db0c8894bbe4565478d30f79efa418498e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63f7cc2c4e13f505743df9a9ea32b3839061e50ab9d4472fc4960e81fd92f831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencClearTrackList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrackList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5006a11292332c42caf92c9f039d6a4562279dd5870b1fb4098f3d73ff0dc58c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaStreamingPolicyCommonEncryptionCencClearTrackOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce72bfdf762dfbd021a2f308fe285ebdfa3f4dc10c075ee7ec1203f4dad0b403)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencClearTrackOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eef5fdca252185f9ba494608c6234a05ab11fe0773cea0aa620d858f55a7fea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3edcf5e28d479deb526368d1d283aeeaad30fe6599b7dd2d62ad1478bec1519f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e902c496cafa08a637382809c96826e322dfdddec3bc78f3d69a121471a8239)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28e3d218fcbad854b6b9de32ecbab96c2b3723a3450606f5710c7e465f56d750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencClearTrackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencClearTrackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__692cca7540d607e416337bf9a465e256061152477e60fce74dce6e855fba665c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a291a673f3fa59e05f712b51772ad2311a719dbdb159a749a0fefd00e48ffd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencClearTrackConditionList:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencClearTrackConditionList, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59aaacacc27d0c947d3a7cf45aba859d9e0ed43368570a598a261b2e7a2469fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping",
    jsii_struct_bases=[],
    name_mapping={"track": "track", "label": "label", "policy_name": "policyName"},
)
class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping:
    def __init__(
        self,
        *,
        track: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack", typing.Dict[builtins.str, typing.Any]]]],
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param track: track block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#track MediaStreamingPolicy#track}
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc95d9831b76ca3bb505d8f6cba491809d989a66b464de34e9da8d22dd74529b)
            check_type(argname="argument track", value=track, expected_type=type_hints["track"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "track": track,
        }
        if label is not None:
            self._values["label"] = label
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def track(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack"]]:
        '''track block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#track MediaStreamingPolicy#track}
        '''
        result = self._values.get("track")
        assert result is not None, "Required property 'track' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack"]], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__757c4be1630811db5c17ad4832b9a47b8e63af103a39ebf4829c986bbe19cefa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb3ce19cd79c279a4c3384a02136b24c0e407262b9a77da22c271f728510af35)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e171f3d39facdf25c8fd18dc83b5a4e3b29015ccf78f6d70343597eb8fa552a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eca202e806dcc97cb320ed91da3f9aff747d5991e3f97ae18934b7b9a4e8a9f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__54210a75b1016938053e441ec379b47f1b62bd0965d7144d07758ca489bc6ded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68a869ced7be3f98b0dc23a3c1692f9990bb4c958b2092ed42b8b3fefa42c02e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__164ad456549161b80b0ac41c6f239022a819e372e7a91cdbffda12f157e3c924)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTrack")
    def put_track(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc1a400c5b2a1619186d3d4d7948a63a3f0c8dcbf5ed7b7eaf791b01a00f9441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTrack", [value]))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="track")
    def track(
        self,
    ) -> "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackList":
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackList", jsii.get(self, "track"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="trackInput")
    def track_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack"]]], jsii.get(self, "trackInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15099aaf8c9c5def02b0a5f3b6baa460d43993ce4123367ee6a254e6445801f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778b4b47857cc59afb31a9ca35c649ee4eec93167f2197f59b29c269259b00f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4738a67cbb88c3695bb5c093b28eb8fab1fdc0dc189a70bb85417f86091470a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition"},
)
class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack:
    def __init__(
        self,
        *,
        condition: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#condition MediaStreamingPolicy#condition}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42a84e632257a3d026d91d5dc12597e92126962fa16615c865d93c75c146c9b8)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "condition": condition,
        }

    @builtins.property
    def condition(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition"]]:
        '''condition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#condition MediaStreamingPolicy#condition}
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition",
    jsii_struct_bases=[],
    name_mapping={"operation": "operation", "property": "property", "value": "value"},
)
class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition:
    def __init__(
        self,
        *,
        operation: builtins.str,
        property: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param operation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#operation MediaStreamingPolicy#operation}.
        :param property: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#property MediaStreamingPolicy#property}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#value MediaStreamingPolicy#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6e61ec0a3011174a67c063da6033f96a33ef48d72daef3dd3e410703b0e931b)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument property", value=property, expected_type=type_hints["property"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operation": operation,
            "property": property,
            "value": value,
        }

    @builtins.property
    def operation(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#operation MediaStreamingPolicy#operation}.'''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def property(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#property MediaStreamingPolicy#property}.'''
        result = self._values.get("property")
        assert result is not None, "Required property 'property' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#value MediaStreamingPolicy#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6adc6eac05f73c7870f7249cae346fe0f4661f4dc708e1b4a99ff500a3639632)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b923fd575e14157497342d7cfeb0b1bbab74ac4bdc063aecaecfecb8d3eab676)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d124f4a83a5564c6b9af05c44b45083a9f649a8ca1c4b845ff1bf27ed8d6c4bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6c1a1faf6d5403bf2c0e6fd68765abaa06d65de6d9f85ead791d2c2479d783f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8d30e09d0829cc9d6f9b672f0b0b17fb8bb44d74d7a99a24dd908f77f659492)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45e1660984ce4672330347aa20ba2b422820ac74f89419e7ebafde817b740130)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbd36327804ee5dd7aa5ab5420584634e907d6f1ec482f7dcfc9348077a42dbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="operationInput")
    def operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationInput"))

    @builtins.property
    @jsii.member(jsii_name="propertyInput")
    def property_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="operation")
    def operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operation"))

    @operation.setter
    def operation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9651f4df2b80137f3313169787f8b7e783462a91185eb0530f448185f46ae84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operation", value)

    @builtins.property
    @jsii.member(jsii_name="property")
    def property(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "property"))

    @property.setter
    def property(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f34483bdc17abb3505632fafcdadf9e8bbe4c26539deb3485527e0d3e282ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "property", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__361f2fd287013c5b2a800c71438dd4cf158e28a7098d8978d2ab470489b9b3b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6779672935f27f00c0197b3ae18bc37998c9ba346a28a8bcc9d8aa85728b4033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17a219864a162cbb8ddbc560df14ab8d4edaa0b3021a09d6490b58dd20b9c02a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd3f4c8ee33dffd25a170849a0ed6e5922370c836bc05b466a3c201a5e2343ab)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c7bb62b3365b4cb9c18bfb443ab1a909e7694214b77585b7efc27ba0f0e495)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70e8254b5acc6d9b3dc010bc9997fec2d881e800ee630dadfe793b20f4b65a82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21332df13e056e8350d299c6c4a9f6f678c7209fc36f16d1f419a80216d89baf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00f0ed63286d271f2f411ff9bf1b99d277b175ede9d45ff1c89cca549ea50137)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fc98ee20d3184daeb81e075fe3fab120f60ec11163e1083442bbf2f8717d95e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33709c8b30378b9e1e16b7effc95f33b7f6630f04633663055b10d36a9798ccf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionList:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionList, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f56f08815bbfd5e99bc69fc5c6d1f087c303d6058979f218092b6e457c16d24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencDefaultContentKey",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "policy_name": "policyName"},
)
class MediaStreamingPolicyCommonEncryptionCencDefaultContentKey:
    def __init__(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3853958f59dba38974fce1224f059072240ec78ad75374837e8ce7214d36797e)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if label is not None:
            self._values["label"] = label
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencDefaultContentKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencDefaultContentKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencDefaultContentKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4efef38efa531147056a619b8885d276abebcce8dd666191fccf7e40960e33e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48d533a5812e4d27fd6f3c75f7731990e44edd7d77a43377d7e5899f4eb61da6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33ba5a8438ae3f2140e0007cc666be8fb5aebaa88dc08125fa5218463c1b1ca5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__693978bf058aae51a1211ff26551943b154c86bd260ef228b7d301c15a5a309b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencDrmPlayready",
    jsii_struct_bases=[],
    name_mapping={
        "custom_attributes": "customAttributes",
        "custom_license_acquisition_url_template": "customLicenseAcquisitionUrlTemplate",
    },
)
class MediaStreamingPolicyCommonEncryptionCencDrmPlayready:
    def __init__(
        self,
        *,
        custom_attributes: typing.Optional[builtins.str] = None,
        custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param custom_attributes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_attributes MediaStreamingPolicy#custom_attributes}.
        :param custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abd053b9c0cf786dd29ec64c2403e20da7a062060fb4d28235b6e45d5fd5cd4a)
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument custom_license_acquisition_url_template", value=custom_license_acquisition_url_template, expected_type=type_hints["custom_license_acquisition_url_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if custom_license_acquisition_url_template is not None:
            self._values["custom_license_acquisition_url_template"] = custom_license_acquisition_url_template

    @builtins.property
    def custom_attributes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_attributes MediaStreamingPolicy#custom_attributes}.'''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_license_acquisition_url_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.'''
        result = self._values.get("custom_license_acquisition_url_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencDrmPlayready(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencDrmPlayreadyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencDrmPlayreadyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c730cac1e5d5ba96f3eac29fd7db2bad91c727880f0f108ea16e4c0b24c17c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetCustomLicenseAcquisitionUrlTemplate")
    def reset_custom_license_acquisition_url_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomLicenseAcquisitionUrlTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="customLicenseAcquisitionUrlTemplateInput")
    def custom_license_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customLicenseAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributes")
    def custom_attributes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customAttributes"))

    @custom_attributes.setter
    def custom_attributes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f81b22ae3d4b4eeee8f29302a5f199102babbfeeac878b18b26c28cec92286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value)

    @builtins.property
    @jsii.member(jsii_name="customLicenseAcquisitionUrlTemplate")
    def custom_license_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customLicenseAcquisitionUrlTemplate"))

    @custom_license_acquisition_url_template.setter
    def custom_license_acquisition_url_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eda5a43db3e9deff6dcbc04dcee89e003f8add169fdbb9c769a8aa04421eca48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customLicenseAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d90d6e7b999d3c281d3e00e14481fca2b6e928f04d6bd16c1c014c127626c513)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencEnabledProtocols",
    jsii_struct_bases=[],
    name_mapping={
        "dash": "dash",
        "download": "download",
        "hls": "hls",
        "smooth_streaming": "smoothStreaming",
    },
)
class MediaStreamingPolicyCommonEncryptionCencEnabledProtocols:
    def __init__(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e09af986d6ac2499aedb220d3b8daec7897d9e7ae8ffc812249f1f96149a306d)
            check_type(argname="argument dash", value=dash, expected_type=type_hints["dash"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument hls", value=hls, expected_type=type_hints["hls"])
            check_type(argname="argument smooth_streaming", value=smooth_streaming, expected_type=type_hints["smooth_streaming"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dash is not None:
            self._values["dash"] = dash
        if download is not None:
            self._values["download"] = download
        if hls is not None:
            self._values["hls"] = hls
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming

    @builtins.property
    def dash(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.'''
        result = self._values.get("dash")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.'''
        result = self._values.get("download")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.'''
        result = self._values.get("hls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyCommonEncryptionCencEnabledProtocols(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyCommonEncryptionCencEnabledProtocolsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencEnabledProtocolsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e0ffff93f4a33e9bdf699c4b0da83a58e1e35fb6ca5faa120132bccb9e98ced)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDash")
    def reset_dash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDash", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetHls")
    def reset_hls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHls", []))

    @jsii.member(jsii_name="resetSmoothStreaming")
    def reset_smooth_streaming(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmoothStreaming", []))

    @builtins.property
    @jsii.member(jsii_name="dashInput")
    def dash_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dashInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="hlsInput")
    def hls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hlsInput"))

    @builtins.property
    @jsii.member(jsii_name="smoothStreamingInput")
    def smooth_streaming_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "smoothStreamingInput"))

    @builtins.property
    @jsii.member(jsii_name="dash")
    def dash(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dash"))

    @dash.setter
    def dash(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__937729370b28437bf6c69443173c9ead21f327b646bd7839bceca2949437c6eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dash", value)

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "download"))

    @download.setter
    def download(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6123f542cb33a5bf58c46e8a6c9ed0fed427cc00350781cc3c0ef057c610f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value)

    @builtins.property
    @jsii.member(jsii_name="hls")
    def hls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hls"))

    @hls.setter
    def hls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e404ef10d056b6a8c117ab9b2374a04c35276ec8bd08591c48c4b99e0bee2837)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hls", value)

    @builtins.property
    @jsii.member(jsii_name="smoothStreaming")
    def smooth_streaming(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "smoothStreaming"))

    @smooth_streaming.setter
    def smooth_streaming(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9074ac3b8289533f75eeeeecc5352c1779cfd13019a3ca5c883f1bf7331ed5a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smoothStreaming", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86eee1014fd79ccecd826e4bab205431539bed119d4b6fbc66eb8e9eae416d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyCommonEncryptionCencOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyCommonEncryptionCencOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d23bb54baa8204ad7a37438c701807627e2d5ebaac190251b4fb75acb577a2c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putClearKeyEncryption")
    def put_clear_key_encryption(
        self,
        *,
        custom_keys_acquisition_url_template: builtins.str,
    ) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption(
            custom_keys_acquisition_url_template=custom_keys_acquisition_url_template
        )

        return typing.cast(None, jsii.invoke(self, "putClearKeyEncryption", [value]))

    @jsii.member(jsii_name="putClearTrack")
    def put_clear_track(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3feecf87ff9d29721de5c48028986bc8786a4256e6e30384f7403b7aabe07a2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putClearTrack", [value]))

    @jsii.member(jsii_name="putContentKeyToTrackMapping")
    def put_content_key_to_track_mapping(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__428fae5abaf72dbeed271e7673d032f5f7238f6dc6765a129e85627c386b7a2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putContentKeyToTrackMapping", [value]))

    @jsii.member(jsii_name="putDefaultContentKey")
    def put_default_content_key(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCencDefaultContentKey(
            label=label, policy_name=policy_name
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultContentKey", [value]))

    @jsii.member(jsii_name="putDrmPlayready")
    def put_drm_playready(
        self,
        *,
        custom_attributes: typing.Optional[builtins.str] = None,
        custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param custom_attributes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_attributes MediaStreamingPolicy#custom_attributes}.
        :param custom_license_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_license_acquisition_url_template MediaStreamingPolicy#custom_license_acquisition_url_template}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCencDrmPlayready(
            custom_attributes=custom_attributes,
            custom_license_acquisition_url_template=custom_license_acquisition_url_template,
        )

        return typing.cast(None, jsii.invoke(self, "putDrmPlayready", [value]))

    @jsii.member(jsii_name="putEnabledProtocols")
    def put_enabled_protocols(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        value = MediaStreamingPolicyCommonEncryptionCencEnabledProtocols(
            dash=dash, download=download, hls=hls, smooth_streaming=smooth_streaming
        )

        return typing.cast(None, jsii.invoke(self, "putEnabledProtocols", [value]))

    @jsii.member(jsii_name="resetClearKeyEncryption")
    def reset_clear_key_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClearKeyEncryption", []))

    @jsii.member(jsii_name="resetClearTrack")
    def reset_clear_track(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClearTrack", []))

    @jsii.member(jsii_name="resetContentKeyToTrackMapping")
    def reset_content_key_to_track_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentKeyToTrackMapping", []))

    @jsii.member(jsii_name="resetDefaultContentKey")
    def reset_default_content_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultContentKey", []))

    @jsii.member(jsii_name="resetDrmPlayready")
    def reset_drm_playready(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrmPlayready", []))

    @jsii.member(jsii_name="resetDrmWidevineCustomLicenseAcquisitionUrlTemplate")
    def reset_drm_widevine_custom_license_acquisition_url_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrmWidevineCustomLicenseAcquisitionUrlTemplate", []))

    @jsii.member(jsii_name="resetEnabledProtocols")
    def reset_enabled_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledProtocols", []))

    @builtins.property
    @jsii.member(jsii_name="clearKeyEncryption")
    def clear_key_encryption(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencClearKeyEncryptionOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencClearKeyEncryptionOutputReference, jsii.get(self, "clearKeyEncryption"))

    @builtins.property
    @jsii.member(jsii_name="clearTrack")
    def clear_track(self) -> MediaStreamingPolicyCommonEncryptionCencClearTrackList:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencClearTrackList, jsii.get(self, "clearTrack"))

    @builtins.property
    @jsii.member(jsii_name="contentKeyToTrackMapping")
    def content_key_to_track_mapping(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingList:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingList, jsii.get(self, "contentKeyToTrackMapping"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKey")
    def default_content_key(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencDefaultContentKeyOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencDefaultContentKeyOutputReference, jsii.get(self, "defaultContentKey"))

    @builtins.property
    @jsii.member(jsii_name="drmPlayready")
    def drm_playready(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencDrmPlayreadyOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencDrmPlayreadyOutputReference, jsii.get(self, "drmPlayready"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocols")
    def enabled_protocols(
        self,
    ) -> MediaStreamingPolicyCommonEncryptionCencEnabledProtocolsOutputReference:
        return typing.cast(MediaStreamingPolicyCommonEncryptionCencEnabledProtocolsOutputReference, jsii.get(self, "enabledProtocols"))

    @builtins.property
    @jsii.member(jsii_name="clearKeyEncryptionInput")
    def clear_key_encryption_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption], jsii.get(self, "clearKeyEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="clearTrackInput")
    def clear_track_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]], jsii.get(self, "clearTrackInput"))

    @builtins.property
    @jsii.member(jsii_name="contentKeyToTrackMappingInput")
    def content_key_to_track_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]], jsii.get(self, "contentKeyToTrackMappingInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKeyInput")
    def default_content_key_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey], jsii.get(self, "defaultContentKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="drmPlayreadyInput")
    def drm_playready_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready], jsii.get(self, "drmPlayreadyInput"))

    @builtins.property
    @jsii.member(jsii_name="drmWidevineCustomLicenseAcquisitionUrlTemplateInput")
    def drm_widevine_custom_license_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "drmWidevineCustomLicenseAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocolsInput")
    def enabled_protocols_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols], jsii.get(self, "enabledProtocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="drmWidevineCustomLicenseAcquisitionUrlTemplate")
    def drm_widevine_custom_license_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "drmWidevineCustomLicenseAcquisitionUrlTemplate"))

    @drm_widevine_custom_license_acquisition_url_template.setter
    def drm_widevine_custom_license_acquisition_url_template(
        self,
        value: builtins.str,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2dd59fd2ec10680d56ab27119a4f6c25f59afc9c2384783981261fd51d31a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drmWidevineCustomLicenseAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCenc]:
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCenc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyCommonEncryptionCenc],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5904c93fe96e8f068d4f5a8832df3f24b189f2d79bc34bb84535ac135860046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "media_services_account_name": "mediaServicesAccountName",
        "name": "name",
        "resource_group_name": "resourceGroupName",
        "common_encryption_cbcs": "commonEncryptionCbcs",
        "common_encryption_cenc": "commonEncryptionCenc",
        "default_content_key_policy_name": "defaultContentKeyPolicyName",
        "envelope_encryption": "envelopeEncryption",
        "id": "id",
        "no_encryption_enabled_protocols": "noEncryptionEnabledProtocols",
        "timeouts": "timeouts",
    },
)
class MediaStreamingPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        media_services_account_name: builtins.str,
        name: builtins.str,
        resource_group_name: builtins.str,
        common_encryption_cbcs: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcs, typing.Dict[builtins.str, typing.Any]]] = None,
        common_encryption_cenc: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCenc, typing.Dict[builtins.str, typing.Any]]] = None,
        default_content_key_policy_name: typing.Optional[builtins.str] = None,
        envelope_encryption: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryption", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        no_encryption_enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyNoEncryptionEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["MediaStreamingPolicyTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param media_services_account_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#media_services_account_name MediaStreamingPolicy#media_services_account_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#name MediaStreamingPolicy#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#resource_group_name MediaStreamingPolicy#resource_group_name}.
        :param common_encryption_cbcs: common_encryption_cbcs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cbcs MediaStreamingPolicy#common_encryption_cbcs}
        :param common_encryption_cenc: common_encryption_cenc block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cenc MediaStreamingPolicy#common_encryption_cenc}
        :param default_content_key_policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key_policy_name MediaStreamingPolicy#default_content_key_policy_name}.
        :param envelope_encryption: envelope_encryption block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#envelope_encryption MediaStreamingPolicy#envelope_encryption}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#id MediaStreamingPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param no_encryption_enabled_protocols: no_encryption_enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#no_encryption_enabled_protocols MediaStreamingPolicy#no_encryption_enabled_protocols}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#timeouts MediaStreamingPolicy#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(common_encryption_cbcs, dict):
            common_encryption_cbcs = MediaStreamingPolicyCommonEncryptionCbcs(**common_encryption_cbcs)
        if isinstance(common_encryption_cenc, dict):
            common_encryption_cenc = MediaStreamingPolicyCommonEncryptionCenc(**common_encryption_cenc)
        if isinstance(envelope_encryption, dict):
            envelope_encryption = MediaStreamingPolicyEnvelopeEncryption(**envelope_encryption)
        if isinstance(no_encryption_enabled_protocols, dict):
            no_encryption_enabled_protocols = MediaStreamingPolicyNoEncryptionEnabledProtocols(**no_encryption_enabled_protocols)
        if isinstance(timeouts, dict):
            timeouts = MediaStreamingPolicyTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4878ea4131a87d6d60113eddadf694d41b21b62e1465ce6346541ff147d60e0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument media_services_account_name", value=media_services_account_name, expected_type=type_hints["media_services_account_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument common_encryption_cbcs", value=common_encryption_cbcs, expected_type=type_hints["common_encryption_cbcs"])
            check_type(argname="argument common_encryption_cenc", value=common_encryption_cenc, expected_type=type_hints["common_encryption_cenc"])
            check_type(argname="argument default_content_key_policy_name", value=default_content_key_policy_name, expected_type=type_hints["default_content_key_policy_name"])
            check_type(argname="argument envelope_encryption", value=envelope_encryption, expected_type=type_hints["envelope_encryption"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument no_encryption_enabled_protocols", value=no_encryption_enabled_protocols, expected_type=type_hints["no_encryption_enabled_protocols"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "media_services_account_name": media_services_account_name,
            "name": name,
            "resource_group_name": resource_group_name,
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
        if common_encryption_cbcs is not None:
            self._values["common_encryption_cbcs"] = common_encryption_cbcs
        if common_encryption_cenc is not None:
            self._values["common_encryption_cenc"] = common_encryption_cenc
        if default_content_key_policy_name is not None:
            self._values["default_content_key_policy_name"] = default_content_key_policy_name
        if envelope_encryption is not None:
            self._values["envelope_encryption"] = envelope_encryption
        if id is not None:
            self._values["id"] = id
        if no_encryption_enabled_protocols is not None:
            self._values["no_encryption_enabled_protocols"] = no_encryption_enabled_protocols
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
    def media_services_account_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#media_services_account_name MediaStreamingPolicy#media_services_account_name}.'''
        result = self._values.get("media_services_account_name")
        assert result is not None, "Required property 'media_services_account_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#name MediaStreamingPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#resource_group_name MediaStreamingPolicy#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_encryption_cbcs(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs]:
        '''common_encryption_cbcs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cbcs MediaStreamingPolicy#common_encryption_cbcs}
        '''
        result = self._values.get("common_encryption_cbcs")
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs], result)

    @builtins.property
    def common_encryption_cenc(
        self,
    ) -> typing.Optional[MediaStreamingPolicyCommonEncryptionCenc]:
        '''common_encryption_cenc block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#common_encryption_cenc MediaStreamingPolicy#common_encryption_cenc}
        '''
        result = self._values.get("common_encryption_cenc")
        return typing.cast(typing.Optional[MediaStreamingPolicyCommonEncryptionCenc], result)

    @builtins.property
    def default_content_key_policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key_policy_name MediaStreamingPolicy#default_content_key_policy_name}.'''
        result = self._values.get("default_content_key_policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def envelope_encryption(
        self,
    ) -> typing.Optional["MediaStreamingPolicyEnvelopeEncryption"]:
        '''envelope_encryption block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#envelope_encryption MediaStreamingPolicy#envelope_encryption}
        '''
        result = self._values.get("envelope_encryption")
        return typing.cast(typing.Optional["MediaStreamingPolicyEnvelopeEncryption"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#id MediaStreamingPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_encryption_enabled_protocols(
        self,
    ) -> typing.Optional["MediaStreamingPolicyNoEncryptionEnabledProtocols"]:
        '''no_encryption_enabled_protocols block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#no_encryption_enabled_protocols MediaStreamingPolicy#no_encryption_enabled_protocols}
        '''
        result = self._values.get("no_encryption_enabled_protocols")
        return typing.cast(typing.Optional["MediaStreamingPolicyNoEncryptionEnabledProtocols"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MediaStreamingPolicyTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#timeouts MediaStreamingPolicy#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MediaStreamingPolicyTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryption",
    jsii_struct_bases=[],
    name_mapping={
        "custom_keys_acquisition_url_template": "customKeysAcquisitionUrlTemplate",
        "default_content_key": "defaultContentKey",
        "enabled_protocols": "enabledProtocols",
    },
)
class MediaStreamingPolicyEnvelopeEncryption:
    def __init__(
        self,
        *,
        custom_keys_acquisition_url_template: typing.Optional[builtins.str] = None,
        default_content_key: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey", typing.Dict[builtins.str, typing.Any]]] = None,
        enabled_protocols: typing.Optional[typing.Union["MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param custom_keys_acquisition_url_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.
        :param default_content_key: default_content_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        :param enabled_protocols: enabled_protocols block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        if isinstance(default_content_key, dict):
            default_content_key = MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey(**default_content_key)
        if isinstance(enabled_protocols, dict):
            enabled_protocols = MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols(**enabled_protocols)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cb90eb32880463f4755042dcc24463ef61f373f9f768c847215c76ab1b7b1ea)
            check_type(argname="argument custom_keys_acquisition_url_template", value=custom_keys_acquisition_url_template, expected_type=type_hints["custom_keys_acquisition_url_template"])
            check_type(argname="argument default_content_key", value=default_content_key, expected_type=type_hints["default_content_key"])
            check_type(argname="argument enabled_protocols", value=enabled_protocols, expected_type=type_hints["enabled_protocols"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom_keys_acquisition_url_template is not None:
            self._values["custom_keys_acquisition_url_template"] = custom_keys_acquisition_url_template
        if default_content_key is not None:
            self._values["default_content_key"] = default_content_key
        if enabled_protocols is not None:
            self._values["enabled_protocols"] = enabled_protocols

    @builtins.property
    def custom_keys_acquisition_url_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#custom_keys_acquisition_url_template MediaStreamingPolicy#custom_keys_acquisition_url_template}.'''
        result = self._values.get("custom_keys_acquisition_url_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_content_key(
        self,
    ) -> typing.Optional["MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey"]:
        '''default_content_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#default_content_key MediaStreamingPolicy#default_content_key}
        '''
        result = self._values.get("default_content_key")
        return typing.cast(typing.Optional["MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey"], result)

    @builtins.property
    def enabled_protocols(
        self,
    ) -> typing.Optional["MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols"]:
        '''enabled_protocols block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#enabled_protocols MediaStreamingPolicy#enabled_protocols}
        '''
        result = self._values.get("enabled_protocols")
        return typing.cast(typing.Optional["MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyEnvelopeEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "policy_name": "policyName"},
)
class MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey:
    def __init__(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ca6f25f0551a0dd153fb894c36475cae74883daa66966617efce5dacfdbdf8c)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if label is not None:
            self._values["label"] = label
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyEnvelopeEncryptionDefaultContentKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryptionDefaultContentKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7a25400e13470a8d3a5fc794b5c58716157155c242369eb1a32712869aaad8e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12c0eb6c0b95c99da34c2a3ae8a166420d5155c710a3dc12479bf964c6c07f41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3717ca119ea2850866528a3403992476696011b1cbb0bd5a0c36465fc43ce077)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba858415766ab7f7853b69e30067bfb960dff97d38ebdad1fe77fbe731480594)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols",
    jsii_struct_bases=[],
    name_mapping={
        "dash": "dash",
        "download": "download",
        "hls": "hls",
        "smooth_streaming": "smoothStreaming",
    },
)
class MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols:
    def __init__(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5150d4e8b5bdf4a004910e828bce7804d9356181d40871a9d13a7515ded446d)
            check_type(argname="argument dash", value=dash, expected_type=type_hints["dash"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument hls", value=hls, expected_type=type_hints["hls"])
            check_type(argname="argument smooth_streaming", value=smooth_streaming, expected_type=type_hints["smooth_streaming"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dash is not None:
            self._values["dash"] = dash
        if download is not None:
            self._values["download"] = download
        if hls is not None:
            self._values["hls"] = hls
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming

    @builtins.property
    def dash(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.'''
        result = self._values.get("dash")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.'''
        result = self._values.get("download")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.'''
        result = self._values.get("hls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyEnvelopeEncryptionEnabledProtocolsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryptionEnabledProtocolsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55561b7e019fe5fb88a2b8df78372952a07bfdb6747b01a72171a5c9840eeedd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDash")
    def reset_dash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDash", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetHls")
    def reset_hls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHls", []))

    @jsii.member(jsii_name="resetSmoothStreaming")
    def reset_smooth_streaming(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmoothStreaming", []))

    @builtins.property
    @jsii.member(jsii_name="dashInput")
    def dash_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dashInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="hlsInput")
    def hls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hlsInput"))

    @builtins.property
    @jsii.member(jsii_name="smoothStreamingInput")
    def smooth_streaming_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "smoothStreamingInput"))

    @builtins.property
    @jsii.member(jsii_name="dash")
    def dash(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dash"))

    @dash.setter
    def dash(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec473d2e92063c88c550211f5c0549d34877ec604d6d853a44d44ff293be9be5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dash", value)

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "download"))

    @download.setter
    def download(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__035ec22085ae9af048f067d403a69e06e735f8c123b13c4fb1ff99b57d57d04c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value)

    @builtins.property
    @jsii.member(jsii_name="hls")
    def hls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hls"))

    @hls.setter
    def hls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e716bd50fd7b9581e9a0adfca77d085e5df71da05a09c12c99b5f0d79fac16f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hls", value)

    @builtins.property
    @jsii.member(jsii_name="smoothStreaming")
    def smooth_streaming(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "smoothStreaming"))

    @smooth_streaming.setter
    def smooth_streaming(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53627a170184528d3f95c290202ef12e95b2af2547b35486cdd2abeb21ba1fd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smoothStreaming", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c82288ec29e1e3a70a5e72b3a91d0a9ea0bd6f560ffa32988e1421dba4fa9b73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaStreamingPolicyEnvelopeEncryptionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyEnvelopeEncryptionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__738afe53963b45a433fda2d717c039c38ed792897db89f8cc2cfbf2ac1eff1e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDefaultContentKey")
    def put_default_content_key(
        self,
        *,
        label: typing.Optional[builtins.str] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#label MediaStreamingPolicy#label}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#policy_name MediaStreamingPolicy#policy_name}.
        '''
        value = MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey(
            label=label, policy_name=policy_name
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultContentKey", [value]))

    @jsii.member(jsii_name="putEnabledProtocols")
    def put_enabled_protocols(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        value = MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols(
            dash=dash, download=download, hls=hls, smooth_streaming=smooth_streaming
        )

        return typing.cast(None, jsii.invoke(self, "putEnabledProtocols", [value]))

    @jsii.member(jsii_name="resetCustomKeysAcquisitionUrlTemplate")
    def reset_custom_keys_acquisition_url_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomKeysAcquisitionUrlTemplate", []))

    @jsii.member(jsii_name="resetDefaultContentKey")
    def reset_default_content_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultContentKey", []))

    @jsii.member(jsii_name="resetEnabledProtocols")
    def reset_enabled_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledProtocols", []))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKey")
    def default_content_key(
        self,
    ) -> MediaStreamingPolicyEnvelopeEncryptionDefaultContentKeyOutputReference:
        return typing.cast(MediaStreamingPolicyEnvelopeEncryptionDefaultContentKeyOutputReference, jsii.get(self, "defaultContentKey"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocols")
    def enabled_protocols(
        self,
    ) -> MediaStreamingPolicyEnvelopeEncryptionEnabledProtocolsOutputReference:
        return typing.cast(MediaStreamingPolicyEnvelopeEncryptionEnabledProtocolsOutputReference, jsii.get(self, "enabledProtocols"))

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplateInput")
    def custom_keys_acquisition_url_template_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customKeysAcquisitionUrlTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultContentKeyInput")
    def default_content_key_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey]:
        return typing.cast(typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey], jsii.get(self, "defaultContentKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledProtocolsInput")
    def enabled_protocols_input(
        self,
    ) -> typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols], jsii.get(self, "enabledProtocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="customKeysAcquisitionUrlTemplate")
    def custom_keys_acquisition_url_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customKeysAcquisitionUrlTemplate"))

    @custom_keys_acquisition_url_template.setter
    def custom_keys_acquisition_url_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47551f261d8b327db99fed51eebb829f4240d581ec50d74e465634bfe739d977)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customKeysAcquisitionUrlTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MediaStreamingPolicyEnvelopeEncryption]:
        return typing.cast(typing.Optional[MediaStreamingPolicyEnvelopeEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyEnvelopeEncryption],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715cd8d19e7a92f010588a1312e9d65d6ea823863a01d0be6545ec67e6e0f1ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyNoEncryptionEnabledProtocols",
    jsii_struct_bases=[],
    name_mapping={
        "dash": "dash",
        "download": "download",
        "hls": "hls",
        "smooth_streaming": "smoothStreaming",
    },
)
class MediaStreamingPolicyNoEncryptionEnabledProtocols:
    def __init__(
        self,
        *,
        dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param dash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.
        :param hls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f083587dd133afccaa6be026dc81882afcc768870d89a0a2d44f6468b78108dc)
            check_type(argname="argument dash", value=dash, expected_type=type_hints["dash"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument hls", value=hls, expected_type=type_hints["hls"])
            check_type(argname="argument smooth_streaming", value=smooth_streaming, expected_type=type_hints["smooth_streaming"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dash is not None:
            self._values["dash"] = dash
        if download is not None:
            self._values["download"] = download
        if hls is not None:
            self._values["hls"] = hls
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming

    @builtins.property
    def dash(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#dash MediaStreamingPolicy#dash}.'''
        result = self._values.get("dash")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#download MediaStreamingPolicy#download}.'''
        result = self._values.get("download")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#hls MediaStreamingPolicy#hls}.'''
        result = self._values.get("hls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#smooth_streaming MediaStreamingPolicy#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyNoEncryptionEnabledProtocols(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyNoEncryptionEnabledProtocolsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyNoEncryptionEnabledProtocolsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__73d2665195eba89e489e69054cb7937e793854448cf8607cd5d54174e1b2ba5f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDash")
    def reset_dash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDash", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetHls")
    def reset_hls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHls", []))

    @jsii.member(jsii_name="resetSmoothStreaming")
    def reset_smooth_streaming(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmoothStreaming", []))

    @builtins.property
    @jsii.member(jsii_name="dashInput")
    def dash_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dashInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="hlsInput")
    def hls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hlsInput"))

    @builtins.property
    @jsii.member(jsii_name="smoothStreamingInput")
    def smooth_streaming_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "smoothStreamingInput"))

    @builtins.property
    @jsii.member(jsii_name="dash")
    def dash(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dash"))

    @dash.setter
    def dash(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13ed9d75a632d7896c7b641967584095cd66b9224f9b0aff861e3fa32c68ecb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dash", value)

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "download"))

    @download.setter
    def download(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e818d3b051fbe60a96bee37254798b5fa9278d290f5aabd67ffd5506964f22b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value)

    @builtins.property
    @jsii.member(jsii_name="hls")
    def hls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hls"))

    @hls.setter
    def hls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e555f99f25b511c676e200f8aa90d8f2b4e962d5d02720d73d0242d556050dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hls", value)

    @builtins.property
    @jsii.member(jsii_name="smoothStreaming")
    def smooth_streaming(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "smoothStreaming"))

    @smooth_streaming.setter
    def smooth_streaming(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b452c41d75701c3b696306783c8fe3df95647b45f70b6fb8199a3143262490f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smoothStreaming", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaStreamingPolicyNoEncryptionEnabledProtocols]:
        return typing.cast(typing.Optional[MediaStreamingPolicyNoEncryptionEnabledProtocols], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaStreamingPolicyNoEncryptionEnabledProtocols],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66bb6b94ce85b074c94d4ff456c77755111286089ade97fb874a415867501b94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "read": "read"},
)
class MediaStreamingPolicyTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#create MediaStreamingPolicy#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#delete MediaStreamingPolicy#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#read MediaStreamingPolicy#read}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42c45c8637f6ce20fd4230f054db64bbefda9a4ad734f3da73d6eb2e3d479693)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if read is not None:
            self._values["read"] = read

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#create MediaStreamingPolicy#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#delete MediaStreamingPolicy#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_streaming_policy#read MediaStreamingPolicy#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaStreamingPolicyTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaStreamingPolicyTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaStreamingPolicy.MediaStreamingPolicyTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__090e66135f5e1c317dbc9a7660d407266f0432c7e2543ae1aa88a13603b7be58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92ba4c208fe9a7b155221b7399a00011d87510bebe2cfec4be9e905e89b35b52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b463a42a5ee4a03592af84e3615f89c7db0db856f8d639ae1df843e36fe3bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98e5cd9e067c7404426aff6c241112f88bb869cbaa3be8f4f973678beed920c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__634394e79a20c88a5f866ee2fc9b0a85994cf73ebdc5af85f33fec236ad324fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "MediaStreamingPolicy",
    "MediaStreamingPolicyCommonEncryptionCbcs",
    "MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption",
    "MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryptionOutputReference",
    "MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey",
    "MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKeyOutputReference",
    "MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay",
    "MediaStreamingPolicyCommonEncryptionCbcsDrmFairplayOutputReference",
    "MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols",
    "MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocolsOutputReference",
    "MediaStreamingPolicyCommonEncryptionCbcsOutputReference",
    "MediaStreamingPolicyCommonEncryptionCenc",
    "MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption",
    "MediaStreamingPolicyCommonEncryptionCencClearKeyEncryptionOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencClearTrack",
    "MediaStreamingPolicyCommonEncryptionCencClearTrackCondition",
    "MediaStreamingPolicyCommonEncryptionCencClearTrackConditionList",
    "MediaStreamingPolicyCommonEncryptionCencClearTrackConditionOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencClearTrackList",
    "MediaStreamingPolicyCommonEncryptionCencClearTrackOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingList",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionList",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackConditionOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackList",
    "MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencDefaultContentKey",
    "MediaStreamingPolicyCommonEncryptionCencDefaultContentKeyOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencDrmPlayready",
    "MediaStreamingPolicyCommonEncryptionCencDrmPlayreadyOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencEnabledProtocols",
    "MediaStreamingPolicyCommonEncryptionCencEnabledProtocolsOutputReference",
    "MediaStreamingPolicyCommonEncryptionCencOutputReference",
    "MediaStreamingPolicyConfig",
    "MediaStreamingPolicyEnvelopeEncryption",
    "MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey",
    "MediaStreamingPolicyEnvelopeEncryptionDefaultContentKeyOutputReference",
    "MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols",
    "MediaStreamingPolicyEnvelopeEncryptionEnabledProtocolsOutputReference",
    "MediaStreamingPolicyEnvelopeEncryptionOutputReference",
    "MediaStreamingPolicyNoEncryptionEnabledProtocols",
    "MediaStreamingPolicyNoEncryptionEnabledProtocolsOutputReference",
    "MediaStreamingPolicyTimeouts",
    "MediaStreamingPolicyTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__16257c9d0eb4ef2573bad9116d8bb571c21ba680834a3edd53f19a45ea21697c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    media_services_account_name: builtins.str,
    name: builtins.str,
    resource_group_name: builtins.str,
    common_encryption_cbcs: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcs, typing.Dict[builtins.str, typing.Any]]] = None,
    common_encryption_cenc: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCenc, typing.Dict[builtins.str, typing.Any]]] = None,
    default_content_key_policy_name: typing.Optional[builtins.str] = None,
    envelope_encryption: typing.Optional[typing.Union[MediaStreamingPolicyEnvelopeEncryption, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    no_encryption_enabled_protocols: typing.Optional[typing.Union[MediaStreamingPolicyNoEncryptionEnabledProtocols, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__badf15e349fea53ef2d71af9be9e08e1d57078eba7ad82a37537c9ad9e35e289(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff0b82166f2e3cc5b8a19afc3ad1c2953313cd570160adc319cc9f2938e42cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ef24ac8e44129183e202d3955033b3db5d2e961074bccd7c531c7b4de79f4ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1817cf563292950dd7674c6e5943446c3ae92dabcada03aa91a431160cb1913(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2343a6be28faf7afc420b5544b2d2a12504c3003edac9bd7d75e2d1e31b3b2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f2f0b8c5454c08c0821875d5ee9a811693b5af751cf21119b10a0a410a401e(
    *,
    clear_key_encryption: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption, typing.Dict[builtins.str, typing.Any]]] = None,
    default_content_key: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey, typing.Dict[builtins.str, typing.Any]]] = None,
    drm_fairplay: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay, typing.Dict[builtins.str, typing.Any]]] = None,
    enabled_protocols: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__316cd40e5e113548b4dd05a2290c1561e088dacc488ddb7d75478f37e91631e9(
    *,
    custom_keys_acquisition_url_template: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c125f731846ffcf68c97d67938a51f3a82299eedf9fdbdaef7c5bd324fe2a1c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__001165656b581fc1a8a0af1c4e34385f9b353528d0371adc71acec43585447f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddec1ba4603f1fb73d0918c23197bacddd65f6b36bdc4a060c2cc8145eef27d5(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsClearKeyEncryption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ede7ee0570a9ddbb9ba5a5caef594fa2f4159fb46e0a51f5d0b9e09adc2370db(
    *,
    label: typing.Optional[builtins.str] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5b5e607ad30a9be53e0b83067853e5b2f214f011af2f66e2b09b662dde3290e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5229cfd5cd24821db6983663746c27a69d3f094ed8ede51ced1b86c50cda2bb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1036a6fad843a59ada93c3d43b1a3e21c891d7e362e29a33f9e6e8919d45521(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7ca0fdc5283ee78c87188f8ed20d4dbe611d81dcfda261877001c3f673ecb6f(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDefaultContentKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7174b584ea9a9539ddac7668b51f26c8039cc313b13b9be2302fd9f6bf6efe70(
    *,
    allow_persistent_license: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4bdcfacaea39711c881a5a7b1df0a28f2c923be9926d2c357e26f4e09cd7c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b8d44f09612e02d6504bca4a6d5c4bac69b728992ca8012c1cdbe31f11dab0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b0640991de63328e9e26599b124c108242e36cc0af810c79669cac1201d5fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f39d4bc20f79fb2b9feac05ea89512168f7722552b1094672ed6681638844a0c(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsDrmFairplay],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bfb76a64ab70b7fa8dbb552b01c261074be771e95eb8b70f0c350d035d993f1(
    *,
    dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a7dba195f8b13866dccb21db829241f95a19d59c337faa123ead142d4bc3cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16dc9c4d20b9742b29840125966dc4d14be4c069d4dd25bfafea21f1bf7351f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35e2afb95a5e576459b1bdb5d4458fa6cbc29abe27c58158f7a3108d18c2148a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b1518de1a2d5493cb51432ea461754bb7fab40bd017b85dfbe6ca8793a2202(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb87cbdc0363e774765dc7994a0dcafa629f1477bbf6d82e502b0e84de53c7a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e516a5b4e7e65edd93a26dc50caf0c01de1f5862601b15452ff5be4adae5610f(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcsEnabledProtocols],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1f1b13db911520be88377e7a65308d43898860c66ba03d141aa2c83c663337(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc579000a5aa76493f51ea936530d93c896241a795afb830eaebf1658e2cab3(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCbcs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df29267f26859d504dd3a49915c66d747218279c77bb061c01f0e4915caeb732(
    *,
    clear_key_encryption: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption, typing.Dict[builtins.str, typing.Any]]] = None,
    clear_track: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, typing.Dict[builtins.str, typing.Any]]]]] = None,
    content_key_to_track_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, typing.Dict[builtins.str, typing.Any]]]]] = None,
    default_content_key: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey, typing.Dict[builtins.str, typing.Any]]] = None,
    drm_playready: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencDrmPlayready, typing.Dict[builtins.str, typing.Any]]] = None,
    drm_widevine_custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
    enabled_protocols: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11904a44b651475f69b30d59a1c896edf1f07c0ffa08806bf6f25fb75a1b2105(
    *,
    custom_keys_acquisition_url_template: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d7095a5425f0e0fdda98f4c421e44126dbb6403ab9a79983a867cd54ecea6cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06fd3a85017e4e1e227dd1466b6283f0cece8e8e9f3ea56a307f7772bfa3868d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b02ab6f18842f49657f6d5a26473bcce5c129c96de4eed847f6e76b84fbda3(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencClearKeyEncryption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0303e613494f1839a8887ffe87a3463a9e908fad8004e7189bac71923282510e(
    *,
    condition: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5dec3b34520e5def1df53acfa25ba44490a4c6cfbd869c53465ccb4be558781(
    *,
    operation: builtins.str,
    property: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a11ab4499b63736092e806525298da8aa62d944bedcbd36870b9aec84dfc0808(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524c41dc24d4861b1edb572d7a5279c53894d9240ec3d1642dbb885f6101527b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__836fb480937cd060ad8841c3ac13182c260cc941041226570cdb1ac2b07f3460(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee4de28939926676f46cc8f1aae6db98e234c77b77d38be79d2ff794893f8341(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dc5b33e718fc9140dc9358c3adc650a6244995cdb1341394431344eae2f4e24(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce4f64e846f3e17776b0ae8b06d1df395f4d3d2a860bc9c7c7bad6f7045262f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c5210c14b6c6dd62c52dfe273cf433a61918ea4af72dcbc6978a267e2a69d0e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89cb58d148ecf84fcab20851caa44496dc76eaedee52e3083990912115ba39fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bf7e710c1a74badd2339121f58f46a68efac1136c537b5f726c9aa025e14629(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd5cfee3d02610008ccd725debea90db0c8894bbe4565478d30f79efa418498e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63f7cc2c4e13f505743df9a9ea32b3839061e50ab9d4472fc4960e81fd92f831(
    value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5006a11292332c42caf92c9f039d6a4562279dd5870b1fb4098f3d73ff0dc58c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce72bfdf762dfbd021a2f308fe285ebdfa3f4dc10c075ee7ec1203f4dad0b403(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eef5fdca252185f9ba494608c6234a05ab11fe0773cea0aa620d858f55a7fea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3edcf5e28d479deb526368d1d283aeeaad30fe6599b7dd2d62ad1478bec1519f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e902c496cafa08a637382809c96826e322dfdddec3bc78f3d69a121471a8239(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28e3d218fcbad854b6b9de32ecbab96c2b3723a3450606f5710c7e465f56d750(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencClearTrack]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692cca7540d607e416337bf9a465e256061152477e60fce74dce6e855fba665c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a291a673f3fa59e05f712b51772ad2311a719dbdb159a749a0fefd00e48ffd8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59aaacacc27d0c947d3a7cf45aba859d9e0ed43368570a598a261b2e7a2469fe(
    value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc95d9831b76ca3bb505d8f6cba491809d989a66b464de34e9da8d22dd74529b(
    *,
    track: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, typing.Dict[builtins.str, typing.Any]]]],
    label: typing.Optional[builtins.str] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__757c4be1630811db5c17ad4832b9a47b8e63af103a39ebf4829c986bbe19cefa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb3ce19cd79c279a4c3384a02136b24c0e407262b9a77da22c271f728510af35(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e171f3d39facdf25c8fd18dc83b5a4e3b29015ccf78f6d70343597eb8fa552a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eca202e806dcc97cb320ed91da3f9aff747d5991e3f97ae18934b7b9a4e8a9f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54210a75b1016938053e441ec379b47f1b62bd0965d7144d07758ca489bc6ded(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68a869ced7be3f98b0dc23a3c1692f9990bb4c958b2092ed42b8b3fefa42c02e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164ad456549161b80b0ac41c6f239022a819e372e7a91cdbffda12f157e3c924(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc1a400c5b2a1619186d3d4d7948a63a3f0c8dcbf5ed7b7eaf791b01a00f9441(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15099aaf8c9c5def02b0a5f3b6baa460d43993ce4123367ee6a254e6445801f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778b4b47857cc59afb31a9ca35c649ee4eec93167f2197f59b29c269259b00f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4738a67cbb88c3695bb5c093b28eb8fab1fdc0dc189a70bb85417f86091470a0(
    value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42a84e632257a3d026d91d5dc12597e92126962fa16615c865d93c75c146c9b8(
    *,
    condition: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e61ec0a3011174a67c063da6033f96a33ef48d72daef3dd3e410703b0e931b(
    *,
    operation: builtins.str,
    property: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6adc6eac05f73c7870f7249cae346fe0f4661f4dc708e1b4a99ff500a3639632(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b923fd575e14157497342d7cfeb0b1bbab74ac4bdc063aecaecfecb8d3eab676(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d124f4a83a5564c6b9af05c44b45083a9f649a8ca1c4b845ff1bf27ed8d6c4bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6c1a1faf6d5403bf2c0e6fd68765abaa06d65de6d9f85ead791d2c2479d783f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8d30e09d0829cc9d6f9b672f0b0b17fb8bb44d74d7a99a24dd908f77f659492(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45e1660984ce4672330347aa20ba2b422820ac74f89419e7ebafde817b740130(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbd36327804ee5dd7aa5ab5420584634e907d6f1ec482f7dcfc9348077a42dbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9651f4df2b80137f3313169787f8b7e783462a91185eb0530f448185f46ae84(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f34483bdc17abb3505632fafcdadf9e8bbe4c26539deb3485527e0d3e282ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__361f2fd287013c5b2a800c71438dd4cf158e28a7098d8978d2ab470489b9b3b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6779672935f27f00c0197b3ae18bc37998c9ba346a28a8bcc9d8aa85728b4033(
    value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17a219864a162cbb8ddbc560df14ab8d4edaa0b3021a09d6490b58dd20b9c02a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd3f4c8ee33dffd25a170849a0ed6e5922370c836bc05b466a3c201a5e2343ab(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c7bb62b3365b4cb9c18bfb443ab1a909e7694214b77585b7efc27ba0f0e495(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70e8254b5acc6d9b3dc010bc9997fec2d881e800ee630dadfe793b20f4b65a82(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21332df13e056e8350d299c6c4a9f6f678c7209fc36f16d1f419a80216d89baf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f0ed63286d271f2f411ff9bf1b99d277b175ede9d45ff1c89cca549ea50137(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fc98ee20d3184daeb81e075fe3fab120f60ec11163e1083442bbf2f8717d95e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33709c8b30378b9e1e16b7effc95f33b7f6630f04633663055b10d36a9798ccf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrackCondition, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f56f08815bbfd5e99bc69fc5c6d1f087c303d6058979f218092b6e457c16d24(
    value: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMappingTrack, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3853958f59dba38974fce1224f059072240ec78ad75374837e8ce7214d36797e(
    *,
    label: typing.Optional[builtins.str] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4efef38efa531147056a619b8885d276abebcce8dd666191fccf7e40960e33e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48d533a5812e4d27fd6f3c75f7731990e44edd7d77a43377d7e5899f4eb61da6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33ba5a8438ae3f2140e0007cc666be8fb5aebaa88dc08125fa5218463c1b1ca5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__693978bf058aae51a1211ff26551943b154c86bd260ef228b7d301c15a5a309b(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencDefaultContentKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abd053b9c0cf786dd29ec64c2403e20da7a062060fb4d28235b6e45d5fd5cd4a(
    *,
    custom_attributes: typing.Optional[builtins.str] = None,
    custom_license_acquisition_url_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c730cac1e5d5ba96f3eac29fd7db2bad91c727880f0f108ea16e4c0b24c17c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f81b22ae3d4b4eeee8f29302a5f199102babbfeeac878b18b26c28cec92286(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eda5a43db3e9deff6dcbc04dcee89e003f8add169fdbb9c769a8aa04421eca48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d90d6e7b999d3c281d3e00e14481fca2b6e928f04d6bd16c1c014c127626c513(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencDrmPlayready],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e09af986d6ac2499aedb220d3b8daec7897d9e7ae8ffc812249f1f96149a306d(
    *,
    dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0ffff93f4a33e9bdf699c4b0da83a58e1e35fb6ca5faa120132bccb9e98ced(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937729370b28437bf6c69443173c9ead21f327b646bd7839bceca2949437c6eb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6123f542cb33a5bf58c46e8a6c9ed0fed427cc00350781cc3c0ef057c610f77(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e404ef10d056b6a8c117ab9b2374a04c35276ec8bd08591c48c4b99e0bee2837(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9074ac3b8289533f75eeeeecc5352c1779cfd13019a3ca5c883f1bf7331ed5a3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86eee1014fd79ccecd826e4bab205431539bed119d4b6fbc66eb8e9eae416d68(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCencEnabledProtocols],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23bb54baa8204ad7a37438c701807627e2d5ebaac190251b4fb75acb577a2c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3feecf87ff9d29721de5c48028986bc8786a4256e6e30384f7403b7aabe07a2f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencClearTrack, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__428fae5abaf72dbeed271e7673d032f5f7238f6dc6765a129e85627c386b7a2b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaStreamingPolicyCommonEncryptionCencContentKeyToTrackMapping, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2dd59fd2ec10680d56ab27119a4f6c25f59afc9c2384783981261fd51d31a1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5904c93fe96e8f068d4f5a8832df3f24b189f2d79bc34bb84535ac135860046(
    value: typing.Optional[MediaStreamingPolicyCommonEncryptionCenc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4878ea4131a87d6d60113eddadf694d41b21b62e1465ce6346541ff147d60e0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    media_services_account_name: builtins.str,
    name: builtins.str,
    resource_group_name: builtins.str,
    common_encryption_cbcs: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCbcs, typing.Dict[builtins.str, typing.Any]]] = None,
    common_encryption_cenc: typing.Optional[typing.Union[MediaStreamingPolicyCommonEncryptionCenc, typing.Dict[builtins.str, typing.Any]]] = None,
    default_content_key_policy_name: typing.Optional[builtins.str] = None,
    envelope_encryption: typing.Optional[typing.Union[MediaStreamingPolicyEnvelopeEncryption, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    no_encryption_enabled_protocols: typing.Optional[typing.Union[MediaStreamingPolicyNoEncryptionEnabledProtocols, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cb90eb32880463f4755042dcc24463ef61f373f9f768c847215c76ab1b7b1ea(
    *,
    custom_keys_acquisition_url_template: typing.Optional[builtins.str] = None,
    default_content_key: typing.Optional[typing.Union[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey, typing.Dict[builtins.str, typing.Any]]] = None,
    enabled_protocols: typing.Optional[typing.Union[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ca6f25f0551a0dd153fb894c36475cae74883daa66966617efce5dacfdbdf8c(
    *,
    label: typing.Optional[builtins.str] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7a25400e13470a8d3a5fc794b5c58716157155c242369eb1a32712869aaad8e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12c0eb6c0b95c99da34c2a3ae8a166420d5155c710a3dc12479bf964c6c07f41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3717ca119ea2850866528a3403992476696011b1cbb0bd5a0c36465fc43ce077(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba858415766ab7f7853b69e30067bfb960dff97d38ebdad1fe77fbe731480594(
    value: typing.Optional[MediaStreamingPolicyEnvelopeEncryptionDefaultContentKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5150d4e8b5bdf4a004910e828bce7804d9356181d40871a9d13a7515ded446d(
    *,
    dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55561b7e019fe5fb88a2b8df78372952a07bfdb6747b01a72171a5c9840eeedd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec473d2e92063c88c550211f5c0549d34877ec604d6d853a44d44ff293be9be5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__035ec22085ae9af048f067d403a69e06e735f8c123b13c4fb1ff99b57d57d04c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e716bd50fd7b9581e9a0adfca77d085e5df71da05a09c12c99b5f0d79fac16f7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53627a170184528d3f95c290202ef12e95b2af2547b35486cdd2abeb21ba1fd0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c82288ec29e1e3a70a5e72b3a91d0a9ea0bd6f560ffa32988e1421dba4fa9b73(
    value: typing.Optional[MediaStreamingPolicyEnvelopeEncryptionEnabledProtocols],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__738afe53963b45a433fda2d717c039c38ed792897db89f8cc2cfbf2ac1eff1e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47551f261d8b327db99fed51eebb829f4240d581ec50d74e465634bfe739d977(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715cd8d19e7a92f010588a1312e9d65d6ea823863a01d0be6545ec67e6e0f1ca(
    value: typing.Optional[MediaStreamingPolicyEnvelopeEncryption],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f083587dd133afccaa6be026dc81882afcc768870d89a0a2d44f6468b78108dc(
    *,
    dash: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    smooth_streaming: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73d2665195eba89e489e69054cb7937e793854448cf8607cd5d54174e1b2ba5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13ed9d75a632d7896c7b641967584095cd66b9224f9b0aff861e3fa32c68ecb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e818d3b051fbe60a96bee37254798b5fa9278d290f5aabd67ffd5506964f22b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e555f99f25b511c676e200f8aa90d8f2b4e962d5d02720d73d0242d556050dc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b452c41d75701c3b696306783c8fe3df95647b45f70b6fb8199a3143262490f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66bb6b94ce85b074c94d4ff456c77755111286089ade97fb874a415867501b94(
    value: typing.Optional[MediaStreamingPolicyNoEncryptionEnabledProtocols],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42c45c8637f6ce20fd4230f054db64bbefda9a4ad734f3da73d6eb2e3d479693(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    read: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__090e66135f5e1c317dbc9a7660d407266f0432c7e2543ae1aa88a13603b7be58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ba4c208fe9a7b155221b7399a00011d87510bebe2cfec4be9e905e89b35b52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b463a42a5ee4a03592af84e3615f89c7db0db856f8d639ae1df843e36fe3bb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e5cd9e067c7404426aff6c241112f88bb869cbaa3be8f4f973678beed920c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__634394e79a20c88a5f866ee2fc9b0a85994cf73ebdc5af85f33fec236ad324fc(
    value: typing.Optional[typing.Union[MediaStreamingPolicyTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
