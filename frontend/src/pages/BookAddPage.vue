<template>
  <v-container fluid>
    <div class="col-md-8 col-sm-10 mx-auto">
      <v-text-field
        v-model="searchValue"
        label="検索キーワード"
        prepend-icon="mdi-magnify"
        clearable
        @keydown.enter="resetInfinite()"
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

                <v-list-item>
                  <v-btn color="green" block @click="addBookCopy(item)">
                    本を登録
                  </v-btn>
                </v-list-item>
                <v-list-item>
                  <v-btn color="orange" block>Kindle本を登録</v-btn>
                </v-list-item>
              </v-col>

              <v-col cols="4">
                <v-img
                  contain
                  :src="item.thumbnail || noImageCover"
                  max-height="185"
                  min-height="185"
                ></v-img>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <infinite-loading
        v-if="searchValue"
        @infinite="infiniteHandler"
        :identifier="infiniteId"
      >
        <div slot="no-more" class="py-4 text-body-2">
          これ以上データはありません
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
import api from '@/services/api'

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
    page: 1,
    maxResults: 12,
    infiniteId: +new Date(),
  }),
  methods: {
    fetchBookList() {
      // BUG: Google Books APIのtotalItemsの数はあてにならない (非固定)
      // →ページ番号の割り振りには使えない

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
              const { volumeInfo } = item

              let amazon_dp
              if (volumeInfo.industryIdentifiers) {
                // ISBNコードが存在する場合、ISBN_13を優先してamazon_dpに入れる
                const industryIdentifier =
                  volumeInfo.industryIdentifiers.find(
                    (e) => e.type === 'ISBN_13'
                  ) || volumeInfo.industryIdentifiers[0]
                amazon_dp = industryIdentifier.identifier
              } else {
                // ISBNコードが存在しない場合、amazon_dpにはnullを入れる
                amazon_dp = null
              }

              this.items.push({
                title: volumeInfo.title,
                authors: volumeInfo.authors || ['不明'],
                thumbnail: volumeInfo.imageLinks
                  ? volumeInfo.imageLinks.thumbnail
                  : null,
                total: volumeInfo.pageCount || 0,
                amazon_dp: amazon_dp,
              })
            })

            return Promise.resolve()
          })
          .catch((error) => {
            return Promise.reject(error)
          })
      } else {
        return Promise.reject()
      }
    },
    infiniteHandler($state) {
      this.fetchBookList()
        .then(() => {
          this.page++
          $state.loaded()
        })
        .catch(() => {
          $state.complete()
        })
    },
    resetInfinite() {
      this.page = 1
      this.items = []
      this.infiniteId++
    },
    async addBookCopy(item) {
      try {
        let bookOrigin, bookCopy, response
        response = await api.post('/book_origin/', {
          author: item.authors.join(','),
          title: item.title,
          thumbnail: item.thumbnail,
        })
        bookOrigin = response.data.id

        // TODO: ここにKindle本の場合の処理も入れる (各種データをモーダルで入力)
        let format_type
        format_type = 0

        response = await api.post('/book_copy/', {
          book_origin: bookOrigin,
          total: item.total,
          amazon_dp: item.amazon_dp,
          format_type: format_type,
        })
        bookCopy = response.data.id

        // TODO: ここにbookCopyの詳細ページに遷移する処理を記述
        console.log(bookCopy)
        this.$store.dispatch('message/setInfoMessage', {
          message: '書籍を登録しました。',
        })
      } catch {
        console.log('Server Error')
      }
    },
  },
}
</script>
