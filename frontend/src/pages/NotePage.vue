<template>
  <v-container fluid>
    <v-col sm="10" class="mx-auto">
      <!-- 検索カード -->
      <SearchCard :total="total" type="note">
        <strong>{{ total }}件</strong>
        のノートが見つかりました。
      </SearchCard>

      <!-- Spinner -->
      <Spinner v-if="isLoading"></Spinner>

      <!-- ノートのリスト -->
      <template v-else-if="notes.length">
        <v-row>
          <v-col v-for="note in notes" :key="note.id" cols="12" md="6">
            <v-card class="mx-auto fill-height">
              <div class="pt-4">
                <v-list-item three-line>
                  <v-list-item-avatar
                    class="hidden-xs-only mr-2"
                    tile
                    size="125"
                  >
                    <v-img
                      contain
                      :src="note.book.thumbnail || noImage"
                    ></v-img>
                  </v-list-item-avatar>

                  <v-list-item-content class="align-self-start">
                    <v-list-item-title>
                      <router-link :to="`/book/detail/${note.book.id}`">
                        {{ note.book.title }}
                      </router-link>
                    </v-list-item-title>
                    <v-list-item-subtitle
                      class="mt-2 grey--text text--darken-4"
                    >
                      位置: {{ note.position
                      }}{{ note.book.format_type === 1 ? '' : 'ページ' }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle class="mt-4">
                      {{ note.content }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </div>

              <!-- 操作メニュー -->
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      class="mr-4"
                      icon
                      color="primary"
                      v-bind="attrs"
                      v-on="on"
                      @click="
                        $refs.noteEdit.showNotePostDialog({
                          note,
                          book: note.book,
                        })
                      "
                    >
                      <v-icon>mdi-pen</v-icon>
                    </v-btn>
                  </template>
                  <span>ノートを編集する</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      class="mr-4"
                      icon
                      color="error"
                      v-bind="attrs"
                      v-on="on"
                      @click="$refs.noteDelete.showItemDeleteDialog(note.id)"
                    >
                      <v-icon>mdi-trash-can</v-icon>
                    </v-btn>
                  </template>
                  <span>ノートを削除する</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      class="mr-4"
                      icon
                      color="success"
                      v-bind="attrs"
                      v-on="on"
                      :to="`/book/detail/${note.book.id}`"
                    >
                      <v-icon>mdi-book</v-icon>
                    </v-btn>
                  </template>
                  <span>書籍を見る</span>
                </v-tooltip>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- ページネーション -->
        <Pagination
          v-model="page"
          :length="totalPages"
          :total-visible="5"
        ></Pagination>
      </template>

      <template v-else>
        <div class="text-center text-body-2">
          <p class="mt-4 mb-5">ノートが見つかりません。</p>
        </div>
      </template>
    </v-col>

    <NotePostDialog
      ref="noteEdit"
      @post="fetchNoteList"
      @delete="fetchNoteList"
    ></NotePostDialog>

    <ItemDeleteDialog
      ref="noteDelete"
      type="note"
      @delete="fetchNoteList"
    ></ItemDeleteDialog>
  </v-container>
</template>

<script>
import { ListViewMixin } from '@/mixins'
import api from '@/services/api'
import Spinner from '@/components/Spinner.vue'
import SearchCard from '@/components/SearchCard.vue'
import NotePostDialog from '@/components/NotePostDialog.vue'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import Pagination from '@/components/Pagination.vue'

export default {
  mixins: [ListViewMixin],
  components: {
    Spinner,
    SearchCard,
    NotePostDialog,
    ItemDeleteDialog,
    Pagination,
  },
  data: () => ({
    notes: [],
    page: 0,
    total: 0,
    isLoading: false,
    noImage: 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=No+Image',
  }),
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにリロードする
    this.fetchNoteList({ route: to })
    next()
  },
  created() {
    this.fetchNoteList()
  },
  methods: {
    async fetchNoteList({ route = this.$route } = {}) {
      this.page = Number(route.query.page || 1)
      this.isLoading = true
      this.notes = []

      try {
        const { data } = await api.get('/note/', {
          params: { ...route.query, page: this.page },
        })

        this.total = data.count
        this.totalPages = data.totalPages
        data.results.forEach((item) => {
          this.notes.push(item)
        })
      } catch (error) {
        if (error.response) {
          const { response } = error
          if (response.status === 404) {
            // ページ数超過の場合、最終ページに遷移
            const params = { ...response.config.params }
            this.replaceWithFinalPage('/note/', params)
          }
        }
      } finally {
        this.isLoading = false
      }
    },
  },
}
</script>
