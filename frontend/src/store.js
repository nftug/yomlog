import Vue from 'vue'
import Vuex from 'vuex'
import api from '@/services/api'
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
        } else if (value !== null && typeof value === 'object') {
          state[key] = {}
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
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      commit('clear')

      // bookListのクリア
      commit('bookList/clear', null, { root: true })
      commit('bookList/clearCache', null, { root: true })

      // 検索バーのクリア
      commit('navbar/clearSearch', null, { root: true })

      // ルート履歴のクリア
      commit('parentRoutes/clear', null, { root: true })

      let to
      if (router.history.current.name !== 'login' && next)
        to = { name: 'login', query: { next } }
      else to = { name: 'home' }

      setTimeout(() => {
        router.push(to)
      }, 100)
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
        const { data } = await api.post('/auth/jwt/refresh/', { refresh })
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
    info: '',
  },
  getters: {
    error: (state) => state.error,
    info: (state) => state.info,
  },
  mutations: {
    set(state, payload) {
      if (payload.error) state.error = payload.error
      if (payload.info) state.info = payload.info
    },
    clear(state) {
      state.error = ''
      state.info = ''
    },
  },
  actions: {
    // エラーメッセージ表示
    setErrorMessage(context, payload) {
      setTimeout(() => {
        context.commit('clear')
        context.commit('set', { error: payload.message })
      }, 150)
    },
    // インフォメーションメッセージ表示
    setInfoMessage(context, payload) {
      setTimeout(() => {
        context.commit('clear')
        context.commit('set', { info: payload.message })
      }, 150)
    },
    // 全メッセージ削除
    clearMessages(context) {
      context.commit('clear')
    },
  },
}

// ナビバーモジュール
const navbarModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    drawer: null,
    search: '',
    loading: false,
  },
  mutations: {
    setDrawer(state, value) {
      state.drawer = value
    },
    toggleDrawer(state) {
      state.drawer = !state.drawer
    },
    setSearch(state, value) {
      state.search = value
    },
    clearSearch(state) {
      state.search = ''
    },
    setLoading(state, value) {
      state.loading = value
    },
  },
  actions: {
    doSearch({ state }) {
      const query = state.search ? { q: state.search } : null
      router.push({
        name: 'shelf',
        params: { state: 'all' },
        query,
      })
    },
  },
}

// 本棚モジュール
const bookListModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    items: [],
    caches: [],
    totalItems: 0,
    totalPages: 0,
    isLoading: false,
    query: {},
  },
  mutations: {
    setLoading(state, val) {
      state.isLoading = val
    },
    setPageInfo(state, { totalItems, totalPages, query }) {
      state.totalItems = totalItems
      state.totalPages = totalPages
      state.query = query
    },
    addList(state, book) {
      const listIndex = state.items.findIndex((e) => e.id === book.id)
      if (listIndex < 0) state.items.push(book)
    },
    addCache(state, book) {
      const cacheIndex = state.caches.findIndex((e) => e.id === book.id)
      if (cacheIndex < 0) state.caches.push(book)
    },
    set(state, book) {
      const listIndex = state.items.findIndex((e) => e.id === book.id)
      state.items.splice(listIndex, 1, book)
      const cacheIndex = state.caches.findIndex((e) => e.id === book.id)
      state.caches.splice(cacheIndex, 1, book)
    },
    delete(state, book) {
      const listIndex = state.items.findIndex((e) => e.id === book.id)
      state.items.splice(listIndex, 1)
      const cacheIndex = state.caches.findIndex((e) => e.id === book.id)
      state.caches.splice(cacheIndex, 1)
    },
    clear(state) {
      state.items = []
    },
    clearCache(state) {
      state.caches = []
    },
  },
  actions: {
    addBook({ commit }, book) {
      commit('addList', book)
      commit('addCache', book)
    },
    async getBookItem({ state, commit }, { id }) {
      try {
        // 本のデータをキャッシュストア or APIから取得 (参照渡し)
        let result = state.caches.find((e) => e.id === id)
        if (!result) {
          result = (await api.get(`/book/${id}/`)).data
          commit('addCache', result)
        }
        return result
      } catch (error) {
        return Promise.reject(error)
      }
    },
    async reflectBookProp({ dispatch }, { id }) {
      // 指定されたidの本をAPIから取得し、キャッシュストアに反映させる

      dispatch('auth/reload', null, { root: true }) // ユーザー情報の更新

      const book = await dispatch('getBookItem', { id })
      const oldState = JSON.stringify(book.status[0])

      // APIから更新された書籍データを取得
      const newBook = (await api.get(`/book/${id}/`)).data
      book.note = newBook.note
      book.status = newBook.status
      const newState = JSON.stringify(book.status[0])

      if (oldState !== newState) {
        // 本棚ページを表示中でない場合、バックグラウンドで現在の本棚リストを更新
        if (router.history.current.name !== 'shelf') {
          dispatch('refreshBookList')
        }
      }
    },
    async refreshBookList({ state, commit }) {
      commit('setLoading', true)
      const { data } = await api.get('/book/', { params: state.query })

      commit('setPageInfo', {
        totalItems: data.count,
        totalPages: data.totalPages,
        query: state.query,
      })

      commit('clear')
      data.results.forEach((item) => {
        commit('addList', item)
      })

      commit('setLoading', false)
    },
  },
}

// ルート履歴モジュール (パンくずリスト用)
const parentRoutesModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    route: {},
    query: {},
    params: {},
    historyBack: false,
  },
  getters: {
    route: (state) => (childName) => state.route[childName] || {},
    query: (state) => (parentName) => state.query[parentName] || {},
    params: (state) => (parentName) => state.params[parentName] || {},
  },
  mutations: {
    set(state, { child, parent }) {
      state.route[child.name] = parent
    },
    saveParentSettings(state, { parent }) {
      state.query[parent.name] = parent.query
      state.params[parent.name] = parent.params
    },
    setHistoryBack(state, value) {
      state.historyBack = value
    },
    clear(state) {
      state.route = {}
      state.query = {}
      state.params = {}
    },
  },
}

const store = new Vuex.Store({
  modules: {
    auth: authModule,
    message: messageModule,
    navbar: navbarModule,
    bookList: bookListModule,
    parentRoutes: parentRoutesModule,
  },
})

export default store
