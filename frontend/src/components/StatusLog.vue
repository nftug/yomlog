<template>
  <div id="status-log" v-if="item.status">
    <v-card outlined class="mx-auto" :height="height">
      <v-virtual-scroll
        v-if="item.status.length && item.status[0].id"
        :height="height"
        :item-height="itemHeight"
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
                      <v-btn
                        small
                        icon
                        v-bind="attrs"
                        v-on="on"
                        :disabled="!state.id"
                      >
                        <v-icon small>mdi-dots-vertical</v-icon>
                      </v-btn>
                    </template>
                    <v-list dense close-on-click>
                      <v-list-item
                        link
                        @click="onClickEditStatus(item, state.id)"
                        :disabled="state.state === 'to_be_read'"
                      >
                        <v-list-item-title>編集</v-list-item-title>
                      </v-list-item>
                      <v-list-item link @click="onClickDeleteStatus(state)">
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

      <template v-else>
        <div class="text-center text-body-2 py-5">記録が見つかりません。</div>
      </template>
    </v-card>

    <ItemDeleteDialog
      ref="statusDelete"
      type="status"
      @delete="sendDeleteProp"
    ></ItemDeleteDialog>
    <StatusEditDialog ref="statusEdit" @post="sendEditProp"></StatusEditDialog>
  </div>
</template>

<script>
import Mixins, { BookListMixin, BookDetailChildMixin } from '@/mixins'
import ItemDeleteDialog from '@/components/ItemDeleteDialog.vue'
import StatusEditDialog from '@/components/StatusPostDialog.vue'

export default {
  mixins: [Mixins, BookListMixin, BookDetailChildMixin],
  props: {
    item: {
      type: Object,
    },
    height: {
      type: String,
      default: '400',
    },
  },
  components: {
    ItemDeleteDialog,
    StatusEditDialog,
  },
  data: () => ({
    itemHeight: 76,
  }),
  computed: {
    benched() {
      return Math.ceil(this.height / this.itemHeight)
    },
  },
  methods: {
    onClickDeleteStatus(item) {
      this.$refs.statusDelete.showItemDeleteDialog(item.id, 'status')
    },
    onClickEditStatus(book, id) {
      this.$refs.statusEdit.showStatusPostDialog({ book: book, id: id })
    },
  },
}
</script>
