<template>
  <v-container fluid>
    <div class="col-md-8 col-sm-10 mx-auto">
      <v-text-field
        v-model="searchValue"
        label="検索キーワード"
        prepend-icon="mdi-magnify"
        clearable
        @keydown.enter="this.changeQuery('q', searchValue, true)"
      ></v-text-field>

      <v-row>
        <v-col v-for="item in items" :key="item.id" cols="12" lg="6">
          <v-card class="mx-auto" height="185">
            <v-row no-gutters>
              <v-col cols="8">
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      v-text="item.title"
                      class="font-weight-medium"
                    ></v-list-item-title>
                    <v-list-item-subtitle
                      v-text="item.authors.join(', ')"
                    ></v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-col>

              <v-col cols="4">
                <v-img
                  contain
                  :src="
                    item.imageLinks ? item.imageLinks.thumbnail : noImageCover
                  "
                  max-height="185"
                  min-height="185"
                ></v-img>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <infinite-loading @infinite="infiniteHandler" :identifier="infiniteId">
        <div slot="no-more" class="py-4 text-body-2">
          これ以上通知はありません
        </div>
        <div slot="no-results" class="py-4 text-body-2">
          データが見つかりません
        </div>
        <div slot="spinner" class="py-4">
          <spinner />
        </div>
      </infinite-loading>
    </div>
  </v-container>
</template>

<script>
import axios from 'axios'
import Spinner from 'vue-simple-spinner'
import InfiniteLoading from 'vue-infinite-loading'

export default {
  components: {
    Spinner,
    InfiniteLoading,
  },
  data: () => ({
    noImageCover:
      'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
    searchValue: '',
    items: [],
    total: 0,
    page: 0,
    maxResults: 12,
    infiniteId: +new Date(),
  }),
  beforeRouteUpdate(to, from, next) {
    // URLパラメータから値を設定してfetchする
    this.fetchBookList(to.query)
    next()
  },
  methods: {
    fetchBookList(query) {
      // BUG: Google Books APIのtotalItemsの数はあてにならない (非固定)
      // →ページネーションの割り振りには使えない

      this.searchValue = query.q || ''

      if (this.searchValue) {
        const startIndex = (this.page - 1) * (this.maxResults + 1)

        return axios
          .get('https://www.googleapis.com/books/v1/volumes', {
            params: {
              q: this.searchValue,
              orderBy: 'relevance',
              maxResults: this.maxResults,
              startIndex: startIndex,
            },
          })
          .then(({ data }) => {
            this.total = data.totalItems
            data.items.forEach((item) => {
              item.volumeInfo.authors = item.volumeInfo.authors || ['不明']
              this.items.push(item.volumeInfo)
            })

            return Promise.resolve()
          })
          .catch((error) => {
            return Promise.reject(error)
          })
      }
    },
    changeQuery(key, val, isClear = false) {
      const query = isClear ? {} : Object.assign({}, this.$route.query)
      query[key] = val

      this.items = []

      if (JSON.stringify(query) != JSON.stringify(this.$route.query)) {
        this.$router.push({
          path: this.$route.path,
          query: query,
        })
      } else {
        this.fetchBookList(this.$route.query)
      }
    },
    infiniteHandler($state) {
      this.page++
      this.fetchBookList(this.$route.query)
        .then(() => {
          $state.loaded()
        })
        .catch(() => {
          $state.complete()
        })
    },
  },
}
</script>
