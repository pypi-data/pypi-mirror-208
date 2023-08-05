export default {
  name: "csv",
  path: "#",
  component: () => import("aleksis.core/components/Parent.vue"),
  meta: {
    inMenu: true,
    titleKey: "csv.menu_title",
    icon: "mdi-swap-vertical",
    permission: "csv_import.view_csv_menu_rule",
  },
  children: [
    {
      path: "import/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "csv.csvImport",
      meta: {
        inMenu: true,
        titleKey: "csv.import.menu_title",
        icon: "mdi-table-arrow-left",
        permission: "csv_import.import_data_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "templates/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "csv.importTemplates",
      meta: {
        inMenu: true,
        titleKey: "csv.import_template.menu_title",
        icon: "mdi-table-cog",
        permission: "csv_import.view_importtemplate_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "templates/upload/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "csv.uploadImportTemplate",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
