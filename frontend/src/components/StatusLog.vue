<template>
  <v-card outlined class="mx-auto">
    <v-virtual-scroll
      :height="height"
      item-height="76"
      :bench="benched"
      :items="item.status"
    >
      <template #default="{ item: state, index }">
        <v-row class="col-lg-8 mx-auto">
          <v-list-item class="py-3">
            <v-row align="center">
              <v-list-item-content>
                <div class="text-lg-h5 text-h6">
                  {{ state.position }} / {{ item.total }}
                  <span class="text-body-2">
                    {{ item.format_type ? '' : 'ページ' }}
                  </span>
                </div>
              </v-list-item-content>

              <v-list-item-action>
                <div class="text-body-2">
                  {{ state.created_at | isoToDateTime }}
                </div>
                <v-chip small class="mt-2" :color="state.state | stateColor">
                  {{ state.state | stateName }}
                </v-chip>
              </v-list-item-action>

              <v-list-item-action>
                <v-menu offset-y>
                  <template #activator="{ on, attrs }">
                    <v-btn small icon v-bind="attrs" v-on="on">
                      <v-icon small>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list dense close-on-click>
                    <v-list-item link>
                      <v-list-item-title>編集</v-list-item-title>
                    </v-list-item>
                    <v-list-item link>
                      <v-list-item-title>削除</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </v-list-item-action>
            </v-row>
          </v-list-item>
        </v-row>
        <v-divider v-if="index + 1 < item.status.length"></v-divider>
      </template>
    </v-virtual-scroll>
  </v-card>
</template>

<script>
import Mixins, { BookListMixin } from '@/mixins'

export default {
  mixins: [Mixins, BookListMixin],
  props: {
    item: {
      type: Object,
    },
    height: {
      type: String,
      default: '400',
    },
  },
  data: () => ({
    benched: 0,
  }),
}
</script>
