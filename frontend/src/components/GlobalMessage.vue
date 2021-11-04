<template>
  <v-container>
    <v-snackbar v-model="showInfo">
      {{ message.info }}
      <template #action="{ attrs }">
        <v-btn color="primary" text v-bind="attrs" @click="showInfo = ''">
          OK
        </v-btn>
      </template>
    </v-snackbar>
    <v-alert
      v-model="showError"
      border="left"
      color="red"
      dark
      dismissible
      class="mb-0"
    >
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
