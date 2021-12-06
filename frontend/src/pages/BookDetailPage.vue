<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error === 404"></NotFoundPage>

  <v-container v-else fluid>
    <!-- Spinner -->
    <spinner v-if="isLoading"></spinner>

    <template v-else>
      <v-col sm="10" class="mx-auto">
        {{ item.title }}
      </v-col>
    </template>
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
