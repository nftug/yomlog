<template>
  <div class="pb-4">
    <v-card class="mx-auto text-body-2" outlined>
      <div class="ma-4">
        <slot :total="total">
          <strong>{{ total }}冊</strong>
          の本が見つかりました。
        </slot>
      </div>
      <div class="ma-4">
        <v-icon>mdi-magnify</v-icon>
        <template v-for="(q, key) in $route.query">
          <v-chip
            v-if="key !== 'page'"
            :key="key"
            class="ma-1"
            close
            small
            @click:close="removeQuery(key)"
          >
            {{ key | searchLabel }}
            {{ q }}
          </v-chip>
        </template>

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
  data() {
    return {
      query: { ...this.$route.query },
    }
  },
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
