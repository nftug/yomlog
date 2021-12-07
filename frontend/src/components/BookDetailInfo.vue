<template>
  <v-card id="book-detail-info" class="text-center" outlined>
    <v-card-text>
      <v-progress-circular
        :size="100"
        :width="15"
        :rotate="-90"
        :value="getProgress(item)"
        color="teal"
        class="text-center text-body-2"
      >
        {{ getProgress(item) }}%
      </v-progress-circular>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
    },
  },
  computed: {
    getProgress() {
      return function (item) {
        if (item.status) {
          return parseInt(
            ((item.status[0].position || 0) / item.total) * 100,
            10
          )
        }
      }
    },
  },
}
</script>
