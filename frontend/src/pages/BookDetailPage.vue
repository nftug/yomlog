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
            @post="onAddProp"
            @edit-book="onEditBook"
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
        @post="onAddProp"
        @edit-book="onEditBook"
      ></BookDetailMenu>

      <!-- 状態表示 -->
      <div class="pb-4">
        <BookDetailInfo :item="item"></BookDetailInfo>
      </div>

      <!-- 進捗とメモ -->
      <div class="pb-5" id="tab">
        <v-toolbar v-if="isShowToolbar" flat dense>
          <v-app-bar-nav-icon @click.stop="disableToolbar">
            <v-icon>mdi-arrow-left</v-icon>
          </v-app-bar-nav-icon>
          <v-chip
            class="ma-1"
            v-for="(q, key) in toolbar.query"
            :key="key"
            close
            small
            @click:close="removeQuery(key)"
          >
            {{ key | searchLabel }}
            {{ q }}
          </v-chip>
        </v-toolbar>

        <v-tabs v-else v-model="activeTab" background-color="transparent" grow>
          <v-tab v-for="tab in tabs" :key="tab.prop" :to="tab.path">
            {{ tab.label }}
            <div class="px-2">
              <v-chip small color="grey darken-1" dark>
                {{ item[tab.prop].length }}
              </v-chip>
            </div>
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <v-tab-item v-for="tab in tabs" :key="tab.prop" :value="tab.path">
            <div style="height: 500px">
              <router-view
                v-if="activeTab === tab.path"
                :item="item"
                height="500"
                @edit="onEditProp"
                @delete="onDeleteProp"
                @set="onSetProp"
                @set-toolbar="setToolbar"
              ></router-view>
            </div>
          </v-tab-item>
        </v-tabs-items>
      </div>
    </v-col>
  </v-container>
</template>

<script>
import api from '@/services/api'
import Spinner from 'vue-simple-spinner'
import NotFoundPage from '@/pages/error/NotFoundPage.vue'
import Mixins, {
  BookListMixin,
  ShelfSearchFromHeaderMixin,
  ListViewMixin,
} from '@/mixins'
import BookDetailInfo from '@/components/BookDetailInfo.vue'
import BookDetailMenu from '@/components/BookDetailMenu.vue'

export default {
  mixins: [Mixins, BookListMixin, ShelfSearchFromHeaderMixin, ListViewMixin],
  components: {
    NotFoundPage,
    Spinner,
    BookDetailInfo,
    BookDetailMenu,
  },
  data() {
    return {
      item: {},
      isLoading: false,
      error: null,
      noImage: 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
      activeTab: null,
      toolbar: {},
      tabs: [
        {
          label: '進捗',
          prop: 'status',
          path: `/book/detail/${this.$route.params.id}`,
        },
        {
          label: 'ノート',
          prop: 'note',
          path: `/book/detail/${this.$route.params.id}/note`,
        },
      ],
    }
  },
  async created() {
    // NOTE: ストアから取得するのはアイテムのコピーになる
    // ⇒ページ内情報の更新とbookListストアの更新処理は別々に行うこと

    this.item = await this.$store.dispatch(
      'bookList/getBookItem',
      this.$route.params.id
    )

    if (!Object.keys(this.item).length) {
      this.fetchBookData()
    }
  },
  computed: {
    isShowToolbar() {
      return !!Object.keys(this.toolbar).length
    },
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
    onSetProp(prop, data) {
      this.setDirtyWithDiffState(this.item, (item) => {
        item[prop] = data
      })
    },
    setToolbar(val) {
      this.toolbar = val
    },
    disableToolbar() {
      if (this.$route.query) {
        this.removeQuery()
      } else {
        this.$route.go(-1)
      }
    },
    onEditBook(data) {
      this.item = data
      this.$store.commit('bookList/set', data)
    },
  },
}
</script>
