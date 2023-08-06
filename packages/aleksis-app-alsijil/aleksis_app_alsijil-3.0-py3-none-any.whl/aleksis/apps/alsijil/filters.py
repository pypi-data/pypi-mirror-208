from django.utils.translation import gettext as _

from django_filters import CharFilter, DateFilter, FilterSet
from material import Layout, Row

from aleksis.core.models import SchoolTerm

from .models import PersonalNote


class PersonalNoteFilter(FilterSet):
    day_start = DateFilter(lookup_expr="gte", label=_("After"))
    day_end = DateFilter(lookup_expr="lte", label=_("Before"))
    subject = CharFilter(lookup_expr="icontains", label=_("Subject"))

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()

            current_school_term = SchoolTerm.current
            if not data.get("day_start") and current_school_term:
                data["day_start"] = current_school_term.date_start

            for name, f in self.base_filters.items():
                initial = f.extra.get("initial")
                if not data.get(name) and initial:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)
        self.form.fields["tardiness__lt"].label = _("Tardiness is lower than")
        self.form.fields["tardiness__gt"].label = _("Tardiness is bigger than")
        self.form.layout = Layout(
            Row("subject"),
            Row("day_start", "day_end"),
            Row("absent", "excused", "excuse_type"),
            Row("tardiness__gt", "tardiness__lt", "extra_marks"),
        )

    class Meta:
        model = PersonalNote
        fields = {
            "excused": ["exact"],
            "tardiness": ["lt", "gt"],
            "absent": ["exact"],
            "excuse_type": ["exact"],
            "extra_marks": ["exact"],
        }
