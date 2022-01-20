<template>
  <v-card v-bind="$attrs">
    <v-card-title class="mx-3 mt-3">読書データ</v-card-title>
    <v-card-text>
      <v-list>
        <template v-for="(item, index) in bookAnalytics">
          <div :key="index">
            <v-list-item :to="item.to">
              <v-list-item-icon>
                <v-icon v-text="item.icon" :color="item.color"></v-icon>
              </v-list-item-icon>
              {{ item.title }}
              <v-spacer></v-spacer>
              <strong>{{ item.value }} 冊</strong>
            </v-list-item>
            <v-divider v-if="index + 1 < bookAnalytics.length"></v-divider>
          </div>
        </template>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    numOfBooks: { type: Object, require: true },
  },
  data: () => ({
    bookAnalytics: [],
  }),
  created() {
    // 読書冊数データ
    this.bookAnalytics = [
      {
        title: '読んだ本',
        icon: 'mdi-book-check',
        color: 'green',
        value: this.numOfBooks.read,
        to: '/shelf/read',
      },
      {
        title: '読んでいる本',
        icon: 'mdi-book-open-variant',
        color: 'blue',
        value: this.numOfBooks.reading,
        to: '/shelf/reading',
      },
      {
        title: 'あとで読む',
        icon: 'mdi-book-clock',
        color: 'orange',
        value: this.numOfBooks.to_be_read,
        to: '/shelf/to_be_read',
      },
    ]
  },
}
</script>
