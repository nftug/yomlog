<template>
  <v-container>
    <!-- リセットページ -->
    <template v-if="$route.params.uid && $route.params.token">
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
          <template v-slot:footer>
            <div class="mt-4">
              <v-btn type="submit" color="primary" block dark>
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
        <p>パスワードリセット用のメールを送信します。</p>

        <SendForm
          v-model="formEmailPassword"
          action="/auth/users/reset_password/"
          method="post"
          @form-success="onSucceedSendEmail"
        >
          <template v-slot:footer>
            <div class="pt-5">
              <v-btn type="submit" color="primary" block dark>
                メールを送信
              </v-btn>
            </div>
          </template>
        </SendForm>
      </div>
    </template>
  </v-container>
</template>

<script>
import SendForm from '@/components/SendForm.vue'

export default {
  components: {
    SendForm,
  },
  data() {
    return {
      formEmailPassword: {
        email: {
          label: 'メールアドレス',
          type: 'email',
          required: true,
          warnings: [],
          value: this.$store.state.auth.email,
          readonly: this.$store.state.auth.email.length > 0,
        },
      },
      formResetPassword: {
        new_password: {
          label: '新しいパスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        re_new_password: {
          label: '新しいパスワード (確認用)',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
      },
      tokenData: {
        uid: this.$route.params.uid,
        token: this.$route.params.token,
      },
    }
  },
  methods: {
    // メール送信成功
    onSucceedSendEmail: function () {
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
    // パスワードリセット成功
    onSucceedResetPassword: function () {
      // リセット後は強制的にログアウト
      if (this.$store.state.auth.isLoggedIn) {
        // console.log('Logout.')
        this.$store.dispatch('auth/logout')
      }

      this.$router.push('/login/')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'パスワードのリセットが完了しました。',
      })
    },
  },
}
</script>
