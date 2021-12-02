<template>
  <Dialog
    ref="dialogNoteAdd"
    title="ノートの追加"
    fullscreen
    hide-overlay
    transition="dialog-bottom-transition"
    :form-valid="isValid"
  >
    <v-form ref="formNoteAdd" v-model="isValid">
      <v-col cols="10" lg="5" md="6" sm="10" class="mx-auto mt-5">
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
          :rules="contentRules"
        ></v-textarea>
      </v-col>
    </v-form>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'

export default {
  props: {
    shelf: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    Dialog,
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
    }
  },
  methods: {
    async showNoteAdd(item) {
      // バリデーションをクリア
      if (this.$refs.formNoteAdd) {
        this.$refs.formNoteAdd.resetValidation()
      }

      // 各種データを入力
      this.id = item.id
      this.format_type = item.format_type
      this.position = item.status.position || 0
      this.content = ''
      this.total = item.total

      // ダイアログを表示
      if (!(await this.$refs.dialogNoteAdd.showDialog())) return

      this.postNote()
    },
    postNote() {
      api({
        url: '/note/',
        method: 'post',
        data: {
          book: this.id,
          position: this.position,
          content: this.content,
        },
      })
        .then(() => {
          // ダイアログを閉じる
          this.$refs.dialogNoteAdd.hideDialog()

          if (!this.shelf) {
            this.$emit('reload')
          }

          this.$store.dispatch('message/setInfoMessage', {
            message: 'ノートを追加しました。',
          })
        })
        .catch(() => {
          this.$store.dispatch('message/setErrorMessage', {
            message: 'エラーが発生しました',
          })
        })
    },
  },
}
</script>
