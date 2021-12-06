<template>
  <Dialog
    ref="dialogShelfSearch"
    title="検索条件の追加"
    :max-width="600"
    label-ok="検索"
  >
    <p>指定した条件でAND/OR検索を行います。</p>
    <v-select
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
            :label="field.label"
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
    formSearch: [
      {
        name: 'q',
        label: 'フリーワード',
        value: '',
        maxlength: null,
        or: false,
      },
      {
        name: 'title',
        label: 'タイトル',
        value: '',
        maxlength: null,
        or: false,
      },
      {
        name: 'authors',
        label: '著者名',
        value: '',
        maxlength: null,
        or: false,
      },
      {
        name: 'amazon_dp',
        label: 'ISBN/ASIN',
        value: '',
        maxlength: 13,
        or: false,
      },
    ],
  }),
  methods: {
    hasNextFilledField(index) {
      const nextFields = this.formSearch.slice(index + 1)
      return nextFields.findIndex((e) => e.value) !== -1
    },
    async showShelfSearch() {
      // フィールドのデフォルト値設定
      // 初期化: すべてのフィールドを初期値に戻す
      this.formSearch.forEach((e) => {
        e.value = ''
      })

      // クエリに従ってフィールドの値を設定
      Object.keys(this.$route.query).forEach((key) => {
        const keyName = key.replace(/_or$/, '')

        const index = this.formSearch.findIndex((e) => e.name === keyName)
        if (index !== -1) {
          // NOTE: 配列をリアクティブに対応させるために、array.splice(index, 1, value)を利用すること
          const field = { ...this.formSearch[index] }
          this.formSearch.splice(index, 1, {
            ...field,
            value: this.$route.query[key],
          })
        }
      })

      // ORフラグの設定
      // 初期化: すべてのORフラグをANDに戻す
      this.formSearch.forEach((e) => {
        e.or = false
      })

      // クエリに従ってフィールドのORフラグを設定
      Object.keys(this.$route.query).forEach((key) => {
        const keyName = key.replace(/_or$/, '')

        if (keyName !== key) {
          let index = this.formSearch.findIndex((e) => e.name === keyName)
          index = this.formSearch.slice(0, index).findIndex((e) => e.value)

          if (index !== -1) {
            const field = { ...this.formSearch[index] }
            this.formSearch.splice(index, 1, {
              ...field,
              or: true,
            })
          }
        }
      })

      this.mode = this.$route.params.mode

      if (!(await this.$refs.dialogShelfSearch.showDialog())) return

      this.doSearch()
    },
    doSearch() {
      this.$refs.dialogShelfSearch.hideDialog()

      let query = {}
      let or = false
      for (const key in this.formSearch) {
        const value = this.formSearch[key]['value']
        let name = this.formSearch[key]['name']
        name = or ? `${name}_or` : name

        if (value) {
          query[name] = value
          or = this.formSearch[key]['or']
        }
      }

      this.$router.push({
        path: `/shelf/${this.mode}/`,
        query: query,
      })
    },
  },
}
</script>
