<template>
  <!--
    TODO: 書籍のバリデーションエラーに対応させる
  -->

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
        :error-messages="errors.title"
        @input="errors.title = []"
      ></v-text-field>
      <v-combobox
        v-model="book.authors"
        :items="authorItems"
        chips
        small-chips
        label="著者"
        multiple
        :rules="authorsRules"
        :error-messages="errors.authors"
        @input="errors.authors = []"
      ></v-combobox>
      <v-text-field
        v-model="book.amazon_dp"
        label="ASIN/ISBNコード"
        :rules="dpRules"
        :error-messages="errors.amazon_dp"
        maxlength="13"
        @input="errors.amazon_dp = []"
      ></v-text-field>
      <v-text-field
        v-model="book.total"
        :label="book.format_type === 1 ? '位置Noの総数' : 'ページ数'"
        type="number"
        min="0"
        :rules="totalRules"
        :error-messages="errors.total"
        @input="errors.total = []"
      ></v-text-field>
      <v-text-field
        v-if="book.format_type === 1"
        v-model="book.total_page"
        label="ページ数"
        type="number"
        min="0"
        :rules="totalRules"
        :error-messages="errors.total_page"
        @input="errors.total_page = []"
      ></v-text-field>
    </v-form>

    <template #actions>
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="$emit('post', null)">
        キャンセル
      </v-btn>
      <v-btn color="green darken-1" text @click="postBook" :disabled="!isValid">
        {{ book.id ? '編集' : '追加' }}
      </v-btn>
    </template>
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
    errors: {
      title: [],
      authors: [],
      amazon_dp: [],
      total: [],
      total_page: [],
    },
  }),
  methods: {
    showBookEditDialog({ book } = {}) {
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
      this.$refs.dialogBookEdit.dialog = true

      return new Promise((resolve) => {
        this.$once('post', async (value) => {
          if (value) {
            resolve(value)
          } else {
            this.$refs.dialogBookEdit.dialog = false
            resolve(null)
          }
        })
      })
    },
    async postBook() {
      // total_pageのデフォルト値を設定
      if (!this.book.total_page) this.book.total_page = 0

      // Bookのデータを登録 or 編集
      // 既に登録されている場合は該当のデータが返却される (statusは200)
      try {
        var { data, status } = await api({
          url: this.book.id ? `/book/${this.book.id}/` : '/book/',
          method: this.book.id ? 'patch' : 'post',
          data: this.book,
        })
      } catch (error) {
        const errorData = error.response.data
        Object.keys(errorData).forEach((key) => {
          this.$set(this.errors, key, errorData[key])
        })
        return Promise.reject(error)
      }

      this.$refs.dialogBookEdit.dialog = false

      let message
      if (status === 201) {
        message = '書籍を登録しました。'
      } else if (this.book.id) {
        message = '書籍情報を編集しました。'
      } else {
        message = 'この書籍は既に登録されています。'
      }

      this.book = data
      this.$store.dispatch('message/setInfoMessage', { message })

      this.$emit('post', this.book)
      return Promise.resolve(this.book)
    },
  },
}
</script>
