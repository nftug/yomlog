<template>
  <v-container v-if="$route.params.uid && $route.params.token">
    <!-- 認証ページ -->
    <Spinner size="100" />
  </v-container>

  <!-- 登録フォームページ -->
  <v-container v-else>
    <!-- メインエリア -->
    <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
      <v-card class="pa-sm-5 pa-2">
        <v-card-title class="text-h4 mb-4 d-none d-lg-block">
          ユーザー登録
        </v-card-title>

        <v-card-text>
          <SendForm
            v-model="formSignUp"
            action="/auth/users/"
            method="post"
            @form-success="onSucceedSend"
          >
            <template #footer>
              <div class="pt-5">
                <v-btn type="submit" color="primary" block>
                  <v-icon left>mdi-account-plus</v-icon>
                  ユーザー登録
                </v-btn>
              </div>
            </template>
          </SendForm>
        </v-card-text>
      </v-card>
    </div>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title class="text-h5">確認メールの送信</v-card-title>

        <v-card-text>
          <p>
            ユーザー登録確認のメールを送信しました。
            <br />
            メールに記載されたリンクをクリックして、ユーザー登録を完了させてください。
            <br />
            数分待っても確認のメールが届かない場合はご連絡ください。
          </p>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="onClickDialogOk()">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import api from '@/services/api'
import Spinner from '@/components/Spinner.vue'
import SendForm from '@/components/SendForm.vue'

export default {
  components: {
    Spinner,
    SendForm,
  },
  data() {
    return {
      dialog: false,
      formSignUp: {
        email: {
          label: 'メールアドレス',
          type: 'email',
          required: true,
          value: '',
          warnings: [],
        },
        fullname: {
          label: 'お名前',
          type: 'group',
          fields: {
            last_name: {
              class: 'col-6',
              label: '姓',
              type: 'text',
              value: '',
              warnings: [],
            },
            first_name: {
              class: 'col-6',
              label: '名',
              type: 'text',
              value: '',
              warnings: [],
            },
          },
        },
        password: {
          label: 'パスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        re_password: {
          label: 'パスワード (確認用)',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        avatar: {
          label: 'プロフィール画像',
          type: 'image',
          value: null,
          prevSrc: '',
          warnings: [],
        },
      },
    }
  },
  created() {
    // UIDとトークンを指定→ユーザーのアクティベーションに進む
    if (this.$route.params.uid && this.$route.params.token) {
      this.activateUser()
    }
  },
  methods: {
    // フォーム送信成功
    onSucceedSend: function () {
      this.dialog = true
    },
    // ユーザーのアクティベーション
    activateUser: function () {
      api({
        method: 'post',
        url: '/auth/users/activation/',
        data: {
          uid: this.$route.params.uid,
          token: this.$route.params.token,
        },
      })
        .then(() => {
          this.$router.replace('/login/')
          this.$store.dispatch('message/setInfoMessage', {
            message: 'アカウントが承認されました。',
          })
        })
        .catch((error) => {
          this.$router.replace('/login/')
          const status = error.response ? error.response.status : 500
          let message

          if (status === 403) {
            message = 'アカウントは既に承認されています。'
          } else {
            message = '不正なトークンです。'
          }
          this.$store.dispatch('message/setErrorMessage', { message: message })
        })
    },
    // ユーザー登録ダイアログ: OK
    onClickDialogOk: function () {
      this.dialog = false
      this.$router.push('/login/')
    },
  },
}
</script>
