<template>
  <div id="send-form">
    <Spinner size="100" v-if="isSending" />

    <v-form v-else @submit.prevent="submitForm()">
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
            ></v-file-input>

            <template v-if="field.type === 'image'">
              <div v-show="field.prevSrc">
                <img :src="field.prevSrc" alt="" width="150" />
                <div>
                  <v-btn text small color="primary" @click="clearFile(index)">
                    クリア
                  </v-btn>
                </div>
              </div>
            </template>
          </template>

          <!-- 通常のフィールド -->
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
    value: { type: Array, require: true },
    action: { type: String, require: true },
    method: { type: String, default: 'post' },
    additionalData: { type: Object, require: false },
  },
  data() {
    return {
      form: this.value,
      fileFieldIndexes: [],
      isSending: false,
    }
  },
  components: {
    Spinner,
  },
  created() {
    // ファイルフィールドを検索し、フィールド名をimageFieldsNameに追加
    // (複数コラムには未対応)
    this.form.forEach((field, index) => {
      if (field.type === 'file' || field.type === 'image') {
        this.fileFieldIndexes.push(index)
      }
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
      this.$emit('input', this.form)
    },
    clearFile(index) {
      const field = this.form[index]
      field.warnings = []
      field.value = null
      field.prevSrc = ''
      this.$emit('input', this.form)
    },
    async submitForm() {
      // データを取り出し & バリデーションをクリア
      let data
      let method = this.method

      if (this.fileFieldIndexes.length) {
        // ファイルフィールドありの場合
        data = new FormData()
        this.form.forEach((field) => {
          if (field.type !== 'group') {
            data.append(field.name, field.value)
            field.warnings = []
          } else {
            field.fields.forEach((column) => {
              data.append(column.name, column.value)
              column.warnings = []
            })
          }
        })
        if (this.additionalData) {
          Object.keys(this.additionalData).forEach((key) => {
            data.append(key, this.additionalData[key])
          })
        }

        // 各ファイルフィールドに対して、アップロードの可否判定
        this.fileFieldIndexes.forEach((index) => {
          const fileField = this.form[index]

          if (!fileField.value) {
            if (fileField.required) {
              this.fileField.warnings.push('この項目は空にできません。')
              return Promise.reject()
            } else if (fileField.prevSrc) {
              data.delete(fileField.name)
              method = 'patch'
            } else {
              data.set(fileField.name, new File([], ''))
            }
          }
        })
      } else {
        // 写真なしの場合
        data = {}
        this.form.forEach((field) => {
          if (field.type !== 'group') {
            data[field.name] = field.value
            field.warnings = []
          } else {
            field.fields.forEach((column) => {
              data[column.name] = column.value
              column.warnings = []
            })
          }
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
      } catch (error) {
        // バリデーションNG
        const errorData = error.response.data

        Object.keys(errorData).forEach((key) => {
          if (key === 'token' || key === 'uid') {
            this.$store.dispatch('message/setErrorMessage', {
              message: '不正なトークンです。',
            })
          } else if (key === 'non_field_errors') {
            if (errorData[key][0].includes('password')) {
              const passwordFields = this.form.filter(
                (field) => field.type === 'password'
              )
              passwordFields.forEach((field) => {
                field.warnings.push('パスワードが一致しません。')
              })
            } else {
              this.$store.dispatch('message/setErrorMessage', {
                message: errorData[key],
              })
            }
          } else if (key === 'current_password') {
            this.form.current_password.warnings.push(
              'パスワードが正しくありません。'
            )
          } else {
            let targetField = this.form.find(({ name }) => name === key)
            // エラーのキーが複数カラムに存在する場合、探索してtargetFieldを設定
            if (!targetField) {
              loop: for (const field of this.form) {
                const row = field.fields
                if (row && Array.isArray(row)) {
                  for (const column of row) {
                    if (column.name === key) {
                      targetField = column
                      break loop
                    }
                  }
                }
              }
            }

            targetField.warnings = errorData[key]
          }
        })

        // バリデーションNGイベント発火
        this.$emit('form-error', errorData)
        return Promise.reject(error)
      } finally {
        this.isSending = false
        this.$emit('input', this.form)
      }
    },
    onInputField(event, index, indexSub) {
      const targetField =
        indexSub !== undefined
          ? this.form[index].fields[indexSub]
          : this.form[index]

      // dataに反映
      targetField.value = event
      // warningsをクリア
      targetField.warnings = []
      // v-modelで指定されたformにinputする
      this.$emit('input', this.form)
    },
  },
}
</script>
