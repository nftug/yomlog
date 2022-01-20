<template>
  <v-container>
    <v-col sm="10" lg="9" xl="7" class="mx-auto">
      <!-- 分析カード -->
      <Spinner v-if="isLoading"></Spinner>
      <AnalyticsCard
        v-else
        class="mx-auto"
        :num-of-books="analytics.number_of_books"
        :pages="analytics.pages_read"
        :days="analytics.days"
        outlined
      ></AnalyticsCard>

      <!-- ページ数集計グラフ -->
      <PagesGraphCard
        title="期間内の読書量"
        :data="pagesDaily"
        :start="query.created_at_after"
        :end="query.created_at_before"
        no-label
        class="mt-4 pb-4 mx-auto"
        outlined
      ></PagesGraphCard>

      <!-- ページ数集計テーブル -->
      <v-card class="mt-8 mx-auto">
        <v-simple-table>
          <thead>
            <tr>
              <th class="text-left">日付</th>
              <th class="text-left">ページ数</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(item, index) in pagesDaily">
              <tr v-if="item.pages > 0" :key="index">
                <td>
                  {{ item.date }}
                </td>
                <td>{{ item.pages }}</td>
              </tr>
            </template>
          </tbody>
        </v-simple-table>
      </v-card>
    </v-col>
  </v-container>
</template>

<script>
import api from '@/services/api'
import moment from 'moment'
import Spinner from '@/components/Common/Spinner.vue'
import AnalyticsCard from '@/components/Analytics/AnalyticsCard.vue'
import PagesGraphCard from '@/components/Analytics/PagesGraphCard.vue'

export default {
  components: { Spinner, AnalyticsCard, PagesGraphCard },
  data: () => ({
    analytics: {},
    pagesDaily: [],
    page: 0,
    total: 0,
    totalPages: 0,
    isLoading: false,
    query: {},
  }),
  beforeRouteUpdate(to, from, next) {
    const isSameParams =
      JSON.stringify(to.params) === JSON.stringify(from.params)
    const isSameQuery = JSON.stringify(to.query) === JSON.stringify(from.query)

    if (!(isSameParams && isSameQuery)) {
      this.fetchAnalyticsData({ route: to })
      this.fetchPagesDailyData({ route: to })
    }
    next()
  },
  created() {
    this.fetchAnalyticsData()
    this.fetchPagesDailyData()
  },
  methods: {
    async fetchAnalyticsData({ route = this.$route } = {}) {
      try {
        this.isLoading = true
        const { data } = await api.get('/analytics/', {
          params: { ...route.query },
        })
        this.analytics = data
      } finally {
        this.isLoading = false
      }
    },
    async fetchPagesDailyData({ route = this.$route } = {}) {
      this.page = Number(route.query.page || 1)
      const page = this.page
      this.query = { ...route.query }
      this.pagesDaily = []

      if (!(this.query.created_at_after || this.query.created_at_before)) {
        // 日付範囲のパラメータが存在しない場合、今月初めから今日までの範囲を表示
        this.query.created_at_after = moment()
          .startOf('month')
          .format('yyyy-MM-DD')
        this.query.created_at_before = moment().format('yyyy-MM-DD')
      }

      const { data } = await api.get('/pages/', {
        params: { ...this.query, page },
      })
      this.total = data.count
      this.totalPages = data.totalPages
      data.results.forEach((item) => {
        this.pagesDaily.push(item)
      })
    },
  },
}
</script>
