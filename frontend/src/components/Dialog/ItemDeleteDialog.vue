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
    async showItemDeleteDialog({ item, book }) {
      if (!(await this.$refs.dialogDeleteBook.showDialog())) return false

      if (Array.isArray(item)) {
        const promises = item.map((e) => this.deleteItem(e))
        await Promise.all(promises)
        item = item[0]
      } else {
        await this.deleteItem(item)
      }

      this.$store.dispatch('message/setInfoMessage', {
        message: `${this.typeStr}を削除しました。`,
      })

      // すべての処理が終了したら書籍データを再取得
      if (book) {
        this.$store.dispatch('bookList/reflectBookProp', { data: { book } })
      }

      return true
    },
    async deleteItem(item) {
      await api({
        url: `/${this.type}/${item.id}/`,
        method: 'delete',
      })

      this.$emit('delete', { prop: this.type, data: item })
    },
  },
}
</script>
