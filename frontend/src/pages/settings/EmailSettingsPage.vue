<template>
  <SendForm
    v-model="changeEmailForm"
    action="/auth/users/me/"
    method="patch"
    @form-success="onSucceedChangeEmail"
  >
    <template v-slot:footer>
      <div class="mt-4">
        <v-btn type="submit" color="primary" block dark>設定の変更</v-btn>
      </div>
    </template>
  </SendForm>
</template>

<script>
import SendForm from '@/components/Common/SendForm.vue'

export default {
  components: {
    SendForm,
  },
  data() {
    return {
      changeEmailForm: {
        email: {
          label: 'メールアドレス',
          type: 'email',
          required: true,
          value: this.$store.state.auth.email,
          warnings: [],
        },
      },
    }
  },
  methods: {
    // パスワード変更押下
    onSucceedChangeEmail() {
      this.$store.dispatch('auth/reload')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'メールアドレスを変更しました。',
      })
    },
  },
}
</script>
