import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'

import VueMeta from 'vue-meta'
import Fragment from 'vue-fragment'
import VueBreadcrumbs from 'vue-2-breadcrumbs'

import router from './router'
import store from './store'

Vue.config.productionTip = false

Vue.use(VueMeta)
Vue.use(VueBreadcrumbs)
Vue.use(Fragment.Plugin)

// ブラウザバックを検知してコンポーネントで「this.$isBrowserBack」で使用できるようにする。
Vue.prototype.$browserBackFlg = false
history.replaceState(null, '', null)
addEventListener('popstate', function () {
  Vue.prototype.$isBrowserBack = true
  store.commit('parentRoutes/setHistoryBack', true)

  setTimeout(() => {
    Vue.prototype.$isBrowserBack = false
    store.commit('parentRoutes/setHistoryBack', false)
  }, 500)
})

new Vue({
  vuetify,
  router,
  store,
  render: (h) => h(App),
}).$mount('#app')
