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
            <v-card class="mx-auto">
              <v-list-item three-line>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ note.book.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    位置: {{ note.position
                    }}{{ note.book.format_type === 1 ? '' : 'ページ' }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle class="mt-3">
                    {{ note.content }}
                  </v-list-item-subtitle>
                </v-list-item-content>

                <v-list-item-action>
                  <div class="d-flex">
                    <v-btn
                      icon
                      @click="
                        $refs.noteEdit.showNotePostDialog({
                          note,
                          book: note.book,
                        })
                      "
                    >
                      <v-icon>mdi-pen</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      @click="$refs.noteDelete.showItemDeleteDialog(note.id)"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                    <v-btn icon :to="`/book/detail/${note.book.id}`">
                      <v-icon>mdi-book</v-icon>
                    </v-btn>
                  </div>
                </v-list-item-action>
              </v-list-item>
            </v-card>
          </v-col>
        </v-row>

        <!-- ページネーション -->
        <Pagination
          v-model="page"
          :length="total"
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
    Pagination,
    ItemDeleteDialog,
  },
  data: () => ({
    notes: [],
    page: 0,
    total: 0,
    isLoading: 0,
  }),
  beforeRouteUpdate(to, from, next) {
    // ナビゲーションガード
    // routeがアップデートされるたびにリロードする
    const isSameQuery = JSON.stringify(to.query) === JSON.stringify(from.query)

    if (!isSameQuery) {
      this.fetchNoteList({ route: to })
    }
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
          params: { ...this.$route.query, page: this.page },
        })

        console.log({ ...this.$route.query, page: this.page })
        console.log(data)

        this.total = data.count
        data.results.forEach((item) => {
          this.notes.push(item)
        })
      } catch (error) {
        if (error.response) {
          const { response } = error
          if (response.status === 404) {
            // ページ数超過の場合、最終ページに遷移
            let params = { ...response.config.params }
            this.replaceWithFinalPage('/note/', params)
          }
        } else {
          return Promise.reject(error)
        }
      } finally {
        this.isLoading = false
      }
    },
  },
}
</script>
