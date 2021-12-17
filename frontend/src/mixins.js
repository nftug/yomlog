import api from '@/services/api'

export const FormRulesMixin = {
  data: () => ({
    requiredRules: [(v) => !!v || 'この項目は入力必須です'],
    emailRules: [
      (v) => !!v || 'メールアドレスを入力してください',
      (v) => /.+@.+/.test(v) || '正しいメールアドレスを入力してください',
    ],
  }),
}

export const WindowResizeMixin = {
  data: () => ({
    windowSize: null,
  }),
  created() {
    this.onWindowResize()
    window.addEventListener('resize', this.onWindowResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
  },
  computed: {
    isLessThanSm: function () {
      return this.windowSize < 600
    },
    isLessThanMd: function () {
      return this.windowSize < 960
    },
    isLessThanLg: function () {
      return this.windowSize < 1264
    },
  },
  methods: {
    onWindowResize: function () {
      this.windowSize = window.innerWidth
    },
  },
}

export const BookListMixin = {
  computed: {
    bookList() {
      return this.$store.state.bookList
    },
    currentState() {
      return function (item) {
        if (item.status.length) {
          return item.status[0]
        } else {
          return {
            id: null,
            state: 'to_be_read',
            position: 0,
          }
        }
      }
    },
    bookProgress() {
      return function (item) {
        return parseInt(
          (this.currentState(item).position / item.total) * 100,
          10
        )
      }
    },
  },
  filters: {
    stateName(state) {
      if (state === 'to_be_read') {
        return '積読中'
      } else if (state === 'reading') {
        return '読書中'
      } else {
        return '読了'
      }
    },
    stateColor(state) {
      if (state === 'to_be_read') {
        return ''
      } else if (state === 'reading') {
        return 'primary'
      } else {
        return 'success'
      }
    },
  },
  methods: {
    setDirtyWithDiffState(book, callback) {
      const oldState = JSON.stringify(book.status[0])
      callback(book)
      const newState = JSON.stringify(book.status[0])

      if (oldState !== newState) {
        this.$store.commit('bookList/setDirty', true)
        return true
      } else {
        return false
      }
    },
  },
}

export const ListViewMixin = {
  data: () => ({
    page: 1,
  }),
  filters: {
    searchLabel(key) {
      const keyName = key.replace(/_or$/, '')
      const or = keyName !== key
      let label

      if (keyName === 'title') {
        label = '書名'
      } else if (keyName === 'authors') {
        label = '著者名'
      } else if (keyName === 'amazon_dp') {
        label = 'ISBN/ASIN'
      } else if (keyName === 'content') {
        label = '内容'
      } else if (keyName === 'quote_text') {
        label = '引用'
      } else {
        label = ''
      }

      if (or) {
        label += `${label ? ' (OR)' : 'OR'}`
      }

      return `${label}${label ? ':' : ''}`
    },
  },
  methods: {
    removeQuery(key, query = this.query) {
      if (key) {
        delete query[key]
      } else {
        query = {}
      }

      // OR検索だけになったらAND検索に置換
      const keys = Object.keys(query)
      const hasAnd = keys.some((e) => e.match(/^(?!.*_or).*$/) !== null)

      if (!hasAnd) {
        query = {}
        keys.forEach((key) => {
          const value = this.query[key]
          const keyName = key.replace(/_or$/, '')
          query[keyName] = value
        })
      }

      this.$router.push({
        path: this.$route.path,
        query: query,
      })
    },
    handlePagination() {
      let query = { ...this.$route.query }
      query.page = this.page

      this.$router.push({
        path: this.$route.path,
        query: query,
      })
    },
    replaceWithFinalPage(url, params) {
      const routeQuery = { ...this.$route.query }
      delete params.page

      api
        .get(url, {
          params: params,
        })
        .then(({ data: { totalPages } }) => {
          routeQuery.page = totalPages
          this.$router.replace({
            path: this.$route.path,
            query: routeQuery,
          })
        })
    },
  },
}

export const ShelfSearchFromHeaderMixin = {
  created() {
    this.$router.app.$on('search', this.handleSearchFromHeader)
  },
  beforeDestroy() {
    this.$router.app.$off('search', this.handleSearchFromHeader)
  },
  methods: {
    handleSearchFromHeader(searchValue) {
      this.$router.push({
        path: '/shelf/all/',
        query: searchValue
          ? {
              q: searchValue,
            }
          : null,
      })
    },
  },
}

export const BookDetailChildMixin = {
  props: {
    item: {
      type: Object,
    },
    height: {
      type: String,
      default: '400',
    },
  },
  data: () => ({
    itemHeight: 0,
    checkbox: [],
  }),
  computed: {
    benched() {
      return Math.ceil(this.height / this.itemHeight)
    },
  },
  created() {
    this.$router.app.$off('clear-checkbox')
    this.$router.app.$on('clear-checkbox', this.initCheckbox)
    this.$router.app.$off('delete-items')
    this.$router.app.$on('delete-items', this.onDeleteItems)
  },
  methods: {
    initCheckbox(type) {
      this.checkbox.splice(0, this.checkbox.length)
      this.item[type].forEach(() => this.checkbox.push(false))
    },
    sendDeleteProp(type, id) {
      const index = this.item[type].findIndex((e) => e.id === id)
      this.checkbox.splice(index, 1)
      this.setToolbar(type)

      this.$emit('delete', type, id)
    },
    sendEditProp(type, data) {
      this.$emit('edit', type, data)
    },
    setToolbar(type) {
      let toolbar = {}
      if (this.checkbox.some((e) => e)) {
        toolbar = { type: type, mode: 'checked' }
      } else if (Object.keys(this.$route.query).length) {
        toolbar = { type: type, mode: 'search' }
      }
      this.$emit('set-toolbar', toolbar)
    },
    onDeleteItems(type) {
      const ids = []
      this.checkbox.forEach((checked, index) => {
        if (checked) {
          ids.push(this.item[type][index].id)
        }
      })
      this.$refs.itemDelete.showItemDeleteDialog(ids)
    },
  },
}

export default {
  filters: {
    isoToDateTime: function (value) {
      if (!value) return

      let dateStr
      const date = new Date(Date.parse(value))
      const dateNow = new Date()

      const dt = {
        year: date.getFullYear(),
        month: date.getMonth() + 1,
        day: date.getDate(),
        hour: date.getHours(),
        minute: date.getMinutes(),
      }

      const dtNow = {
        year: dateNow.getFullYear(),
        month: dateNow.getMonth() + 1,
        day: dateNow.getDate(),
        hour: dateNow.getHours(),
        minute: dateNow.getMinutes(),
      }

      if (dtNow.year === dt.year) {
        const dayTime = new Date(dt.year, dt.month - 1, dt.day).getTime()
        const dayTimeNow = new Date(
          dtNow.year,
          dtNow.month - 1,
          dtNow.day
        ).getTime()
        const dayTimeYesterday = new Date(
          dtNow.year,
          dtNow.month - 1,
          dtNow.day - 1
        ).getTime()
        const dayTimeTwoDaysAgo = new Date(
          dtNow.year,
          dtNow.month - 1,
          dtNow.day - 2
        ).getTime()

        if (dayTime === dayTimeNow) {
          dateStr = '今日'
        } else if (dayTime === dayTimeYesterday) {
          dateStr = '昨日'
        } else if (dayTime === dayTimeTwoDaysAgo) {
          dateStr = '一昨日'
        } else {
          dateStr = `${dt.month}/${dt.day}`
        }
      } else {
        dateStr = `${dt.year}/${dt.month}/${dt.day}`
      }

      return `${dateStr} ${dt.hour}:${('00' + dt.minute).slice(-2)}`
    },
    sliceContent(content, num = 30) {
      if (content.length < num) {
        return content
      } else {
        return `${content.slice(0, num)}...`
      }
    },
  },
  computed: {
    isLoggedIn: function () {
      return this.$store.state.auth.isLoggedIn
    },
    isShowMenuButton: function () {
      return this.$route.meta.isShowMenuButton
    },
    isSameDateTime: function () {
      return function (value_1, value_2) {
        let dt_1 = new Date(Date.parse(value_1))
        let dt_2 = new Date(Date.parse(value_2))
        dt_1.setSeconds(dt_1.getSeconds(), 0)
        dt_2.setSeconds(dt_2.getSeconds(), 0)

        return dt_1.getTime() === dt_2.getTime()
      }
    },
    initialName: function () {
      return function (name) {
        let splitName = name.split(' ')
        let ret = ''
        splitName.forEach((s) => {
          ret += s.charAt(0).toUpperCase()
        })
        return ret
      }
    },
    appName: function () {
      return process.env.VUE_APP_APPNAME
    },
    currentUserInfo: function () {
      return this.$store.state.auth
    },
  },
  methods: {
    isEmptyObj: function (obj) {
      let ret = true
      Object.keys(obj).forEach((key) => {
        if (obj[key].length) ret = false
      })
      return ret
    },
    getUserInfo: function (username) {
      return api.get('/auth/users/').then((response) => {
        const index = response.data.findIndex(
          (item) => item.username === username
        )
        if (index != -1) return Promise.resolve(response.data[index])
        else return Promise.reject()
      })
    },
    logout: function () {
      // Data clear
      this.$store.dispatch('auth/logout')
      this.$router.push('/login/')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'ログアウトしました。',
      })
    },
  },
}
