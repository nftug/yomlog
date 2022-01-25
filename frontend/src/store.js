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
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      commit('clear')

      if (router.history.current.name !== 'login') {
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

// ナビバーモジュール
const navbarModule = {
  strict: process.env.NODE_ENV !== 'production',
  namespaced: true,
  state: {
    drawer: null,
    search: '',
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
    add(state, book) {
      state.items.push(book)
      state.caches.push(book)
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
  },
  actions: {
    async getBookItem({ state: { caches } }, { id, state = 'all' }) {
      try {
        let result, currentState

        // 本のデータをキャッシュストア or APIから取得 (参照渡し)
        const ret = caches.find((e) => e.id === id)

        if (ret) {
          result = ret
        } else {
          const { data } = await api.get(`/book/${id}/`)
          result = data
          caches.push(data)
        }

        // データから現在のstateを取得し、与えられた引数stateと照合する
        currentState = result.status.length
          ? result.status[0].state
          : 'to_be_read'

        if (state !== 'all' && state !== currentState) {
          // ステータスが一致しなければエラーを返す
          throw new Error('State of the book is not corresponded')
        }

        return result
      } catch (error) {
        return Promise.reject(error)
      }
    },
    async reflectBookProp({ commit, dispatch }, { book: { id } }) {
      // dataからbookのidを受け取り、APIから現在の書籍データに更新
      // TODO: 書籍データのidを直接渡すように変更する

      const book = await dispatch('getBookItem', { id })

      // 本のstatusが前と異なる場合、各種データの更新処理を行う
      // （処理内容はコールバック関数を引数callbackで渡すこと)
      dispatch('auth/reload', null, { root: true }) // ユーザー情報の更新

      const oldState = JSON.stringify(book.status[0])

      // NOTE: apiの更新への対応
      const newBook = (await api.get(`/book/${book.id}/`)).data
      book.note = newBook.note
      book.status = newBook.status

      const newState = JSON.stringify(book.status[0])

      if (oldState !== newState) {
        commit('setDirty', true) // BookListの更新
        // 書籍詳細の画面を表示していて、ルーターのstateがallではない場合:
        // ルーターのstateを新しいstateに書き換える
        const currentRoute = router.history.current
        const isMatchedBookDetailPage = currentRoute.matched.some(
          (r) => r.name === 'book_detail'
        )
        const isNotStateAll = currentRoute.params.state !== 'all'
        if (isMatchedBookDetailPage && isNotStateAll) {
          router.replace({ params: { state: JSON.parse(newState).state } })
        }
        return true
      } else {
        return false
      }
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
