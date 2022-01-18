import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'

const LoginPage = () => import('@/pages/LoginPage.vue')
const HomePage = () => import('@/pages/HomePage.vue')
const ShelfPage = () => import('@/pages/ShelfPage.vue')
const SignUpPage = () => import('@/pages/SignUpPage.vue')
const NotFoundPage = () => import('@/pages/error/NotFoundPage.vue')
const PasswordResetPage = () => import('@/pages/settings/PasswordResetPage.vue')
const SettingsPage = () => import('@/pages/settings/SettingsPage.vue')
const ProfileSettingsPage = () =>
  import('@/pages/settings/ProfileSettingsPage.vue')
const EmailSettingsPage = () => import('@/pages/settings/EmailSettingsPage.vue')
const PasswordChangePage = () =>
  import('@/pages/settings/PasswordChangePage.vue')
const BookDetailPage = () => import('@/pages/BookDetailPage.vue')
const StatusLog = () => import('@/components/StatusLog.vue')
const NoteList = () => import('@/components/NoteList.vue')
const CalendarPage = () => import('@/pages/CalendarPage.vue')
const SocialAuthPage = () => import('@/pages/SocialAuthPage.vue')
const NotePage = () => import('@/pages/NotePage.vue')
const AuthorsPage = () => import('@/pages/AuthorPage.vue')

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
      meta: {
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: 'ホーム',
      },
    },
    {
      path: '/shelf/:state',
      name: 'shelf',
      component: ShelfPage,
      meta: {
        title: '本棚',
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: { label: '本棚', parent: 'home' },
      },
    },
    {
      path: '/book/:state/:id',
      name: 'book_detail',
      component: BookDetailPage,
      meta: {
        title: '本の詳細',
        requiresAuth: true,
        isShowMenuButton: false,
        breadcrumb: { label: '本の詳細', parent: 'shelf' },
      },
      children: [
        {
          path: '/',
          name: 'book_detail_status',
          component: StatusLog,
          meta: { title: '本の詳細', isShowMenuButton: false, noScroll: true },
        },
        {
          path: 'note/',
          name: 'book_detail_note',
          component: NoteList,
          meta: {
            title: '本の詳細',
            isShowMenuButton: false,
            noScroll: true,
            breadcrumb: 'ノート',
          },
        },
      ],
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: CalendarPage,
      meta: {
        title: 'カレンダー',
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: { label: 'カレンダー', parent: 'home' },
      },
    },
    {
      path: '/note',
      name: 'note',
      component: NotePage,
      meta: {
        title: 'ノート',
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: { label: 'ノート', parent: 'home' },
      },
    },
    {
      path: '/author',
      name: 'author',
      component: AuthorsPage,
      meta: {
        title: '著者リスト',
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: { label: '著者リスト', parent: 'home' },
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { title: 'ログイン', requiresNotAuth: true },
    },
    {
      path: '/login/social/start/:provider',
      name: 'social_start',
      component: SocialAuthPage,
      meta: { requiresNotAuth: true },
    },
    {
      path: '/login/social/end/:provider',
      name: 'social_end',
      component: SocialAuthPage,
      meta: { requiresNotAuth: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpPage,
      meta: { title: 'ユーザー登録', requiresNotAuth: true },
    },
    {
      path: '/activate/:uid/:token',
      name: 'signup_activate',
      component: SignUpPage,
      meta: { title: 'ユーザー認証' },
    },
    {
      path: '/password/reset',
      name: 'password_reset',
      component: PasswordResetPage,
      meta: { title: 'パスワードのリセット' },
    },
    {
      path: '/password/reset/confirm/:uid/:token',
      name: 'password_reset_confirm',
      component: PasswordResetPage,
      meta: { title: 'パスワードのリセット' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsPage,
      meta: {
        title: '設定',
        requiresAuth: true,
        isShowMenuButton: true,
        breadcrumb: { label: '設定', parent: 'home' },
      },
      children: [
        {
          path: 'profile/',
          name: 'settings_profile',
          component: ProfileSettingsPage,
          meta: {
            title: 'プロフィールの設定',
            isShowMenuButton: false,
            breadcrumb: { label: 'プロフィールの設定' },
          },
        },
        {
          path: 'email/',
          name: 'settings_email',
          component: EmailSettingsPage,
          meta: {
            title: 'メールアドレスの設定',
            isShowMenuButton: false,
            breadcrumb: { label: 'メールアドレスの設定' },
          },
        },
        {
          path: 'password/',
          name: 'settings_password',
          component: PasswordChangePage,
          meta: {
            title: 'パスワードの変更',
            isShowMenuButton: false,
            breadcrumb: { label: 'パスワードの変更' },
          },
        },
      ],
    },
    { path: '*', component: NotFoundPage },
  ],
  // 画面遷移時のスクロール
  scrollBehavior: (to, from, savedPosition) => {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return { selector: to.hash }
    } else if (to.meta.noScroll) {
      const parent = from.matched[0].path
      if (parent === to.matched[0].path) {
        return {}
      } else {
        return { x: 0, y: 0 }
      }
    } else {
      return { x: 0, y: 0 }
    }
  },
})

// 画面遷移の直前に毎回実行されるナビゲーションガード
router.beforeEach(async (to, from, next) => {
  const isLoggedIn = store.state.auth.isLoggedIn

  // エラーなし→通知をクリア
  if (!store.state.message.error) {
    store.dispatch('message/clearMessages')
  }

  try {
    if (!isLoggedIn) {
      // 未ログイン時→ユーザー情報取得を試行
      const token = localStorage.getItem('access')
      if (token) {
        // 認証用トークンが残っていればユーザー情報を再取得
        try {
          await store.dispatch('auth/reload')
          goNextOrHome(to, next)
        } catch {
          goLoginOrPublic(to, next)
        }
      } else {
        // 認証用トークンが残っていなければ、ログイン画面へ強制遷移 or そのまま続行
        goLoginOrPublic(to, next)
      }
    } else {
      // ログインしている場合、そのまま続行
      goNextOrHome(to, next)
    }
  } catch (error) {
    // NavigationDuplicatedのエラーを無視する
    if (error.name !== 'NavigationDuplicated') {
      throw error
    }
  }
})

function goNextOrHome(to, next) {
  // ログイン済み かつ requiresNotAuthがtrue→ホーム画面にリダイレクト
  const isLoggedIn = store.state.auth.isLoggedIn
  const isRequiresNotAuth = to.matched.some(
    (element) => element.meta.requiresNotAuth
  )
  if (isLoggedIn && isRequiresNotAuth) {
    next('/')
  } else {
    next()
  }
}

function goLoginOrPublic(to, next) {
  // requiresAuthがtrueなら、ログイン画面へ遷移
  if (to.matched.some((element) => element.meta.requiresAuth)) {
    next({
      path: '/login/',
      query: { next: to.fullPath },
    })
  } else {
    next()
  }
}

export default router
