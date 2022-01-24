import Vue from 'vue'
import Vuetify from 'vuetify'
import VueBreadcrumbs from 'vue-2-breadcrumbs'
import Fragment from 'vue-fragment'
// import store from '@/store'

Vue.use(Vuetify)
Vue.use(VueBreadcrumbs)
Vue.use(Fragment.Plugin)

const noop = () => {}
Object.defineProperty(window, 'scrollTo', { value: noop, writable: true })
