<template>
  <v-menu
    ref="menu"
    v-model="menu"
    transition="scale-transition"
    :return-value.sync="time"
    offset-y
    min-width="auto"
    :close-on-content-click="false"
  >
    <template v-slot:activator="{ on }">
      <v-text-field
        slot="activator"
        v-model="time"
        :label="label"
        readonly
        v-on="on"
        prepend-icon="mdi-clock"
        append-icon="mdi-restore"
        @click:append="time = defaultValue"
      />
    </template>
    <v-time-picker v-model="time" v-bind="$attrs">
      <v-spacer></v-spacer>
      <v-btn text color="primary" @click="menu = false">キャンセル</v-btn>
      <v-btn text color="primary" @click="$refs.menu.save(time)">OK</v-btn>
    </v-time-picker>
  </v-menu>
</template>

<script>
import moment from 'moment'

export default {
  props: {
    value: {
      type: String,
      default: moment().format('HH:mm'),
    },
    defaultValue: {
      type: String,
      default: moment().format('HH:mm'),
    },
    label: {
      type: String,
      default: '時刻',
    },
  },
  data: () => ({
    menu: false,
  }),
  computed: {
    time: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
  },
}
</script>
