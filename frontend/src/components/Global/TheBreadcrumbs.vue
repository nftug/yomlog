<template>
  <v-toolbar v-if="items.length > 1" flat dense color="grey lighten-3">
    <v-breadcrumbs :items="items" class="breadcrumbs">
      <template #item="{ item }">
        <v-breadcrumbs-item :to="item.to" :disabled="item.disabled" exact>
          {{ item.text }}
        </v-breadcrumbs-item>
      </template>
    </v-breadcrumbs>
  </v-toolbar>
</template>

<script>
export default {
  computed: {
    items() {
      return this.$breadcrumbs.map((crumb, i) => {
        return {
          text: this.getBreadcrumb(crumb.meta.breadcrumb),
          disabled: this.$breadcrumbs.length - 1 === i,
          to: this.getRoute(crumb),
        }
      })
    },
  },
  methods: {
    getBreadcrumb(name) {
      if (typeof name === 'function') {
        name = name.call(this, this.$route.params)
      }
      if (typeof name === 'object') {
        name = name.label
      }
      return name
    },
    getRoute(crumb) {
      const { name } = crumb
      const getQuery = this.$store.getters['parentRoutes/query']
      const getParams = this.$store.getters['parentRoutes/params']

      let params = getParams(name)
      if (!Object.keys(params).length) {
        params = { state: 'all' }
      }

      return { name, query: getQuery(name), params }
    },
  },
}
</script>
