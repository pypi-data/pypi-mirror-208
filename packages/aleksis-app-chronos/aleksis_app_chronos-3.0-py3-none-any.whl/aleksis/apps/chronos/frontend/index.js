import { hasPersonValidator } from "aleksis.core/routeValidators";

export default {
  meta: {
    inMenu: true,
    titleKey: "chronos.menu_title",
    icon: "mdi-school-outline",
    validators: [hasPersonValidator],
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.allTimetables",
      meta: {
        inMenu: true,
        titleKey: "chronos.timetable.menu_title_all",
        icon: "mdi-grid",
        permission: "chronos.view_timetable_overview_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/my/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.myTimetable",
      meta: {
        inMenu: true,
        titleKey: "chronos.timetable.menu_title_my",
        icon: "mdi-account-outline",
        permission: "chronos.view_my_timetable_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/my/:year/:month/:day/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.myTimetableByDate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/:type_/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.timetable",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/:type_/:pk/:year/:week/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.timetableByWeek",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/:type_/:pk/print/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.timetablePrint",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "timetable/:type_/:pk/:regular/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.timetableRegular",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "lessons/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.lessonsDay",
      meta: {
        inMenu: true,
        titleKey: "chronos.lessons.menu_title_daily",
        icon: "mdi-calendar-outline",
        permission: "chronos.view_lessons_day_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "lessons/:year/:month/:day/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.lessonsDayByDate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "lessons/:id_/:week/substitution/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.editSubstitution",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "lessons/:id_/:week/substitution/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.deleteSubstitution",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "substitutions/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.substitutions",
      meta: {
        inMenu: true,
        titleKey: "chronos.substitutions.menu_title",
        icon: "mdi-update",
        permission: "chronos.view_substitutions_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "substitutions/print/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.substitutionsPrint",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "substitutions/:year/:month/:day/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.substitutionsByDate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "substitutions/:year/:month/:day/print/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.substitutionsPrintByDate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "supervisions/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.supervisionsDay",
      meta: {
        inMenu: true,
        titleKey: "chronos.supervisions.menu_title_daily",
        icon: "mdi-calendar-outline",
        permission: "chronos.view_supervisions_day_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "supervisions/:year/:month/:day/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.supervisionsDayByDate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "supervisions/:id_/:week/substitution/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.editSupervisionSubstitution",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "supervisions/:id_/:week/substitution/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "chronos.deleteSupervisionSubstitution",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
