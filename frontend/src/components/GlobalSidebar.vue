<template>
  <v-navigation-drawer app clipped v-model="drawer">
    <v-list>
      <v-list-item style="line-height: 1.5">
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            {{ currentUserInfo.fullname }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <v-divider></v-divider>

    <v-list nav>
      <v-list-item v-for="item in items" :key="item.title" :to="item.path" link>
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
      title="ログアウト"
      message="ログアウトしますか？"
      label-ok="ログアウト"
    ></Dialog>
  </v-navigation-drawer>
</template>

<script>
import Mixin from '@/mixins'
import Dialog from '@/components/Dialog.vue'

export default {
  mixins: [Mixin],
  components: {
    Dialog,
  },
  props: {
    value: Boolean,
  },
  data: () => ({
    items: [
      {
        title: '本棚',
        icon: 'mdi-book-open-blank-variant',
        path: '/',
      },
      { title: '本の追加', icon: 'mdi-book-plus', path: '/book/add' },
      { title: '設定', icon: 'mdi-cog', path: '/settings' },
    ],
  }),
  computed: {
    drawer: {
      get() {
        return this.value
      },
      set(val) {
        this.$emit('input', val)
      },
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
