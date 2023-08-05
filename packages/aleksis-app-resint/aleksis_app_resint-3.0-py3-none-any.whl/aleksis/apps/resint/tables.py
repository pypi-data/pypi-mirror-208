from django.utils.translation import gettext as _

from django_tables2 import A, BooleanColumn, Column, DateTimeColumn, LinkColumn, Table


class LiveDocumentTable(Table):
    """Table to list live documents."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    document_name = Column(accessor="pk")
    name = LinkColumn("edit_live_document", args=[A("id")])
    filename = LinkColumn("show_live_document", args=[A("slug")])
    last_update = DateTimeColumn(accessor=A("last_update"))
    last_update_triggered_manually = BooleanColumn()
    edit = LinkColumn(
        "edit_live_document",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
        verbose_name=_("Edit"),
    )
    delete = LinkColumn(
        "delete_live_document",
        args=[A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
        verbose_name=_("Delete"),
    )

    def render_document_name(self, value, record):
        return record._meta.verbose_name

    def value_last_update(self, value, record):
        return record.last_update
