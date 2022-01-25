<template>
  <!-- Not Found -->
  <NotFoundPage v-if="error"></NotFoundPage>

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
                :to="`/shelf/all/?authors=${author}`"
                v-text="author"
              ></router-link>
              <span v-if="index + 1 < item.authors.length" v-text="', '"></span>
            </span>
          </div>

          <BookDetailMenu
            :item="item"
            class="my-2 hidden-xs-only"
            @dialog="showDialog"
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
        @dialog="showDialog"
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
        </v-toolbar>

        <v-tabs
          v-show="!isShowToolbar"
          v-model="activeTab"
          fixed-tabs
          @change="onClickTab"
        >
          <v-tab v-for="(tab, index) in tabs" :key="index">
            <v-icon class="hidden-sm-and-up" v-text="tab.icon"></v-icon>
            <div class="hidden-xs-only" v-text="tab.label"></div>

            <div v-if="tab.count" class="hidden-xs-only px-2">
              <v-chip small color="grey darken-1" dark>
                {{ item[tab.name].length }}
              </v-chip>
            </div>
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <v-tab-item>
            <StatusLog
              :item="item"
              height="500"
              @set-toolbar="setToolbar"
            ></StatusLog>
          </v-tab-item>
          <v-tab-item>
            <NoteList
              :item="item"
              height="500"
              @set-toolbar="setToolbar"
            ></NoteList>
          </v-tab-item>
          <v-tab-item>
            <Calendar
              v-model="date"
              height="500"
              :query="{ book: item.id }"
            ></Calendar>
          </v-tab-item>
        </v-tabs-items>
      </div>
    </v-col>

    <BookDetailFab :item="item" @dialog="showDialog"></BookDetailFab>

    <!-- ダイアログ -->
    <BookEditDialog
      ref="bookEdit"
      hash="edit-book"
      @post="onEditBook"
    ></BookEditDialog>
    <ItemDeleteDialog
      ref="bookDelete"
      type="book"
      @delete="onDeleteBook"
    ></ItemDeleteDialog>
    <StatusAddDialog ref="statusAdd" hash="add-status"></StatusAddDialog>
    <NoteAddDialog ref="noteAdd" hash="add-note"></NoteAddDialog>
  </v-container>
</template>

<script>
import Spinner from '@/components/Common/Spinner.vue'
import NotFoundPage from '@/pages/error/NotFoundPage.vue'
import Mixins, { BookListMixin, ListViewMixin } from '@/mixins'
import BookDetailInfo from '@/components/BookDetail/BookDetailInfo.vue'
import BookDetailMenu from '@/components/BookDetail/BookDetailMenu.vue'
import BookDetailFab from '@/components/BookDetail/BookDetailFab.vue'
import StatusLog from '@/components/BookDetail/StatusLog.vue'
import NoteList from '@/components/BookDetail/NoteList.vue'
import Calendar from '@/components/Common/Calendar.vue'
import StatusAddDialog from '@/components/Dialog/StatusPostDialog.vue'
import NoteAddDialog from '@/components/Dialog/NotePostDialog.vue'
import BookEditDialog from '@/components/Dialog/BookEditDialog.vue'
import ItemDeleteDialog from '@/components/Dialog/ItemDeleteDialog.vue'

import moment from 'moment'

export default {
  mixins: [Mixins, BookListMixin, ListViewMixin],
  components: {
    NotFoundPage,
    Spinner,
    BookDetailInfo,
    BookDetailMenu,
    BookDetailFab,
    StatusLog,
    NoteList,
    Calendar,
    StatusAddDialog,
    NoteAddDialog,
    ItemDeleteDialog,
    BookEditDialog,
  },
  data() {
    return {
      item: {},
      isLoading: false,
      error: null,
      activeTab: 0,
      toolbar: {},
      tabs: [
        {
          label: '進捗',
          icon: 'mdi-bookmark',
          name: 'status',
          count: true,
        },
        {
          label: 'ノート',
          icon: 'mdi-note',
          name: 'note',
          count: true,
        },
        {
          label: 'カレンダー',
          icon: 'mdi-calendar',
          name: 'calendar',
          count: false,
        },
      ],
      date: moment().format('yyyy-MM-DD'),
    }
  },
  async created() {
    // URLのハッシュに基づいてアクティブなタブを設定
    this.setTabFromHash()

    // 書籍データをストア or Web APIから取得

    try {
      this.isLoading = true
      this.item = await this.$store.dispatch('bookList/getBookItem', {
        id: this.$route.params.id,
        state: this.$route.params.state,
      })

      // カレンダーの日付を進捗の最終更新日に合わせる
      this.date = moment(this.currentState(this.item).created_at).format(
        'yyyy-MM-DD'
      )
    } catch (error) {
      this.error = error.response ? error.response.status : 404
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
    showDialog(name, payload) {
      if (name === 'add-note') {
        this.$refs.noteAdd.showNotePostDialog(payload)
      } else if (name === 'add-status') {
        this.$refs.statusAdd.showStatusPostDialog(payload)
      } else if (name === 'edit-book') {
        this.$refs.bookEdit.showBookEditDialog(payload)
      } else if (name === 'delete-book') {
        this.$refs.bookDelete.showItemDeleteDialog(payload)
      }
    },
    setTabFromHash() {
      const hashName = this.$route.hash.replace(/^#/, '')
      const index = this.tabs.findIndex((item) => item.name === hashName)
      this.activeTab = index > -1 ? index : 0
    },
    onClickTab() {
      // activeTabのindexに応じてhashを変更する
      const hashName = this.tabs[this.activeTab].name
      this.$router.replace(`#${hashName}`)
    },
    onEditBook(book) {
      this.$store.dispatch('auth/reload')
      this.$store.commit('bookList/set', book)
      this.item = book
    },
    onDeleteBook(book) {
      this.$store.dispatch('auth/reload')
      this.$router.replace({
        name: 'shelf',
        params: {
          state: this.currentState(book).state,
        },
      })
    },
    setToolbar(val) {
      this.toolbar = val
    },
    disableToolbar() {
      this.$router.app.$emit('clear-checkbox', this.toolbar.type)
      this.toolbar = {}
    },
    deleteItems() {
      const type = this.toolbar.type
      this.$router.app.$emit('delete-items', type)
    },
  },
}
</script>
