<!-- 参考: https://zukucode.com/2020/04/vue-alert-confirm.html -->
<!-- TODO: mixinにconfirmDialogを記述 -->

<template>
  <v-dialog v-model="show" :max-width="400">
    <v-card>
      <v-card-title class="text-h5" primary-title>
        {{ title }}
      </v-card-title>
      <v-card-text class="pa-4">
        <p>{{ message }}</p>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="ok">OK</v-btn>
        <v-btn @click="cancel">キャンセル</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    message: {
      type: String,
      required: true,
    },
    okAction: {
      type: Function,
      required: true,
    },
    cancelAction: {
      type: Function,
      required: true,
    },
  },
  methods: {
    ok() {
      this.okAction()
      this.close()
    },
    cancel() {
      this.cancelAction()
      this.close()
    },
  },
}
</script>
