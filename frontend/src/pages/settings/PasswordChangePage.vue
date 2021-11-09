<template>
  <div id="password-change-page">
    <!-- メインエリア -->
    <div class="col-lg-7 col-md-6 col-sm-10 mx-auto">
      <SendForm
        v-model="formChangePassword"
        action="/auth/users/set_password/"
        method="post"
        @form-success="onSucceedChangePassword"
      >
        <template v-slot:footer>
          <div class="mt-4">
            <v-btn type="submit" color="primary" block dark>
              パスワードの変更
            </v-btn>
          </div>
          <div class="text-right pt-5 text-body-2">
            <div class="mb-1">
              <router-link class="button secondaryAction" to="/password/reset">
                パスワードを忘れましたか？
              </router-link>
            </div>
          </div>
        </template>
      </SendForm>
    </div>
  </div>
</template>

<script>
import SendForm from '@/components/SendForm.vue'

export default {
  components: {
    SendForm,
  },
  data() {
    return {
      formChangePassword: {
        current_password: {
          label: '現在のパスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        new_password: {
          label: '新しいパスワード',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
        re_new_password: {
          label: '新しいパスワード (確認用)',
          type: 'password',
          required: true,
          value: '',
          warnings: [],
        },
      },
    }
  },
  methods: {
    // パスワード変更押下
    onSucceedChangePassword: function () {
      this.$store.dispatch('message/setInfoMessage', {
        message: 'パスワードを変更しました。',
      })
    },
  },
}
</script>
