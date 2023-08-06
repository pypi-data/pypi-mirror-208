from typing import Any, Optional

import django.apps
from django.db import transaction

from reversion.signals import post_revision_commit

from aleksis.core.util.apps import AppConfig


class ChronosConfig(AppConfig):
    name = "aleksis.apps.chronos"
    verbose_name = "AlekSIS — Chronos (Timetables)"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-Chronos/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2018, 2019, 2020, 2021, 2022], "Jonathan Weth", "wethjo@katharineum.de"),
        ([2018, 2019], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2019, 2020, 2022], "Dominik George", "dominik.george@teckids.org"),
        ([2019, 2021], "Hangzhi Yu", "yuha@katharineum.de"),
        ([2019], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2019], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2021], "Lloyd Meins", "meinsll@katharineum.de"),
    )

    def ready(self):
        super().ready()

        from .util.change_tracker import handle_new_revision  # noqa

        def _handle_post_revision_commit(sender, revision, versions, **kwargs):
            """Handle a new post revision commit signal in background."""
            transaction.on_commit(lambda: handle_new_revision.delay(revision.pk))

        post_revision_commit.connect(_handle_post_revision_commit, weak=False)

    def _ensure_notification_task(self):
        """Update or create the task for sending notifications."""
        from django.conf import settings  # noqa

        from celery import schedules
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        from aleksis.core.util.core_helpers import get_site_preferences

        time_for_sending = get_site_preferences()["chronos__time_for_sending_notifications"]
        active = get_site_preferences()["chronos__send_notifications_site"]

        if active:
            schedule = schedules.crontab(
                minute=str(time_for_sending.minute), hour=str(time_for_sending.hour)
            )
            schedule = CrontabSchedule.from_schedule(schedule)
            schedule.timezone = settings.TIME_ZONE
            schedule.save()

        possible_periodic_tasks = PeriodicTask.objects.filter(
            task="chronos_send_notifications_for_next_day"
        )

        if not active:
            possible_periodic_tasks.delete()

        elif possible_periodic_tasks.exists():
            task = possible_periodic_tasks[0]
            for d_task in possible_periodic_tasks:
                if d_task != task:
                    d_task.delete()

            if task.crontab != schedule:
                task.interval, task.solar, task.clocked = None, None, None
                task.crontab = schedule
                task.save()

        elif active:
            PeriodicTask.objects.get_or_create(
                task="chronos_send_notifications_for_next_day",
                crontab=schedule,
                defaults=dict(name="Send notifications for next day (automatic schedule)"),
            )

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        if section == "chronos" and name in (
            "send_notifications_site",
            "time_for_sending_notifications",
        ):
            self._ensure_notification_task()

    def post_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        **kwargs,
    ) -> None:
        super().post_migrate(app_config, verbosity, interactive, using, **kwargs)
        # Ensure that the notification task is created after setting up AlekSIS
        self._ensure_notification_task()
