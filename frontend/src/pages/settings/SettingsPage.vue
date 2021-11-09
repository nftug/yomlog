<template>
  <!-- メインエリア (モバイル) -->
  <div v-if="!isDisplayLarge">
    <v-container v-if="$route.name === 'settings'">
      <div class="col-md-6 col-sm-10 mx-auto">
        <v-card class="mx-auto" tile>
          <v-list-item-group v-model="selectedIndex" color="primary">
            <v-list-item v-for="(page, i) in pages" :key="i" :to="page.path">
              <v-list-item-icon>
                <v-icon v-text="page.icon"></v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title v-text="page.title"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-card>
      </div>
    </v-container>

    <v-container v-else>
      <v-container>
        <router-view></router-view>
      </v-container>
    </v-container>
  </div>

  <!-- PC用 -->
  <div v-else>
    <v-container>
      <div class="col-xl-6 col-lg-7 col-md-7 mx-auto">
        <p class="text-h4 my-4">設定</p>

        <v-tabs v-model="selectedIndex" @change="onChangeTab()">
          <v-tab v-for="(page, i) in pages" :key="i">
            {{ page.titleTab }}
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="selectedIndex">
          <v-tab-item v-for="(page, i) in pages" :key="i" :transition="false">
            <v-card flat>
              <v-card-text>
                <router-view></router-view>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </div>
    </v-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedIndex: 0,
      pages: [
        {
          path: '/settings/profile',
          icon: 'mdi-account-circle',
          title: 'プロフィールの設定',
          titleTab: 'プロフィール',
        },
        {
          path: '/settings/email',
          icon: 'mdi-email',
          title: 'メールアドレスの設定',
          titleTab: 'メールアドレス',
        },
        {
          path: '/settings/password',
          icon: 'mdi-lock',
          title: 'パスワードの変更',
          titleTab: 'パスワード',
        },
      ],
      notChangeRoute: false,
      isDisplayLarge: false,
    }
  },
  watch: {
    $route: function () {
      this.changeIndex()
    },
  },
  created() {
    this.changeIndex()
    this.notChangeRoute = false

    this.handleResize()
    window.addEventListener('resize', this.handleResize)
  },
  destroyed() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    changeIndex: function () {
      if (this.$route.name === 'settings' && window.innerWidth >= 992) {
        // 画面サイズがlarge以上でpathがルートなら、プロフィールページに遷移
        this.$router.replace('/settings/profile')
      } else if (this.$route.name != 'settings') {
        // pathがルート以外なら、そのままselectedIndexを変更
        // onChangeTab()でフックされたpath変更の動作が作動する
        this.selectedIndex = this.pages.findIndex(
          (e) => e.path === this.$route.path
        )
      } else {
        // pathがルートなら、selectedIndex=0でユーザー情報を表示
        // ただしpath変更のフックは動作させない (notChangeRouteで制御)
        this.selectedIndex = 0
        this.notChangeRoute = true
      }
    },
    onChangeTab: function () {
      if (this.isDisplayLarge && !this.notChangeRoute) {
        let path = this.pages[this.selectedIndex]
        if (this.$route.path != path) this.$router.push(path)
      }
      this.notChangeRoute = false
    },
    handleResize: function () {
      this.isDisplayLarge = window.innerWidth > 1264
    },
  },
}
</script>
