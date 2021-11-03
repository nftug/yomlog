<template>
  <v-container>
    <div class="col-xl-4 col-lg-5 col-md-6 col-sm-10 mx-auto">
      <v-card class="mx-auto pa-sm-5 pa-2">
        <v-form
          v-model="formLogin.valid"
          @submit.prevent="submitLogin()"
          ref="formLogin"
        >
          <v-card-title class="text-h4 mb-4">ログイン</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="formLogin.username.value"
              label="ユーザー名"
              :error-messages="formLogin.username.warnings"
              @input="formLogin.username.warnings = []"
              required
            ></v-text-field>
            <v-text-field
              v-model="formLogin.password.value"
              label="パスワード"
              type="password"
              :error-messages="formLogin.password.warnings"
              @input="formLogin.password.warnings = []"
              required
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" block type="submit">
              <v-icon left>mdi-login</v-icon>
              ログイン
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </div>
  </v-container>
</template>

<script>
import { FormRulesMixin } from '@/mixins'

export default {
  mixins: [FormRulesMixin],
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
    submitLogin: function () {
      // ログイン実行
      this.$store
        .dispatch('auth/login', {
          username: this.formLogin.username.value,
          password: this.formLogin.password.value,
        })
        .then(() => {
          console.log('Login succeeded.')
          // クエリ文字列にnextがなければホーム画面へ
          const next = this.$route.query.next || '/'
          this.$router.replace(next)
        })
        .catch((error) => {
          let data = error.response.data
          if (error.response.status === 400) {
            Object.keys(data).forEach((key) => {
              this.formLogin[key].warnings = data[key]
            })
          } else {
            this.$refs.formLogin.reset()
          }
        })
    },
  },
}
</script>
