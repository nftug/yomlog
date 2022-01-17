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

// リトライなしのAPIメソッド
const rawApi = axios.create({ ...config })

// リトライありのAPIメソッド
const api = axios.create({
  ...config,
  raxConfig: {
    retry: 3,
    noResponseRetries: 2,
    retryDelay: 1000,
    statusCodesToRetry: [
      [100, 199],
      [401, 429],
      [500, 599],
    ],
    httpMethodsToRetry: [
      'GET',
      'HEAD',
      'OPTIONS',
      'DELETE',
      'PUT',
      'PATCH',
      'POST',
    ],
    shouldRetry: async (error) => {
      const raxConfig = rax.getConfig(error)
      if (raxConfig.currentRetryAttempt >= raxConfig.retry) return false

      const status = error.response ? error.response.status : 500
      if (status === 401 && error.response.data.code === 'token_not_valid') {
        // 認証エラー
        try {
          // トークンのリフレッシュ
          console.log('Access token expired. Trying to refresh...')
          const access = await store.dispatch('auth/refresh')
          console.log('Refresh succeeded. Retrying to request...')
          // ヘッダー更新
          error.config.headers.Authorization = 'JWT ' + access
          return true
        } catch (error) {
          console.log('Refresh token expired.')
          return false
        }
      } else {
        return rax.shouldRetryRequest(error)
      }
    },
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
  (error) => {
    console.log('error.response=', error.response)
    const status = error.response ? error.response.status : 500

    // エラー内容に応じてstoreのメッセージを更新
    let message
    if (status === 400 || status === 404) {
      // バリデーションNGと404の処理は各コンポーネントに任せる
      return Promise.reject(error)
    } else {
      if (status === 401) {
        if (error.response.data.code === 'token_not_valid') {
          store.dispatch('auth/logout', {
            next: router.history.current.fullPath,
          })
          message = 'ログインの期限切れです。'
        } else {
          message = '認証エラーです。'
          store.dispatch('auth/logout')
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

export { api as default, rawApi }
