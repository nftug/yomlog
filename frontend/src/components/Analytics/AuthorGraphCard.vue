<template>
  <v-card v-bind="$attrs">
    <v-card-title class="mx-3 mt-3">{{ title }}</v-card-title>
    <v-card-text class="pb-0">
      <v-row justify="center">
        <GraphDoughnut
          :data="graphData"
          :options="options"
          :width="width"
          :height="height"
          :styles="{ display: 'flex', 'justify-content': 'center' }"
        ></GraphDoughnut>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <slot name="footer"></slot>
    </v-card-actions>
  </v-card>
</template>

<script>
import GraphDoughnut from '@/components/Common/GraphDoughnut.vue'

export default {
  components: { GraphDoughnut },
  props: {
    title: { type: String, default: 'トップの著者' },
    data: { type: Array, require: true },
    colors: {
      type: Array,
      default: () => [
        '#0288D1',
        '#039BE5',
        '#03A9F4',
        '#29B6F6',
        '#4FC3F7',
        '#81D4FA',
        '#B3E5FC',
        '#E1F5FE',
      ],
    },
    options: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: 'right',
        },
      }),
    },
    width: { type: Number, require: false },
    height: { type: Number, require: false },
  },
  data: () => ({
    graphData: {},
  }),
  created() {
    // 著者ランキングデータ
    this.graphData = {
      labels: this.graphDataSet.labels,
      datasets: [
        {
          data: this.graphDataSet.counts,
          backgroundColor: this.colors,
        },
      ],
    }
  },
  computed: {
    graphDataSet() {
      return {
        labels: this.data.map((item) => item.name),
        counts: this.data.map((item) => item.count),
      }
    },
  },
}
</script>
