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
    async getBookItem({ state: { items } }, { id, state = 'all' }) {
      try {
        let result, currentState

        // 本のデータをストア or APIから取得
        const ret = { ...items.find((e) => e.id === id) }
        if (Object.keys(ret).length) {
          result = ret
        } else {
          const { data } = await api.get(`/book/${id}/`)
          result = data
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
    setDirtyWithDiffState({ commit, dispatch }, { book, callback }) {
      // 本のstatusが前と異なる場合、各種データの更新処理を行う
      // （処理内容はコールバック関数を引数callbackで渡すこと)
      dispatch('auth/reload', null, { root: true }) // ユーザー情報の更新

      const oldState = JSON.stringify(book.status[0])
      callback(book)
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
