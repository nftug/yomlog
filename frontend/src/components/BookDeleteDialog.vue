<template>
  <Dialog
    ref="dialogDeleteBook"
    title="本の削除"
    message="この本を削除しますか？"
  ></Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Dialog.vue'

export default {
  components: {
    Dialog,
  },
  methods: {
    async showBookDeleteDialog(item) {
      if (!(await this.$refs.dialogDeleteBook.showDialog())) return

      api({
        url: `/book/${item.id}/`,
        method: 'delete',
      })
        .then(() => {
          this.$emit('delete-book')
          this.$store.dispatch('message/setInfoMessage', {
            message: '書籍を削除しました。',
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
