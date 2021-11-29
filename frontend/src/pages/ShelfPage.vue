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
  </v-container>
</template>

<script>
import BookList from '@/components/BookList.vue'
import Spinner from 'vue-simple-spinner'
import InfiniteLoading from 'vue-infinite-loading'
import Mixins from '@/mixins'
import api from '@/services/api'

export default {
  mixins: [Mixins],
  components: {
    Spinner,
    InfiniteLoading,
    BookList,
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
    this.mode = to.params.mode
    this.resetInfinite()
    next()
  },
  methods: {
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
          console.log('Completed')
          $state.complete()
        })
    },
    resetInfinite() {
      this.infiniteId++
      this.page = 1
      this.items = []
    },
  },
}
</script>
