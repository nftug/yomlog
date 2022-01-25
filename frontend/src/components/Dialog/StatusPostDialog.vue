<template>
  <Dialog
    ref="dialogStatusAdd"
    title="進捗状況の入力"
    :max-width="350"
    :hash="hash"
  >
    <v-form ref="formStatusAdd" v-model="isValid" @submit.prevent>
      <v-text-field
        v-model="position"
        :label="format_type === 1 ? '位置No' : 'ページ数'"
        type="number"
        min="0"
        autofocus
        :max="total"
        :suffix="` / ${total}`"
        :rules="to_be_read ? [] : positionRules"
        :disabled="to_be_read"
        :error-messages="positionErrors"
        @input="positionErrors = []"
        @keydown.enter="handleKeydownEnter"
      ></v-text-field>
      <v-switch
        v-model="to_be_read"
        label="あとで読む"
        :disabled="!!statusId"
        :rules="toBeReadRules"
      ></v-switch>
      <DatePicker
        v-model="date"
        :defaultValue="defaultValues.date"
        label="日付"
        @input="resetTime"
      ></DatePicker>
      <TimePicker
        v-model="time"
        :defaultValue="defaultValues.time"
        label="時刻"
        format="ampm"
        scrollable
        ampm-in-title
      ></TimePicker>
    </v-form>

    <template #actions="{ cancel }">
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="cancel">キャンセル</v-btn>
      <v-btn
        color="green darken-1"
        text
        @click="postStatus"
        :disabled="!isValid"
      >
        {{ statusId ? '編集' : '追加' }}
      </v-btn>
    </template>
  </Dialog>
</template>

<script>
import api from '@/services/api'
import Dialog from '@/components/Common/Dialog.vue'
import DatePicker from '@/components/Common/DatePicker.vue'
import TimePicker from '@/components/Common/TimePicker.vue'
import moment from 'moment'
import { BookListMixin } from '@/mixins'

export default {
  props: {
    hash: String,
  },
  components: {
    Dialog,
    DatePicker,
    TimePicker,
  },
  mixins: [BookListMixin],
  data() {
    return {
      statusId: '',
      book: {},
      bookId: '',
      position: 0,
      total: 0,
      format_type: 0,
      to_be_read: false,
      date: null,
      time: null,
      positionRules: [
        (v) => v > 0 || '0より大きい数値を入力してください',
        (v) =>
          v <= this.total ||
          (this.format_type === 1 ? '位置No' : 'ページ数') + 'が不正です',
      ],
      toBeReadRules: [
        (v) =>
          !(v && this.defaultValues.to_be_read) ||
          '以前と異なるステータスを入力してください',
      ],
      positionErrors: [],
      isValid: false,
      defaultValues: {
        position: 0,
        to_be_read: false,
        date: null,
        time: null,
      },
    }
  },
  methods: {
    showStatusPostDialog({ book, status = {} }) {
      this.initFields({ book, id: status.id })

      // ダイアログを表示
      this.$refs.dialogStatusAdd.showDialog()
    },
    initFields({ book, id }) {
      // TODO: propsでbookとidを指定できるようにする + onMountメソッドのバインディング

      // バリデーションをリセット
      if (this.$refs.formStatusAdd) {
        this.$refs.formStatusAdd.resetValidation()
        this.positionErrors = []
      }

      // 各種データを入力
      this.book = book
      this.bookId = book.id
      this.format_type = book.format_type
      this.total = book.total

      if (id) {
        const status = book.status.find((e) => e.id === id)
        this.statusId = id
        this.position = status.position.value
        this.to_be_read = status.state === 'to_be_read'
        this.date = moment(status.created_at).format('yyyy-MM-DD')
        this.time = moment(status.created_at).format('HH:mm')
      } else {
        this.statusId = ''
        this.position = 0
        this.to_be_read = this.currentState(book).state === 'to_be_read'
        this.date = moment().format('yyyy-MM-DD')
        this.time = moment().format('HH:mm')
      }

      // デフォルト値を保存
      this.defaultValues.position = this.position
      this.defaultValues.to_be_read = this.to_be_read
      this.defaultValues.date = this.date
      this.defaultValues.time = this.time
    },
    async postStatus() {
      const params = {
        position: this.to_be_read ? 0 : this.position,
      }
      let method, url
      this.$refs.dialogStatusAdd.hideDialog(true)

      // 現在の日時 (秒単位は切り捨て) と入力値が異なる場合、params.created_atを設定する
      const now = moment().startOf('minute').format()
      const created_at = moment(`${this.date} ${this.time}`).format()
      if (now !== created_at) {
        params.created_at = created_at
      }

      // 編集 or 新規でAjaxのパラメータを変更
      if (this.statusId) {
        method = 'patch'
        url = `/status/${this.statusId}/`
      } else {
        params.book = this.bookId
        method = 'post'
        url = '/status/'
      }

      try {
        const { data } = await api({ url, method, data: params })

        this.$refs.dialogStatusAdd.hideDialog()

        this.$emit('post', { prop: 'status', data })
        this.$store.dispatch('bookList/reflectBookProp', { book: this.book })

        this.$store.dispatch('message/setInfoMessage', {
          message: '進捗状況を記録しました。',
        })
      } catch (error) {
        if (error.data) {
          const { data } = error
          if (data.position) {
            this.positionErrors = data.position
          } else {
            this.$store.dispatch('message/setErrorMessage', {
              message: 'エラーが発生しました',
            })
          }
        }
        return Promise.reject(error)
      }
    },
    handleKeydownEnter() {
      if (!this.$refs.formStatusAdd.validate()) return
      this.postStatus()
    },
    resetTime() {
      if (this.date !== this.defaultValues.date) {
        this.time = '00:00'
      } else {
        this.time = this.defaultValues.time
      }
    },
  },
}
</script>
