<template>
  <Dialog
    ref="dialogDeleteBook"
    :title="`${typeStr}の削除`"
    :message="`この${typeStr}を削除しますか？`"
  ></Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'

export default {
  components: {
    Dialog,
  },
  props: {
    type: {
      type: String,
      default: 'book',
      validator(value) {
        return ['book', 'status', 'note'].indexOf(value) !== -1
      },
    },
  },
  computed: {
    typeStr() {
      if (this.type === 'book') {
        return '本'
      } else if (this.type === 'status') {
        return '記録'
      } else if (this.type === 'note') {
        return 'ノート'
      } else {
        return ''
      }
    },
  },
  methods: {
    async showItemDeleteDialog(id) {
      if (!(await this.$refs.dialogDeleteBook.showDialog())) return false

      try {
        if (Array.isArray(id)) {
          const promises = id.map((e) => this.deleteItem(e))
          return await Promise.all(promises)
        } else {
          return await this.deleteItem(id)
        }
      } finally {
        this.$store.dispatch('message/setInfoMessage', {
          message: `${this.typeStr}を削除しました。`,
        })
      }
    },
    async deleteItem(id) {
      await api({
        url: `/${this.type}/${id}/`,
        method: 'delete',
      })

      this.$emit('delete', { prop: this.type, id })
    },
  },
}
</script>
