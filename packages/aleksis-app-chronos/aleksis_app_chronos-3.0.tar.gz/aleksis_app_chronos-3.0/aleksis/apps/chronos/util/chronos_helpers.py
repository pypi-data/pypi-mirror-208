from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from guardian.core import ObjectPermissionChecker

from aleksis.core.models import Announcement, Group, Person, Room, SchoolTerm
from aleksis.core.util.core_helpers import get_site_preferences
from aleksis.core.util.predicates import check_global_permission

from ..managers import TimetableType
from ..models import (
    Absence,
    LessonPeriod,
    LessonSubstitution,
    Supervision,
    SupervisionSubstitution,
    TimePeriod,
)
from .build import build_substitutions_list
from .js import date_unix

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa


def get_el_by_pk(
    request: HttpRequest,
    type_: str,
    pk: int,
    year: Optional[int] = None,
    week: Optional[int] = None,
    regular: Optional[str] = None,
    prefetch: bool = False,
    *args,
    **kwargs,
):
    if type_ == TimetableType.GROUP.value:
        return get_object_or_404(
            Group.objects.prefetch_related("owners", "parent_groups") if prefetch else Group,
            pk=pk,
        )
    elif type_ == TimetableType.TEACHER.value:
        return get_object_or_404(Person, pk=pk)
    elif type_ == TimetableType.ROOM.value:
        return get_object_or_404(Room, pk=pk)
    else:
        return HttpResponseNotFound()


def get_substitution_by_id(request: HttpRequest, id_: int, week: int):
    lesson_period = get_object_or_404(LessonPeriod, pk=id_)
    wanted_week = lesson_period.lesson.get_calendar_week(week)

    return LessonSubstitution.objects.filter(
        week=wanted_week.week, year=wanted_week.year, lesson_period=lesson_period
    ).first()


def get_supervision_substitution_by_id(request: HttpRequest, id_: int, date: datetime.date):
    supervision = get_object_or_404(Supervision, pk=id_)

    return SupervisionSubstitution.objects.filter(date=date, supervision=supervision).first()


def get_teachers(user: "User"):
    """Get the teachers whose timetables are allowed to be seen by current user."""
    checker = ObjectPermissionChecker(user)

    school_term = SchoolTerm.current
    school_term_q = Q(lessons_as_teacher__validity__school_term=school_term) if school_term else Q()
    teachers = (
        Person.objects.annotate(lessons_count=Count("lessons_as_teacher", filter=school_term_q))
        .filter(lessons_count__gt=0)
        .order_by("short_name", "last_name")
    )

    if not check_global_permission(user, "chronos.view_all_person_timetables"):
        checker.prefetch_perms(teachers)

        wanted_teachers = set()

        for teacher in teachers:
            if checker.has_perm("core.view_person_timetable", teacher):
                wanted_teachers.add(teacher.pk)

        teachers = teachers.filter(Q(pk=user.person.pk) | Q(pk__in=wanted_teachers))

    return teachers


def get_classes(user: "User"):
    """Get the classes whose timetables are allowed to be seen by current user."""
    checker = ObjectPermissionChecker(user)

    classes = (
        Group.objects.for_current_school_term_or_all()
        .annotate(
            lessons_count=Count("lessons"),
            child_lessons_count=Count("child_groups__lessons"),
        )
        .filter(
            Q(lessons_count__gt=0, parent_groups=None)
            | Q(child_lessons_count__gt=0, parent_groups=None)
        )
        .order_by("short_name", "name")
    )

    if not check_global_permission(user, "chronos.view_all_group_timetables"):
        checker.prefetch_perms(classes)

        wanted_classes = set()

        for _class in classes:
            if checker.has_perm("core.view_group_timetable", _class):
                wanted_classes.add(_class.pk)

        classes = classes.filter(
            Q(pk__in=wanted_classes) | Q(members=user.person) | Q(owners=user.person)
        )
        if user.person.primary_group:
            classes = classes.filter(Q(pk=user.person.primary_group.pk))

    return classes


def get_rooms(user: "User"):
    """Get the rooms whose timetables are allowed to be seen by current user."""
    checker = ObjectPermissionChecker(user)

    school_term = SchoolTerm.current
    school_term_q = (
        Q(lesson_periods__lesson__validity__school_term=school_term) if school_term else Q()
    )

    rooms = (
        Room.objects.annotate(lessons_count=Count("lesson_periods", filter=school_term_q))
        .filter(lessons_count__gt=0)
        .order_by("short_name", "name")
    )

    if not check_global_permission(user, "chronos.view_all_room_timetables"):
        checker.prefetch_perms(rooms)

        wanted_rooms = set()

        for room in rooms:
            if checker.has_perm("core.view_room_timetable", room):
                wanted_rooms.add(room.pk)

        rooms = rooms.filter(Q(pk__in=wanted_rooms))

    return rooms


def get_substitutions_context_data(
    request: Optional[HttpRequest] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    is_print: bool = False,
    number_of_days: Optional[int] = None,
    show_header_box: Optional[bool] = None,
):
    """Get context data for the substitutions table."""
    context = {}

    if day:
        wanted_day = timezone.datetime(year=year, month=month, day=day).date()
        wanted_day = TimePeriod.get_next_relevant_day(wanted_day)
    else:
        wanted_day = TimePeriod.get_next_relevant_day(timezone.now().date(), timezone.now().time())

    day_number = (
        number_of_days or get_site_preferences()["chronos__substitutions_print_number_of_days"]
    )
    show_header_box = (
        show_header_box
        if show_header_box is not None
        else get_site_preferences()["chronos__substitutions_show_header_box"]
    )
    day_contexts = {}

    if is_print:
        next_day = wanted_day
        for i in range(day_number):
            day_contexts[next_day] = {"day": next_day}
            next_day = TimePeriod.get_next_relevant_day(next_day + timedelta(days=1))
    else:
        day_contexts = {wanted_day: {"day": wanted_day}}

    for day in day_contexts:
        subs = build_substitutions_list(day)
        day_contexts[day]["substitutions"] = subs

        day_contexts[day]["announcements"] = (
            Announcement.for_timetables().on_date(day).filter(show_in_timetables=True)
        )

        if show_header_box:
            subs = LessonSubstitution.objects.on_day(day).order_by(
                "lesson_period__lesson__groups", "lesson_period__period"
            )
            absences = Absence.objects.on_day(day)
            day_contexts[day]["absent_teachers"] = absences.absent_teachers()
            day_contexts[day]["absent_groups"] = absences.absent_groups()
            day_contexts[day]["affected_teachers"] = subs.affected_teachers()
            affected_groups = subs.affected_groups()
            if get_site_preferences()["chronos__affected_groups_parent_groups"]:
                groups_with_parent_groups = affected_groups.filter(parent_groups__isnull=False)
                groups_without_parent_groups = affected_groups.filter(parent_groups__isnull=True)
                affected_groups = Group.objects.filter(
                    Q(child_groups__pk__in=groups_with_parent_groups.values_list("pk", flat=True))
                    | Q(pk__in=groups_without_parent_groups.values_list("pk", flat=True))
                ).distinct()
            day_contexts[day]["affected_groups"] = affected_groups

    if not is_print:
        context = day_contexts[wanted_day]
        context["datepicker"] = {
            "date": date_unix(wanted_day),
            "dest": reverse("substitutions"),
        }

        context["url_prev"], context["url_next"] = TimePeriod.get_prev_next_by_day(
            wanted_day, "substitutions_by_date"
        )

    else:
        context["days"] = day_contexts

    return context
