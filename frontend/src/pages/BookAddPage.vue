<template>
  <v-container fluid>
    <div class="col-sm-10 mx-auto">
      <!-- 検索結果リスト -->
      <BookList :items="items" :loading="true">
        <template #content="{ item }">
          <v-list-item>
            <v-btn color="green" dark block @click="addBook(item, 0)">
              本を登録
            </v-btn>
          </v-list-item>
          <v-list-item>
            <v-btn color="orange" dark block @click="addBook(item, 1)">
              Kindle本を登録
            </v-btn>
          </v-list-item>
        </template>
      </BookList>

      <!-- Infinite Loading -->
      <infinite-loading
        v-if="infiniteId"
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

      <v-card v-else class="pa-5 text-center">
        <h2>書籍の追加</h2>

        <p class="mt-2 text-body-2">
          検索アイコンをクリックして、追加する書籍を検索してください
        </p>
      </v-card>
    </div>

    <!-- スクロール -->
    <Fab icon="mdi-chevron-up" @click="onClickFab"></Fab>

    <!-- ページ数入力のダイアログ -->
    <Dialog
      ref="dialogPages"
      title="ページ数の入力"
      :max-width="400"
      :form-valid="formPages.valid"
    >
      <p>
        ページ数を取得できません。
        <br />
        この本のページ数を入力してください。
      </p>

      <v-form ref="formPages" v-model="formPages.valid" @submit.prevent>
        <v-text-field
          v-model="formPages.value"
          label="ページ数"
          type="number"
          min="0"
          :rules="formPages.pagesRules"
        ></v-text-field>
      </v-form>
    </Dialog>

    <!-- Kindle本のデータ入力ダイアログ -->
    <BookEditDialog ref="bookEdit"></BookEditDialog>
  </v-container>
</template>

<script>
import axios from 'axios'
import Spinner from 'vue-simple-spinner'
import InfiniteLoading from 'vue-infinite-loading'
import api from '@/services/api'
import Mixin, { FormRulesMixin } from '@/mixins'
import Dialog from '@/components/Dialog.vue'
import BookList from '@/components/BookList.vue'
import BookEditDialog from '@/components/BookEditDialog.vue'
import Fab from '@/components/Fab.vue'
import VueScrollTo from 'vue-scrollto'

export default {
  mixins: [Mixin, FormRulesMixin],
  components: {
    Spinner,
    InfiniteLoading,
    Dialog,
    BookList,
    BookEditDialog,
    Fab,
  },
  data: () => ({
    searchValue: '',
    items: [],
    total: 0,
    page: 1,
    maxResults: 12,
    infiniteId: null,
    searchBottomSheet: true,
    formPages: {
      value: 0,
      valid: false,
      pagesRules: [(v) => v > 0 || '0より大きい数値を入力してください'],
    },
  }),
  created() {
    this.$router.app.$on('search', this.handleSearch)
  },
  beforeDestroy() {
    this.$router.app.$off('search', this.handleSearch)
  },
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
              const { volumeInfo, id } = item
              let amazon_dp

              if (volumeInfo.industryIdentifiers) {
                // ISBNコードが存在する場合、ISBN_13→ISBN_10の順番でamazon_dpに入れる
                let industryIdentifier =
                  volumeInfo.industryIdentifiers.find(
                    (e) => e.type === 'ISBN_13'
                  ) ||
                  volumeInfo.industryIdentifiers.find(
                    (e) => e.type === 'ISBN_10'
                  ) ||
                  ''
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
                id_google: id,
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
      // infinite-loadingの有効化 or リセット
      if (this.infiniteId) {
        this.infiniteId++
      } else {
        this.infiniteId = +new Date()
      }

      this.page = 1
      this.items = []

      // ボトムシートの非表示
      this.searchBottomSheet = false
    },
    async addBook(book, format_type) {
      let item = { ...book }

      item.format_type = format_type

      // 書籍データの入力
      if (format_type === 1) {
        // Kindle本の場合、各種データを入力
        try {
          item.total = 0
          item = await this.$refs.bookEdit.showBookEditDialog({
            book: item,
            post: false,
          })
        } catch {
          // ダイアログがキャンセルの場合の処理
          return
        }
      } else {
        // 通常の書籍データで登録
        // ページ数が空の場合はダイアログで入力を求める
        if (!item.total) {
          if (!(await this.showPagesDialog())) return
          item.total = this.formPages.value
        }
      }

      // Bookのデータを登録
      // 既に登録されている場合は該当のデータが返却される (statusは200)
      let response
      response = await api({
        url: '/book/',
        method: 'post',
        data: {
          id_google: item.id_google,
          authors: item.authors.join(','),
          title: item.title,
          thumbnail: item.thumbnail,
          total: item.total,
          amazon_dp: item.amazon_dp,
          format_type: item.format_type,
        },
      })

      // 書籍の詳細ページに遷移
      this.$router.replace({
        name: 'book_detail',
        params: {
          id: response.data.id,
        },
      })

      if (response.status === 201) {
        this.$store.dispatch('message/setInfoMessage', {
          message: '書籍を登録しました。',
        })
      } else {
        this.$store.dispatch('message/setInfoMessage', {
          message: 'この本は既に登録されています。',
        })
      }
    },
    showPagesDialog() {
      if (this.$refs.formPages) {
        this.formPages.value = 0
        this.$refs.formPages.resetValidation()
      }
      return this.$refs.dialogPages.showDialog()
    },
    onClickFab() {
      VueScrollTo.scrollTo('#app')
    },
    handleSearch(searchValue) {
      this.searchValue = searchValue
      this.resetInfinite()
    },
  },
}
</script>
