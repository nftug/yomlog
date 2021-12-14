<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error === 404"></NotFoundPage>

  <v-container v-else fluid>
    <!-- Spinner -->
    <spinner v-if="isLoading"></spinner>

    <v-col v-else sm="10" md="8" xl="7" class="mx-auto">
      <v-row class="pb-4">
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
            @post-status="onAddProp('status', $event)"
            @post-note="onAddProp('notes', $event)"
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
        @post-status="onAddProp('status', $event)"
        @post-note="onAddProp('notes', $event)"
      ></BookDetailMenu>

      <!-- 状態表示 -->
      <div class="pb-4">
        <BookDetailInfo :item="item"></BookDetailInfo>
      </div>

      <!-- 進捗とメモ -->
      <div class="pb-5">
        <v-tabs v-model="tab" background-color="transparent" grow>
          <v-tab v-for="item in tabs" :key="item">
            {{ item }}
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item>
            <StatusLog
              v-if="item.status"
              :item="item"
              height="600"
              @edit="onEditProp('status', $event)"
              @delete="onDeleteProp('status', $event)"
            ></StatusLog>
          </v-tab-item>
          <v-tab-item>
            <NoteList
              v-if="item.notes"
              :item="item"
              height="600"
              @edit="onEditProp('notes', $event)"
              @delete="onDeleteProp('notes', $event)"
            ></NoteList>
          </v-tab-item>
          <v-tab-item>Calender</v-tab-item>
        </v-tabs-items>
      </div>
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
import StatusLog from '@/components/StatusLog.vue'
import NoteList from '@/components/NoteList.vue'

export default {
  mixins: [Mixins, BookListMixin, ShelfSearchFromHeaderMixin],
  components: {
    NotFoundPage,
    Spinner,
    BookDetailInfo,
    BookDetailMenu,
    StatusLog,
    NoteList,
  },
  data: () => ({
    item: {},
    isLoading: false,
    error: null,
    noImage: 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
    tab: 0,
    tabs: ['進捗', 'ノート', 'カレンダー'],
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
          this.item = data
        })
        .catch((error) => {
          if (error.response) this.error = error.response.status
        })
        .finally(() => {
          this.isLoading = false
        })
    },
    onAddProp(prop, data) {
      this.setDirtyWithDiffState(this.item, (item) => {
        item[prop].unshift(data)
      })
    },
    onDeleteProp(prop, id) {
      this.setDirtyWithDiffState(this.item, (item) => {
        const index = item[prop].findIndex((e) => e.id === id)
        item[prop].splice(index, 1)
      })
    },
    onEditProp(prop, data) {
      this.setDirtyWithDiffState(this.item, (item) => {
        const index = item[prop].findIndex((e) => e.id === data.id)
        item[prop].splice(index, 1, data)
      })
    },
  },
}
</script>
