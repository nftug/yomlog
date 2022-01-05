<template>
  <v-container>
    <v-col sm="10" lg="9" xl="7" class="mx-auto">
      <v-card outlined color="transparent" class="py-2">
        <!-- ユーザー情報 -->
        <v-list>
          <v-list-item two-line>
            <v-list-item-avatar color="grey" size="80">
              <img v-if="auth.avatar" :alt="auth.fullname" :src="auth.avatar" />
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
      </v-card>

      <!-- 分析 -->
      <v-card outlined class="text-center">
        <v-row class="mx-auto my-3">
          <template v-for="(item, index) in analytics">
            <v-col cols="6" md="3" :key="index">
              <div class="text-body-2" v-text="item.title"></div>
              <div class="text-h5 mt-1">
                {{ item.value }}
                <span class="text-body-2">{{ item.unit }}</span>
              </div>
            </v-col>
          </template>
        </v-row>
      </v-card>

      <!-- 読書データ -->
      <v-row class="my-3">
        <v-col cols="12" md="6">
          <v-card outlined>
            <v-card-title class="mx-3 mt-3">読書データ</v-card-title>
            <v-card-text>
              <v-list>
                <template v-for="(item, index) in bookAnalytics">
                  <div :key="index">
                    <v-list-item :to="item.to">
                      <v-list-item-icon>
                        <v-icon v-text="item.icon" :color="item.color"></v-icon>
                      </v-list-item-icon>
                      {{ item.title }}
                      <v-spacer></v-spacer>
                      <strong>{{ item.value }} 冊</strong>
                    </v-list-item>
                    <v-divider
                      v-if="index + 1 < bookAnalytics.length"
                    ></v-divider>
                  </div>
                </template>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-col>
  </v-container>
</template>

<script>
import Mixin from '@/mixins'
import { mapGetters, mapState } from 'vuex'

export default {
  mixins: [Mixin],
  data: () => ({
    analytics: [],
    bookAnalytics: [],
  }),
  computed: {
    ...mapState(['auth']),
    ...mapGetters({ created_at: 'auth/created_at' }),
    ...mapState({
      numOfBooks: (state) => state.auth.analytics.number_of_books,
      pages: (state) => state.auth.analytics.pages_read,
      days: (state) => state.auth.analytics.days,
    }),
  },
  created() {
    this.analytics = [
      {
        title: '読んだ本',
        value: this.numOfBooks.read,
        unit: '冊',
      },
      {
        title: '読んだページ数',
        value: this.pages.total,
        unit: 'ページ',
      },
      {
        title: '一日の平均',
        value: this.pages.avg_per_day,
        unit: 'ページ',
      },
      {
        title: '連続読書日数',
        value: this.days.continuous,
        unit: '日',
      },
    ]
    this.bookAnalytics = [
      {
        title: '読んだ本',
        icon: 'mdi-book-check',
        color: 'green',
        value: this.numOfBooks.read,
        to: '/shelf/read',
      },
      {
        title: '読んでいる本',
        icon: 'mdi-book-open-variant',
        color: 'blue',
        value: this.numOfBooks.reading,
        to: '/shelf/reading',
      },
      {
        title: 'あとで読む',
        icon: 'mdi-book-clock',
        color: 'orange',
        value: this.numOfBooks.to_be_read,
        to: '/shelf/to_be_read',
      },
    ]
  },
}
</script>
