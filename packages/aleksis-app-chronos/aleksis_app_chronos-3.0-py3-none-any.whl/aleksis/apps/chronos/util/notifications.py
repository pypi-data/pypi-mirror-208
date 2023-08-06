import zoneinfo
from datetime import datetime, timedelta
from typing import Union
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from aleksis.core.models import Notification, Person
from aleksis.core.util.core_helpers import get_site_preferences

from ..models import Event, ExtraLesson, LessonSubstitution, SupervisionSubstitution


def send_notifications_for_object(
    instance: Union[ExtraLesson, LessonSubstitution, Event, SupervisionSubstitution]
):
    """Send notifications for a change object."""
    recipients = []
    if isinstance(instance, LessonSubstitution):
        recipients += instance.lesson_period.lesson.teachers.all()
        recipients += instance.teachers.all()
        recipients += Person.objects.filter(
            member_of__in=instance.lesson_period.lesson.groups.all()
        )
    elif isinstance(instance, Event):
        recipients += instance.teachers.all()
        recipients += Person.objects.filter(member_of__in=instance.groups.all())
    elif isinstance(instance, ExtraLesson):
        recipients += instance.teachers.all()
        recipients += Person.objects.filter(member_of__in=instance.groups.all())
    elif isinstance(instance, SupervisionSubstitution):
        recipients.append(instance.teacher)
        recipients.append(instance.supervision.teacher)

    description = ""
    if isinstance(instance, LessonSubstitution):
        # Date, lesson, subject
        subject = instance.lesson_period.lesson.subject
        day = instance.date
        period = instance.lesson_period.period

        if instance.cancelled:
            description += (
                _(
                    "The {subject} lesson in the {period}. period on {day} has been cancelled."
                ).format(subject=subject.name, period=period.period, day=date_format(day))
                + " "
            )
        else:
            description += (
                _(
                    "The {subject} lesson in the {period}. period "
                    "on {day} has some current changes."
                ).format(subject=subject.name, period=period.period, day=date_format(day))
                + " "
            )

            if instance.teachers.all():
                description += (
                    ngettext(
                        "The teacher {old} is substituted by {new}.",
                        "The teachers {old} are substituted by {new}.",
                        instance.teachers.count(),
                    ).format(
                        old=instance.lesson_period.lesson.teacher_names,
                        new=instance.teacher_names,
                    )
                    + " "
                )

            if instance.subject:
                description += (
                    _("The subject is changed to {subject}.").format(subject=instance.subject.name)
                    + " "
                )

            if instance.room:
                description += (
                    _("The lesson is moved from {old} to {new}.").format(
                        old=instance.lesson_period.room.name,
                        new=instance.room.name,
                    )
                    + " "
                )

        if instance.comment:
            description += (
                _("There is an additional comment: {comment}.").format(comment=instance.comment)
                + " "
            )

    elif isinstance(instance, Event):
        if instance.date_start != instance.date_end:
            description += (
                _(
                    "There is an event that starts on {date_start}, {period_from}. period "
                    "and ends on {date_end}, {period_to}. period:"
                ).format(
                    date_start=date_format(instance.date_start),
                    date_end=date_format(instance.date_end),
                    period_from=instance.period_from.period,
                    period_to=instance.period_to.period,
                )
                + "\n"
            )
        else:
            description += (
                _(
                    "There is an event on {date} from the "
                    "{period_from}. period to the {period_to}. period:"
                ).format(
                    date=date_format(instance.date_start),
                    period_from=instance.period_from.period,
                    period_to=instance.period_to.period,
                )
                + "\n"
            )

        if instance.groups.all():
            description += _("Groups: {groups}").format(groups=instance.group_names) + "\n"
        if instance.teachers.all():
            description += _("Teachers: {teachers}").format(teachers=instance.teacher_names) + "\n"
        if instance.rooms.all():
            description += (
                _("Rooms: {rooms}").format(
                    rooms=", ".join([room.name for room in instance.rooms.all()])
                )
                + "\n"
            )
    elif isinstance(instance, ExtraLesson):
        description += (
            _("There is an extra lesson on {date} in the {period}. period:").format(
                date=date_format(instance.date),
                period=instance.period.period,
            )
            + "\n"
        )

        if instance.groups.all():
            description += _("Groups: {groups}").format(groups=instance.group_names) + "\n"
        if instance.room:
            description += _("Subject: {subject}").format(subject=instance.subject.name) + "\n"
        if instance.teachers.all():
            description += _("Teachers: {teachers}").format(teachers=instance.teacher_names) + "\n"
        if instance.room:
            description += _("Room: {room}").format(room=instance.room.name) + "\n"
        if instance.comment:
            description += _("Comment: {comment}.").format(comment=instance.comment) + "\n"
    elif isinstance(instance, SupervisionSubstitution):
        description += _(
            "The supervision of {old} on {date} between the {period_from}. period "
            "and the {period_to}. period in the area {area} is substituted by {new}."
        ).format(
            old=instance.supervision.teacher.full_name,
            date=date_format(instance.date),
            period_from=instance.supervision.break_item.after_period_number,
            period_to=instance.supervision.break_item.before_period_number,
            area=instance.supervision.area.name,
            new=instance.teacher.full_name,
        )

    day = instance.date if hasattr(instance, "date") else instance.date_start

    url = urljoin(
        settings.BASE_URL,
        reverse(
            "my_timetable_by_date",
            args=[day.year, day.month, day.day],
        ),
    )

    dt_start, dt_end = instance.time_range
    dt_start = dt_start.replace(tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))
    dt_end = dt_end.replace(tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))

    send_time = get_site_preferences()["chronos__time_for_sending_notifications"]
    number_of_days = get_site_preferences()["chronos__days_in_advance_notifications"]

    start_range = timezone.now().replace(hour=send_time.hour, minute=send_time.minute)
    if timezone.now().time() > send_time:
        start_range = start_range - timedelta(days=1)
    end_range = start_range + timedelta(days=number_of_days)

    if dt_start < start_range and dt_end < end_range:
        # Skip this, because the change is in the past
        return

    if dt_start <= end_range and dt_end >= start_range:
        # Send immediately
        send_at = timezone.now()
    else:
        # Schedule for later
        send_at = datetime.combine(
            dt_start.date() - timedelta(days=number_of_days), send_time
        ).replace(tzinfo=zoneinfo.ZoneInfo(settings.TIME_ZONE))

    for recipient in recipients:
        if recipient.preferences["chronos__send_notifications"]:
            n = Notification(
                recipient=recipient,
                sender=_("Timetable"),
                title=_("There are current changes to your timetable."),
                description=description,
                link=url,
                send_at=send_at,
            )
            n.save()
