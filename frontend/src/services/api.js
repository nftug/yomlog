import axios from 'axios'
import * as rax from 'retry-axios'
import store from '@/store'
import router from '@/router'

// CSRFトークンの送信設定
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// 基本設定
const config = {
  baseURL: process.env.VUE_APP_ROOT_API,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
}

// リトライありのAPIメソッド
const api = axios.create({
  ...config,
  raxConfig: {
    retry: 3,
    noResponseRetries: 2,
    retryDelay: 1000,
    statusCodesToRetry: [[500, 599]],
    httpMethodsToRetry: ['GET', 'HEAD', 'OPTIONS'],
  },
})

rax.attach(api)

// 共通前処理
api.interceptors.request.use(
  (config) => {
    // 認証用トークンがあればリクエストヘッダに加える
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = 'JWT ' + token
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 共通エラー処理
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const status = error.response ? error.response.status : 500

    // エラー内容に応じてstoreのメッセージを更新
    let message
    if (status === 400 || status === 404) {
      // バリデーションNGと404の処理は各コンポーネントに任せる
      return Promise.reject(error)
    } else {
      if (status === 401) {
        const [errorCode, url] = [
          error.response.data.code,
          error.response.config.url,
        ]
        if (errorCode === 'token_not_valid') {
          if (url !== '/auth/jwt/refresh/') {
            // トークン期限切れの場合、更新処理を入れる
            const access = await store.dispatch('auth/refresh')
            error.config.headers.Authorization = 'JWT ' + access
            return api.request(error.config)
          } else {
            // トークン更新失敗の場合、期限切れの処理を行う
            if (store.state.auth.isLoggedIn) {
              store.dispatch('auth/logout', {
                next: router.history.current.fullPath,
              })
            }
            message = 'ログインの期限切れです。'
          }
        } else {
          store.dispatch('auth/logout')
          message = '認証エラーです。'
        }
      } else if (status === 403) {
        // 権限エラー
        message = '権限エラーです。'
      } else {
        // その他のエラー
        message = error.response.data.detail
      }
      store.dispatch('message/setErrorMessage', { message })
      return Promise.reject(error)
    }
  }
)

export default api
