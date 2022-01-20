<template>
  <v-card v-bind="$attrs">
    <v-card-title class="mx-3 mt-3">{{ title }}</v-card-title>
    <v-card-text class="pb-0">
      <v-sheet class="v-sheet--offset mx-auto" max-width="calc(100% - 32px)">
        <div class="mt-md-6">
          <v-sparkline
            :labels="noLabel ? [] : pagesDaily.date"
            :value="pagesDaily.pages"
            color="primary"
            line-width="2"
            padding="16"
            height="100%"
          ></v-sparkline>
        </div>
      </v-sheet>
    </v-card-text>

    <v-card-actions>
      <slot name="footer"></slot>
    </v-card-actions>
  </v-card>
</template>

<script>
import moment from 'moment'

export default {
  props: {
    title: { type: String, default: '最近の読書量' },
    data: { type: Array, require: true },
    start: { type: String, require: true },
    end: { type: String, require: true },
    noLabel: { type: Boolean, default: false },
  },
  computed: {
    pagesDaily() {
      const keys = Object.keys(this.data)
      keys.sort()

      // 日付範囲で結果の配列を生成
      const [date, pages] = [[], []]
      const [start, end] = [moment(this.start), moment(this.end)]

      for (let d = start; d <= end; d = moment(d).add(1, 'days')) {
        date.push(moment(d).format('MM/DD'))

        const key = moment(d).format('yyyy-MM-DD')
        const index = this.data.findIndex((e) => e.date === key)
        if (index > -1) {
          pages.push(this.data[index].pages)
        } else {
          pages.push(0)
        }
      }

      return { date, pages }
    },
  },
}
</script>
