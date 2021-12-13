<template>
  <v-row :dense="isLessThanSm">
    <v-col cols="6">
      <v-btn color="primary" small dark block @click="onClickNoteAdd(item)">
        <v-icon small>mdi-pen-plus</v-icon>
        ノートを追加
      </v-btn>
    </v-col>

    <v-col cols="6">
      <v-btn color="success" small dark block @click="onClickStatusAdd(item)">
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
          <v-list-item link>
            <v-list-item-title>書籍の編集</v-list-item-title>
          </v-list-item>
          <v-list-item link>
            <v-list-item-title @click="onClickBookDelete(item)">
              書籍の削除
            </v-list-item-title>
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
    <ItemDeleteDialog
      ref="bookDelete"
      @delete-book="onDeleteBook(item)"
    ></ItemDeleteDialog>
    <StatusAddDialog ref="statusAdd" @post="onAddStatus"></StatusAddDialog>
    <NoteAddDialog ref="noteAdd"></NoteAddDialog>
  </v-row>
</template>

<script>
import StatusAddDialog from '@/components/StatusPostDialog.vue'
import NoteAddDialog from '@/components/NotePostDialog.vue'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import { WindowResizeMixin } from '@/mixins'

export default {
  mixins: [WindowResizeMixin],
  props: {
    item: {
      type: Object,
    },
  },
  components: {
    StatusAddDialog,
    NoteAddDialog,
    ItemDeleteDialog,
  },
  computed: {
    googleLink() {
      return `https://books.google.co.jp/books/?id=${this.item.id_google}`
    },
  },
  methods: {
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusPostDialog({ book: item })
    },
    onClickNoteAdd(item) {
      this.$refs.noteAdd.showNotePostDialog({ book: item })
    },
    onClickBookDelete(item) {
      this.$refs.bookDelete.showItemDeleteDialog(item)
    },
    onDeleteBook(item) {
      this.$router.replace({
        name: 'shelf',
        params: {
          mode: item.status[0].state,
        },
      })
    },
    onAddStatus(data) {
      this.item.status.unshift(data)
    },
  },
}
</script>
