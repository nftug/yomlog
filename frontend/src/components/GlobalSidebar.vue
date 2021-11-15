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

      <v-list-item link @click="dialogLogout = true">
        <v-list-item-icon><v-icon>mdi-logout</v-icon></v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>ログアウト</v-list-item-title>
        </v-list-item-content>
        <LogoutDialog v-model="dialogLogout"></LogoutDialog>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import LogoutDialog from '@/components/LogoutDialog.vue'
import Mixin from '@/mixins'

export default {
  mixins: [Mixin],
  props: {
    value: Boolean,
  },
  data: () => ({
    items: [{ title: '設定', icon: 'mdi-cog', path: '/settings' }],
    dialogLogout: false,
  }),
  components: { LogoutDialog },
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
}
</script>
