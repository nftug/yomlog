<template>
  <v-tabs v-model="selectedTab" centered>
    <v-tab v-for="(tab, index) in tabs" :key="index" :to="tab.path">
      {{ tab.label }}
    </v-tab>

    <v-tab v-if="search" :to="`/shelf/search/?q=${encodeURI(search)}`">
      検索
    </v-tab>
  </v-tabs>
</template>

<script>
export default {
  props: {
    search: String,
  },
  data: () => ({
    selectedTab: null,
    tabs: [
      {
        label: 'あとで読む',
        path: '/shelf/to_be_read',
        isShow: true,
      },
      {
        label: '読んでいる本',
        path: '/shelf/reading',
        isShow: true,
      },
      {
        label: '読んだ本',
        path: '/shelf/read',
        isShow: true,
      },
    ],
  }),
}
</script>
