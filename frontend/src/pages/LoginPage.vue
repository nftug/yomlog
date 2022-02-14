<template>
  <v-container>
    <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
      <v-card class="pa-sm-5 pa-2" outlined>
        <v-form
          v-model="formLogin.valid"
          @submit.prevent="submitLogin()"
          ref="formLogin"
        >
          <v-card-title class="text-h4 mb-4 d-none d-lg-block">
            ログイン
          </v-card-title>
          <v-card-text>
            <v-text-field
              ref="username"
              id="username"
              v-model="formLogin.username.value"
              label="ユーザー名"
              :error-messages="formLogin.username.warnings"
              @input="formLogin.username.warnings = []"
              required
            ></v-text-field>
            <v-text-field
              ref="password"
              id="password"
              v-model="formLogin.password.value"
              label="パスワード"
              type="password"
              :error-messages="formLogin.password.warnings"
              @input="formLogin.password.warnings = []"
              required
            ></v-text-field>
          </v-card-text>

          <v-card-actions>
            <v-btn color="primary" block type="submit" aria-label="login">
              <v-icon left>mdi-login</v-icon>
              ログイン
            </v-btn>
          </v-card-actions>
          <v-card-actions>
            <v-btn
              disabled
              block
              to="/login/social/start/google-oauth2"
              aria-label="google-login"
            >
              <v-icon left>mdi-google</v-icon>
              Googleでログイン
            </v-btn>
          </v-card-actions>

          <div class="text-right pt-4 text-body-2">
            <div class="mb-1">
              <router-link class="button secondaryAction" to="/password/reset">
                パスワードを忘れましたか？
              </router-link>
            </div>
          </div>
        </v-form>
      </v-card>
    </div>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    formLogin: {
      valid: false,
      username: {
        value: '',
        warnings: [],
      },
      password: {
        value: '',
        warnings: [],
      },
    },
  }),
  methods: {
    // ログインボタン押下
    async submitLogin() {
      // ログイン実行
      try {
        await this.$store.dispatch('auth/login', {
          username: this.formLogin.username.value,
          password: this.formLogin.password.value,
        })
      } catch ({ response }) {
        const data = response.data
        if (response.status === 400) {
          Object.keys(data).forEach((key) => {
            this.formLogin[key].warnings = data[key]
          })
        } else {
          this.$refs.username.focus()
        }
        return
      }

      // console.log('Login succeeded.')
      // クエリ文字列にnextがなければホーム画面へ
      const next = this.$route.query.next || '/'
      this.$router.replace(next)
      this.$store.commit('message/clear')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'ログインしました。',
      })
    },
  },
}
</script>
