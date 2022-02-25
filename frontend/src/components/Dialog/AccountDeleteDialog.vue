<template>
  <Dialog
    ref="dialogDeleteAccount"
    title="アカウントの削除"
    hash="delete-account"
    :maxWidth="500"
  >
    <p>アカウントを削除します。パスワードを入力してください。</p>

    <div class="text-center mb-1">
      <v-icon large color="red">mdi-alert</v-icon>
    </div>

    <p class="red--text font-weight-bold text-center">
      「退会する」ボタンを押すと即座にアカウントが削除されます。
      <br />
      この操作は取り消せません！
    </p>

    <SendForm
      ref="formDeleteAccount"
      v-model="fieldsDeleteAccount"
      action="/auth/users/me/"
      method="delete"
      @form-success="$emit('delete', true)"
    >
      <template #footer>
        <span></span>
      </template>
    </SendForm>

    <template #actions>
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="$emit('delete', null)">
        キャンセル
      </v-btn>
      <v-btn color="red darken-1" dark @click="onClickDelete">
        <v-icon left>mdi-account-remove</v-icon>
        退会する
      </v-btn>
    </template>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Common/Dialog.vue'
import SendForm from '@/components/Common/SendForm.vue'

export default {
  components: { Dialog, SendForm },
  data: () => ({
    fieldsDeleteAccount: [
      {
        name: 'current_password',
        label: '現在のパスワード',
        type: 'password',
        required: true,
        value: '',
        warnings: [],
      },
    ],
  }),
  methods: {
    showDialog() {
      this.$refs.dialogDeleteAccount.dialog = true

      return new Promise((resolve) => {
        this.$once('delete', async (value) => {
          if (value) {
            this.$store.dispatch('auth/logout')
            this.$store.dispatch('message/setInfoMessage', {
              message: '退会操作が完了しました。ご利用ありがとうございました。',
            })
            resolve(value)
          } else {
            this.$refs.dialogDeleteAccount.dialog = false
            resolve(null)
          }
        })
      })
    },
    onClickDelete() {
      this.$refs.formDeleteAccount.submitForm()
    },
  },
}
</script>
