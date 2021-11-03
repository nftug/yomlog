<template>
  <div id="logout-dialog">
    <v-dialog v-model="dialog" max-width="350">
      <v-card>
        <v-card-title class="text-h5">ログアウト</v-card-title>

        <v-card-text>ログアウトしますか？</v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="dialog = false">
            キャンセル
          </v-btn>
          <v-btn color="green darken-1" text @click="onClickLogout()">
            ログアウト
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Mixin from '@/mixins'

export default {
  mixins: [Mixin],
  props: {
    value: Boolean,
  },
  computed: {
    dialog: {
      get() {
        return this.value
      },
      set(val) {
        this.$emit('input', val)
      },
    },
  },
  methods: {
    onClickLogout() {
      this.dialog = false
      this.logout()
    },
  },
}
</script>
