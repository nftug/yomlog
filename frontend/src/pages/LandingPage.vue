<template>
  <v-container fluid>
    <v-parallax
      dark
      src="https://cdn.vuetifyjs.com/images/backgrounds/vbanner.jpg"
    >
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 class="text-h3 font-weight-thin mb-4">YomLog</h1>
          <h4 class="subheading mt-7">
            YomLog はあなたの読書ライフをサポートする読書管理サービスです。
          </h4>
          <v-btn class="cyan darken-1 mt-7" dark x-large to="/login">
            使ってみる
          </v-btn>
        </v-col>
      </v-row>
    </v-parallax>

    <v-col sm="10" lg="9" xl="7" class="mx-auto"></v-col>
  </v-container>
</template>
