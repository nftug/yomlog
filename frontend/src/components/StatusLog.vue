<template>
  <v-list two-line>
    <v-list-item v-for="(state, i) in item.status" :key="i">
      <v-row class="spacer" no-gutters>
        <div class="flex-grow-1">
          <div class="text-h5">
            {{ state.position }} / {{ item.total }}
            <span class="text-body-2">
              {{ item.format_type ? '' : 'ページ' }}
            </span>
          </div>
        </div>

        <v-row dense>
          {{ state.created_at | isoToDateTime }}
        </v-row>
      </v-row>
    </v-list-item>
  </v-list>
</template>

<script>
import Mixins from '@/mixins'

export default {
  mixins: [Mixins],
  props: {
    item: {
      type: Object,
    },
  },
}
</script>
