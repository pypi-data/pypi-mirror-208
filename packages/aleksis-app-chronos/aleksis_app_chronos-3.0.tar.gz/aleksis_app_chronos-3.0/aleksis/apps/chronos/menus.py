from django.utils.translation import gettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Timetables"),
            "url": "#",
            "svg_icon": "mdi:school-outline",
            "root": True,
            "validators": [
                "menu_generator.validators.is_authenticated",
                "aleksis.core.util.core_helpers.has_person",
            ],
            "submenu": [
                {
                    "name": _("My timetable"),
                    "url": "my_timetable",
                    "svg_icon": "mdi:account-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "chronos.view_my_timetable_rule",
                        ),
                    ],
                },
                {
                    "name": _("All timetables"),
                    "url": "all_timetables",
                    "svg_icon": "mdi:grid",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "chronos.view_timetable_overview_rule",
                        ),
                    ],
                },
                {
                    "name": _("Daily lessons"),
                    "url": "lessons_day",
                    "svg_icon": "mdi:calendar-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "chronos.view_lessons_day_rule",
                        ),
                    ],
                },
                {
                    "name": _("Daily supervisions"),
                    "url": "supervisions_day",
                    "svg_icon": "mdi:calendar-outline",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "chronos.view_supervisions_day_rule",
                        ),
                    ],
                },
                {
                    "name": _("Substitutions"),
                    "url": "substitutions",
                    "svg_icon": "mdi:update",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "chronos.view_substitutions_rule",
                        ),
                    ],
                },
            ],
        }
    ]
}
