<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error === 404"></NotFoundPage>

  <v-container v-else fluid>
    <!-- Spinner -->
    <Spinner v-if="isLoading"></Spinner>

    <v-col v-else sm="10" md="8" xl="7" class="mx-auto">
      <v-row class="pb-4">
        <v-col cols="12" sm="9">
          <!-- 書籍情報 -->
          <div class="text-h6 my-2 font-weight-bold" v-text="item.title"></div>
          <div class="text-body-2 mb-sm-5">
            <span v-for="(author, index) in item.authors" :key="index">
              <router-link
                :to="`/book/all/?authors=${author}`"
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
            @delete-book="onDeleteBook"
          ></BookDetailMenu>
        </v-col>

        <v-col cols="12" sm="3">
          <v-img
            contain
            :src="item.thumbnail"
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
        @delete-book="onDeleteBook"
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

          <div class="ma-2"></div>

          <template v-if="toolbar.mode === 'checked'">
            <v-btn color="red" dark @click="deleteItems">
              <v-icon left>mdi-delete</v-icon>
              削除
            </v-btn>
          </template>

          <template v-else-if="toolbar.mode === 'search'">
            <v-chip
              class="ma-1"
              v-for="(q, key) in $route.query"
              :key="key"
              close
              small
              @click:close="removeQuery(key, { ...$route.query })"
            >
              {{ key | searchLabel }}
              {{ q }}
            </v-chip>
          </template>
        </v-toolbar>

        <v-tabs v-show="!isShowToolbar" v-model="activeTab" grow>
          <v-tab v-for="tab in tabs" :key="tab.type" :to="tab.path" replace>
            {{ tab.label }}
            <div class="px-2">
              <v-chip small color="grey darken-1" dark>
                {{ item[tab.type].length }}
              </v-chip>
            </div>
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <v-tab-item v-for="tab in tabs" :key="tab.type" :value="tab.path">
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

    <BookDetailFab :item="item" @post="onAddProp"></BookDetailFab>
  </v-container>
</template>

<script>
import Spinner from '@/components/Spinner.vue'
import NotFoundPage from '@/pages/error/NotFoundPage.vue'
import Mixins, { BookListMixin, ListViewMixin } from '@/mixins'
import BookDetailInfo from '@/components/BookDetailInfo.vue'
import BookDetailMenu from '@/components/BookDetailMenu.vue'
import BookDetailFab from '@/components/BookDetailFab.vue'

export default {
  mixins: [Mixins, BookListMixin, ListViewMixin],
  components: {
    NotFoundPage,
    Spinner,
    BookDetailInfo,
    BookDetailMenu,
    BookDetailFab,
  },
  data() {
    return {
      item: {},
      isLoading: false,
      error: null,
      activeTab: null,
      toolbar: {},
      tabs: [
        {
          label: '進捗',
          type: 'status',
          path: `/book/${this.$route.params.mode}/${this.$route.params.id}/`,
        },
        {
          label: 'ノート',
          type: 'note',
          path: `/book/${this.$route.params.mode}/${this.$route.params.id}/note`,
        },
      ],
    }
  },
  async created() {
    // NOTE: ストアから取得するのはアイテムのコピーになる
    // ⇒ページ内情報の更新とbookListストアの更新処理は別々に行うこと
    try {
      this.isLoading = true
      this.item = await this.$store.dispatch(
        'bookList/getBookItem',
        this.$route.params.id
      )
    } catch (error) {
      if (error.response) this.error = error.response.status
    } finally {
      this.isLoading = false
    }
  },
  computed: {
    isShowToolbar() {
      return !!Object.keys(this.toolbar).length
    },
  },
  methods: {
    onAddProp({ prop, data }) {
      this.$store.dispatch('bookList/addProp', {
        book: this.item,
        prop,
        data,
      })
    },
    onDeleteProp({ prop, id }) {
      this.$store.dispatch('bookList/deleteProp', {
        book: this.item,
        prop,
        id,
      })
    },
    onEditProp({ prop, data }) {
      this.$store.dispatch('bookList/editProp', {
        book: this.item,
        prop,
        data,
      })
    },
    onSetProp({ prop, data }) {
      this.$store.dispatch('bookList/setProp', {
        book: this.item,
        prop,
        data,
      })
    },
    onEditBook(data) {
      this.$store.dispatch('auth/reload')
      this.item = data
      this.$store.commit('bookList/set', data)
    },
    onDeleteBook(data) {
      this.$store.dispatch('auth/reload')
      this.$router.replace({
        name: 'shelf',
        params: {
          mode: this.currentState(data).state,
        },
      })
    },
    setToolbar(val) {
      this.toolbar = val
    },
    disableToolbar() {
      this.$router.app.$emit('clear-checkbox', this.toolbar.type)
      if (this.toolbar.mode === 'search') {
        this.removeQuery()
      }
      this.toolbar = {}
    },
    deleteItems() {
      const type = this.toolbar.type
      this.$router.app.$emit('delete-items', type)
    },
  },
}
</script>
