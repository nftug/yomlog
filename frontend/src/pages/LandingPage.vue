<template>
  <v-container fluid>
    <v-parallax dark src="@/assets/jumbotron_bg.jpg">
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 class="text-h3 font-weight-thin mb-4">{{ appName }}</h1>
          <div class="text-body-2 mt-7">
            <div class="mb-1">
              {{ appName }}
              はあなたの読書ライフをサポートする読書管理サービスです。
            </div>
            <div class="mb-1">
              日々の読書状況を可視化して、読書の習慣を継続させましょう。
            </div>
          </div>
          <v-btn class="cyan darken-1 mt-7" dark x-large to="/login">
            <strong>使ってみる</strong>
          </v-btn>
        </v-col>
      </v-row>
    </v-parallax>

    <v-col sm="10" lg="9" class="mx-auto my-10">
      <v-row align="center" justify="center">
        <IntroductionCard
          icon="mdi-bookmark-check"
          title="本を読むたびに進捗を記録"
        >
          ページ単位で日々の読書量を記録できます。
          <br />
          一日に読んだページ数が一目瞭然。読書の継続に役立ちます。
        </IntroductionCard>

        <IntroductionCard icon="mdi-note-edit" title="読書ノートを残す">
          読書中に気になった箇所にはノートを残しましょう。
          <br />
          記録したノートは全文検索が可能。
          <br />
          複数冊の本を横断した検索も可能です。
        </IntroductionCard>

        <IntroductionCard icon="mdi-library-shelves" title="自動で本を分類分け">
          読書の進捗に応じて、自動で本を本棚に分類します。
          <br />
          読み忘れの防止や読んだ本の振り返りにも便利です。
        </IntroductionCard>

        <IntroductionCard icon="mdi-poll" title="読書状況を分析">
          一日に読んだページ数がひと目で分かります。
          <br />
          カレンダー機能で月単位での読書状況も俯瞰できます。
        </IntroductionCard>

        <IntroductionCard icon="mdi-tablet-android" title="Kindle本にも対応">
          ページ番号を持たないKindle本にも対応。
          <br />
          記録の際は位置Noをそのまま記入でOK。
          <br />
          自動で対応する紙の本のページ番号に変換します。
        </IntroductionCard>
      </v-row>

      <v-divider class="my-8"></v-divider>

      <v-row align="center" justify="center">
        <v-col cols="12" md="8" lg="6">
          <v-card class="elevation-0 transparent my-2">
            <v-card-title class="headline justify-center">
              {{ appName }}をはじめよう
            </v-card-title>
            <v-card-text class="text-center text-body-2">
              {{ appName }}の利用はこちらからどうぞ。
            </v-card-text>

            <v-card-actions class="justify-center mt-3">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-btn
                    class="cyan darken-1 col-12 col-sm-6"
                    dark
                    x-large
                    to="/login"
                    block
                  >
                    <v-icon left size="24">mdi-login</v-icon>
                    ログイン
                  </v-btn>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-btn
                    class="indigo darken-1 col-12 col-sm-6"
                    dark
                    x-large
                    to="/signup"
                    block
                  >
                    <v-icon left size="24">mdi-account-plus</v-icon>
                    ユーザー登録
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-col>
  </v-container>
</template>

<script>
import Mixins from '@/mixins'
import IntroductionCard from '@/components/Landing/IntroductionCard.vue'

export default {
  mixins: [Mixins],
  components: { IntroductionCard },
}
</script>
