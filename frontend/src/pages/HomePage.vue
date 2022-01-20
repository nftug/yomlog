<template>
  <v-container fluid>
    <v-col sm="10" lg="9" xl="7" class="mx-auto">
      <div class="pb-2">
        <!-- ユーザー情報 -->
        <v-list>
          <v-list-item two-line>
            <v-list-item-avatar color="grey" size="80">
              <v-img
                v-if="auth.avatar"
                :alt="auth.fullname"
                :src="auth.avatar"
              />
              <v-icon v-else dark size="80">mdi-account-circle</v-icon>
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title class="text-h6">
                {{ auth.fullname }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ created_at }} に登録
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </div>

      <!-- 分析 -->
      <AnalyticsCard
        :num-of-books="numOfBooks"
        :pages="pages"
        :days="days"
        outlined
      ></AnalyticsCard>

      <!-- 読書データ -->
      <v-row class="my-3">
        <v-col cols="12" md="6">
          <ReadingDataCard
            :num-of-books="numOfBooks"
            class="fill-height"
            outlined
          ></ReadingDataCard>
        </v-col>

        <!-- 最近読んだ/追加した本 -->
        <v-col cols="12" md="6">
          <RecentBooksCard
            :items="recentBooks"
            class="fill-height"
            outlined
          ></RecentBooksCard>
        </v-col>

        <!-- トップ8の著者 -->
        <v-col cols="12" md="6">
          <AuthorGraphCard
            :data="authorsCount"
            :width="graphWidth"
            :height="graphHeight"
            class="fill-height"
            outlined
          ></AuthorGraphCard>
        </v-col>

        <!-- 一日ごとのページ数集計グラフ -->
        <v-col cols="12" md="6">
          <PagesGraphCard
            :data="pagesDaily"
            class="fill-height"
            outlined
          ></PagesGraphCard>
        </v-col>
      </v-row>
    </v-col>
  </v-container>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import AnalyticsCard from '@/components/Analytics/AnalyticsCard.vue'
import ReadingDataCard from '@/components/Analytics/ReadingDataCard.vue'
import RecentBooksCard from '@/components/Analytics/RecentBooksCard.vue'
import AuthorGraphCard from '@/components/Analytics/AuthorGraphCard.vue'
import PagesGraphCard from '@/components/Analytics/PagesGraphCard.vue'

export default {
  components: {
    AnalyticsCard,
    ReadingDataCard,
    RecentBooksCard,
    AuthorGraphCard,
    PagesGraphCard,
  },
  computed: {
    ...mapState(['auth']),
    ...mapGetters({
      created_at: 'auth/created_at',
    }),
    ...mapState({
      numOfBooks: (state) => state.auth.analytics.number_of_books,
      pages: (state) => state.auth.analytics.pages_read,
      days: (state) => state.auth.analytics.days,
      recentBooks: (state) => state.auth.analytics.recent_books,
      authorsCount: (state) => state.auth.analytics.authors_count,
      pagesDaily: (state) => state.auth.analytics.pages_daily,
    }),
    graphHeight() {
      return window.innerHeight / 4
    },
    graphWidth() {
      return window.innerWidth / 4
    },
  },
}
</script>
