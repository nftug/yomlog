<template>
  <v-row :dense="isLessThanSm">
    <v-col cols="6">
      <v-btn
        color="primary"
        small
        dark
        block
        @click="$refs.noteAdd.showNotePostDialog({ book: item })"
      >
        <v-icon small>mdi-pen-plus</v-icon>
        ノートを追加
      </v-btn>
    </v-col>

    <v-col cols="6">
      <v-btn
        color="success"
        small
        dark
        block
        @click="$refs.statusAdd.showStatusPostDialog({ book: item })"
      >
        <v-icon small>mdi-bookmark-plus</v-icon>
        進捗を追加
      </v-btn>
    </v-col>

    <v-col cols="6">
      <v-menu offset-y close-on-click>
        <template v-slot:activator="{ on, attrs }">
          <v-btn color="secondary" dark v-bind="attrs" v-on="on" small block>
            <v-spacer></v-spacer>
            <v-icon small>mdi-book-edit</v-icon>
            編集
            <v-spacer></v-spacer>
            <v-icon small>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item
            link
            @click="$refs.bookEdit.showBookEditDialog({ book: item })"
          >
            <v-list-item-title>書籍の編集</v-list-item-title>
          </v-list-item>
          <v-list-item
            link
            @click="$refs.bookDelete.showItemDeleteDialog(item.id)"
          >
            <v-list-item-title>書籍の削除</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-col>

    <v-col cols="6">
      <v-btn
        color="info"
        small
        dark
        block
        :href="googleLink"
        target="_blank"
        rel="noopener noreferrer"
      >
        <v-icon small>mdi-google</v-icon>
        Google Books
      </v-btn>
    </v-col>

    <!-- ダイアログ -->
    <BookEditDialog
      ref="bookEdit"
      @post="$emit('edit-book', $event)"
    ></BookEditDialog>
    <ItemDeleteDialog
      ref="bookDelete"
      type="book"
      @delete="$emit('delete-book', $event)"
    ></ItemDeleteDialog>
    <StatusAddDialog
      ref="statusAdd"
      @post="$emit('post', $event)"
    ></StatusAddDialog>
    <NoteAddDialog ref="noteAdd" @post="$emit('post', $event)"></NoteAddDialog>
  </v-row>
</template>

<script>
import StatusAddDialog from '@/components/Dialog/StatusPostDialog.vue'
import NoteAddDialog from '@/components/Dialog/NotePostDialog.vue'
import BookEditDialog from '@/components/Dialog/BookEditDialog.vue'
import ItemDeleteDialog from '@/components/Dialog/ItemDeleteDialog.vue'
import { WindowResizeMixin, BookListMixin } from '@/mixins'

export default {
  mixins: [WindowResizeMixin, BookListMixin],
  props: {
    item: {
      type: Object,
    },
  },
  components: {
    StatusAddDialog,
    NoteAddDialog,
    ItemDeleteDialog,
    BookEditDialog,
  },
  computed: {
    googleLink() {
      return `https://books.google.co.jp/books/?id=${this.item.id_google}`
    },
  },
}
</script>
