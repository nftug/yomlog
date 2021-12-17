<template>
  <Dialog
    ref="dialogStatusAdd"
    title="進捗状況の入力"
    :max-width="350"
    :ok="postStatus"
    :form-valid="isValid"
  >
    <v-form ref="formStatusAdd" v-model="isValid" @submit.prevent>
      <v-text-field
        v-model="position"
        :label="!format_type ? 'ページ数' : '位置No'"
        type="number"
        min="0"
        autofocus
        :max="total"
        :suffix="` / ${total}`"
        :rules="to_be_read ? [] : positionRules"
        :disabled="to_be_read"
        :error-messages="positionErrors"
        @input="positionErrors = []"
        @keydown.enter="handleKeydownEnter"
      ></v-text-field>
      <v-switch
        v-model="to_be_read"
        label="あとで読む"
        :disabled="!!statusId"
        :rules="toBeReadRules"
      ></v-switch>
    </v-form>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'
import { BookListMixin } from '@/mixins'

export default {
  components: {
    Dialog,
  },
  mixins: [BookListMixin],
  data() {
    return {
      statusId: '',
      bookId: '',
      position: 0,
      total: 0,
      format_type: 0,
      to_be_read: false,
      positionRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (!this.format_type ? 'ページ数' : '位置No') + 'が不正です',
        (v) =>
          v !== this.defaultValues.position ||
          '以前と異なる数値を入力してください',
      ],
      toBeReadRules: [
        (v) =>
          !(v && this.defaultValues.to_be_read) ||
          '以前と異なるステータスを入力してください',
      ],
      positionErrors: [],
      isValid: false,
      defaultValues: {
        position: 0,
        to_be_read: false,
      },
    }
  },
  methods: {
    showStatusPostDialog({ book, id }) {
      // バリデーションをリセット
      if (this.$refs.formStatusAdd) {
        this.$refs.formStatusAdd.resetValidation()
        this.positionErrors = []
      }

      // 各種データを入力
      this.bookId = book.id
      this.format_type = book.format_type
      this.total = book.total

      if (id) {
        const status = book.status.find((e) => e.id === id)
        this.statusId = id
        this.position = status.position
        this.to_be_read = status.state === 'to_be_read'
      } else {
        this.statusId = ''
        this.position = this.currentState(book).position || 0
        this.to_be_read = this.currentState(book).state === 'to_be_read'
      }

      // デフォルト値を保存
      this.defaultValues.position = this.position
      this.defaultValues.to_be_read = this.to_be_read

      // ダイアログを表示
      this.$refs.dialogStatusAdd.showDialog()
    },
    postStatus() {
      let params = { position: this.to_be_read ? 0 : this.position }
      let method, url

      if (this.statusId) {
        method = 'patch'
        url = `/status/${this.statusId}/`
      } else {
        params.book = this.bookId
        method = 'post'
        url = '/status/'
      }

      api({
        url: url,
        method: method,
        data: params,
      })
        .then(({ data }) => {
          // ダイアログを閉じる
          this.$refs.dialogStatusAdd.hideDialog()

          this.$emit('post', 'status', data)

          this.$store.dispatch('message/setInfoMessage', {
            message: '進捗状況を記録しました。',
          })
        })
        .catch((error) => {
          if (error.data) {
            const { data } = error
            if (data.position) {
              this.positionErrors = data.position
            } else {
              this.$store.dispatch('message/setErrorMessage', {
                message: 'エラーが発生しました',
              })
            }
          }
        })
    },
    handleKeydownEnter() {
      if (!this.$refs.formStatusAdd.validate()) return
      this.postStatus()
    },
  },
}
</script>
