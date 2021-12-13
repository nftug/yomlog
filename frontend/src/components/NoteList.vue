<template>
  <div id="note-list">
    <v-card outlined class="mx-auto" :height="height">
      <v-virtual-scroll
        v-if="item.notes.length"
        :height="height"
        :item-height="itemHeight"
        :bench="benched"
        :items="item.notes"
      >
        <template #default="{ item: note, index }">
          <v-list-item two-line link @click="onClickEditNote(item, note.id)">
            <v-list-item-content>
              <v-list-item-title>
                {{ note.position }} / {{ item.total }}
                {{ item.format_type ? '' : 'ページ' }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ note.content }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-divider v-if="index + 1 < item.notes.length"></v-divider>
        </template>
      </v-virtual-scroll>

      <template v-else>
        <div class="text-center text-body-2 py-5">ノートが見つかりません。</div>
      </template>
    </v-card>

    <ItemDeleteDialog
      ref="noteDelete"
      type="note"
      @delete-note="onDeleteNote"
    ></ItemDeleteDialog>
    <NotePostDialog ref="noteEdit" @post="onEditNote"></NotePostDialog>
  </div>
</template>

<script>
import Mixins, { BookListMixin } from '@/mixins'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import NotePostDialog from '@/components/NotePostDialog.vue'

export default {
  mixins: [Mixins, BookListMixin],
  props: {
    item: {
      type: Object,
    },
    height: {
      type: String,
      default: '400',
    },
  },
  components: {
    ItemDeleteDialog,
    NotePostDialog,
  },
  data: () => ({
    itemHeight: 64,
  }),
  computed: {
    benched() {
      return Math.ceil(this.height / this.itemHeight)
    },
  },
  methods: {
    onClickDeleteStatus(item) {
      this.$refs.noteDelete.showItemDeleteDialog(item)
    },
    onDeleteNote({ id }) {
      const index = this.item.notes.findIndex((e) => e.id === id)
      this.item.notes.splice(index, 1)
    },
    onClickEditNote(book, id) {
      this.$refs.noteEdit.showNotePostDialog({ book: book, id: id })
    },
    onEditNote(data) {
      const index = this.item.notes.findIndex((e) => e.id === data.id)
      this.item.notes.splice(index, 1, data)
    },
  },
}
</script>
