<template>
  <fragment>
    <template v-if="!(search && isLessThanSm)">
      <slot name="default" :search="search"></slot>
    </template>

    <v-row justify-content="end">
      <v-spacer></v-spacer>
      <v-col cols="12" sm="7" md="5" lg="4" xl="3">
        <v-text-field
          ref="search"
          name="search"
          v-model="searchValue"
          clearable
          flat
          :placeholder="placeholder"
          type="search"
          prepend-inner-icon="mdi-magnify"
          solo-inverted
          single-line
          hide-details
          v-show="search || !isLessThanSm"
          @blur="search = false"
          @keydown.enter="handleSearch"
        ></v-text-field>
      </v-col>
    </v-row>
    <v-btn icon v-if="!search && isLessThanSm" @click="showSearchBar">
      <v-icon>mdi-magnify</v-icon>
    </v-btn>
  </fragment>
</template>

<script>
import { WindowResizeMixin } from '@/mixins'

export default {
  mixins: [WindowResizeMixin],
  props: {
    placeholder: {
      type: String,
      default: '検索',
    },
  },
  data: () => ({
    search: false,
  }),
  computed: {
    searchValue: {
      get() {
        return this.$store.state.navbar.search
      },
      set(value) {
        this.$store.commit('navbar/setSearch', value)
      },
    },
  },
  methods: {
    showSearchBar() {
      this.search = true
      this.$nextTick(() => {
        this.$refs.search.focus()
      })
    },
    handleSearch($event) {
      this.search = false
      $event.target.blur()
      this.$store.dispatch('navbar/doSearch')
    },
  },
}
</script>
