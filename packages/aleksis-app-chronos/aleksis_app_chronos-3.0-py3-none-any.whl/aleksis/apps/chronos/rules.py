from rules import add_perm

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import LessonSubstitution
from .util.predicates import has_any_timetable_object, has_room_timetable_perm, has_timetable_perm

# View timetable overview
view_timetable_overview_predicate = has_person & (
    has_any_timetable_object | has_global_perm("chronos.view_timetable_overview")
)
add_perm("chronos.view_timetable_overview_rule", view_timetable_overview_predicate)

# View my timetable
add_perm("chronos.view_my_timetable_rule", has_person)

# View timetable
view_timetable_predicate = has_person & has_timetable_perm
add_perm("chronos.view_timetable_rule", view_timetable_predicate)

# View all lessons per day
view_lessons_day_predicate = has_person & has_global_perm("chronos.view_lessons_day")
add_perm("chronos.view_lessons_day_rule", view_lessons_day_predicate)

# Edit substition
edit_substitution_predicate = has_person & (
    has_global_perm("chronos.change_lessonsubstitution")
    | has_object_perm("chronos.change_lessonsubstitution")
)
add_perm("chronos.edit_substitution_rule", edit_substitution_predicate)

# Delete substitution
delete_substitution_predicate = has_person & (
    has_global_perm("chronos.delete_lessonsubstitution")
    | has_object_perm("chronos.delete_lessonsubstitution")
)
add_perm("chronos.delete_substitution_rule", delete_substitution_predicate)

# View substitutions
view_substitutions_predicate = has_person & (
    has_global_perm("chronos.view_lessonsubstitution")
    | has_any_object("chronos.view_lessonsubstitution", LessonSubstitution)
)
add_perm("chronos.view_substitutions_rule", view_substitutions_predicate)

# View all supervisions per day
view_supervisions_day_predicate = has_person & has_global_perm("chronos.view_supervisions_day")
add_perm("chronos.view_supervisions_day_rule", view_supervisions_day_predicate)

# Edit supervision substitution
edit_supervision_substitution_predicate = has_person & (
    has_global_perm("chronos.change_supervisionsubstitution")
)
add_perm("chronos.edit_supervision_substitution_rule", edit_supervision_substitution_predicate)

# Delete supervision substitution
delete_supervision_substitution_predicate = has_person & (
    has_global_perm("chronos.delete_supervisionsubstitution")
)
add_perm("chronos.delete_supervision_substitution_rule", delete_supervision_substitution_predicate)

# View room (timetable)
view_room_predicate = has_person & has_room_timetable_perm
add_perm("chronos.view_room_rule", view_room_predicate)
