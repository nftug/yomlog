<template>
  <div id="status-add">
    <Dialog ref="dialogStatusAdd" title="進捗状況の入力" :max-width="400">
      <template #content>
        <v-form ref="formStatusAdd" v-model="isValid">
          <v-text-field
            v-model="position"
            :label="!format_type ? 'ページ数' : '位置No'"
            type="number"
            min="0"
            :suffix="` / ${total}`"
            :rules="pageRules"
            :disabled="to_be_read"
          ></v-text-field>
          <v-switch v-model="to_be_read" label="あとで読む"></v-switch>
        </v-form>
      </template>

      <template #actions="{ ok, cancel }">
        <v-spacer></v-spacer>
        <v-btn color="green darken-1" text @click="cancel">キャンセル</v-btn>
        <v-btn color="green darken-1" text @click="ok" :disabled="!isValid">
          OK
        </v-btn>
      </template>
    </Dialog>
  </div>
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
      position: 0,
      total: 0,
      format_type: 0,
      to_be_read: false,
      pageRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (!this.format_type ? 'ページ数' : '位置No') + 'が不正です',
      ],
      isValid: false,
    }
  },
  methods: {
    async showStatusAdd(
      { id, format_type, status: { position, state }, total },
      shelf
    ) {
      // バリデーションをクリア
      if (this.$refs.formStatusAdd) {
        this.$refs.formStatusAdd.resetValidation()
      }

      // 各種データを入力
      this.format_type = format_type
      this.position = position || 0
      this.total = total
      this.to_be_read = state === 'to_be_read'

      // ダイアログを表示
      if (!(await this.$refs.dialogStatusAdd.showDialog())) return

      // ステータスを投稿
      api({
        url: '/status_log/',
        method: 'post',
        data: {
          book: id,
          position: this.to_be_read ? 0 : this.position,
        },
      }).then(({ data }) => {
        if (shelf) {
          this.$router.push(`/shelf/${data.state}`)
        }

        this.$store.dispatch('message/setInfoMessage', {
          message: '進捗状況を記録しました。',
        })
      })
    },
  },
}
</script>
