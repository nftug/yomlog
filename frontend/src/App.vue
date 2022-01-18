<template>
  <v-app>
    <header>
      <GlobalHeader></GlobalHeader>
    </header>

    <aside>
      <GlobalSidebar v-if="$store.state.auth.isLoggedIn"></GlobalSidebar>
    </aside>

    <v-main>
      <TheBreadcrumbs></TheBreadcrumbs>
      <GlobalMessage></GlobalMessage>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import GlobalHeader from '@/components/GlobalHeader.vue'
import GlobalSidebar from '@/components/GlobalSidebar.vue'
import GlobalMessage from '@/components/GlobalMessage.vue'
import TheBreadcrumbs from '@/components/TheBreadcrumbs.vue'

export default {
  name: 'App',
  components: {
    GlobalHeader,
    GlobalSidebar,
    GlobalMessage,
    TheBreadcrumbs,
  },
  metaInfo() {
    return {
      title: this.$route.meta.title
        ? `${this.$route.meta.title} - ${process.env.VUE_APP_APPNAME}`
        : process.env.VUE_APP_APPNAME,
    }
  },
}
</script>
