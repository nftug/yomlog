<template>
  <Dialog
    ref="dialogRequireEmail"
    title="メールアドレスが設定されていません"
    max-width="500"
  >
    <p>
      この操作を行うにはメールアドレスの設定が必要です。
      <br />
      先にメールアドレスの設定を完了させてください。
    </p>
    <template #actions="{ ok }">
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="ok">OK</v-btn>
    </template>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Common/Dialog.vue'

export default {
  components: { Dialog },
  async mounted() {
    // メールアドレスが設定されていない状態でリセットを試みた場合
    // ダイアログを表示してメールアドレスの設定に遷移
    const { email, isLoggedIn } = this.$store.state.auth

    if (isLoggedIn && !email) {
      await this.$refs.dialogRequireEmail.showDialog()
      this.$router.push({ name: 'settings_email' })
    }
  },
}
</script>
