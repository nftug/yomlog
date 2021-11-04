import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'

const LoginPage = () => import('@/pages/LoginPage.vue')
const HomePage = () => import('@/pages/HomePage.vue')
const SignUpPage = () => import('@/pages/SignUpPage.vue')
const NotFoundPage = () => import('@/pages/error/NotFoundPage.vue')

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  // ログインが必要な画面には「requiresAuth」フラグを付けておく
  // ログイン時には表示しない画面には「requiresNotAuth」フラグを付けておく
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { requiresAuth: true, title: 'ホーム' },
    },
    {
      path: '/login/',
      name: 'login',
      component: LoginPage,
      meta: { requiresNotAuth: true, title: 'ログイン' },
    },
    {
      path: '/signup/',
      name: 'signup',
      component: SignUpPage,
      meta: { requiresNotAuth: true, title: 'ユーザー登録' },
    },
    {
      path: '/activate/:uid/:token/',
      name: 'signup_activate',
      component: SignUpPage,
      meta: { title: 'ユーザー認証' },
    },
    { path: '*', component: NotFoundPage },
  ],
  // 画面遷移時のスクロール
  scrollBehavior: async (to, from, savedPosition) => {
    if (savedPosition) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(savedPosition)
        })
      })
    } else if (to.hash) {
      return { selector: to.hash }
    } else {
      return { x: 0, y: 0 }
    }
  },
})

// 画面遷移の直前に毎回実行されるナビゲーションガード
router.beforeEach((to, from, next) => {
  const isLoggedIn = store.state.auth.isLoggedIn
  const token = localStorage.getItem('access')
  console.log('to.path=', to.path)
  console.log('isLoggedIn=', isLoggedIn)

  // エラーなし→通知をクリア
  if (!store.state.message.error) {
    store.dispatch('message/clearMessages')
  }

  if (!isLoggedIn) {
    // 未ログイン時→ユーザー情報取得を試行
    console.log('User is not logged in.')
    if (token != null) {
      // 認証用トークンが残っていればユーザー情報を再取得
      console.log('Trying to reload user info.')
      store
        .dispatch('auth/reload')
        .then(() => {
          console.log('Succeeded to reload.')
          goNextOrHome(to, next)
        })
        .catch(() => {
          goLoginOrPublic(to, next)
        })
    } else {
      // 認証用トークンが残っていなければ、ログイン画面へ強制遷移 or そのまま続行
      goLoginOrPublic(to, next)
    }
  } else {
    // ログインしている場合、そのまま続行
    goNextOrHome(to, next)
  }
})

function goNextOrHome(to, next) {
  // ログイン済み かつ requiresNotAuthがtrue→ホーム画面にリダイレクト
  const isLoggedIn = store.state.auth.isLoggedIn
  if (
    isLoggedIn &&
    to.matched.some((element) => element.meta.requiresNotAuth)
  ) {
    console.log('Force to Home page.')
    next('/')
  } else {
    console.log('Go to next page.')
    next()
  }
}

function goLoginOrPublic(to, next) {
  // requiresAuthがtrueなら、ログイン画面へ遷移
  if (to.matched.some((element) => element.meta.requiresAuth)) {
    console.log('Force to Login page.')
    next({
      path: '/login/',
      query: { next: to.fullPath },
    })
  } else {
    // ログインが不要であればそのまま次へ
    console.log('Go to public page.')
    next()
  }
}

export default router
