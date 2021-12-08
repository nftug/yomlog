<template>
  <v-card id="book-detail-info" outlined>
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
          <v-chip class="mt-3" v-text="state" :color="stateColor"></v-chip>
        </v-col>
        <v-col sm="6" cols="12">
          <v-progress-circular
            :size="100"
            :width="15"
            :rotate="-90"
            :value="progress(item)"
            color="teal"
            class="text-center text-body-2"
          >
            {{ progress(item) }}%
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
  computed: {
    state() {
      const state = this.item.status[0].state
      if (state === 'to_be_read') {
        return '積読中'
      } else if (state === 'reading') {
        return '読書中'
      } else {
        return '読了'
      }
    },
    stateColor() {
      const state = this.item.status[0].state
      if (state === 'to_be_read') {
        return ''
      } else if (state === 'reading') {
        return 'primary'
      } else {
        return 'success'
      }
    },
  },
}
</script>
