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

    <GlobalFooter></GlobalFooter>
  </v-app>
</template>

<script>
import GlobalHeader from '@/components/Global/GlobalHeader.vue'
import GlobalSidebar from '@/components/Global/GlobalSidebar.vue'
import GlobalMessage from '@/components/Global/GlobalMessage.vue'
import GlobalFooter from '@/components/Global/GlobalFooter.vue'
import TheBreadcrumbs from '@/components/Global/TheBreadcrumbs.vue'

export default {
  name: 'App',
  components: {
    GlobalHeader,
    GlobalSidebar,
    GlobalMessage,
    GlobalFooter,
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
