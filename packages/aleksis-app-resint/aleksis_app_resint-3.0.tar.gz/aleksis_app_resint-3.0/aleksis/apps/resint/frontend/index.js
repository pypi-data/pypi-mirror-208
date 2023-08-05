export default {
  meta: {
    inMenu: true,
    titleKey: "resint.menu_title",
    icon: "mdi-open-in-app",
    permission: "resint.view_menu_rule",
  },
  children: [
    {
      path: "",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterIndex",
      meta: {
        inMenu: true,
        titleKey: "resint.manage_posters.menu_title",
        icon: "mdi-file-upload-outline",
        permission: "resint.view_posters_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "upload/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterUpload",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: ":pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterEdit",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: ":pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterDelete",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: ":slug.pdf",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterShowCurrent",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.posterGroupList",
      meta: {
        inMenu: true,
        titleKey: "resint.poster_groups.menu_title",
        icon: "mdi-folder-multiple-outline",
        permission: "resint.view_postergroups_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.createPosterGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.editPosterGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "groups/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.deletePosterGroup",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "live/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.liveDocuments",
      meta: {
        inMenu: true,
        titleKey: "resint.live_documents.menu_title",
        icon: "mdi-update",
        permission: "resint.view_livedocuments_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "live/:app/:model/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.createLiveDocument",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "live/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.editLiveDocument",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "live_documents/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.deleteLiveDocument",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "live_documents/:slug.pdf",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.showLiveDocument",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "api/live_documents/:slug.pdf",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "resint.apiShowLiveDocument",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
