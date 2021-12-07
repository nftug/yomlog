<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error === 404"></NotFoundPage>

  <v-container v-else fluid>
    <!-- Spinner -->
    <spinner v-if="isLoading"></spinner>

    <v-col v-else sm="10" class="mx-auto">
      <v-card class="mx-auto" outlined>
        <v-card-text>
          <div class="d-sm-flex flex-row">
            <v-img
              contain
              :src="item.thumbnail || noImage"
              max-height="185"
              min-height="185"
            ></v-img>

            <v-list-item>
              <v-list-item-content>
                <v-list-item-title
                  v-text="item.title"
                  class="font-weight-medium"
                ></v-list-item-title>
                <v-list-item-subtitle>
                  <span v-for="(author, index) in item.authors" :key="index">
                    <router-link :to="`/shelf/all/?authors=${author}`">
                      {{ author }}
                    </router-link>
                    <span v-if="index + 1 < item.authors.length">,</span>
                  </span>
                </v-list-item-subtitle>

                <div class="text-center">
                  <div class="pt-5 mx-auto d-flex flex-row">
                    <v-progress-circular
                      :size="100"
                      :width="15"
                      :rotate="-90"
                      :value="getProgress(item)"
                      color="teal"
                      class="text-center"
                    >
                      進捗度
                      <br />
                      {{ getProgress(item) }}%
                    </v-progress-circular>
                  </div>
                </div>
              </v-list-item-content>
            </v-list-item>
          </div>
        </v-card-text>
      </v-card>

      <div class="text-center"></div>
    </v-col>
  </v-container>
</template>

<script>
import api from '@/services/api'
import Spinner from 'vue-simple-spinner'
import NotFoundPage from '@/pages/error/NotFoundPage.vue'
import Mixins, { BookListMixin, ShelfSearchFromHeaderMixin } from '@/mixins'

export default {
  mixins: [Mixins, BookListMixin, ShelfSearchFromHeaderMixin],
  components: {
    NotFoundPage,
    Spinner,
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
  methods: {
    fetchBookData() {
      this.isLoading = true
      api
        .get(`/book_copy/${this.$route.params.id}/`)
        .then(({ data }) => {
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
