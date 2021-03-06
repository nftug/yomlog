<template>
  <v-container>
    <!-- リセットページ -->
    <template v-if="hasResetToken">
      <!-- メインエリア -->
      <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
        <p class="text-h4 mt-4 mb-5 d-none d-lg-block">パスワードのリセット</p>

        <SendForm
          v-model="formResetPassword"
          action="/auth/users/reset_password_confirm/"
          method="post"
          :additional-data="tokenData"
          @form-success="onSucceedResetPassword"
        >
          <template #footer="{ isValid }">
            <div class="mt-4">
              <v-btn
                type="submit"
                color="primary"
                block
                :dark="isValid"
                :disabled="!isValid"
              >
                パスワードのリセット
              </v-btn>
            </div>
          </template>
        </SendForm>
      </div>
    </template>

    <!-- メール送信ページ -->
    <template v-else>
      <!-- メインエリア -->
      <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
        <p class="text-h4 mt-4 pb-4 d-none d-lg-block">パスワードのリセット</p>
        <p class="text-body-2">パスワードリセット用のメールを送信します。</p>

        <SendForm
          v-model="formEmailPassword"
          action="/auth/users/reset_password/"
          method="post"
          @form-success="onSucceedSendEmail"
        >
          <template #footer="{ isValid }">
            <div class="mt-4">
              <v-btn
                type="submit"
                color="primary"
                block
                :dark="isValid"
                :disabled="!isValid"
              >
                メールを送信
              </v-btn>
            </div>
          </template>
        </SendForm>
      </div>

      <RequireEmailDialog></RequireEmailDialog>
    </template>
  </v-container>
</template>

<script>
import SendForm from '@/components/Common/SendForm.vue'
import RequireEmailDialog from '@/components/Dialog/RequireEmailDialog.vue'

export default {
  components: {
    SendForm,
    RequireEmailDialog,
  },
  data() {
    return {
      formEmailPassword: [
        {
          name: 'email',
          label: 'メールアドレス',
          type: 'email',
          required: true,
          warnings: [],
          value: this.$store.state.auth.email,
          readonly: this.$store.state.auth.email.length > 0,
        },
      ],
      formResetPassword: [
        {
          name: 'new_password',
          label: '新しいパスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        {
          name: 're_new_password',
          label: '新しいパスワード (確認用)',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
      ],
      tokenData: {
        uid: this.$route.params.uid,
        token: this.$route.params.token,
      },
    }
  },
  computed: {
    hasResetToken() {
      return this.$route.params.uid && this.$route.params.token
    },
  },
  methods: {
    onSucceedSendEmail() {
      if (this.$store.state.auth.isLoggedIn) {
        // ログイン時はルートに遷移
        this.$router.push('/')
      } else {
        // ログアウト時はログイン画面に遷移
        this.$router.push('/login')
      }

      this.$store.dispatch('message/setInfoMessage', {
        message: 'パスワードリセット用のメールを送信しました。',
      })
    },
    onSucceedResetPassword() {
      // リセット後は強制的にログアウト
      if (this.$store.state.auth.isLoggedIn) {
        this.$store.dispatch('auth/logout')
      }

      this.$router.push('/login')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'パスワードのリセットが完了しました。',
      })
    },
  },
}
</script>
