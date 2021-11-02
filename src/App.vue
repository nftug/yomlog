<template>
  <v-app>
    <v-app-bar app color="primary" dark clipped-left>
      <v-app-bar-nav-icon
        class="mr-2 hidden-lg-and-up"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/vuetifyjs/vuetify/releases/latest"
        target="_blank"
        text
      >
        <span class="mr-2 hidden-sm-and-down">Latest Release</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer app clipped v-model="drawer">
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">Application</v-list-item-title>
          <v-list-item-subtitle>subtext</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list nav>
        <v-list-item v-for="item in items" :key="item.title" link>
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <v-alert
          v-model="showInfo"
          border="left"
          color="indigo"
          dark
          dismissible
        >
          {{ message.info }}
        </v-alert>

        <v-card width="700px" class="mx-auto pa-5 text-center">
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
                  <v-btn text type="submit" :disabled="!formName.valid">
                    OK
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-dialog>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      dialog: false,
      drawer: null,
      items: [
        { title: 'Dashboard', icon: 'mdi-view-dashboard' },
        { title: 'Photos', icon: 'mdi-image' },
        { title: 'About', icon: 'mdi-help-box' },
      ],
      formName: {
        valid: true,
        firstname: '',
        lastname: '',
      },
      nameRules: [(v) => !!v || '名前を入力してください'],
      emailRules: [
        (v) => !!v || 'メールアドレスを入力してください',
        (v) => /.+@.+/.test(v) || '正しいメールアドレスを入力してください',
      ],
      message: {
        info: '',
        error: '',
      },
    }
  },
  computed: {
    showInfo: {
      get() {
        return this.message.info.length > 0
      },
      set(val) {
        this.message.info = val
      },
    },
  },
  watch: {
    dialog() {
      this.$refs.form.reset()
    },
  },
  methods: {
    submitForm() {
      if (this.$refs.form.validate()) {
        this.message.info = `${this.formName.lastname} ${this.formName.firstname}さん、こんにちは！`
        this.dialog = false
      }
    },
  },
}
</script>
