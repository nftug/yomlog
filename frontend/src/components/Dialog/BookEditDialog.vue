<template>
  <Dialog
    ref="dialogBookEdit"
    :title="`書籍の${book.id ? '編集' : '登録'}`"
    :max-width="400"
    :form-valid="isValid"
    :hash="hash"
  >
    <p>書籍の情報を入力してください。</p>

    <v-form ref="formBookEdit" v-model="isValid">
      <v-text-field
        v-model="book.title"
        label="タイトル"
        :rules="requiredRules"
      ></v-text-field>
      <v-combobox
        v-model="book.authors"
        :items="authorItems"
        chips
        small-chips
        label="著者"
        multiple
        :rules="authorsRules"
      ></v-combobox>
      <v-text-field
        v-model="book.amazon_dp"
        label="ASIN/ISBNコード"
        :rules="dpRules"
        maxlength="13"
      ></v-text-field>
      <v-text-field
        v-model="book.total"
        :label="book.format_type === 1 ? '位置Noの総数' : 'ページ数'"
        type="number"
        min="0"
        :rules="totalRules"
      ></v-text-field>
      <v-text-field
        v-if="book.format_type === 1"
        v-model="book.total_page"
        label="ページ数"
        type="number"
        min="0"
      ></v-text-field>
    </v-form>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Common/Dialog.vue'
import { FormRulesMixin } from '@/mixins'
import api from '@/services/api'

export default {
  mixins: [FormRulesMixin],
  components: {
    Dialog,
  },
  props: {
    hash: String,
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
    authorsRules: [(v) => v.length > 0 || 'この項目は入力必須です'],
    authorItems: [],
  }),
  methods: {
    async showBookEditDialog({ book } = {}) {
      // bookに対する直接の操作は行わない
      // オブジェクト属性の書き換えは呼び出し元に担当させる

      // バリデーションのリセット
      if (this.$refs.formBookEdit) {
        this.$refs.formBookEdit.resetValidation()
      }
      this.book = { ...book }

      // authorItemsを取得
      this.authorItems = [...this.book.authors]

      // ダイアログを表示
      if (!(await this.$refs.dialogBookEdit.showDialog()))
        return Promise.resolve(false)

      // total_pageのデフォルト値を設定
      if (!this.book.total_page) this.book.total_page = 0

      if (book.id) {
        // idが存在する場合、データをpatch後にpostイベントを発行
        const { data } = await api({
          url: `/book/${book.id}/`,
          method: 'patch',
          data: this.book,
        })
        this.$store.dispatch('message/setInfoMessage', {
          message: '書籍情報を編集しました。',
        })
        this.$emit('post', data)
      }

      return Promise.resolve(this.book)
    },
  },
}
</script>
