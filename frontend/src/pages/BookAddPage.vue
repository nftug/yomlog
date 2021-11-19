<template>
  <v-container fluid>
    <div class="col-md-8 col-sm-10 mx-auto">
      <v-text-field
        v-model="searchValue"
        label="検索キーワード"
        prepend-icon="mdi-magnify"
        clearable
        @keydown.enter="doSearch()"
      ></v-text-field>

      <v-subheader>
        Google Booksからの検索結果 ({{ totalForGoogle }}件)
      </v-subheader>
      <v-row>
        <v-col v-for="item in itemsForGoogle" :key="item.id" cols="12" lg="6">
          <v-card class="mx-auto" height="185">
            <v-row no-gutters>
              <v-col cols="8">
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      v-text="item.title"
                      class="font-weight-medium"
                    ></v-list-item-title>
                    <v-list-item-subtitle
                      v-text="item.authors.join(', ')"
                    ></v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-col>

              <v-col cols="4">
                <v-img
                  contain
                  :src="
                    item.imageLinks ? item.imageLinks.thumbnail : noImageCover
                  "
                  max-height="185"
                  min-height="185"
                ></v-img>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data: () => ({
    noImageCover:
      'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
    searchValue: '',
    itemsForGoogle: [],
    totalForGoogle: 0,
    pageForGoogle: 1,
    infiniteId: +new Date(),
  }),
  methods: {
    doSearch() {
      // TODO: 無限スクロールに対応させる
      if (this.searchValue) {
        // TODO: クリア処理を無限スクロール関連のメソッドに移す
        this.itemsForGoogle = []

        axios
          .get('https://www.googleapis.com/books/v1/volumes', {
            params: {
              q: this.searchValue,
              orderBy: 'relevance',
            },
          })
          .then(({ data }) => {
            this.totalForGoogle = data.totalItems
            data.items.forEach((item) => {
              item.volumeInfo.authors = item.volumeInfo.authors || ['不明']
              this.itemsForGoogle.push(item.volumeInfo)
            })
          })
      }
    },
  },
}
</script>
