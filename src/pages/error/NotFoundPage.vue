<template>
  <v-container>
    <p class="text-h4 mt-4 mb-5">ページが見つかりません</p>
    <p>URLが間違っているか、ページが削除された可能性があります。</p>
    <div class="py-2 mb-2">
      <a href="javascript:void(0)" onclick="history.back()" class="mr-3">
        戻る
      </a>
      <router-link to="/">トップページへ</router-link>
    </div>
  </v-container>
</template>
