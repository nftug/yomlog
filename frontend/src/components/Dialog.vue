<template>
  <v-dialog
    v-model="isShowDialog"
    :max-width="maxWidth"
    :fullscreen="fullscreen"
    :hide-overlay="hideOverlay"
    :transition="transition"
    :scrollable="scrollable"
  >
    <template #activator="{ on, attrs }">
      <slot name="activator" :on="on" :attrs="attrs"></slot>
    </template>

    <v-card tile>
      <!-- フルスクリーンダイアログ -->
      <template v-if="fullscreen">
        <slot
          name="toolbar"
          :title="title"
          :ok="handleAnswer.bind(null, true)"
          :cancel="handleAnswer.bind(null, false)"
        >
          <v-toolbar flat dark color="primary">
            <v-btn icon dark @click="handleAnswer(false)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>{{ title }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-toolbar-items>
              <v-btn
                dark
                icon
                @click="handleAnswer(true)"
                :disabled="!formValid"
              >
                <v-icon>mdi-content-save</v-icon>
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
    height: {
      type: [String, Number],
    },
    scrollable: {
      type: Boolean,
    },
  },
  data: () => ({
    isShowDialog: false,
  }),
  watch: {
    $route() {
      this.isShowDialog = false
    },
  },
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
        if (!val) this.isShowDialog = false
        this.$emit('answeredDialog', val)
      }
    },
  },
}
</script>
