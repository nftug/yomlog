<template>
  <div class="text-center pt-4">
    <v-progress-circular
      indeterminate
      :color="color"
      :size="size"
    ></v-progress-circular>
  </div>
</template>

<script>
export default {
  props: {
    color: {
      type: String,
      default: 'primary',
    },
    size: {
      type: [Number, String],
      default: 75,
    },
  },
}
</script>
