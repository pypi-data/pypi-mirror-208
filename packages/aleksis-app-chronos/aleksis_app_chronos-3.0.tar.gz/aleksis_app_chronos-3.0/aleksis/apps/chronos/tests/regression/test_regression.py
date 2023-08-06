from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from aleksis.apps.chronos.util.chronos_helpers import get_rooms, get_teachers
from aleksis.core.models import Group, Person, Room, SchoolTerm

pytestmark = pytest.mark.django_db


from aleksis.apps.chronos.models import Lesson, LessonPeriod, Subject, TimePeriod, ValidityRange


def test_rooms_teachers_only_from_current_school_term():
    User = get_user_model()

    user = User.objects.create(username="test", is_staff=True, is_superuser=True)
    person_user = Person.objects.create(user=user, first_name="Test", last_name="User")

    correct_school_term = SchoolTerm.objects.create(
        date_start=timezone.now() - timedelta(days=1),
        date_end=timezone.now() + timedelta(days=1),
        name="Correct school term",
    )
    wrong_school_term = SchoolTerm.objects.create(
        date_start=timezone.now() - timedelta(days=3),
        date_end=timezone.now() - timedelta(days=2),
        name="Wrong school term",
    )

    correct_validity = ValidityRange.objects.create(
        school_term=correct_school_term,
        date_start=correct_school_term.date_start,
        date_end=correct_school_term.date_end,
        name="Correct validity",
    )
    wrong_validity = ValidityRange.objects.create(
        school_term=wrong_school_term,
        date_start=wrong_school_term.date_start,
        date_end=wrong_school_term.date_end,
        name="Wrong validity",
    )

    subject = Subject.objects.create(name="Test subject", short_name="TS")
    time_period = TimePeriod.objects.create(
        weekday=0, period=1, time_start=time(8, 0), time_end=time(9, 0)
    )

    correct_person = Person.objects.create(first_name="Correct", last_name="Person")
    wrong_person = Person.objects.create(first_name="Wrong", last_name="Person")

    correct_lesson = Lesson.objects.create(validity=correct_validity, subject=subject)
    correct_lesson.teachers.add(correct_person)
    wrong_lesson = Lesson.objects.create(validity=wrong_validity, subject=subject)
    wrong_lesson.teachers.add(wrong_person)

    correct_room = Room.objects.create(name="Correct room", short_name="cr")
    wrong_room = Room.objects.create(name="Wrong room", short_name="wr")

    correct_lesson_period = LessonPeriod.objects.create(
        lesson=correct_lesson, period=time_period, room=correct_room
    )
    wrong_lesson_period = LessonPeriod.objects.create(
        lesson=wrong_lesson, period=time_period, room=wrong_room
    )

    rooms = get_rooms(user)
    assert correct_room in rooms
    assert wrong_room not in rooms

    teachers = get_teachers(user)
    assert correct_person in teachers
    assert wrong_person not in teachers
