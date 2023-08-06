export default {
  meta: {
    inMenu: true,
    titleKey: "stoelindeling.menu_title",
    icon: "mdi-view-list-outline",
    permission: "stoelindeling.view_seatingplans_rule",
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "seating_plans/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.seatingPlans",
      meta: {
        inMenu: true,
        titleKey: "stoelindeling.menu_title",
        icon: "mdi-view-list-outline",
        permission: "stoelindeling.view_seatingplans_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "seating_plans/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.createSeatingPlan",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "seating_plans/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.seatingPlan",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "seating_plans/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.editSeatingPlan",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "seating_plans/:pk/copy/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.copySeatingPlan",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "seating_plans/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "stoelindeling.deleteSeatingPlan",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
