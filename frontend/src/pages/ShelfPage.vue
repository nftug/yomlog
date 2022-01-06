<template>
  <v-container fluid>
    <v-col sm="10" class="mx-auto">
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

            <SearchDialog type="book" hash="search-book">
              <template #activator="{ on, attrs }">
                <v-btn small class="ma-1" icon v-on="on" v-bind="attrs">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </template>
            </SearchDialog>
          </div>
        </v-card>
      </div>

      <!-- Spinner -->
      <Spinner v-if="bookList.isLoading"></Spinner>

      <template v-else>
        <!-- 本棚 -->
        <BookList :items="bookList.items" detail-link>
          <template #content="{ item }">
            <!-- 追加の情報 -->
            <v-list-item>
              <v-chip
                :color="item.format_type === 1 ? 'orange' : 'green'"
                dark
                small
                class="mr-2"
                v-text="item.format_type === 1 ? 'Kindle' : 'Book'"
              ></v-chip>
              <v-chip small>
                {{ currentState(item).position.percentage }}%
              </v-chip>
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
    </v-col>

    <!-- ダイアログ -->
    <StatusAddDialog ref="statusAdd" @post="handleReload"></StatusAddDialog>
    <NoteAddDialog ref="noteAdd"></NoteAddDialog>
    <ItemDeleteDialog
      ref="bookDelete"
      type="book"
      @delete="handleReload"
    ></ItemDeleteDialog>

    <BookAddDialog ref="bookAdd">
      <template #activator="{ on, attrs }">
        <Fab icon="mdi-book-plus" v-on="on" v-bind="attrs"></Fab>
      </template>
    </BookAddDialog>
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Mixins, { BookListMixin, ListViewMixin } from '@/mixins'
import api from '@/services/api'
import StatusAddDialog from '@/components/StatusPostDialog.vue'
import NoteAddDialog from '@/components/NotePostDialog.vue'
import SearchDialog from '@/components/SearchDialog.vue'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import Spinner from '@/components/Spinner.vue'
import BookAddDialog from '@/components/BookAddDialog.vue'
import Fab from '@/components/Fab.vue'

export default {
  mixins: [BookListMixin, ListViewMixin, Mixins],
  components: {
    BookList,
    StatusAddDialog,
    ItemDeleteDialog,
    NoteAddDialog,
    SearchDialog,
    Spinner,
    BookAddDialog,
    Fab,
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
    const isSameParams =
      JSON.stringify(to.params) === JSON.stringify(from.params)
    const isSameQuery = JSON.stringify(to.query) === JSON.stringify(from.query)

    if (!(isSameParams && isSameQuery)) {
      this.initPage({ isReload: true, route: to })
    }
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
        this.$router.app.$emit('changeSearchValue', route.query.q || '')
      })
    },
    async fetchBookList() {
      this.$store.commit('bookList/setLoading', true)
      this.$store.commit('bookList/clear')

      try {
        const { data } = await api.get('/book/', {
          params: { ...this.query, page: this.page, status: this.mode },
        })
        this.$store.commit('bookList/setProps', {
          totalItems: data.count,
          totalPages: data.totalPages,
        })
        data.results.forEach((item) => {
          this.$store.commit('bookList/add', item)
        })
      } catch (error) {
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
      } finally {
        this.$store.commit('bookList/setLoading', false)
      }
    },
    handleReload(data) {
      this.$store.dispatch('auth/reload') // ユーザー情報の更新

      if (!data.state) {
        this.initPage({ isReload: true })
        return
      }

      const fullPath = `/shelf/${data.state}`
      if (fullPath !== this.$route.fullPath) {
        this.$router.push(fullPath)
      } else {
        this.initPage({ isReload: true })
      }
    },
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusPostDialog({ book: item })
    },
    onClickNoteAdd(item) {
      this.$refs.noteAdd.showNotePostDialog({ book: item })
    },
    onClickDeleteBook(item) {
      this.$refs.bookDelete.showItemDeleteDialog(item.id)
    },
  },
}
</script>
