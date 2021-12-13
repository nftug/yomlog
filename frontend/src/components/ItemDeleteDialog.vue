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
  data: () => ({
    type: '',
  }),
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
    async showItemDeleteDialog(id, type = 'book') {
      this.type = type

      if (!(await this.$refs.dialogDeleteBook.showDialog())) return false

      return api({
        url: `/${this.type}/${id}/`,
        method: 'delete',
      })
        .then(() => {
          this.$emit(`delete-${this.type}`, id)
          this.$store.dispatch('message/setInfoMessage', {
            message: `${this.typeStr}を削除しました。`,
          })
          return Promise.resolve(true)
        })
        .catch(() => {
          this.$store.dispatch('message/setErrorMessage', {
            message: 'エラーが発生しました。',
          })
          return Promise.resolve(false)
        })
    },
  },
}
</script>
