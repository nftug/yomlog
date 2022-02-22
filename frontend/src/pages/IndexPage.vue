<template>
  <HomePage v-if="auth.isLoggedIn"></HomePage>
  <LandingPage v-else></LandingPage>
</template>

<script>
import HomePage from '@/pages/HomePage.vue'
import LandingPage from '@/pages/LandingPage.vue'
import { mapState } from 'vuex'

export default {
  components: { HomePage, LandingPage },
  computed: {
    ...mapState(['auth']),
  },
}
</script>
