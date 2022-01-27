<template>
  <v-card id="book-detail-info" class="pa-6" outlined v-if="book.status">
    <v-row class="mx-auto text-center">
      <v-col sm="6" cols="12">
        <div class="text-body-2">現在の進捗</div>
        <div class="text-h5">
          {{ pageState }}
          <span class="text-body-2">ページ</span>
        </div>
        <v-chip class="mt-3" :color="currentBookState.state | stateColor">
          {{ currentBookState.state | stateName }}
        </v-chip>
      </v-col>
      <v-col sm="6" cols="12">
        <v-progress-circular
          :size="100"
          :width="15"
          :rotate="-90"
          :value="currentBookState.position.percentage"
          color="teal"
          class="text-center"
        >
          {{ currentBookState.position.percentage }}%
        </v-progress-circular>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
import { BookListMixin } from '@/mixins'

export default {
  mixins: [BookListMixin],
  props: {
    book: {
      type: Object,
      require: true,
    },
  },
  computed: {
    pageState() {
      // 進捗状況のページ数を表示
      // 書籍の種類によって分母を変える
      const denominator =
        this.book.format_type === 1 ? this.book.total_page : this.book.total
      return `${this.currentBookState.position.page}  / ${denominator}`
    },
    currentBookState() {
      return this.currentState(this.book)
    },
  },
}
</script>
