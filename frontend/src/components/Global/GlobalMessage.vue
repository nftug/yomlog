<template>
  <div id="global-message">
    <v-snackbar v-model="showInfo">
      {{ message.info }}
      <template #action="{ attrs }">
        <v-btn color="primary" text v-bind="attrs" @click="showInfo = ''">
          OK
        </v-btn>
      </template>
    </v-snackbar>

    <div class="col-12 col-md-8 alert-bar">
      <v-alert
        v-model="showError"
        dismissible
        elevation="2"
        type="error"
        class="mb-0"
        transition="scale-transition"
      >
        {{ message.error }}
      </v-alert>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    message() {
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

<style scoped>
.alert-bar {
  position: absolute;
  margin-top: 0rem;
  top: -0.5rem;
  left: 0px;
  right: 0px;
  margin: auto;
  z-index: 20;
}
</style>
