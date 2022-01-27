<template>
  <div id="note-list" v-if="book.note">
    <v-card outlined class="mx-auto overflow-hidden" :height="height">
      <div v-if="isLoading" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </div>

      <v-sheet v-else flat class="overflow-y-auto fill-height">
        <template v-if="book.note.length">
          <div v-for="(note, index) in book.note" :key="index">
            <v-list-item two-line link>
              <v-list-item-action>
                <v-checkbox
                  v-model="checkbox[index]"
                  @change="setToolbar('note')"
                ></v-checkbox>
              </v-list-item-action>

              <v-list-item-content
                @click="$refs.noteEdit.showNotePostDialog({ book, note })"
              >
                <v-list-item-title>
                  {{ note.position
                  }}{{ book.format_type === 1 ? '' : 'ページ' }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ note.content }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </div>
        </template>

        <template v-else>
          <div class="text-center text-body-2 py-5">
            ノートが見つかりません。
          </div>
        </template>
      </v-sheet>

      <!-- 検索 -->
      <SearchDialog type="note" :book-id="book.id">
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
      hash="edit-note"
      @post="$emit('post', $event)"
      @delete="onDeleteItems"
    ></NotePostDialog>

    <ItemDeleteDialog
      ref="itemDelete"
      type="note"
      @delete="onDeleteItems"
    ></ItemDeleteDialog>
  </div>
</template>

<script>
import Mixins, { BookListMixin, BookDetailChildMixin } from '@/mixins'
import NotePostDialog from '@/components/Dialog/NotePostDialog.vue'
import SearchDialog from '@/components/Common/SearchDialog.vue'
import ItemDeleteDialog from '@/components/Dialog/ItemDeleteDialog.vue'

export default {
  mixins: [Mixins, BookListMixin, BookDetailChildMixin],
  components: {
    NotePostDialog,
    SearchDialog,
    ItemDeleteDialog,
  },
  data: () => ({
    isLoading: false,
  }),
  mounted() {
    this.initCheckbox('note')
  },
}
</script>

<style scoped>
.v-btn--floating {
  bottom: 0;
  margin: 0 0 48px 48px;
}
</style>
