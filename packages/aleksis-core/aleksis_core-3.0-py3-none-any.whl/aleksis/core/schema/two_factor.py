import graphene
from graphene import ObjectType
from two_factor.plugins.email.utils import mask_email
from two_factor.plugins.phonenumber.utils import (
    backup_phones,
    format_phone_number,
    get_available_phone_methods,
    mask_phone_number,
)
from two_factor.plugins.registry import registry
from two_factor.utils import default_device


class TwoFactorDeviceType(ObjectType):
    persistent_id = graphene.ID()
    name = graphene.String()
    method_code = graphene.String()
    verbose_name = graphene.String()
    confirmed = graphene.Boolean()
    method_verbose_name = graphene.String()

    action = graphene.String()
    verbose_action = graphene.String()

    def get_method(root, info, **kwargs):
        if getattr(root, "method", None):
            return registry.get_method(root.method)
        return registry.method_from_device(root)

    def resolve_action(root, info, **kwargs):
        method = TwoFactorDeviceType.get_method(root, info, **kwargs)
        return method.get_action(root)

    def resolve_verbose_action(root, info, **kwargs):
        method = TwoFactorDeviceType.get_method(root, info, **kwargs)
        return method.get_verbose_action(root)

    def resolve_verbose_name(root, info, **kwargs):
        method = TwoFactorDeviceType.get_method(root, info, **kwargs)
        if method.code in ["sms", "call"]:
            return mask_phone_number(format_phone_number(root.number))
        elif method.code == "email":
            email = root.email or root.user.email
            if email:
                return mask_email(email)

        return method.verbose_name

    def resolve_method_verbose_name(root, info, **kwargs):
        method = TwoFactorDeviceType.get_method(root, info, **kwargs)
        return method.verbose_name

    def resolve_method_code(root, info, **kwargs):
        method = TwoFactorDeviceType.get_method(root, info, **kwargs)

        return method.code


class PhoneTwoFactorDeviceType(TwoFactorDeviceType):
    number = graphene.String


class TwoFactorType(ObjectType):
    activated = graphene.Boolean()
    default_device = graphene.Field(TwoFactorDeviceType)
    backup_phones = graphene.List(PhoneTwoFactorDeviceType)
    other_devices = graphene.List(TwoFactorDeviceType)
    backup_tokens_count = graphene.Int()
    phone_methods_available = graphene.Boolean()

    def resolve_backup_tokens_count(root, info, **kwargs):
        try:
            backup_tokens = root.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0
        return backup_tokens

    def resolve_phone_methods_available(root, info, **kwargs):
        return bool(get_available_phone_methods())

    def resolve_default_device(root, info, **kwargs):
        return default_device(root)

    def resolve_activated(root, info, **kwargs):
        return bool(default_device(root))

    def resolve_other_devices(root, info, **kwargs):
        main_device = TwoFactorType.resolve_default_device(root, info, **kwargs)
        other_devices = []
        for method in registry.get_methods():
            other_devices += list(method.get_other_authentication_devices(root, main_device))

        return other_devices

    def resolve_backup_phones(root, info, **kwargs):
        return backup_phones(root)
