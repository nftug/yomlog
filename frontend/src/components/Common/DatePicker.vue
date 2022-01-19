<template>
  <v-menu
    v-model="menu"
    transition="scale-transition"
    offset-y
    min-width="auto"
  >
    <template v-slot:activator="{ on }">
      <v-text-field
        slot="activator"
        v-model="date"
        :label="label"
        readonly
        v-on="on"
        prepend-icon="mdi-calendar"
        append-icon="mdi-restore"
        @click:append="date = defaultValue"
      />
    </template>
    <v-date-picker
      v-model="date"
      locale="ja-jp"
      :day-format="(date) => new Date(date).getDate()"
      v-bind="$attrs"
    />
  </v-menu>
</template>

<script>
import moment from 'moment'

export default {
  props: {
    value: {
      type: String,
      default: moment().format('yyyy-MM-DD'),
    },
    defaultValue: {
      type: String,
      default: moment().format('yyyy-MM-DD'),
    },
    label: {
      type: String,
      default: '日付',
    },
  },
  data: () => ({
    menu: false,
  }),
  computed: {
    date: {
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
