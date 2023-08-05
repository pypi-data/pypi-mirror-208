'''
# `azurerm_media_transform`

Refer to the Terraform Registory for docs: [`azurerm_media_transform`](https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform).
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


class MediaTransform(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransform",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform azurerm_media_transform}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        media_services_account_name: builtins.str,
        name: builtins.str,
        resource_group_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutput", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["MediaTransformTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform azurerm_media_transform} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param media_services_account_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#media_services_account_name MediaTransform#media_services_account_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#name MediaTransform#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#resource_group_name MediaTransform#resource_group_name}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#description MediaTransform#description}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#id MediaTransform#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output MediaTransform#output}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#timeouts MediaTransform#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c41f75eff24819994958b09a36c6e201c83521a2f56558da9c72e6c1092fecb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MediaTransformConfig(
            media_services_account_name=media_services_account_name,
            name=name,
            resource_group_name=resource_group_name,
            description=description,
            id=id,
            output=output,
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

    @jsii.member(jsii_name="putOutput")
    def put_output(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutput", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac089d9982f230f82d95ebdb742b3102b62365a83b3986aecb192666f5605a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOutput", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#create MediaTransform#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#delete MediaTransform#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#read MediaTransform#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#update MediaTransform#update}.
        '''
        value = MediaTransformTimeouts(
            create=create, delete=delete, read=read, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOutput")
    def reset_output(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutput", []))

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
    @jsii.member(jsii_name="output")
    def output(self) -> "MediaTransformOutputList":
        return typing.cast("MediaTransformOutputList", jsii.get(self, "output"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MediaTransformTimeoutsOutputReference":
        return typing.cast("MediaTransformTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    @jsii.member(jsii_name="outputInput")
    def output_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutput"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutput"]]], jsii.get(self, "outputInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["MediaTransformTimeouts", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["MediaTransformTimeouts", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c484f553fe83e00cc7ebf3d19380c26db01278d40912d3122273cf5d87a4ef98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765acf3267073be26589e651f5abc8aa1b9ebe6f00d0c2dd01fee2598ac8decb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="mediaServicesAccountName")
    def media_services_account_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mediaServicesAccountName"))

    @media_services_account_name.setter
    def media_services_account_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a64d0fd84d7e7cdb13bbbf9a77362ca775919c44e5f389baff7604ff496577f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mediaServicesAccountName", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__612d790c370ef7c1243727283235dc5de0f8207e4ac50898580bcdf405a06082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16de48379a7915c82c056609e94f7730f02cc6b10d0405f0db65a2579af36cc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformConfig",
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
        "description": "description",
        "id": "id",
        "output": "output",
        "timeouts": "timeouts",
    },
)
class MediaTransformConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutput", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeouts: typing.Optional[typing.Union["MediaTransformTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param media_services_account_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#media_services_account_name MediaTransform#media_services_account_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#name MediaTransform#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#resource_group_name MediaTransform#resource_group_name}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#description MediaTransform#description}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#id MediaTransform#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param output: output block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output MediaTransform#output}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#timeouts MediaTransform#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = MediaTransformTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d209c9d3caa58f11af5ecf8bd18ddc9bff1f3ac46948505b039466b853b75d7c)
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
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument output", value=output, expected_type=type_hints["output"])
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if output is not None:
            self._values["output"] = output
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#media_services_account_name MediaTransform#media_services_account_name}.'''
        result = self._values.get("media_services_account_name")
        assert result is not None, "Required property 'media_services_account_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#name MediaTransform#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#resource_group_name MediaTransform#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#description MediaTransform#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#id MediaTransform#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutput"]]]:
        '''output block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output MediaTransform#output}
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutput"]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MediaTransformTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#timeouts MediaTransform#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MediaTransformTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutput",
    jsii_struct_bases=[],
    name_mapping={
        "audio_analyzer_preset": "audioAnalyzerPreset",
        "builtin_preset": "builtinPreset",
        "custom_preset": "customPreset",
        "face_detector_preset": "faceDetectorPreset",
        "on_error_action": "onErrorAction",
        "relative_priority": "relativePriority",
        "video_analyzer_preset": "videoAnalyzerPreset",
    },
)
class MediaTransformOutput:
    def __init__(
        self,
        *,
        audio_analyzer_preset: typing.Optional[typing.Union["MediaTransformOutputAudioAnalyzerPreset", typing.Dict[builtins.str, typing.Any]]] = None,
        builtin_preset: typing.Optional[typing.Union["MediaTransformOutputBuiltinPreset", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_preset: typing.Optional[typing.Union["MediaTransformOutputCustomPreset", typing.Dict[builtins.str, typing.Any]]] = None,
        face_detector_preset: typing.Optional[typing.Union["MediaTransformOutputFaceDetectorPreset", typing.Dict[builtins.str, typing.Any]]] = None,
        on_error_action: typing.Optional[builtins.str] = None,
        relative_priority: typing.Optional[builtins.str] = None,
        video_analyzer_preset: typing.Optional[typing.Union["MediaTransformOutputVideoAnalyzerPreset", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param audio_analyzer_preset: audio_analyzer_preset block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analyzer_preset MediaTransform#audio_analyzer_preset}
        :param builtin_preset: builtin_preset block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#builtin_preset MediaTransform#builtin_preset}
        :param custom_preset: custom_preset block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#custom_preset MediaTransform#custom_preset}
        :param face_detector_preset: face_detector_preset block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#face_detector_preset MediaTransform#face_detector_preset}
        :param on_error_action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#on_error_action MediaTransform#on_error_action}.
        :param relative_priority: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#relative_priority MediaTransform#relative_priority}.
        :param video_analyzer_preset: video_analyzer_preset block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#video_analyzer_preset MediaTransform#video_analyzer_preset}
        '''
        if isinstance(audio_analyzer_preset, dict):
            audio_analyzer_preset = MediaTransformOutputAudioAnalyzerPreset(**audio_analyzer_preset)
        if isinstance(builtin_preset, dict):
            builtin_preset = MediaTransformOutputBuiltinPreset(**builtin_preset)
        if isinstance(custom_preset, dict):
            custom_preset = MediaTransformOutputCustomPreset(**custom_preset)
        if isinstance(face_detector_preset, dict):
            face_detector_preset = MediaTransformOutputFaceDetectorPreset(**face_detector_preset)
        if isinstance(video_analyzer_preset, dict):
            video_analyzer_preset = MediaTransformOutputVideoAnalyzerPreset(**video_analyzer_preset)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__666c2c9da913938700dc7a27642e2ad57f50a195b5bb94a8c837c8d76bb13caa)
            check_type(argname="argument audio_analyzer_preset", value=audio_analyzer_preset, expected_type=type_hints["audio_analyzer_preset"])
            check_type(argname="argument builtin_preset", value=builtin_preset, expected_type=type_hints["builtin_preset"])
            check_type(argname="argument custom_preset", value=custom_preset, expected_type=type_hints["custom_preset"])
            check_type(argname="argument face_detector_preset", value=face_detector_preset, expected_type=type_hints["face_detector_preset"])
            check_type(argname="argument on_error_action", value=on_error_action, expected_type=type_hints["on_error_action"])
            check_type(argname="argument relative_priority", value=relative_priority, expected_type=type_hints["relative_priority"])
            check_type(argname="argument video_analyzer_preset", value=video_analyzer_preset, expected_type=type_hints["video_analyzer_preset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if audio_analyzer_preset is not None:
            self._values["audio_analyzer_preset"] = audio_analyzer_preset
        if builtin_preset is not None:
            self._values["builtin_preset"] = builtin_preset
        if custom_preset is not None:
            self._values["custom_preset"] = custom_preset
        if face_detector_preset is not None:
            self._values["face_detector_preset"] = face_detector_preset
        if on_error_action is not None:
            self._values["on_error_action"] = on_error_action
        if relative_priority is not None:
            self._values["relative_priority"] = relative_priority
        if video_analyzer_preset is not None:
            self._values["video_analyzer_preset"] = video_analyzer_preset

    @builtins.property
    def audio_analyzer_preset(
        self,
    ) -> typing.Optional["MediaTransformOutputAudioAnalyzerPreset"]:
        '''audio_analyzer_preset block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analyzer_preset MediaTransform#audio_analyzer_preset}
        '''
        result = self._values.get("audio_analyzer_preset")
        return typing.cast(typing.Optional["MediaTransformOutputAudioAnalyzerPreset"], result)

    @builtins.property
    def builtin_preset(self) -> typing.Optional["MediaTransformOutputBuiltinPreset"]:
        '''builtin_preset block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#builtin_preset MediaTransform#builtin_preset}
        '''
        result = self._values.get("builtin_preset")
        return typing.cast(typing.Optional["MediaTransformOutputBuiltinPreset"], result)

    @builtins.property
    def custom_preset(self) -> typing.Optional["MediaTransformOutputCustomPreset"]:
        '''custom_preset block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#custom_preset MediaTransform#custom_preset}
        '''
        result = self._values.get("custom_preset")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPreset"], result)

    @builtins.property
    def face_detector_preset(
        self,
    ) -> typing.Optional["MediaTransformOutputFaceDetectorPreset"]:
        '''face_detector_preset block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#face_detector_preset MediaTransform#face_detector_preset}
        '''
        result = self._values.get("face_detector_preset")
        return typing.cast(typing.Optional["MediaTransformOutputFaceDetectorPreset"], result)

    @builtins.property
    def on_error_action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#on_error_action MediaTransform#on_error_action}.'''
        result = self._values.get("on_error_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def relative_priority(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#relative_priority MediaTransform#relative_priority}.'''
        result = self._values.get("relative_priority")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def video_analyzer_preset(
        self,
    ) -> typing.Optional["MediaTransformOutputVideoAnalyzerPreset"]:
        '''video_analyzer_preset block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#video_analyzer_preset MediaTransform#video_analyzer_preset}
        '''
        result = self._values.get("video_analyzer_preset")
        return typing.cast(typing.Optional["MediaTransformOutputVideoAnalyzerPreset"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputAudioAnalyzerPreset",
    jsii_struct_bases=[],
    name_mapping={
        "audio_analysis_mode": "audioAnalysisMode",
        "audio_language": "audioLanguage",
        "experimental_options": "experimentalOptions",
    },
)
class MediaTransformOutputAudioAnalyzerPreset:
    def __init__(
        self,
        *,
        audio_analysis_mode: typing.Optional[builtins.str] = None,
        audio_language: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param audio_analysis_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.
        :param audio_language: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86be4a547b7de35e3afda494aa38b62e654677fcdff205b65dff86815f012de5)
            check_type(argname="argument audio_analysis_mode", value=audio_analysis_mode, expected_type=type_hints["audio_analysis_mode"])
            check_type(argname="argument audio_language", value=audio_language, expected_type=type_hints["audio_language"])
            check_type(argname="argument experimental_options", value=experimental_options, expected_type=type_hints["experimental_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if audio_analysis_mode is not None:
            self._values["audio_analysis_mode"] = audio_analysis_mode
        if audio_language is not None:
            self._values["audio_language"] = audio_language
        if experimental_options is not None:
            self._values["experimental_options"] = experimental_options

    @builtins.property
    def audio_analysis_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.'''
        result = self._values.get("audio_analysis_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audio_language(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.'''
        result = self._values.get("audio_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def experimental_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.'''
        result = self._values.get("experimental_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputAudioAnalyzerPreset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputAudioAnalyzerPresetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputAudioAnalyzerPresetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33b7d395d1b3f01cb790ac467032c53ffa9ec5ce4c5d360da4f2b991b3a8b77d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAudioAnalysisMode")
    def reset_audio_analysis_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioAnalysisMode", []))

    @jsii.member(jsii_name="resetAudioLanguage")
    def reset_audio_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioLanguage", []))

    @jsii.member(jsii_name="resetExperimentalOptions")
    def reset_experimental_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExperimentalOptions", []))

    @builtins.property
    @jsii.member(jsii_name="audioAnalysisModeInput")
    def audio_analysis_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audioAnalysisModeInput"))

    @builtins.property
    @jsii.member(jsii_name="audioLanguageInput")
    def audio_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audioLanguageInput"))

    @builtins.property
    @jsii.member(jsii_name="experimentalOptionsInput")
    def experimental_options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "experimentalOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="audioAnalysisMode")
    def audio_analysis_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audioAnalysisMode"))

    @audio_analysis_mode.setter
    def audio_analysis_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d65612928c10a6dca460daef87ccf949b480be7328a992cce94e160dcc5f4c4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioAnalysisMode", value)

    @builtins.property
    @jsii.member(jsii_name="audioLanguage")
    def audio_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audioLanguage"))

    @audio_language.setter
    def audio_language(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72b9492548862da82bd8cb63c7d8f31f8dae74ec2c02438e53905504a40b8364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioLanguage", value)

    @builtins.property
    @jsii.member(jsii_name="experimentalOptions")
    def experimental_options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "experimentalOptions"))

    @experimental_options.setter
    def experimental_options(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca692e77e9be8b46f8c1979a4a4d48be36f7768229bc7bcf125c34790152f1a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "experimentalOptions", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputAudioAnalyzerPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputAudioAnalyzerPreset], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputAudioAnalyzerPreset],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebfb78476aa46c3af4b31d0c08f0f4906badb1955918d4992296705c51407255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputBuiltinPreset",
    jsii_struct_bases=[],
    name_mapping={
        "preset_name": "presetName",
        "preset_configuration": "presetConfiguration",
    },
)
class MediaTransformOutputBuiltinPreset:
    def __init__(
        self,
        *,
        preset_name: builtins.str,
        preset_configuration: typing.Optional[typing.Union["MediaTransformOutputBuiltinPresetPresetConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_name MediaTransform#preset_name}.
        :param preset_configuration: preset_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_configuration MediaTransform#preset_configuration}
        '''
        if isinstance(preset_configuration, dict):
            preset_configuration = MediaTransformOutputBuiltinPresetPresetConfiguration(**preset_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc0cfa8e191093b2699a78d5eacb297553ab56fbcd29a7002d0f47feefac77b2)
            check_type(argname="argument preset_name", value=preset_name, expected_type=type_hints["preset_name"])
            check_type(argname="argument preset_configuration", value=preset_configuration, expected_type=type_hints["preset_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "preset_name": preset_name,
        }
        if preset_configuration is not None:
            self._values["preset_configuration"] = preset_configuration

    @builtins.property
    def preset_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_name MediaTransform#preset_name}.'''
        result = self._values.get("preset_name")
        assert result is not None, "Required property 'preset_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def preset_configuration(
        self,
    ) -> typing.Optional["MediaTransformOutputBuiltinPresetPresetConfiguration"]:
        '''preset_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_configuration MediaTransform#preset_configuration}
        '''
        result = self._values.get("preset_configuration")
        return typing.cast(typing.Optional["MediaTransformOutputBuiltinPresetPresetConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputBuiltinPreset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputBuiltinPresetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputBuiltinPresetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0fc02c10b96f92dbd42b1e4867b5445b62a5f082b94a254aad7de93633cb3e9b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPresetConfiguration")
    def put_preset_configuration(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        interleave_output: typing.Optional[builtins.str] = None,
        key_frame_interval_in_seconds: typing.Optional[jsii.Number] = None,
        max_bitrate_bps: typing.Optional[jsii.Number] = None,
        max_height: typing.Optional[jsii.Number] = None,
        max_layers: typing.Optional[jsii.Number] = None,
        min_bitrate_bps: typing.Optional[jsii.Number] = None,
        min_height: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param interleave_output: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#interleave_output MediaTransform#interleave_output}.
        :param key_frame_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval_in_seconds MediaTransform#key_frame_interval_in_seconds}.
        :param max_bitrate_bps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate_bps MediaTransform#max_bitrate_bps}.
        :param max_height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_height MediaTransform#max_height}.
        :param max_layers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_layers MediaTransform#max_layers}.
        :param min_bitrate_bps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_bitrate_bps MediaTransform#min_bitrate_bps}.
        :param min_height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_height MediaTransform#min_height}.
        '''
        value = MediaTransformOutputBuiltinPresetPresetConfiguration(
            complexity=complexity,
            interleave_output=interleave_output,
            key_frame_interval_in_seconds=key_frame_interval_in_seconds,
            max_bitrate_bps=max_bitrate_bps,
            max_height=max_height,
            max_layers=max_layers,
            min_bitrate_bps=min_bitrate_bps,
            min_height=min_height,
        )

        return typing.cast(None, jsii.invoke(self, "putPresetConfiguration", [value]))

    @jsii.member(jsii_name="resetPresetConfiguration")
    def reset_preset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresetConfiguration", []))

    @builtins.property
    @jsii.member(jsii_name="presetConfiguration")
    def preset_configuration(
        self,
    ) -> "MediaTransformOutputBuiltinPresetPresetConfigurationOutputReference":
        return typing.cast("MediaTransformOutputBuiltinPresetPresetConfigurationOutputReference", jsii.get(self, "presetConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="presetConfigurationInput")
    def preset_configuration_input(
        self,
    ) -> typing.Optional["MediaTransformOutputBuiltinPresetPresetConfiguration"]:
        return typing.cast(typing.Optional["MediaTransformOutputBuiltinPresetPresetConfiguration"], jsii.get(self, "presetConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="presetNameInput")
    def preset_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "presetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="presetName")
    def preset_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "presetName"))

    @preset_name.setter
    def preset_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca46e3a1a2b119a67fd3a9df7a632485257928812a7eb25e1bf2eda4eec9be6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "presetName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MediaTransformOutputBuiltinPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputBuiltinPreset], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputBuiltinPreset],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2c5f4d0cb36a7ef6df80284babe5ce85a6bb15f2343aa9be57a287a12090476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputBuiltinPresetPresetConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "complexity": "complexity",
        "interleave_output": "interleaveOutput",
        "key_frame_interval_in_seconds": "keyFrameIntervalInSeconds",
        "max_bitrate_bps": "maxBitrateBps",
        "max_height": "maxHeight",
        "max_layers": "maxLayers",
        "min_bitrate_bps": "minBitrateBps",
        "min_height": "minHeight",
    },
)
class MediaTransformOutputBuiltinPresetPresetConfiguration:
    def __init__(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        interleave_output: typing.Optional[builtins.str] = None,
        key_frame_interval_in_seconds: typing.Optional[jsii.Number] = None,
        max_bitrate_bps: typing.Optional[jsii.Number] = None,
        max_height: typing.Optional[jsii.Number] = None,
        max_layers: typing.Optional[jsii.Number] = None,
        min_bitrate_bps: typing.Optional[jsii.Number] = None,
        min_height: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param interleave_output: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#interleave_output MediaTransform#interleave_output}.
        :param key_frame_interval_in_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval_in_seconds MediaTransform#key_frame_interval_in_seconds}.
        :param max_bitrate_bps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate_bps MediaTransform#max_bitrate_bps}.
        :param max_height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_height MediaTransform#max_height}.
        :param max_layers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_layers MediaTransform#max_layers}.
        :param min_bitrate_bps: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_bitrate_bps MediaTransform#min_bitrate_bps}.
        :param min_height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_height MediaTransform#min_height}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ec9e24e0af1f270697bef2afb290a540770c2baa2c5e24a5a23f73053d55244)
            check_type(argname="argument complexity", value=complexity, expected_type=type_hints["complexity"])
            check_type(argname="argument interleave_output", value=interleave_output, expected_type=type_hints["interleave_output"])
            check_type(argname="argument key_frame_interval_in_seconds", value=key_frame_interval_in_seconds, expected_type=type_hints["key_frame_interval_in_seconds"])
            check_type(argname="argument max_bitrate_bps", value=max_bitrate_bps, expected_type=type_hints["max_bitrate_bps"])
            check_type(argname="argument max_height", value=max_height, expected_type=type_hints["max_height"])
            check_type(argname="argument max_layers", value=max_layers, expected_type=type_hints["max_layers"])
            check_type(argname="argument min_bitrate_bps", value=min_bitrate_bps, expected_type=type_hints["min_bitrate_bps"])
            check_type(argname="argument min_height", value=min_height, expected_type=type_hints["min_height"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if complexity is not None:
            self._values["complexity"] = complexity
        if interleave_output is not None:
            self._values["interleave_output"] = interleave_output
        if key_frame_interval_in_seconds is not None:
            self._values["key_frame_interval_in_seconds"] = key_frame_interval_in_seconds
        if max_bitrate_bps is not None:
            self._values["max_bitrate_bps"] = max_bitrate_bps
        if max_height is not None:
            self._values["max_height"] = max_height
        if max_layers is not None:
            self._values["max_layers"] = max_layers
        if min_bitrate_bps is not None:
            self._values["min_bitrate_bps"] = min_bitrate_bps
        if min_height is not None:
            self._values["min_height"] = min_height

    @builtins.property
    def complexity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.'''
        result = self._values.get("complexity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def interleave_output(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#interleave_output MediaTransform#interleave_output}.'''
        result = self._values.get("interleave_output")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_frame_interval_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval_in_seconds MediaTransform#key_frame_interval_in_seconds}.'''
        result = self._values.get("key_frame_interval_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_bitrate_bps(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate_bps MediaTransform#max_bitrate_bps}.'''
        result = self._values.get("max_bitrate_bps")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_height MediaTransform#max_height}.'''
        result = self._values.get("max_height")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_layers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_layers MediaTransform#max_layers}.'''
        result = self._values.get("max_layers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_bitrate_bps(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_bitrate_bps MediaTransform#min_bitrate_bps}.'''
        result = self._values.get("min_bitrate_bps")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_height(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#min_height MediaTransform#min_height}.'''
        result = self._values.get("min_height")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputBuiltinPresetPresetConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputBuiltinPresetPresetConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputBuiltinPresetPresetConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f02e2d10371e1246be3d1f04fe1eb112a3dc307e068e70a72dc171fda09c2677)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetComplexity")
    def reset_complexity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplexity", []))

    @jsii.member(jsii_name="resetInterleaveOutput")
    def reset_interleave_output(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterleaveOutput", []))

    @jsii.member(jsii_name="resetKeyFrameIntervalInSeconds")
    def reset_key_frame_interval_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFrameIntervalInSeconds", []))

    @jsii.member(jsii_name="resetMaxBitrateBps")
    def reset_max_bitrate_bps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBitrateBps", []))

    @jsii.member(jsii_name="resetMaxHeight")
    def reset_max_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxHeight", []))

    @jsii.member(jsii_name="resetMaxLayers")
    def reset_max_layers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLayers", []))

    @jsii.member(jsii_name="resetMinBitrateBps")
    def reset_min_bitrate_bps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinBitrateBps", []))

    @jsii.member(jsii_name="resetMinHeight")
    def reset_min_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinHeight", []))

    @builtins.property
    @jsii.member(jsii_name="complexityInput")
    def complexity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complexityInput"))

    @builtins.property
    @jsii.member(jsii_name="interleaveOutputInput")
    def interleave_output_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interleaveOutputInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFrameIntervalInSecondsInput")
    def key_frame_interval_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyFrameIntervalInSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBitrateBpsInput")
    def max_bitrate_bps_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBitrateBpsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxHeightInput")
    def max_height_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxHeightInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLayersInput")
    def max_layers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLayersInput"))

    @builtins.property
    @jsii.member(jsii_name="minBitrateBpsInput")
    def min_bitrate_bps_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minBitrateBpsInput"))

    @builtins.property
    @jsii.member(jsii_name="minHeightInput")
    def min_height_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minHeightInput"))

    @builtins.property
    @jsii.member(jsii_name="complexity")
    def complexity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "complexity"))

    @complexity.setter
    def complexity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fca632f432164c280911b1eb931bc808cebcb9dddbceb496c50352c4ff8d206)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complexity", value)

    @builtins.property
    @jsii.member(jsii_name="interleaveOutput")
    def interleave_output(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interleaveOutput"))

    @interleave_output.setter
    def interleave_output(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc906972f5fe4c6ffd539533f0ceb4d57d6f34641a2dc806a3c3d1ba692912e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interleaveOutput", value)

    @builtins.property
    @jsii.member(jsii_name="keyFrameIntervalInSeconds")
    def key_frame_interval_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyFrameIntervalInSeconds"))

    @key_frame_interval_in_seconds.setter
    def key_frame_interval_in_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4318d9b12a21eefaf5a66e85a235c04cd90c722a31fa32aa3430f05b270816c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFrameIntervalInSeconds", value)

    @builtins.property
    @jsii.member(jsii_name="maxBitrateBps")
    def max_bitrate_bps(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBitrateBps"))

    @max_bitrate_bps.setter
    def max_bitrate_bps(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b6c9b8ede6dac50f6337b7353297f45adb3105ae171103e27f6741ec5bc54fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBitrateBps", value)

    @builtins.property
    @jsii.member(jsii_name="maxHeight")
    def max_height(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxHeight"))

    @max_height.setter
    def max_height(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb476ef77773559ebcaae433f9e21acce5dcf4639757e78aae5c53406e306eb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxHeight", value)

    @builtins.property
    @jsii.member(jsii_name="maxLayers")
    def max_layers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLayers"))

    @max_layers.setter
    def max_layers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bac00b455968b70940e380b59f8e6bd49b7563adfa5cb18576008231db6396c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLayers", value)

    @builtins.property
    @jsii.member(jsii_name="minBitrateBps")
    def min_bitrate_bps(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minBitrateBps"))

    @min_bitrate_bps.setter
    def min_bitrate_bps(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7084df8490d312a6605a3022eb3c6ed32dec356330a190d6028cff76d55e530)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minBitrateBps", value)

    @builtins.property
    @jsii.member(jsii_name="minHeight")
    def min_height(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minHeight"))

    @min_height.setter
    def min_height(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63a18c6289552b522e6662406c621c75e60af93868d41e942f3f79c8b09b3ef6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minHeight", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputBuiltinPresetPresetConfiguration]:
        return typing.cast(typing.Optional[MediaTransformOutputBuiltinPresetPresetConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputBuiltinPresetPresetConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97dc6935ab831d0365fb3be6e61f1a0fca92483b31914396c6f0d9e63f237660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPreset",
    jsii_struct_bases=[],
    name_mapping={"codec": "codec", "format": "format", "filter": "filter"},
)
class MediaTransformOutputCustomPreset:
    def __init__(
        self,
        *,
        codec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetCodec", typing.Dict[builtins.str, typing.Any]]]],
        format: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFormat", typing.Dict[builtins.str, typing.Any]]]],
        filter: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilter", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param codec: codec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#codec MediaTransform#codec}
        :param format: format block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#format MediaTransform#format}
        :param filter: filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filter MediaTransform#filter}
        '''
        if isinstance(filter, dict):
            filter = MediaTransformOutputCustomPresetFilter(**filter)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3eee445d59c63cbf85bb195a68b139d4a9eea1b7131f768f07504ceeda3f7f)
            check_type(argname="argument codec", value=codec, expected_type=type_hints["codec"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "codec": codec,
            "format": format,
        }
        if filter is not None:
            self._values["filter"] = filter

    @builtins.property
    def codec(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodec"]]:
        '''codec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#codec MediaTransform#codec}
        '''
        result = self._values.get("codec")
        assert result is not None, "Required property 'codec' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodec"]], result)

    @builtins.property
    def format(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormat"]]:
        '''format block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#format MediaTransform#format}
        '''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormat"]], result)

    @builtins.property
    def filter(self) -> typing.Optional["MediaTransformOutputCustomPresetFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filter MediaTransform#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPreset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodec",
    jsii_struct_bases=[],
    name_mapping={
        "aac_audio": "aacAudio",
        "copy_audio": "copyAudio",
        "copy_video": "copyVideo",
        "dd_audio": "ddAudio",
        "h264_video": "h264Video",
        "h265_video": "h265Video",
    },
)
class MediaTransformOutputCustomPresetCodec:
    def __init__(
        self,
        *,
        aac_audio: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecAacAudio", typing.Dict[builtins.str, typing.Any]]] = None,
        copy_audio: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecCopyAudio", typing.Dict[builtins.str, typing.Any]]] = None,
        copy_video: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecCopyVideo", typing.Dict[builtins.str, typing.Any]]] = None,
        dd_audio: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecDdAudio", typing.Dict[builtins.str, typing.Any]]] = None,
        h264_video: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecH264Video", typing.Dict[builtins.str, typing.Any]]] = None,
        h265_video: typing.Optional[typing.Union["MediaTransformOutputCustomPresetCodecH265Video", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aac_audio: aac_audio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#aac_audio MediaTransform#aac_audio}
        :param copy_audio: copy_audio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#copy_audio MediaTransform#copy_audio}
        :param copy_video: copy_video block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#copy_video MediaTransform#copy_video}
        :param dd_audio: dd_audio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#dd_audio MediaTransform#dd_audio}
        :param h264_video: h264_video block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#h264_video MediaTransform#h264_video}
        :param h265_video: h265_video block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#h265_video MediaTransform#h265_video}
        '''
        if isinstance(aac_audio, dict):
            aac_audio = MediaTransformOutputCustomPresetCodecAacAudio(**aac_audio)
        if isinstance(copy_audio, dict):
            copy_audio = MediaTransformOutputCustomPresetCodecCopyAudio(**copy_audio)
        if isinstance(copy_video, dict):
            copy_video = MediaTransformOutputCustomPresetCodecCopyVideo(**copy_video)
        if isinstance(dd_audio, dict):
            dd_audio = MediaTransformOutputCustomPresetCodecDdAudio(**dd_audio)
        if isinstance(h264_video, dict):
            h264_video = MediaTransformOutputCustomPresetCodecH264Video(**h264_video)
        if isinstance(h265_video, dict):
            h265_video = MediaTransformOutputCustomPresetCodecH265Video(**h265_video)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adaad5f7810c550fa20cc1d3aa41259a84c69b66a2c4beb4de7df1fc2f56096)
            check_type(argname="argument aac_audio", value=aac_audio, expected_type=type_hints["aac_audio"])
            check_type(argname="argument copy_audio", value=copy_audio, expected_type=type_hints["copy_audio"])
            check_type(argname="argument copy_video", value=copy_video, expected_type=type_hints["copy_video"])
            check_type(argname="argument dd_audio", value=dd_audio, expected_type=type_hints["dd_audio"])
            check_type(argname="argument h264_video", value=h264_video, expected_type=type_hints["h264_video"])
            check_type(argname="argument h265_video", value=h265_video, expected_type=type_hints["h265_video"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aac_audio is not None:
            self._values["aac_audio"] = aac_audio
        if copy_audio is not None:
            self._values["copy_audio"] = copy_audio
        if copy_video is not None:
            self._values["copy_video"] = copy_video
        if dd_audio is not None:
            self._values["dd_audio"] = dd_audio
        if h264_video is not None:
            self._values["h264_video"] = h264_video
        if h265_video is not None:
            self._values["h265_video"] = h265_video

    @builtins.property
    def aac_audio(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecAacAudio"]:
        '''aac_audio block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#aac_audio MediaTransform#aac_audio}
        '''
        result = self._values.get("aac_audio")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecAacAudio"], result)

    @builtins.property
    def copy_audio(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecCopyAudio"]:
        '''copy_audio block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#copy_audio MediaTransform#copy_audio}
        '''
        result = self._values.get("copy_audio")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecCopyAudio"], result)

    @builtins.property
    def copy_video(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecCopyVideo"]:
        '''copy_video block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#copy_video MediaTransform#copy_video}
        '''
        result = self._values.get("copy_video")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecCopyVideo"], result)

    @builtins.property
    def dd_audio(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecDdAudio"]:
        '''dd_audio block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#dd_audio MediaTransform#dd_audio}
        '''
        result = self._values.get("dd_audio")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecDdAudio"], result)

    @builtins.property
    def h264_video(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecH264Video"]:
        '''h264_video block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#h264_video MediaTransform#h264_video}
        '''
        result = self._values.get("h264_video")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecH264Video"], result)

    @builtins.property
    def h265_video(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetCodecH265Video"]:
        '''h265_video block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#h265_video MediaTransform#h265_video}
        '''
        result = self._values.get("h265_video")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetCodecH265Video"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecAacAudio",
    jsii_struct_bases=[],
    name_mapping={
        "bitrate": "bitrate",
        "channels": "channels",
        "label": "label",
        "profile": "profile",
        "sampling_rate": "samplingRate",
    },
)
class MediaTransformOutputCustomPresetCodecAacAudio:
    def __init__(
        self,
        *,
        bitrate: typing.Optional[jsii.Number] = None,
        channels: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param channels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49003c3e5e7b5536b4a3c97e72593fd73e4392aa814f88bd379767d23298e45a)
            check_type(argname="argument bitrate", value=bitrate, expected_type=type_hints["bitrate"])
            check_type(argname="argument channels", value=channels, expected_type=type_hints["channels"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument sampling_rate", value=sampling_rate, expected_type=type_hints["sampling_rate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bitrate is not None:
            self._values["bitrate"] = bitrate
        if channels is not None:
            self._values["channels"] = channels
        if label is not None:
            self._values["label"] = label
        if profile is not None:
            self._values["profile"] = profile
        if sampling_rate is not None:
            self._values["sampling_rate"] = sampling_rate

    @builtins.property
    def bitrate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.'''
        result = self._values.get("bitrate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def channels(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.'''
        result = self._values.get("channels")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sampling_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.'''
        result = self._values.get("sampling_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecAacAudio(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecAacAudioOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecAacAudioOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82c3335d8c933673ef54c2817114c3cd1cf600d5309e6b60a070a58dec3cb65f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBitrate")
    def reset_bitrate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBitrate", []))

    @jsii.member(jsii_name="resetChannels")
    def reset_channels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannels", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetSamplingRate")
    def reset_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamplingRate", []))

    @builtins.property
    @jsii.member(jsii_name="bitrateInput")
    def bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="channelsInput")
    def channels_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "channelsInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="samplingRateInput")
    def sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "samplingRateInput"))

    @builtins.property
    @jsii.member(jsii_name="bitrate")
    def bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bitrate"))

    @bitrate.setter
    def bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf41e4cd192ea5d1bf0798d16d72ad776c25c55041d96508e8cbb6ea16762d15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bitrate", value)

    @builtins.property
    @jsii.member(jsii_name="channels")
    def channels(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "channels"))

    @channels.setter
    def channels(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fff3305579adc5f8e3455ca3bded09209c8a2095b0040075494bdc7b9dc3da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channels", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b3b72802359df12bab8e4ffccf52a8f40230ae09ed167939e6468c5e99d8bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee0b10bbc9a5fe983c8a9dd298f8e222ab680dfc4180509291ef84f7fd6ba82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value)

    @builtins.property
    @jsii.member(jsii_name="samplingRate")
    def sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingRate"))

    @sampling_rate.setter
    def sampling_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9993ad64e0fad6e99c2bcd51aa1dbc75107363db2def59266e46d9984a68ca9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingRate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b1ca1fdff0211374179dc76079001b34aabd5921ee5111a88760345a49b372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecCopyAudio",
    jsii_struct_bases=[],
    name_mapping={"label": "label"},
)
class MediaTransformOutputCustomPresetCodecCopyAudio:
    def __init__(self, *, label: typing.Optional[builtins.str] = None) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__505505c30558157cdde8e56545366f398d51a250b7054f91b381df36c5df7f6b)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if label is not None:
            self._values["label"] = label

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecCopyAudio(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecCopyAudioOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecCopyAudioOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64f5d3f0c788c1c5efcd8f6a48a97cddad1303f9d35a23b3fb635ecab76da1e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1862d2760dbce5356b5d46b83584e10fc9f33ff12436f57950854dc2abc99a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f306a3019da7dd3bc7531985a4fe3ecb609494d42f2ef6e9a08ea70624e2131c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecCopyVideo",
    jsii_struct_bases=[],
    name_mapping={"label": "label"},
)
class MediaTransformOutputCustomPresetCodecCopyVideo:
    def __init__(self, *, label: typing.Optional[builtins.str] = None) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6428ecbb7a7dc2be6b3766b5d16e96f5a71648ffffc67df7ffbae1caeb6cb96)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if label is not None:
            self._values["label"] = label

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecCopyVideo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecCopyVideoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecCopyVideoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1abb0252a3baa2ceb607e588f33bee8befc3a327b81643b39b59cec6a06d3e2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af8ede4ed719ed878bd7eac80f713ad574a876c96bd60512dcf0b675ce05669)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd9ce88b0f6506e28e702828268ae1e70cae2957dd5c8593f922c09ba691c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecDdAudio",
    jsii_struct_bases=[],
    name_mapping={
        "bitrate": "bitrate",
        "channels": "channels",
        "label": "label",
        "sampling_rate": "samplingRate",
    },
)
class MediaTransformOutputCustomPresetCodecDdAudio:
    def __init__(
        self,
        *,
        bitrate: typing.Optional[jsii.Number] = None,
        channels: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param channels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f023ab91f7c0f9ab16335d2f19437f7aa40909863a8933f7c589e73ecfe38ce9)
            check_type(argname="argument bitrate", value=bitrate, expected_type=type_hints["bitrate"])
            check_type(argname="argument channels", value=channels, expected_type=type_hints["channels"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument sampling_rate", value=sampling_rate, expected_type=type_hints["sampling_rate"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bitrate is not None:
            self._values["bitrate"] = bitrate
        if channels is not None:
            self._values["channels"] = channels
        if label is not None:
            self._values["label"] = label
        if sampling_rate is not None:
            self._values["sampling_rate"] = sampling_rate

    @builtins.property
    def bitrate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.'''
        result = self._values.get("bitrate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def channels(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.'''
        result = self._values.get("channels")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sampling_rate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.'''
        result = self._values.get("sampling_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecDdAudio(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecDdAudioOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecDdAudioOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c4601e7b428f7066f8316058e98f72eab05a9cac600955dfd875a4e68c50011)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBitrate")
    def reset_bitrate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBitrate", []))

    @jsii.member(jsii_name="resetChannels")
    def reset_channels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannels", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetSamplingRate")
    def reset_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamplingRate", []))

    @builtins.property
    @jsii.member(jsii_name="bitrateInput")
    def bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="channelsInput")
    def channels_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "channelsInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="samplingRateInput")
    def sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "samplingRateInput"))

    @builtins.property
    @jsii.member(jsii_name="bitrate")
    def bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bitrate"))

    @bitrate.setter
    def bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8e09ea8536a3263a73d22c233b3e54250350f7262ac1fde37b4e210d10117e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bitrate", value)

    @builtins.property
    @jsii.member(jsii_name="channels")
    def channels(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "channels"))

    @channels.setter
    def channels(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8219e81ea2fa46eff721f18683bf092c2913732ecb284f9de885b2716214ae1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channels", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af7c293f6cb8c1ba7aad5f169132ad344fe5dba400194288a41da2cb0ad30a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="samplingRate")
    def sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingRate"))

    @sampling_rate.setter
    def sampling_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f3ed9a8adf63f9aed643588bad41cdb411fea7e0ad0043cd5a6cd39d1307c4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samplingRate", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb431ac233e7ffd5da650cc8cb0e158e31a5bf0ed3213afd4ebbb9560823e9c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH264Video",
    jsii_struct_bases=[],
    name_mapping={
        "complexity": "complexity",
        "key_frame_interval": "keyFrameInterval",
        "label": "label",
        "layer": "layer",
        "rate_control_mode": "rateControlMode",
        "scene_change_detection_enabled": "sceneChangeDetectionEnabled",
        "stretch_mode": "stretchMode",
        "sync_mode": "syncMode",
    },
)
class MediaTransformOutputCustomPresetCodecH264Video:
    def __init__(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        key_frame_interval: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetCodecH264VideoLayer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        rate_control_mode: typing.Optional[builtins.str] = None,
        scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        stretch_mode: typing.Optional[builtins.str] = None,
        sync_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param key_frame_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param layer: layer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        :param rate_control_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rate_control_mode MediaTransform#rate_control_mode}.
        :param scene_change_detection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.
        :param stretch_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.
        :param sync_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0614973057ec008d49a290ede7145b4ed953f3663d389e3eae0dcf8d48205fe2)
            check_type(argname="argument complexity", value=complexity, expected_type=type_hints["complexity"])
            check_type(argname="argument key_frame_interval", value=key_frame_interval, expected_type=type_hints["key_frame_interval"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument layer", value=layer, expected_type=type_hints["layer"])
            check_type(argname="argument rate_control_mode", value=rate_control_mode, expected_type=type_hints["rate_control_mode"])
            check_type(argname="argument scene_change_detection_enabled", value=scene_change_detection_enabled, expected_type=type_hints["scene_change_detection_enabled"])
            check_type(argname="argument stretch_mode", value=stretch_mode, expected_type=type_hints["stretch_mode"])
            check_type(argname="argument sync_mode", value=sync_mode, expected_type=type_hints["sync_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if complexity is not None:
            self._values["complexity"] = complexity
        if key_frame_interval is not None:
            self._values["key_frame_interval"] = key_frame_interval
        if label is not None:
            self._values["label"] = label
        if layer is not None:
            self._values["layer"] = layer
        if rate_control_mode is not None:
            self._values["rate_control_mode"] = rate_control_mode
        if scene_change_detection_enabled is not None:
            self._values["scene_change_detection_enabled"] = scene_change_detection_enabled
        if stretch_mode is not None:
            self._values["stretch_mode"] = stretch_mode
        if sync_mode is not None:
            self._values["sync_mode"] = sync_mode

    @builtins.property
    def complexity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.'''
        result = self._values.get("complexity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_frame_interval(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.'''
        result = self._values.get("key_frame_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodecH264VideoLayer"]]]:
        '''layer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        '''
        result = self._values.get("layer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodecH264VideoLayer"]]], result)

    @builtins.property
    def rate_control_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rate_control_mode MediaTransform#rate_control_mode}.'''
        result = self._values.get("rate_control_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scene_change_detection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.'''
        result = self._values.get("scene_change_detection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def stretch_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.'''
        result = self._values.get("stretch_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sync_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.'''
        result = self._values.get("sync_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecH264Video(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH264VideoLayer",
    jsii_struct_bases=[],
    name_mapping={
        "bitrate": "bitrate",
        "adaptive_b_frame_enabled": "adaptiveBFrameEnabled",
        "b_frames": "bFrames",
        "buffer_window": "bufferWindow",
        "crf": "crf",
        "entropy_mode": "entropyMode",
        "frame_rate": "frameRate",
        "height": "height",
        "label": "label",
        "level": "level",
        "max_bitrate": "maxBitrate",
        "profile": "profile",
        "reference_frames": "referenceFrames",
        "slices": "slices",
        "width": "width",
    },
)
class MediaTransformOutputCustomPresetCodecH264VideoLayer:
    def __init__(
        self,
        *,
        bitrate: jsii.Number,
        adaptive_b_frame_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        b_frames: typing.Optional[jsii.Number] = None,
        buffer_window: typing.Optional[builtins.str] = None,
        crf: typing.Optional[jsii.Number] = None,
        entropy_mode: typing.Optional[builtins.str] = None,
        frame_rate: typing.Optional[builtins.str] = None,
        height: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        level: typing.Optional[builtins.str] = None,
        max_bitrate: typing.Optional[jsii.Number] = None,
        profile: typing.Optional[builtins.str] = None,
        reference_frames: typing.Optional[jsii.Number] = None,
        slices: typing.Optional[jsii.Number] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param adaptive_b_frame_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#adaptive_b_frame_enabled MediaTransform#adaptive_b_frame_enabled}.
        :param b_frames: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#b_frames MediaTransform#b_frames}.
        :param buffer_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#buffer_window MediaTransform#buffer_window}.
        :param crf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crf MediaTransform#crf}.
        :param entropy_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#entropy_mode MediaTransform#entropy_mode}.
        :param frame_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#frame_rate MediaTransform#frame_rate}.
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#level MediaTransform#level}.
        :param max_bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate MediaTransform#max_bitrate}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.
        :param reference_frames: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#reference_frames MediaTransform#reference_frames}.
        :param slices: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#slices MediaTransform#slices}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48ef16278d2aa15e2a9c0f83405ce28edae1e64ec5ec60426c9cc79f9834bad4)
            check_type(argname="argument bitrate", value=bitrate, expected_type=type_hints["bitrate"])
            check_type(argname="argument adaptive_b_frame_enabled", value=adaptive_b_frame_enabled, expected_type=type_hints["adaptive_b_frame_enabled"])
            check_type(argname="argument b_frames", value=b_frames, expected_type=type_hints["b_frames"])
            check_type(argname="argument buffer_window", value=buffer_window, expected_type=type_hints["buffer_window"])
            check_type(argname="argument crf", value=crf, expected_type=type_hints["crf"])
            check_type(argname="argument entropy_mode", value=entropy_mode, expected_type=type_hints["entropy_mode"])
            check_type(argname="argument frame_rate", value=frame_rate, expected_type=type_hints["frame_rate"])
            check_type(argname="argument height", value=height, expected_type=type_hints["height"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument level", value=level, expected_type=type_hints["level"])
            check_type(argname="argument max_bitrate", value=max_bitrate, expected_type=type_hints["max_bitrate"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument reference_frames", value=reference_frames, expected_type=type_hints["reference_frames"])
            check_type(argname="argument slices", value=slices, expected_type=type_hints["slices"])
            check_type(argname="argument width", value=width, expected_type=type_hints["width"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bitrate": bitrate,
        }
        if adaptive_b_frame_enabled is not None:
            self._values["adaptive_b_frame_enabled"] = adaptive_b_frame_enabled
        if b_frames is not None:
            self._values["b_frames"] = b_frames
        if buffer_window is not None:
            self._values["buffer_window"] = buffer_window
        if crf is not None:
            self._values["crf"] = crf
        if entropy_mode is not None:
            self._values["entropy_mode"] = entropy_mode
        if frame_rate is not None:
            self._values["frame_rate"] = frame_rate
        if height is not None:
            self._values["height"] = height
        if label is not None:
            self._values["label"] = label
        if level is not None:
            self._values["level"] = level
        if max_bitrate is not None:
            self._values["max_bitrate"] = max_bitrate
        if profile is not None:
            self._values["profile"] = profile
        if reference_frames is not None:
            self._values["reference_frames"] = reference_frames
        if slices is not None:
            self._values["slices"] = slices
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def bitrate(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.'''
        result = self._values.get("bitrate")
        assert result is not None, "Required property 'bitrate' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def adaptive_b_frame_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#adaptive_b_frame_enabled MediaTransform#adaptive_b_frame_enabled}.'''
        result = self._values.get("adaptive_b_frame_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def b_frames(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#b_frames MediaTransform#b_frames}.'''
        result = self._values.get("b_frames")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def buffer_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#buffer_window MediaTransform#buffer_window}.'''
        result = self._values.get("buffer_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crf(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crf MediaTransform#crf}.'''
        result = self._values.get("crf")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def entropy_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#entropy_mode MediaTransform#entropy_mode}.'''
        result = self._values.get("entropy_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frame_rate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#frame_rate MediaTransform#frame_rate}.'''
        result = self._values.get("frame_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def height(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#level MediaTransform#level}.'''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_bitrate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate MediaTransform#max_bitrate}.'''
        result = self._values.get("max_bitrate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reference_frames(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#reference_frames MediaTransform#reference_frames}.'''
        result = self._values.get("reference_frames")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def slices(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#slices MediaTransform#slices}.'''
        result = self._values.get("slices")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecH264VideoLayer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecH264VideoLayerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH264VideoLayerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f534d213b35b6898cc9e5db06b441d9cdecac1f8b621b45ffa8c07dd9648095)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetCodecH264VideoLayerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e8108db937585b6847cecbd2ac6eb2f2d7102498fc54e5e524ba59c6c6f00e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetCodecH264VideoLayerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14b2a944761d822fbc52f87282826f434d61ae3f3678ed4d98b77742c46fe1af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f61dc6a0e9ecd4230db1e50671cfbca592fec19fccf5c8f71188e189e530d601)
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
            type_hints = typing.get_type_hints(_typecheckingstub__346094e91bf7d656cd7e75be5d69e6f9b31a02981401113107c0a0e809144823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b6d5b320a9d55d6c611f2d708d83a978796f46986f65e82aafd5e31eb1c829b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecH264VideoLayerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH264VideoLayerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8452b03a2beb565be3a2197558eb5fac7a671c0a8661a56d46848a08a382dce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAdaptiveBFrameEnabled")
    def reset_adaptive_b_frame_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdaptiveBFrameEnabled", []))

    @jsii.member(jsii_name="resetBFrames")
    def reset_b_frames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBFrames", []))

    @jsii.member(jsii_name="resetBufferWindow")
    def reset_buffer_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBufferWindow", []))

    @jsii.member(jsii_name="resetCrf")
    def reset_crf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrf", []))

    @jsii.member(jsii_name="resetEntropyMode")
    def reset_entropy_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntropyMode", []))

    @jsii.member(jsii_name="resetFrameRate")
    def reset_frame_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrameRate", []))

    @jsii.member(jsii_name="resetHeight")
    def reset_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeight", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetLevel")
    def reset_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLevel", []))

    @jsii.member(jsii_name="resetMaxBitrate")
    def reset_max_bitrate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBitrate", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetReferenceFrames")
    def reset_reference_frames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferenceFrames", []))

    @jsii.member(jsii_name="resetSlices")
    def reset_slices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlices", []))

    @jsii.member(jsii_name="resetWidth")
    def reset_width(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidth", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveBFrameEnabledInput")
    def adaptive_b_frame_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "adaptiveBFrameEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="bFramesInput")
    def b_frames_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bFramesInput"))

    @builtins.property
    @jsii.member(jsii_name="bitrateInput")
    def bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="bufferWindowInput")
    def buffer_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bufferWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="crfInput")
    def crf_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "crfInput"))

    @builtins.property
    @jsii.member(jsii_name="entropyModeInput")
    def entropy_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entropyModeInput"))

    @builtins.property
    @jsii.member(jsii_name="frameRateInput")
    def frame_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frameRateInput"))

    @builtins.property
    @jsii.member(jsii_name="heightInput")
    def height_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "heightInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="levelInput")
    def level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "levelInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBitrateInput")
    def max_bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceFramesInput")
    def reference_frames_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "referenceFramesInput"))

    @builtins.property
    @jsii.member(jsii_name="slicesInput")
    def slices_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "slicesInput"))

    @builtins.property
    @jsii.member(jsii_name="widthInput")
    def width_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widthInput"))

    @builtins.property
    @jsii.member(jsii_name="adaptiveBFrameEnabled")
    def adaptive_b_frame_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "adaptiveBFrameEnabled"))

    @adaptive_b_frame_enabled.setter
    def adaptive_b_frame_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__243111df7a6b4f106295925f100ecd0c600b16110edaecc393c64c0f39f51dda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adaptiveBFrameEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="bFrames")
    def b_frames(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bFrames"))

    @b_frames.setter
    def b_frames(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a405d9d00539d6685d02e5798a6bc0eeb5f6081cec787b5016aa6a69997c0eae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bFrames", value)

    @builtins.property
    @jsii.member(jsii_name="bitrate")
    def bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bitrate"))

    @bitrate.setter
    def bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b17fa8c0420c5c642b0d2dcd2e3731da6da3f30e37255bb14829d26e12ab67df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bitrate", value)

    @builtins.property
    @jsii.member(jsii_name="bufferWindow")
    def buffer_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bufferWindow"))

    @buffer_window.setter
    def buffer_window(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f99dd9d583f564c7302aa80a11bd29f9c1437a4de80ae37bede51b8d1c361f12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bufferWindow", value)

    @builtins.property
    @jsii.member(jsii_name="crf")
    def crf(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "crf"))

    @crf.setter
    def crf(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac55b051d0d12087a8a806a7ae0c737245f181d3d712917d96e2137bf7bbdb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crf", value)

    @builtins.property
    @jsii.member(jsii_name="entropyMode")
    def entropy_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entropyMode"))

    @entropy_mode.setter
    def entropy_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7709245ac4372982479b439edd2f7bdad3b941a80ffb237ddda8a99ca0ac89ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entropyMode", value)

    @builtins.property
    @jsii.member(jsii_name="frameRate")
    def frame_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frameRate"))

    @frame_rate.setter
    def frame_rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c46c9138a2a33ae3990fca067638e773d64c12d3767d2688f8e0c2e36c8a7bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frameRate", value)

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "height"))

    @height.setter
    def height(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__779f14d368137c32ff8a24dc6277c9a90310b9bda49c509e353380e2a1a1c622)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "height", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__490790497c8d91b25bda86a8d0fb9d13e8250f800d925b90bf7a18de7746f0a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="level")
    def level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "level"))

    @level.setter
    def level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52ac382ec0f6e9dbc59178e36d27536a8165508f211068af0c42c634c8b76e52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "level", value)

    @builtins.property
    @jsii.member(jsii_name="maxBitrate")
    def max_bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBitrate"))

    @max_bitrate.setter
    def max_bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efbd3450a96e252d1bef7fc148c5053d949566c3838e51b8bc43d0a0d3315b35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBitrate", value)

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6febdf90af8d9588d5b96a9cb36e7dd3e16f20c15e67fbb163b2fa0a7072db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value)

    @builtins.property
    @jsii.member(jsii_name="referenceFrames")
    def reference_frames(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceFrames"))

    @reference_frames.setter
    def reference_frames(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9357c1d9d8cffe04a506badbf568b91d8a7ddf74c7a8dae29260876f40976e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceFrames", value)

    @builtins.property
    @jsii.member(jsii_name="slices")
    def slices(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "slices"))

    @slices.setter
    def slices(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6b0085e8c1dbd5ffc7910e9de920d1bcf084906c2301edb7ffd0a0581b2fafe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slices", value)

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "width"))

    @width.setter
    def width(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da362f963cbd9bc3c9329c50c552958c80952ce3810d431e59ec01163ec41042)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "width", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e125e9cb8e0e896a03d2135fc758b146d14c8c9e9461c6ff942f40da19fcfb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecH264VideoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH264VideoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ee4a6f1788cfe3730d2b15fc7fd57a461cdace6545a549a86cc947e65086363)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLayer")
    def put_layer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce41dd102b2fd416a64215a2f5330e8e287cc62565b4cac215dd3fb528db4230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLayer", [value]))

    @jsii.member(jsii_name="resetComplexity")
    def reset_complexity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplexity", []))

    @jsii.member(jsii_name="resetKeyFrameInterval")
    def reset_key_frame_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFrameInterval", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetLayer")
    def reset_layer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLayer", []))

    @jsii.member(jsii_name="resetRateControlMode")
    def reset_rate_control_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRateControlMode", []))

    @jsii.member(jsii_name="resetSceneChangeDetectionEnabled")
    def reset_scene_change_detection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSceneChangeDetectionEnabled", []))

    @jsii.member(jsii_name="resetStretchMode")
    def reset_stretch_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStretchMode", []))

    @jsii.member(jsii_name="resetSyncMode")
    def reset_sync_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyncMode", []))

    @builtins.property
    @jsii.member(jsii_name="layer")
    def layer(self) -> MediaTransformOutputCustomPresetCodecH264VideoLayerList:
        return typing.cast(MediaTransformOutputCustomPresetCodecH264VideoLayerList, jsii.get(self, "layer"))

    @builtins.property
    @jsii.member(jsii_name="complexityInput")
    def complexity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complexityInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFrameIntervalInput")
    def key_frame_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFrameIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="layerInput")
    def layer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]], jsii.get(self, "layerInput"))

    @builtins.property
    @jsii.member(jsii_name="rateControlModeInput")
    def rate_control_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rateControlModeInput"))

    @builtins.property
    @jsii.member(jsii_name="sceneChangeDetectionEnabledInput")
    def scene_change_detection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sceneChangeDetectionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="stretchModeInput")
    def stretch_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stretchModeInput"))

    @builtins.property
    @jsii.member(jsii_name="syncModeInput")
    def sync_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "syncModeInput"))

    @builtins.property
    @jsii.member(jsii_name="complexity")
    def complexity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "complexity"))

    @complexity.setter
    def complexity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85574a4a7e744437d62c4e44b369b9650ac364b3b67755c2d8dda32f1ef6f29d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complexity", value)

    @builtins.property
    @jsii.member(jsii_name="keyFrameInterval")
    def key_frame_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyFrameInterval"))

    @key_frame_interval.setter
    def key_frame_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15f9dd22e2e15b9775223c1a535110bcc32fb44297697a2480db5779b41aa090)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFrameInterval", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acb4fa35f48aaaba49631fc0d36732a5bde34f47016cf20de915bfef6027fa6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="rateControlMode")
    def rate_control_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rateControlMode"))

    @rate_control_mode.setter
    def rate_control_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0de4c419e94f5fd621ff0051463b796150005a082db9594b514c8cad860743a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rateControlMode", value)

    @builtins.property
    @jsii.member(jsii_name="sceneChangeDetectionEnabled")
    def scene_change_detection_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sceneChangeDetectionEnabled"))

    @scene_change_detection_enabled.setter
    def scene_change_detection_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f4c424d4f8f8861b4cd80137ea7f4e60ea30ebacf0b39fb72af34d3cda9441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sceneChangeDetectionEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="stretchMode")
    def stretch_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stretchMode"))

    @stretch_mode.setter
    def stretch_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3697787796e8b007527ca4392ca7119292c24185a190c9e51e0f65d1ee48aad6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stretchMode", value)

    @builtins.property
    @jsii.member(jsii_name="syncMode")
    def sync_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncMode"))

    @sync_mode.setter
    def sync_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3880029924d5341ec4a57ab25ea03b8d255cf5985d3405b8f172591441e30c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncMode", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecH264Video]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecH264Video], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecH264Video],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17454c0ba2d87d14be7debf069d616cc6f7cf452cb1a1f3f79972223cb58776)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH265Video",
    jsii_struct_bases=[],
    name_mapping={
        "complexity": "complexity",
        "key_frame_interval": "keyFrameInterval",
        "label": "label",
        "layer": "layer",
        "scene_change_detection_enabled": "sceneChangeDetectionEnabled",
        "stretch_mode": "stretchMode",
        "sync_mode": "syncMode",
    },
)
class MediaTransformOutputCustomPresetCodecH265Video:
    def __init__(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        key_frame_interval: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetCodecH265VideoLayer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        stretch_mode: typing.Optional[builtins.str] = None,
        sync_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param key_frame_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param layer: layer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        :param scene_change_detection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.
        :param stretch_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.
        :param sync_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c2132a38699534039ae15fea77b210359922af3a65de92c73d084d4bf9b136e)
            check_type(argname="argument complexity", value=complexity, expected_type=type_hints["complexity"])
            check_type(argname="argument key_frame_interval", value=key_frame_interval, expected_type=type_hints["key_frame_interval"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument layer", value=layer, expected_type=type_hints["layer"])
            check_type(argname="argument scene_change_detection_enabled", value=scene_change_detection_enabled, expected_type=type_hints["scene_change_detection_enabled"])
            check_type(argname="argument stretch_mode", value=stretch_mode, expected_type=type_hints["stretch_mode"])
            check_type(argname="argument sync_mode", value=sync_mode, expected_type=type_hints["sync_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if complexity is not None:
            self._values["complexity"] = complexity
        if key_frame_interval is not None:
            self._values["key_frame_interval"] = key_frame_interval
        if label is not None:
            self._values["label"] = label
        if layer is not None:
            self._values["layer"] = layer
        if scene_change_detection_enabled is not None:
            self._values["scene_change_detection_enabled"] = scene_change_detection_enabled
        if stretch_mode is not None:
            self._values["stretch_mode"] = stretch_mode
        if sync_mode is not None:
            self._values["sync_mode"] = sync_mode

    @builtins.property
    def complexity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.'''
        result = self._values.get("complexity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_frame_interval(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.'''
        result = self._values.get("key_frame_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodecH265VideoLayer"]]]:
        '''layer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        '''
        result = self._values.get("layer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetCodecH265VideoLayer"]]], result)

    @builtins.property
    def scene_change_detection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.'''
        result = self._values.get("scene_change_detection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def stretch_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.'''
        result = self._values.get("stretch_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sync_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.'''
        result = self._values.get("sync_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecH265Video(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH265VideoLayer",
    jsii_struct_bases=[],
    name_mapping={
        "bitrate": "bitrate",
        "adaptive_b_frame_enabled": "adaptiveBFrameEnabled",
        "b_frames": "bFrames",
        "buffer_window": "bufferWindow",
        "crf": "crf",
        "frame_rate": "frameRate",
        "height": "height",
        "label": "label",
        "level": "level",
        "max_bitrate": "maxBitrate",
        "profile": "profile",
        "reference_frames": "referenceFrames",
        "slices": "slices",
        "width": "width",
    },
)
class MediaTransformOutputCustomPresetCodecH265VideoLayer:
    def __init__(
        self,
        *,
        bitrate: jsii.Number,
        adaptive_b_frame_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        b_frames: typing.Optional[jsii.Number] = None,
        buffer_window: typing.Optional[builtins.str] = None,
        crf: typing.Optional[jsii.Number] = None,
        frame_rate: typing.Optional[builtins.str] = None,
        height: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        level: typing.Optional[builtins.str] = None,
        max_bitrate: typing.Optional[jsii.Number] = None,
        profile: typing.Optional[builtins.str] = None,
        reference_frames: typing.Optional[jsii.Number] = None,
        slices: typing.Optional[jsii.Number] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param adaptive_b_frame_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#adaptive_b_frame_enabled MediaTransform#adaptive_b_frame_enabled}.
        :param b_frames: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#b_frames MediaTransform#b_frames}.
        :param buffer_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#buffer_window MediaTransform#buffer_window}.
        :param crf: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crf MediaTransform#crf}.
        :param frame_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#frame_rate MediaTransform#frame_rate}.
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#level MediaTransform#level}.
        :param max_bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate MediaTransform#max_bitrate}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.
        :param reference_frames: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#reference_frames MediaTransform#reference_frames}.
        :param slices: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#slices MediaTransform#slices}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feb8641d5a996da27949de372d5433e134f1b471ed1a72c0b6d4b2362c2c108d)
            check_type(argname="argument bitrate", value=bitrate, expected_type=type_hints["bitrate"])
            check_type(argname="argument adaptive_b_frame_enabled", value=adaptive_b_frame_enabled, expected_type=type_hints["adaptive_b_frame_enabled"])
            check_type(argname="argument b_frames", value=b_frames, expected_type=type_hints["b_frames"])
            check_type(argname="argument buffer_window", value=buffer_window, expected_type=type_hints["buffer_window"])
            check_type(argname="argument crf", value=crf, expected_type=type_hints["crf"])
            check_type(argname="argument frame_rate", value=frame_rate, expected_type=type_hints["frame_rate"])
            check_type(argname="argument height", value=height, expected_type=type_hints["height"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument level", value=level, expected_type=type_hints["level"])
            check_type(argname="argument max_bitrate", value=max_bitrate, expected_type=type_hints["max_bitrate"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument reference_frames", value=reference_frames, expected_type=type_hints["reference_frames"])
            check_type(argname="argument slices", value=slices, expected_type=type_hints["slices"])
            check_type(argname="argument width", value=width, expected_type=type_hints["width"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bitrate": bitrate,
        }
        if adaptive_b_frame_enabled is not None:
            self._values["adaptive_b_frame_enabled"] = adaptive_b_frame_enabled
        if b_frames is not None:
            self._values["b_frames"] = b_frames
        if buffer_window is not None:
            self._values["buffer_window"] = buffer_window
        if crf is not None:
            self._values["crf"] = crf
        if frame_rate is not None:
            self._values["frame_rate"] = frame_rate
        if height is not None:
            self._values["height"] = height
        if label is not None:
            self._values["label"] = label
        if level is not None:
            self._values["level"] = level
        if max_bitrate is not None:
            self._values["max_bitrate"] = max_bitrate
        if profile is not None:
            self._values["profile"] = profile
        if reference_frames is not None:
            self._values["reference_frames"] = reference_frames
        if slices is not None:
            self._values["slices"] = slices
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def bitrate(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.'''
        result = self._values.get("bitrate")
        assert result is not None, "Required property 'bitrate' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def adaptive_b_frame_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#adaptive_b_frame_enabled MediaTransform#adaptive_b_frame_enabled}.'''
        result = self._values.get("adaptive_b_frame_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def b_frames(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#b_frames MediaTransform#b_frames}.'''
        result = self._values.get("b_frames")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def buffer_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#buffer_window MediaTransform#buffer_window}.'''
        result = self._values.get("buffer_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crf(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crf MediaTransform#crf}.'''
        result = self._values.get("crf")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def frame_rate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#frame_rate MediaTransform#frame_rate}.'''
        result = self._values.get("frame_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def height(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#level MediaTransform#level}.'''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_bitrate(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#max_bitrate MediaTransform#max_bitrate}.'''
        result = self._values.get("max_bitrate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reference_frames(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#reference_frames MediaTransform#reference_frames}.'''
        result = self._values.get("reference_frames")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def slices(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#slices MediaTransform#slices}.'''
        result = self._values.get("slices")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def width(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetCodecH265VideoLayer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetCodecH265VideoLayerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH265VideoLayerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d2f77d9262927d06e7adcc912720850529f928d3c593bef40751cdc5df7c103)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetCodecH265VideoLayerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5560f191103cea17c2d517a872afd7de8ef2d146f9a482fc918dad4b91e4ab6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetCodecH265VideoLayerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d935215b944526a9345d538e0b59ae60024f284f6a9e11128c73574ac0751460)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e0371add1eab2de3aa7a52a3bee7d9196ce43b01715231e02c336c6d6724a02)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7359bb57bab29360f8e759cc36d76c2af14fa79859e84642633e1bd821243de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1384494e7b25290e690f8a7a06ac9389bba0efad28a35faeb7bd6536d79183b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecH265VideoLayerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH265VideoLayerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26a756c3b95b0a51b2fe2deeb783803c714af6b28210a07fb8442d19b6fe23e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAdaptiveBFrameEnabled")
    def reset_adaptive_b_frame_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdaptiveBFrameEnabled", []))

    @jsii.member(jsii_name="resetBFrames")
    def reset_b_frames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBFrames", []))

    @jsii.member(jsii_name="resetBufferWindow")
    def reset_buffer_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBufferWindow", []))

    @jsii.member(jsii_name="resetCrf")
    def reset_crf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrf", []))

    @jsii.member(jsii_name="resetFrameRate")
    def reset_frame_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrameRate", []))

    @jsii.member(jsii_name="resetHeight")
    def reset_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeight", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetLevel")
    def reset_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLevel", []))

    @jsii.member(jsii_name="resetMaxBitrate")
    def reset_max_bitrate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBitrate", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetReferenceFrames")
    def reset_reference_frames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferenceFrames", []))

    @jsii.member(jsii_name="resetSlices")
    def reset_slices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlices", []))

    @jsii.member(jsii_name="resetWidth")
    def reset_width(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidth", []))

    @builtins.property
    @jsii.member(jsii_name="adaptiveBFrameEnabledInput")
    def adaptive_b_frame_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "adaptiveBFrameEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="bFramesInput")
    def b_frames_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bFramesInput"))

    @builtins.property
    @jsii.member(jsii_name="bitrateInput")
    def bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="bufferWindowInput")
    def buffer_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bufferWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="crfInput")
    def crf_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "crfInput"))

    @builtins.property
    @jsii.member(jsii_name="frameRateInput")
    def frame_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frameRateInput"))

    @builtins.property
    @jsii.member(jsii_name="heightInput")
    def height_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "heightInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="levelInput")
    def level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "levelInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBitrateInput")
    def max_bitrate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBitrateInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceFramesInput")
    def reference_frames_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "referenceFramesInput"))

    @builtins.property
    @jsii.member(jsii_name="slicesInput")
    def slices_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "slicesInput"))

    @builtins.property
    @jsii.member(jsii_name="widthInput")
    def width_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widthInput"))

    @builtins.property
    @jsii.member(jsii_name="adaptiveBFrameEnabled")
    def adaptive_b_frame_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "adaptiveBFrameEnabled"))

    @adaptive_b_frame_enabled.setter
    def adaptive_b_frame_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__525d611fc9970e5d54f1379cf15da1a475765f210a99715b335aebcc6e861186)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adaptiveBFrameEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="bFrames")
    def b_frames(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bFrames"))

    @b_frames.setter
    def b_frames(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c0c400a29f3b4df551a3b34ef186385142839469bc7ffb0dd2309dc7cb84356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bFrames", value)

    @builtins.property
    @jsii.member(jsii_name="bitrate")
    def bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bitrate"))

    @bitrate.setter
    def bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54aea717e9a399451a82ceab3f5dd5609c5acce2f9876b302d6ec13c6f318f8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bitrate", value)

    @builtins.property
    @jsii.member(jsii_name="bufferWindow")
    def buffer_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bufferWindow"))

    @buffer_window.setter
    def buffer_window(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28897d4a6782be58909bc3d27990991a6ccfd09a8a4c3e88718cbf8b0bb0ff44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bufferWindow", value)

    @builtins.property
    @jsii.member(jsii_name="crf")
    def crf(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "crf"))

    @crf.setter
    def crf(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__047b263dae683bac1d8d2dced13bd23d98ad3722201eb15235c84c6200b14169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crf", value)

    @builtins.property
    @jsii.member(jsii_name="frameRate")
    def frame_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frameRate"))

    @frame_rate.setter
    def frame_rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4dc0f4f6fd314b1b88d7cf875dff5127c384ad011036e3ba9dbb6497e651aed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frameRate", value)

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "height"))

    @height.setter
    def height(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd7e6f639859060596c26bafa03e980759b5908044917b0da222752458f25a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "height", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18f50ea03e58c4d2652e7b5e064b3cb0eb66f515eca7eace501def6d05a22ee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="level")
    def level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "level"))

    @level.setter
    def level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5230b256c9fa679795de4e3679e4870f32263d8fae518cf4333069ffad4616d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "level", value)

    @builtins.property
    @jsii.member(jsii_name="maxBitrate")
    def max_bitrate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBitrate"))

    @max_bitrate.setter
    def max_bitrate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8568f6dff2f261c435f75c0beecbed4e8fae8ac33500a6f80bce17bab8cde04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBitrate", value)

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c953948385c5929a5325d1cf3e064a77df79c1a7d01166679f8fc1f42afba2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value)

    @builtins.property
    @jsii.member(jsii_name="referenceFrames")
    def reference_frames(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceFrames"))

    @reference_frames.setter
    def reference_frames(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ecdda1009a9d4e6f621e463259a9a85134a79426579be8336d985f2bd885939)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceFrames", value)

    @builtins.property
    @jsii.member(jsii_name="slices")
    def slices(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "slices"))

    @slices.setter
    def slices(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__797b56ad9ab0bd5355a7191a6baaa33d6f639c3608e5f540a42bdb70ca62c04e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slices", value)

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "width"))

    @width.setter
    def width(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49e08f754be02af1b452cdeca60fdaee7464f9705a4a1da54262ce049e7061d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "width", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd051ac8e3111b243f3fe6a977cf85289530771f46ef243323a7c8dd1c5a806f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecH265VideoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecH265VideoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9eeec47f8d6240c65bb65d88794793227f77a4f8bbdeea45867e7759c9a5b9e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLayer")
    def put_layer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__788a86d2cf268bc3db8bd8f2491f34799129e0e96f18aa90bb889441c1647561)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLayer", [value]))

    @jsii.member(jsii_name="resetComplexity")
    def reset_complexity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComplexity", []))

    @jsii.member(jsii_name="resetKeyFrameInterval")
    def reset_key_frame_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFrameInterval", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetLayer")
    def reset_layer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLayer", []))

    @jsii.member(jsii_name="resetSceneChangeDetectionEnabled")
    def reset_scene_change_detection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSceneChangeDetectionEnabled", []))

    @jsii.member(jsii_name="resetStretchMode")
    def reset_stretch_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStretchMode", []))

    @jsii.member(jsii_name="resetSyncMode")
    def reset_sync_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyncMode", []))

    @builtins.property
    @jsii.member(jsii_name="layer")
    def layer(self) -> MediaTransformOutputCustomPresetCodecH265VideoLayerList:
        return typing.cast(MediaTransformOutputCustomPresetCodecH265VideoLayerList, jsii.get(self, "layer"))

    @builtins.property
    @jsii.member(jsii_name="complexityInput")
    def complexity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "complexityInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFrameIntervalInput")
    def key_frame_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFrameIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="layerInput")
    def layer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]], jsii.get(self, "layerInput"))

    @builtins.property
    @jsii.member(jsii_name="sceneChangeDetectionEnabledInput")
    def scene_change_detection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sceneChangeDetectionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="stretchModeInput")
    def stretch_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stretchModeInput"))

    @builtins.property
    @jsii.member(jsii_name="syncModeInput")
    def sync_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "syncModeInput"))

    @builtins.property
    @jsii.member(jsii_name="complexity")
    def complexity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "complexity"))

    @complexity.setter
    def complexity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e48c967f53b702255661887acb24f0ded13b3c9bf78a96dc77a07e3e77431262)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "complexity", value)

    @builtins.property
    @jsii.member(jsii_name="keyFrameInterval")
    def key_frame_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyFrameInterval"))

    @key_frame_interval.setter
    def key_frame_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57edd75dc69f1ad650f2fb2e208b077bbd339d07f285926ea7373b6c88bc9b20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFrameInterval", value)

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3db6f070c0bc766ea366a82115f0913787b3a1cac87909a23558ceab47b6ed7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value)

    @builtins.property
    @jsii.member(jsii_name="sceneChangeDetectionEnabled")
    def scene_change_detection_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sceneChangeDetectionEnabled"))

    @scene_change_detection_enabled.setter
    def scene_change_detection_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fea77d04ecf2af668b2fef6c750b68fe625391d69eacfcb301c72f16d383221e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sceneChangeDetectionEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="stretchMode")
    def stretch_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stretchMode"))

    @stretch_mode.setter
    def stretch_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a793403f5ec3a2ca987dc5158e5817abb4e24728a3a97b486ec9bbc5441a419)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stretchMode", value)

    @builtins.property
    @jsii.member(jsii_name="syncMode")
    def sync_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syncMode"))

    @sync_mode.setter
    def sync_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c82c6e85a41c284efff948e42e2025cf5050f8e574b09affe2875ffb1aeb329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncMode", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecH265Video]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecH265Video], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetCodecH265Video],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__714d5bb0ee6b6cecc8d2726c0e63a88117e0f3507f1aed7d585c560eaaccdcee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eaf84390b48d975ff7e5ff782452612fe860e25247393d9f2f4d9f42c258e292)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetCodecOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0925b03f3f47ffb4dc1b567f21e56f4ca1cc7eeab97abf86322076ae7588bb4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetCodecOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd3d709e5383f3d5548c28f99e7cc7ac08ef82dba71fe5b2256850af8024014)
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
            type_hints = typing.get_type_hints(_typecheckingstub__578cddb836fe42cc2c111db9510ad6e7777e18dbd6b045b0d8c8f4a1ffe9f556)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7b617a9a3cc99979c8e58ea8b0227b2a647b7974917bcc88f742c19f8fcabd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b54de4bcf0480219c60973d8d49a3e89b8faeb6f0bfc49d2868a2b1aee9a412e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetCodecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetCodecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc1a793d4739d015f3332cc48f62418043972e4f38a7a65ac7e808c062ef7548)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAacAudio")
    def put_aac_audio(
        self,
        *,
        bitrate: typing.Optional[jsii.Number] = None,
        channels: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        profile: typing.Optional[builtins.str] = None,
        sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param channels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#profile MediaTransform#profile}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.
        '''
        value = MediaTransformOutputCustomPresetCodecAacAudio(
            bitrate=bitrate,
            channels=channels,
            label=label,
            profile=profile,
            sampling_rate=sampling_rate,
        )

        return typing.cast(None, jsii.invoke(self, "putAacAudio", [value]))

    @jsii.member(jsii_name="putCopyAudio")
    def put_copy_audio(self, *, label: typing.Optional[builtins.str] = None) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        '''
        value = MediaTransformOutputCustomPresetCodecCopyAudio(label=label)

        return typing.cast(None, jsii.invoke(self, "putCopyAudio", [value]))

    @jsii.member(jsii_name="putCopyVideo")
    def put_copy_video(self, *, label: typing.Optional[builtins.str] = None) -> None:
        '''
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        '''
        value = MediaTransformOutputCustomPresetCodecCopyVideo(label=label)

        return typing.cast(None, jsii.invoke(self, "putCopyVideo", [value]))

    @jsii.member(jsii_name="putDdAudio")
    def put_dd_audio(
        self,
        *,
        bitrate: typing.Optional[jsii.Number] = None,
        channels: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        sampling_rate: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param bitrate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#bitrate MediaTransform#bitrate}.
        :param channels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#channels MediaTransform#channels}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sampling_rate MediaTransform#sampling_rate}.
        '''
        value = MediaTransformOutputCustomPresetCodecDdAudio(
            bitrate=bitrate,
            channels=channels,
            label=label,
            sampling_rate=sampling_rate,
        )

        return typing.cast(None, jsii.invoke(self, "putDdAudio", [value]))

    @jsii.member(jsii_name="putH264Video")
    def put_h264_video(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        key_frame_interval: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, typing.Dict[builtins.str, typing.Any]]]]] = None,
        rate_control_mode: typing.Optional[builtins.str] = None,
        scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        stretch_mode: typing.Optional[builtins.str] = None,
        sync_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param key_frame_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param layer: layer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        :param rate_control_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rate_control_mode MediaTransform#rate_control_mode}.
        :param scene_change_detection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.
        :param stretch_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.
        :param sync_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.
        '''
        value = MediaTransformOutputCustomPresetCodecH264Video(
            complexity=complexity,
            key_frame_interval=key_frame_interval,
            label=label,
            layer=layer,
            rate_control_mode=rate_control_mode,
            scene_change_detection_enabled=scene_change_detection_enabled,
            stretch_mode=stretch_mode,
            sync_mode=sync_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putH264Video", [value]))

    @jsii.member(jsii_name="putH265Video")
    def put_h265_video(
        self,
        *,
        complexity: typing.Optional[builtins.str] = None,
        key_frame_interval: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, typing.Dict[builtins.str, typing.Any]]]]] = None,
        scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        stretch_mode: typing.Optional[builtins.str] = None,
        sync_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param complexity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#complexity MediaTransform#complexity}.
        :param key_frame_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#key_frame_interval MediaTransform#key_frame_interval}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#label MediaTransform#label}.
        :param layer: layer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#layer MediaTransform#layer}
        :param scene_change_detection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#scene_change_detection_enabled MediaTransform#scene_change_detection_enabled}.
        :param stretch_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#stretch_mode MediaTransform#stretch_mode}.
        :param sync_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#sync_mode MediaTransform#sync_mode}.
        '''
        value = MediaTransformOutputCustomPresetCodecH265Video(
            complexity=complexity,
            key_frame_interval=key_frame_interval,
            label=label,
            layer=layer,
            scene_change_detection_enabled=scene_change_detection_enabled,
            stretch_mode=stretch_mode,
            sync_mode=sync_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putH265Video", [value]))

    @jsii.member(jsii_name="resetAacAudio")
    def reset_aac_audio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAacAudio", []))

    @jsii.member(jsii_name="resetCopyAudio")
    def reset_copy_audio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyAudio", []))

    @jsii.member(jsii_name="resetCopyVideo")
    def reset_copy_video(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyVideo", []))

    @jsii.member(jsii_name="resetDdAudio")
    def reset_dd_audio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDdAudio", []))

    @jsii.member(jsii_name="resetH264Video")
    def reset_h264_video(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetH264Video", []))

    @jsii.member(jsii_name="resetH265Video")
    def reset_h265_video(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetH265Video", []))

    @builtins.property
    @jsii.member(jsii_name="aacAudio")
    def aac_audio(self) -> MediaTransformOutputCustomPresetCodecAacAudioOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecAacAudioOutputReference, jsii.get(self, "aacAudio"))

    @builtins.property
    @jsii.member(jsii_name="copyAudio")
    def copy_audio(
        self,
    ) -> MediaTransformOutputCustomPresetCodecCopyAudioOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecCopyAudioOutputReference, jsii.get(self, "copyAudio"))

    @builtins.property
    @jsii.member(jsii_name="copyVideo")
    def copy_video(
        self,
    ) -> MediaTransformOutputCustomPresetCodecCopyVideoOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecCopyVideoOutputReference, jsii.get(self, "copyVideo"))

    @builtins.property
    @jsii.member(jsii_name="ddAudio")
    def dd_audio(self) -> MediaTransformOutputCustomPresetCodecDdAudioOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecDdAudioOutputReference, jsii.get(self, "ddAudio"))

    @builtins.property
    @jsii.member(jsii_name="h264Video")
    def h264_video(
        self,
    ) -> MediaTransformOutputCustomPresetCodecH264VideoOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecH264VideoOutputReference, jsii.get(self, "h264Video"))

    @builtins.property
    @jsii.member(jsii_name="h265Video")
    def h265_video(
        self,
    ) -> MediaTransformOutputCustomPresetCodecH265VideoOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetCodecH265VideoOutputReference, jsii.get(self, "h265Video"))

    @builtins.property
    @jsii.member(jsii_name="aacAudioInput")
    def aac_audio_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio], jsii.get(self, "aacAudioInput"))

    @builtins.property
    @jsii.member(jsii_name="copyAudioInput")
    def copy_audio_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio], jsii.get(self, "copyAudioInput"))

    @builtins.property
    @jsii.member(jsii_name="copyVideoInput")
    def copy_video_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo], jsii.get(self, "copyVideoInput"))

    @builtins.property
    @jsii.member(jsii_name="ddAudioInput")
    def dd_audio_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio], jsii.get(self, "ddAudioInput"))

    @builtins.property
    @jsii.member(jsii_name="h264VideoInput")
    def h264_video_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecH264Video]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecH264Video], jsii.get(self, "h264VideoInput"))

    @builtins.property
    @jsii.member(jsii_name="h265VideoInput")
    def h265_video_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetCodecH265Video]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetCodecH265Video], jsii.get(self, "h265VideoInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodec, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodec, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodec, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bc2cb69feb978543c48a7a6cdb2cd4e0d21695afbca33daff128ee2342ed3d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilter",
    jsii_struct_bases=[],
    name_mapping={
        "crop_rectangle": "cropRectangle",
        "deinterlace": "deinterlace",
        "fade_in": "fadeIn",
        "fade_out": "fadeOut",
        "overlay": "overlay",
        "rotation": "rotation",
    },
)
class MediaTransformOutputCustomPresetFilter:
    def __init__(
        self,
        *,
        crop_rectangle: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterCropRectangle", typing.Dict[builtins.str, typing.Any]]] = None,
        deinterlace: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterDeinterlace", typing.Dict[builtins.str, typing.Any]]] = None,
        fade_in: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterFadeIn", typing.Dict[builtins.str, typing.Any]]] = None,
        fade_out: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterFadeOut", typing.Dict[builtins.str, typing.Any]]] = None,
        overlay: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFilterOverlay", typing.Dict[builtins.str, typing.Any]]]]] = None,
        rotation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param crop_rectangle: crop_rectangle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        :param deinterlace: deinterlace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#deinterlace MediaTransform#deinterlace}
        :param fade_in: fade_in block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in MediaTransform#fade_in}
        :param fade_out: fade_out block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out MediaTransform#fade_out}
        :param overlay: overlay block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#overlay MediaTransform#overlay}
        :param rotation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rotation MediaTransform#rotation}.
        '''
        if isinstance(crop_rectangle, dict):
            crop_rectangle = MediaTransformOutputCustomPresetFilterCropRectangle(**crop_rectangle)
        if isinstance(deinterlace, dict):
            deinterlace = MediaTransformOutputCustomPresetFilterDeinterlace(**deinterlace)
        if isinstance(fade_in, dict):
            fade_in = MediaTransformOutputCustomPresetFilterFadeIn(**fade_in)
        if isinstance(fade_out, dict):
            fade_out = MediaTransformOutputCustomPresetFilterFadeOut(**fade_out)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9b0f5a34aba8329ea4a236b3f00be748f5698db6b4e60b44a0abdc02980d191)
            check_type(argname="argument crop_rectangle", value=crop_rectangle, expected_type=type_hints["crop_rectangle"])
            check_type(argname="argument deinterlace", value=deinterlace, expected_type=type_hints["deinterlace"])
            check_type(argname="argument fade_in", value=fade_in, expected_type=type_hints["fade_in"])
            check_type(argname="argument fade_out", value=fade_out, expected_type=type_hints["fade_out"])
            check_type(argname="argument overlay", value=overlay, expected_type=type_hints["overlay"])
            check_type(argname="argument rotation", value=rotation, expected_type=type_hints["rotation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if crop_rectangle is not None:
            self._values["crop_rectangle"] = crop_rectangle
        if deinterlace is not None:
            self._values["deinterlace"] = deinterlace
        if fade_in is not None:
            self._values["fade_in"] = fade_in
        if fade_out is not None:
            self._values["fade_out"] = fade_out
        if overlay is not None:
            self._values["overlay"] = overlay
        if rotation is not None:
            self._values["rotation"] = rotation

    @builtins.property
    def crop_rectangle(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterCropRectangle"]:
        '''crop_rectangle block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        '''
        result = self._values.get("crop_rectangle")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterCropRectangle"], result)

    @builtins.property
    def deinterlace(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterDeinterlace"]:
        '''deinterlace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#deinterlace MediaTransform#deinterlace}
        '''
        result = self._values.get("deinterlace")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterDeinterlace"], result)

    @builtins.property
    def fade_in(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterFadeIn"]:
        '''fade_in block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in MediaTransform#fade_in}
        '''
        result = self._values.get("fade_in")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterFadeIn"], result)

    @builtins.property
    def fade_out(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterFadeOut"]:
        '''fade_out block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out MediaTransform#fade_out}
        '''
        result = self._values.get("fade_out")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterFadeOut"], result)

    @builtins.property
    def overlay(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFilterOverlay"]]]:
        '''overlay block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#overlay MediaTransform#overlay}
        '''
        result = self._values.get("overlay")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFilterOverlay"]]], result)

    @builtins.property
    def rotation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rotation MediaTransform#rotation}.'''
        result = self._values.get("rotation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterCropRectangle",
    jsii_struct_bases=[],
    name_mapping={"height": "height", "left": "left", "top": "top", "width": "width"},
)
class MediaTransformOutputCustomPresetFilterCropRectangle:
    def __init__(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63a90e0cf3a378ad2202b5b298a9fb11f1fffb4a731a8b1c8c61529d26aebce8)
            check_type(argname="argument height", value=height, expected_type=type_hints["height"])
            check_type(argname="argument left", value=left, expected_type=type_hints["left"])
            check_type(argname="argument top", value=top, expected_type=type_hints["top"])
            check_type(argname="argument width", value=width, expected_type=type_hints["width"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if height is not None:
            self._values["height"] = height
        if left is not None:
            self._values["left"] = left
        if top is not None:
            self._values["top"] = top
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def height(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def left(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.'''
        result = self._values.get("left")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def top(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.'''
        result = self._values.get("top")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def width(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterCropRectangle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterCropRectangleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterCropRectangleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57782f0745a62ed5bb4f780715f84c595f3247c2104cfad3eb2569bd06799034)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHeight")
    def reset_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeight", []))

    @jsii.member(jsii_name="resetLeft")
    def reset_left(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLeft", []))

    @jsii.member(jsii_name="resetTop")
    def reset_top(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTop", []))

    @jsii.member(jsii_name="resetWidth")
    def reset_width(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidth", []))

    @builtins.property
    @jsii.member(jsii_name="heightInput")
    def height_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "heightInput"))

    @builtins.property
    @jsii.member(jsii_name="leftInput")
    def left_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "leftInput"))

    @builtins.property
    @jsii.member(jsii_name="topInput")
    def top_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topInput"))

    @builtins.property
    @jsii.member(jsii_name="widthInput")
    def width_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widthInput"))

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "height"))

    @height.setter
    def height(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49bd6bfabe2e6d995d21f85173c81d2f256b9158c9d8c10eb1c86dd7de212989)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "height", value)

    @builtins.property
    @jsii.member(jsii_name="left")
    def left(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "left"))

    @left.setter
    def left(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__547cd7adf4a352c36d39c3ad01671d97fba51280a2a2a9178cb2380566966641)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "left", value)

    @builtins.property
    @jsii.member(jsii_name="top")
    def top(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "top"))

    @top.setter
    def top(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8301e0dc1391360e8e3ebc1d533334d6eed338c30ffaff0848273b44e60bf14f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "top", value)

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "width"))

    @width.setter
    def width(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__963283f5f4bb0d471b89ba2cae569ee80a3d5bc620daf32841d2ad5b76ddc300)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "width", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c09e504d60f3692aa0cf543161fb162c1180171c8ffd8dc63d14aefb2a0e073)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterDeinterlace",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "parity": "parity"},
)
class MediaTransformOutputCustomPresetFilterDeinterlace:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        parity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#mode MediaTransform#mode}.
        :param parity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#parity MediaTransform#parity}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a2b7e60a16577b45e842a0b1e81605850f49ec0cadf0ac3c07b142021f7da8)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument parity", value=parity, expected_type=type_hints["parity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if parity is not None:
            self._values["parity"] = parity

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#mode MediaTransform#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#parity MediaTransform#parity}.'''
        result = self._values.get("parity")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterDeinterlace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterDeinterlaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterDeinterlaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4ea5e7541c9d204d52fd5ee4cace7851c215d4f70e97659fbb2eeb541ed5037)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetParity")
    def reset_parity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParity", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="parityInput")
    def parity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parityInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3caf2a85887bda1d35ef00b7401d28aadda0063e3e8905e28f5a722bd27d5070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value)

    @builtins.property
    @jsii.member(jsii_name="parity")
    def parity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parity"))

    @parity.setter
    def parity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21fc4afca0bc452208f70112e2f75b5308d8d1c2829880aa45800da3e3464456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parity", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__579498f06d441d4555ed5d861d11a5b29b14dfa9a6cc8c7cdf1aff1a9b074dc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterFadeIn",
    jsii_struct_bases=[],
    name_mapping={"duration": "duration", "fade_color": "fadeColor", "start": "start"},
)
class MediaTransformOutputCustomPresetFilterFadeIn:
    def __init__(
        self,
        *,
        duration: builtins.str,
        fade_color: builtins.str,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.
        :param fade_color: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8592f33870e8b521a2af754a50b4b6cb5fc40e538ff4d1d46b284305848b6941)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument fade_color", value=fade_color, expected_type=type_hints["fade_color"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "duration": duration,
            "fade_color": fade_color,
        }
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.'''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fade_color(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.'''
        result = self._values.get("fade_color")
        assert result is not None, "Required property 'fade_color' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterFadeIn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterFadeInOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterFadeInOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f35677a7d1cf3f98bef75e43cff11253c6918df8bd03058f6ccb1b0f6c761ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeColorInput")
    def fade_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeColorInput"))

    @builtins.property
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7d7083b6ff28551a5d4cbd5f0d589ae16fb5eaed8303de5007ed273a39ae39d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value)

    @builtins.property
    @jsii.member(jsii_name="fadeColor")
    def fade_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeColor"))

    @fade_color.setter
    def fade_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e52eb9f88e9650a3e1ec1c59470f69a7ba4ea85e0d68b5777a203ae5aa196cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeColor", value)

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e50473820fd67296dd38714d14de8a326e295589c49a7939d96a7ed1cd0a3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a8db5c0e37ca53057bc35236f350295ae7cd431957f87274ae236008769fcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterFadeOut",
    jsii_struct_bases=[],
    name_mapping={"duration": "duration", "fade_color": "fadeColor", "start": "start"},
)
class MediaTransformOutputCustomPresetFilterFadeOut:
    def __init__(
        self,
        *,
        duration: builtins.str,
        fade_color: builtins.str,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.
        :param fade_color: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765eedb410cb2bc43f8fe6206285494cd047a4254745c1cf3a06b64a9341c6cd)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument fade_color", value=fade_color, expected_type=type_hints["fade_color"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "duration": duration,
            "fade_color": fade_color,
        }
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def duration(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.'''
        result = self._values.get("duration")
        assert result is not None, "Required property 'duration' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fade_color(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.'''
        result = self._values.get("fade_color")
        assert result is not None, "Required property 'fade_color' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterFadeOut(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterFadeOutOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterFadeOutOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5cf0efd33277237f145912e57ad1f7357711d51c90b1f1ba40981f6a22c97491)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeColorInput")
    def fade_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeColorInput"))

    @builtins.property
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0880a0759ed38f029c4cf4cb5cbbaa869b4e51f2293aa00d3fab9c22c6c343f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value)

    @builtins.property
    @jsii.member(jsii_name="fadeColor")
    def fade_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeColor"))

    @fade_color.setter
    def fade_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f00a62c46e0c4a0533a215ca6918399d91493f6cf0fb88bb25e921a40eba5a79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeColor", value)

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7c3c68ad0bb7b91906dd84f507d66ab0e1cef148ad7c16e3a3b35352f250ca3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4221803d1cacf2b0bcdf5689502bd2ded1e0caf2200fc18faaeaba2b0d6cdbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFilterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76f408e7a95b67476ad115def276feb73d5a0c53f124209edea6dc0d1202ccbc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCropRectangle")
    def put_crop_rectangle(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        value = MediaTransformOutputCustomPresetFilterCropRectangle(
            height=height, left=left, top=top, width=width
        )

        return typing.cast(None, jsii.invoke(self, "putCropRectangle", [value]))

    @jsii.member(jsii_name="putDeinterlace")
    def put_deinterlace(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        parity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#mode MediaTransform#mode}.
        :param parity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#parity MediaTransform#parity}.
        '''
        value = MediaTransformOutputCustomPresetFilterDeinterlace(
            mode=mode, parity=parity
        )

        return typing.cast(None, jsii.invoke(self, "putDeinterlace", [value]))

    @jsii.member(jsii_name="putFadeIn")
    def put_fade_in(
        self,
        *,
        duration: builtins.str,
        fade_color: builtins.str,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.
        :param fade_color: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        value = MediaTransformOutputCustomPresetFilterFadeIn(
            duration=duration, fade_color=fade_color, start=start
        )

        return typing.cast(None, jsii.invoke(self, "putFadeIn", [value]))

    @jsii.member(jsii_name="putFadeOut")
    def put_fade_out(
        self,
        *,
        duration: builtins.str,
        fade_color: builtins.str,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#duration MediaTransform#duration}.
        :param fade_color: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_color MediaTransform#fade_color}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        value = MediaTransformOutputCustomPresetFilterFadeOut(
            duration=duration, fade_color=fade_color, start=start
        )

        return typing.cast(None, jsii.invoke(self, "putFadeOut", [value]))

    @jsii.member(jsii_name="putOverlay")
    def put_overlay(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFilterOverlay", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__558c028bc02fa18ffb82efba716da46419fa41c7162b3324f4539235a7046482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOverlay", [value]))

    @jsii.member(jsii_name="resetCropRectangle")
    def reset_crop_rectangle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCropRectangle", []))

    @jsii.member(jsii_name="resetDeinterlace")
    def reset_deinterlace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeinterlace", []))

    @jsii.member(jsii_name="resetFadeIn")
    def reset_fade_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeIn", []))

    @jsii.member(jsii_name="resetFadeOut")
    def reset_fade_out(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeOut", []))

    @jsii.member(jsii_name="resetOverlay")
    def reset_overlay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverlay", []))

    @jsii.member(jsii_name="resetRotation")
    def reset_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotation", []))

    @builtins.property
    @jsii.member(jsii_name="cropRectangle")
    def crop_rectangle(
        self,
    ) -> MediaTransformOutputCustomPresetFilterCropRectangleOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterCropRectangleOutputReference, jsii.get(self, "cropRectangle"))

    @builtins.property
    @jsii.member(jsii_name="deinterlace")
    def deinterlace(
        self,
    ) -> MediaTransformOutputCustomPresetFilterDeinterlaceOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterDeinterlaceOutputReference, jsii.get(self, "deinterlace"))

    @builtins.property
    @jsii.member(jsii_name="fadeIn")
    def fade_in(self) -> MediaTransformOutputCustomPresetFilterFadeInOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterFadeInOutputReference, jsii.get(self, "fadeIn"))

    @builtins.property
    @jsii.member(jsii_name="fadeOut")
    def fade_out(self) -> MediaTransformOutputCustomPresetFilterFadeOutOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterFadeOutOutputReference, jsii.get(self, "fadeOut"))

    @builtins.property
    @jsii.member(jsii_name="overlay")
    def overlay(self) -> "MediaTransformOutputCustomPresetFilterOverlayList":
        return typing.cast("MediaTransformOutputCustomPresetFilterOverlayList", jsii.get(self, "overlay"))

    @builtins.property
    @jsii.member(jsii_name="cropRectangleInput")
    def crop_rectangle_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle], jsii.get(self, "cropRectangleInput"))

    @builtins.property
    @jsii.member(jsii_name="deinterlaceInput")
    def deinterlace_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace], jsii.get(self, "deinterlaceInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeInInput")
    def fade_in_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn], jsii.get(self, "fadeInInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeOutInput")
    def fade_out_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut], jsii.get(self, "fadeOutInput"))

    @builtins.property
    @jsii.member(jsii_name="overlayInput")
    def overlay_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFilterOverlay"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFilterOverlay"]]], jsii.get(self, "overlayInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationInput")
    def rotation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationInput"))

    @builtins.property
    @jsii.member(jsii_name="rotation")
    def rotation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotation"))

    @rotation.setter
    def rotation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17f290558d727a1560fc9134c981fe89acf77381872596b6482ba78ae612f5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotation", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MediaTransformOutputCustomPresetFilter]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilter],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8afd4b810bebbbeaf153198761131fe0a684a4fa9abdbde25691c20867455ccb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlay",
    jsii_struct_bases=[],
    name_mapping={"audio": "audio", "video": "video"},
)
class MediaTransformOutputCustomPresetFilterOverlay:
    def __init__(
        self,
        *,
        audio: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayAudio", typing.Dict[builtins.str, typing.Any]]] = None,
        video: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayVideo", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param audio: audio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio MediaTransform#audio}
        :param video: video block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#video MediaTransform#video}
        '''
        if isinstance(audio, dict):
            audio = MediaTransformOutputCustomPresetFilterOverlayAudio(**audio)
        if isinstance(video, dict):
            video = MediaTransformOutputCustomPresetFilterOverlayVideo(**video)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__140872c6e8f044feafb84c85accf0515697622204dda500dded6f29001be8d5b)
            check_type(argname="argument audio", value=audio, expected_type=type_hints["audio"])
            check_type(argname="argument video", value=video, expected_type=type_hints["video"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if audio is not None:
            self._values["audio"] = audio
        if video is not None:
            self._values["video"] = video

    @builtins.property
    def audio(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayAudio"]:
        '''audio block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio MediaTransform#audio}
        '''
        result = self._values.get("audio")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayAudio"], result)

    @builtins.property
    def video(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideo"]:
        '''video block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#video MediaTransform#video}
        '''
        result = self._values.get("video")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterOverlay(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayAudio",
    jsii_struct_bases=[],
    name_mapping={
        "input_label": "inputLabel",
        "audio_gain_level": "audioGainLevel",
        "end": "end",
        "fade_in_duration": "fadeInDuration",
        "fade_out_duration": "fadeOutDuration",
        "start": "start",
    },
)
class MediaTransformOutputCustomPresetFilterOverlayAudio:
    def __init__(
        self,
        *,
        input_label: builtins.str,
        audio_gain_level: typing.Optional[jsii.Number] = None,
        end: typing.Optional[builtins.str] = None,
        fade_in_duration: typing.Optional[builtins.str] = None,
        fade_out_duration: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.
        :param audio_gain_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.
        :param fade_in_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.
        :param fade_out_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b131475ed54b22663f5a2fdd63e570984bfae626cc84db383c736d8e25680ad)
            check_type(argname="argument input_label", value=input_label, expected_type=type_hints["input_label"])
            check_type(argname="argument audio_gain_level", value=audio_gain_level, expected_type=type_hints["audio_gain_level"])
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument fade_in_duration", value=fade_in_duration, expected_type=type_hints["fade_in_duration"])
            check_type(argname="argument fade_out_duration", value=fade_out_duration, expected_type=type_hints["fade_out_duration"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "input_label": input_label,
        }
        if audio_gain_level is not None:
            self._values["audio_gain_level"] = audio_gain_level
        if end is not None:
            self._values["end"] = end
        if fade_in_duration is not None:
            self._values["fade_in_duration"] = fade_in_duration
        if fade_out_duration is not None:
            self._values["fade_out_duration"] = fade_out_duration
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def input_label(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.'''
        result = self._values.get("input_label")
        assert result is not None, "Required property 'input_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audio_gain_level(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.'''
        result = self._values.get("audio_gain_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fade_in_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.'''
        result = self._values.get("fade_in_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fade_out_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.'''
        result = self._values.get("fade_out_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterOverlayAudio(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterOverlayAudioOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayAudioOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34e59f5f5460b06e03a819fc35b4ebdac246fe9df25bd771e8edd3ac1ed19d51)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAudioGainLevel")
    def reset_audio_gain_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioGainLevel", []))

    @jsii.member(jsii_name="resetEnd")
    def reset_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnd", []))

    @jsii.member(jsii_name="resetFadeInDuration")
    def reset_fade_in_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeInDuration", []))

    @jsii.member(jsii_name="resetFadeOutDuration")
    def reset_fade_out_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeOutDuration", []))

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @builtins.property
    @jsii.member(jsii_name="audioGainLevelInput")
    def audio_gain_level_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "audioGainLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="endInput")
    def end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeInDurationInput")
    def fade_in_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeInDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeOutDurationInput")
    def fade_out_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeOutDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="inputLabelInput")
    def input_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startInput"))

    @builtins.property
    @jsii.member(jsii_name="audioGainLevel")
    def audio_gain_level(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "audioGainLevel"))

    @audio_gain_level.setter
    def audio_gain_level(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__143a36f500bde3e2d62ff4a40d351dc994eb4b78c1ca8ef9aa444cefc164e85a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioGainLevel", value)

    @builtins.property
    @jsii.member(jsii_name="end")
    def end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "end"))

    @end.setter
    def end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8365ce92c4242ce9e8583c00fe482eff44ee04c769e8d998d617fa3da4c1d1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value)

    @builtins.property
    @jsii.member(jsii_name="fadeInDuration")
    def fade_in_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeInDuration"))

    @fade_in_duration.setter
    def fade_in_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be1c4b2d52a5f701323366da78d2a1224d56e8a495fe8f3e8e2db0d2adad336)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeInDuration", value)

    @builtins.property
    @jsii.member(jsii_name="fadeOutDuration")
    def fade_out_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeOutDuration"))

    @fade_out_duration.setter
    def fade_out_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__627cbe58f4c646c740037c7cea94bc6708776b6ba79b92427456cdc1261ca185)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeOutDuration", value)

    @builtins.property
    @jsii.member(jsii_name="inputLabel")
    def input_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputLabel"))

    @input_label.setter
    def input_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__320c62ace214a4637f93788459d5c7cbd700ac7258132afb707e2e10a470dd63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputLabel", value)

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72d1f101a3674951581268c75af0694d547c79442dc8ff28b84817a3c3cd91e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d8425bab4588ede30879f0aca19e84c7653a06234b9063ecb2873510d4cd4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFilterOverlayList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14e2b51d5f24c7060fa35d4a2c359a44cf04fd0d70903943f7aacb34f89413d1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetFilterOverlayOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959380e59b48a3cf1bd2934c33ee63125f3b01234d997390f7e86d43d942452f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetFilterOverlayOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa3aed96efe2a6674b9277bfd9fb4f0079b3cce1c8d9911912175c390d6fa99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ea40247cabd67bc232d9dee204703db3d32cd75e18be3a2e348153d1cde20e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed7375157db7934042391a08d09d8e888c8c9c764578057790a47af927caaa56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFilterOverlay]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFilterOverlay]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFilterOverlay]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c211fc86e815fcb9302d3da59f27fc3789a495470d1b6dd8932e4b75f4dec13b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFilterOverlayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d46286b276ebd3e6bcff7a6b5af32866a27469400be507c88185f01bfcb5ab2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAudio")
    def put_audio(
        self,
        *,
        input_label: builtins.str,
        audio_gain_level: typing.Optional[jsii.Number] = None,
        end: typing.Optional[builtins.str] = None,
        fade_in_duration: typing.Optional[builtins.str] = None,
        fade_out_duration: typing.Optional[builtins.str] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.
        :param audio_gain_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.
        :param fade_in_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.
        :param fade_out_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        value = MediaTransformOutputCustomPresetFilterOverlayAudio(
            input_label=input_label,
            audio_gain_level=audio_gain_level,
            end=end,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            start=start,
        )

        return typing.cast(None, jsii.invoke(self, "putAudio", [value]))

    @jsii.member(jsii_name="putVideo")
    def put_video(
        self,
        *,
        input_label: builtins.str,
        audio_gain_level: typing.Optional[jsii.Number] = None,
        crop_rectangle: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle", typing.Dict[builtins.str, typing.Any]]] = None,
        end: typing.Optional[builtins.str] = None,
        fade_in_duration: typing.Optional[builtins.str] = None,
        fade_out_duration: typing.Optional[builtins.str] = None,
        opacity: typing.Optional[jsii.Number] = None,
        position: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayVideoPosition", typing.Dict[builtins.str, typing.Any]]] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.
        :param audio_gain_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.
        :param crop_rectangle: crop_rectangle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.
        :param fade_in_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.
        :param fade_out_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.
        :param opacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#opacity MediaTransform#opacity}.
        :param position: position block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#position MediaTransform#position}
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        value = MediaTransformOutputCustomPresetFilterOverlayVideo(
            input_label=input_label,
            audio_gain_level=audio_gain_level,
            crop_rectangle=crop_rectangle,
            end=end,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            opacity=opacity,
            position=position,
            start=start,
        )

        return typing.cast(None, jsii.invoke(self, "putVideo", [value]))

    @jsii.member(jsii_name="resetAudio")
    def reset_audio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudio", []))

    @jsii.member(jsii_name="resetVideo")
    def reset_video(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVideo", []))

    @builtins.property
    @jsii.member(jsii_name="audio")
    def audio(
        self,
    ) -> MediaTransformOutputCustomPresetFilterOverlayAudioOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterOverlayAudioOutputReference, jsii.get(self, "audio"))

    @builtins.property
    @jsii.member(jsii_name="video")
    def video(
        self,
    ) -> "MediaTransformOutputCustomPresetFilterOverlayVideoOutputReference":
        return typing.cast("MediaTransformOutputCustomPresetFilterOverlayVideoOutputReference", jsii.get(self, "video"))

    @builtins.property
    @jsii.member(jsii_name="audioInput")
    def audio_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio], jsii.get(self, "audioInput"))

    @builtins.property
    @jsii.member(jsii_name="videoInput")
    def video_input(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideo"]:
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideo"], jsii.get(self, "videoInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f2f23917e1f130cc66a21aa66e1d54b9764ceb0ac66da6da5c2e3f2650c8637)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideo",
    jsii_struct_bases=[],
    name_mapping={
        "input_label": "inputLabel",
        "audio_gain_level": "audioGainLevel",
        "crop_rectangle": "cropRectangle",
        "end": "end",
        "fade_in_duration": "fadeInDuration",
        "fade_out_duration": "fadeOutDuration",
        "opacity": "opacity",
        "position": "position",
        "start": "start",
    },
)
class MediaTransformOutputCustomPresetFilterOverlayVideo:
    def __init__(
        self,
        *,
        input_label: builtins.str,
        audio_gain_level: typing.Optional[jsii.Number] = None,
        crop_rectangle: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle", typing.Dict[builtins.str, typing.Any]]] = None,
        end: typing.Optional[builtins.str] = None,
        fade_in_duration: typing.Optional[builtins.str] = None,
        fade_out_duration: typing.Optional[builtins.str] = None,
        opacity: typing.Optional[jsii.Number] = None,
        position: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFilterOverlayVideoPosition", typing.Dict[builtins.str, typing.Any]]] = None,
        start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.
        :param audio_gain_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.
        :param crop_rectangle: crop_rectangle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        :param end: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.
        :param fade_in_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.
        :param fade_out_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.
        :param opacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#opacity MediaTransform#opacity}.
        :param position: position block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#position MediaTransform#position}
        :param start: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.
        '''
        if isinstance(crop_rectangle, dict):
            crop_rectangle = MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle(**crop_rectangle)
        if isinstance(position, dict):
            position = MediaTransformOutputCustomPresetFilterOverlayVideoPosition(**position)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef01cb74534ee9af87d3c66cca798e326ce901edf830659558ff3ac225d9e523)
            check_type(argname="argument input_label", value=input_label, expected_type=type_hints["input_label"])
            check_type(argname="argument audio_gain_level", value=audio_gain_level, expected_type=type_hints["audio_gain_level"])
            check_type(argname="argument crop_rectangle", value=crop_rectangle, expected_type=type_hints["crop_rectangle"])
            check_type(argname="argument end", value=end, expected_type=type_hints["end"])
            check_type(argname="argument fade_in_duration", value=fade_in_duration, expected_type=type_hints["fade_in_duration"])
            check_type(argname="argument fade_out_duration", value=fade_out_duration, expected_type=type_hints["fade_out_duration"])
            check_type(argname="argument opacity", value=opacity, expected_type=type_hints["opacity"])
            check_type(argname="argument position", value=position, expected_type=type_hints["position"])
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "input_label": input_label,
        }
        if audio_gain_level is not None:
            self._values["audio_gain_level"] = audio_gain_level
        if crop_rectangle is not None:
            self._values["crop_rectangle"] = crop_rectangle
        if end is not None:
            self._values["end"] = end
        if fade_in_duration is not None:
            self._values["fade_in_duration"] = fade_in_duration
        if fade_out_duration is not None:
            self._values["fade_out_duration"] = fade_out_duration
        if opacity is not None:
            self._values["opacity"] = opacity
        if position is not None:
            self._values["position"] = position
        if start is not None:
            self._values["start"] = start

    @builtins.property
    def input_label(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#input_label MediaTransform#input_label}.'''
        result = self._values.get("input_label")
        assert result is not None, "Required property 'input_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audio_gain_level(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_gain_level MediaTransform#audio_gain_level}.'''
        result = self._values.get("audio_gain_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def crop_rectangle(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle"]:
        '''crop_rectangle block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        '''
        result = self._values.get("crop_rectangle")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle"], result)

    @builtins.property
    def end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#end MediaTransform#end}.'''
        result = self._values.get("end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fade_in_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in_duration MediaTransform#fade_in_duration}.'''
        result = self._values.get("fade_in_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fade_out_duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out_duration MediaTransform#fade_out_duration}.'''
        result = self._values.get("fade_out_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#opacity MediaTransform#opacity}.'''
        result = self._values.get("opacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def position(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoPosition"]:
        '''position block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#position MediaTransform#position}
        '''
        result = self._values.get("position")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoPosition"], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#start MediaTransform#start}.'''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterOverlayVideo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle",
    jsii_struct_bases=[],
    name_mapping={"height": "height", "left": "left", "top": "top", "width": "width"},
)
class MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle:
    def __init__(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c9881344a669bf7003845fd19f14c16a4dded2ef821d0652cf20acdfc70253)
            check_type(argname="argument height", value=height, expected_type=type_hints["height"])
            check_type(argname="argument left", value=left, expected_type=type_hints["left"])
            check_type(argname="argument top", value=top, expected_type=type_hints["top"])
            check_type(argname="argument width", value=width, expected_type=type_hints["width"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if height is not None:
            self._values["height"] = height
        if left is not None:
            self._values["left"] = left
        if top is not None:
            self._values["top"] = top
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def height(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def left(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.'''
        result = self._values.get("left")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def top(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.'''
        result = self._values.get("top")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def width(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__402d903337cd5c45b8e25cca6deaabe4366c9bf456b210f0945262cebec4798f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHeight")
    def reset_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeight", []))

    @jsii.member(jsii_name="resetLeft")
    def reset_left(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLeft", []))

    @jsii.member(jsii_name="resetTop")
    def reset_top(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTop", []))

    @jsii.member(jsii_name="resetWidth")
    def reset_width(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidth", []))

    @builtins.property
    @jsii.member(jsii_name="heightInput")
    def height_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "heightInput"))

    @builtins.property
    @jsii.member(jsii_name="leftInput")
    def left_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "leftInput"))

    @builtins.property
    @jsii.member(jsii_name="topInput")
    def top_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topInput"))

    @builtins.property
    @jsii.member(jsii_name="widthInput")
    def width_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widthInput"))

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "height"))

    @height.setter
    def height(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b9f659ea86511c4684143dea32ab46de578a730c959dad78d47dc8504b6373e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "height", value)

    @builtins.property
    @jsii.member(jsii_name="left")
    def left(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "left"))

    @left.setter
    def left(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f528fbb6be9a700592a6370b2e8f3ef3cd4bcc2b5c7ae625bcadc1357148717)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "left", value)

    @builtins.property
    @jsii.member(jsii_name="top")
    def top(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "top"))

    @top.setter
    def top(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edcfdad836e093e49b74c60aad82a1f8076743eb9ecda145c9a6a528472f8dd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "top", value)

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "width"))

    @width.setter
    def width(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf19ca327f844d96aacfa4cb00bc2920eecce2e6e67ba4313099b52282047f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "width", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1337c73f336a37380bf477907a7278ca56697296ca10ce37204ec66201075f1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFilterOverlayVideoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c29e733a301b14632884054afa2b0dd7c9bf0e3fea188a6d8c5103727caf5c7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCropRectangle")
    def put_crop_rectangle(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        value = MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle(
            height=height, left=left, top=top, width=width
        )

        return typing.cast(None, jsii.invoke(self, "putCropRectangle", [value]))

    @jsii.member(jsii_name="putPosition")
    def put_position(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        value = MediaTransformOutputCustomPresetFilterOverlayVideoPosition(
            height=height, left=left, top=top, width=width
        )

        return typing.cast(None, jsii.invoke(self, "putPosition", [value]))

    @jsii.member(jsii_name="resetAudioGainLevel")
    def reset_audio_gain_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioGainLevel", []))

    @jsii.member(jsii_name="resetCropRectangle")
    def reset_crop_rectangle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCropRectangle", []))

    @jsii.member(jsii_name="resetEnd")
    def reset_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnd", []))

    @jsii.member(jsii_name="resetFadeInDuration")
    def reset_fade_in_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeInDuration", []))

    @jsii.member(jsii_name="resetFadeOutDuration")
    def reset_fade_out_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFadeOutDuration", []))

    @jsii.member(jsii_name="resetOpacity")
    def reset_opacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpacity", []))

    @jsii.member(jsii_name="resetPosition")
    def reset_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosition", []))

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @builtins.property
    @jsii.member(jsii_name="cropRectangle")
    def crop_rectangle(
        self,
    ) -> MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangleOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangleOutputReference, jsii.get(self, "cropRectangle"))

    @builtins.property
    @jsii.member(jsii_name="position")
    def position(
        self,
    ) -> "MediaTransformOutputCustomPresetFilterOverlayVideoPositionOutputReference":
        return typing.cast("MediaTransformOutputCustomPresetFilterOverlayVideoPositionOutputReference", jsii.get(self, "position"))

    @builtins.property
    @jsii.member(jsii_name="audioGainLevelInput")
    def audio_gain_level_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "audioGainLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="cropRectangleInput")
    def crop_rectangle_input(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle], jsii.get(self, "cropRectangleInput"))

    @builtins.property
    @jsii.member(jsii_name="endInput")
    def end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeInDurationInput")
    def fade_in_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeInDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="fadeOutDurationInput")
    def fade_out_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fadeOutDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="inputLabelInput")
    def input_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="opacityInput")
    def opacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "opacityInput"))

    @builtins.property
    @jsii.member(jsii_name="positionInput")
    def position_input(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoPosition"]:
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFilterOverlayVideoPosition"], jsii.get(self, "positionInput"))

    @builtins.property
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startInput"))

    @builtins.property
    @jsii.member(jsii_name="audioGainLevel")
    def audio_gain_level(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "audioGainLevel"))

    @audio_gain_level.setter
    def audio_gain_level(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__934a1b51a49c192fa747242deada04fd1b2d836c2d37a5dddefeb630a346e54f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioGainLevel", value)

    @builtins.property
    @jsii.member(jsii_name="end")
    def end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "end"))

    @end.setter
    def end(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48bf1305bb2d4d04e2a6498de1ab13d3b9b4b3ce4c9e786eccf16012d9904832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "end", value)

    @builtins.property
    @jsii.member(jsii_name="fadeInDuration")
    def fade_in_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeInDuration"))

    @fade_in_duration.setter
    def fade_in_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34eb945cdfc545ae61bf59bddb933ff2b66b78745e79f135e92b1456b993db07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeInDuration", value)

    @builtins.property
    @jsii.member(jsii_name="fadeOutDuration")
    def fade_out_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fadeOutDuration"))

    @fade_out_duration.setter
    def fade_out_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b20968aa158f8615e37ab4ac68abe1592f823d18be163f5873ddcb258054cb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fadeOutDuration", value)

    @builtins.property
    @jsii.member(jsii_name="inputLabel")
    def input_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputLabel"))

    @input_label.setter
    def input_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a4900f9dc5baf160e2340b02245cc543477ce115101276392cb0bcc18770002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputLabel", value)

    @builtins.property
    @jsii.member(jsii_name="opacity")
    def opacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "opacity"))

    @opacity.setter
    def opacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fec1a784c315e6bc3ecc22c68db2526b5f8cacce9268657fb1fb7f3036e5e89d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opacity", value)

    @builtins.property
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae087a8541291e098a7a3717f6925c0aaaf435979d756e33aa8f634a59bab599)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "start", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideo]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6857390da838ed241702ff7c3958675ac7a4c5652c26ffa530bcac5e9f07f20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideoPosition",
    jsii_struct_bases=[],
    name_mapping={"height": "height", "left": "left", "top": "top", "width": "width"},
)
class MediaTransformOutputCustomPresetFilterOverlayVideoPosition:
    def __init__(
        self,
        *,
        height: typing.Optional[builtins.str] = None,
        left: typing.Optional[builtins.str] = None,
        top: typing.Optional[builtins.str] = None,
        width: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param height: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.
        :param left: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.
        :param top: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.
        :param width: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d622acfc3cb210659435f6d99e0561ed7452a528e9df2d13a5bd601996512b15)
            check_type(argname="argument height", value=height, expected_type=type_hints["height"])
            check_type(argname="argument left", value=left, expected_type=type_hints["left"])
            check_type(argname="argument top", value=top, expected_type=type_hints["top"])
            check_type(argname="argument width", value=width, expected_type=type_hints["width"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if height is not None:
            self._values["height"] = height
        if left is not None:
            self._values["left"] = left
        if top is not None:
            self._values["top"] = top
        if width is not None:
            self._values["width"] = width

    @builtins.property
    def height(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#height MediaTransform#height}.'''
        result = self._values.get("height")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def left(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#left MediaTransform#left}.'''
        result = self._values.get("left")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def top(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#top MediaTransform#top}.'''
        result = self._values.get("top")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def width(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#width MediaTransform#width}.'''
        result = self._values.get("width")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFilterOverlayVideoPosition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFilterOverlayVideoPositionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFilterOverlayVideoPositionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5b255d0279e2104d75d403e50ec8f08aab94fb4696a1d0c5d38da8f92f20fae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHeight")
    def reset_height(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeight", []))

    @jsii.member(jsii_name="resetLeft")
    def reset_left(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLeft", []))

    @jsii.member(jsii_name="resetTop")
    def reset_top(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTop", []))

    @jsii.member(jsii_name="resetWidth")
    def reset_width(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWidth", []))

    @builtins.property
    @jsii.member(jsii_name="heightInput")
    def height_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "heightInput"))

    @builtins.property
    @jsii.member(jsii_name="leftInput")
    def left_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "leftInput"))

    @builtins.property
    @jsii.member(jsii_name="topInput")
    def top_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topInput"))

    @builtins.property
    @jsii.member(jsii_name="widthInput")
    def width_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "widthInput"))

    @builtins.property
    @jsii.member(jsii_name="height")
    def height(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "height"))

    @height.setter
    def height(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2450c10de8e55ff43f89aeaa43433d8eca76a9e4893412bbd699d64bbde7ead5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "height", value)

    @builtins.property
    @jsii.member(jsii_name="left")
    def left(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "left"))

    @left.setter
    def left(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14f6a133125e0d81fca5033b483f783fafd16d7ccd46556e1fa46af7443dd01c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "left", value)

    @builtins.property
    @jsii.member(jsii_name="top")
    def top(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "top"))

    @top.setter
    def top(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4621685850855688c83840d34e098ec1432000b4aefd0cf27ddf8ba0993cc8bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "top", value)

    @builtins.property
    @jsii.member(jsii_name="width")
    def width(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "width"))

    @width.setter
    def width(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a91c61397cbb23234552ccaa925fe72d43be626a733b4c3f97ad96cf8b0f84c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "width", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoPosition]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoPosition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoPosition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3cca5b2d7db89a7f15aeba638fec58219fd4e7d4e8896c9623ff5e24b948876)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormat",
    jsii_struct_bases=[],
    name_mapping={"mp4": "mp4", "transport_stream": "transportStream"},
)
class MediaTransformOutputCustomPresetFormat:
    def __init__(
        self,
        *,
        mp4: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFormatMp4", typing.Dict[builtins.str, typing.Any]]] = None,
        transport_stream: typing.Optional[typing.Union["MediaTransformOutputCustomPresetFormatTransportStream", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param mp4: mp4 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#mp4 MediaTransform#mp4}
        :param transport_stream: transport_stream block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#transport_stream MediaTransform#transport_stream}
        '''
        if isinstance(mp4, dict):
            mp4 = MediaTransformOutputCustomPresetFormatMp4(**mp4)
        if isinstance(transport_stream, dict):
            transport_stream = MediaTransformOutputCustomPresetFormatTransportStream(**transport_stream)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97ffb02af523ce8c0138729722ae2cb28a4f8b4f61ba57904be6fa86db11e58c)
            check_type(argname="argument mp4", value=mp4, expected_type=type_hints["mp4"])
            check_type(argname="argument transport_stream", value=transport_stream, expected_type=type_hints["transport_stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mp4 is not None:
            self._values["mp4"] = mp4
        if transport_stream is not None:
            self._values["transport_stream"] = transport_stream

    @builtins.property
    def mp4(self) -> typing.Optional["MediaTransformOutputCustomPresetFormatMp4"]:
        '''mp4 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#mp4 MediaTransform#mp4}
        '''
        result = self._values.get("mp4")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFormatMp4"], result)

    @builtins.property
    def transport_stream(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFormatTransportStream"]:
        '''transport_stream block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#transport_stream MediaTransform#transport_stream}
        '''
        result = self._values.get("transport_stream")
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFormatTransportStream"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFormat(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFormatList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3de0d8e09d57ff4eb04c601242a588af76388e30ad3edb79e0fcff3d887dff15)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetFormatOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aad0510bb6e6e3be1234e3541cfaa7fc809284c1b95f9ce2472e6681436c093f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetFormatOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9275677a46c3fd82d4a0d19446162b7873f66d34473a26f9c3965f7a26972adb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__075ee6b2acafc736f85f94ec59164c1568a3f59f33b1b7abc0ca9f02c0cd4cca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b241b2cd94105dc1f58777a31dc537fbbfdb6de4a375558011cb62845155630f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__129bd33e1c80be2a6bb38b7465cd76cb6f18a6ff2aa53bf24bc7e12cea61e9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatMp4",
    jsii_struct_bases=[],
    name_mapping={"filename_pattern": "filenamePattern", "output_file": "outputFile"},
)
class MediaTransformOutputCustomPresetFormatMp4:
    def __init__(
        self,
        *,
        filename_pattern: builtins.str,
        output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFormatMp4OutputFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param filename_pattern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.
        :param output_file: output_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a2937961d9f9a169ddab9b98b8bcdadb9dd5e3b11206b1075ec4d1091856c74)
            check_type(argname="argument filename_pattern", value=filename_pattern, expected_type=type_hints["filename_pattern"])
            check_type(argname="argument output_file", value=output_file, expected_type=type_hints["output_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "filename_pattern": filename_pattern,
        }
        if output_file is not None:
            self._values["output_file"] = output_file

    @builtins.property
    def filename_pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.'''
        result = self._values.get("filename_pattern")
        assert result is not None, "Required property 'filename_pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormatMp4OutputFile"]]]:
        '''output_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        result = self._values.get("output_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormatMp4OutputFile"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFormatMp4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatMp4OutputFile",
    jsii_struct_bases=[],
    name_mapping={"labels": "labels"},
)
class MediaTransformOutputCustomPresetFormatMp4OutputFile:
    def __init__(self, *, labels: typing.Sequence[builtins.str]) -> None:
        '''
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#labels MediaTransform#labels}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f1096a4daa33a5ba0cdd28f20b999986dcdc7fe7ecda12b63734fa0cd09f24)
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "labels": labels,
        }

    @builtins.property
    def labels(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#labels MediaTransform#labels}.'''
        result = self._values.get("labels")
        assert result is not None, "Required property 'labels' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFormatMp4OutputFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFormatMp4OutputFileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatMp4OutputFileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76f0f1016b18fab453aee7c2861d5ff177f6a7bde444f9190a28dc7c6e2bc320)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetFormatMp4OutputFileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12611f8ccc0c0faa7923e108426938bd801962f49eb706aabf56d6c5ad66a7cd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetFormatMp4OutputFileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48239786427e5a456fee4c0a4eed9b5a611130fe848211d04958b8ac645813fa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd52c7910ca5e15fdac0f8c80eb9511f74133fac5e9e7727c9a36b007993beab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__385789b3d88e1b4b0acd7519e272af4e0fa95f36156e1c33a4cbccba0fd0d5d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f83bc957291092639da29f363b8e2c69b43f2b41f15337a54a343265ba69e3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFormatMp4OutputFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatMp4OutputFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb9f535cfe08a7a49f3eef31aacd43df0ae1c1e498818a8d0710567c00a09663)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21946f4fe82ed8826ee92441607a6cf43d92adfe24771029ad970ac61ad093b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdd6ea0086f759643896fcb959070102ca1a55ac4ae2c645b0759e6ced8ea2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFormatMp4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatMp4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e58fc337ec9a7d62e730fc3c0d148949f9c6a7463d7671ae13934e9e95a6795)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOutputFile")
    def put_output_file(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c00358e4fb3d1048b69f55814034f6f45e893082002f16a40fa709e58f054047)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOutputFile", [value]))

    @jsii.member(jsii_name="resetOutputFile")
    def reset_output_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFile", []))

    @builtins.property
    @jsii.member(jsii_name="outputFile")
    def output_file(self) -> MediaTransformOutputCustomPresetFormatMp4OutputFileList:
        return typing.cast(MediaTransformOutputCustomPresetFormatMp4OutputFileList, jsii.get(self, "outputFile"))

    @builtins.property
    @jsii.member(jsii_name="filenamePatternInput")
    def filename_pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenamePatternInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFileInput")
    def output_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]], jsii.get(self, "outputFileInput"))

    @builtins.property
    @jsii.member(jsii_name="filenamePattern")
    def filename_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filenamePattern"))

    @filename_pattern.setter
    def filename_pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a13c6e423cefb97a507712390d6c329f88cde6ac83ff531eca50bf97037e267)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filenamePattern", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFormatMp4]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFormatMp4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFormatMp4],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__229d718d8c7f107f21ec1d398ec2f7406f6a8b97b84d51e244e6941afabfb36e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFormatOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2beff49deee80986ebc6d34a65b818cec2e73ec621266fbb4ec2730ed97592de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putMp4")
    def put_mp4(
        self,
        *,
        filename_pattern: builtins.str,
        output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param filename_pattern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.
        :param output_file: output_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        value = MediaTransformOutputCustomPresetFormatMp4(
            filename_pattern=filename_pattern, output_file=output_file
        )

        return typing.cast(None, jsii.invoke(self, "putMp4", [value]))

    @jsii.member(jsii_name="putTransportStream")
    def put_transport_stream(
        self,
        *,
        filename_pattern: builtins.str,
        output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFormatTransportStreamOutputFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param filename_pattern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.
        :param output_file: output_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        value = MediaTransformOutputCustomPresetFormatTransportStream(
            filename_pattern=filename_pattern, output_file=output_file
        )

        return typing.cast(None, jsii.invoke(self, "putTransportStream", [value]))

    @jsii.member(jsii_name="resetMp4")
    def reset_mp4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMp4", []))

    @jsii.member(jsii_name="resetTransportStream")
    def reset_transport_stream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransportStream", []))

    @builtins.property
    @jsii.member(jsii_name="mp4")
    def mp4(self) -> MediaTransformOutputCustomPresetFormatMp4OutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFormatMp4OutputReference, jsii.get(self, "mp4"))

    @builtins.property
    @jsii.member(jsii_name="transportStream")
    def transport_stream(
        self,
    ) -> "MediaTransformOutputCustomPresetFormatTransportStreamOutputReference":
        return typing.cast("MediaTransformOutputCustomPresetFormatTransportStreamOutputReference", jsii.get(self, "transportStream"))

    @builtins.property
    @jsii.member(jsii_name="mp4Input")
    def mp4_input(self) -> typing.Optional[MediaTransformOutputCustomPresetFormatMp4]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFormatMp4], jsii.get(self, "mp4Input"))

    @builtins.property
    @jsii.member(jsii_name="transportStreamInput")
    def transport_stream_input(
        self,
    ) -> typing.Optional["MediaTransformOutputCustomPresetFormatTransportStream"]:
        return typing.cast(typing.Optional["MediaTransformOutputCustomPresetFormatTransportStream"], jsii.get(self, "transportStreamInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormat, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormat, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormat, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5650e1899847f2eacbcd497862a955c8a2a94b511e343d17392eb24a60a62b83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatTransportStream",
    jsii_struct_bases=[],
    name_mapping={"filename_pattern": "filenamePattern", "output_file": "outputFile"},
)
class MediaTransformOutputCustomPresetFormatTransportStream:
    def __init__(
        self,
        *,
        filename_pattern: builtins.str,
        output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MediaTransformOutputCustomPresetFormatTransportStreamOutputFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param filename_pattern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.
        :param output_file: output_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a052edb64cbeca87f085f92bd5df89309a79cd4ffd863c9cd28dc2af29fbbe7)
            check_type(argname="argument filename_pattern", value=filename_pattern, expected_type=type_hints["filename_pattern"])
            check_type(argname="argument output_file", value=output_file, expected_type=type_hints["output_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "filename_pattern": filename_pattern,
        }
        if output_file is not None:
            self._values["output_file"] = output_file

    @builtins.property
    def filename_pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filename_pattern MediaTransform#filename_pattern}.'''
        result = self._values.get("filename_pattern")
        assert result is not None, "Required property 'filename_pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormatTransportStreamOutputFile"]]]:
        '''output_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#output_file MediaTransform#output_file}
        '''
        result = self._values.get("output_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MediaTransformOutputCustomPresetFormatTransportStreamOutputFile"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFormatTransportStream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatTransportStreamOutputFile",
    jsii_struct_bases=[],
    name_mapping={"labels": "labels"},
)
class MediaTransformOutputCustomPresetFormatTransportStreamOutputFile:
    def __init__(self, *, labels: typing.Sequence[builtins.str]) -> None:
        '''
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#labels MediaTransform#labels}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27a127ad614a33de138c24158e6f69a960ffffb2608b964e6ea7caaa4accdf02)
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "labels": labels,
        }

    @builtins.property
    def labels(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#labels MediaTransform#labels}.'''
        result = self._values.get("labels")
        assert result is not None, "Required property 'labels' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputCustomPresetFormatTransportStreamOutputFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputCustomPresetFormatTransportStreamOutputFileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatTransportStreamOutputFileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a7d3502e777541bca0d11307c1cf516fd1e4fbd103ca8cedc10aaedc327201a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MediaTransformOutputCustomPresetFormatTransportStreamOutputFileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76144842485da9cdc09083ca5f027fd680183295b8cbafe00410f141e97097d3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputCustomPresetFormatTransportStreamOutputFileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c423a08d1146895a5f404d78cfd8e8666b017ae9ed9f07cfcfd9f16b5a81ff)
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
            type_hints = typing.get_type_hints(_typecheckingstub__346ce926721e92bd99fabd944935a5d83c1e3c64d7753c02fe91471aa932c10c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bcf1a666d9b854056027aad6083a408fefa979130a99434c8b68733f95e1407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eba6bf20e623278805720b1c925fbf561cad1567b6f7697feef9e56427b61a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFormatTransportStreamOutputFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatTransportStreamOutputFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9139ebf1f5a6f9970b0dbdcd62ec549f072756807a8509d9e37c8b0481ac0f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8799cebcc12017200888112323fe48c1d2c5088c1ac0dfbc4a99a1f48391274a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__329e2f8f5a1bca6477b1e74a0ef26853922d455f9adba8b21f783e4570472603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetFormatTransportStreamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetFormatTransportStreamOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__987bfe3ed4539122247fad4fb1cfea5268be1d177ffe21bed1bf2013a5c4cc39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOutputFile")
    def put_output_file(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0409d13fbbe2cc391336c2012fdb7524a13d622b3300f3566452f94c419b58b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOutputFile", [value]))

    @jsii.member(jsii_name="resetOutputFile")
    def reset_output_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFile", []))

    @builtins.property
    @jsii.member(jsii_name="outputFile")
    def output_file(
        self,
    ) -> MediaTransformOutputCustomPresetFormatTransportStreamOutputFileList:
        return typing.cast(MediaTransformOutputCustomPresetFormatTransportStreamOutputFileList, jsii.get(self, "outputFile"))

    @builtins.property
    @jsii.member(jsii_name="filenamePatternInput")
    def filename_pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenamePatternInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFileInput")
    def output_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]], jsii.get(self, "outputFileInput"))

    @builtins.property
    @jsii.member(jsii_name="filenamePattern")
    def filename_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filenamePattern"))

    @filename_pattern.setter
    def filename_pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f28dc19ea5242b38920ea0495b58a19b5867204a7dadefb3524868de18c650d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filenamePattern", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputCustomPresetFormatTransportStream]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFormatTransportStream], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPresetFormatTransportStream],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e318bfe7fc1db7fa1c993953fe52efddbaab0899114992a73b7fb016671070e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputCustomPresetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputCustomPresetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ea9252f6dc724f481dc3f7c60983db8b3ed8f98dc4235190ed0a02923f6f77c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCodec")
    def put_codec(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodec, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f47f1a5dde3e3374a2181cff1d833b30a2347a876f047e250519fc5f8d8e832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCodec", [value]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        crop_rectangle: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterCropRectangle, typing.Dict[builtins.str, typing.Any]]] = None,
        deinterlace: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterDeinterlace, typing.Dict[builtins.str, typing.Any]]] = None,
        fade_in: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterFadeIn, typing.Dict[builtins.str, typing.Any]]] = None,
        fade_out: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterFadeOut, typing.Dict[builtins.str, typing.Any]]] = None,
        overlay: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, typing.Dict[builtins.str, typing.Any]]]]] = None,
        rotation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param crop_rectangle: crop_rectangle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#crop_rectangle MediaTransform#crop_rectangle}
        :param deinterlace: deinterlace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#deinterlace MediaTransform#deinterlace}
        :param fade_in: fade_in block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_in MediaTransform#fade_in}
        :param fade_out: fade_out block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#fade_out MediaTransform#fade_out}
        :param overlay: overlay block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#overlay MediaTransform#overlay}
        :param rotation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#rotation MediaTransform#rotation}.
        '''
        value = MediaTransformOutputCustomPresetFilter(
            crop_rectangle=crop_rectangle,
            deinterlace=deinterlace,
            fade_in=fade_in,
            fade_out=fade_out,
            overlay=overlay,
            rotation=rotation,
        )

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="putFormat")
    def put_format(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormat, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c023d59674971f317b69e2961cb58b31a01ccd44d63e7a42601020b2fb7c97f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFormat", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @builtins.property
    @jsii.member(jsii_name="codec")
    def codec(self) -> MediaTransformOutputCustomPresetCodecList:
        return typing.cast(MediaTransformOutputCustomPresetCodecList, jsii.get(self, "codec"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> MediaTransformOutputCustomPresetFilterOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetFilterOutputReference, jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> MediaTransformOutputCustomPresetFormatList:
        return typing.cast(MediaTransformOutputCustomPresetFormatList, jsii.get(self, "format"))

    @builtins.property
    @jsii.member(jsii_name="codecInput")
    def codec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]], jsii.get(self, "codecInput"))

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional[MediaTransformOutputCustomPresetFilter]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPresetFilter], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MediaTransformOutputCustomPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPreset], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputCustomPreset],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9de60dc00c0785c04d223c7822367773bfed264e64755716d258a2f16040795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputFaceDetectorPreset",
    jsii_struct_bases=[],
    name_mapping={
        "analysis_resolution": "analysisResolution",
        "blur_type": "blurType",
        "experimental_options": "experimentalOptions",
        "face_redactor_mode": "faceRedactorMode",
    },
)
class MediaTransformOutputFaceDetectorPreset:
    def __init__(
        self,
        *,
        analysis_resolution: typing.Optional[builtins.str] = None,
        blur_type: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        face_redactor_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param analysis_resolution: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#analysis_resolution MediaTransform#analysis_resolution}.
        :param blur_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#blur_type MediaTransform#blur_type}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        :param face_redactor_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#face_redactor_mode MediaTransform#face_redactor_mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c59bd284086270465237bf3fd3a92dcc4058494fffeee893f3de6bade87935c)
            check_type(argname="argument analysis_resolution", value=analysis_resolution, expected_type=type_hints["analysis_resolution"])
            check_type(argname="argument blur_type", value=blur_type, expected_type=type_hints["blur_type"])
            check_type(argname="argument experimental_options", value=experimental_options, expected_type=type_hints["experimental_options"])
            check_type(argname="argument face_redactor_mode", value=face_redactor_mode, expected_type=type_hints["face_redactor_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analysis_resolution is not None:
            self._values["analysis_resolution"] = analysis_resolution
        if blur_type is not None:
            self._values["blur_type"] = blur_type
        if experimental_options is not None:
            self._values["experimental_options"] = experimental_options
        if face_redactor_mode is not None:
            self._values["face_redactor_mode"] = face_redactor_mode

    @builtins.property
    def analysis_resolution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#analysis_resolution MediaTransform#analysis_resolution}.'''
        result = self._values.get("analysis_resolution")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def blur_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#blur_type MediaTransform#blur_type}.'''
        result = self._values.get("blur_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def experimental_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.'''
        result = self._values.get("experimental_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def face_redactor_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#face_redactor_mode MediaTransform#face_redactor_mode}.'''
        result = self._values.get("face_redactor_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputFaceDetectorPreset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputFaceDetectorPresetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputFaceDetectorPresetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a0c631f840d38c32d0e610f614c22be53a7272a95389d831392f2fa43ddffd8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAnalysisResolution")
    def reset_analysis_resolution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalysisResolution", []))

    @jsii.member(jsii_name="resetBlurType")
    def reset_blur_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlurType", []))

    @jsii.member(jsii_name="resetExperimentalOptions")
    def reset_experimental_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExperimentalOptions", []))

    @jsii.member(jsii_name="resetFaceRedactorMode")
    def reset_face_redactor_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaceRedactorMode", []))

    @builtins.property
    @jsii.member(jsii_name="analysisResolutionInput")
    def analysis_resolution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "analysisResolutionInput"))

    @builtins.property
    @jsii.member(jsii_name="blurTypeInput")
    def blur_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blurTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="experimentalOptionsInput")
    def experimental_options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "experimentalOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="faceRedactorModeInput")
    def face_redactor_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "faceRedactorModeInput"))

    @builtins.property
    @jsii.member(jsii_name="analysisResolution")
    def analysis_resolution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "analysisResolution"))

    @analysis_resolution.setter
    def analysis_resolution(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1db3e523de183b9f9fa92fb1205b76ea7168ed14ed188ef3c002688eedb783)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "analysisResolution", value)

    @builtins.property
    @jsii.member(jsii_name="blurType")
    def blur_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blurType"))

    @blur_type.setter
    def blur_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af42b2c854256bd4f3ad287686f6f5537c5fa3f51aa0d56cb9712bdfba33bea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blurType", value)

    @builtins.property
    @jsii.member(jsii_name="experimentalOptions")
    def experimental_options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "experimentalOptions"))

    @experimental_options.setter
    def experimental_options(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b03ebc16204986c569345615284c0d15661bde1192bc988c97a85054459fce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "experimentalOptions", value)

    @builtins.property
    @jsii.member(jsii_name="faceRedactorMode")
    def face_redactor_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faceRedactorMode"))

    @face_redactor_mode.setter
    def face_redactor_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c84ebf43a262740e70c182ab090933454005b232e9aadfe790e8a837e62e4eaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faceRedactorMode", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MediaTransformOutputFaceDetectorPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputFaceDetectorPreset], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputFaceDetectorPreset],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cb4155e3f3339515d1ccf85655135e9c64762332528a9ef97fa82ac3371abdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9317d382df1ad8258ff57d6871121b80fb035c98bd4801c9b19a27204f83a2e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MediaTransformOutputOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1441d9de76bfa2c71300f6f681987187350e3cc8a8964886d7b039986a6ca5e9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MediaTransformOutputOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26285451211fb4312004f4c366e60eba513d2cac63e7f94d5d0848a78066b300)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1e0a546320d11a4b1e336ba244ce3ef08c04d643dfca8dc2c9a0f525c1ca0a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9495279790ab8749bc4f493ea18cb893f7cfb80f5fa56125c3d18f7e394f5842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutput]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutput]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutput]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238c880f727f4e248192e062f420d9b65f16c8eeecee50297408cde591f7bf1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class MediaTransformOutputOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91bd6a33c37bb09f019110b2d711d588d130f4ff4aa13d9ae44bb8f7fa19af48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAudioAnalyzerPreset")
    def put_audio_analyzer_preset(
        self,
        *,
        audio_analysis_mode: typing.Optional[builtins.str] = None,
        audio_language: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param audio_analysis_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.
        :param audio_language: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        '''
        value = MediaTransformOutputAudioAnalyzerPreset(
            audio_analysis_mode=audio_analysis_mode,
            audio_language=audio_language,
            experimental_options=experimental_options,
        )

        return typing.cast(None, jsii.invoke(self, "putAudioAnalyzerPreset", [value]))

    @jsii.member(jsii_name="putBuiltinPreset")
    def put_builtin_preset(
        self,
        *,
        preset_name: builtins.str,
        preset_configuration: typing.Optional[typing.Union[MediaTransformOutputBuiltinPresetPresetConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_name MediaTransform#preset_name}.
        :param preset_configuration: preset_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#preset_configuration MediaTransform#preset_configuration}
        '''
        value = MediaTransformOutputBuiltinPreset(
            preset_name=preset_name, preset_configuration=preset_configuration
        )

        return typing.cast(None, jsii.invoke(self, "putBuiltinPreset", [value]))

    @jsii.member(jsii_name="putCustomPreset")
    def put_custom_preset(
        self,
        *,
        codec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodec, typing.Dict[builtins.str, typing.Any]]]],
        format: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormat, typing.Dict[builtins.str, typing.Any]]]],
        filter: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param codec: codec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#codec MediaTransform#codec}
        :param format: format block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#format MediaTransform#format}
        :param filter: filter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#filter MediaTransform#filter}
        '''
        value = MediaTransformOutputCustomPreset(
            codec=codec, format=format, filter=filter
        )

        return typing.cast(None, jsii.invoke(self, "putCustomPreset", [value]))

    @jsii.member(jsii_name="putFaceDetectorPreset")
    def put_face_detector_preset(
        self,
        *,
        analysis_resolution: typing.Optional[builtins.str] = None,
        blur_type: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        face_redactor_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param analysis_resolution: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#analysis_resolution MediaTransform#analysis_resolution}.
        :param blur_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#blur_type MediaTransform#blur_type}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        :param face_redactor_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#face_redactor_mode MediaTransform#face_redactor_mode}.
        '''
        value = MediaTransformOutputFaceDetectorPreset(
            analysis_resolution=analysis_resolution,
            blur_type=blur_type,
            experimental_options=experimental_options,
            face_redactor_mode=face_redactor_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putFaceDetectorPreset", [value]))

    @jsii.member(jsii_name="putVideoAnalyzerPreset")
    def put_video_analyzer_preset(
        self,
        *,
        audio_analysis_mode: typing.Optional[builtins.str] = None,
        audio_language: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        insights_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param audio_analysis_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.
        :param audio_language: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        :param insights_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#insights_type MediaTransform#insights_type}.
        '''
        value = MediaTransformOutputVideoAnalyzerPreset(
            audio_analysis_mode=audio_analysis_mode,
            audio_language=audio_language,
            experimental_options=experimental_options,
            insights_type=insights_type,
        )

        return typing.cast(None, jsii.invoke(self, "putVideoAnalyzerPreset", [value]))

    @jsii.member(jsii_name="resetAudioAnalyzerPreset")
    def reset_audio_analyzer_preset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioAnalyzerPreset", []))

    @jsii.member(jsii_name="resetBuiltinPreset")
    def reset_builtin_preset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuiltinPreset", []))

    @jsii.member(jsii_name="resetCustomPreset")
    def reset_custom_preset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPreset", []))

    @jsii.member(jsii_name="resetFaceDetectorPreset")
    def reset_face_detector_preset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaceDetectorPreset", []))

    @jsii.member(jsii_name="resetOnErrorAction")
    def reset_on_error_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnErrorAction", []))

    @jsii.member(jsii_name="resetRelativePriority")
    def reset_relative_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRelativePriority", []))

    @jsii.member(jsii_name="resetVideoAnalyzerPreset")
    def reset_video_analyzer_preset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVideoAnalyzerPreset", []))

    @builtins.property
    @jsii.member(jsii_name="audioAnalyzerPreset")
    def audio_analyzer_preset(
        self,
    ) -> MediaTransformOutputAudioAnalyzerPresetOutputReference:
        return typing.cast(MediaTransformOutputAudioAnalyzerPresetOutputReference, jsii.get(self, "audioAnalyzerPreset"))

    @builtins.property
    @jsii.member(jsii_name="builtinPreset")
    def builtin_preset(self) -> MediaTransformOutputBuiltinPresetOutputReference:
        return typing.cast(MediaTransformOutputBuiltinPresetOutputReference, jsii.get(self, "builtinPreset"))

    @builtins.property
    @jsii.member(jsii_name="customPreset")
    def custom_preset(self) -> MediaTransformOutputCustomPresetOutputReference:
        return typing.cast(MediaTransformOutputCustomPresetOutputReference, jsii.get(self, "customPreset"))

    @builtins.property
    @jsii.member(jsii_name="faceDetectorPreset")
    def face_detector_preset(
        self,
    ) -> MediaTransformOutputFaceDetectorPresetOutputReference:
        return typing.cast(MediaTransformOutputFaceDetectorPresetOutputReference, jsii.get(self, "faceDetectorPreset"))

    @builtins.property
    @jsii.member(jsii_name="videoAnalyzerPreset")
    def video_analyzer_preset(
        self,
    ) -> "MediaTransformOutputVideoAnalyzerPresetOutputReference":
        return typing.cast("MediaTransformOutputVideoAnalyzerPresetOutputReference", jsii.get(self, "videoAnalyzerPreset"))

    @builtins.property
    @jsii.member(jsii_name="audioAnalyzerPresetInput")
    def audio_analyzer_preset_input(
        self,
    ) -> typing.Optional[MediaTransformOutputAudioAnalyzerPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputAudioAnalyzerPreset], jsii.get(self, "audioAnalyzerPresetInput"))

    @builtins.property
    @jsii.member(jsii_name="builtinPresetInput")
    def builtin_preset_input(
        self,
    ) -> typing.Optional[MediaTransformOutputBuiltinPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputBuiltinPreset], jsii.get(self, "builtinPresetInput"))

    @builtins.property
    @jsii.member(jsii_name="customPresetInput")
    def custom_preset_input(self) -> typing.Optional[MediaTransformOutputCustomPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputCustomPreset], jsii.get(self, "customPresetInput"))

    @builtins.property
    @jsii.member(jsii_name="faceDetectorPresetInput")
    def face_detector_preset_input(
        self,
    ) -> typing.Optional[MediaTransformOutputFaceDetectorPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputFaceDetectorPreset], jsii.get(self, "faceDetectorPresetInput"))

    @builtins.property
    @jsii.member(jsii_name="onErrorActionInput")
    def on_error_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "onErrorActionInput"))

    @builtins.property
    @jsii.member(jsii_name="relativePriorityInput")
    def relative_priority_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "relativePriorityInput"))

    @builtins.property
    @jsii.member(jsii_name="videoAnalyzerPresetInput")
    def video_analyzer_preset_input(
        self,
    ) -> typing.Optional["MediaTransformOutputVideoAnalyzerPreset"]:
        return typing.cast(typing.Optional["MediaTransformOutputVideoAnalyzerPreset"], jsii.get(self, "videoAnalyzerPresetInput"))

    @builtins.property
    @jsii.member(jsii_name="onErrorAction")
    def on_error_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "onErrorAction"))

    @on_error_action.setter
    def on_error_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2b52788bfb52c59c765e93837dd3322f5b6385f2acb62c10e7417eb1621019)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onErrorAction", value)

    @builtins.property
    @jsii.member(jsii_name="relativePriority")
    def relative_priority(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "relativePriority"))

    @relative_priority.setter
    def relative_priority(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0f09cd0fcfd254e31c1e3dee7525a0411b00cbd866d45828cf85383fc67c7b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "relativePriority", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformOutput, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformOutput, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformOutput, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2f4e0b3413e107129052b78146364562f08f8efbd59c8a649d1f81919a0795f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputVideoAnalyzerPreset",
    jsii_struct_bases=[],
    name_mapping={
        "audio_analysis_mode": "audioAnalysisMode",
        "audio_language": "audioLanguage",
        "experimental_options": "experimentalOptions",
        "insights_type": "insightsType",
    },
)
class MediaTransformOutputVideoAnalyzerPreset:
    def __init__(
        self,
        *,
        audio_analysis_mode: typing.Optional[builtins.str] = None,
        audio_language: typing.Optional[builtins.str] = None,
        experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        insights_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param audio_analysis_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.
        :param audio_language: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.
        :param experimental_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.
        :param insights_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#insights_type MediaTransform#insights_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f21d4da6e7f3bdf0c69bad3f28be58309cea877c7882b3ea9c5c9aaddbab0cf3)
            check_type(argname="argument audio_analysis_mode", value=audio_analysis_mode, expected_type=type_hints["audio_analysis_mode"])
            check_type(argname="argument audio_language", value=audio_language, expected_type=type_hints["audio_language"])
            check_type(argname="argument experimental_options", value=experimental_options, expected_type=type_hints["experimental_options"])
            check_type(argname="argument insights_type", value=insights_type, expected_type=type_hints["insights_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if audio_analysis_mode is not None:
            self._values["audio_analysis_mode"] = audio_analysis_mode
        if audio_language is not None:
            self._values["audio_language"] = audio_language
        if experimental_options is not None:
            self._values["experimental_options"] = experimental_options
        if insights_type is not None:
            self._values["insights_type"] = insights_type

    @builtins.property
    def audio_analysis_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_analysis_mode MediaTransform#audio_analysis_mode}.'''
        result = self._values.get("audio_analysis_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audio_language(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#audio_language MediaTransform#audio_language}.'''
        result = self._values.get("audio_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def experimental_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#experimental_options MediaTransform#experimental_options}.'''
        result = self._values.get("experimental_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def insights_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#insights_type MediaTransform#insights_type}.'''
        result = self._values.get("insights_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformOutputVideoAnalyzerPreset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformOutputVideoAnalyzerPresetOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformOutputVideoAnalyzerPresetOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f7b71787ab213f88aeb08caebb759ba4d0f4294809be57ede57b675db5a966b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAudioAnalysisMode")
    def reset_audio_analysis_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioAnalysisMode", []))

    @jsii.member(jsii_name="resetAudioLanguage")
    def reset_audio_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudioLanguage", []))

    @jsii.member(jsii_name="resetExperimentalOptions")
    def reset_experimental_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExperimentalOptions", []))

    @jsii.member(jsii_name="resetInsightsType")
    def reset_insights_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsightsType", []))

    @builtins.property
    @jsii.member(jsii_name="audioAnalysisModeInput")
    def audio_analysis_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audioAnalysisModeInput"))

    @builtins.property
    @jsii.member(jsii_name="audioLanguageInput")
    def audio_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audioLanguageInput"))

    @builtins.property
    @jsii.member(jsii_name="experimentalOptionsInput")
    def experimental_options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "experimentalOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="insightsTypeInput")
    def insights_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "insightsTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="audioAnalysisMode")
    def audio_analysis_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audioAnalysisMode"))

    @audio_analysis_mode.setter
    def audio_analysis_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd082d360b16eaf74b374b0253738554ac685bc145d88aa402d656590efd47b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioAnalysisMode", value)

    @builtins.property
    @jsii.member(jsii_name="audioLanguage")
    def audio_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audioLanguage"))

    @audio_language.setter
    def audio_language(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a57824460c1121ea78e5d8968903fcc20738f54e058af73d6f0ff4fdcacce6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audioLanguage", value)

    @builtins.property
    @jsii.member(jsii_name="experimentalOptions")
    def experimental_options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "experimentalOptions"))

    @experimental_options.setter
    def experimental_options(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a540b3542e3e33dbb239ef9a5724e7a29047fb00db08b55982c89f5501a845ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "experimentalOptions", value)

    @builtins.property
    @jsii.member(jsii_name="insightsType")
    def insights_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "insightsType"))

    @insights_type.setter
    def insights_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b059fe9fac3b9147ece6eac4638aa137dbec22b481310e4707a0f97ea9cf9bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insightsType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MediaTransformOutputVideoAnalyzerPreset]:
        return typing.cast(typing.Optional[MediaTransformOutputVideoAnalyzerPreset], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MediaTransformOutputVideoAnalyzerPreset],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__881c3d50817b9e2442aed3ae97a01f7998ebcffd13b2200569e06c177352c83a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "delete": "delete",
        "read": "read",
        "update": "update",
    },
)
class MediaTransformTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#create MediaTransform#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#delete MediaTransform#delete}.
        :param read: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#read MediaTransform#read}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#update MediaTransform#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e43fd1b703a56fc20bc768a0e7bce6dea3287e74430531f0e92c599aeddb818)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if read is not None:
            self._values["read"] = read
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#create MediaTransform#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#delete MediaTransform#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#read MediaTransform#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/azurerm/3.56.0/docs/resources/media_transform#update MediaTransform#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MediaTransformTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MediaTransformTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-azurerm.mediaTransform.MediaTransformTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__44d1510a9dad2d32571f2a0a58a967146d7ca8a5e44a1196823c610994557a37)
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
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__d840edc49ea910bbe1c70bca8273605df6f1f1181a00d3f967d9e3cb453e8db2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8199f8eb674c4e565702cd4419fc3289f16065c22c1a2877d6600c85ec469407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e0b423cdf9c4e5831c0ebc9012e376762dbd9fb012e0ef446b6c0e65d07cd51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ebd1d73f32d40163f1fe5d7b1f9a32f163b322085eb417766e9979973cac2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MediaTransformTimeouts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MediaTransformTimeouts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MediaTransformTimeouts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e8c5f7043957b5b658727509151c81a1bfe14f11d2020ef9a582f5bbe84fda4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "MediaTransform",
    "MediaTransformConfig",
    "MediaTransformOutput",
    "MediaTransformOutputAudioAnalyzerPreset",
    "MediaTransformOutputAudioAnalyzerPresetOutputReference",
    "MediaTransformOutputBuiltinPreset",
    "MediaTransformOutputBuiltinPresetOutputReference",
    "MediaTransformOutputBuiltinPresetPresetConfiguration",
    "MediaTransformOutputBuiltinPresetPresetConfigurationOutputReference",
    "MediaTransformOutputCustomPreset",
    "MediaTransformOutputCustomPresetCodec",
    "MediaTransformOutputCustomPresetCodecAacAudio",
    "MediaTransformOutputCustomPresetCodecAacAudioOutputReference",
    "MediaTransformOutputCustomPresetCodecCopyAudio",
    "MediaTransformOutputCustomPresetCodecCopyAudioOutputReference",
    "MediaTransformOutputCustomPresetCodecCopyVideo",
    "MediaTransformOutputCustomPresetCodecCopyVideoOutputReference",
    "MediaTransformOutputCustomPresetCodecDdAudio",
    "MediaTransformOutputCustomPresetCodecDdAudioOutputReference",
    "MediaTransformOutputCustomPresetCodecH264Video",
    "MediaTransformOutputCustomPresetCodecH264VideoLayer",
    "MediaTransformOutputCustomPresetCodecH264VideoLayerList",
    "MediaTransformOutputCustomPresetCodecH264VideoLayerOutputReference",
    "MediaTransformOutputCustomPresetCodecH264VideoOutputReference",
    "MediaTransformOutputCustomPresetCodecH265Video",
    "MediaTransformOutputCustomPresetCodecH265VideoLayer",
    "MediaTransformOutputCustomPresetCodecH265VideoLayerList",
    "MediaTransformOutputCustomPresetCodecH265VideoLayerOutputReference",
    "MediaTransformOutputCustomPresetCodecH265VideoOutputReference",
    "MediaTransformOutputCustomPresetCodecList",
    "MediaTransformOutputCustomPresetCodecOutputReference",
    "MediaTransformOutputCustomPresetFilter",
    "MediaTransformOutputCustomPresetFilterCropRectangle",
    "MediaTransformOutputCustomPresetFilterCropRectangleOutputReference",
    "MediaTransformOutputCustomPresetFilterDeinterlace",
    "MediaTransformOutputCustomPresetFilterDeinterlaceOutputReference",
    "MediaTransformOutputCustomPresetFilterFadeIn",
    "MediaTransformOutputCustomPresetFilterFadeInOutputReference",
    "MediaTransformOutputCustomPresetFilterFadeOut",
    "MediaTransformOutputCustomPresetFilterFadeOutOutputReference",
    "MediaTransformOutputCustomPresetFilterOutputReference",
    "MediaTransformOutputCustomPresetFilterOverlay",
    "MediaTransformOutputCustomPresetFilterOverlayAudio",
    "MediaTransformOutputCustomPresetFilterOverlayAudioOutputReference",
    "MediaTransformOutputCustomPresetFilterOverlayList",
    "MediaTransformOutputCustomPresetFilterOverlayOutputReference",
    "MediaTransformOutputCustomPresetFilterOverlayVideo",
    "MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle",
    "MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangleOutputReference",
    "MediaTransformOutputCustomPresetFilterOverlayVideoOutputReference",
    "MediaTransformOutputCustomPresetFilterOverlayVideoPosition",
    "MediaTransformOutputCustomPresetFilterOverlayVideoPositionOutputReference",
    "MediaTransformOutputCustomPresetFormat",
    "MediaTransformOutputCustomPresetFormatList",
    "MediaTransformOutputCustomPresetFormatMp4",
    "MediaTransformOutputCustomPresetFormatMp4OutputFile",
    "MediaTransformOutputCustomPresetFormatMp4OutputFileList",
    "MediaTransformOutputCustomPresetFormatMp4OutputFileOutputReference",
    "MediaTransformOutputCustomPresetFormatMp4OutputReference",
    "MediaTransformOutputCustomPresetFormatOutputReference",
    "MediaTransformOutputCustomPresetFormatTransportStream",
    "MediaTransformOutputCustomPresetFormatTransportStreamOutputFile",
    "MediaTransformOutputCustomPresetFormatTransportStreamOutputFileList",
    "MediaTransformOutputCustomPresetFormatTransportStreamOutputFileOutputReference",
    "MediaTransformOutputCustomPresetFormatTransportStreamOutputReference",
    "MediaTransformOutputCustomPresetOutputReference",
    "MediaTransformOutputFaceDetectorPreset",
    "MediaTransformOutputFaceDetectorPresetOutputReference",
    "MediaTransformOutputList",
    "MediaTransformOutputOutputReference",
    "MediaTransformOutputVideoAnalyzerPreset",
    "MediaTransformOutputVideoAnalyzerPresetOutputReference",
    "MediaTransformTimeouts",
    "MediaTransformTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__4c41f75eff24819994958b09a36c6e201c83521a2f56558da9c72e6c1092fecb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    media_services_account_name: builtins.str,
    name: builtins.str,
    resource_group_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutput, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[MediaTransformTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__aac089d9982f230f82d95ebdb742b3102b62365a83b3986aecb192666f5605a0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutput, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c484f553fe83e00cc7ebf3d19380c26db01278d40912d3122273cf5d87a4ef98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765acf3267073be26589e651f5abc8aa1b9ebe6f00d0c2dd01fee2598ac8decb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a64d0fd84d7e7cdb13bbbf9a77362ca775919c44e5f389baff7604ff496577f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__612d790c370ef7c1243727283235dc5de0f8207e4ac50898580bcdf405a06082(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16de48379a7915c82c056609e94f7730f02cc6b10d0405f0db65a2579af36cc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d209c9d3caa58f11af5ecf8bd18ddc9bff1f3ac46948505b039466b853b75d7c(
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
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    output: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutput, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeouts: typing.Optional[typing.Union[MediaTransformTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__666c2c9da913938700dc7a27642e2ad57f50a195b5bb94a8c837c8d76bb13caa(
    *,
    audio_analyzer_preset: typing.Optional[typing.Union[MediaTransformOutputAudioAnalyzerPreset, typing.Dict[builtins.str, typing.Any]]] = None,
    builtin_preset: typing.Optional[typing.Union[MediaTransformOutputBuiltinPreset, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_preset: typing.Optional[typing.Union[MediaTransformOutputCustomPreset, typing.Dict[builtins.str, typing.Any]]] = None,
    face_detector_preset: typing.Optional[typing.Union[MediaTransformOutputFaceDetectorPreset, typing.Dict[builtins.str, typing.Any]]] = None,
    on_error_action: typing.Optional[builtins.str] = None,
    relative_priority: typing.Optional[builtins.str] = None,
    video_analyzer_preset: typing.Optional[typing.Union[MediaTransformOutputVideoAnalyzerPreset, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86be4a547b7de35e3afda494aa38b62e654677fcdff205b65dff86815f012de5(
    *,
    audio_analysis_mode: typing.Optional[builtins.str] = None,
    audio_language: typing.Optional[builtins.str] = None,
    experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b7d395d1b3f01cb790ac467032c53ffa9ec5ce4c5d360da4f2b991b3a8b77d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d65612928c10a6dca460daef87ccf949b480be7328a992cce94e160dcc5f4c4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72b9492548862da82bd8cb63c7d8f31f8dae74ec2c02438e53905504a40b8364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca692e77e9be8b46f8c1979a4a4d48be36f7768229bc7bcf125c34790152f1a2(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebfb78476aa46c3af4b31d0c08f0f4906badb1955918d4992296705c51407255(
    value: typing.Optional[MediaTransformOutputAudioAnalyzerPreset],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc0cfa8e191093b2699a78d5eacb297553ab56fbcd29a7002d0f47feefac77b2(
    *,
    preset_name: builtins.str,
    preset_configuration: typing.Optional[typing.Union[MediaTransformOutputBuiltinPresetPresetConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fc02c10b96f92dbd42b1e4867b5445b62a5f082b94a254aad7de93633cb3e9b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca46e3a1a2b119a67fd3a9df7a632485257928812a7eb25e1bf2eda4eec9be6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2c5f4d0cb36a7ef6df80284babe5ce85a6bb15f2343aa9be57a287a12090476(
    value: typing.Optional[MediaTransformOutputBuiltinPreset],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec9e24e0af1f270697bef2afb290a540770c2baa2c5e24a5a23f73053d55244(
    *,
    complexity: typing.Optional[builtins.str] = None,
    interleave_output: typing.Optional[builtins.str] = None,
    key_frame_interval_in_seconds: typing.Optional[jsii.Number] = None,
    max_bitrate_bps: typing.Optional[jsii.Number] = None,
    max_height: typing.Optional[jsii.Number] = None,
    max_layers: typing.Optional[jsii.Number] = None,
    min_bitrate_bps: typing.Optional[jsii.Number] = None,
    min_height: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02e2d10371e1246be3d1f04fe1eb112a3dc307e068e70a72dc171fda09c2677(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fca632f432164c280911b1eb931bc808cebcb9dddbceb496c50352c4ff8d206(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc906972f5fe4c6ffd539533f0ceb4d57d6f34641a2dc806a3c3d1ba692912e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4318d9b12a21eefaf5a66e85a235c04cd90c722a31fa32aa3430f05b270816c0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b6c9b8ede6dac50f6337b7353297f45adb3105ae171103e27f6741ec5bc54fa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb476ef77773559ebcaae433f9e21acce5dcf4639757e78aae5c53406e306eb7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac00b455968b70940e380b59f8e6bd49b7563adfa5cb18576008231db6396c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7084df8490d312a6605a3022eb3c6ed32dec356330a190d6028cff76d55e530(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63a18c6289552b522e6662406c621c75e60af93868d41e942f3f79c8b09b3ef6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97dc6935ab831d0365fb3be6e61f1a0fca92483b31914396c6f0d9e63f237660(
    value: typing.Optional[MediaTransformOutputBuiltinPresetPresetConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3eee445d59c63cbf85bb195a68b139d4a9eea1b7131f768f07504ceeda3f7f(
    *,
    codec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodec, typing.Dict[builtins.str, typing.Any]]]],
    format: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormat, typing.Dict[builtins.str, typing.Any]]]],
    filter: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilter, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adaad5f7810c550fa20cc1d3aa41259a84c69b66a2c4beb4de7df1fc2f56096(
    *,
    aac_audio: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecAacAudio, typing.Dict[builtins.str, typing.Any]]] = None,
    copy_audio: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecCopyAudio, typing.Dict[builtins.str, typing.Any]]] = None,
    copy_video: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecCopyVideo, typing.Dict[builtins.str, typing.Any]]] = None,
    dd_audio: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecDdAudio, typing.Dict[builtins.str, typing.Any]]] = None,
    h264_video: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH264Video, typing.Dict[builtins.str, typing.Any]]] = None,
    h265_video: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH265Video, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49003c3e5e7b5536b4a3c97e72593fd73e4392aa814f88bd379767d23298e45a(
    *,
    bitrate: typing.Optional[jsii.Number] = None,
    channels: typing.Optional[jsii.Number] = None,
    label: typing.Optional[builtins.str] = None,
    profile: typing.Optional[builtins.str] = None,
    sampling_rate: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82c3335d8c933673ef54c2817114c3cd1cf600d5309e6b60a070a58dec3cb65f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf41e4cd192ea5d1bf0798d16d72ad776c25c55041d96508e8cbb6ea16762d15(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fff3305579adc5f8e3455ca3bded09209c8a2095b0040075494bdc7b9dc3da0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b3b72802359df12bab8e4ffccf52a8f40230ae09ed167939e6468c5e99d8bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee0b10bbc9a5fe983c8a9dd298f8e222ab680dfc4180509291ef84f7fd6ba82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9993ad64e0fad6e99c2bcd51aa1dbc75107363db2def59266e46d9984a68ca9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b1ca1fdff0211374179dc76079001b34aabd5921ee5111a88760345a49b372(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecAacAudio],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__505505c30558157cdde8e56545366f398d51a250b7054f91b381df36c5df7f6b(
    *,
    label: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64f5d3f0c788c1c5efcd8f6a48a97cddad1303f9d35a23b3fb635ecab76da1e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1862d2760dbce5356b5d46b83584e10fc9f33ff12436f57950854dc2abc99a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f306a3019da7dd3bc7531985a4fe3ecb609494d42f2ef6e9a08ea70624e2131c(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecCopyAudio],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6428ecbb7a7dc2be6b3766b5d16e96f5a71648ffffc67df7ffbae1caeb6cb96(
    *,
    label: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1abb0252a3baa2ceb607e588f33bee8befc3a327b81643b39b59cec6a06d3e2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af8ede4ed719ed878bd7eac80f713ad574a876c96bd60512dcf0b675ce05669(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd9ce88b0f6506e28e702828268ae1e70cae2957dd5c8593f922c09ba691c04(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecCopyVideo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f023ab91f7c0f9ab16335d2f19437f7aa40909863a8933f7c589e73ecfe38ce9(
    *,
    bitrate: typing.Optional[jsii.Number] = None,
    channels: typing.Optional[jsii.Number] = None,
    label: typing.Optional[builtins.str] = None,
    sampling_rate: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4601e7b428f7066f8316058e98f72eab05a9cac600955dfd875a4e68c50011(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8e09ea8536a3263a73d22c233b3e54250350f7262ac1fde37b4e210d10117e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8219e81ea2fa46eff721f18683bf092c2913732ecb284f9de885b2716214ae1f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af7c293f6cb8c1ba7aad5f169132ad344fe5dba400194288a41da2cb0ad30a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f3ed9a8adf63f9aed643588bad41cdb411fea7e0ad0043cd5a6cd39d1307c4b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb431ac233e7ffd5da650cc8cb0e158e31a5bf0ed3213afd4ebbb9560823e9c9(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecDdAudio],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0614973057ec008d49a290ede7145b4ed953f3663d389e3eae0dcf8d48205fe2(
    *,
    complexity: typing.Optional[builtins.str] = None,
    key_frame_interval: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    rate_control_mode: typing.Optional[builtins.str] = None,
    scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    stretch_mode: typing.Optional[builtins.str] = None,
    sync_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ef16278d2aa15e2a9c0f83405ce28edae1e64ec5ec60426c9cc79f9834bad4(
    *,
    bitrate: jsii.Number,
    adaptive_b_frame_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    b_frames: typing.Optional[jsii.Number] = None,
    buffer_window: typing.Optional[builtins.str] = None,
    crf: typing.Optional[jsii.Number] = None,
    entropy_mode: typing.Optional[builtins.str] = None,
    frame_rate: typing.Optional[builtins.str] = None,
    height: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    level: typing.Optional[builtins.str] = None,
    max_bitrate: typing.Optional[jsii.Number] = None,
    profile: typing.Optional[builtins.str] = None,
    reference_frames: typing.Optional[jsii.Number] = None,
    slices: typing.Optional[jsii.Number] = None,
    width: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f534d213b35b6898cc9e5db06b441d9cdecac1f8b621b45ffa8c07dd9648095(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e8108db937585b6847cecbd2ac6eb2f2d7102498fc54e5e524ba59c6c6f00e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14b2a944761d822fbc52f87282826f434d61ae3f3678ed4d98b77742c46fe1af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f61dc6a0e9ecd4230db1e50671cfbca592fec19fccf5c8f71188e189e530d601(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__346094e91bf7d656cd7e75be5d69e6f9b31a02981401113107c0a0e809144823(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b6d5b320a9d55d6c611f2d708d83a978796f46986f65e82aafd5e31eb1c829b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH264VideoLayer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8452b03a2beb565be3a2197558eb5fac7a671c0a8661a56d46848a08a382dce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__243111df7a6b4f106295925f100ecd0c600b16110edaecc393c64c0f39f51dda(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a405d9d00539d6685d02e5798a6bc0eeb5f6081cec787b5016aa6a69997c0eae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b17fa8c0420c5c642b0d2dcd2e3731da6da3f30e37255bb14829d26e12ab67df(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f99dd9d583f564c7302aa80a11bd29f9c1437a4de80ae37bede51b8d1c361f12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac55b051d0d12087a8a806a7ae0c737245f181d3d712917d96e2137bf7bbdb1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7709245ac4372982479b439edd2f7bdad3b941a80ffb237ddda8a99ca0ac89ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c46c9138a2a33ae3990fca067638e773d64c12d3767d2688f8e0c2e36c8a7bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__779f14d368137c32ff8a24dc6277c9a90310b9bda49c509e353380e2a1a1c622(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__490790497c8d91b25bda86a8d0fb9d13e8250f800d925b90bf7a18de7746f0a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ac382ec0f6e9dbc59178e36d27536a8165508f211068af0c42c634c8b76e52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efbd3450a96e252d1bef7fc148c5053d949566c3838e51b8bc43d0a0d3315b35(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6febdf90af8d9588d5b96a9cb36e7dd3e16f20c15e67fbb163b2fa0a7072db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9357c1d9d8cffe04a506badbf568b91d8a7ddf74c7a8dae29260876f40976e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6b0085e8c1dbd5ffc7910e9de920d1bcf084906c2301edb7ffd0a0581b2fafe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da362f963cbd9bc3c9329c50c552958c80952ce3810d431e59ec01163ec41042(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e125e9cb8e0e896a03d2135fc758b146d14c8c9e9461c6ff942f40da19fcfb5(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ee4a6f1788cfe3730d2b15fc7fd57a461cdace6545a549a86cc947e65086363(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce41dd102b2fd416a64215a2f5330e8e287cc62565b4cac215dd3fb528db4230(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH264VideoLayer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85574a4a7e744437d62c4e44b369b9650ac364b3b67755c2d8dda32f1ef6f29d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15f9dd22e2e15b9775223c1a535110bcc32fb44297697a2480db5779b41aa090(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acb4fa35f48aaaba49631fc0d36732a5bde34f47016cf20de915bfef6027fa6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0de4c419e94f5fd621ff0051463b796150005a082db9594b514c8cad860743a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f4c424d4f8f8861b4cd80137ea7f4e60ea30ebacf0b39fb72af34d3cda9441(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3697787796e8b007527ca4392ca7119292c24185a190c9e51e0f65d1ee48aad6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3880029924d5341ec4a57ab25ea03b8d255cf5985d3405b8f172591441e30c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17454c0ba2d87d14be7debf069d616cc6f7cf452cb1a1f3f79972223cb58776(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecH264Video],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c2132a38699534039ae15fea77b210359922af3a65de92c73d084d4bf9b136e(
    *,
    complexity: typing.Optional[builtins.str] = None,
    key_frame_interval: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    layer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scene_change_detection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    stretch_mode: typing.Optional[builtins.str] = None,
    sync_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feb8641d5a996da27949de372d5433e134f1b471ed1a72c0b6d4b2362c2c108d(
    *,
    bitrate: jsii.Number,
    adaptive_b_frame_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    b_frames: typing.Optional[jsii.Number] = None,
    buffer_window: typing.Optional[builtins.str] = None,
    crf: typing.Optional[jsii.Number] = None,
    frame_rate: typing.Optional[builtins.str] = None,
    height: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    level: typing.Optional[builtins.str] = None,
    max_bitrate: typing.Optional[jsii.Number] = None,
    profile: typing.Optional[builtins.str] = None,
    reference_frames: typing.Optional[jsii.Number] = None,
    slices: typing.Optional[jsii.Number] = None,
    width: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d2f77d9262927d06e7adcc912720850529f928d3c593bef40751cdc5df7c103(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5560f191103cea17c2d517a872afd7de8ef2d146f9a482fc918dad4b91e4ab6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d935215b944526a9345d538e0b59ae60024f284f6a9e11128c73574ac0751460(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e0371add1eab2de3aa7a52a3bee7d9196ce43b01715231e02c336c6d6724a02(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7359bb57bab29360f8e759cc36d76c2af14fa79859e84642633e1bd821243de(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1384494e7b25290e690f8a7a06ac9389bba0efad28a35faeb7bd6536d79183b2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodecH265VideoLayer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26a756c3b95b0a51b2fe2deeb783803c714af6b28210a07fb8442d19b6fe23e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__525d611fc9970e5d54f1379cf15da1a475765f210a99715b335aebcc6e861186(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c0c400a29f3b4df551a3b34ef186385142839469bc7ffb0dd2309dc7cb84356(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54aea717e9a399451a82ceab3f5dd5609c5acce2f9876b302d6ec13c6f318f8a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28897d4a6782be58909bc3d27990991a6ccfd09a8a4c3e88718cbf8b0bb0ff44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__047b263dae683bac1d8d2dced13bd23d98ad3722201eb15235c84c6200b14169(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4dc0f4f6fd314b1b88d7cf875dff5127c384ad011036e3ba9dbb6497e651aed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd7e6f639859060596c26bafa03e980759b5908044917b0da222752458f25a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18f50ea03e58c4d2652e7b5e064b3cb0eb66f515eca7eace501def6d05a22ee1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5230b256c9fa679795de4e3679e4870f32263d8fae518cf4333069ffad4616d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8568f6dff2f261c435f75c0beecbed4e8fae8ac33500a6f80bce17bab8cde04(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c953948385c5929a5325d1cf3e064a77df79c1a7d01166679f8fc1f42afba2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ecdda1009a9d4e6f621e463259a9a85134a79426579be8336d985f2bd885939(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797b56ad9ab0bd5355a7191a6baaa33d6f639c3608e5f540a42bdb70ca62c04e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e49e08f754be02af1b452cdeca60fdaee7464f9705a4a1da54262ce049e7061d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd051ac8e3111b243f3fe6a977cf85289530771f46ef243323a7c8dd1c5a806f(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eeec47f8d6240c65bb65d88794793227f77a4f8bbdeea45867e7759c9a5b9e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__788a86d2cf268bc3db8bd8f2491f34799129e0e96f18aa90bb889441c1647561(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodecH265VideoLayer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e48c967f53b702255661887acb24f0ded13b3c9bf78a96dc77a07e3e77431262(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57edd75dc69f1ad650f2fb2e208b077bbd339d07f285926ea7373b6c88bc9b20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3db6f070c0bc766ea366a82115f0913787b3a1cac87909a23558ceab47b6ed7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea77d04ecf2af668b2fef6c750b68fe625391d69eacfcb301c72f16d383221e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a793403f5ec3a2ca987dc5158e5817abb4e24728a3a97b486ec9bbc5441a419(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c82c6e85a41c284efff948e42e2025cf5050f8e574b09affe2875ffb1aeb329(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__714d5bb0ee6b6cecc8d2726c0e63a88117e0f3507f1aed7d585c560eaaccdcee(
    value: typing.Optional[MediaTransformOutputCustomPresetCodecH265Video],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaf84390b48d975ff7e5ff782452612fe860e25247393d9f2f4d9f42c258e292(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0925b03f3f47ffb4dc1b567f21e56f4ca1cc7eeab97abf86322076ae7588bb4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd3d709e5383f3d5548c28f99e7cc7ac08ef82dba71fe5b2256850af8024014(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__578cddb836fe42cc2c111db9510ad6e7777e18dbd6b045b0d8c8f4a1ffe9f556(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7b617a9a3cc99979c8e58ea8b0227b2a647b7974917bcc88f742c19f8fcabd8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b54de4bcf0480219c60973d8d49a3e89b8faeb6f0bfc49d2868a2b1aee9a412e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetCodec]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc1a793d4739d015f3332cc48f62418043972e4f38a7a65ac7e808c062ef7548(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bc2cb69feb978543c48a7a6cdb2cd4e0d21695afbca33daff128ee2342ed3d8(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetCodec, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9b0f5a34aba8329ea4a236b3f00be748f5698db6b4e60b44a0abdc02980d191(
    *,
    crop_rectangle: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterCropRectangle, typing.Dict[builtins.str, typing.Any]]] = None,
    deinterlace: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterDeinterlace, typing.Dict[builtins.str, typing.Any]]] = None,
    fade_in: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterFadeIn, typing.Dict[builtins.str, typing.Any]]] = None,
    fade_out: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterFadeOut, typing.Dict[builtins.str, typing.Any]]] = None,
    overlay: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, typing.Dict[builtins.str, typing.Any]]]]] = None,
    rotation: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63a90e0cf3a378ad2202b5b298a9fb11f1fffb4a731a8b1c8c61529d26aebce8(
    *,
    height: typing.Optional[builtins.str] = None,
    left: typing.Optional[builtins.str] = None,
    top: typing.Optional[builtins.str] = None,
    width: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57782f0745a62ed5bb4f780715f84c595f3247c2104cfad3eb2569bd06799034(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49bd6bfabe2e6d995d21f85173c81d2f256b9158c9d8c10eb1c86dd7de212989(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__547cd7adf4a352c36d39c3ad01671d97fba51280a2a2a9178cb2380566966641(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8301e0dc1391360e8e3ebc1d533334d6eed338c30ffaff0848273b44e60bf14f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__963283f5f4bb0d471b89ba2cae569ee80a3d5bc620daf32841d2ad5b76ddc300(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c09e504d60f3692aa0cf543161fb162c1180171c8ffd8dc63d14aefb2a0e073(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterCropRectangle],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a2b7e60a16577b45e842a0b1e81605850f49ec0cadf0ac3c07b142021f7da8(
    *,
    mode: typing.Optional[builtins.str] = None,
    parity: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4ea5e7541c9d204d52fd5ee4cace7851c215d4f70e97659fbb2eeb541ed5037(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3caf2a85887bda1d35ef00b7401d28aadda0063e3e8905e28f5a722bd27d5070(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21fc4afca0bc452208f70112e2f75b5308d8d1c2829880aa45800da3e3464456(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__579498f06d441d4555ed5d861d11a5b29b14dfa9a6cc8c7cdf1aff1a9b074dc2(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterDeinterlace],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8592f33870e8b521a2af754a50b4b6cb5fc40e538ff4d1d46b284305848b6941(
    *,
    duration: builtins.str,
    fade_color: builtins.str,
    start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f35677a7d1cf3f98bef75e43cff11253c6918df8bd03058f6ccb1b0f6c761ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7d7083b6ff28551a5d4cbd5f0d589ae16fb5eaed8303de5007ed273a39ae39d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e52eb9f88e9650a3e1ec1c59470f69a7ba4ea85e0d68b5777a203ae5aa196cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e50473820fd67296dd38714d14de8a326e295589c49a7939d96a7ed1cd0a3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a8db5c0e37ca53057bc35236f350295ae7cd431957f87274ae236008769fcc(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterFadeIn],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765eedb410cb2bc43f8fe6206285494cd047a4254745c1cf3a06b64a9341c6cd(
    *,
    duration: builtins.str,
    fade_color: builtins.str,
    start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf0efd33277237f145912e57ad1f7357711d51c90b1f1ba40981f6a22c97491(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0880a0759ed38f029c4cf4cb5cbbaa869b4e51f2293aa00d3fab9c22c6c343f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00a62c46e0c4a0533a215ca6918399d91493f6cf0fb88bb25e921a40eba5a79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7c3c68ad0bb7b91906dd84f507d66ab0e1cef148ad7c16e3a3b35352f250ca3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4221803d1cacf2b0bcdf5689502bd2ded1e0caf2200fc18faaeaba2b0d6cdbd(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterFadeOut],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76f408e7a95b67476ad115def276feb73d5a0c53f124209edea6dc0d1202ccbc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__558c028bc02fa18ffb82efba716da46419fa41c7162b3324f4539235a7046482(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17f290558d727a1560fc9134c981fe89acf77381872596b6482ba78ae612f5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8afd4b810bebbbeaf153198761131fe0a684a4fa9abdbde25691c20867455ccb(
    value: typing.Optional[MediaTransformOutputCustomPresetFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__140872c6e8f044feafb84c85accf0515697622204dda500dded6f29001be8d5b(
    *,
    audio: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlayAudio, typing.Dict[builtins.str, typing.Any]]] = None,
    video: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlayVideo, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b131475ed54b22663f5a2fdd63e570984bfae626cc84db383c736d8e25680ad(
    *,
    input_label: builtins.str,
    audio_gain_level: typing.Optional[jsii.Number] = None,
    end: typing.Optional[builtins.str] = None,
    fade_in_duration: typing.Optional[builtins.str] = None,
    fade_out_duration: typing.Optional[builtins.str] = None,
    start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34e59f5f5460b06e03a819fc35b4ebdac246fe9df25bd771e8edd3ac1ed19d51(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__143a36f500bde3e2d62ff4a40d351dc994eb4b78c1ca8ef9aa444cefc164e85a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8365ce92c4242ce9e8583c00fe482eff44ee04c769e8d998d617fa3da4c1d1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be1c4b2d52a5f701323366da78d2a1224d56e8a495fe8f3e8e2db0d2adad336(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__627cbe58f4c646c740037c7cea94bc6708776b6ba79b92427456cdc1261ca185(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__320c62ace214a4637f93788459d5c7cbd700ac7258132afb707e2e10a470dd63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72d1f101a3674951581268c75af0694d547c79442dc8ff28b84817a3c3cd91e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d8425bab4588ede30879f0aca19e84c7653a06234b9063ecb2873510d4cd4de(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayAudio],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14e2b51d5f24c7060fa35d4a2c359a44cf04fd0d70903943f7aacb34f89413d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959380e59b48a3cf1bd2934c33ee63125f3b01234d997390f7e86d43d942452f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa3aed96efe2a6674b9277bfd9fb4f0079b3cce1c8d9911912175c390d6fa99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ea40247cabd67bc232d9dee204703db3d32cd75e18be3a2e348153d1cde20e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed7375157db7934042391a08d09d8e888c8c9c764578057790a47af927caaa56(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c211fc86e815fcb9302d3da59f27fc3789a495470d1b6dd8932e4b75f4dec13b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFilterOverlay]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d46286b276ebd3e6bcff7a6b5af32866a27469400be507c88185f01bfcb5ab2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f2f23917e1f130cc66a21aa66e1d54b9764ceb0ac66da6da5c2e3f2650c8637(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlay, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef01cb74534ee9af87d3c66cca798e326ce901edf830659558ff3ac225d9e523(
    *,
    input_label: builtins.str,
    audio_gain_level: typing.Optional[jsii.Number] = None,
    crop_rectangle: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle, typing.Dict[builtins.str, typing.Any]]] = None,
    end: typing.Optional[builtins.str] = None,
    fade_in_duration: typing.Optional[builtins.str] = None,
    fade_out_duration: typing.Optional[builtins.str] = None,
    opacity: typing.Optional[jsii.Number] = None,
    position: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFilterOverlayVideoPosition, typing.Dict[builtins.str, typing.Any]]] = None,
    start: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c9881344a669bf7003845fd19f14c16a4dded2ef821d0652cf20acdfc70253(
    *,
    height: typing.Optional[builtins.str] = None,
    left: typing.Optional[builtins.str] = None,
    top: typing.Optional[builtins.str] = None,
    width: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__402d903337cd5c45b8e25cca6deaabe4366c9bf456b210f0945262cebec4798f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9f659ea86511c4684143dea32ab46de578a730c959dad78d47dc8504b6373e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f528fbb6be9a700592a6370b2e8f3ef3cd4bcc2b5c7ae625bcadc1357148717(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edcfdad836e093e49b74c60aad82a1f8076743eb9ecda145c9a6a528472f8dd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cf19ca327f844d96aacfa4cb00bc2920eecce2e6e67ba4313099b52282047f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1337c73f336a37380bf477907a7278ca56697296ca10ce37204ec66201075f1d(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoCropRectangle],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c29e733a301b14632884054afa2b0dd7c9bf0e3fea188a6d8c5103727caf5c7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__934a1b51a49c192fa747242deada04fd1b2d836c2d37a5dddefeb630a346e54f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bf1305bb2d4d04e2a6498de1ab13d3b9b4b3ce4c9e786eccf16012d9904832(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34eb945cdfc545ae61bf59bddb933ff2b66b78745e79f135e92b1456b993db07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b20968aa158f8615e37ab4ac68abe1592f823d18be163f5873ddcb258054cb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a4900f9dc5baf160e2340b02245cc543477ce115101276392cb0bcc18770002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fec1a784c315e6bc3ecc22c68db2526b5f8cacce9268657fb1fb7f3036e5e89d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae087a8541291e098a7a3717f6925c0aaaf435979d756e33aa8f634a59bab599(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6857390da838ed241702ff7c3958675ac7a4c5652c26ffa530bcac5e9f07f20(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideo],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d622acfc3cb210659435f6d99e0561ed7452a528e9df2d13a5bd601996512b15(
    *,
    height: typing.Optional[builtins.str] = None,
    left: typing.Optional[builtins.str] = None,
    top: typing.Optional[builtins.str] = None,
    width: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b255d0279e2104d75d403e50ec8f08aab94fb4696a1d0c5d38da8f92f20fae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2450c10de8e55ff43f89aeaa43433d8eca76a9e4893412bbd699d64bbde7ead5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f6a133125e0d81fca5033b483f783fafd16d7ccd46556e1fa46af7443dd01c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4621685850855688c83840d34e098ec1432000b4aefd0cf27ddf8ba0993cc8bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a91c61397cbb23234552ccaa925fe72d43be626a733b4c3f97ad96cf8b0f84c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3cca5b2d7db89a7f15aeba638fec58219fd4e7d4e8896c9623ff5e24b948876(
    value: typing.Optional[MediaTransformOutputCustomPresetFilterOverlayVideoPosition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97ffb02af523ce8c0138729722ae2cb28a4f8b4f61ba57904be6fa86db11e58c(
    *,
    mp4: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatMp4, typing.Dict[builtins.str, typing.Any]]] = None,
    transport_stream: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatTransportStream, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de0d8e09d57ff4eb04c601242a588af76388e30ad3edb79e0fcff3d887dff15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad0510bb6e6e3be1234e3541cfaa7fc809284c1b95f9ce2472e6681436c093f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9275677a46c3fd82d4a0d19446162b7873f66d34473a26f9c3965f7a26972adb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__075ee6b2acafc736f85f94ec59164c1568a3f59f33b1b7abc0ca9f02c0cd4cca(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b241b2cd94105dc1f58777a31dc537fbbfdb6de4a375558011cb62845155630f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__129bd33e1c80be2a6bb38b7465cd76cb6f18a6ff2aa53bf24bc7e12cea61e9cb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormat]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a2937961d9f9a169ddab9b98b8bcdadb9dd5e3b11206b1075ec4d1091856c74(
    *,
    filename_pattern: builtins.str,
    output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f1096a4daa33a5ba0cdd28f20b999986dcdc7fe7ecda12b63734fa0cd09f24(
    *,
    labels: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76f0f1016b18fab453aee7c2861d5ff177f6a7bde444f9190a28dc7c6e2bc320(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12611f8ccc0c0faa7923e108426938bd801962f49eb706aabf56d6c5ad66a7cd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48239786427e5a456fee4c0a4eed9b5a611130fe848211d04958b8ac645813fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd52c7910ca5e15fdac0f8c80eb9511f74133fac5e9e7727c9a36b007993beab(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__385789b3d88e1b4b0acd7519e272af4e0fa95f36156e1c33a4cbccba0fd0d5d9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f83bc957291092639da29f363b8e2c69b43f2b41f15337a54a343265ba69e3c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatMp4OutputFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb9f535cfe08a7a49f3eef31aacd43df0ae1c1e498818a8d0710567c00a09663(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21946f4fe82ed8826ee92441607a6cf43d92adfe24771029ad970ac61ad093b5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdd6ea0086f759643896fcb959070102ca1a55ac4ae2c645b0759e6ced8ea2e(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e58fc337ec9a7d62e730fc3c0d148949f9c6a7463d7671ae13934e9e95a6795(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c00358e4fb3d1048b69f55814034f6f45e893082002f16a40fa709e58f054047(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatMp4OutputFile, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a13c6e423cefb97a507712390d6c329f88cde6ac83ff531eca50bf97037e267(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__229d718d8c7f107f21ec1d398ec2f7406f6a8b97b84d51e244e6941afabfb36e(
    value: typing.Optional[MediaTransformOutputCustomPresetFormatMp4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2beff49deee80986ebc6d34a65b818cec2e73ec621266fbb4ec2730ed97592de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5650e1899847f2eacbcd497862a955c8a2a94b511e343d17392eb24a60a62b83(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormat, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a052edb64cbeca87f085f92bd5df89309a79cd4ffd863c9cd28dc2af29fbbe7(
    *,
    filename_pattern: builtins.str,
    output_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a127ad614a33de138c24158e6f69a960ffffb2608b964e6ea7caaa4accdf02(
    *,
    labels: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a7d3502e777541bca0d11307c1cf516fd1e4fbd103ca8cedc10aaedc327201a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76144842485da9cdc09083ca5f027fd680183295b8cbafe00410f141e97097d3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c423a08d1146895a5f404d78cfd8e8666b017ae9ed9f07cfcfd9f16b5a81ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__346ce926721e92bd99fabd944935a5d83c1e3c64d7753c02fe91471aa932c10c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bcf1a666d9b854056027aad6083a408fefa979130a99434c8b68733f95e1407(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eba6bf20e623278805720b1c925fbf561cad1567b6f7697feef9e56427b61a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9139ebf1f5a6f9970b0dbdcd62ec549f072756807a8509d9e37c8b0481ac0f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8799cebcc12017200888112323fe48c1d2c5088c1ac0dfbc4a99a1f48391274a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__329e2f8f5a1bca6477b1e74a0ef26853922d455f9adba8b21f783e4570472603(
    value: typing.Optional[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__987bfe3ed4539122247fad4fb1cfea5268be1d177ffe21bed1bf2013a5c4cc39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0409d13fbbe2cc391336c2012fdb7524a13d622b3300f3566452f94c419b58b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormatTransportStreamOutputFile, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f28dc19ea5242b38920ea0495b58a19b5867204a7dadefb3524868de18c650d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e318bfe7fc1db7fa1c993953fe52efddbaab0899114992a73b7fb016671070e9(
    value: typing.Optional[MediaTransformOutputCustomPresetFormatTransportStream],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ea9252f6dc724f481dc3f7c60983db8b3ed8f98dc4235190ed0a02923f6f77c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f47f1a5dde3e3374a2181cff1d833b30a2347a876f047e250519fc5f8d8e832(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetCodec, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c023d59674971f317b69e2961cb58b31a01ccd44d63e7a42601020b2fb7c97f5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MediaTransformOutputCustomPresetFormat, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9de60dc00c0785c04d223c7822367773bfed264e64755716d258a2f16040795(
    value: typing.Optional[MediaTransformOutputCustomPreset],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c59bd284086270465237bf3fd3a92dcc4058494fffeee893f3de6bade87935c(
    *,
    analysis_resolution: typing.Optional[builtins.str] = None,
    blur_type: typing.Optional[builtins.str] = None,
    experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    face_redactor_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a0c631f840d38c32d0e610f614c22be53a7272a95389d831392f2fa43ddffd8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1db3e523de183b9f9fa92fb1205b76ea7168ed14ed188ef3c002688eedb783(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af42b2c854256bd4f3ad287686f6f5537c5fa3f51aa0d56cb9712bdfba33bea9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b03ebc16204986c569345615284c0d15661bde1192bc988c97a85054459fce(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c84ebf43a262740e70c182ab090933454005b232e9aadfe790e8a837e62e4eaf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cb4155e3f3339515d1ccf85655135e9c64762332528a9ef97fa82ac3371abdc(
    value: typing.Optional[MediaTransformOutputFaceDetectorPreset],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9317d382df1ad8258ff57d6871121b80fb035c98bd4801c9b19a27204f83a2e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1441d9de76bfa2c71300f6f681987187350e3cc8a8964886d7b039986a6ca5e9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26285451211fb4312004f4c366e60eba513d2cac63e7f94d5d0848a78066b300(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e0a546320d11a4b1e336ba244ce3ef08c04d643dfca8dc2c9a0f525c1ca0a8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9495279790ab8749bc4f493ea18cb893f7cfb80f5fa56125c3d18f7e394f5842(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238c880f727f4e248192e062f420d9b65f16c8eeecee50297408cde591f7bf1f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MediaTransformOutput]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bd6a33c37bb09f019110b2d711d588d130f4ff4aa13d9ae44bb8f7fa19af48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2b52788bfb52c59c765e93837dd3322f5b6385f2acb62c10e7417eb1621019(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0f09cd0fcfd254e31c1e3dee7525a0411b00cbd866d45828cf85383fc67c7b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2f4e0b3413e107129052b78146364562f08f8efbd59c8a649d1f81919a0795f(
    value: typing.Optional[typing.Union[MediaTransformOutput, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f21d4da6e7f3bdf0c69bad3f28be58309cea877c7882b3ea9c5c9aaddbab0cf3(
    *,
    audio_analysis_mode: typing.Optional[builtins.str] = None,
    audio_language: typing.Optional[builtins.str] = None,
    experimental_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    insights_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f7b71787ab213f88aeb08caebb759ba4d0f4294809be57ede57b675db5a966b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd082d360b16eaf74b374b0253738554ac685bc145d88aa402d656590efd47b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a57824460c1121ea78e5d8968903fcc20738f54e058af73d6f0ff4fdcacce6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a540b3542e3e33dbb239ef9a5724e7a29047fb00db08b55982c89f5501a845ee(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b059fe9fac3b9147ece6eac4638aa137dbec22b481310e4707a0f97ea9cf9bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__881c3d50817b9e2442aed3ae97a01f7998ebcffd13b2200569e06c177352c83a(
    value: typing.Optional[MediaTransformOutputVideoAnalyzerPreset],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e43fd1b703a56fc20bc768a0e7bce6dea3287e74430531f0e92c599aeddb818(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    read: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44d1510a9dad2d32571f2a0a58a967146d7ca8a5e44a1196823c610994557a37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d840edc49ea910bbe1c70bca8273605df6f1f1181a00d3f967d9e3cb453e8db2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8199f8eb674c4e565702cd4419fc3289f16065c22c1a2877d6600c85ec469407(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e0b423cdf9c4e5831c0ebc9012e376762dbd9fb012e0ef446b6c0e65d07cd51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ebd1d73f32d40163f1fe5d7b1f9a32f163b322085eb417766e9979973cac2a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e8c5f7043957b5b658727509151c81a1bfe14f11d2020ef9a582f5bbe84fda4(
    value: typing.Optional[typing.Union[MediaTransformTimeouts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
