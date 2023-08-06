from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A


class SeatingPlanTable(tables.Table):
    class Meta:
        attrs = {"class": "highlight"}

    name = tables.LinkColumn("seating_plan", accessor=A("pk"), args=[A("id")])
    edit = tables.LinkColumn(
        "edit_seating_plan",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
    )
    delete = tables.LinkColumn(
        "delete_seating_plan",
        args=[A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
    )

    def render_name(self, value, record):
        return str(record)
