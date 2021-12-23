<template>
  <div>
    <Dialog
      ref="dialogBookAdd"
      title="書籍の追加"
      :max-width="600"
      fullscreen
      hide-overlay
      scrollable
      transition="dialog-bottom-transition"
    >
      <template #activator="{ attrs }">
        <slot
          name="activator"
          :on="{ click: showBookAddDialog }"
          :attrs="attrs"
        ></slot>
      </template>

      <template #toolbar="{ title, cancel }">
        <v-toolbar flat dark color="primary">
          <v-btn icon dark @click="cancel">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title style="cursor: pointer" @click="scrollToTop">
            {{ title }}
          </v-toolbar-title>
        </v-toolbar>
      </template>

      <!-- 検索 -->
      <v-container>
        <v-text-field
          v-model="searchValue"
          @keydown.enter="resetInfinite"
          autofocus
        ></v-text-field>
      </v-container>

      <v-card-text style="height: 100vh" id="book-add-content">
        <v-container>
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
              <Spinner></Spinner>
            </div>
          </infinite-loading>

          <v-card v-else class="pa-5 text-center">
            <h2>書籍の追加</h2>

            <p class="mt-2 text-body-2">
              検索アイコンをクリックして、追加する書籍を検索してください
            </p>
          </v-card>
        </v-container>
        <div style="flex: 1 1 auto"></div>
      </v-card-text>
    </Dialog>

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
  </div>
</template>

<script>
import axios from 'axios'
import Spinner from '@/components/Spinner.vue'
import InfiniteLoading from 'vue-infinite-loading'
import api from '@/services/api'
import Mixin, { FormRulesMixin } from '@/mixins'
import Dialog from '@/components/Dialog.vue'
import BookList from '@/components/BookList.vue'
import BookEditDialog from '@/components/BookEditDialog.vue'
// import VueScrollTo from 'vue-scrollto'

export default {
  mixins: [Mixin, FormRulesMixin],
  components: {
    Spinner,
    InfiniteLoading,
    Dialog,
    BookList,
    BookEditDialog,
  },
  data: () => ({
    searchValue: '',
    items: [],
    total: 0,
    page: 1,
    maxResults: 12,
    infiniteId: null,
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
    showBookAddDialog() {
      this.searchValue = ''
      this.resetInfinite()
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

          this.items.push({
            title: volumeInfo.title,
            authors: volumeInfo.authors || ['不明'],
            thumbnail: volumeInfo.imageLinks
              ? volumeInfo.imageLinks.thumbnail
              : null,
            total: volumeInfo.pageCount || 0,
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
      this.items = []
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
      const { data, status } = await api({
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
          id: data.id,
        },
      })

      if (status === 201) {
        this.$store.dispatch('message/setInfoMessage', {
          message: '書籍を登録しました。',
        })
      } else {
        this.$store.dispatch('message/setInfoMessage', {
          message: 'この本は既に登録されています。',
        })
      }

      this.$refs.dialogBookAdd.hideDialog()
    },
    showPagesDialog() {
      if (this.$refs.formPages) {
        this.formPages.value = 0
        this.$refs.formPages.resetValidation()
      }
      return this.$refs.dialogPages.showDialog()
    },
    scrollToTop() {
      // VueScrollTo.scrollTo('#app')
      const element = document.getElementById('book-add-content')
      element.scrollTop = 0
    },
    handleSearch(searchValue) {
      this.searchValue = searchValue
      this.resetInfinite()
    },
  },
}
</script>
