<template>
  <v-app-bar app color="primary" dark clipped-left>
    <!-- Menu button or Back button (Mobile) -->
    <template v-if="isLoggedIn && isShowMenuButton">
      <v-app-bar-nav-icon
        class="hidden-lg-and-up"
        @click.stop="$store.commit('drawer/toggle')"
      ></v-app-bar-nav-icon>
    </template>
    <template v-else-if="$route.name != 'login'">
      <v-app-bar-nav-icon class="hidden-lg-and-up" @click="$router.go(-1)">
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
      <SearchField v-model="searchValue" @search="handleSearch">
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

    <!-- Right (not authed) -->
    <template v-else>
      <v-toolbar-title style="cursor: pointer">
        <div class="hidden-lg-and-up">
          {{ $route.meta.title }}
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
  </v-app-bar>
</template>

<script>
import Mixin, { WindowResizeMixin } from '@/mixins'
import ShelfTabBar from '@/components/ShelfTabBar.vue'
import SearchField from '@/components/SearchField.vue'

export default {
  mixins: [Mixin, WindowResizeMixin],
  components: {
    ShelfTabBar,
    SearchField,
  },
  data: () => ({
    searchValue: '',
  }),
  created() {
    // TODO: 値が正常に反映されない？→ストアを利用してみる
    this.$router.app.$on('changeSearchValue', this.onChangeSearchValue)
  },
  beforeDestroy() {
    this.$router.app.$off('changeSearchValue', this.onChangeSearchValue)
  },
  methods: {
    handleSearch() {
      this.$router.push({
        path: '/shelf/all/',
        query: this.searchValue
          ? {
              q: this.searchValue,
            }
          : null,
      })
    },
    onChangeSearchValue(searchValue) {
      this.searchValue = searchValue
    },
  },
}
</script>

<style scoped>
.v-btn:focus::after {
  opacity: 0 !important;
}
</style>
