<template>
  <!-- メインエリア -->
  <div id="profile-settings-page">
    <SendForm
      v-model="userInfoForm"
      action="/auth/users/me/"
      method="patch"
      @form-success="onSucceedChangeUserInfo"
    >
      <template #footer="{ isValid }">
        <div class="mt-4">
          <v-btn
            type="submit"
            color="primary"
            block
            :dark="isValid"
            :disabled="!isValid"
          >
            設定の変更
          </v-btn>
        </div>
      </template>
    </SendForm>
  </div>
</template>

<script>
import SendForm from '@/components/Common/SendForm.vue'

export default {
  components: {
    SendForm,
  },
  data() {
    return {
      userInfoForm: [
        {
          name: 'fullname',
          label: 'お名前',
          type: 'group',
          fields: [
            {
              name: 'last_name',
              class: 'col-6',
              label: '姓',
              type: 'text',
              value: this.$store.state.auth.last_name,
              warnings: [],
            },
            {
              name: 'first_name',
              class: 'col-6',
              label: '名',
              type: 'text',
              value: this.$store.state.auth.first_name,
              warnings: [],
            },
          ],
        },
        {
          name: 'avatar',
          label: 'プロフィール画像',
          type: 'image',
          value: null,
          prevSrc: this.$store.state.auth.avatar,
          warnings: [],
        },
      ],
    }
  },
  methods: {
    // パスワード変更押下
    onSucceedChangeUserInfo() {
      this.$store.dispatch('auth/reload')
      this.$store.dispatch('message/setInfoMessage', {
        message: 'ユーザー情報を設定しました。',
      })
    },
  },
}
</script>
