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
            color="indigo"
            v-on="on"
            v-bind="attrs"
            @click="$refs.noteAdd.showNotePostDialog({ book: item })"
          >
            <v-icon>mdi-pen-plus</v-icon>
          </v-btn>
        </template>
        <span>ノートの追加</span>
      </v-tooltip>

      <v-tooltip left>
        <template #activator="{ on, attrs }">
          <v-btn
            fab
            dark
            small
            color="green"
            v-on="on"
            v-bind="attrs"
            @click="$refs.statusAdd.showStatusPostDialog({ book: item })"
          >
            <v-icon>mdi-bookmark-plus</v-icon>
          </v-btn>
        </template>
        <span>進捗の追加</span>
      </v-tooltip>
    </v-speed-dial>

    <StatusPostDialog ref="statusAdd" @post="onAddStatus"></StatusPostDialog>
    <NotePostDialog ref="noteAdd" @post="onAddNote"></NotePostDialog>
  </div>
</template>

<script>
import StatusPostDialog from '@/components/StatusPostDialog.vue'
import NotePostDialog from '@/components/NotePostDialog.vue'

export default {
  components: {
    StatusPostDialog,
    NotePostDialog,
  },
  props: {
    item: {
      type: Object,
      require: true,
    },
  },
  data: () => ({
    fab: false,
  }),
  methods: {
    onAddStatus(type, data) {
      this.$emit('post', 'status', data)
    },
    onAddNote(type, data) {
      this.$emit('post', 'note', data)
    },
  },
}
</script>
