import Vue from 'vue'
import Vuex from 'vuex'
import api, { rawApi } from '@/services/api'
import router from './router'
import moment from 'moment'

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
    avatar_thumbnail: '',
    date_joined: '',
    is_superuser: false,
    analytics: null,
    isLoggedIn: false,
  },
  getters: {
    created_at: (state) => moment(state.date_joined).format('yyyy/MM/DD'),
    authorsCount: ({ analytics: { authors_count } }) => ({
      authors: Object.keys(authors_count),
      counts: Object.keys(authors_count).map((key) => authors_count[key]),
    }),
    pagesDaily: ({ analytics: { pages_daily } }) => {
      const keys = Object.keys(pages_daily)
      keys.sort()
      const start = moment(keys[0])
      const end = moment().startOf('day')

      // 日付範囲で結果の配列を生成
      const [date, pages] = [[], []]

      for (let d = start; d <= end; d = moment(d).add(1, 'days')) {
        date.push(moment(d).format('MM/DD'))

        const key = moment(d).format('yyyy-MM-DD')
        if (pages_daily.hasOwnProperty(key)) {
          pages.push(pages_daily[key])
        } else {
          pages.push(0)
        }
      }

      return { date, pages }
    },
  },
  mutations: {
    set(state, { user }) {
      for (const key in state) {
        state[key] = user[key]
      }
      state.isLoggedIn = true
    },
    clear(state) {
      for (const [key, value] of Object.entries(state)) {
        if (typeof value === 'string') {
          state[key] = ''
        } else if (typeof value === 'boolean') {
          state[key] = false
        } else if (typeof value === 'number') {
          state[key] = 0
        } else {
          state[key] = null
        }
      }
    },
  },
  actions: {
    // ログイン
    async login({ dispatch }, { username, password }) {
      const { data } = await api.post('/auth/jwt/create/', {
        username,
        password,
      })
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      return dispatch('reload')
    },
    // トークンを指定してログイン
    async loginWithToken({ dispatch }, { access, refresh }) {
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      return dispatch('reload')
    },
    // ログアウト
    logout({ commit }, { next = null } = {}) {
      if (router.history.current.name !== 'login') {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        commit('clear')

        const query = {}
        if (next) query.next = next
        router.push({ name: 'login', query })
      }
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

      try {
        const { data } = await rawApi.post('/auth/jwt/refresh/', { refresh })
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', refresh)
        return data.access
      } catch (error) {
        return Promise.reject(error)
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
    setDirtyWithDiffState({ commit, dispatch }, { book, callback }) {
      // 本のstatusが前と異なる場合、各種データの更新処理を行う
      // （処理内容はコールバック関数を引数callbackで渡すこと)
      dispatch('auth/reload', null, { root: true }) // ユーザー情報の更新

      const oldState = JSON.stringify(book.status[0])
      callback(book)
      const newState = JSON.stringify(book.status[0])

      if (oldState !== newState) {
        commit('setDirty', true) // BookListの更新
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
