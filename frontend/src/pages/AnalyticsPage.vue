<template>
  <v-container>
    <v-col sm="10" lg="9" xl="7" class="mx-auto">
      <!-- 範囲選択 -->
      <v-row justify-content="end">
        <v-spacer></v-spacer>
        <v-col cols="12" sm="7" md="5" lg="4" xl="3">
          <v-select
            placeholder="日付の範囲"
            :items="dateRanges"
            v-model="dateRange"
            @change="onChangeDateRange"
            dense
          ></v-select>
        </v-col>
      </v-row>

      <!-- 分析カード -->
      <AnalyticsCard
        v-if="!isLoading"
        :num-of-books="analytics.number_of_books"
        :pages="analytics.pages_read"
        :days="analytics.days"
        outlined
      ></AnalyticsCard>

      <!-- ページ数集計グラフ -->
      <PagesGraphCard
        title="期間内の読書量"
        :data="pagesDaily"
        :start="graphRange.start"
        :end="graphRange.end"
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
            <tr v-for="(item, index) in pagesDailyList" :key="index">
              <td>
                {{ item.date }}
              </td>
              <td>{{ item.pages }}</td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card>

      <!-- ページネーション -->
      <Pagination
        v-model="page"
        :length="totalPages"
        :total-visible="5"
      ></Pagination>
    </v-col>
  </v-container>
</template>

<script>
import { ListViewMixin } from '@/mixins'
import api from '@/services/api'
import moment from 'moment'
import AnalyticsCard from '@/components/Analytics/AnalyticsCard.vue'
import PagesGraphCard from '@/components/Analytics/PagesGraphCard.vue'
import Pagination from '@/components/Common/Pagination.vue'

export default {
  mixins: [ListViewMixin],
  components: { AnalyticsCard, PagesGraphCard, Pagination },
  data() {
    return {
      analytics: {},
      pagesDaily: [],
      page: 0,
      total: 0,
      totalPages: 0,
      isLoading: false,
      query: {},
      graphRange: {},
      dateRanges: [],
      dateRange: 30,
      ranges: [7, 30, 90, 180, 365, 'all'],
    }
  },
  beforeRouteUpdate(to, from, next) {
    const isSameParams =
      JSON.stringify(to.params) === JSON.stringify(from.params)
    const isSameQuery = JSON.stringify(to.query) === JSON.stringify(from.query)

    if (!(isSameParams && isSameQuery)) {
      this.initPage({ route: to })
    }
    next()
  },
  created() {
    // セレクトボックスの初期化
    for (const range of this.ranges) {
      this.dateRanges.push({
        text: range === 'all' ? '全ての期間' : `過去${range}日間`,
        value: range,
      })
    }

    this.initPage()
  },
  computed: {
    pagesDailyList() {
      // 進捗0ページを除いたpagesDailyのリストを取得
      return this.pagesDaily.filter((item) => item.pages > 0)
    },
  },
  methods: {
    initPage({ route = this.$route } = {}) {
      this.query = { ...route.query }

      // 日付範囲クエリの設定 & セレクトボックスのデフォルト値の設定
      if (route.query.days_range !== 'all') {
        let days_range = Number(route.query.days_range)
        if (!this.ranges.includes(days_range)) days_range = 30

        this.query.created_at_after = moment()
          .subtract(days_range, 'days')
          .format('yyyy-MM-DD')
        this.query.created_at_before = moment().format('yyyy-MM-DD')

        const target = this.dateRanges.find((item) => item.value === days_range)
        this.dateRange = target.value
      } else {
        this.dateRange = 'all'
      }

      this.fetchAnalyticsData()
      this.fetchPagesDailyData({ route })
    },
    onChangeDateRange(value) {
      this.$router.push({
        ...this.$route,
        query: { days_range: value },
      })
    },
    async fetchAnalyticsData() {
      try {
        this.isLoading = true
        const { data } = await api.get('/analytics/', {
          params: { ...this.query },
        })
        this.analytics = data
      } finally {
        this.isLoading = false
      }
    },
    async fetchPagesDailyData({ route = this.$route } = {}) {
      this.page = Number(route.query.page || 1)
      const page = this.page
      this.pagesDaily = []

      try {
        const { data } = await api.get('/pages/', {
          params: { ...this.query, page },
        })
        data.results.forEach((item) => {
          this.pagesDaily.push(item)
        })

        this.total = this.pagesDailyList.length
        this.totalPages = Math.ceil(this.pagesDailyList.length / data.pageSize)

        const dataLen = this.pagesDaily.length
        if (dataLen) {
          this.graphRange = {
            start: this.pagesDaily[dataLen - 1].date,
            end: this.pagesDaily[0].date,
          }
        }
      } catch (error) {
        if (error.response) {
          const { response } = error
          if (response.status === 404) {
            // ページ数超過の場合、最終ページに遷移
            const params = { ...response.config.params }
            this.replaceWithFinalPage('/pages/', params)
          }
        }
      }
    },
  },
}
</script>
