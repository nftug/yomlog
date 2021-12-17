<template>
  <div id="note-list" v-if="item.note">
    <v-card outlined class="mx-auto" :height="height">
      <div v-if="isLoading" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </div>

      <v-virtual-scroll
        v-if="item.note.length"
        :height="height"
        :item-height="itemHeight"
        :bench="benched"
        :items="item.note"
      >
        <template #default="{ item: note, index }">
          <v-list-item two-line link>
            <v-list-item-action>
              <v-checkbox
                v-model="checkbox[index]"
                @change="setToolbar('note')"
              ></v-checkbox>
            </v-list-item-action>

            <v-list-item-content @click="onClickEditNote(note.id)">
              <v-list-item-title>
                {{ note.position }} / {{ item.total }}
                {{ item.format_type ? '' : 'ページ' }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ note.content }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-divider v-if="index + 1 < item.note.length"></v-divider>
        </template>
      </v-virtual-scroll>

      <template v-else>
        <div class="text-center text-body-2 py-5">ノートが見つかりません。</div>
      </template>

      <!-- 検索 -->
      <SearchDialog type="note" :book-id="item.id">
        <template #activator="{ on, attrs }">
          <v-btn
            color="pink"
            dark
            bottom
            right
            fab
            absolute
            class="v-btn--floating"
            v-on="on"
            v-bind="attrs"
          >
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </template>
      </SearchDialog>
    </v-card>

    <NotePostDialog
      ref="noteEdit"
      @post="sendEditProp"
      @delete="sendDeleteProp"
    ></NotePostDialog>

    <ItemDeleteDialog
      ref="itemDelete"
      type="note"
      @delete="sendDeleteProp"
    ></ItemDeleteDialog>
  </div>
</template>

<script>
import Mixins, { BookListMixin, BookDetailChildMixin } from '@/mixins'
import NotePostDialog from '@/components/NotePostDialog.vue'
import SearchDialog from '@/components/SearchDialog.vue'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import api from '@/services/api'

export default {
  mixins: [Mixins, BookListMixin, BookDetailChildMixin],
  components: {
    NotePostDialog,
    SearchDialog,
    ItemDeleteDialog,
  },
  data: () => ({
    itemHeight: 64,
    isLoading: false,
  }),
  mounted() {
    this.fetchBookNote()
  },
  watch: {
    '$route.query'() {
      this.fetchBookNote()
    },
  },
  computed: {
    benched() {
      return Math.ceil(this.height / this.itemHeight)
    },
  },
  methods: {
    onClickEditNote(id) {
      this.$refs.noteEdit.showNotePostDialog({ book: this.item, id: id })
    },
    async fetchBookNote() {
      try {
        this.isLoading = true
        const params = {
          ...this.$route.query,
          book: this.item.id,
          no_pagination: true,
        }
        const { data } = await api.get('/note/', { params: params })
        this.$emit('set', 'note', data)

        // ツールバーの制御
        const toolbar = {}
        if (Object.keys(this.$route.query).length) {
          toolbar.type = 'note'
          toolbar.mode = 'search'
          toolbar.query = this.$route.query
        }
        this.$emit('set-toolbar', toolbar)
      } finally {
        this.isLoading = false
        this.initCheckbox('note')
      }
    },
  },
}
</script>

<style scoped>
.v-btn--floating {
  bottom: 0;
  margin: 0 0 48px 48px;
}
</style>
