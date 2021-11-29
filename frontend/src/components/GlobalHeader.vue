<template>
  <v-app-bar app color="primary" dark clipped-left>
    <!-- Menu button or Back button (Mobile) -->
    <template v-if="isLoggedIn && isShowMenuButton">
      <v-app-bar-nav-icon
        class="hidden-lg-and-up"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>
    </template>
    <template v-else-if="$route.name != 'login'">
      <v-app-bar-nav-icon class="hidden-lg-and-up" @click="$router.go(-1)">
        <v-icon>mdi-arrow-left</v-icon>
      </v-app-bar-nav-icon>
    </template>

    <!-- Title -->
    <template v-if="!isShowSearch || !isLessThanLg">
      <v-toolbar-title style="cursor: pointer">
        <div class="hidden-lg-and-up">
          {{ $route.meta.title }}
        </div>
        <router-link tag="div" class="hidden-md-and-down" to="/">
          {{ appName }}
        </router-link>
      </v-toolbar-title>

      <v-spacer></v-spacer>
    </template>

    <!-- Right -->
    <template v-if="isLoggedIn">
      <!--
      <v-btn icon @click="$router.app.$emit('openSearch')">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      -->
      <v-expand-x-transition>
        <v-text-field
          ref="search"
          v-model="searchValue"
          clearable
          flat
          placeholder="検索"
          type="search"
          prepend-inner-icon="mdi-magnify"
          solo-inverted
          single-line
          hide-details
          v-show="isShowSearch"
          @blur="isShowSearch = false"
          @keydown.enter="handleSearch"
        ></v-text-field>
      </v-expand-x-transition>
      <v-btn icon v-if="!isShowSearch" @click="showSearchBar">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
    </template>

    <!-- Right (not authed) -->
    <template v-else-if="$route.name === 'login' || $route.name === 'signup'">
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
      <v-tabs v-model="selectedTab" centered>
        <v-tab v-for="(tab, index) in tabs" :key="index" :to="tab.path">
          {{ tab.label }}
        </v-tab>
      </v-tabs>
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
  data: () => ({
    isShowSearch: false,
    searchValue: '',
    selectedTab: null,
    tabs: [
      {
        label: 'あとで読む',
        path: '/shelf/to_be_read',
      },
      {
        label: '読んでいる本',
        path: '/shelf/reading',
      },
      {
        label: '読んだ本',
        path: '/shelf/read',
      },
    ],
  }),
  created() {
    // TODO: 値が正常に反映されない？→ストアを利用してみる
    this.$router.app.$on('changeSearchValue', this.onChangeSearchValue)
  },
  beforeDestroy() {
    this.$router.app.$off('changeSearchValue', this.onChangeSearchValue)
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
