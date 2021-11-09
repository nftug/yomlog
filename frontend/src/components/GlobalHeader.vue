<template>
  <v-app-bar app color="primary" dark clipped-left>
    <!-- Menu button or Back button (Mobile) -->
    <v-app-bar-nav-icon
      v-if="isLoggedIn && isShowMenuButton"
      class="hidden-lg-and-up mr-2"
      @click.stop="drawer = !drawer"
    ></v-app-bar-nav-icon>
    <v-btn
      v-else-if="$route.name != 'login'"
      class="hidden-lg-and-up mr-2"
      @click="$router.go(-1)"
      icon
    >
      <v-icon>mdi-arrow-left</v-icon>
    </v-btn>

    <!-- Title -->
    <v-toolbar-title>
      <div class="hidden-lg-and-up">
        {{ $route.meta.title }}
      </div>
      <div class="hidden-md-and-down">Vuetify Test</div>
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <!-- Right -->
    <template v-if="isLoggedIn">
      <v-btn icon v-show="$route.name === 'home'">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <v-menu left bottom v-show="$route.name === 'home'">
        <template #activator="{ on, attrs }">
          <v-btn icon v-show="$route.name === 'home'" v-bind="attrs" v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item @click="() => {}">本の登録</v-list-item>
          <v-list-item @click="() => {}">本の削除</v-list-item>
        </v-list>
      </v-menu>
    </template>

    <template v-else>
      <v-btn to="/login" :icon="isLessThanLg" :text="!isLessThanLg">
        <v-icon class="hidden-lg-and-up">mdi-login</v-icon>
        <span class="hidden-md-and-down">Login</span>
      </v-btn>
      <v-btn to="/signup" :icon="isLessThanLg" :text="!isLessThanLg">
        <v-icon class="hidden-lg-and-up">mdi-account-plus</v-icon>
        <span class="hidden-md-and-down">Sign Up</span>
      </v-btn>
    </template>
  </v-app-bar>
</template>

<script>
import Mixin, { WindowResizeMixin } from '@/mixins'

export default {
  mixins: [Mixin, WindowResizeMixin],
  props: {
    value: Boolean,
  },
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

<style scoped>
.v-btn:focus::after {
  opacity: 0 !important;
}
</style>
