<template>
  <div id="account-delete-page">
    <p class="text-body-2">
      アカウントを削除するには「退会する」ボタンを押してください。
    </p>

    <p>
      <v-btn
        color="red"
        block
        dark
        @click="$refs.AccountDeleteDialog.showDialog()"
      >
        <v-icon left>mdi-account-remove</v-icon>
        退会する
      </v-btn>
    </p>

    <AccountDeleteDialog ref="AccountDeleteDialog"></AccountDeleteDialog>
  </div>
</template>

<script>
import AccountDeleteDialog from '@/components/Dialog/AccountDeleteDialog.vue'

export default {
  components: { AccountDeleteDialog },
}
</script>
