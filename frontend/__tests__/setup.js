import Vue from 'vue'
import Vuetify from 'vuetify'
import VueBreadcrumbs from 'vue-2-breadcrumbs'
import Fragment from 'vue-fragment'

Vue.use(Vuetify)
Vue.use(VueBreadcrumbs)
Vue.use(Fragment.Plugin)

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

const noop = () => {}
Object.defineProperty(window, 'scrollTo', { value: noop, writable: true })
