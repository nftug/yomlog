<template>
  <v-container fluid>
    <div class="col-sm-10 mx-auto">
      <!-- 件数 -->
      <div class="pb-4" v-if="totalItems > 0">
        <v-card class="mx-auto">
          <v-list-item>
            <strong>{{ totalItems }}冊</strong>
            の本が見つかりました。
          </v-list-item>
        </v-card>
      </div>

      <!-- Spinner -->
      <spinner v-if="isLoading"></spinner>

      <template v-else>
        <!-- 本棚 -->
        <BookList :items="items">
          <template #actions="{ item }">
            <v-row class="mx-auto mt-2">
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn icon color="secondary" v-bind="attrs" v-on="on">
                      <v-icon>mdi-eye</v-icon>
                    </v-btn>
                  </template>
                  <span>詳細</span>
                </v-tooltip>
              </v-col>
              <v-col cols="3">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn icon color="primary" v-bind="attrs" v-on="on">
                      <v-icon>mdi-pen-plus</v-icon>
                    </v-btn>
                  </template>
                  <span>メモを追加</span>
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
            </v-row>
          </template>
        </BookList>

        <!-- ページネーション -->
        <v-row justify="center" v-show="items.length">
          <v-col cols="8">
            <v-container class="max-width">
              <v-pagination
                v-model="page"
                class="my-4"
                :length="totalPages"
                @input="handlePagination"
              ></v-pagination>
            </v-container>
          </v-col>
        </v-row>
      </template>
    </div>

    <!-- ダイアログ -->
    <StatusAdd ref="statusAdd"></StatusAdd>
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Spinner from 'vue-simple-spinner'
import Mixins from '@/mixins'
import api from '@/services/api'
import StatusAdd from '@/components/StatusAdd.vue'

export default {
  mixins: [Mixins],
  components: {
    Spinner,
    BookList,
    StatusAdd,
  },
  data() {
    return {
      infiniteId: +new Date(),
      items: [],
      page: 1,
      mode: this.$route.params.mode,
      searchValue: '',
      totalItems: 0,
      totalPages: 0,
      isLoading: false,
    }
  },
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにモードを変更する
    this.initPage(to)
    next()
  },
  created() {
    this.$router.app.$on('search', this.handleSearch)
    this.initPage()
  },
  beforeDestroy() {
    this.$router.app.$off('search', this.handleSearch)
  },
  methods: {
    initPage(route = this.$route) {
      this.mode = route.params.mode !== 'search' ? route.params.mode : ''
      this.searchValue = decodeURI(route.query.q || '')
      this.page = Number(route.query.page || 1)
      this.totalItems = 0
      this.totalPages = 0

      this.fetchBookList()

      this.$nextTick(() => {
        this.$router.app.$emit('changeSearchValue', this.searchValue)
      })
    },
    fetchBookList() {
      this.isLoading = true
      this.items = []

      return api
        .get('/book_copy/', {
          params: {
            page: this.page,
            status: this.mode,
            q: this.searchValue,
          },
        })
        .then(({ data }) => {
          this.totalItems = data.count
          this.totalPages = data.totalPages
          this.items.push(...data.results)

          return Promise.resolve()
        })
        .catch((err) => {
          // FIXME: 最後のページ数+1が二重に読み込まれてしまうバグあり
          // (動作上問題はない)
          return Promise.reject(err)
        })
        .finally(() => {
          this.isLoading = false
        })
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
    handleSearch(searchValue) {
      this.$router.push({
        path: '/shelf/search',
        query: searchValue
          ? {
              q: encodeURI(searchValue),
            }
          : null,
      })
    },
    handlePagination() {
      const pageQuery = { ...this.$route.query }
      pageQuery.page = this.page

      this.$router.push({
        path: this.$route.path,
        query: pageQuery,
      })
    },
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusAdd(item, true)
    },
  },
}
</script>
