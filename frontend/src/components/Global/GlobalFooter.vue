<template>
  <v-footer absolute padless app>
    <v-card flat tile width="100%" class="primary text-center">
      <v-row justify="center" no-gutters>
        <v-btn
          v-for="link in links"
          :key="link.label"
          :to="link.to"
          color="white"
          text
          small
          rounded
          class="my-2"
        >
          {{ link.label }}
        </v-btn>
      </v-row>

      <v-col class="py-2 text-center white--text text-caption" cols="12">
        2022 —
        <strong>{{ appName }}</strong>
      </v-col>
    </v-card>
  </v-footer>
</template>

<script>
import Mixins from '@/mixins'

export default {
  mixins: [Mixins],
  data: () => ({
    links: [
      {
        label: 'ホーム',
        to: '/',
      },
      {
        label: 'YomLogについて',
        to: '/about',
      },
      {
        label: 'お問い合わせ',
        to: '/inquiry',
      },
    ],
  }),
}
</script>
