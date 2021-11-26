<template>
  <v-container>
    <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
      <v-card class="pa-sm-5 pa-2">
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
              ref="email"
              type="email"
              v-model="formLogin.email.value"
              label="メールアドレス"
              :error-messages="formLogin.email.warnings"
              @input="formLogin.email.warnings = []"
              required
            ></v-text-field>
            <v-text-field
              ref="password"
              v-model="formLogin.password.value"
              label="パスワード"
              type="password"
              :error-messages="formLogin.password.warnings"
              @input="formLogin.password.warnings = []"
              required
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" block type="submit">
              <v-icon left>mdi-login</v-icon>
              ログイン
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
      email: {
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
    submitLogin: function () {
      // ログイン実行
      this.$store
        .dispatch('auth/login', {
          email: this.formLogin.email.value,
          password: this.formLogin.password.value,
        })
        .then(() => {
          console.log('Login succeeded.')
          // クエリ文字列にnextがなければホーム画面へ
          const next = this.$route.query.next || '/'
          this.$router.replace(next)
          this.$store.commit('message/clear')
          this.$store.dispatch('message/setInfoMessage', {
            message: 'ログインしました',
          })
        })
        .catch((error) => {
          let data = error.response.data
          if (error.response.status === 400) {
            Object.keys(data).forEach((key) => {
              this.formLogin[key].warnings = data[key]
            })
          } else {
            this.formLogin.email.value = ''
            this.$refs.email.focus()
          }
        })
    },
  },
}
</script>
