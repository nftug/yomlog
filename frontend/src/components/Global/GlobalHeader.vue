<template>
  <v-app-bar app color="primary" dark clipped-left>
    <!-- Menu button or Back button (Mobile) -->
    <template v-if="isLoggedIn && isShowMenuButton">
      <v-app-bar-nav-icon
        class="hidden-lg-and-up"
        @click.stop="$store.commit('navbar/toggleDrawer')"
      ></v-app-bar-nav-icon>
    </template>
    <template v-else-if="$route.name !== 'home'">
      <v-app-bar-nav-icon class="hidden-lg-and-up" @click="goParentRoute">
        <v-icon>mdi-arrow-left</v-icon>
      </v-app-bar-nav-icon>
    </template>
    <template v-else>
      <v-app-bar-nav-icon class="d-none">
        <span></span>
      </v-app-bar-nav-icon>
    </template>

    <!-- Right -->
    <template v-if="isLoggedIn">
      <SearchField placeholder="本を検索">
        <v-toolbar-title style="cursor: pointer">
          <div class="hidden-lg-and-up">
            {{ $route.meta.title || appName }}
          </div>
          <router-link tag="div" class="hidden-md-and-down" to="/">
            {{ appName }}
          </router-link>
        </v-toolbar-title>
      </SearchField>
    </template>

    <!-- Right (not authorized) -->
    <template v-else>
      <v-toolbar-title style="cursor: pointer">
        <div class="hidden-lg-and-up">
          {{ $route.meta.title || appName }}
        </div>
        <router-link tag="div" class="hidden-md-and-down" to="/">
          {{ appName }}
        </router-link>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn to="/login" :icon="isLessThanLg" :text="!isLessThanLg">
        <v-icon class="hidden-lg-and-up">mdi-login</v-icon>
        <span class="hidden-md-and-down">Login</span>
      </v-btn>
      <v-btn to="/signup" :icon="isLessThanLg" :text="!isLessThanLg">
        <v-icon class="hidden-lg-and-up">mdi-account-plus</v-icon>
        <span class="hidden-md-and-down">Sign Up</span>
      </v-btn>
    </template>

    <template #extension v-if="$route.name === 'shelf'">
      <ShelfTabBar></ShelfTabBar>
    </template>

    <!-- Progress bar -->
    <v-progress-linear
      :active="$store.state.navbar.loading"
      :indeterminate="$store.state.navbar.loading"
      absolute
      top
      color="white"
      height="3"
    ></v-progress-linear>
  </v-app-bar>
</template>

<script>
import Mixin, { WindowResizeMixin } from '@/mixins'
import ShelfTabBar from '@/components/Header/ShelfTabBar.vue'
import SearchField from '@/components/Header/SearchField.vue'

export default {
  mixins: [Mixin, WindowResizeMixin],
  components: { ShelfTabBar, SearchField },
  methods: {
    goParentRoute() {
      const index = this.$breadcrumbs.length - 2
      let name

      if (index > 0) {
        name = this.$breadcrumbs[index].parent
      } else {
        if (this.$store.state.auth.isLoggedIn) name = 'home'
      }

      if (name) {
        const getQuery = this.$store.getters['parentRoutes/query']
        const getParams = this.$store.getters['parentRoutes/params']
        this.$router.push({
          name,
          query: getQuery(name),
          params: getParams(name),
        })
      } else {
        this.$router.go(-1)
      }
    },
  },
}
</script>

<style scoped>
.v-btn:focus::after {
  opacity: 0 !important;
}
</style>
