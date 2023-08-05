from wagtail.contrib.modeladmin.options import (ModelAdmin)

from .models import Publication


class PublicationModelAdmin(ModelAdmin):

    model = Publication
    menu_icon = 'date'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = True  # or True to exclude pages of this type from Wagtail's explorer view
    exclude_from_admin_menu = False

    list_display = ('year', 'doi', 'publication_title', 'author_names')
    list_filter = ('tags',)
    search_fields = ('publication_title',)
    ordering = ('-year', 'publication_title', 'doi')

    index_view_extra_js = ["bibster/js/publication_modeladmin.js"]

    instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PublicationModelAdmin.instance = self
