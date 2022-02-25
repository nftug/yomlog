<template>
  <v-dialog v-model="dialog" v-bind="$attrs" :max-width="maxWidth">
    <template #activator="{ on, attrs }">
      <slot name="activator" :on="on" :attrs="attrs"></slot>
    </template>

    <v-card tile>
      <!-- フルスクリーンダイアログ -->
      <template v-if="noTemplate">
        <slot
          name="default"
          :title="title"
          :ok="handleAnswer.bind(null, true)"
          :cancel="handleAnswer.bind(null, false)"
        ></slot>
      </template>

      <!-- 通常のダイアログ -->
      <template v-else>
        <slot name="title" :title="title">
          <v-card-title class="text-h5" primary-title>
            {{ title }}
          </v-card-title>
        </slot>

        <v-card-text>
          <slot
            name="default"
            :message="message"
            :ok="handleAnswer.bind(null, true)"
            :cancel="handleAnswer.bind(null, false)"
          >
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
            <v-btn color="green darken-1" text @click="handleAnswer(false)">
              {{ labelCancel }}
            </v-btn>
            <v-btn
              color="green darken-1"
              text
              @click="handleAnswer(true)"
              :disabled="!formValid"
            >
              {{ labelOk }}
            </v-btn>
          </slot>
        </v-card-actions>
      </template>
    </v-card>
  </v-dialog>
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
      type: [String, Number],
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
    formValid: {
      type: Boolean,
      default: true,
    },
    noTemplate: {
      type: Boolean,
    },
    hash: {
      type: String,
    },
  },
  data: () => ({
    dialog: false,
    answer: null,
  }),
  watch: {
    '$route.hash'(newHash, oldHash) {
      // ブラウザの戻るボタンを押した時、ダイアログを閉じる
      if (this.hash) {
        if (oldHash === `#${this.hash}` && this.$isBrowserBack) {
          this.dialog = false
          if (this.answer === null) {
            this.$emit('answeredDialog', null)
          }
        }
      }
    },
    async dialog(newVal) {
      const hasRouteHash = this.$route.hash == `#${this.hash}`
      if (this.hash) {
        if (newVal && !hasRouteHash) {
          await this.$router.push({ ...this.$route, hash: `#${this.hash}` })
        } else if (!newVal && hasRouteHash) {
          // answeredDialogイベントが発行されていなければ発行 (主に領域外タップの場合)
          if (this.answer === null) {
            this.$emit('answeredDialog', null)
          }
          await this.$router.go(-1)
        }
      }

      if (newVal) this.$emit('show')

      // answerをnullに戻す
      this.$nextTick(() => {
        this.answer = null
      })
    },
  },
  mounted() {
    this.$emit('mount')
  },
  methods: {
    showDialog() {
      this.dialog = true
      return new Promise((resolve) => {
        this.$once('answeredDialog', (value) => {
          this.answer = value
          this.dialog = false
          resolve(value)
        })
      })
    },
    hideDialog(val) {
      if (val !== undefined) {
        this.answer = val
      }
      this.dialog = false
    },
    handleAnswer(val) {
      this.answer = val
      this.$emit('answeredDialog', val)
    },
  },
}
</script>
