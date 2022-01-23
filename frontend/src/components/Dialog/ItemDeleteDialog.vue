<template>
  <Dialog
    ref="dialogDeleteBook"
    :title="`${typeStr}の削除`"
    :message="`この${typeStr}を削除しますか？`"
    :hash="`delete-${this.type}`"
  ></Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Common/Dialog.vue'

export default {
  components: {
    Dialog,
  },
  props: {
    type: {
      type: String,
      require: true,
      validator(value) {
        return ['book', 'status', 'note'].indexOf(value) !== -1
      },
    },
    hash: { type: String },
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
