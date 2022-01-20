<template>
  <v-card class="text-center" v-bind="$attrs">
    <v-row class="mx-auto my-3">
      <template v-for="(item, index) in analytics">
        <v-col cols="6" md="3" :key="index">
          <div class="text-body-2" v-text="item.title"></div>
          <div class="text-h5 mt-1">
            {{ item.value }}
            <span class="text-body-2">{{ item.unit }}</span>
          </div>
        </v-col>
      </template>
    </v-row>
  </v-card>
</template>

<script>
export default {
  props: {
    numOfBooks: { type: Object, require: true },
    pages: { type: Object, require: true },
    days: { type: Object, require: true },
  },
  data: () => ({
    analytics: [],
  }),
  created() {
    //分析データ
    this.analytics = [
      {
        title: '読んだ本',
        value: this.numOfBooks.read,
        unit: '冊',
      },
      {
        title: '読んだページ数',
        value: this.pages.total,
        unit: 'ページ',
      },
      {
        title: '一日の平均',
        value: this.pages.avg_per_day,
        unit: 'ページ',
      },
      {
        title: '連続読書日数',
        value: this.days.continuous,
        unit: '日',
      },
    ]
  },
}
</script>
