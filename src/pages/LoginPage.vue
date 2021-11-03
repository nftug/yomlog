<template>
  <v-container>
    <v-card max-width="500px" class="mx-auto pa-5 text-center">
      <v-form
        lazy-validation
        v-model="formLogin.valid"
        @submit.prevent="submitLogin()"
      >
        <v-card-title class="text-h4 mb-4">ログイン</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="formLogin.username"
                label="ユーザー名"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formLogin.password"
                label="パスワード"
                type="password"
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            block
            type="submit"
            :disabled="!formLogin.valid"
          >
            ログイン
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-container>
</template>

<script>
import { FormRulesMixin } from '@/mixins'

export default {
  mixins: [FormRulesMixin],
  data: () => ({
    formLogin: {
      valid: null,
      email: '',
      password: '',
    },
  }),
  methods: {
    // ログインボタン押下
    submitLogin: function () {
      // ログイン実行
      this.$store
        .dispatch('auth/login', {
          username: this.formLogin.username,
          password: this.formLogin.password,
        })
        .then(() => {
          console.log('Login succeeded.')
          // クエリ文字列にnextがなければホーム画面へ
          const next = this.$route.query.next || '/'
          this.$router.replace(next)
        })
    },
  },
}
</script>
