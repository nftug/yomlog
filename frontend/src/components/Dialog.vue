<template>
  <div id="dialog">
    <v-dialog
      v-model="isShowDialog"
      :max-width="maxWidth"
      :fullscreen="fullscreen"
      :hide-overlay="hideOverlay"
      :transition="transition"
    >
      <v-card>
        <!-- フルスクリーンダイアログ -->
        <template v-if="fullscreen">
          <slot
            name="toolbar"
            :title="title"
            :ok="handleAnswer.bind(null, true)"
            :cancel="handleAnswer.bind(null, false)"
          >
            <v-toolbar dark color="primary">
              <v-btn icon dark @click="handleAnswer(false)">
                <v-icon>mdi-close</v-icon>
              </v-btn>
              <v-toolbar-title>{{ title }}</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-toolbar-items>
                <v-btn
                  dark
                  text
                  @click="handleAnswer(true)"
                  :disabled="!formValid"
                >
                  保存
                </v-btn>
              </v-toolbar-items>
            </v-toolbar>
          </slot>

          <slot name="default" :message="message">
            <p>{{ message }}</p>
          </slot>
        </template>

        <!-- 通常のダイアログ -->
        <template v-else>
          <slot name="title" :title="title">
            <v-card-title class="text-h5" primary-title>
              {{ title }}
            </v-card-title>
          </slot>

          <v-card-text>
            <slot name="default" :message="message">
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
    formValid: {
      type: Boolean,
      default: true,
    },
    ok: {
      type: Function,
    },
    fullscreen: {
      type: Boolean,
    },
    hideOverlay: {
      type: Boolean,
    },
    transition: {
      type: String,
    },
  },
  data: () => ({
    isShowDialog: false,
  }),
  methods: {
    showDialog() {
      this.isShowDialog = true
      if (!this.ok) {
        return new Promise((resolve) => {
          this.$once('answeredDialog', (value) => {
            if (!this.ok) this.isShowDialog = false
            resolve(value)
          })
        })
      }
    },
    hideDialog() {
      this.isShowDialog = false
    },
    handleAnswer(val) {
      if (this.ok) {
        if (val) {
          this.ok()
        } else {
          this.isShowDialog = false
        }
      } else {
        this.$emit('answeredDialog', val)
      }
    },
  },
}
</script>
