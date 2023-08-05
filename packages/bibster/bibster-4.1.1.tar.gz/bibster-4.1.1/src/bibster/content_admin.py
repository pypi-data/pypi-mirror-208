
from wagtail_content_admin.content_admin import ContentAdmin

from .identifiers import DEFAULT_STYLE
from .format_auxiliaries import DEFAULT_MARKUP_FORMAT, HTML_MARKUP_FORMAT
from .permissions import permission_policy
from .apps import get_app_label

__all__ = ['publication_admin', 'PublicationAdmin']

APP_LABEL = get_app_label()


class PublicationAdmin(ContentAdmin):

    url_namespace = APP_LABEL
    permission_policy = permission_policy

    def __init__(self, style_name=DEFAULT_STYLE, markup_format_name=DEFAULT_MARKUP_FORMAT):
        super(PublicationAdmin, self).__init__()

        self.style_name = style_name
        self.markup_format_name = markup_format_name

    def render_preview_inner(self, instance, **kwargs):
        result, _ = instance.format(self.style_name,
                                    markup_format_name=self.markup_format_name,
                                    placeholder="",
                                    bypass_cache=False)

        return result


publication_admin = PublicationAdmin(markup_format_name=HTML_MARKUP_FORMAT)
