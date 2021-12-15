<template>
  <div id="note-list" v-if="item.note">
    <v-card outlined class="mx-auto" :height="height">
      <v-virtual-scroll
        v-if="item.note.length"
        :height="height"
        :item-height="itemHeight"
        :bench="benched"
        :items="item.note"
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
  </div>
</template>

<script>
import Mixins, { BookListMixin, BookDetailChildMixin } from '@/mixins'
import NotePostDialog from '@/components/NotePostDialog.vue'
import SearchDialog from '@/components/SearchDialog.vue'

export default {
  mixins: [Mixins, BookListMixin, BookDetailChildMixin],
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
    SearchDialog,
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
  },
}
</script>

<style scoped>
.v-btn--floating {
  bottom: 0;
  margin: 0 0 48px 48px;
}
</style>
