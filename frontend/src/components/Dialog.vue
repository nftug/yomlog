<template>
  <v-dialog
    v-model="dialog"
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
    noTemplate: {
      type: Boolean,
    },
    hash: {
      type: String,
    },
  },
  data: () => ({
    dialog: false,
    to: null,
  }),
  watch: {
    $route() {
      if (!this.hash) {
        this.dialog = false
      }
    },
    '$route.hash'(newHash, oldHash) {
      if (this.hash) {
        if (newHash === `#${this.hash}`) {
          this.dialog = true
        } else if (oldHash === `#${this.hash}`) {
          this.dialog = false
        }
      }
    },
    dialog(newVal) {
      const hasRouteHash = this.$route.hash == `#${this.hash}`
      if (this.hash) {
        if (newVal && !hasRouteHash) {
          this.$router.push(`#${this.hash}`)
        } else if (!newVal && hasRouteHash && !this.to) {
          this.$router.back()
        }
      }
    },
  },
  created() {
    if (this.hash && this.$route.hash === `#${this.hash}`) {
      this.dialog = true
    }
    this.to = null
  },
  methods: {
    showDialog() {
      this.dialog = true
      if (!this.ok) {
        return new Promise((resolve) => {
          this.$once('answeredDialog', (value) => {
            if (!this.ok) this.dialog = false
            resolve(value)
          })
        })
      }
    },
    hideDialog({ to = null } = {}) {
      if (to) {
        this.to = to
        this.$router.push(to)
      }
      this.dialog = false
    },
    handleAnswer(val) {
      if (this.ok) {
        if (val) {
          this.ok()
        } else {
          this.dialog = false
        }
      } else {
        if (!val) this.dialog = false
        this.$emit('answeredDialog', val)
      }
    },
  },
}
</script>
