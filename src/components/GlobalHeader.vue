<template>
  <v-app-bar app color="primary" dark clipped-left>
    <v-app-bar-nav-icon
      v-if="isLoggedIn"
      class="mr-2 hidden-lg-and-up"
      @click.stop="drawer = !drawer"
    ></v-app-bar-nav-icon>
    <div class="d-flex align-center">
      <v-img
        alt="Vuetify Logo"
        class="shrink mr-2"
        contain
        src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
        transition="scale-transition"
        width="40"
      />

      <v-img
        alt="Vuetify Name"
        class="shrink mt-1 hidden-sm-and-down"
        contain
        min-width="100"
        src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
        width="100"
      />
    </div>

    <v-spacer></v-spacer>

    <template v-if="isLoggedIn">
      <v-btn
        @click.stop="dialogLogout = true"
        :icon="isLessThanMd"
        :text="!isLessThanMd"
      >
        <v-icon class="hidden-md-and-up">mdi-logout</v-icon>
        <span class="hidden-sm-and-down">Logout</span>
      </v-btn>
      <LogoutDialog v-model="dialogLogout"></LogoutDialog>
    </template>

    <template v-else>
      <v-btn to="/login/" :icon="isLessThanMd" :text="!isLessThanMd">
        <v-icon class="hidden-md-and-up">mdi-login</v-icon>
        <span class="hidden-sm-and-down">Login</span>
      </v-btn>
      <v-btn to="/signup/" :icon="isLessThanMd" :text="!isLessThanMd">
        <v-icon class="hidden-md-and-up">mdi-account-plus</v-icon>
        <span class="hidden-sm-and-down">Sign Up</span>
      </v-btn>
    </template>

    <WindowResize v-model="windowSize"></WindowResize>
  </v-app-bar>
</template>

<script>
import Mixin from '@/mixins'
import LogoutDialog from '@/components/LogoutDialog.vue'
import WindowResize from '@/components/WindowResize.vue'

export default {
  mixins: [Mixin],
  components: {
    LogoutDialog,
    WindowResize,
  },
  props: {
    value: Boolean,
  },
  data: () => ({
    dialogLogout: false,
    windowSize: null,
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
    isLessThanMd: function () {
      return this.windowSize < 960
    },
  },
}
</script>

<style scoped>
.v-btn:focus::after {
  opacity: 0 !important;
}
</style>
