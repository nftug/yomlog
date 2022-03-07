<template>
  <div id="send-form">
    <Spinner size="100" v-if="fileFieldIndexes.Length && isSending" />

    <v-form v-else @submit.prevent="submitForm()" v-model="isValid" ref="form">
      <div v-for="(field, index) in form" :key="index">
        <template v-if="field.type != 'group'">
          <!-- ファイル送信フィールド -->
          <template v-if="field.type === 'file' || field.type === 'image'">
            <v-file-input
              :value="form[index].value"
              :id="field.name"
              :label="field.label"
              :ref="field.name"
              :required="field.required"
              :readonly="field.readonly"
              :error-messages="form[index].warnings"
              :accept="field.type === 'image' ? 'image/*' : null"
              @change="inputFile($event, index)"
              @click:clear="clearFile(index)"
            ></v-file-input>

            <template v-if="field.type === 'image'">
              <div v-show="field.prevSrc" style="position: relative">
                <template v-if="field.name === 'avatar'">
                  <v-list-item-avatar color="grey" size="150">
                    <v-img :src="field.prevSrc" />
                  </v-list-item-avatar>
                </template>
                <template v-else>
                  <img :src="field.prevSrc" alt="" width="150" />
                </template>

                <div style="position: absolute; top: 0px; left: 150px">
                  <v-btn text icon small @click="clearFile(index)">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                </div>
              </div>
            </template>
          </template>

          <!-- 通常のフィールド -->
          <template v-else-if="field.type === 'textarea'">
            <v-textarea
              :type="field.type"
              :value="form[index].value"
              :id="field.name"
              :label="field.label"
              :rows="field.rows"
              :required="field.required"
              :readonly="field.readonly"
              :error-messages="form[index].warnings"
              @input="onInputField($event, index)"
            ></v-textarea>
          </template>

          <template v-else>
            <v-text-field
              :type="field.type"
              :value="form[index].value"
              :id="field.name"
              :label="field.label"
              :required="field.required"
              :readonly="field.readonly"
              :error-messages="form[index].warnings"
              @input="onInputField($event, index)"
            ></v-text-field>
          </template>
        </template>

        <!-- 複数カラムのフィールド -->
        <template v-else>
          <v-row>
            <div
              v-for="(column, indexSub) in field.fields"
              :key="indexSub"
              :class="column.class"
            >
              <v-text-field
                :type="column.type"
                :value="form[index].fields[indexSub].value"
                :id="column.name"
                :label="column.label"
                :required="column.required"
                :readonly="column.readonly"
                :error-messages="column.warnings"
                @input="onInputField($event, index, indexSub)"
              ></v-text-field>
            </div>
          </v-row>
        </template>
      </div>

      <slot name="footer" :is-valid="isValid">
        <div class="pt-5">
          <v-btn
            type="submit"
            color="primary"
            block
            :dark="isValid"
            :disabled="!isValid"
          >
            送信
          </v-btn>
        </div>
      </slot>
    </v-form>
  </div>
</template>

<script>
import api from '@/services/api'
import Spinner from '@/components/Common/Spinner.vue'

