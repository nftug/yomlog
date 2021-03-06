<template>
  <Dialog
    ref="dialogBookAdd"
    title="書籍の追加"
    max-width="75vw"
    :fullscreen="isLessThanMd"
    :hide-overlay="isLessThanMd"
    no-template
    scrollable
    transition="dialog-bottom-transition"
    hash="add-book"
  >
    <template #activator="{ attrs }">
      <slot
        name="activator"
        :on="{ click: showBookAddDialog }"
        :attrs="attrs"
      ></slot>
    </template>

    <template #default="{ title, cancel }">
      <v-toolbar flat dark color="primary">
        <v-btn icon dark @click="cancel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <SearchField v-model="searchValue" @search="resetInfinite">
          <v-toolbar-title style="cursor: pointer" @click="scrollToTop">
            {{ title }}
          </v-toolbar-title>
        </SearchField>
      </v-toolbar>

      <v-card-text style="height: 100vh" id="book-add-content">
        <v-container>
          <!-- 検索結果リスト -->
          <BookList :books="books" :loading="true">
            <template #content="{ book }">
              <v-list-item>
                <v-btn color="green" dark block @click="addBook(book, 0)">
                  本を登録
                </v-btn>
              </v-list-item>
              <v-list-item>
                <v-btn color="orange" dark block @click="addBook(book, 1)">
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
              <Spinner></Spinner>
            </div>
          </infinite-loading>

          <v-card v-else class="pa-5 text-center elevation-0 transparent">
            <v-card-title primary-title class="layout justify-center">
              <div class="headline text-center">書籍の追加</div>
            </v-card-title>

            <v-card-text class="text-center">
              <v-icon x-large class="green--text">mdi-book-plus</v-icon>
              <div class="mt-5">
                上部のバーから追加する書籍を検索してください。
              </div>
            </v-card-text>
          </v-card>
        </v-container>
        <div style="flex: 1 1 auto"></div>
      </v-card-text>

      <!-- Kindle本のデータ入力ダイアログ -->
      <BookEditDialog ref="bookEdit" hash="edit-book"></BookEditDialog>
    </template>
  </Dialog>
</template>

<script>
import axios from 'axios'
import Spinner from '@/components/Common/Spinner.vue'
import InfiniteLoading from 'vue-infinite-loading'
import Mixin, { FormRulesMixin, WindowResizeMixin } from '@/mixins'
import Dialog from '@/components/Common/Dialog.vue'
import BookList from '@/components/Common/BookList.vue'
import BookEditDialog from '@/components/Dialog/BookEditDialog.vue'
import SearchField from '@/components/Header/SearchField.vue'

export default {
  mixins: [Mixin, FormRulesMixin, WindowResizeMixin],
  components: {
    Spinner,
    InfiniteLoading,
    Dialog,
    BookList,
    BookEditDialog,
    SearchField,
  },
  data: () => ({
    searchValue: '',
    books: [],
    total: 0,
    page: 1,
    maxResults: 12,
    infiniteId: null,
  }),
  methods: {
    showBookAddDialog() {
      this.searchValue = ''
      this.resetInfinite()
      this.infiniteId = null
      this.$refs.dialogBookAdd.showDialog()
    },
    async fetchBookList() {
      // BUG: Google Books APIのtotalItemsの数はあてにならない (非固定)
      // →ページ番号の割り振りには使えない

      if (this.searchValue) {
        const startIndex = (this.page - 1) * (this.maxResults + 1)
        const { data } = await axios.get(
          'https://www.googleapis.com/books/v1/volumes',
          {
            params: {
              q: this.searchValue,
              orderBy: 'relevance',
              maxResults: this.maxResults,
              startIndex,
            },
          }
        )

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

          this.books.push({
            title: volumeInfo.title,
            authors: volumeInfo.authors || ['不明'],
            thumbnail: volumeInfo.imageLinks
              ? volumeInfo.imageLinks.thumbnail
              : null,
            total: volumeInfo.pageCount || 0,
            total_page: volumeInfo.pageCount || 0,
            amazon_dp,
            id_google: id,
          })
        })
      } else {
        return Promise.reject()
      }
    },
    async infiniteHandler($state) {
      try {
        await this.fetchBookList()
        this.page++
        $state.loaded()
      } catch {
        $state.complete()
      }
    },
    resetInfinite() {
      // infinite-loadingの有効化 or リセット
      if (this.infiniteId) {
        this.infiniteId++
      } else {
        this.infiniteId = +new Date()
      }

      this.page = 1
      this.books = []
    },
    async addBook(book, format_type) {
      let item = { ...book }
      item.format_type = format_type

      if (format_type === 1) {
        // Kindle本の場合、total_pageは残してtotalをクリア
        item.total = 0
      } else {
        // 通常の書籍の場合、total_pageをクリア
        delete item.total_page
      }

      item = await this.$refs.bookEdit.showBookEditDialog({ book: item })

      // ダイアログがキャンセルの場合
      if (!item) return

      // ユーザーデータを更新
      this.$store.dispatch('auth/reload')

      // bookListを更新
      const { status: stateName } = this.$store.state.bookList.query
      if (stateName === 'to_be_read' || stateName === 'all') {
        this.$store.dispatch('bookList/refreshBookList')
      }

      // 書籍の詳細ページに遷移
      setTimeout(() => {
        this.$router.replace(`/book/detail/${item.id}`)
      }, 100)
    },
    scrollToTop() {
      const element = document.getElementById('book-add-content')
      element.scrollTop = 0
    },
  },
}
</script>
