<template>
  <Dialog
    ref="dialogShelfSearch"
    title="検索条件の追加"
    :max-width="400"
    label-ok="検索"
  >
    <p>指定した条件でAND検索を行います。</p>
    <v-select label="モード" :items="modes" v-model="mode"></v-select>
    <v-text-field v-model="formSearch.q" label="フリーワード"></v-text-field>
    <v-text-field v-model="formSearch.title" label="タイトル"></v-text-field>
    <v-text-field v-model="formSearch.authors" label="著者名"></v-text-field>
    <v-text-field
      v-model="formSearch.amazon_dp"
      label="ISBN/ASIN"
      maxlength="13"
    ></v-text-field>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Dialog.vue'

export default {
  components: {
    Dialog,
  },
  data: () => ({
    mode: '',
    modes: ['あとで読む', '読んでいる本', '読んだ本', '全ての本'],
    formSearch: {
      q: '',
      title: '',
      authors: '',
      amazon_dp: '',
    },
  }),
  methods: {
    async showShelfSearch() {
      this.formSearch.q = this.$route.query.q || ''
      this.formSearch.title = this.$route.query.title || ''
      this.formSearch.authors = this.$route.query.authors || ''
      this.formSearch.amazon_dp = this.$route.query.amazon_dp || ''

      // TODO: モードの切り替えを実装する

      if (!(await this.$refs.dialogShelfSearch.showDialog())) return

      let query = { ...this.formSearch }
      for (const key in query) {
        if (!query[key]) delete query[key]
      }

      this.$router.push({
        path: this.$route.path,
        query: query,
      })
    },
  },
}
</script>
