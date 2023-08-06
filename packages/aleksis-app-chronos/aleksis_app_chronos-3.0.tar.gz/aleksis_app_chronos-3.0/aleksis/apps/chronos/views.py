from datetime import datetime
from typing import Optional

from django.apps import apps
from django.db.models import FilteredRelation, Q
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

import reversion
from django_tables2 import RequestConfig
from rules.contrib.views import permission_required

from aleksis.core.decorators import pwa_cache
from aleksis.core.models import Announcement
from aleksis.core.util import messages
from aleksis.core.util.core_helpers import has_person
from aleksis.core.util.pdf import render_pdf

from .filters import LessonPeriodFilter, SupervisionFilter
from .forms import LessonSubstitutionForm, SupervisionSubstitutionForm
from .managers import TimetableType
from .models import Holiday, LessonPeriod, Supervision, TimePeriod
from .tables import LessonsTable, SupervisionsTable
from .util.build import build_timetable, build_weekdays
from .util.change_tracker import TimetableDataChangeTracker
from .util.chronos_helpers import (
    get_classes,
    get_el_by_pk,
    get_rooms,
    get_substitution_by_id,
    get_substitutions_context_data,
    get_supervision_substitution_by_id,
    get_teachers,
)
from .util.date import CalendarWeek, get_weeks_for_year, week_weekday_to_date
from .util.js import date_unix


@pwa_cache
@permission_required("chronos.view_timetable_overview_rule")
def all_timetables(request: HttpRequest) -> HttpResponse:
    """View all timetables for persons, groups and rooms."""
    context = {}

    user = request.user
    teachers, classes, rooms = get_teachers(user), get_classes(user), get_rooms(user)

    context["teachers"] = teachers
    context["classes"] = classes
    context["rooms"] = rooms

    return render(request, "chronos/all.html", context)


