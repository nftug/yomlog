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

    <!-- Title -->
    <template v-if="!isShowSearch || !isLessThanSm">
      <v-toolbar-title style="cursor: pointer">
        <div class="hidden-lg-and-up">
          {{ $route.meta.title }}
        </div>
        <router-link tag="div" class="hidden-md-and-down" to="/">
          {{ appName }}
        </router-link>
      </v-toolbar-title>
    </template>

    <!-- Right -->
    <template v-if="isLoggedIn">
      <v-row justify-content="end">
        <v-spacer></v-spacer>
        <v-col cols="12" sm="7" md="5" lg="4" xl="3">
          <v-text-field
            ref="search"
            name="search"
            v-model="searchValue"
            clearable
            flat
            placeholder="検索"
            type="search"
            prepend-inner-icon="mdi-magnify"
            solo-inverted
            single-line
            hide-details
            v-show="isShowSearch || !isLessThanSm"
            @blur="isShowSearch = false"
            @keydown.enter="handleSearch"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-btn icon v-if="!isShowSearch && isLessThanSm" @click="showSearchBar">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
    </template>

    <!-- Right (not authed) -->
    <template v-else-if="$route.name === 'login' || $route.name === 'signup'">
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

export default {
  mixins: [Mixin, WindowResizeMixin],
  components: {
    ShelfTabBar,
  },
  data: () => ({
    isShowSearch: false,
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
    showSearchBar() {
      this.isShowSearch = true
      this.$nextTick(() => {
        this.$refs.search.focus()
      })
    },
    handleSearch() {
      this.$router.app.$emit('search', this.searchValue)
      this.isShowSearch = false
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
