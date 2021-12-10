<template>
  <v-card id="book-detail-info" outlined v-if="item.status">
    <v-card-text>
      <v-row class="col-lg-8 mx-auto text-center">
        <v-col sm="6" cols="12">
          現在の進捗
          <div class="text-h5">
            {{ item.status[0].position }} / {{ item.total }}
            <span class="text-body-2">
              {{ item.format_type ? '' : 'ページ' }}
            </span>
          </div>
          <v-chip class="mt-3" :color="item.status[0].state | stateColor">
            {{ item.status[0].state | stateName }}
          </v-chip>
        </v-col>
        <v-col sm="6" cols="12">
          <v-progress-circular
            :size="100"
            :width="15"
            :rotate="-90"
            :value="item | bookProgress"
            color="teal"
            class="text-center"
          >
            {{ item | bookProgress }}%
          </v-progress-circular>
        </v-col>
      </v-row>
    </v-card-text>
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
}
</script>
