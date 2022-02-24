<template>
  <v-col cols="12" md="6" lg="4">
    <v-card class="elevation-0 transparent my-2">
      <v-card-text class="text-center">
        <v-icon x-large class="blue--text text--lighten-2">
          {{ icon }}
        </v-icon>
      </v-card-text>
      <v-card-title primary-title class="layout justify-center">
        <div class="headline text-center">{{ title }}</div>
      </v-card-title>
      <v-card-text class="text-center">
        <slot name="default"></slot>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script>
export default {
  props: {
    icon: { type: String, required: true },
    title: { type: String, required: true },
  },
}
</script>
