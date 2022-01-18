<template>
  <v-tabs v-model="selectedTab" centered>
    <v-tab
      v-for="(tab, index) in tabs"
      :key="index"
      :to="URIWithQuery(tab.path)"
    >
      {{ tab.label }}
    </v-tab>
  </v-tabs>
</template>

<script>
export default {
  data: () => ({
    selectedTab: null,
    tabs: [
      {
        label: 'あとで読む',
        path: '/book/to_be_read',
        isShow: true,
      },
      {
        label: '読んでいる本',
        path: '/book/reading',
        isShow: true,
      },
      {
        label: '読んだ本',
        path: '/book/read',
        isShow: true,
      },
      {
        label: '全ての本',
        path: '/book/all',
        isShow: true,
      },
    ],
    authors: '',
  }),
  computed: {
    URIWithQuery() {
      return function (path) {
        if (path === this.$route.path) {
          return {
            path: path,
            query: this.$route.query,
          }
        } else {
          return path
        }
      }
    },
  },
}
</script>
