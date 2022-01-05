<template>
  <v-card id="book-detail-info" class="pa-6" outlined v-if="item.status">
    <v-row class="mx-auto text-center">
      <v-col sm="6" cols="12">
        <div class="text-body-2">現在の進捗</div>
        <div class="text-h5">
          {{ getStateDisplay(item, currentState(item)) }}
          <span class="text-body-2">ページ</span>
        </div>
        <v-chip class="mt-3" :color="currentState(item).state | stateColor">
          {{ currentState(item).state | stateName }}
        </v-chip>
      </v-col>
      <v-col sm="6" cols="12">
        <v-progress-circular
          :size="100"
          :width="15"
          :rotate="-90"
          :value="currentState(item).position.percentage"
          color="teal"
          class="text-center"
        >
          {{ currentState(item).position.percentage }}%
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
    item: {
      type: Object,
    },
  },
  methods: {
    getStateDisplay(book, state) {
      if (state.position.page) {
        return `${state.position.page} / ${book.total_page}`
      } else {
        return `${state.position.value} / ${book.total}`
      }
    },
  },
}
</script>
