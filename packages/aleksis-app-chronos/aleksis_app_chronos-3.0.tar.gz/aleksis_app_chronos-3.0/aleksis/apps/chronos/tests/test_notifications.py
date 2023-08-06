from datetime import date, time

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.test import TransactionTestCase, override_settings

import pytest

from aleksis.apps.chronos.models import (
    Event,
    ExtraLesson,
    Lesson,
    LessonPeriod,
    LessonSubstitution,
    Subject,
    SupervisionSubstitution,
    TimePeriod,
)
from aleksis.apps.chronos.util.change_tracker import TimetableDataChangeTracker
from aleksis.core.models import Group, Person, Room, SchoolTerm

pytestmark = pytest.mark.django_db


@override_settings(CELERY_BROKER_URL="memory://localhost//")
class NotificationTests(TransactionTestCase):
    serialized_rollback = True

    def setUp(self):
        self.school_term = SchoolTerm.objects.create(
            date_start=date(2020, 1, 1), date_end=date(2020, 12, 31)
        )

        self.teacher_a = Person.objects.create(
            first_name="Teacher", last_name="A", short_name="A", email="test@example.org"
        )
        self.teacher_b = Person.objects.create(
            first_name="Teacher", last_name="B", short_name="B", email="test@example.org"
        )

        self.student_a = Person.objects.create(
            first_name="Student", last_name="A", email="test@example.org"
        )
        self.student_b = Person.objects.create(
            first_name="Student", last_name="B", email="test@example.org"
        )
        self.student_c = Person.objects.create(
            first_name="Student", last_name="C", email="test@example.org"
        )
        self.student_d = Person.objects.create(
            first_name="Student", last_name="D", email="test@example.org"
        )
        self.student_e = Person.objects.create(
            first_name="Student", last_name="E", email="test@example.org"
        )

        self.group_a = Group.objects.create(
            name="Class 9a", short_name="9a", school_term=self.school_term
        )
        self.group_a.owners.add(self.teacher_a)
        self.group_a.members.add(self.student_a, self.student_b, self.student_c)
        self.group_b = Group.objects.create(
            name="Class 9b", short_name="9b", school_term=self.school_term
        )
        self.group_b.owners.add(self.teacher_b)
        self.group_b.members.add(self.student_c, self.student_d, self.student_e)

        self.time_period_a = TimePeriod.objects.create(
            weekday=0, period=1, time_start=time(8, 0), time_end=time(9, 0)
        )
        self.time_period_b = TimePeriod.objects.create(
            weekday=1, period=2, time_start=time(9, 0), time_end=time(10, 0)
        )

        self.subject_a = Subject.objects.create(name="English", short_name="En")
        self.subject_b = Subject.objects.create(name="Deutsch", short_name="De")

        self.room_a = Room.objects.create(short_name="004", name="Room 0.04")
        self.room_b = Room.objects.create(short_name="005", name="Room 0.05")

        self.lesson = Lesson.objects.create(subject=self.subject_a)
        self.lesson.groups.set([self.group_a])
        self.lesson.teachers.set([self.teacher_a])

        self.period_1 = LessonPeriod.objects.create(
            period=self.time_period_a, room=self.room_a, lesson=self.lesson
        )
        self.period_2 = LessonPeriod.objects.create(
            period=self.time_period_b, room=self.room_a, lesson=self.lesson
        )

    def _parse_receivers(self, receivers):
        return [str(r[1]) for r in receivers]

    def test_signal_registration(self):
        for model in [Event, LessonSubstitution, ExtraLesson, SupervisionSubstitution]:
            assert "TimetableDataChangeTracker._handle_save" not in "".join(
                [str(r) for r in post_save._live_receivers(model)]
            )

        for model in [Event, LessonSubstitution, ExtraLesson, SupervisionSubstitution]:
            assert "TimetableDataChangeTracker._handle_delete" not in "".join(
                [str(r) for r in post_delete._live_receivers(model)]
            )

        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(LessonSubstitution.teachers.through)]
        )
        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(Event.teachers.through)]
        )
        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(Event.groups.through)]
        )
        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(ExtraLesson.teachers.through)]
        )
        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(ExtraLesson.groups.through)]
        )
        assert "TimetableDataChangeTracker._handle_m2m_changed" not in "".join(
            [str(r) for r in m2m_changed._live_receivers(ExtraLesson.groups.through)]
        )

        with transaction.atomic():
            tracker = TimetableDataChangeTracker()

            for model in [Event, LessonSubstitution, ExtraLesson, SupervisionSubstitution]:
                assert "TimetableDataChangeTracker._handle_save" in "".join(
                    [str(r) for r in post_save._live_receivers(model)]
                )

            for model in [Event, LessonSubstitution, ExtraLesson, SupervisionSubstitution]:
                assert "TimetableDataChangeTracker._handle_delete" in "".join(
                    [str(r) for r in pre_delete._live_receivers(model)]
                )

            assert "TimetableDataChangeTracker._handle_m2m_changed" in "".join(
                [str(r) for r in m2m_changed._live_receivers(LessonSubstitution.teachers.through)]
            )
            assert "TimetableDataChangeTracker._handle_m2m_changed" in "".join(
                [str(r) for r in m2m_changed._live_receivers(Event.teachers.through)]
            )
            assert "TimetableDataChangeTracker._handle_m2m_changed" in "".join(
                [str(r) for r in m2m_changed._live_receivers(Event.groups.through)]
            )
            assert "TimetableDataChangeTracker._handle_m2m_changed" in "".join(
                [str(r) for r in m2m_changed._live_receivers(ExtraLesson.teachers.through)]
            )
            assert "TimetableDataChangeTracker._handle_m2m_changed" in "".join(
                [str(r) for r in m2m_changed._live_receivers(ExtraLesson.groups.through)]
            )

    def test_outside_transaction(self):
        with pytest.raises(RuntimeError):
            TimetableDataChangeTracker()

    def test_create_detection(self):
        with transaction.atomic():
            tracker = TimetableDataChangeTracker()

            assert not tracker.changes

            lesson_substitution = LessonSubstitution.objects.create(
                week=20, year=2020, lesson_period=self.period_1, cancelled=True
            )

            assert tracker.changes

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert change.created
            assert not change.deleted
            assert not change.changed_fields

            lesson_substitution.cancelled = False
            lesson_substitution.subject = self.subject_b
            lesson_substitution.save()

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert change.created
            assert not change.deleted
            assert change.changed_fields

    def test_change_detection(self):
        with transaction.atomic():
            lesson_substitution = LessonSubstitution.objects.create(
                week=20, year=2020, lesson_period=self.period_1, cancelled=True
            )

            tracker = TimetableDataChangeTracker()

            assert not tracker.changes

            lesson_substitution.cancelled = False
            lesson_substitution.subject = self.subject_b
            lesson_substitution.save()

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert not change.created
            assert not change.deleted
            assert set(change.changed_fields.keys()) == {"cancelled", "subject_id"}

            assert change.changed_fields["cancelled"]
            assert change.changed_fields["subject_id"] is None

            lesson_substitution.teachers.add(self.teacher_a)

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert not change.created
            assert not change.deleted
            assert set(change.changed_fields.keys()) == {"cancelled", "subject_id", "teachers"}

            assert change.changed_fields["teachers"] == []

            lesson_substitution.teachers.remove(self.teacher_a)

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert not change.created
            assert not change.deleted
            assert set(change.changed_fields.keys()) == {"cancelled", "subject_id", "teachers"}

            assert change.changed_fields["teachers"] == []

        with transaction.atomic():
            lesson_substitution.teachers.add(self.teacher_a)

            tracker = TimetableDataChangeTracker()

            lesson_substitution.teachers.remove(self.teacher_a)

            assert len(tracker.changes) == 1
            change = tracker.changes[tracker.get_instance_key(lesson_substitution)]
            assert change.instance == lesson_substitution
            assert not change.created
            assert not change.deleted
            assert set(change.changed_fields.keys()) == {"teachers"}

            assert change.changed_fields["teachers"] == [self.teacher_a]

    def test_delete_detected(self):
        lesson_substitution = LessonSubstitution.objects.create(
            week=20, year=2020, lesson_period=self.period_1, cancelled=True
        )

        with transaction.atomic():
            tracker = TimetableDataChangeTracker()

            pk = lesson_substitution.pk

            assert not tracker.changes

            lesson_substitution.delete()

            assert len(tracker.changes) == 1
            change = tracker.changes[f"lessonsubstitution_{pk}"]
            assert change.instance == lesson_substitution
            assert not change.created
            assert change.deleted
            assert not change.changed_fields
