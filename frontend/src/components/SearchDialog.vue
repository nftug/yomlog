<template>
  <Dialog
    ref="dialogSearch"
    :title="title"
    :max-width="600"
    :hash="hash"
    @mount="onMount"
  >
    <template #activator="{ attrs }">
      <slot
        name="activator"
        :on="{ click: showSearchDialog }"
        :attrs="attrs"
      ></slot>
    </template>

    <p>指定した条件でAND/OR検索を行います。</p>

    <v-select
      v-if="type === 'book'"
      label="モード"
      :items="modes"
      v-model="mode"
      :dense="isLessThanSm"
    ></v-select>

    <div v-for="(field, index) in formSearch" :key="index">
      <v-row :no-gutters="isLessThanSm">
        <v-col sm="9" cols="12">
          <v-text-field
            v-model="field.value"
            @keypress.enter="doSearch"
            :label="field.label"
            :autofocus="field.autofocus"
            :maxlength="field.maxlength"
            :dense="isLessThanSm"
          ></v-text-field>
        </v-col>
        <v-col sm="3" cols="12">
          <v-select
            :items="andOrList"
            v-model="field.or"
            :dense="isLessThanSm"
            :disabled="
              index === formSearch.length - 1 ||
              !field.value ||
              !hasNextFilledField(index)
            "
          ></v-select>
        </v-col>
      </v-row>
    </div>

    <template #actions="{ cancel }">
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="cancel">キャンセル</v-btn>
      <v-btn color="green darken-1" text @click="doSearch">検索</v-btn>
    </template>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Dialog.vue'
import { WindowResizeMixin } from '@/mixins'

export default {
  mixins: [WindowResizeMixin],
  components: {
    Dialog,
  },
  props: {
    type: {
      type: String,
      default: 'book',
      validator: function (value) {
        return ['book', 'note'].indexOf(value) !== -1
      },
    },
    bookId: {
      type: String,
    },
    title: {
      type: String,
      default: '検索条件の追加',
    },
    hash: {
      type: String,
    },
  },
  data: () => ({
    mode: null,
    modes: [
      { text: 'あとで読む', value: 'to_be_read' },
      { text: '読んでいる本', value: 'reading' },
      { text: '読んだ本', value: 'read' },
      { text: '全ての本', value: 'all' },
    ],
    andOrList: [
      { text: 'AND', value: false },
      { text: 'OR', value: true },
    ],
    formSearchBook: [
      {
        name: 'q',
        label: 'フリーワード',
        value: '',
        maxlength: null,
        autofocus: true,
        or: false,
      },
      {
        name: 'title',
        label: 'タイトル',
        value: '',
        maxlength: null,
        autofocus: false,
        or: false,
      },
      {
        name: 'authors',
        label: '著者名',
        value: '',
        maxlength: null,
        autofocus: false,
        or: false,
      },
      {
        name: 'amazon_dp',
        label: 'ISBN/ASIN',
        value: '',
        maxlength: 13,
        autofocus: false,
        or: false,
      },
    ],
    formSearchBookNote: [
      {
        name: 'q',
        label: 'フリーワード',
        value: '',
        maxlength: null,
        autofocus: true,
        or: false,
      },
      {
        name: 'content',
        label: 'ノートの内容',
        value: '',
        maxlength: null,
        autofocus: false,
        or: false,
      },
      {
        name: 'quote_text',
        label: '引用の内容',
        value: '',
        maxlength: null,
        autofocus: false,
        or: false,
      },
    ],
    formSearch: [{}],
  }),
  created() {
    if (this.type === 'book') {
      this.formSearch = this.formSearchBook
    } else if (this.type === 'note') {
      this.formSearch = this.formSearchBookNote
    } else {
      this.formSearch = [{}]
    }
  },
  methods: {
    hasNextFilledField(index) {
      const nextFields = this.formSearch.slice(index + 1)
      return nextFields.findIndex((e) => e.value) !== -1
    },
    showSearchDialog() {
      this.onMount()
      this.$refs.dialogSearch.showDialog()
    },
    onMount() {
      // フィールドのデフォルト値設定
      // 初期化: すべてのフィールドを初期値に戻す
      this.formSearch.forEach((e) => {
        e.value = ''
        e.or = false
      })

      // クエリに従ってフィールドの値を設定
      Object.keys(this.$route.query).forEach((key) => {
        const keyName = key.replace(/_or$/, '')

        const index = this.formSearch.findIndex((e) => e.name === keyName)
        if (index !== -1) {
          // NOTE: 配列をリアクティブに対応させるために、array.splice(index, 1, value)を利用すること
          this.formSearch.splice(index, 1, {
            ...this.formSearch[index],
            value: this.$route.query[key],
          })
        }
      })

      // クエリに従ってフィールドのORフラグを設定
      Object.keys(this.$route.query).forEach((key) => {
        const keyName = key.replace(/_or$/, '')

        if (keyName !== key) {
          let index = this.formSearch.findIndex((e) => e.name === keyName)
          index = this.formSearch.slice(0, index).findIndex((e) => e.value)

          if (index !== -1) {
            this.formSearch.splice(index, 1, {
              ...this.formSearch[index],
              or: true,
            })
          }
        }
      })

      this.mode = this.$route.params.mode
    },
    doSearch() {
      const query = {}
      let or = false
      for (const field of this.formSearch) {
        const value = field.value
        if (value) {
          const name = or ? `${field.name}_or` : field.name
          query[name] = value
          // 次のフィールドのORフラグを設定
          or = field.or
        }
      }

      const to = {}
      if (this.type === 'book') {
        to.name = 'shelf'
        to.params = { mode: this.mode }
      } else if (this.type === 'note' && this.bookId) {
        to.name = 'book_detail_note'
        to.params = { id: this.$route.params.id }
      }

      if (this.hash) {
        this.$router.replace({ ...to, query })
      } else {
        this.$router.push({ ...to, query })
      }
    },
  },
}
</script>
