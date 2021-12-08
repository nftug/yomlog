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
              <v-chip small v-text="`${bookProgress(item)}%`"></v-chip>
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
                :total-visible="5"
                @input="handlePagination"
              ></v-pagination>
            </v-container>
          </v-col>
        </v-row>
      </template>
    </div>

    <!-- ダイアログ -->
    <StatusAddDialog ref="statusAdd" @reload="handleReload"></StatusAddDialog>
    <NoteAddDialog ref="noteAdd"></NoteAddDialog>
    <ShelfSearchDialog ref="shelfSearch"></ShelfSearchDialog>
    <BookDeleteDialog
      ref="bookDelete"
      @delete-book="handleReload"
    ></BookDeleteDialog>
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Spinner from 'vue-simple-spinner'
import Mixins, {
  BookListMixin,
  ShelfSearchFromHeaderMixin,
  ListViewMixin,
} from '@/mixins'
import api from '@/services/api'
import StatusAddDialog from '@/components/StatusAddDialog.vue'
import NoteAddDialog from '@/components/NoteAddDialog.vue'
import ShelfSearchDialog from '@/components/ShelfSearchDialog.vue'
import BookDeleteDialog from '@/components/BookDeleteDialog.vue'

export default {
  mixins: [BookListMixin, ShelfSearchFromHeaderMixin, ListViewMixin, Mixins],
  components: {
    Spinner,
    BookList,
    StatusAddDialog,
    BookDeleteDialog,
    NoteAddDialog,
    ShelfSearchDialog,
  },
  data() {
    return {
      mode: this.$route.params.mode,
      query: {},
    }
  },
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにモードを変更する
    this.initPage({ isReload: true, route: to })
    next()
  },
  created() {
    this.initPage({
      isReload: this.bookList.isDirty || !this.$isBrowserBack,
    })

    if (this.bookList.isDirty) {
      this.$store.commit('bookList/setDirty', false)
    }
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
      this.page = Number(route.query.page || 1)

      if (isReload || !this.bookList.items.length) {
        this.fetchBookList()
      }

      this.$nextTick(() => {
        this.$router.app.$emit('changeSearchValue', route.query.q || '')
      })
    },
    fetchBookList() {
      this.$store.commit('bookList/setLoading', true)
      this.$store.commit('bookList/clear')

      return api
        .get('/book/', {
          params: {
            ...this.query,
            page: this.page,
            status: this.mode,
          },
        })
        .then(({ data }) => {
          this.$store.commit('bookList/setProps', {
            totalItems: data.count,
            totalPages: data.totalPages,
          })

          data.results.forEach((item) => {
            this.fixStatus(item)
            this.$store.commit('bookList/add', item)
          })

          return Promise.resolve()
        })
        .catch((error) => {
          if (error.response) {
            const { response } = error
            if (response.status === 404) {
              // ページ数超過の場合、最終ページに遷移
              let params = { ...response.config.params }
              this.replaceWithFinalPage('/book/', params)
              return Promise.resolve()
            } else {
              return Promise.reject(response)
            }
          }
        })
        .finally(() => {
          this.$store.commit('bookList/setLoading', false)
        })
    },
    handleReload(state) {
      if (!state) this.initPage({ isReload: true })

      const fullPath = `/shelf/${state}`
      if (fullPath !== this.$route.fullPath) {
        this.$router.push(fullPath)
      } else {
        this.initPage({ isReload: true })
      }
    },
    onClickQueryAdd() {
      this.$refs.shelfSearch.showShelfSearchDialog()
    },
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusAddDialog(item)
    },
    onClickNoteAdd(item) {
      this.$refs.noteAdd.showNoteAddDialog(item)
    },
    onClickDeleteBook(item) {
      this.$refs.bookDelete.showBookDeleteDialog(item)
    },
  },
}
</script>
