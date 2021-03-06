<template>
  <v-container>
    <!-- Spinner -->
    <Spinner v-if="isLoading"></Spinner>

    <template v-else-if="authors.length">
      <v-col sm="10" lg="9" xl="7" class="mx-auto">
        <!-- 件数 -->
        <div class="mx-auto text-body-2 pa-2">
          <strong>{{ total }}名</strong>
          の著者が見つかりました。
        </div>

        <!-- トップ10のグラフ -->
        <AuthorGraphCard
          title="トップ10の著者"
          :data="authorsTop"
          :height="245"
          outlined
          class="mt-4 pb-4 mx-auto"
        ></AuthorGraphCard>

        <!-- 著者リストテーブル -->
        <v-card class="mt-8 mx-auto" outlined>
          <v-simple-table>
            <thead>
              <tr>
                <th class="text-left">著者名</th>
                <th class="text-left">冊数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in authors" :key="index">
                <td>
                  <router-link
                    :to="`/shelf/all/?authors=${item.name}`"
                    v-text="item.name"
                  ></router-link>
                </td>
                <td>{{ item.count }}</td>
              </tr>
            </tbody>
          </v-simple-table>
        </v-card>
      </v-col>

      <!-- ページネーション -->
      <Pagination
        v-model="page"
        :length="totalPages"
        :total-visible="5"
      ></Pagination>
    </template>

    <template v-else>
      <div class="text-center text-body-2 py-5">記録が見つかりません。</div>
    </template>
  </v-container>
</template>

<script>
import { ListViewMixin } from '@/mixins'
import api from '@/services/api'
import AuthorGraphCard from '@/components/Analytics/AuthorGraphCard.vue'
import Spinner from '@/components/Common/Spinner.vue'
import Pagination from '@/components/Common/Pagination.vue'

export default {
  mixins: [ListViewMixin],
  components: { AuthorGraphCard, Spinner, Pagination },
  data: () => ({
    authors: [],
    authorsTop: [],
    graphOptions: {
      responsive: true,
      maintainAspectRatio: false,
      legend: {
        display: true,
        position: 'top',
      },
    },
    isLoading: false,
    page: 0,
    total: 0,
    totalPages: 0,
  }),
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにリロードする
    const isSameParams =
      JSON.stringify(to.params) === JSON.stringify(from.params)
    const isSameQuery = JSON.stringify(to.query) === JSON.stringify(from.query)

    if (!(isSameParams && isSameQuery)) {
      this.fetchAuthors({ route: to })
    }
    next()
  },
  async mounted() {
    this.fetchAuthors()
  },
  methods: {
    async fetchAuthors({ route = this.$route } = {}) {
      this.page = Number(route.query.page || 1)

      this.isLoading = true
      this.authors = []

      try {
        const { data } = await api.get('/author/', {
          params: { ...route.query, page: this.page },
        })

        this.total = data.count
        this.totalPages = data.totalPages
        data.results.forEach((item) => {
          this.authors.push(item)
        })

        // グラフ用データを作成
        if (!this.authorsTop.length) {
          if (this.page !== 1) {
            const {
              data: { results },
            } = await api.get('/author/', {
              params: { ...route.query, page: 1 },
            })
            this.authorsTop = results.slice(0, 10)
          } else {
            this.authorsTop = this.authors.slice(0, 10)
          }
        }
      } catch (error) {
        if (error.response) {
          const { response } = error
          if (response.status === 404) {
            // ページ数超過の場合、最終ページに遷移
            const params = { ...response.config.params }
            this.replaceWithFinalPage('/author/', params)
          }
        }
      } finally {
        this.isLoading = false
      }
    },
  },
}
</script>
