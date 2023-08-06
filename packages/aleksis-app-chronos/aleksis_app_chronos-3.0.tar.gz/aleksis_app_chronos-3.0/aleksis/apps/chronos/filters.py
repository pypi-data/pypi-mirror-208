from typing import Sequence

from django.db.models import Count, Q
from django.forms import RadioSelect
from django.utils.translation import gettext as _

from django_filters import BooleanFilter, FilterSet, ModelMultipleChoiceFilter
from django_select2.forms import ModelSelect2MultipleWidget
from material import Layout, Row

from aleksis.core.models import Group, Person, Room, SchoolTerm

from .models import Break, Subject, SupervisionArea, TimePeriod


class MultipleModelMultipleChoiceFilter(ModelMultipleChoiceFilter):
    """Filter for filtering multiple fields with one input.

    >>> multiple_filter = MultipleModelMultipleChoiceFilter(["room", "substitution_room"])
    """

    def filter(self, qs, value):  # noqa
        if not value:
            return qs

        if self.is_noop(qs, value):
            return qs

        q = Q()
        for v in set(value):
            if v == self.null_value:
                v = None
            for field in self.lookup_fields:
                q = q | Q(**{field: v})

            qs = self.get_method(qs)(q)

        return qs.distinct() if self.distinct else qs

    def __init__(self, lookup_fields: Sequence[str], *args, **kwargs):
        self.lookup_fields = lookup_fields
        super().__init__(self, *args, **kwargs)


class LessonPeriodFilter(FilterSet):
    period = ModelMultipleChoiceFilter(queryset=TimePeriod.objects.all())
    lesson__groups = ModelMultipleChoiceFilter(
        queryset=Group.objects.all(),
        widget=ModelSelect2MultipleWidget(
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            search_fields=[
                "name__icontains",
                "short_name__icontains",
            ],
        ),
    )
    room = MultipleModelMultipleChoiceFilter(
        ["room", "current_substitution__room"],
        queryset=Room.objects.all(),
        label=_("Room"),
        widget=ModelSelect2MultipleWidget(
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            search_fields=[
                "name__icontains",
                "short_name__icontains",
            ],
        ),
    )
    lesson__teachers = MultipleModelMultipleChoiceFilter(
        ["lesson__teachers", "current_substitution__teachers"],
        queryset=Person.objects.none(),
        label=_("Teachers"),
        widget=ModelSelect2MultipleWidget(
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
        ),
    )
    lesson__subject = MultipleModelMultipleChoiceFilter(
        ["lesson__subject", "current_substitution__subject"],
        queryset=Subject.objects.all(),
        label=_("Subject"),
        widget=ModelSelect2MultipleWidget(
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            search_fields=[
                "name__icontains",
                "short_name__icontains",
            ],
        ),
    )
    substituted = BooleanFilter(
        field_name="current_substitution",
        label=_("Substitution status"),
        lookup_expr="isnull",
        exclude=True,
        widget=RadioSelect(
            choices=[
                ("", _("All lessons")),
                (True, _("Substituted")),
                (False, _("Not substituted")),
            ]
        ),
    )

    def __init__(self, *args, **kwargs):
        weekday = kwargs.pop("weekday")
        super().__init__(*args, **kwargs)
        self.filters["period"].queryset = TimePeriod.objects.filter(weekday=weekday)
        self.filters["lesson__teachers"].queryset = (
            Person.objects.annotate(
                lessons_count=Count(
                    "lessons_as_teacher",
                    filter=Q(lessons_as_teacher__validity__school_term=SchoolTerm.current)
                    if SchoolTerm.current
                    else Q(),
                )
            )
            .filter(lessons_count__gt=0)
            .order_by("short_name", "last_name")
        )
        self.form.layout = Layout(
            Row("period", "lesson__groups", "room"),
            Row("lesson__teachers", "lesson__subject", "substituted"),
        )


class SupervisionFilter(FilterSet):
    break_item = ModelMultipleChoiceFilter(queryset=Break.objects.all())
    area = ModelMultipleChoiceFilter(queryset=SupervisionArea.objects.all())
    teacher = MultipleModelMultipleChoiceFilter(
        ["teacher", "current_substitution__teacher"],
        queryset=Person.objects.none(),
        label=_("Teacher"),
        widget=ModelSelect2MultipleWidget(
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
        ),
    )
    substituted = BooleanFilter(
        field_name="current_substitution",
        label=_("Substitution status"),
        lookup_expr="isnull",
        exclude=True,
        widget=RadioSelect(
            choices=[
                ("", _("All supervisions")),
                (True, _("Substituted")),
                (False, _("Not substituted")),
            ]
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["break_item"].queryset = Break.objects.filter(supervisions__in=self.queryset)
        self.filters["teacher"].queryset = (
            Person.objects.annotate(
                lessons_count=Count(
                    "lessons_as_teacher",
                    filter=Q(lessons_as_teacher__validity__school_term=SchoolTerm.current)
                    if SchoolTerm.current
                    else Q(),
                )
            )
            .filter(lessons_count__gt=0)
            .order_by("short_name", "last_name")
        )
        self.form.layout = Layout(
            Row("break_item", "area"),
            Row("teacher", "substituted"),
        )
