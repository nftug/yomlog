<template>
  <v-navigation-drawer app clipped v-model="drawer">
    <v-list>
      <v-list-item>
        <v-list-item-avatar color="grey">
          <img v-if="auth.avatar" :alt="auth.fullname" :src="auth.avatar" />
          <v-icon v-else dark>mdi-account-circle</v-icon>
        </v-list-item-avatar>

        <v-list-item-content>
          <v-list-item-title class="text-h6">
            {{ auth.fullname }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <v-divider></v-divider>

    <v-list nav>
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.path"
        link
      >
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-item link @click="showLogoutDialog()">
        <v-list-item-icon><v-icon>mdi-logout</v-icon></v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>ログアウト</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <Dialog
      ref="dialogLogout"
      hash="logout"
      title="ログアウト"
      message="ログアウトしますか？"
      label-ok="ログアウト"
    ></Dialog>
  </v-navigation-drawer>
</template>

<script>
import Mixin from '@/mixins'
import Dialog from '@/components/Common/Dialog.vue'
import { mapState } from 'vuex'

export default {
  mixins: [Mixin],
  components: {
    Dialog,
  },
  data: () => ({
    items: [
      {
        title: 'ホーム',
        icon: 'mdi-home',
        path: '/',
      },
      {
        title: '本棚',
        icon: 'mdi-book-open-blank-variant',
        path: '/shelf/reading',
      },
      {
        title: 'カレンダー',
        icon: 'mdi-calendar',
        path: '/calendar',
      },
      {
        title: 'ノート',
        icon: 'mdi-note',
        path: '/note',
      },
      {
        title: '設定',
        icon: 'mdi-cog',
        path: '/settings',
      },
    ],
  }),
  computed: {
    ...mapState(['auth']),
    drawer: {
      get() {
        return this.$store.state.navbar.drawer
      },
      set(val) {
        this.$store.commit('navbar/setDrawer', val)
      },
    },
    menuItems() {
      const items = [...this.items]
      const itemShelf = items.find((e) => e.title === '本棚')

      if (this.$route.name === 'shelf') {
        itemShelf.path = {
          name: 'shelf',
          params: {
            state: this.$route.params.state,
          },
          query: this.$route.query,
        }
      } else {
        itemShelf.path = '/shelf/reading'
      }

      return items
    },
  },
  methods: {
    async showLogoutDialog() {
      let ret = await this.$refs.dialogLogout.showDialog()
      if (ret) this.logout()
    },
  },
}
</script>
