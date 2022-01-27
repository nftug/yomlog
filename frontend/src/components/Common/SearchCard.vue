<template>
  <div class="pb-4">
    <v-card class="mx-auto text-body-2">
      <div class="pa-2">
        <div class="ma-4">
          <slot :total="total">
            <strong>{{ total }}冊</strong>
            の本が見つかりました。
          </slot>
        </div>
        <div class="ma-4">
          <SearchDialog :type="type" :hash="`search-${type}`" :book-id="bookId">
            <template #activator="{ on: { click } }">
              <v-btn
                dark
                color="indigo"
                :small="!isXSmallButton"
                :x-small="isXSmallButton"
                :fab="isXSmallButton"
                elevation="1"
                class="ma-1"
                @click="click"
              >
                <template v-if="isXSmallButton">
                  <v-icon>mdi-magnify-plus-outline</v-icon>
                </template>
                <template v-else>
                  <v-icon left>mdi-magnify-plus-outline</v-icon>
                  検索
                </template>
              </v-btn>
            </template>
          </SearchDialog>

          <v-btn
            v-if="hasQuery"
            dark
            color="red"
            :small="!isXSmallButton"
            :x-small="isXSmallButton"
            :fab="isXSmallButton"
            elevation="1"
            class="ma-1"
            @click="removeQuery()"
          >
            <template v-if="isXSmallButton">
              <v-icon>mdi-close</v-icon>
            </template>
            <template v-else>
              <v-icon left>mdi-close</v-icon>
              クリア
            </template>
          </v-btn>

          <span class="ml-2">
            <div class="mt-2 hidden-sm-and-up"></div>
            <template v-for="(value, key) in query">
              <v-chip
                v-if="key !== 'page'"
                :key="key"
                class="ma-1"
                close
                small
                @click:close="removeQuery(key)"
              >
                {{ key | searchLabel }}
                {{ value }}
              </v-chip>
              <span class="mt-2" :key="`${key}-2`"></span>
            </template>
          </span>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script>
import SearchDialog from '@/components/Common/SearchDialog.vue'
import { WindowResizeMixin } from '@/mixins'

export default {
  mixins: [WindowResizeMixin],
  props: {
    total: { type: Number, require: true },
    type: { type: String, require: true },
    bookId: { type: String, require: false },
  },
  components: {
    SearchDialog,
  },
  computed: {
    hasQuery() {
      return Object.keys(this.query).length > 0
    },
    isXSmallButton() {
      return this.hasQuery && !this.isLessThanSm
    },
    query() {
      const query = { ...this.$route.query }
      delete query.page
      delete query.book
      return query
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
    removeQuery(key) {
      const queryOrigin = { ...this.query }

      if (key) {
        delete this.query[key]
        delete this.query.page
      } else {
        for (const key in this.query) {
          delete this.query[key]
        }
      }

      // OR検索だけになったらAND検索に置換
      const keys = Object.keys(this.query)
      const hasAnd = keys.some((e) => e.match(/^(?!.*_or).*$/) !== null)

      if (!hasAnd) {
        this.query = {}
        keys.forEach((key) => {
          const value = queryOrigin[key]
          const keyName = key.replace(/_or$/, '')
          this.query[keyName] = value
        })
      }

      this.$router.push({
        path: this.$route.path,
        query: this.query,
      })
    },
  },
}
</script>
