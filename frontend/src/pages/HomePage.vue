<template>
  <v-container fluid>
    <v-col sm="10" class="mx-auto">
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

      <!-- 読書データ -->
      <v-card outlined class="py-4 text-center">
        <v-row class="mx-auto">
          <v-col cols="2" sm="3">
            <div class="text-body-2">読んだ本</div>
            <div class="text-h5 mt-1">
              {{ numOfBooks.read }}
              <span class="text-body-2">冊</span>
            </div>
          </v-col>
          <v-col cols="2" sm="3">
            <div class="text-body-2">読んだページ数</div>
            <div class="text-h5 mt-1">
              {{ pages.total }}
              <span class="text-body-2">ページ</span>
            </div>
          </v-col>
          <v-col cols="2" sm="3">
            <div class="text-body-2">一日の平均</div>
            <div class="text-h5 mt-1">
              {{ pages.avg_per_day }}
              <span class="text-body-2">ページ</span>
            </div>
          </v-col>
          <v-col cols="2" sm="3">
            <div class="text-body-2">連続読書日数</div>
            <div class="text-h5 mt-1">
              {{ days.continuous }}
              <span class="text-body-2">日</span>
            </div>
          </v-col>
        </v-row>
      </v-card>
    </v-col>
  </v-container>
</template>

<script>
import Mixin from '@/mixins'
import { mapGetters, mapState } from 'vuex'

export default {
  mixins: [Mixin],
  computed: {
    ...mapState(['auth']),
    ...mapGetters({ created_at: 'auth/created_at' }),
    ...mapState({
      numOfBooks: (state) => state.auth.analytics.number_of_books,
      pages: (state) => state.auth.analytics.pages_read,
      days: (state) => state.auth.analytics.days,
    }),
  },
}
</script>
