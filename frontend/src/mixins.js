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
    innerWidth: null,
    innerHeight: null,
  }),
  created() {
    this.onWindowResize()
    window.addEventListener('resize', this.onWindowResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
  },
  computed: {
    isLessThanSm() {
      return this.innerWidth < 600
    },
    isLessThanMd() {
      return this.innerWidth < 960
    },
    isLessThanLg() {
      return this.innerWidth < 1264
    },
  },
  methods: {
    onWindowResize() {
      this.innerWidth = window.innerWidth
      this.innerHeight = window.innerHeight
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
        if (item.status !== undefined && item.status.length) {
          return item.status[0]
        } else {
          return {
            id: null,
            state: 'to_be_read',
            position: {
              value: 0,
              percentage: 0,
              page: 0,
              created_at: new Date(),
            },
          }
        }
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
}

export const ListViewMixin = {
  methods: {
    replaceWithFinalPage(url, params) {
      const routeQuery = { ...this.$route.query }
      delete params.page

      api.get(url, { params }).then(({ data: { totalPages } }) => {
        routeQuery.page = totalPages
        this.$router.replace({
          path: this.$route.path,
          query: routeQuery,
        })
      })
    },
  },
}

export const BookDetailChildMixin = {
  props: {
    item: {
      type: Object,
      require: true,
    },
    height: {
      type: [String, Number],
      default: '400',
    },
  },
  data: () => ({
    checkbox: [],
  }),
  created() {
    this.$router.app.$off('clear-checkbox')
    this.$router.app.$on('clear-checkbox', this.initCheckbox)
    this.$router.app.$off('delete-items')
    this.$router.app.$on('delete-items', this.onClickDeleteItems)
  },
  methods: {
    initCheckbox(type) {
      this.checkbox.splice(0, this.checkbox.length)
      this.item[type].forEach(() => this.checkbox.push(false))
    },
    sendDeleteProp({ prop }) {
      // チェックボックスの解除
      this.initCheckbox(prop)
      // ツールバーの解除
      this.setToolbar(prop)
    },
    setToolbar(type) {
      let toolbar = {}
      if (this.checkbox.some((e) => e)) {
        toolbar = { type: type, mode: 'checked' }
      }
      this.$emit('set-toolbar', toolbar)
    },
    onClickDeleteItems(type) {
      const items = []
      this.checkbox.forEach((checked, index) => {
        if (checked) {
          items.push(this.item[type][index])
        }
      })
      this.$refs.itemDelete.showItemDeleteDialog({
        item: items,
        book: this.item,
      })
    },
  },
}

export default {
  filters: {
    isoToDateTime(value) {
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
    isLoggedIn() {
      return this.$store.state.auth.isLoggedIn
    },
    isShowMenuButton() {
      return this.$route.meta.isShowMenuButton
    },
    isSameDateTime() {
      return function (value_1, value_2) {
        let dt_1 = new Date(Date.parse(value_1))
        let dt_2 = new Date(Date.parse(value_2))
        dt_1.setSeconds(dt_1.getSeconds(), 0)
        dt_2.setSeconds(dt_2.getSeconds(), 0)

        return dt_1.getTime() === dt_2.getTime()
      }
    },
    appName() {
      return process.env.VUE_APP_APPNAME
    },
  },
  methods: {
    isEmptyObj(obj) {
      let ret = true
      Object.keys(obj).forEach((key) => {
        if (obj[key].length) ret = false
      })
      return ret
    },
    getUserInfo(username) {
      return api.get('/auth/users/').then((response) => {
        const index = response.data.findIndex(
          (item) => item.username === username
        )
        if (index != -1) return Promise.resolve(response.data[index])
        else return Promise.reject()
      })
    },
  },
}
