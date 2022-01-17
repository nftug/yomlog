<template>
  <div id="status-log" v-if="item.status">
    <v-card outlined class="mx-auto overflow-hidden" :height="height">
      <v-sheet flat class="overflow-y-auto fill-height">
        <template v-if="item.status.length">
          <div v-for="(state, index) in item.status" :key="index">
            <v-list-item link>
              <v-list-item-action>
                <v-checkbox
                  v-model="checkbox[index]"
                  @change="setToolbar('status')"
                ></v-checkbox>
              </v-list-item-action>

              <v-list-item-content @click="onClickEditStatus(state)">
                <div>{{ state | statePosition }}</div>
                <div
                  v-if="state.diff.value"
                  class="text-body-2 grey--text text--darken-2"
                >
                  {{ state | stateDiff }}
                </div>
              </v-list-item-content>

              <v-list-item-action @click="onClickEditStatus(state)">
                <div class="text-body-2">
                  {{ state.created_at | isoToDateTime }}
                </div>
                <v-chip small class="mt-2" :color="state.state | stateColor">
                  {{ state.state | stateName }}
                </v-chip>
              </v-list-item-action>
            </v-list-item>
            <v-divider v-if="index + 1 < item.status.length"></v-divider>
          </div>
        </template>

        <template v-else>
          <div class="text-center text-body-2 py-5">記録が見つかりません。</div>
        </template>
      </v-sheet>
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
  created() {
    this.initCheckbox('status')
  },
  filters: {
    statePosition({ position }) {
      if (position.page) {
        return `${position.page} ページ`
      } else {
        return `${position.value}`
      }
    },
    stateDiff({ diff }) {
      if (diff.page) {
        return `+${diff.page} ページ (+${diff.percentage}%)`
      } else {
        return `+${diff.value} (+${diff.percentage}%)`
      }
    },
  },
  methods: {
    onClickDeleteStatus(item) {
      this.$refs.itemDelete.showItemDeleteDialog(item.id)
    },
    onClickEditStatus(item) {
      this.$refs.statusEdit.showStatusPostDialog({
        book: this.item,
        status: item,
      })
    },
  },
}
</script>
