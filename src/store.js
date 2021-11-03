import Vue from 'vue'
import Vuex from 'vuex'
import api from '@/services/api'

Vue.use(Vuex)

// 認証情報モジュール
const authModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    username: '',
    email: '',
    isSuperuser: false,
    isLoggedIn: false,
  },
  getters: {
    username: (state) => state.username,
    email: (state) => state.email,
    isSuperUser: (state) => state.isSuperuser,
    isLoggedIn: (state) => state.isLoggedIn,
  },
  mutations: {
    set(state, payload) {
      state.username = payload.user.username
      state.email = payload.user.email
      state.isSuperuser = payload.user.is_superuser
      state.isLoggedIn = true
    },
    clear(state) {
      state.username = ''
      state.email = ''
      state.isSuperuser = false
      state.isLoggedIn = false
    },
  },
  actions: {
    // ログイン
    login(context, payload) {
      return api
        .post('/auth/jwt/create/', {
          username: payload.username,
          password: payload.password,
        })
        .then((response) => {
          // 認証用トークンとリフレッシュトークンをlocalStorageに保存
          localStorage.setItem('access', response.data.access)
          localStorage.setItem('refresh', response.data.refresh)
          // ユーザー情報を取得してstoreのユーザー情報を更新
          return context.dispatch('reload')
        })
    },
    // ログアウト
    logout(context) {
      // 認証用トークンとリフレッシュトークンをlocalstorageから削除
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      // storeのユーザー情報をクリア
      context.commit('clear')
    },
    // ユーザー情報更新
    reload(context) {
      return api.get('/auth/users/me/').then((response) => {
        const user = response.data
        // storeのユーザー情報を更新
        context.commit('set', { user: user })
        return user
      })
    },
    // アクセストークンのリフレッシュ
    refresh() {
      localStorage.removeItem('access')
      const refresh = localStorage.getItem('refresh')

      if (refresh != null) {
        return api
          .post('/auth/jwt/refresh/', {
            refresh: refresh,
          })
          .then((response) => {
            localStorage.setItem('access', response.data.access)
            localStorage.setItem('refresh', refresh)
            return response.data.access
          })
      }
    },
  },
}

// グローバルメッセージモジュール
const messageModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    error: '',
    warnings: [],
    info: '',
  },
  getters: {
    error: (state) => state.error,
    warnings: (state) => state.warnings,
    info: (state) => state.info,
  },
  mutations: {
    set(state, payload) {
      if (payload.error) state.error = payload.error
      if (payload.warnings) state.warnings = payload.warnings
      if (payload.info) state.info = payload.info
    },
    clear(state) {
      state.error = ''
      state.warnings = []
      state.info = ''
    },
  },
  actions: {
    // エラーメッセージ表示
    setErrorMessage(context, payload) {
      context.commit('clear')
      context.commit('set', { error: payload.message })
    },
    // 警告メッセージ (複数) 表示
    setWarningMessages(context, payload) {
      context.commit('clear')
      context.commit('set', { warnings: payload.messages })
    },
    // インフォメーションメッセージ表示
    setInfoMessage(context, payload) {
      context.commit('clear')
      context.commit('set', { info: payload.message })
    },
    // 全メッセージ削除
    clearMessages(context) {
      context.commit('clear')
    },
  },
}

const store = new Vuex.Store({
  modules: {
    auth: authModule,
    message: messageModule,
  },
})

export default store
