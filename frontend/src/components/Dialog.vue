<!-- 参考: https://zukucode.com/2020/04/vue-alert-confirm.html -->
<!-- TODO: mixinにconfirmDialogを記述 -->

<template>
  <div id="dialog">
    <v-dialog v-model="isShowDialog" :max-width="maxWidth">
      <v-card>
        <slot name="title" :title="title">
          <v-card-title class="text-h5" primary-title>
            {{ title }}
          </v-card-title>
        </slot>

        <v-card-text>
          <slot name="content" :message="message">
            <p>{{ message }}</p>
          </slot>
        </v-card-text>

        <v-card-actions>
          <slot
            name="actions"
            :ok="handleAnswer.bind(null, true)"
            :cancel="handleAnswer.bind(null, false)"
          >
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click="handleAnswer(true)">
              {{ labelOk }}
            </v-btn>
            <v-btn color="green darken-1" text @click="handleAnswer(false)">
              {{ labelCancel }}
            </v-btn>
          </slot>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
    },
    message: {
      type: String,
    },
    maxWidth: {
      type: Number,
      default: 350,
    },
    labelOk: {
      type: String,
      default: 'OK',
    },
    labelCancel: {
      type: String,
      default: 'キャンセル',
    },
  },
  data: () => ({
    isShowDialog: false,
  }),
  methods: {
    showDialog() {
      this.isShowDialog = true
      return new Promise((resolve) => {
        this.$once('answeredDialog', (value) => {
          this.isShowDialog = false
          resolve(value)
        })
      })
    },
    handleAnswer(val) {
      this.$emit('answeredDialog', val)
    },
  },
}
</script>
