<template>
  <div>
    <v-speed-dial
      v-model="fab"
      bottom
      right
      fixed
      direction="top"
      transition="slide-y-reverse-transition"
    >
      <template #activator>
        <v-btn v-model="fab" color="blue darken-2" dark fab>
          <v-icon v-if="fab">mdi-close</v-icon>
          <v-icon v-else>mdi-plus</v-icon>
        </v-btn>
      </template>

      <v-tooltip left>
        <template #activator="{ on, attrs }">
          <v-btn
            fab
            dark
            small
            color="green"
            v-on="on"
            v-bind="attrs"
            @click="$emit('dialog', 'add-status', { book: item })"
          >
            <v-icon>mdi-bookmark-plus</v-icon>
          </v-btn>
        </template>
        <span>進捗の追加</span>
      </v-tooltip>

      <v-tooltip left>
        <template #activator="{ on, attrs }">
          <v-btn
            fab
            dark
            small
            color="indigo"
            v-on="on"
            v-bind="attrs"
            @click="$emit('dialog', 'add-note', { book: item })"
          >
            <v-icon>mdi-pen-plus</v-icon>
          </v-btn>
        </template>
        <span>ノートの追加</span>
      </v-tooltip>
    </v-speed-dial>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      require: true,
    },
  },
  data: () => ({
    fab: false,
  }),
}
</script>
