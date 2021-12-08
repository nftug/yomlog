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

      let dateStr = ''
      const dt = new Date(Date.parse(value))
      const dt_now = new Date()

      let year = dt.getFullYear()
      let month = dt.getMonth() + 1
      let day = dt.getDate()
      let hour = dt.getHours()
      let minute = dt.getMinutes()

      if (year === dt_now.getFullYear()) {
        const d_value = new Date(year, month - 1, day).getTime()
        const d_today = new Date(
          dt_now.getFullYear(),
          dt_now.getMonth(),
          dt_now.getDate()
        ).getTime()
        const d_yesterday = new Date(
          dt_now.getFullYear(),
          dt_now.getMonth(),
          dt_now.getDate() - 1
        ).getTime()
        const d_twoDaysAgo = new Date(
          dt_now.getFullYear(),
          dt_now.getMonth(),
          dt_now.getDate() - 2
        ).getTime()

        if (d_value === d_today) {
          dateStr = '今日'
        } else if (d_value === d_yesterday) {
          dateStr = '昨日'
        } else if (d_value === d_twoDaysAgo) {
          dateStr = '一昨日'
        } else {
          dateStr = `${month}/${day}`
        }
      } else {
        dateStr = `${year}/${month}/${day}`
      }

      minute = ('00' + minute).slice(-2)

      return `${dateStr} ${hour}:${minute}`
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