export default {
  components: { Spinner },
  props: {
    value: { type: Array, require: true },
    action: { type: String, require: true },
    method: { type: String, default: 'post' },
    additionalData: { type: Object, require: false },
    confirmMethod: { type: Function, require: false },
  },
  data() {
    return {
      form: [],
      fields: [],
      formOrigin: [],
      fileFieldIndexes: [],
      isSending: false,
      isValid: false,
    }
  },
  created() {
    // propsからフォームをディープコピー
    this.form = JSON.parse(JSON.stringify(this.value))

    this.form.forEach((field, index) => {
      // ファイルフィールドを検索し、フィールド名をimageFieldsNameに追加
      // (複数コラムには未対応)
      if (field.type === 'file' || field.type === 'image') {
        this.fileFieldIndexes.push(index)
      }

      // fieldsに与えられたフィールドをすべて入れる
      if (field.type !== 'group') {
        this.fields.push(field)
      } else {
        field.fields.forEach((column) => {
          this.fields.push(column)
        })
      }

      // フォームのデフォルト値を保存
      this.formOrigin = JSON.parse(JSON.stringify(this.form))
    })
  },
  methods: {
    inputFile(event, index) {
      const field = this.form[index]
      field.warnings = []
      if (event) {
        field.prevSrc = URL.createObjectURL(event)
        field.value = event
      } else {
        field.prevSrc = ''
      }

      this.setModelValue()
    },
    clearFile(index) {
      const field = this.form[index]
      field.warnings = []
      field.value = null
      field.prevSrc = ''

      this.setModelValue()
    },
    onInputField($event, index, indexSub) {
      const targetField =
        indexSub !== undefined
          ? this.form[index].fields[indexSub]
          : this.form[index]

      targetField.value = $event
      targetField.warnings = []

      // パスワード欄のバリデーションをクリア
      if (targetField.name === 'password') {
        const pairField = this.fields.find(
          (field) => field.name === 're_password'
        )
        pairField.warnings = []
      } else if (targetField.name === 're_password') {
        const pairField = this.fields.find((field) => field.name === 'password')
        pairField.warnings = []
      }

      this.setModelValue()
    },
    resetFields() {
      // フィールドをすべてリセット
      this.form = this.formOrigin
      this.setModelValue()
    },
    setModelValue() {
      // フォームの内容を親に反映させる
      const formCopied = JSON.parse(JSON.stringify(this.form))
      this.$emit('input', formCopied)
    },
    async submitForm() {
      let data
      let method = this.method

      // フォームのバリデーション
      if (!this.$refs.form.validate()) return

      // 確認メソッドの実行
      if (this.confirmMethod) {
        const ans = await this.confirmMethod()
        if (!ans) return
      }

      // 送信データのarrange
      if (this.fileFieldIndexes.length) {
        // ファイルフィールドありの場合
        data = new FormData()
        this.fields.forEach((field) => {
          const { name, type, value } = field
          if (value !== undefined && value !== null) {
            data.append(name, value)
          } else if ((type === 'file' || type === 'image') && !field.prevSrc) {
            data.append(name, new File([], ''))
          }
        })
        if (this.additionalData) {
          Object.keys(this.additionalData).forEach((key) => {
            data.append(key, this.additionalData[key])
          })
        }
      } else {
        // ファイルフィールドなしの場合
        data = {}
        this.fields.forEach((field) => {
          data[field.name] = field.value
        })
        if (this.additionalData) {
          Object.assign(data, this.additionalData)
        }
      }

      try {
        // フォーム送信
        this.isSending = true
        const response = await api({ method, url: this.action, data })
        // フォーム送信完了イベント発火
        this.$emit('form-success', response.data)
        //
      } catch (error) {
        // バリデーションNG
        const errorData = error.response.data
        Object.keys(errorData).forEach((key) => {
          this.setError(key, errorData[key])
        })

        // バリデーションNGイベント発火 & warningの反映
        this.$emit('form-error', errorData)
        this.setModelValue()
        return Promise.reject(error)
      } finally {
        this.isSending = false
      }
    },
    setError(key, value) {
      // エラー処理用
      if (key === 'token' || key === 'uid') {
        this.$store.dispatch('message/setErrorMessage', {
          message: '不正なトークンです。',
        })
      } else if (key === 'non_field_errors') {
        if (value[0].includes('password')) {
          const passwordFields = this.fields.filter(
            (field) =>
              field.type === 'password' && field.name !== 'current_password'
          )
          passwordFields.forEach((field) => {
            field.warnings.push('パスワードが一致しません。')
          })
        } else {
          this.$store.dispatch('message/setErrorMessage', {
            message: value,
          })
        }
      } else {
        const targetField = this.fields.find(({ name }) => name === key)
        if (key === 'current_password') value = 'パスワードが正しくありません。'
        targetField.warnings = value
      }
    },
  },
}
</script>
