<template>
  <v-container>
    <v-alert v-model="showInfo" border="left" color="indigo" dark dismissible>
      {{ message.info }}
    </v-alert>
    <v-alert v-model="showError" border="left" color="red" dark dismissible>
      {{ message.error }}
    </v-alert>
  </v-container>
</template>

<script>
export default {
  computed: {
    message: function () {
      return this.$store.state.message
    },
    showError: {
      get() {
        return this.$store.state.message.error.length > 0
      },
      set(value) {
        this.$store.dispatch('message/setErrorMessage', { message: value })
      },
    },
    showInfo: {
      get() {
        return this.$store.state.message.info.length > 0
      },
      set(value) {
        this.$store.dispatch('message/setInfoMessage', { message: value })
      },
    },
  },
}
</script>
