<template>
  <v-container>
    <v-col sm="10" lg="7" xl="5" class="mx-auto">
      <p class="text-h4 my-5 d-none d-lg-block">お問い合わせ</p>
      <SendForm
        v-model="formInquiry"
        action="/inquiry/"
        method="post"
        @form-success="onSucceedSend"
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
              <v-icon left>mdi-email</v-icon>
              送信
            </v-btn>
          </div>
        </template>
      </SendForm>
    </v-col>

    <RequireEmailDialog></RequireEmailDialog>
  </v-container>
</template>

<script>
import RequireEmailDialog from '@/components/Dialog/RequireEmailDialog.vue'
import SendForm from '@/components/Common/SendForm.vue'

export default {
  components: { RequireEmailDialog, SendForm },
  data() {
    return {
      formInquiry: [
        {
          name: 'email',
          label: 'メールアドレス',
          type: 'email',
          required: true,
          warnings: [],
          value: this.$store.state.auth.email,
          readonly: this.$store.state.auth.email.length > 0,
        },
        {
          name: 'title',
          label: 'タイトル',
          type: 'text',
          required: true,
          warnings: [],
          value: '',
        },
        {
          name: 'content',
          label: 'お問い合わせ内容',
          type: 'textarea',
          required: true,
          warnings: [],
          value: '',
          rows: 8,
        },
      ],
    }
  },
  methods: {
    onSucceedSend() {
      this.$router.go(-1)
      this.$store.dispatch('message/setInfoMessage', {
        message: 'お問い合わせメールを送信しました。',
      })
    },
  },
}
</script>
