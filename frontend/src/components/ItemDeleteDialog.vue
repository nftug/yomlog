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
  props: {
    type: {
      type: String,
      default: 'book',
    },
  },
  components: {
    Dialog,
  },
  computed: {
    typeStr() {
      if (this.type === 'book') {
        return '本'
      } else if (this.type === 'status_log') {
        return '記録'
      } else if (this.type === 'note') {
        return 'ノート'
      } else {
        return ''
      }
    },
  },
  methods: {
    async showItemDeleteDialog(item) {
      if (!(await this.$refs.dialogDeleteBook.showDialog())) return

      api({
        url: `/${this.type}/${item.id}/`,
        method: 'delete',
      })
        .then(() => {
          this.$emit(`delete-${this.type}`, { id: item.id })
          this.$store.dispatch('message/setInfoMessage', {
            message: `${this.typeStr}を削除しました。`,
          })
        })
        .catch(() => {
          this.$store.dispatch('message/setErrorMessage', {
            message: 'エラーが発生しました。',
          })
        })
    },
  },
}
</script>
