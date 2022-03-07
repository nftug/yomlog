<template>
  <v-footer absolute padless app>
    <v-card flat tile width="100%" class="primary text-center">
      <v-row justify="center" no-gutters>
        <div class="mt-4">
          <template v-for="link in links">
            <v-btn
              v-if="isLoggedIn || !link.requiresAuth"
              :key="link.label"
              :to="link.to"
              color="white"
              text
              small
              rounded
            >
              {{ link.label }}
            </v-btn>
          </template>
        </div>
      </v-row>

      <div class="py-4 text-center white--text text-caption">
        2022 —
        <strong>{{ appName }}</strong>
      </div>
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
        requiresAuth: true,
      },
      {
        label: '利用規約',
        to: '/terms_of_use',
      },
      {
        label: 'お問い合わせ',
        to: '/inquiry',
      },
    ],
  }),
}
</script>
