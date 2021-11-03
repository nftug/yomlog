<template>
  <v-app>
    <header>
      <GlobalHeader v-model="drawer"></GlobalHeader>
    </header>

    <aside>
      <GlobalSidebar
        v-if="$store.state.auth.isLoggedIn"
        v-model="drawer"
      ></GlobalSidebar>
    </aside>

    <v-main>
      <GlobalMessage></GlobalMessage>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import GlobalHeader from '@/components/GlobalHeader.vue'
import GlobalSidebar from '@/components/GlobalSidebar.vue'
import GlobalMessage from '@/components/GlobalMessage.vue'

export default {
  name: 'App',
  components: {
    GlobalHeader,
    GlobalSidebar,
    GlobalMessage,
  },
  data: () => ({
    drawer: null,
  }),
}
</script>
