<template>
  <Dialog
    :hash="hash"
    ref="dialogDateRange"
    title="日付範囲の指定"
    :max-width="350"
    :form-valid="isValid"
  >
    <v-form ref="formStatusAdd" v-model="isValid" @submit.prevent>
      <DatePicker
        v-model="start"
        :default-value="startDefault"
        label="開始日"
        :max="end"
      ></DatePicker>
      <DatePicker
        v-model="end"
        :default-value="endDefault"
        label="終了日"
        :min="start"
      ></DatePicker>
    </v-form>
  </Dialog>
</template>

<script>
import Dialog from '@/components/Common/Dialog.vue'
import DatePicker from '@/components/Common/DatePicker.vue'

export default {
  components: { Dialog, DatePicker },
  props: { hash: { type: String } },
  data: () => ({
    isValid: false,
    start: '',
    end: '',
    startDefault: '',
    endDefault: '',
  }),
  methods: {
    async showDateRangeDialog({ start, end }) {
      ;[this.start, this.end] = [start, end]
      ;[this.startDefault, this.endDefault] = [start, end]

      if (await this.$refs.dialogDateRange.showDialog()) {
        return { start: this.start, end: this.end }
      } else {
        return Promise.reject()
      }
    },
  },
}
</script>
