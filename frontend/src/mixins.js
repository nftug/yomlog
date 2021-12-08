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
    bookProgress() {
      return function (item) {
        if (item.status) {
          return parseInt(
            ((item.status[0].position || 0) / item.total) * 100,
            10
          )
        }
      }
    },
  },
  methods: {
    fixStatus(item) {
      const length = item.status.length
      if (!length) {
        // ステータスが空の場合の処理
        item.status = [
          {
            state: 'to_be_read',
            id: null,
            position: 0,
            created_at: null,
            book: item.id,
          },
        ]
      } else if (length > 1 && item.status[0].state === 'to_be_read') {
        // 積読中で前のステータスレコードが存在する場合、現在の進捗を修正
        item.status[0].position = item.status[1].position
      }
    },
  },
}

export const ListViewMixin = {
  data: () => ({
    page: 1,
  }),
  methods: {
    removeQuery(key) {
      let query = { ...this.query }
      delete query[key]

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
