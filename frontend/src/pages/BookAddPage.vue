<template>
  <v-container fluid>
    <div class="col-sm-10 mx-auto">
      <!-- 検索結果リスト -->
      <v-row>
        <v-col v-for="item in items" :key="item.id" cols="12" md="6" lg="4">
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
                  <v-btn color="orange" block @click="addBookCopy(item, true)">
                    Kindle本を登録
                  </v-btn>
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
    </div>

    <!-- 検索用ボトムシート -->
    <v-bottom-sheet v-model="searchBottomSheet" inset>
      <!-- アクティベーター -->
      <template #activator="{ on, attrs }">
        <v-fab-transition>
          <v-btn
            color="pink"
            dark
            bottom
            right
            fab
            fixed
            class="v-btn--search"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </v-fab-transition>
      </template>

      <!-- ボトムシート本体 -->
      <v-sheet class="text-center" height="200px">
        <v-btn
          class="mt-6"
          text
          color="error"
          @click="searchBottomSheet = !searchBottomSheet"
        >
          close
        </v-btn>

        <v-text-field
          v-model="searchValue"
          label="検索キーワード"
          prepend-icon="mdi-magnify"
          clearable
          class="mx-md-10 mx-5"
          @keypress.enter="resetInfinite()"
        ></v-text-field>
      </v-sheet>
    </v-bottom-sheet>

    <!-- Kindle本のデータ入力ダイアログ -->
    <Dialog
      ref="inputKindle"
      title="Kindle本のデータ"
      message="Kindle本のデータを入力してください。"
      :max-width="400"
    >
      <template #content="{ message }">
        <p>{{ message }}</p>

        <v-form ref="formKindle" v-model="formKindle.valid">
          <v-text-field
            v-model="formKindle.asin"
            label="ASINコード"
            :rules="formKindle.asinRules"
            maxlength="10"
          ></v-text-field>
          <v-text-field
            v-model="formKindle.total"
            label="位置Noの総数"
            type="number"
            min="0"
            :rules="formKindle.totalRules"
          ></v-text-field>
        </v-form>
      </template>

      <template #actions="{ ok, cancel }">
        <v-spacer></v-spacer>
        <v-btn
          color="green darken-1"
          text
          @click="ok"
          :disabled="!formKindle.valid"
        >
          OK
        </v-btn>
        <v-btn color="green darken-1" text @click="cancel">キャンセル</v-btn>
      </template>
    </Dialog>
  </v-container>
</template>

<script>
import axios from 'axios'
import Spinner from 'vue-simple-spinner'
import InfiniteLoading from 'vue-infinite-loading'
import api from '@/services/api'
import Mixin, { FormRulesMixin } from '@/mixins'
import Dialog from '@/components/Dialog.vue'

export default {
  mixins: [Mixin, FormRulesMixin],
  components: {
    Spinner,
    InfiniteLoading,
    Dialog,
  },
  data: () => ({
    noImageCover:
      'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
    searchValue: '',
    items: [],
    total: 0,
    page: 1,
    maxResults: 12,
    infiniteId: null,
    searchBottomSheet: true,
    formKindle: {
      asin: '',
      total: 0,
      valid: false,
      asinRules: [
        (v) => !!v || 'この項目は入力必須です',
        (v) => v.length === 10 || '10文字のコードを入力してください',
      ],
      totalRules: [(v) => v > 0 || '0より大きい数値を入力してください'],
    },
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
    async addBookCopy(item, kindle) {
      try {
        let bookOrigin, bookCopy, response, format_type

        // BookOriginのデータを登録
        // 既に登録されている場合は該当のデータが返却される (statusは200)
        response = await api({
          url: '/book_origin/',
          method: 'post',
          data: {
            author: item.authors.join(','),
            title: item.title,
            thumbnail: item.thumbnail,
          },
        })
        bookOrigin = response.data.id

        // 書籍データの入力
        if (kindle) {
          // Kindle本の場合、各種データを入力
          let ret = await this.showKindleDialog()
          if (!ret) return

          format_type = 1
          item.amazon_dp = this.formKindle.asin
          item.total = this.formKindle.total
        } else {
          // 通常の書籍データで登録
          format_type = 0
        }

        // BookCopyのデータを登録
        // 既に登録されている場合は該当のデータが返却される (statusは200)
        response = await api({
          url: '/book_copy/',
          method: 'post',
          data: {
            book_origin: bookOrigin,
            total: item.total,
            amazon_dp: item.amazon_dp,
            format_type: format_type,
          },
        })
        bookCopy = response.data.id

        // TODO: ここにbookCopyの詳細ページに遷移する処理を記述
        console.log(bookCopy)

        if (response.status === 201) {
          this.$store.dispatch('message/setInfoMessage', {
            message: '書籍を登録しました。',
          })
        } else {
          this.$store.dispatch('message/setInfoMessage', {
            message: 'この本は既に登録されています。',
          })
        }
      } catch (err) {
        console.log(err)
        this.$store.dispatch('message/setErrorMessage', {
          message: 'サーバーエラーが発生しました。',
        })
      }
    },
    showKindleDialog() {
      if (this.$refs.formKindle) {
        this.formKindle.asin = ''
        this.formKindle.total = 0
        this.$refs.formKindle.resetValidation()
      }
      return this.$refs.inputKindle.showDialog()
    },
  },
}
</script>

<style scoped>
.v-btn--search {
  bottom: 0;
  margin: 0 0 24px 48px;
}
</style>
