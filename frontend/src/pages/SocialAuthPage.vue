<template>
  <div></div>
</template>

<script>
import api, { rawApi } from '@/services/api'

export default {
  created() {
    const routeName = this.$route.name
    if (routeName === 'social_start') {
      this.startPoint()
    } else if (routeName === 'social_end') {
      this.endPoint()
    }
  },
  methods: {
    async startPoint() {
      // スタートポイント: 指定された認証ページにリダイレクト
      const { provider } = this.$route.query

      try {
        const { data } = await api.get(`/auth/social/o/${provider}/`, {
          params: {
            redirect_uri: `${process.env.VUE_APP_SOCIAL_ENDPOINT}/${provider}`,
          },
        })
        location.replace(data.authorization_url)
      } catch {
        this.error('OAuth2認証にアクセスできません。')
      }
    },
    async endPoint() {
      // エンドポイント:
      // 連携先から取得したcodeとstateをもとに、ログイントークンを取得してログイン

      // 送信するデータの作成
      const { code, state } = this.$route.query
      const params = new URLSearchParams()
      params.append('code', code)
      params.append('state', state)

      // providerの取得
      const { provider } = this.$route.params

      // トークンの取得
      try {
        // NOTE: トークン取得は同一のルートからのみ有効 (vue-cliのテスト用サーバーでは無効)
        const { data } = await rawApi({
          method: 'post',
          url: `/auth/social/o/${provider}/`,
          data: params,
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })

        // トークンの設定
        this.$store.dispatch('auth/loginWithToken', data)

        // ホーム画面に遷移
        this.$router.replace({ name: 'home' })
      } catch {
        this.error('OAuth認証に失敗しました。')
      }
    },
    error(message) {
      this.$router.replace({ name: 'login' })
      this.$store.dispatch('message/setErrorMessage', { message })
    },
  },
}
</script>
