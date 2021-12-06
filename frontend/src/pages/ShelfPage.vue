<template>
  <v-container fluid>
    <div class="col-sm-10 mx-auto">
      <!-- 件数 -->
      <div class="pb-4">
        <v-card class="mx-auto text-body-2" outlined>
          <div class="ma-4">
            <strong>{{ bookList.totalItems }}冊</strong>
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

            <v-btn small class="ma-1" icon @click="onClickQueryAdd">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
        </v-card>
      </div>

      <!-- Spinner -->
      <spinner v-if="bookList.isLoading"></spinner>

      <template v-else>
        <!-- 本棚 -->
        <BookList :items="bookList.items" detail-link>
          <template #content="{ item }">
            <!-- 追加の情報 -->
            <v-list-item>
              <v-chip
                :color="item.format_type ? 'orange' : 'green'"
                dark
                small
                class="mr-2"
                v-text="item.format_type ? 'Kindle' : 'Book'"
              ></v-chip>
              <v-chip
                small
                v-text="
                  parseInt(
                    ((item.status[0].position || 0) / item.total) * 100,
                    10
                  ) + '%'
                "
              ></v-chip>
            </v-list-item>

            <!-- メニュー -->
            <v-row class="col-11" no-gutters>
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      icon
                      color="secondary"
                      v-bind="attrs"
                      v-on="on"
                      :to="`/book/detail/${item.id}`"
                    >
                      <v-icon>mdi-eye</v-icon>
                    </v-btn>
                  </template>
                  <span>詳細</span>
                </v-tooltip>
              </v-col>
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      icon
                      color="primary"
                      v-bind="attrs"
                      v-on="on"
                      @click="onClickNoteAdd(item)"
                    >
                      <v-icon>mdi-pen-plus</v-icon>
                    </v-btn>
                  </template>
                  <span>ノートを追加</span>
                </v-tooltip>
              </v-col>
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      icon
                      color="success"
                      v-bind="attrs"
                      v-on="on"
                      @click="onClickStatusAdd(item)"
                    >
                      <v-icon>mdi-bookmark-plus</v-icon>
                    </v-btn>
                  </template>
                  <span>進捗を記録</span>
                </v-tooltip>
              </v-col>
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      icon
                      color="error"
                      v-bind="attrs"
                      v-on="on"
                      @click="onClickDeleteBook(item)"
                    >
                      <v-icon>mdi-trash-can</v-icon>
                    </v-btn>
                  </template>
                  <span>本を削除</span>
                </v-tooltip>
              </v-col>
            </v-row>
          </template>
        </BookList>

        <!-- ページネーション -->
        <v-row justify="center" v-show="bookList.items.length">
          <v-col cols="8">
            <v-container class="max-width">
              <v-pagination
                v-model="page"
                class="my-4"
                :length="bookList.totalPages"
                @input="handlePagination"
              ></v-pagination>
            </v-container>
          </v-col>
        </v-row>
      </template>
    </div>

    <!-- ダイアログ -->
    <StatusAdd
      ref="statusAdd"
      shelf
      @reload="initPage({ isReload: true })"
    ></StatusAdd>

    <NoteAdd ref="noteAdd" shelf></NoteAdd>

    <ShelfSearch ref="shelfSearch"></ShelfSearch>

    <Dialog
      ref="dialogDeleteBook"
      title="本の削除"
      message="この本を削除しますか？"
    ></Dialog>
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Spinner from 'vue-simple-spinner'
import Mixins, { BookListMixin, ShelfSearchFromHeaderMixin } from '@/mixins'
import api from '@/services/api'
import StatusAdd from '@/components/StatusAdd.vue'
import NoteAdd from '@/components/NoteAdd.vue'
import ShelfSearch from '@/components/ShelfSearch.vue'
import Dialog from '@/components/Dialog.vue'

export default {
  mixins: [BookListMixin, ShelfSearchFromHeaderMixin, Mixins],
  components: {
    Spinner,
    BookList,
    StatusAdd,
    Dialog,
    NoteAdd,
    ShelfSearch,
  },
  data() {
    return {
      page: 1,
      mode: this.$route.params.mode,
      query: {},
      searchValue: '',
    }
  },
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにモードを変更する
    this.initPage({ isReload: true, route: to })
    next()
  },
  created() {
    this.initPage({ isReload: !this.$isBrowserBack })
  },
  filters: {
    searchLabel(key) {
      const keyName = key.replace(/_or$/, '')
      let or = keyName !== key
      let label

      if (keyName === 'title') {
        label = '書名'
      } else if (keyName === 'authors') {
        label = '著者名'
      } else if (keyName === 'amazon_dp') {
        label = 'ISBN/ASIN'
      } else {
        label = '検索'
      }

      return or ? `${label} (OR):` : `${label}:`
    },
  },
  methods: {
    initPage({ isReload, route = this.$route }) {
      this.mode = route.params.mode !== 'all' ? route.params.mode : ''
      this.query = { ...route.query }
      delete this.query.page
      this.page = Number(route.query.page || 1)

      if (isReload || !this.bookList.items.length) {
        this.fetchBookList()
      }

      this.$nextTick(() => {
        this.$router.app.$emit('changeSearchValue', this.searchValue)
      })
    },
    fetchBookList() {
      this.$store.commit('bookList/setLoading', true)
      this.$store.commit('bookList/clear')

      return api
        .get('/book_copy/', {
          params: {
            page: this.page,
            status: this.mode,
            ...this.query,
          },
        })
        .then(({ data }) => {
          this.$store.commit('bookList/setPageProps', {
            totalItems: data.count,
            totalPages: data.totalPages,
          })

          this.$store.commit('bookList/add', [...data.results])

          return Promise.resolve()
        })
        .catch(({ response }) => {
          if (response.status === 404) {
            // ページ数超過の場合、最終ページに遷移
            let params = { ...response.config.params }
            delete params.page

            api
              .get('/book_copy/', {
                params: params,
              })
              .then(({ data: { totalPages } }) => {
                params.page = totalPages
                this.$router.replace({
                  path: this.$route.path,
                  query: params,
                })
              })
          } else {
            return Promise.reject(response)
          }
        })
        .finally(() => {
          this.$store.commit('bookList/setLoading', false)
        })
    },
    removeQuery(key) {
      let query = { ...this.query }
      delete query[key]
      this.$router.push({
        path: this.$route.path,
        query: query,
      })
    },
    handlePagination() {
      let query = { ...this.$route.query }
      query.page = this.page

      this.$router.push({
        path: this.$route.path,
        query: query,
      })
    },
    onClickQueryAdd() {
      this.$refs.shelfSearch.showShelfSearch()
    },
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusAdd(item)
    },
    onClickNoteAdd(item) {
      this.$refs.noteAdd.showNoteAdd(item)
    },
    async onClickDeleteBook(item) {
      if (!(await this.$refs.dialogDeleteBook.showDialog())) return

      api({
        url: `/book_copy/${item.id}/`,
        method: 'delete',
      })
        .then(() => {
          this.fetchBookList()
          this.$store.dispatch('message/setInfoMessage', {
            message: '書籍を削除しました。',
          })
        })
        .catch(() => {
          this.$store.dispatch('message/setErrorMessage', {
            message: 'エラーが発生しました。',
          })
        })
    },
  },
}
</script>
