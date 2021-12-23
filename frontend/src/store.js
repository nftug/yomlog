import Vue from 'vue'
import Vuex from 'vuex'
import api from '@/services/api'
import router from './router'

Vue.use(Vuex)

// 認証情報モジュール
const authModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    fullname: '',
    id: '',
    avatar: '',
    isSuperuser: false,
    isLoggedIn: false,
  },
  mutations: {
    set(state, { user }) {
      for (const key in state) {
        state[key] = user[key]
      }
      state.isLoggedIn = true
    },
    clear(state) {
      for (const key in state) {
        if (typeof state[key] === 'string') {
          state[key] = ''
        } else if (typeof state[key] === 'boolean') {
          state[key] = false
        } else {
          state[key] = 0
        }
      }
    },
  },
  actions: {
    // ログイン
    async login({ dispatch }, { email, password }) {
      const { data } = await api.post('/auth/jwt/create/', { email, password })
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      return dispatch('reload')
    },
    // ログアウト
    logout({ commit }) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      commit('clear')
      router.push('/login')
    },
    // ユーザー情報更新
    async reload({ commit }) {
      const { data: user } = await api.get('/auth/users/me/')
      commit('set', { user })
      return user
    },
    // アクセストークンのリフレッシュ
    async refresh() {
      localStorage.removeItem('access')
      const refresh = localStorage.getItem('refresh')

      if (refresh !== null) {
        const { data } = await api.post('/auth/jwt/refresh', { refresh })
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', refresh)
        return data.access
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

// ドロワーモジュール
const drawerModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    drawer: null,
  },
  mutations: {
    set(state, val) {
      state.drawer = val
    },
    toggle(state) {
      state.drawer = !state.drawer
    },
  },
}

// 本棚モジュール
const bookListModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    items: [],
    totalItems: 0,
    totalPages: 0,
    isLoading: false,
    isDirty: false,
  },
  mutations: {
    setLoading(state, val) {
      state.isLoading = val
    },
    setProps(state, payload) {
      state.totalItems = payload.totalItems
      state.totalPages = payload.totalPages
    },
    setDirty(state, val) {
      state.isDirty = val
    },
    add(state, item) {
      state.items.push(item)
    },
    set(state, item) {
      const index = state.items.findIndex((e) => e.id === item.id)
      state.items.splice(index, 1, { ...item })
      state.isDirty = true
    },
    delete(state, item) {
      const index = state.items.findIndex((e) => e.id === item.id)
      state.items.splice(index, 1)
    },
    clear(state) {
      state.items = []
    },
  },
  actions: {
    async getBookItem({ state }, id) {
      const ret = { ...state.items.find((e) => e.id === id) }
      if (Object.keys(ret).length) {
        return ret
      } else {
        try {
          const { data } = await api.get(`/book/${id}/`)
          return data
        } catch (error) {
          return Promise.reject(error)
        }
      }
    },
    setDirtyWithDiffState({ commit }, { book, callback }) {
      const oldState = JSON.stringify(book.status[0])
      callback(book)
      const newState = JSON.stringify(book.status[0])

      if (oldState !== newState) {
        commit('setDirty', true)
        return true
      } else {
        return false
      }
    },
    addProp({ dispatch }, { book, prop, data }) {
      return dispatch('setDirtyWithDiffState', {
        book,
        callback: (newBook) => {
          newBook[prop].unshift(data)
        },
      })
    },
    editProp({ dispatch }, { book, prop, data }) {
      return dispatch('setDirtyWithDiffState', {
        book,
        callback: (newBook) => {
          const index = newBook[prop].findIndex((e) => e.id === data.id)
          newBook[prop].splice(index, 1, data)
        },
      })
    },
    deleteProp({ dispatch }, { book, prop, id }) {
      return dispatch('setDirtyWithDiffState', {
        book,
        callback: (newBook) => {
          const index = newBook[prop].findIndex((e) => e.id === id)
          newBook[prop].splice(index, 1)
        },
      })
    },
    setProp({ dispatch }, { book, prop, data }) {
      return dispatch('setDirtyWithDiffState', {
        book,
        callback: (newBook) => {
          newBook[prop] = data
        },
      })
    },
  },
}

const store = new Vuex.Store({
  modules: {
    auth: authModule,
    message: messageModule,
    drawer: drawerModule,
    bookList: bookListModule,
  },
})

export default store
