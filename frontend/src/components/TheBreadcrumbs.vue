<template>
  <v-breadcrumbs v-if="items.length > 1" :items="items" class="breadcrumbs">
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item :to="item.to" :disabled="item.disabled" exact>
        {{ item.text }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script>
export default {
  computed: {
    items() {
      return this.$breadcrumbs.map((crumb, i) => {
        return {
          text: this.getBreadcrumb(crumb.meta.breadcrumb),
          disabled: this.$breadcrumbs.length - 1 === i,
          to: this.getPath(crumb),
        }
      })
    },
  },
  methods: {
    getBreadcrumb(bc) {
      let name = bc
      if (typeof name === 'function') {
        name = name.call(this, this.$route.params)
      }
      if (typeof name === 'object') {
        name = name.label
      }
      return name
    },
    getPath(crumb) {
      let { path } = crumb
      for (const [key, value] of Object.entries(this.$route.params)) {
        path = path.replace(`:${key}`, value)
      }
      return path
    },
  },
}
</script>

<style scoped>
.breadcrumbs {
  padding-bottom: 0px !important;
}
</style>
