<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error === 404"></NotFoundPage>

  <v-container v-else fluid>
    <!-- Spinner -->
    <spinner v-if="isLoading"></spinner>

    <v-col v-else sm="10" md="8" class="mx-auto">
      <v-row class="pb-5">
        <v-col cols="12" sm="9">
          <!-- 書籍情報 -->
          <div class="text-h6 my-2 font-weight-bold" v-text="item.title"></div>
          <div class="text-body-2 mb-sm-5">
            <span v-for="(author, index) in item.authors" :key="index">
              <router-link
                :to="`/shelf/all/?authors=${author}`"
                v-text="author"
              ></router-link>
              <span v-if="index + 1 < item.authors.length" v-text="', '"></span>
            </span>
          </div>

          <BookDetailMenu
            :item="item"
            class="my-2 hidden-xs-only"
            @reload="fetchBookData"
          ></BookDetailMenu>
        </v-col>

        <v-col cols="12" sm="3">
          <v-img
            contain
            :src="item.thumbnail || noImage"
            max-height="185"
            min-height="185"
          ></v-img>
        </v-col>
      </v-row>

      <BookDetailMenu
        :item="item"
        class="my-2 hidden-sm-and-up"
        @reload="fetchBookData"
      ></BookDetailMenu>

      <!-- 状態表示 -->
      <BookDetailInfo :item="item" class="my-4"></BookDetailInfo>
    </v-col>
  </v-container>
</template>

<script>
import api from '@/services/api'
import Spinner from 'vue-simple-spinner'
import NotFoundPage from '@/pages/error/NotFoundPage.vue'
import Mixins, { BookListMixin, ShelfSearchFromHeaderMixin } from '@/mixins'
import BookDetailInfo from '@/components/BookDetailInfo.vue'
import BookDetailMenu from '@/components/BookDetailMenu.vue'

export default {
  mixins: [Mixins, BookListMixin, ShelfSearchFromHeaderMixin],
  components: {
    NotFoundPage,
    Spinner,
    BookDetailInfo,
    BookDetailMenu,
  },
  data: () => ({
    item: {},
    isLoading: false,
    error: null,
    noImage: 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
  }),
  async created() {
    this.item = await this.$store.dispatch(
      'bookList/getBookItem',
      this.$route.params.id
    )

    if (!Object.keys(this.item).length) {
      this.fetchBookData()
    }
  },
  methods: {
    fetchBookData() {
      this.isLoading = true
      api
        .get(`/book/${this.$route.params.id}/`)
        .then(({ data }) => {
          this.fixStatus(data)

          if (this.bookList.items.length) {
            // this.$store.commit('bookList/set', data)
            if (
              JSON.stringify(this.item.status[0]) !==
              JSON.stringify(data.status[0])
            ) {
              this.$store.commit('bookList/setDirty', true)
            }
          }

          this.item = data
        })
        .catch(({ response }) => {
          this.error = response.status
        })
        .finally(() => {
          this.isLoading = false
        })
    },
  },
}
</script>
