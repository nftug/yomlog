<template>
  <v-footer absolute padless app>
    <v-card flat tile width="100%" class="primary text-center">
      <v-card-text class="white--text">
        2022 —
        <strong>{{ appName }}</strong>
      </v-card-text>
    </v-card>
  </v-footer>
</template>

<script>
import Mixins from '@/mixins'

export default {
  mixins: [Mixins],
}
</script>
