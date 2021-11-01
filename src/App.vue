<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon class="mr-2"></v-app-bar-nav-icon>
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

    <v-bottom-navigation v-model="value" app dark class="hidden-md-and-up">
      <v-btn value="recent">
        <span>Recent</span>

        <v-icon>mdi-history</v-icon>
      </v-btn>

      <v-btn value="favorites">
        <span>Favorites</span>

        <v-icon>mdi-heart</v-icon>
      </v-btn>

      <v-btn value="nearby">
        <span>Nearby</span>

        <v-icon>mdi-map-marker</v-icon>
      </v-btn>
    </v-bottom-navigation>

    <v-main>
      <v-container>
        <div class="text-center">
          <h1 class="mt-2">Hello Vuetify!</h1>

          <p class="mt-2">
            Vuetify
            <v-icon>mdi-vuetify</v-icon>
            のテストです。
          </p>
        </div>

        <v-row class="mt-2 mx-auto" justify="center">
          <v-col cols="6">
            <v-dialog v-model="dialog" width="500">
              <template #activator="{ on, attrs }">
                <v-btn block v-bind="attrs" v-on="on">Click Me!</v-btn>
              </template>

              <v-card>
                <v-card-title class="text-h5 green--text">
                  こんにちは。
                </v-card-title>
                <v-card-text>これはダイアログです。</v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn text @click="dialog = false">キャンセル</v-btn>
                  <v-btn text @click="dialog = false">OK</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',

  data: () => ({
    value: 'recent',
    dialog: false,
  }),
}
</script>
