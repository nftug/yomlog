<template>
  <div>
    <div class="text-center pt-4">
      <v-progress-circular
        indeterminate
        :color="color"
        :size="size"
      ></v-progress-circular>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: Boolean,
    color: {
      type: String,
      default: 'primary',
    },
    size: {
      type: [Number, String],
      default: 75,
    },
  },
  computed: {
    isLoading: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
  },
}
</script>
