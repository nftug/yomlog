<template>
  <div id="send-form">
    <Spinner size="100" v-if="isSending" />

    <v-form v-else @submit.prevent="submitForm()">
      <div v-for="(field, key) in form" :key="key">
        <template v-if="field.type != 'group'">
          <template v-if="field.type === 'file' || field.type === 'image'">
            <v-file-input
              :value="form[key].value"
              :id="key"
              :label="field.label"
              :ref="key"
              :required="field.required"
              :readonly="field.readonly"
              :error-messages="form[key].warnings"
              :accept="field.type === 'image' ? 'image/*' : null"
              @change="inputFile($event, key)"
            ></v-file-input>

            <template v-if="field.type === 'image'">
              <div v-show="field.prevSrc">
                <img :src="field.prevSrc" alt="" width="150" />
                <div>
                  <v-btn text small color="primary" @click="clearFile(key)">
                    クリア
                  </v-btn>
                </div>
              </div>
            </template>
          </template>
          <template v-else>
            <v-text-field
              :type="field.type"
              :value="form[key].value"
              :id="key"
              :label="field.label"
              :required="field.required"
              :readonly="field.readonly"
              :error-messages="form[key].warnings"
              @input="onInputField($event, key)"
            ></v-text-field>
          </template>
        </template>

        <template v-else>
          <v-row>
            <div
              v-for="(column, key2) in field.fields"
              :key="key2"
              :class="column.class"
            >
              <v-text-field
                :type="field.type"
                :value="form[key].fields[key2].value"
                :id="key2"
                :label="column.label"
                :required="column.required"
                :readonly="column.readonly"
                :error-messages="column.warnings"
                @input="onInputField($event, key, key2)"
              ></v-text-field>
            </div>
          </v-row>
        </template>
      </div>

      <slot name="footer">
        <div class="pt-5">
          <v-btn type="submit" color="primary" block>送信</v-btn>
        </div>
      </slot>
    </v-form>
  </div>
</template>

<script>
import api from '@/services/api'
import Spinner from '@/components/Common/Spinner.vue'

export default {
  props: {
    value: Object,
    action: String,
    method: String,
    additionalData: Object,
  },
  data() {
    return {
      form: this.value,
      fileFieldNames: [],
      isSending: false,
    }
  },
  components: {
    Spinner,
  },
  created() {
    // ファイルフィールドを検索し、フィールド名をimageFieldsNameに追加
    // (複数コラムには未対応)
    Object.keys(this.form).forEach((key) => {
      let field = this.form[key]
      if (field.type === 'file' || field.type === 'image') {
        this.fileFieldNames.push(key)
      }
    })
  },
  methods: {
    inputFile: function (event, key) {
      let field = this.form[key]
      field.warnings = []
      if (event) {
        field.prevSrc = URL.createObjectURL(event)
        field.value = event
      } else {
        field.prevSrc = ''
      }
      this.$emit('input', this.form)
    },
    clearFile: function (fieldName) {
      let field = this.form[fieldName]
      field.warnings = []
      field.value = null
      field.prevSrc = ''
      this.$emit('input', this.form)
    },
    submitForm: async function () {
      // データを取り出し & バリデーションをクリア
      let data
      let postMethod = this.method

      if (this.fileFieldNames.length) {
        // ファイルフィールドありの場合
        data = new FormData()
        Object.keys(this.form).forEach((key) => {
          if (this.form[key].type != 'group') {
            data.append(key, this.form[key].value)
            this.form[key].warnings = []
          } else {
            Object.keys(this.form[key].fields).forEach((key2) => {
              data.append(key2, this.form[key].fields[key2].value)
              this.form[key].fields[key2].warnings = []
            })
          }
        })
        if (this.additionalData) {
          Object.keys(this.additionalData).forEach((key) => {
            data.append(key, this.additionalData[key])
          })
        }

        // 各ファイルフィールドに対して、アップロードの可否判定
        this.fileFieldNames.forEach((key) => {
          let fileField = this.form[key]

          if (!fileField.value) {
            if (fileField.required) {
              this.fileField.warnings.push('この項目は空にできません。')
              return Promise.reject()
            } else if (fileField.prevSrc) {
              data.delete(key)
              postMethod = 'patch'
            } else {
              data.set(key, new File([], ''))
            }
          }
        })
      } else {
        // 写真なしの場合
        data = {}
        Object.keys(this.form).forEach((key) => {
          if (this.form[key].type != 'group') {
            data[key] = this.form[key].value
            this.form[key].warnings = []
          } else {
            Object.keys(this.form[key].fields).forEach((key2) => {
              data[key2] = this.form[key].fields[key2].value
              this.form[key].fields[key2].warnings = []
            })
          }
        })
        if (this.additionalData) {
          Object.assign(data, this.additionalData)
        }
      }

      // フォーム送信
      this.isSending = true
      await api({
        method: postMethod,
        url: this.action,
        data: data,
      })
        .then((response) => {
          this.isSending = false
          // フォーム送信完了イベント発火
          this.$emit('form-success', response.data)
        })
        .catch((error) => {
          this.isSending = false
          // バリデーションNG
          let errData = error.response.data
          Object.keys(errData).forEach((key) => {
            if (key === 'token' || key === 'uid') {
              this.$store.dispatch('message/setErrorMessage', {
                message: '不正なトークンです。',
              })
            } else if (key === 'non_field_errors') {
              if (errData[key][0].includes('password')) {
                const prefix = this.form.new_password ? 'new_' : ''
                this.form[`${prefix}password`].warnings.push(
                  'パスワードが一致しません。'
                )
                this.form[`re_${prefix}password`].warnings.push(
                  'パスワードが一致しません。'
                )
              } else {
                this.form.non_field.warnings = errData[key]
              }
            } else if (key === 'current_password') {
              this.form.current_password.warnings.push(
                'パスワードが正しくありません。'
              )
            } else {
              if (this.form[key].fields) {
                // 複数コラムの場合、フィールドのエラーを一つずつ処理
                Object.keys(this.form[key].fields).forEach((key2) => {
                  if (key2 === key) {
                    this.form[key].fields[key2].warnings = errData[key2]
                  }
                })
              } else {
                this.form[key].warnings = errData[key]
              }
            }
          })

          // バリデーションNGイベント発火
          this.$emit('form-error', error.response.data)
          return Promise.reject(error)
        })

      this.$emit('input', this.form)
    },
    onInputField: function (event, key, key2) {
      let field = key2 ? this.form[key].fields[key2] : this.form[key]

      // dataに反映
      field.value = event
      // warningsをクリア
      field.warnings = []
      // v-modelで指定されたformにinputする
      this.$emit('input', this.form)
    },
  },
}
</script>
