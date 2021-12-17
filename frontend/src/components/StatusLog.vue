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
          <v-list-item link>
            <v-list-item-action>
              <v-checkbox
                v-model="checkbox[index]"
                @change="setToolbar('status')"
              ></v-checkbox>
            </v-list-item-action>

            <v-list-item-content @click="onClickEditStatus(item, state.id)">
              <div class="text-lg-h5 text-h6">
                {{ state.position }} / {{ item.total }}
              </div>
            </v-list-item-content>

            <v-list-item-action @click="onClickEditStatus(item, state.id)">
              <div class="text-body-2">
                {{ state.created_at | isoToDateTime }}
              </div>
              <v-chip small class="mt-2" :color="state.state | stateColor">
                {{ state.state | stateName }}
              </v-chip>
            </v-list-item-action>
          </v-list-item>
          <v-divider v-if="index + 1 < item.status.length"></v-divider>
        </template>
      </v-virtual-scroll>

      <template v-else>
        <div class="text-center text-body-2 py-5">記録が見つかりません。</div>
      </template>
    </v-card>

    <ItemDeleteDialog
      ref="itemDelete"
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
  components: {
    ItemDeleteDialog,
    StatusEditDialog,
  },
  data: () => ({
    itemHeight: 76,
  }),
  created() {
    this.initCheckbox('status')
  },
  methods: {
    onClickDeleteStatus(item) {
      this.$refs.itemDelete.showItemDeleteDialog(item.id)
    },
    onClickEditStatus(book, id) {
      this.$refs.statusEdit.showStatusPostDialog({ book: book, id: id })
    },
  },
}
</script>
