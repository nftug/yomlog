<template>
  <div class="pb-4">
    <v-card class="mx-auto text-body-2">
      <div class="pa-2">
        <div class="ma-4">
          <slot :total="total">
            <strong>{{ total }}冊</strong>
            の本が見つかりました。
          </slot>
        </div>
        <div class="ma-4">
          <SearchDialog :type="type" :hash="`search-${type}`">
            <template #activator="{ on: { click } }">
              <v-btn
                dark
                color="indigo"
                :small="!hasQuery"
                :x-small="hasQuery"
                :fab="hasQuery"
                elevation="1"
                class="ma-1"
                @click="click"
              >
                <template v-if="hasQuery">
                  <v-icon>mdi-magnify-plus-outline</v-icon>
                </template>
                <template v-else>
                  <v-icon left>mdi-magnify-plus-outline</v-icon>
                  検索
                </template>
              </v-btn>
            </template>
          </SearchDialog>

          <span class="ml-2">
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
          </span>
        </div>
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
  computed: {
    hasQuery() {
      return Object.keys(this.$route.query).length > 0
    },
  },
}
</script>
