<template>
  <v-card class="overflow-hidden" v-bind="$attrs">
    <v-card-title class="mx-3 mt-3">最近読んだ／追加した本</v-card-title>

    <v-card-text class="pb-0">
      <v-sheet flat class="overflow-y-auto" height="200px" outlined>
        <v-list v-if="items.length">
          <template v-for="(book, index) in items">
            <div :key="index">
              <v-list-item :to="`/book/detail/${book.id}`">
                <v-list-item-avatar tile size="50px">
                  <v-img contain :src="book.thumbnail"></v-img>
                </v-list-item-avatar>

                <v-list-item-content>
                  <v-list-item-title class="text-body-2">
                    {{ book.title }}
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-divider v-if="index + 1 < items.length"></v-divider>
            </div>
          </template>
        </v-list>

        <template v-else>
          <div class="text-center py-5">記録が見つかりません。</div>
        </template>
      </v-sheet>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text color="primary" to="/shelf/all">もっと見る</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    items: { type: Array, require: true },
  },
}
</script>
