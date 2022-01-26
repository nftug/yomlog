<template>
  <Dialog
    ref="dialogNoteAdd"
    max-width="600"
    :fullscreen="isLessThanMd"
    :hide-overlay="isLessThanMd"
    no-template
    transition="dialog-bottom-transition"
    :form-valid="isValid"
    :hash="hash"
  >
    <template #default="{ ok, cancel }">
      <v-toolbar dark color="primary">
        <v-btn icon dark @click="cancel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title
          v-text="`ノートの${noteId ? '編集' : '追加'}`"
        ></v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn
            v-show="!!noteId && !isBookDetailPage"
            dark
            icon
            :to="`/book/detail/${bookId}`"
          >
            <v-icon>mdi-book</v-icon>
          </v-btn>
          <v-btn v-show="!!noteId" dark icon @click="onClickDeleteNote(cancel)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
          <v-btn dark icon @click="ok" :disabled="!isValid">
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
        </v-toolbar-items>

        <template #extension>
          <v-tabs v-model="tab" centered>
            <v-tab>ノート</v-tab>
            <v-tab>引用の詳細</v-tab>
          </v-tabs>
        </template>
      </v-toolbar>

      <Spinner size="100" v-if="isSending" />

      <v-form v-else ref="formNoteAdd" v-model="isValid" @submit.prevent>
        <v-card-text>
          <v-container>
            <v-tabs-items v-model="tab">
              <v-tab-item class="mt-3">
                <v-text-field
                  v-model="position"
                  :label="format_type === 1 ? '位置No' : 'ページ'"
                  type="number"
                  min="0"
                  :max="total"
                  :suffix="` / ${total}`"
                  :rules="positionRules"
                ></v-text-field>

                <v-textarea
                  v-model="content"
                  outlined
                  label="ノートの内容"
                  rows="8"
                  :rules="contentRules"
                ></v-textarea>
              </v-tab-item>

              <v-tab-item class="mt-3">
                <v-textarea
                  v-model="quoteText"
                  outlined
                  label="引用内容 (テキスト)"
                  rows="8"
                ></v-textarea>

                <v-file-input
                  v-model="quoteImage"
                  label="引用内容 (画像)"
                  ref="quote_image"
                  accept="image/*"
                  @change="inputQuoteImage($event)"
                ></v-file-input>

                <div v-show="prevSrc" class="mb-4 mx-4">
                  <v-img :src="prevSrc" alt="" width="150" />
                  <v-btn text small color="primary" @click="clearQuoteImage">
                    クリア
                  </v-btn>
                </div>
              </v-tab-item>
            </v-tabs-items>
          </v-container>
        </v-card-text>
      </v-form>

      <ItemDeleteDialog ref="noteDelete" type="note"></ItemDeleteDialog>
    </template>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Common/Dialog.vue'
import Spinner from '@/components/Common/Spinner.vue'
import ItemDeleteDialog from '@/components/Dialog/ItemDeleteDialog.vue'
import { BookListMixin, WindowResizeMixin } from '@/mixins'

export default {
  mixins: [BookListMixin, WindowResizeMixin],
  props: { hash: { type: String } },
  components: {
    Dialog,
    Spinner,
    ItemDeleteDialog,
  },
  data() {
    return {
      book: {},
      note: {},
      bookId: '',
      noteId: '',
      format_type: 0,
      position: 0,
      total: 0,
      content: '',
      positionRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (this.format_type === 1 ? '位置No' : 'ページ数') + 'が不正です',
      ],
      contentRules: [(v) => !!v || '内容を入力してください'],
      isValid: false,
      quoteText: '',
      quoteImage: null,
      prevSrc: '',
      isSending: false,
      tab: 0,
    }
  },
  computed: {
    isBookDetailPage() {
      return this.$route.name.startsWith('book_detail')
    },
  },
  methods: {
    async showNotePostDialog({ book, note } = {}) {
      this.tab = 0

      // バリデーションをクリア
      if (this.$refs.formNoteAdd) {
        this.$refs.formNoteAdd.resetValidation()
      }

      // 各種データを入力
      this.book = book
      this.note = note
      this.bookId = book.id
      this.format_type = book.format_type
      this.total = book.total
      this.quoteImage = null

      if (note) {
        this.position = note.position
        this.content = note.content
        this.quoteText = note.quote_text
        this.prevSrc = note.quote_image
        this.noteId = note.id
      } else if (book) {
        this.position = this.currentState(book).position.value || 0
        this.content = ''
        this.quoteText = ''
        this.prevSrc = ''
        this.noteId = ''
      } else {
        throw new Error('No params for showNotePostDialog')
      }

      // ダイアログを表示
      if (!(await this.$refs.dialogNoteAdd.showDialog())) return

      this.postNote()
    },
    async postNote() {
      let form = new FormData()
      form.append('book', this.bookId)
      form.append('position', this.position)
      form.append('content', this.content)
      form.append('quote_text', this.quoteText)

      // ファイルのアップロード可否判定
      if (this.quoteImage) {
        form.append('quote_image', this.quoteImage)
      } else if (!this.prevSrc) {
        form.append('quote_image', new File([], ''))
      }

      // POST/PATCHの切り替え
      let method, url
      if (this.noteId) {
        method = 'patch'
        url = `/note/${this.noteId}/`
      } else {
        method = 'post'
        url = '/note/'
      }

      // フォーム送信
      try {
        this.isSending = true
        const { data } = await api({ url, method, data: form })

        this.$refs.dialogNoteAdd.hideDialog()

        await this.$store.dispatch('bookList/reflectBookProp', {
          id: this.book.id,
        })
        this.$emit('post', { prop: 'note', data })

        this.$store.dispatch('message/setInfoMessage', {
          message: `ノートを${this.noteId ? '編集' : '追加'}しました。`,
        })
      } catch {
        this.$store.dispatch('message/setErrorMessage', {
          message: 'エラーが発生しました',
        })
      } finally {
        this.isSending = false
      }
    },
    inputQuoteImage(event) {
      if (event) {
        this.prevSrc = URL.createObjectURL(event)
        this.quoteImage = event
      } else {
        this.prevSrc = ''
      }
    },
    clearQuoteImage() {
      this.quoteImage = null
      this.prevSrc = ''
    },
    async onClickDeleteNote(callback) {
      const ret = await this.$refs.noteDelete.showItemDeleteDialog({
        item: this.note,
        book: this.book,
      })

      if (ret) {
        this.$refs.dialogNoteAdd.hideDialog(false)
        this.$emit('delete', { prop: 'note', data: this.note })
        callback()
      }
    },
  },
}
</script>
