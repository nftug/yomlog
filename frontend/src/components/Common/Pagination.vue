<template>
  <v-row justify="center">
    <v-col cols="8">
      <v-container class="max-width">
        <v-pagination
          v-model="page"
          class="my-4"
          v-bind="$attrs"
          @input="handlePagination"
        ></v-pagination>
      </v-container>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    value: { type: Number, require: true },
    hash: { type: String, require: false },
  },
  computed: {
    page: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
  },
  methods: {
    handlePagination() {
      this.$nextTick(() => {
        let query = { ...this.$route.query }
        query.page = this.page
        const oldPage = Number(this.$route.query.page || 1)

        if (query.page !== oldPage) {
          this.$router.push({
            path: this.$route.path,
            query,
            hash: this.hash,
          })
        }
      })
    },
  },
}
</script>
