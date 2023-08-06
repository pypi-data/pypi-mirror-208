import {
  notLoggedInValidator,
  hasPersonValidator,
} from "aleksis.core/routeValidators";

export default {
  meta: {
    inMenu: true,
    titleKey: "alsijil.menu_title",
    icon: "mdi-account-group-outline",
    validators: [hasPersonValidator],
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "lesson",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.lessonPeriod",
      meta: {
        inMenu: true,
        titleKey: "alsijil.lesson.menu_title",
        icon: "mdi-alarm",
        permission: "alsijil.view_lesson_menu_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "lesson/:year(\\d+)/:week(\\d+)/:id_(\\d+)",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.lessonPeriodByCWAndID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "extra_lesson/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.extraLessonByID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "event/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.eventByID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekView",
      meta: {
        inMenu: true,
        titleKey: "alsijil.week.menu_title",
        icon: "mdi-view-week-outline",
        permission: "alsijil.view_week_menu_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/:year(\\d+)/:week(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekViewByWeek",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/year/cw/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekViewPlaceholders",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/:type_/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekViewByTypeAndID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/year/cw/:type_/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekViewPlaceholdersByTypeAndID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "week/:year(\\d+)/:week(\\d+)/:type_/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.weekViewByWeekTypeAndID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "print/group/:id_(\\d+)",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.fullRegisterGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.myGroups",
      meta: {
        inMenu: true,
        titleKey: "alsijil.groups.menu_title",
        icon: "mdi-account-multiple-outline",
        permission: "alsijil.view_my_groups_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.studentsList",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "persons/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.myStudents",
      meta: {
        inMenu: true,
        titleKey: "alsijil.persons.menu_title",
        icon: "mdi-account-school-outline",
        permission: "alsijil.view_my_students_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "persons/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.overviewPerson",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "me/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.overviewMe",
      meta: {
        inMenu: true,
        titleKey: "alsijil.my_overview.menu_title",
        icon: "mdi-chart-box-outline",
        permission: "alsijil.view_person_overview_menu_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "notes/:pk(\\d+)/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.deletePersonalNote",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "absence/new/:id_(\\d+)/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.registerAbsenceWithID",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "absence/new/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.registerAbsence",
      meta: {
        inMenu: true,
        titleKey: "alsijil.absence.menu_title",
        icon: "mdi-message-alert-outline",
        permission: "alsijil.view_register_absence_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "extra_marks/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.extraMarks",
      meta: {
        inMenu: true,
        titleKey: "alsijil.extra_marks.menu_title",
        icon: "mdi-label-variant-outline",
        permission: "alsijil.view_extramarks_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "extra_marks/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.createExtraMark",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "extra_marks/:pk(\\d+)/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.editExtraMark",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "extra_marks/:pk(\\d+)/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.deleteExtraMark",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "excuse_types/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.excuseTypes",
      meta: {
        inMenu: true,
        titleKey: "alsijil.excuse_types.menu_title",
        icon: "mdi-label-outline",
        permission: "alsijil.view_excusetypes_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "excuse_types/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.createExcuseType",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "excuse_types/:pk(\\d+)/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.editExcuseType",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "excuse_types/:pk(\\d+)/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.deleteExcuseType",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.groupRoles",
      meta: {
        inMenu: true,
        titleKey: "alsijil.group_roles.menu_title_manage",
        icon: "mdi-clipboard-plus-outline",
        permission: "alsijil.view_grouproles_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.createGroupRole",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/:pk(\\d+)/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.editGroupRole",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/:pk(\\d+)/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.deleteGroupRole",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk(\\d+)/group_roles/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.assignedGroupRoles",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk(\\d+)/group_roles/assign/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.assignGroupRole",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk(\\d+)/group_roles/:role_pk(\\d+)/assign/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.assignGroupRoleByRolePK",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/assignments/:pk(\\d+)/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.editGroupRoleAssignment",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/assignments/:pk(\\d+)/stop/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.stopGroupRoleAssignment",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/assignments/:pk(\\d+)/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.deleteGroupRoleAssignment",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "group_roles/assignments/assign/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.assignGroupRoleMultiple",
      meta: {
        inMenu: true,
        titleKey: "alsijil.group_roles.menu_title_assign",
        icon: "mdi-clipboard-account-outline",
        permission: "alsijil.assign_grouprole_for_multiple_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "all/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "alsijil.allRegisterObjects",
      meta: {
        inMenu: true,
        titleKey: "alsijil.all_lessons.menu_title",
        icon: "mdi-format-list-text",
        permission: "alsijil.view_register_objects_list_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
