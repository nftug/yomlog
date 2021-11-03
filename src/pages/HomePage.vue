<template>
  <v-container fluid>
    <div class="col-md-8 col-sm-10 mx-auto">
      <v-card class="pa-5 text-center">
        <h1>Hello Vuetify!</h1>

        <p class="mt-2">Vuetifyのテストです。</p>

        <v-dialog v-model="dialog" width="500">
          <template #activator="{ on, attrs }">
            <v-btn v-bind="attrs" v-on="on">Click Me!</v-btn>
          </template>

          <v-form
            lazy-validation
            v-model="formName.valid"
            ref="form"
            @submit.prevent="submitForm()"
          >
            <v-card>
              <v-card-title class="text-h5 green--text">
                こんにちは。
              </v-card-title>
              <v-card-text>
                お名前を入力してください。
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formName.lastname"
                      :rules="nameRules"
                      label="姓"
                      required
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formName.firstname"
                      :rules="nameRules"
                      label="名"
                      required
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="formName.email"
                      :rules="emailRules"
                      label="Email"
                      required
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="dialog = false">キャンセル</v-btn>
                <v-btn text type="submit" :disabled="!formName.valid">OK</v-btn>
              </v-card-actions>
            </v-card>
          </v-form>
        </v-dialog>
      </v-card>
    </div>
  </v-container>
</template>

<script>
import { FormRulesMixin } from '@/mixins'

export default {
  mixins: [FormRulesMixin],
  data: () => ({
    dialog: false,
    formName: {
      valid: true,
      firstname: '',
      lastname: '',
    },
  }),
  watch: {
    dialog() {
      this.$refs.form.reset()
    },
  },
  methods: {
    submitForm() {
      if (this.$refs.form.validate()) {
        let message = `${this.formName.lastname} ${this.formName.firstname}さん、こんにちは！`
        this.$store.dispatch('message/setInfoMessage', { message: message })
        this.dialog = false
      }
    },
  },
}
</script>
