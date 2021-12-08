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
        :max="total"
        :suffix="` / ${total}`"
        :rules="positionRules"
        :disabled="to_be_read"
        :error-messages="positionErrors"
        @input="positionErrors = []"
      ></v-text-field>
      <v-switch
        v-model="to_be_read"
        label="あとで読む"
        :rules="toBeReadRules"
      ></v-switch>
    </v-form>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'

export default {
  components: {
    Dialog,
  },
  data() {
    return {
      id: '',
      position: 0,
      total: 0,
      format_type: 0,
      to_be_read: false,
      positionRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (!this.format_type ? 'ページ数' : '位置No') + 'が不正です',
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
    async showStatusAddDialog(item) {
      // バリデーションをクリア
      if (this.$refs.formStatusAdd) {
        this.$refs.formStatusAdd.resetValidation()
        this.positionErrors = []
      }

      // 各種データを入力
      this.id = item.id
      this.format_type = item.format_type
      this.position = item.status[0].position || 0
      this.total = item.total
      this.to_be_read = item.status[0].state === 'to_be_read'

      // デフォルト値を保存
      this.defaultValues.position = this.position
      this.defaultValues.to_be_read = this.to_be_read

      // ダイアログを表示
      this.$refs.dialogStatusAdd.showDialog()
    },
    postStatus() {
      api({
        url: '/status_log/',
        method: 'post',
        data: {
          book: this.id,
          position: this.to_be_read ? 0 : this.position,
        },
      })
        .then(({ data }) => {
          // ダイアログを閉じる
          this.$refs.dialogStatusAdd.hideDialog()

          this.$emit('reload', data.state)

          this.$store.dispatch('message/setInfoMessage', {
            message: '進捗状況を記録しました。',
          })
        })
        .catch(({ response: { data } }) => {
          if (data.position) {
            this.positionErrors = data.position
          } else {
            this.$store.dispatch('message/setErrorMessage', {
              message: 'エラーが発生しました',
            })
          }
        })
    },
  },
}
</script>
