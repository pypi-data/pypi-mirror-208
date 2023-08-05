from django.templatetags.static import static

import graphene


class ThemeLogoType(graphene.ObjectType):
    url = graphene.String(required=False)


class SitePreferencesType(graphene.ObjectType):
    general_title = graphene.String()

    theme_logo = graphene.Field(ThemeLogoType)
    theme_primary = graphene.String()
    theme_secondary = graphene.String()

    footer_imprint_url = graphene.String()
    footer_privacy_url = graphene.String()

    account_person_prefer_photo = graphene.Boolean()

    def resolve_general_title(parent, info, **kwargs):
        return parent["general__title"]

    def resolve_theme_logo(parent, info, **kwargs):
        return (
            parent["theme__logo"]
            if parent["theme__logo"]
            else {"url": static("/img/aleksis-banner.svg")}
        )

    def resolve_theme_primary(parent, info, **kwargs):
        return parent["theme__primary"]

    def resolve_theme_secondary(parent, info, **kwargs):
        return parent["theme__secondary"]

    def resolve_footer_imprint_url(parent, info, **kwargs):
        return parent["footer__imprint_url"]

    def resolve_footer_privacy_url(parent, info, **kwargs):
        return parent["footer__privacy_url"]

    def resolve_account_person_prefer_photo(parent, info, **kwargs):
        return parent["account__person_prefer_photo"]
