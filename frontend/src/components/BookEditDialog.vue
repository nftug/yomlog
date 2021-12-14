<template>
  <Dialog
    ref="dialogBookEdit"
    title="書籍情報の入力"
    :max-width="400"
    :form-valid="isValid"
  >
    <p>本の情報を入力してください。</p>

    <v-form ref="formBookEdit" v-model="isValid">
      <v-text-field
        v-model="book.title"
        label="タイトル"
        :rules="requiredRules"
      ></v-text-field>
      <v-text-field
        v-model="book.authors"
        label="著者"
        :rules="requiredRules"
      ></v-text-field>
      <v-text-field
        v-model="book.amazon_dp"
        label="ASIN/ISBNコード"
        :rules="dpRules"
        maxlength="13"
      ></v-text-field>
      <v-text-field
        v-model="book.total"
        label="位置Noの総数"
        type="number"
        min="0"
        :rules="totalRules"
      ></v-text-field>
    </v-form>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Dialog.vue'
import { FormRulesMixin } from '@/mixins'
import api from '@/services/api'

export default {
  mixins: [FormRulesMixin],
  components: {
    Dialog,
  },
  data: () => ({
    isValid: false,
    book: {},
    dpRules: [
      (v) =>
        !v ||
        v.length === 10 ||
        v.length === 13 ||
        '正しい桁数のコードを入力してください',
    ],
    totalRules: [(v) => v > 0 || '0より大きい数値を入力してください'],
  }),
  methods: {
    async showBookEditDialog({ book, post = true } = {}) {
      // bookに対する直接の操作は行わない
      // オブジェクト属性の書き換えは呼び出し元に担当させる

      if (this.$refs.formBookEdit) {
        this.$refs.formBookEdit.resetValidation()
      }
      this.book = { ...book }
      this.book.authors = this.book.authors.join(',')

      if (!(await this.$refs.dialogBookEdit.showDialog()))
        return Promise.reject()

      if (post) {
        // postパラメータがtrueの場合、データをpatch後にpostイベントを発行
        const { data } = await api({
          url: `/book/${book.id}/`,
          method: 'patch',
          data: this.book,
        })
        this.$emit('post', data)
      } else {
        // postパラメータがfalseの場合、変更されたbookの参照を返す
        // (メソッドの呼び出しにはawaitを使うこと)
        this.book.authors = this.book.authors.split(',')
        return Promise.resolve(this.book)
      }
    },
  },
}
</script>
