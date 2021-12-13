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

    <NotePostDialog
      ref="noteEdit"
      @post="onEditNote"
      @delete="onDeleteNote"
    ></NotePostDialog>
  </div>
</template>

<script>
import Mixins, { BookListMixin } from '@/mixins'
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
    onClickEditNote(book, id) {
      this.$refs.noteEdit.showNotePostDialog({ book: book, id: id })
    },
    onEditNote(data) {
      this.$emit('edit', data)
    },
    onDeleteNote(id) {
      this.$emit('delete', id)
    },
  },
}
</script>
