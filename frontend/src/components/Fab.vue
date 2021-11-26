<template>
  <v-fab-transition>
    <v-btn
      color="pink"
      dark
      bottom
      right
      fab
      fixed
      class="v-btn--floating"
      @click="handleClick"
    >
      <v-icon v-text="icon"></v-icon>
    </v-btn>
  </v-fab-transition>
</template>

<script>
export default {
  props: {
    icon: {
      type: String,
      default: 'mdi-chevron-up',
    },
  },
  methods: {
    handleClick() {
      this.$emit('click')
    },
  },
}
</script>

<style scoped>
.v-btn--floating {
  bottom: 0;
  margin: 0 0 24px 48px;
}
</style>
