import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'

import VueMeta from 'vue-meta'
import Fragment from 'vue-fragment'

import router from './router'
import store from './store'

Vue.config.productionTip = false

Vue.use(VueMeta)
Vue.use(Fragment.Plugin)

// ブラウザバックを検知してコンポーネントで「this.$isBrowserBack」で使用できるようにする。
Vue.prototype.$browserBackFlg = false
history.replaceState(null, '', null)
addEventListener('popstate', function () {
  Vue.prototype.$isBrowserBack = true

  setTimeout(() => {
    Vue.prototype.$isBrowserBack = false
  }, 500)
})

new Vue({
  vuetify,
  router,
  store,
  render: (h) => h(App),
}).$mount('#app')
