<template>
  <div class="pb-4">
    <v-card class="mx-auto text-body-2" outlined>
      <div class="ma-4">
        <strong>{{ total }}冊</strong>
        の本が見つかりました。
      </div>
      <div class="ma-4">
        <v-icon>mdi-magnify</v-icon>
        <v-chip
          class="ma-1"
          v-for="(q, key) in query"
          :key="key"
          close
          small
          @click:close="removeQuery(key)"
        >
          {{ key | searchLabel }}
          {{ q }}
        </v-chip>

        <SearchDialog :type="type" :hash="`search-${type}`">
          <template #activator="{ on, attrs }">
            <v-btn small class="ma-1" icon v-on="on" v-bind="attrs">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </SearchDialog>
      </div>
    </v-card>
  </div>
</template>

<script>
import SearchDialog from '@/components/SearchDialog.vue'

export default {
  props: {
    total: { type: Number, require: true },
    type: { type: String, require: true },
  },
  data: () => ({
    query: {},
  }),
  components: {
    SearchDialog,
  },
  watch: {
    '$route.query'() {
      this.query = { ...this.$route.query }
      delete this.query.page
    },
  },
  filters: {
    searchLabel(key) {
      const keyName = key.replace(/_or$/, '')
      const or = keyName !== key
      let label

      if (keyName === 'title') {
        label = '書名'
      } else if (keyName === 'authors') {
        label = '著者名'
      } else if (keyName === 'amazon_dp') {
        label = 'ISBN/ASIN'
      } else if (keyName === 'content') {
        label = '内容'
      } else if (keyName === 'quote_text') {
        label = '引用'
      } else {
        label = ''
      }

      if (or) {
        label += `${label ? ' (OR)' : 'OR'}`
      }

      return `${label}${label ? ':' : ''}`
    },
  },
  methods: {
    removeQuery(key, query = this.query) {
      if (key) {
        delete query[key]
      } else {
        query = {}
      }

      // OR検索だけになったらAND検索に置換
      const keys = Object.keys(query)
      const hasAnd = keys.some((e) => e.match(/^(?!.*_or).*$/) !== null)

      if (!hasAnd) {
        query = {}
        keys.forEach((key) => {
          const value = this.query[key]
          const keyName = key.replace(/_or$/, '')
          query[keyName] = value
        })
      }

      this.$router.push({
        path: this.$route.path,
        query,
      })
    },
  },
}
</script>
