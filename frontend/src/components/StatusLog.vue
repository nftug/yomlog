<template>
  <v-card outlined class="mx-auto">
    <v-virtual-scroll
      :height="height"
      item-height="76"
      :bench="benched"
      :items="item.status"
    >
      <template #default="{ item: state, index }">
        <v-row class="col-lg-8 mx-auto">
          <v-list-item class="py-3">
            <v-row align="center">
              <v-col class="flex-grow-1 flex-shrink-0">
                <div class="text-lg-h5 text-h6">
                  {{ state.position }} / {{ item.total }}
                  <span class="text-body-2">
                    {{ item.format_type ? '' : 'ページ' }}
                  </span>
                </div>
              </v-col>

              <v-col cols="5" class="flex-grow-0 flex-shrink-0" align="right">
                <div class="text-body-2">
                  {{ state.created_at | isoToDateTime }}
                </div>
                <v-chip small class="mt-2" :color="state.state | stateColor">
                  {{ state.state | stateName }}
                </v-chip>
              </v-col>
            </v-row>
          </v-list-item>
        </v-row>
        <v-divider v-if="index + 1 < item.status.length"></v-divider>
      </template>
    </v-virtual-scroll>
  </v-card>
</template>

<script>
import Mixins, { BookListMixin } from '@/mixins'

export default {
  mixins: [Mixins, BookListMixin],
  props: {
    item: {
      type: Object,
    },
    height: {
      type: String,
      default: '400',
    },
  },
  data: () => ({
    benched: 0,
  }),
}
</script>
