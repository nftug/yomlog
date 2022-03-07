<template>
  <v-container v-if="$route.params.uid && $route.params.token">
    <!-- 認証ページ -->
    <Spinner size="100" />
  </v-container>

  <!-- 登録フォームページ -->
  <v-container v-else>
    <!-- メインエリア -->
    <div class="col-xl-3 col-lg-5 col-md-6 col-sm-10 mx-auto">
      <v-card class="pa-sm-5 pa-2" outlined>
        <v-card-title class="text-h4 mb-4 d-none d-lg-block">
          ユーザー登録
        </v-card-title>

        <v-card-text>
          <SendForm
            v-model="formSignUp"
            action="/auth/users/"
            method="post"
            :confirm-method="showTermsOfUseDialog"
            @form-success="onSucceedSend"
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
                  <v-icon left>mdi-account-plus</v-icon>
                  ユーザー登録
                </v-btn>
              </div>
            </template>
          </SendForm>
        </v-card-text>
      </v-card>
    </div>

    <Dialog ref="dialogConfirm" max-width="600" title="確認メールの送信">
      ユーザー登録確認のメールを送信しました。
      <br />
      メールに記載されたリンクをクリックして、ユーザー登録を完了させてください。
      <br />
      数分待っても確認のメールが届かない場合はご連絡ください。

      <template #actions="{ ok }">
        <v-spacer></v-spacer>
        <v-btn color="green darken-1" text @click="ok">OK</v-btn>
      </template>
    </Dialog>

    <Dialog
      ref="dialogTermsOfUse"
      max-width="800"
      title="利用規約への同意"
      label-ok="同意する"
      label-cancel="キャンセル"
      scrollable
    >
      ユーザー登録の際に以下の利用規約に同意する必要があります。
      <TermsOfUse outlined class="mt-3" title-class="text-h6"></TermsOfUse>
    </Dialog>
  </v-container>
</template>

<script>
import api from '@/services/api'
import Spinner from '@/components/Common/Spinner.vue'
import SendForm from '@/components/Common/SendForm.vue'
import Dialog from '@/components/Common/Dialog.vue'
import TermsOfUse from '@/components/TermsOfUse/TermsOfUse.vue'

export default {
  components: {
    Spinner,
    SendForm,
    Dialog,
    TermsOfUse,
  },
  data: () => ({
    dialog: false,
    formSignUp: [
      {
        name: 'username',
        label: 'ユーザー名',
        type: 'text',
        required: true,
        value: '',
        warnings: [],
      },
      {
        name: 'email',
        label: 'メールアドレス (任意)',
        type: 'email',
        required: false,
        value: '',
        warnings: [],
      },
      {
        name: 'fullname',
        label: 'お名前',
        type: 'group',
        fields: [
          {
            name: 'last_name',
            class: 'col-6',
            label: '姓 (任意)',
            type: 'text',
            value: '',
            warnings: [],
          },
          {
            name: 'first_name',
            class: 'col-6',
            label: '名 (任意)',
            type: 'text',
            value: '',
            warnings: [],
          },
        ],
      },
      {
        name: 'password',
        label: 'パスワード',
        type: 'password',
        required: true,
        value: '',
        warnings: [],
      },
      {
        name: 're_password',
        label: 'パスワード (確認用)',
        type: 'password',
        required: true,
        value: '',
        warnings: [],
      },
      {
        name: 'avatar',
        label: 'プロフィール画像',
        type: 'image',
        value: null,
        prevSrc: '',
        warnings: [],
      },
    ],
  }),
  created() {
    // UIDとトークンを指定→ユーザーのアクティベーションに進む
    if (this.$route.params.uid && this.$route.params.token) {
      this.activateUser()
    }
  },
  methods: {
    // 利用規約ダイアログの表示
    async showTermsOfUseDialog() {
      return await this.$refs.dialogTermsOfUse.showDialog()
    },
    // フォーム送信成功
    async onSucceedSend({ username, is_active }) {
      if (is_active) {
        // アカウントがアクティブの場合、そのままログイン
        const { value: password } = this.formSignUp.find(
          ({ name }) => name === 'password'
        )

        await this.$store.dispatch('auth/login', { username, password })
        this.$router.replace({ name: 'home' })
        this.$store.dispatch('message/setInfoMessage', {
          message: 'アカウントを作成しました。',
        })
      } else {
        // アクティブでない場合、メール送信済みのダイアログを表示
        await this.$refs.dialogConfirm.showDialog()
        this.$router.push('/login')
      }
    },
    // ユーザーのアクティベーション
    async activateUser() {
      try {
        await api({
          method: 'post',
          url: '/auth/users/activation/',
          data: {
            uid: this.$route.params.uid,
            token: this.$route.params.token,
          },
        })

        this.$router.replace('/login/')
        this.$store.dispatch('message/setInfoMessage', {
          message: 'アカウントが承認されました。',
        })
      } catch (error) {
        this.$router.replace('/login/')
        const status = error.response ? error.response.status : 500
        let message

        if (status === 403) {
          message = 'アカウントは既に承認されています。'
        } else {
          message = '不正なトークンです。'
        }
        this.$store.dispatch('message/setErrorMessage', { message: message })
      }
    },
  },
}
</script>
