<template>
  <div id="email-settings-page">
    <!-- メインエリア -->
    <div class="col-lg-7 col-md-6 col-sm-10 mx-auto">
      <SendForm
        v-model="changeEmailForm"
        action="/auth/users/set_email/"
        method="post"
        @form-success="onSucceedChangeEmail"
      >
        <template v-slot:footer>
          <div class="mt-4">
            <v-btn type="submit" color="primary" block dark>設定の変更</v-btn>
          </div>
          <div class="text-right pt-5 text-body-2">
            <div class="mb-1">
              <router-link class="button secondaryAction" to="/password/reset/">
                パスワードを忘れましたか？
              </router-link>
            </div>
          </div>
        </template>
      </SendForm>
    </div>
  </div>
</template>

<script>
import SendForm from '@/components/SendForm.vue'

export default {
  components: {
    SendForm,
  },
  data() {
    return {
      changeEmailForm: {
        new_email: {
          label: '新しいメールアドレス',
          type: 'email',
          required: true,
          value: '',
          warnings: [],
        },
        current_password: {
          label: '現在のパスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
      },
    }
  },
  methods: {
    // パスワード変更押下
    onSucceedChangeEmail: function () {
      this.$store.dispatch('auth/reload')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'メールアドレスを変更しました。',
      })
    },
  },
}
</script>
