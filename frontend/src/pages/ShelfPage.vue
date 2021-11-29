<template>
  <v-container fluid>
    <div class="col-sm-10 mx-auto">
      <!-- 本棚 -->
      <BookList :items="items"></BookList>

      <!-- Infinite Loading -->
      <infinite-loading @infinite="infiniteHandler" :identifier="infiniteId">
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

    <!-- スクロール -->
    <Fab icon="mdi-chevron-up" @click="onClickFab"></Fab>
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Spinner from 'vue-simple-spinner'
import InfiniteLoading from 'vue-infinite-loading'
import Mixins from '@/mixins'
import api from '@/services/api'
import VueScrollTo from 'vue-scrollto'
import Fab from '@/components/Fab.vue'

export default {
  mixins: [Mixins],
  components: {
    Spinner,
    InfiniteLoading,
    BookList,
    Fab,
  },
  data() {
    return {
      infiniteId: +new Date(),
      items: [],
      page: 1,
      mode: this.$route.params.mode,
      searchValue: '',
      total: 0,
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
      this.mode = route.params.mode
      this.searchValue = decodeURI(route.query.q || '')
      this.$nextTick(() => {
        this.$router.app.$emit('changeSearchValue', this.searchValue)
      })

      this.resetInfinite()
    },
    fetchBookList() {
      return api
        .get('/book_copy/', {
          params: {
            page: this.page,
            status: this.mode,
            q: this.searchValue,
          },
        })
        .then(({ data }) => {
          this.total = data.totalItems
          this.items.push(...data.results)

          return Promise.resolve()
        })
        .catch((err) => {
          // FIXME: 最後のページ数+1が二重に読み込まれてしまうバグあり
          // (動作上問題はない)
          return Promise.reject(err)
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
    resetInfinite() {
      this.infiniteId++
      this.page = 1
      this.items = []
    },
    handleSearch(searchValue) {
      this.$router.push({
        path: this.$route.path,
        query: searchValue
          ? {
              q: encodeURI(searchValue),
            }
          : null,
      })
    },
    onClickFab() {
      VueScrollTo.scrollTo('#app')
    },
  },
}
</script>
