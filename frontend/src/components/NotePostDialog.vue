<template>
  <Dialog
    ref="dialogNoteAdd"
    title="ノートの追加"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    :form-valid="isValid"
  >
    <template #toolbar="{ ok, cancel, title }">
      <v-toolbar dark color="primary">
        <v-btn icon dark @click="cancel">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>{{ title }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
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
    </template>

    <spinner size="large" v-if="isSending" />

    <v-form v-else ref="formNoteAdd" v-model="isValid" @submit.prevent>
      <v-col cols="11" lg="5" md="6" sm="10" class="mx-auto mt-5">
        <v-tabs-items v-model="tab">
          <v-tab-item class="mt-3">
            <v-text-field
              v-model="position"
              :label="!format_type ? 'ページ数' : '位置No'"
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
              <!-- TODO: ファイルクリアを追加 -->
            </div>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-form>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'
import Spinner from 'vue-simple-spinner'

export default {
  components: {
    Dialog,
    Spinner,
  },
  data() {
    return {
      id: '',
      format_type: 0,
      position: 0,
      total: 0,
      content: '',
      positionRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (!this.format_type ? 'ページ数' : '位置No') + 'が不正です',
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
  methods: {
    async showNotePostDialog({ book, id }) {
      this.tab = 0

      // バリデーションをクリア
      if (this.$refs.formNoteAdd) {
        this.$refs.formNoteAdd.resetValidation()
      }

      // 各種データを入力
      this.id = book.id
      this.format_type = book.format_type
      this.total = book.total
      this.quoteImage = null

      if (id) {
        const note = book.notes.find((e) => e.id === id)
        this.position = note.position
        this.content = note.content
        this.quoteText = note.quote_text
        this.prevSrc = note.quote_image
      } else {
        this.position = book.status[0].position || 0
        this.content = ''
        this.quoteText = ''
        this.prevSrc = ''
      }

      // ダイアログを表示
      if (!(await this.$refs.dialogNoteAdd.showDialog())) return

      this.postNote(id)
    },
    postNote(id) {
      let data = new FormData()
      data.append('book', this.id)
      data.append('position', this.position)
      data.append('content', this.content)
      data.append('quote_text', this.quoteText)

      // ファイルのアップロード可否判定
      if (this.quoteImage) {
        data.append('quote_image', this.quoteImage)
      } else if (!this.prevSrc) {
        data.append('quote_image', new File([], ''))
      }

      // POST/PATCHの切り替え
      let method, url
      if (id) {
        method = 'patch'
        url = `/note/${id}/`
      } else {
        method = 'post'
        url = '/note/'
      }

      // フォーム送信
      this.isSending = true
      api({
        url: url,
        method: method,
        data: data,
      })
        .then(({ data }) => {
          // ダイアログを閉じる
          this.$refs.dialogNoteAdd.hideDialog()

          this.$emit('post', data)

          this.$store.dispatch('message/setInfoMessage', {
            message: `ノートを${id ? '編集' : '追加'}しました。`,
          })
        })
        .catch(() => {
          this.$store.dispatch('message/setErrorMessage', {
            message: 'エラーが発生しました',
          })
        })
        .finally(() => {
          this.isSending = false
        })
    },
    inputQuoteImage(event) {
      if (event) {
        this.prevSrc = URL.createObjectURL(event)
        this.quoteImage = event
      } else {
        this.prevSrc = ''
      }
    },
  },
}
</script>