@pwa_cache
@permission_required("chronos.view_my_timetable_rule")
def my_timetable(
    request: HttpRequest,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> HttpResponse:
    """View personal timetable on a specified date."""
    context = {}

    if day:
        wanted_day = timezone.datetime(year=year, month=month, day=day).date()
        wanted_day = TimePeriod.get_next_relevant_day(wanted_day)
    else:
        wanted_day = TimePeriod.get_next_relevant_day(timezone.now().date(), datetime.now().time())

    wanted_week = CalendarWeek.from_date(wanted_day)

    if has_person(request.user):
        person = request.user.person
        type_ = person.timetable_type

        # Build timetable
        timetable = build_timetable("person", person, wanted_day)
        week_timetable = build_timetable("person", person, wanted_week)

        if type_ is None:
            # If no student or teacher, redirect to all timetables
            return redirect("all_timetables")

        super_el = person.timetable_object

        context["timetable"] = timetable
        context["week_timetable"] = week_timetable
        context["holiday"] = Holiday.on_day(wanted_day)
        context["super"] = {"type": type_, "el": super_el}
        context["type"] = type_
        context["day"] = wanted_day
        context["today"] = timezone.now().date()
        context["week"] = wanted_week
        context["periods"] = TimePeriod.get_times_dict()
        context["smart"] = True
        context["announcements"] = (
            Announcement.for_timetables().on_date(wanted_day).for_person(person)
        )
        context["week_announcements"] = (
            Announcement.for_timetables()
            .within_days(wanted_week[0], wanted_week[6])
            .for_person(person)
        )
        context["weekdays"] = build_weekdays(TimePeriod.WEEKDAY_CHOICES, wanted_week)
        context["weekdays_short"] = build_weekdays(TimePeriod.WEEKDAY_CHOICES_SHORT, wanted_week)
        context["url_prev"], context["url_next"] = TimePeriod.get_prev_next_by_day(
            wanted_day, "my_timetable_by_date"
        )

        return render(request, "chronos/my_timetable.html", context)
    else:
        return redirect("all_timetables")


@pwa_cache
@permission_required("chronos.view_timetable_rule", fn=get_el_by_pk)
def timetable(
    request: HttpRequest,
    type_: str,
    pk: int,
    year: Optional[int] = None,
    week: Optional[int] = None,
    regular: Optional[str] = None,
    is_print: bool = False,
) -> HttpResponse:
    """View a selected timetable for a person, group or room."""
    context = {}

    is_smart = regular != "regular"

    if is_print:
        is_smart = False

    el = get_el_by_pk(request, type_, pk, prefetch=True)

    if type(el) == HttpResponseNotFound:
        return HttpResponseNotFound()

    type_ = TimetableType.from_string(type_)

    if year and week:
        wanted_week = CalendarWeek(year=year, week=week)
    else:
        wanted_week = TimePeriod.get_relevant_week_from_datetime()

    # Build timetable
    timetable = build_timetable(type_, el, wanted_week, with_holidays=is_smart)
    context["timetable"] = timetable

    # Add time periods
    context["periods"] = TimePeriod.get_times_dict()

    # Build lists with weekdays and corresponding dates (long and short variant)
    context["weekdays"] = build_weekdays(
        TimePeriod.WEEKDAY_CHOICES, wanted_week, with_holidays=is_smart
    )
    context["weekdays_short"] = build_weekdays(
        TimePeriod.WEEKDAY_CHOICES_SHORT, wanted_week, with_holidays=is_smart
    )

    context["weeks"] = get_weeks_for_year(year=wanted_week.year)
    context["week"] = wanted_week
    context["type"] = type_
    context["pk"] = pk
    context["el"] = el
    context["smart"] = is_smart
    context["week_select"] = {
        "year": wanted_week.year,
        "dest": reverse(
            "timetable_by_week",
            args=[type_.value, pk, wanted_week.year, wanted_week.week],
        )[::-1]
        .replace(str(wanted_week.week)[::-1], "cw"[::-1], 1)
        .replace(str(wanted_week.year)[::-1], "year"[::-1], 1)[::-1],
    }

    if is_smart:
        start = wanted_week[TimePeriod.weekday_min]
        stop = wanted_week[TimePeriod.weekday_max]
        context["announcements"] = (
            Announcement.for_timetables().relevant_for(el).within_days(start, stop)
        )

    week_prev = wanted_week - 1
    week_next = wanted_week + 1

    context["url_prev"] = reverse(
        "timetable_by_week", args=[type_.value, pk, week_prev.year, week_prev.week]
    )
    context["url_next"] = reverse(
        "timetable_by_week", args=[type_.value, pk, week_next.year, week_next.week]
    )

    if apps.is_installed("aleksis.apps.alsijil"):
        context["is_alsijil_installed"] = True

    if is_print:
        context["back_url"] = reverse(
            "timetable_by_week",
            args=[type_.value, pk, wanted_week.year, wanted_week.week],
        )
        return render_pdf(request, "chronos/timetable_print.html", context)
    else:
        return render(request, "chronos/timetable.html", context)


@pwa_cache
@permission_required("chronos.view_lessons_day_rule")
def lessons_day(
    request: HttpRequest,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> HttpResponse:
    """View all lessons taking place on a specified day."""
    context = {}

    if day:
        wanted_day = timezone.datetime(year=year, month=month, day=day).date()
        wanted_day = TimePeriod.get_next_relevant_day(wanted_day)
    else:
        wanted_day = TimePeriod.get_next_relevant_day(timezone.now().date(), datetime.now().time())

    # Get lessons
    lesson_periods = LessonPeriod.objects.on_day(wanted_day)

    # Get filter
    lesson_periods_filter = LessonPeriodFilter(
        request.GET,
        queryset=lesson_periods.annotate(
            current_substitution=FilteredRelation(
                "substitutions",
                condition=(
                    Q(substitutions__week=wanted_day.isocalendar()[1], substitutions__year=year)
                ),
            )
        ),
        weekday=wanted_day.weekday(),
    )
    context["lesson_periods_filter"] = lesson_periods_filter

    # Build table
    lessons_table = LessonsTable(lesson_periods_filter.qs)
    RequestConfig(request).configure(lessons_table)

    context["lessons_table"] = lessons_table
    context["day"] = wanted_day
    context["lesson_periods"] = lesson_periods

    context["datepicker"] = {
        "date": date_unix(wanted_day),
        "dest": reverse("lessons_day"),
    }

    context["url_prev"], context["url_next"] = TimePeriod.get_prev_next_by_day(
        wanted_day, "lessons_day_by_date"
    )

    return render(request, "chronos/lessons_day.html", context)


@never_cache
@permission_required("chronos.edit_substitution_rule", fn=get_substitution_by_id)
def edit_substitution(request: HttpRequest, id_: int, week: int) -> HttpResponse:
    """View a form to edit a substitution lessen."""
    context = {}

    lesson_period = get_object_or_404(LessonPeriod, pk=id_)
    wanted_week = lesson_period.lesson.get_calendar_week(week)
    context["lesson_period"] = lesson_period
    day = week_weekday_to_date(wanted_week, lesson_period.period.weekday)
    context["date"] = day

    lesson_substitution = get_substitution_by_id(request, id_, week)

    if lesson_substitution:
        edit_substitution_form = LessonSubstitutionForm(
            request, request.POST or None, instance=lesson_substitution
        )
    else:
        edit_substitution_form = LessonSubstitutionForm(
            request,
            request.POST or None,
        )

    context["substitution"] = lesson_substitution

    if request.method == "POST":
        if edit_substitution_form.is_valid():
            with reversion.create_revision(atomic=True):
                tracker = TimetableDataChangeTracker()

                lesson_substitution = edit_substitution_form.save(commit=False)
                if not lesson_substitution.pk:
                    lesson_substitution.lesson_period = lesson_period
                    lesson_substitution.week = wanted_week.week
                    lesson_substitution.year = wanted_week.year
                lesson_substitution.save()
                edit_substitution_form.save_m2m()

                messages.success(request, _("The substitution has been saved."))

            return redirect("lessons_day_by_date", year=day.year, month=day.month, day=day.day)

    context["edit_substitution_form"] = edit_substitution_form

    return render(request, "chronos/edit_substitution.html", context)


@permission_required("chronos.delete_substitution_rule", fn=get_substitution_by_id)
def delete_substitution(request: HttpRequest, id_: int, week: int) -> HttpResponse:
    """Delete a substitution lesson.

    Redirects back to substition list on success.
    """
    lesson_period = get_object_or_404(LessonPeriod, pk=id_)
    wanted_week = lesson_period.lesson.get_calendar_week(week)

    get_substitution_by_id(request, id_, week).delete()

    messages.success(request, _("The substitution has been deleted."))

    date = wanted_week[lesson_period.period.weekday]
    return redirect("lessons_day_by_date", year=date.year, month=date.month, day=date.day)


@pwa_cache
@permission_required("chronos.view_substitutions_rule")
def substitutions(
    request: HttpRequest,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    is_print: bool = False,
) -> HttpResponse:
    """View all substitutions on a specified day."""
    context = get_substitutions_context_data(request, year, month, day, is_print)
    if not is_print:
        return render(request, "chronos/substitutions.html", context)
    else:
        return render_pdf(request, "chronos/substitutions_print.html", context)


@pwa_cache
@permission_required("chronos.view_supervisions_day_rule")
def supervisions_day(
    request: HttpRequest,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> HttpResponse:
    """View all supervisions taking place on a specified day."""
    context = {}

    if day:
        wanted_day = timezone.datetime(year=year, month=month, day=day).date()
        wanted_day = TimePeriod.get_next_relevant_day(wanted_day)
    else:
        wanted_day = TimePeriod.get_next_relevant_day(timezone.now().date(), datetime.now().time())

    # Get supervisions
    supervisions = (
        Supervision.objects.on_day(wanted_day)
        .filter_by_weekday(wanted_day.weekday())
        .order_by("break_item__before_period__period")
    )

    # Get filter
    supervisions_filter = SupervisionFilter(
        request.GET,
        queryset=supervisions.annotate(
            current_substitution=FilteredRelation(
                "substitutions",
                condition=(Q(substitutions__date=wanted_day)),
            )
        ),
    )
    context["supervisions_filter"] = supervisions_filter

    # Build table
    supervisions_table = SupervisionsTable(
        supervisions_filter.qs.annotate_week(week=CalendarWeek.from_date(wanted_day))
    )
    RequestConfig(request).configure(supervisions_table)

    context["supervisions_table"] = supervisions_table
    context["day"] = wanted_day
    context["supervisions"] = supervisions

    context["datepicker"] = {
        "date": date_unix(wanted_day),
        "dest": reverse("supervisions_day"),
    }

    context["url_prev"], context["url_next"] = TimePeriod.get_prev_next_by_day(
        wanted_day, "supervisions_day_by_date"
    )

    return render(request, "chronos/supervisions_day.html", context)


@never_cache
@permission_required("chronos.edit_supervision_substitution_rule")
def edit_supervision_substitution(request: HttpRequest, id_: int, week: int) -> HttpResponse:
    """View a form to edit a supervision substitution."""
    context = {}

    supervision = get_object_or_404(Supervision, pk=id_)
    wanted_week = supervision.get_calendar_week(week)
    context["week"] = week
    context["supervision"] = supervision
    date = week_weekday_to_date(wanted_week, supervision.break_item.weekday)
    context["date"] = date

    supervision_substitution = get_supervision_substitution_by_id(request, id_, date)

    if supervision_substitution:
        edit_supervision_substitution_form = SupervisionSubstitutionForm(
            request, request.POST or None, instance=supervision_substitution
        )
    else:
        edit_supervision_substitution_form = SupervisionSubstitutionForm(
            request,
            request.POST or None,
        )

    context["substitution"] = supervision_substitution

    if request.method == "POST":
        if edit_supervision_substitution_form.is_valid():
            with reversion.create_revision(atomic=True):
                tracker = TimetableDataChangeTracker()

                supervision_substitution = edit_supervision_substitution_form.save(commit=False)
                if not supervision_substitution.pk:
                    supervision_substitution.supervision = supervision
                    supervision_substitution.date = date
                supervision_substitution.save()
                edit_supervision_substitution_form.save_m2m()

                messages.success(request, _("The substitution has been saved."))

            return redirect(
                "supervisions_day_by_date", year=date.year, month=date.month, day=date.day
            )

    context["edit_supervision_substitution_form"] = edit_supervision_substitution_form

    return render(request, "chronos/edit_supervision_substitution.html", context)


@permission_required("chronos.delete_supervision_substitution_rule")
def delete_supervision_substitution(request: HttpRequest, id_: int, week: int) -> HttpResponse:
    """Delete a supervision substitution.

    Redirects back to supervision list on success.
    """
    supervision = get_object_or_404(Supervision, pk=id_)
    wanted_week = supervision.get_calendar_week(week)
    date = week_weekday_to_date(wanted_week, supervision.break_item.weekday)

    get_supervision_substitution_by_id(request, id_, date).delete()

    messages.success(request, _("The substitution has been deleted."))

    return redirect("supervisions_day_by_date", year=date.year, month=date.month, day=date.day)
