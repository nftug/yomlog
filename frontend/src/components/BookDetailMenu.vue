<template>
  <v-col>
    <v-row>
      <v-col xl="3" cols="6">
        <v-btn color="primary" small dark block @click="onClickNoteAdd(item)">
          <v-icon small>mdi-pen-plus</v-icon>
          ノートを追加
        </v-btn>
      </v-col>

      <v-col xl="3" cols="6">
        <v-btn color="success" small dark block @click="onClickStatusAdd(item)">
          <v-icon small>mdi-bookmark-plus</v-icon>
          進捗を追加
        </v-btn>
      </v-col>

      <v-col xl="3" cols="6">
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

      <v-col xl="3" cols="6">
        <v-btn
          v-show="item.amazon_dp"
          color="orange"
          small
          dark
          block
          :href="amazonLink"
          target="_blank"
          rel="noopener noreferrer"
        >
          <v-icon small>mdi-shopping</v-icon>
          Amazon
        </v-btn>
      </v-col>
    </v-row>

    <!-- ダイアログ -->
    <BookDeleteDialog
      ref="bookDelete"
      @delete-book="onDeleteBook(item)"
    ></BookDeleteDialog>
    <StatusAddDialog
      ref="statusAdd"
      @reload="$emit('reload')"
    ></StatusAddDialog>
    <NoteAddDialog ref="noteAdd" @reload="$emit('reload')"></NoteAddDialog>
  </v-col>
</template>

<script>
import StatusAddDialog from '@/components/StatusAddDialog.vue'
import NoteAddDialog from '@/components/NoteAddDialog.vue'
import BookDeleteDialog from '@/components/BookDeleteDialog.vue'

export default {
  props: {
    item: {
      type: Object,
    },
  },
  components: {
    StatusAddDialog,
    NoteAddDialog,
    BookDeleteDialog,
  },
  computed: {
    amazonLink() {
      return `https://www.amazon.co.jp/s?k=${this.item.amazon_dp}`
    },
  },
  methods: {
    onClickStatusAdd(item) {
      this.$refs.statusAdd.showStatusAddDialog(item)
    },
    onClickNoteAdd(item) {
      this.$refs.noteAdd.showNoteAddDialog(item)
    },
    onClickBookDelete(item) {
      this.$refs.bookDelete.showBookDeleteDialog(item)
    },
    onDeleteBook(item) {
      this.$router.replace({
        name: 'shelf',
        params: {
          mode: item.status[0].state,
        },
      })
    },
  },
}
</script>
