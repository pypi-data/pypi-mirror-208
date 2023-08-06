'''
# `cloudflare_list_item`

Refer to the Terraform Registory for docs: [`cloudflare_list_item`](https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item).
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


class ListItemA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.listItem.ListItemA",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item cloudflare_list_item}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: builtins.str,
        list_id: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip: typing.Optional[builtins.str] = None,
        redirect: typing.Optional[typing.Union["ListItemRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item cloudflare_list_item} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The account identifier to target for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#account_id ListItemA#account_id}
        :param list_id: The list identifier to target for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#list_id ListItemA#list_id}
        :param comment: An optional comment for the item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#comment ListItemA#comment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#id ListItemA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip: IP address to include in the list. Must provide only one of ``ip``, ``redirect``. **Modifying this attribute will force creation of a new resource.** Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#ip ListItemA#ip}
        :param redirect: redirect block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#redirect ListItemA#redirect}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17050bfd2a83146cda94bc0f1d9321465e6529d93d8c212e3f708f43a34ae3bd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ListItemAConfig(
            account_id=account_id,
            list_id=list_id,
            comment=comment,
            id=id,
            ip=ip,
            redirect=redirect,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putRedirect")
    def put_redirect(
        self,
        *,
        source_url: builtins.str,
        target_url: builtins.str,
        include_subdomains: typing.Optional[builtins.str] = None,
        preserve_path_suffix: typing.Optional[builtins.str] = None,
        preserve_query_string: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[jsii.Number] = None,
        subpath_matching: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_url: The source url of the redirect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#source_url ListItemA#source_url}
        :param target_url: The target url of the redirect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#target_url ListItemA#target_url}
        :param include_subdomains: Whether the redirect also matches subdomains of the source url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#include_subdomains ListItemA#include_subdomains}
        :param preserve_path_suffix: Whether to preserve the path suffix when doing subpath matching. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_path_suffix ListItemA#preserve_path_suffix}
        :param preserve_query_string: Whether the redirect target url should keep the query string of the request's url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_query_string ListItemA#preserve_query_string}
        :param status_code: The status code to be used when redirecting a request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#status_code ListItemA#status_code}
        :param subpath_matching: Whether the redirect also matches subpaths of the source url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#subpath_matching ListItemA#subpath_matching}
        '''
        value = ListItemRedirect(
            source_url=source_url,
            target_url=target_url,
            include_subdomains=include_subdomains,
            preserve_path_suffix=preserve_path_suffix,
            preserve_query_string=preserve_query_string,
            status_code=status_code,
            subpath_matching=subpath_matching,
        )

        return typing.cast(None, jsii.invoke(self, "putRedirect", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetRedirect")
    def reset_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirect", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(self) -> "ListItemRedirectOutputReference":
        return typing.cast("ListItemRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="listIdInput")
    def list_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "listIdInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectInput")
    def redirect_input(self) -> typing.Optional["ListItemRedirect"]:
        return typing.cast(typing.Optional["ListItemRedirect"], jsii.get(self, "redirectInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d440a0537d9d62a0e987d306ec4ee6a76e1991d47db4a5e1529f28ecd43cd1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value)

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a7cc4e5e375b37b4ad8116e089771a58da1ec0b0f708ab81a573de9d91a36bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ce148f2fd65e45651f267e12c06d1d4c8d94864c77a27248dda4f05a2d0389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98d4ee03576e2ac2abd13152573d2b7a7b9492ef535ec12ff1be1c33563dce7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value)

    @builtins.property
    @jsii.member(jsii_name="listId")
    def list_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listId"))

    @list_id.setter
    def list_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1f102f9f25a000c28cd2e9e76a3ed0c34de2115f5a469f6c83cfc9557b5376)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.listItem.ListItemAConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "list_id": "listId",
        "comment": "comment",
        "id": "id",
        "ip": "ip",
        "redirect": "redirect",
    },
)
class ListItemAConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: builtins.str,
        list_id: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip: typing.Optional[builtins.str] = None,
        redirect: typing.Optional[typing.Union["ListItemRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The account identifier to target for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#account_id ListItemA#account_id}
        :param list_id: The list identifier to target for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#list_id ListItemA#list_id}
        :param comment: An optional comment for the item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#comment ListItemA#comment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#id ListItemA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip: IP address to include in the list. Must provide only one of ``ip``, ``redirect``. **Modifying this attribute will force creation of a new resource.** Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#ip ListItemA#ip}
        :param redirect: redirect block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#redirect ListItemA#redirect}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(redirect, dict):
            redirect = ListItemRedirect(**redirect)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cdd5d032374ded443a6c766d97d90cfc05ba668c1cfb6e16010b7d4b2f8de87)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument list_id", value=list_id, expected_type=type_hints["list_id"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument redirect", value=redirect, expected_type=type_hints["redirect"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "list_id": list_id,
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
        if id is not None:
            self._values["id"] = id
        if ip is not None:
            self._values["ip"] = ip
        if redirect is not None:
            self._values["redirect"] = redirect

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
    def account_id(self) -> builtins.str:
        '''The account identifier to target for the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#account_id ListItemA#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def list_id(self) -> builtins.str:
        '''The list identifier to target for the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#list_id ListItemA#list_id}
        '''
        result = self._values.get("list_id")
        assert result is not None, "Required property 'list_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional comment for the item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#comment ListItemA#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#id ListItemA#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''IP address to include in the list.

        Must provide only one of ``ip``, ``redirect``. **Modifying this attribute will force creation of a new resource.**

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#ip ListItemA#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect(self) -> typing.Optional["ListItemRedirect"]:
        '''redirect block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#redirect ListItemA#redirect}
        '''
        result = self._values.get("redirect")
        return typing.cast(typing.Optional["ListItemRedirect"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListItemAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.listItem.ListItemRedirect",
    jsii_struct_bases=[],
    name_mapping={
        "source_url": "sourceUrl",
        "target_url": "targetUrl",
        "include_subdomains": "includeSubdomains",
        "preserve_path_suffix": "preservePathSuffix",
        "preserve_query_string": "preserveQueryString",
        "status_code": "statusCode",
        "subpath_matching": "subpathMatching",
    },
)
class ListItemRedirect:
    def __init__(
        self,
        *,
        source_url: builtins.str,
        target_url: builtins.str,
        include_subdomains: typing.Optional[builtins.str] = None,
        preserve_path_suffix: typing.Optional[builtins.str] = None,
        preserve_query_string: typing.Optional[builtins.str] = None,
        status_code: typing.Optional[jsii.Number] = None,
        subpath_matching: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_url: The source url of the redirect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#source_url ListItemA#source_url}
        :param target_url: The target url of the redirect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#target_url ListItemA#target_url}
        :param include_subdomains: Whether the redirect also matches subdomains of the source url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#include_subdomains ListItemA#include_subdomains}
        :param preserve_path_suffix: Whether to preserve the path suffix when doing subpath matching. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_path_suffix ListItemA#preserve_path_suffix}
        :param preserve_query_string: Whether the redirect target url should keep the query string of the request's url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_query_string ListItemA#preserve_query_string}
        :param status_code: The status code to be used when redirecting a request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#status_code ListItemA#status_code}
        :param subpath_matching: Whether the redirect also matches subpaths of the source url. Available values: ``disabled``, ``enabled``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#subpath_matching ListItemA#subpath_matching}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__434a16ac13fce9dbf8d03b287fa4d399a45ab2b8622f33e9155c63d47f76af28)
            check_type(argname="argument source_url", value=source_url, expected_type=type_hints["source_url"])
            check_type(argname="argument target_url", value=target_url, expected_type=type_hints["target_url"])
            check_type(argname="argument include_subdomains", value=include_subdomains, expected_type=type_hints["include_subdomains"])
            check_type(argname="argument preserve_path_suffix", value=preserve_path_suffix, expected_type=type_hints["preserve_path_suffix"])
            check_type(argname="argument preserve_query_string", value=preserve_query_string, expected_type=type_hints["preserve_query_string"])
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
            check_type(argname="argument subpath_matching", value=subpath_matching, expected_type=type_hints["subpath_matching"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_url": source_url,
            "target_url": target_url,
        }
        if include_subdomains is not None:
            self._values["include_subdomains"] = include_subdomains
        if preserve_path_suffix is not None:
            self._values["preserve_path_suffix"] = preserve_path_suffix
        if preserve_query_string is not None:
            self._values["preserve_query_string"] = preserve_query_string
        if status_code is not None:
            self._values["status_code"] = status_code
        if subpath_matching is not None:
            self._values["subpath_matching"] = subpath_matching

    @builtins.property
    def source_url(self) -> builtins.str:
        '''The source url of the redirect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#source_url ListItemA#source_url}
        '''
        result = self._values.get("source_url")
        assert result is not None, "Required property 'source_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_url(self) -> builtins.str:
        '''The target url of the redirect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#target_url ListItemA#target_url}
        '''
        result = self._values.get("target_url")
        assert result is not None, "Required property 'target_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_subdomains(self) -> typing.Optional[builtins.str]:
        '''Whether the redirect also matches subdomains of the source url. Available values: ``disabled``, ``enabled``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#include_subdomains ListItemA#include_subdomains}
        '''
        result = self._values.get("include_subdomains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preserve_path_suffix(self) -> typing.Optional[builtins.str]:
        '''Whether to preserve the path suffix when doing subpath matching. Available values: ``disabled``, ``enabled``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_path_suffix ListItemA#preserve_path_suffix}
        '''
        result = self._values.get("preserve_path_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preserve_query_string(self) -> typing.Optional[builtins.str]:
        '''Whether the redirect target url should keep the query string of the request's url. Available values: ``disabled``, ``enabled``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#preserve_query_string ListItemA#preserve_query_string}
        '''
        result = self._values.get("preserve_query_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status_code(self) -> typing.Optional[jsii.Number]:
        '''The status code to be used when redirecting a request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#status_code ListItemA#status_code}
        '''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subpath_matching(self) -> typing.Optional[builtins.str]:
        '''Whether the redirect also matches subpaths of the source url. Available values: ``disabled``, ``enabled``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/4.6.0/docs/resources/list_item#subpath_matching ListItemA#subpath_matching}
        '''
        result = self._values.get("subpath_matching")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListItemRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ListItemRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.listItem.ListItemRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a363c220c86881c40354aca27b75d00e201a2ad313aa5a2b3c01a2f4a3a86c8c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIncludeSubdomains")
    def reset_include_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeSubdomains", []))

    @jsii.member(jsii_name="resetPreservePathSuffix")
    def reset_preserve_path_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreservePathSuffix", []))

    @jsii.member(jsii_name="resetPreserveQueryString")
    def reset_preserve_query_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreserveQueryString", []))

    @jsii.member(jsii_name="resetStatusCode")
    def reset_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatusCode", []))

    @jsii.member(jsii_name="resetSubpathMatching")
    def reset_subpath_matching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubpathMatching", []))

    @builtins.property
    @jsii.member(jsii_name="includeSubdomainsInput")
    def include_subdomains_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includeSubdomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="preservePathSuffixInput")
    def preserve_path_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preservePathSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="preserveQueryStringInput")
    def preserve_query_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preserveQueryStringInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceUrlInput")
    def source_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "statusCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="subpathMatchingInput")
    def subpath_matching_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subpathMatchingInput"))

    @builtins.property
    @jsii.member(jsii_name="targetUrlInput")
    def target_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="includeSubdomains")
    def include_subdomains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includeSubdomains"))

    @include_subdomains.setter
    def include_subdomains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46d2c733dd487ae0bdaa4b4a6823b84fa97d518d12c634f2091018ce9698a645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeSubdomains", value)

    @builtins.property
    @jsii.member(jsii_name="preservePathSuffix")
    def preserve_path_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preservePathSuffix"))

    @preserve_path_suffix.setter
    def preserve_path_suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7420f361bed73b8b5a3c9adcff94d38f2805ae5c7799e38965dfdeed2a4218e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preservePathSuffix", value)

    @builtins.property
    @jsii.member(jsii_name="preserveQueryString")
    def preserve_query_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preserveQueryString"))

    @preserve_query_string.setter
    def preserve_query_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6827925c88ceba937a801834d55fe3031ad1ce80fa548e181c07237ad757ef6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preserveQueryString", value)

    @builtins.property
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUrl"))

    @source_url.setter
    def source_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d80b80cf30ad26fd4337c899d972fbf6ae8768bdbfebae918bcc824c2a8790f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceUrl", value)

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3444d89c1c5a1e8ab8521ba2f5cf7e302e98403c9e1eba35d1ca2b1eeb004bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value)

    @builtins.property
    @jsii.member(jsii_name="subpathMatching")
    def subpath_matching(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subpathMatching"))

    @subpath_matching.setter
    def subpath_matching(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a06928e0ff152bcd1189461d83d106269db1beaeb5b9d116a4412647014e1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subpathMatching", value)

    @builtins.property
    @jsii.member(jsii_name="targetUrl")
    def target_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUrl"))

    @target_url.setter
    def target_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de8b5cbcd21a44fac3f75494331b6035ff5589d14435fed3fb03e2037e959a98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUrl", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ListItemRedirect]:
        return typing.cast(typing.Optional[ListItemRedirect], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ListItemRedirect]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ea81aaa6c8d577ed12f1435081ed6c26c4f17432de02f7fd1d78d4c8236c98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "ListItemA",
    "ListItemAConfig",
    "ListItemRedirect",
    "ListItemRedirectOutputReference",
]

publication.publish()

def _typecheckingstub__17050bfd2a83146cda94bc0f1d9321465e6529d93d8c212e3f708f43a34ae3bd(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: builtins.str,
    list_id: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip: typing.Optional[builtins.str] = None,
    redirect: typing.Optional[typing.Union[ListItemRedirect, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1d440a0537d9d62a0e987d306ec4ee6a76e1991d47db4a5e1529f28ecd43cd1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a7cc4e5e375b37b4ad8116e089771a58da1ec0b0f708ab81a573de9d91a36bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ce148f2fd65e45651f267e12c06d1d4c8d94864c77a27248dda4f05a2d0389(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98d4ee03576e2ac2abd13152573d2b7a7b9492ef535ec12ff1be1c33563dce7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1f102f9f25a000c28cd2e9e76a3ed0c34de2115f5a469f6c83cfc9557b5376(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cdd5d032374ded443a6c766d97d90cfc05ba668c1cfb6e16010b7d4b2f8de87(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    list_id: builtins.str,
    comment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip: typing.Optional[builtins.str] = None,
    redirect: typing.Optional[typing.Union[ListItemRedirect, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__434a16ac13fce9dbf8d03b287fa4d399a45ab2b8622f33e9155c63d47f76af28(
    *,
    source_url: builtins.str,
    target_url: builtins.str,
    include_subdomains: typing.Optional[builtins.str] = None,
    preserve_path_suffix: typing.Optional[builtins.str] = None,
    preserve_query_string: typing.Optional[builtins.str] = None,
    status_code: typing.Optional[jsii.Number] = None,
    subpath_matching: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a363c220c86881c40354aca27b75d00e201a2ad313aa5a2b3c01a2f4a3a86c8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d2c733dd487ae0bdaa4b4a6823b84fa97d518d12c634f2091018ce9698a645(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7420f361bed73b8b5a3c9adcff94d38f2805ae5c7799e38965dfdeed2a4218e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6827925c88ceba937a801834d55fe3031ad1ce80fa548e181c07237ad757ef6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d80b80cf30ad26fd4337c899d972fbf6ae8768bdbfebae918bcc824c2a8790f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3444d89c1c5a1e8ab8521ba2f5cf7e302e98403c9e1eba35d1ca2b1eeb004bc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a06928e0ff152bcd1189461d83d106269db1beaeb5b9d116a4412647014e1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de8b5cbcd21a44fac3f75494331b6035ff5589d14435fed3fb03e2037e959a98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ea81aaa6c8d577ed12f1435081ed6c26c4f17432de02f7fd1d78d4c8236c98(
    value: typing.Optional[ListItemRedirect],
) -> None:
    """Type checking stubs"""
    pass
