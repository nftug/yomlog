<template>
  <div id="book-detail-menu">
    <v-btn
      color="orange"
      small
      dark
      :href="amazonLink"
      target="_blank"
      rel="noopener noreferrer"
    >
      Amazonを見る
    </v-btn>

    <v-menu offset-y close-on-click>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="ml-2"
          color="secondary"
          dark
          v-bind="attrs"
          v-on="on"
          small
        >
          書籍を編集
          <v-icon small>mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item link>
          <v-list-item-title>書籍の編集</v-list-item-title>
        </v-list-item>
        <v-list-item link>
          <v-list-item-title>書籍の削除</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-btn class="ml-2" color="primary" small dark>ノートを追加</v-btn>
    <v-btn class="ml-2" color="success" small dark>進捗の追加</v-btn>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
    },
  },
  computed: {
    amazonLink() {
      return `https://www.amazon.co.jp/s?k=${this.item.amazon_dp}`
    },
  },
}
</script>
