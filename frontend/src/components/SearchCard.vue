<template>
  <div class="pb-4">
    <v-card class="mx-auto text-body-2" outlined>
      <div class="ma-4">
        <strong>{{ total }}冊</strong>
        の本が見つかりました。
      </div>
      <div class="ma-4">
        <v-icon>mdi-magnify</v-icon>
        <v-chip
          class="ma-1"
          v-for="(q, key) in query"
          :key="key"
          close
          small
          @click:close="removeQuery(key)"
        >
          {{ key | searchLabel }}
          {{ q }}
        </v-chip>

        <SearchDialog :type="type" :hash="`search-${type}`">
          <template #activator="{ on, attrs }">
            <v-btn small class="ma-1" icon v-on="on" v-bind="attrs">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
        </SearchDialog>
      </div>
    </v-card>
  </div>
</template>

<script>
import SearchDialog from '@/components/SearchDialog.vue'
import { ListViewMixin } from '@/mixins'

export default {
  mixins: [ListViewMixin],
  props: {
    total: { type: Number, require: true },
    type: { type: String, require: true },
  },
  data: () => ({
    query: {},
  }),
  components: {
    SearchDialog,
  },
  watch: {
    '$route.query'() {
      this.query = { ...this.$route.query }
      delete this.query.page
    },
  },
}
</script>
