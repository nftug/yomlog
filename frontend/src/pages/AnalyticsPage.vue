<template>
  <v-container>
    <v-col sm="10" lg="9" xl="7" class="mx-auto">
      <!-- 範囲選択 -->
      <v-row justify-content="end">
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-col cols="12" md="5">
          <div class="d-flex">
            <v-select
              placeholder="日付の範囲"
              :items="dateRanges"
              v-model="dateRange"
              @input="onChangeDateRange"
              dense
            ></v-select>
            <v-btn class="ml-3" elevation="1" @click="selectDateRangeManually">
              <v-icon left>mdi-calendar</v-icon>
              日付指定
            </v-btn>
          </div>
        </v-col>
        <DateRangeDialog ref="dateRange" hash="date-range"></DateRangeDialog>
      </v-row>

      <!-- Spinner -->
      <Spinner v-if="isLoading"></Spinner>

      <template v-else>
        <!-- 分析カード -->
        <AnalyticsCard
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
        <v-card class="mt-8 mx-auto" id="paged-list" outlined>
          <v-simple-table>
            <thead>
              <tr>
                <th class="text-left">日付</th>
                <th class="text-left">ページ数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in pagedList" :key="index">
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
      </template>
    </v-col>
  </v-container>
</template>

<script>
import { ListViewMixin } from '@/mixins'
import api from '@/services/api'
import moment from 'moment'
import Spinner from '@/components/Common/Spinner.vue'
import DateRangeDialog from '@/components/Dialog/DateRangeDialog.vue'
import AnalyticsCard from '@/components/Analytics/AnalyticsCard.vue'
import PagesGraphCard from '@/components/Analytics/PagesGraphCard.vue'
import Pagination from '@/components/Common/Pagination.vue'

export default {
  mixins: [ListViewMixin],
  components: {
    Spinner,
    DateRangeDialog,
    AnalyticsCard,
    PagesGraphCard,
    Pagination,
  },
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
      dateRangeOld: null,
      ranges: [7, 30, 90, 180, 365, 'all', 'user'],
      pageSize: 31,
    }
  },
  beforeRouteUpdate(to, from, next) {
    const toQuery = { ...to.query, page: null }
    const fromQuery = { ...from.query, page: null }

    const isSameParams =
      JSON.stringify(to.params) === JSON.stringify(from.params)
    const isSameQuery = JSON.stringify(toQuery) === JSON.stringify(fromQuery)

    if (!(isSameParams && isSameQuery)) {
      this.initPage({ route: to })
    }
    next()
  },
  created() {
    // セレクトボックスの初期化
    for (const range of this.ranges) {
      let text
      if (range === 'all') {
        text = '全ての期間'
      } else if (range === 'user') {
        text = 'ユーザー指定'
      } else {
        text = `過去${range}日間`
      }

      this.dateRanges.push({ text, value: range })
    }

    this.initPage()
  },
  watch: {
    dateRange(newVal, oldVal) {
      this.dateRangeOld = oldVal
    },
  },
  computed: {
    pagedList() {
      const start = (this.page - 1) * this.pageSize
      const end = start + this.pageSize
      return this.pagesDaily.slice(start, end)
    },
  },
  methods: {
    initPage({ route = this.$route } = {}) {
      this.query = { ...route.query }

      // 日付範囲クエリの設定 & セレクトボックスのデフォルト値の設定
      if (route.query.created_at_after || route.query.created_at_before) {
        this.dateRange = 'user'
      } else if (route.query.days_range === 'all') {
        this.dateRange = 'all'
      } else {
        let days_range = Number(route.query.days_range)
        if (!this.ranges.includes(days_range)) days_range = 30

        this.query.created_at_after = moment()
          .subtract(days_range, 'days')
          .format('yyyy-MM-DD')
        this.query.created_at_before = moment().format('yyyy-MM-DD')

        const target = this.dateRanges.find((item) => item.value === days_range)
        this.dateRange = target.value
      }

      this.fetchAnalyticsData()
      this.fetchPagesDailyData()

      this.page = Number(route.query.page || 1)
    },
    async onChangeDateRange(value) {
      if (value === 'user') {
        try {
          await this.selectDateRangeManually()
        } catch {
          this.dateRange = this.dateRangeOld
        }
      } else {
        this.$router.push({
          query: { days_range: value },
        })
      }
    },
    async selectDateRangeManually() {
      // ダイアログから範囲を入力して、クエリを指定
      try {
        const { start, end } = await this.$refs.dateRange.showDateRangeDialog({
          start: this.graphRange.start,
          end: this.graphRange.end,
        })
        setTimeout(() => {
          this.$router.push({
            query: { created_at_after: start, created_at_before: end },
          })
        }, 100)
      } catch (error) {
        throw error
      }
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
    async fetchPagesDailyData() {
      const { data } = await api.get('/pages/', {
        params: { ...this.query },
      })
      this.pagesDaily = data.map((item) => item)

      this.total = this.pagesDaily.length
      this.totalPages = Math.ceil(this.pagesDaily.length / this.pageSize)

      if (this.total) {
        this.graphRange = {
          start:
            this.query.created_at_after || this.pagesDaily[this.total - 1].date,
          end: this.query.created_at_before || moment().format('yyyy-MM-DD'),
        }
      } else {
        this.graphRange = {
          start: moment(this.$store.state.auth.date_joined).format(
            'yyyy-MM-DD'
          ),
          end: this.query.created_at_before || moment().format('yyyy-MM-DD'),
        }
      }
    },
  },
}
</script>
