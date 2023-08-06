from django.contrib.auth.models import User
from django.db.models import Model

from rules import predicate

from aleksis.core.models import Group, Person, Room
from aleksis.core.util.predicates import has_global_perm, has_object_perm

from .chronos_helpers import get_classes, get_rooms, get_teachers


@predicate
def has_timetable_perm(user: User, obj: Model) -> bool:
    """
    Check if can access timetable.

    Predicate which checks whether the user is allowed
    to access the requested timetable.
    """
    if isinstance(obj, Group):
        return has_group_timetable_perm(user, obj)
    elif isinstance(obj, Person):
        return has_person_timetable_perm(user, obj)
    elif isinstance(obj, Room):
        return has_room_timetable_perm(user, obj)
    else:
        return False


@predicate
def has_group_timetable_perm(user: User, obj: Group) -> bool:
    """
    Check if can access group timetable.

    Predicate which checks whether the user is allowed
    to access the requested group timetable.
    """
    return (
        obj in user.person.member_of.all()
        or user.person.primary_group == obj
        or obj in user.person.owner_of.all()
        or has_global_perm("chronos.view_all_group_timetables")(user)
        or has_object_perm("core.view_group_timetable")(user, obj)
    )


@predicate
def has_person_timetable_perm(user: User, obj: Person) -> bool:
    """
    Check if can access person timetable.

    Predicate which checks whether the user is allowed
    to access the requested person timetable.
    """
    return (
        user.person == obj
        or has_global_perm("chronos.view_all_person_timetables")(user)
        or has_object_perm("core.view_person_timetable")(user, obj)
    )


@predicate
def has_room_timetable_perm(user: User, obj: Room) -> bool:
    """
    Check if can access room timetable.

    Predicate which checks whether the user is allowed
    to access the requested room timetable.
    """
    return has_global_perm("chronos.view_all_room_timetables")(user) or has_object_perm(
        "core.view_room_timetable"
    )(user, obj)


@predicate
def has_any_timetable_object(user: User) -> bool:
    """Predicate which checks whether there are any timetables the user is allowed to access."""
    return get_classes(user).exists() or get_rooms(user).exists() or get_teachers(user).exists()
