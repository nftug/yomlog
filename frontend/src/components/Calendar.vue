<template>
  <div>
    <v-sheet
      tile
      height="6vh"
      color="grey lighten-3"
      class="d-flex align-center"
    >
      <v-btn outlined small class="ma-2" @click="setToday">今日</v-btn>
      <v-btn icon @click="$refs.calendar.prev()">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
      <v-btn icon @click="$refs.calendar.next()">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
      <v-toolbar-title>{{ title }}</v-toolbar-title>
    </v-sheet>

    <v-sheet :height="height">
      <!-- Loading overlay -->
      <v-overlay absolute v-show="isLoading" color="grey">
        <v-progress-circular
          indeterminate
          color="white"
          size="100"
          width="5"
        ></v-progress-circular>
      </v-overlay>

      <!-- カレンダー -->
      <v-calendar
        ref="calendar"
        v-model="value"
        :events="events"
        :event-color="getEventColor"
        locale="ja-jp"
        :day-format="(timestamp) => new Date(timestamp.date).getDate()"
        :month-format="
          (timestamp) => new Date(timestamp.date).getMonth() + 1 + ' /'
        "
        event-more-text="+{0}件の記録"
        @change="getEvents"
        @click:event="showEvent"
        @click:more="showMore"
        @click:date="showMore"
      ></v-calendar>

      <!-- ポップアップメニュー -->
      <v-menu
        v-model="selectedOpen"
        :close-on-content-click="false"
        :activator="selectedElement"
        offset-x
        style="max-width: 320px"
      >
        <v-card class="overflow-hidden">
          <v-toolbar color="primary" dark dense flat>
            <v-btn icon @click="selectedOpen = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>{{ selectedDate }}</v-toolbar-title>
          </v-toolbar>

          <v-sheet
            color="grey lighten-4"
            width="320px"
            max-height="320px"
            flat
            class="overflow-y-auto"
          >
            <v-card-text>
              <template v-if="!isEventsEmpty">
                <div
                  v-for="(item, key) in selectedEvents"
                  :key="key"
                  class="pb-3"
                >
                  <template v-if="item.events.length">
                    <v-list dense :color="item.events[0].color" dark two-line>
                      <v-subheader>
                        {{ item.label }}
                        <v-chip x-small class="ma-2" light>
                          {{ item.events.length }}
                        </v-chip>
                      </v-subheader>
                      <v-list-item v-for="(event, i) in item.events" :key="i">
                        <v-list-item-content>
                          <v-list-item-title>
                            {{ event.item | getItemTitle }}
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            {{ event.item.book.title }}
                          </v-list-item-subtitle>
                        </v-list-item-content>

                        <v-list-item-action>
                          <v-btn
                            icon
                            small
                            :to="`/book/detail/${event.item.book.id}`"
                          >
                            <v-icon>mdi-book</v-icon>
                          </v-btn>
                        </v-list-item-action>
                        <v-list-item-action>
                          <v-btn
                            icon
                            small
                            @click="showEvent({ event, nativeEvent: $event })"
                          >
                            <v-icon>mdi-pen</v-icon>
                          </v-btn>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list>
                  </template>
                </div>
              </template>

              <template v-else>
                <div class="text-center py-5">記録が見つかりません。</div>
              </template>
            </v-card-text>
          </v-sheet>
        </v-card>
      </v-menu>
    </v-sheet>

    <StatusEditDialog ref="statusEdit" @post="onEditProp"></StatusEditDialog>
    <NotePostDialog
      ref="noteEdit"
      @post="onEditProp"
      @delete="onDeleteProp"
    ></NotePostDialog>
  </div>
</template>

<script>
import api from '@/services/api'
import moment from 'moment'
import StatusEditDialog from '@/components/StatusPostDialog.vue'
import NotePostDialog from '@/components/NotePostDialog.vue'

export default {
  props: {
    height: {
      type: String,
      default: '82vh',
    },
  },
  components: {
    StatusEditDialog,
    NotePostDialog,
  },
  data: () => ({
    isLoading: false,
    events: [],
    value: moment().format('yyyy-MM-DD'),
    selectedEvent: {},
    selectedEvents: {
      status: {
        label: '進捗',
        events: [],
      },
      note: {
        label: 'ノート',
        events: [],
      },
    },
    selectedDate: null,
    selectedElement: null,
    selectedOpen: false,
    book: {},
    period: { start: '', end: '' },
  }),
  computed: {
    title() {
      return moment(this.value).format('yyyy年 M月')
    },
    isEventsEmpty() {
      let ret = true
      for (const key in this.selectedEvents) {
        if (this.selectedEvents[key].events.length) {
          ret = false
          break
        }
      }
      return ret
    },
  },
  filters: {
    getItemTitle(item) {
      return `${item.position.page}ページ (+${item.diff.page}ページ)`
    },
  },
  methods: {
    async getEvents({ start, end }) {
      try {
        this.isLoading = true

        const created_at__gte = moment(start.date)
          .subtract(1, 'M')
          .format('yyyy-MM-26')
        const created_at__lte = moment(end.date).add(1, 'M').format('yyyy-MM-6')

        const params = {
          no_pagination: true,
          only_progress: true,
          created_at__gte,
          created_at__lte,
        }
        this.events = []

        const { data: status } = await api.get('/status/', { params })
        status.forEach((item) => {
          this.events.push({
            name: `${item.book.title} (+${item.diff.page})`,
            start: new Date(item.created_at),
            end: new Date(item.created_at),
            color: 'blue',
            category: 'status',
            item: item,
            timed: false,
          })
        })

        const { data: note } = await api.get('/note/', { params })
        note.forEach((item) => {
          this.events.push({
            name: `${item.book.title} (${item.position})`,
            start: new Date(item.created_at),
            end: new Date(item.created_at),
            color: 'green',
            category: 'note',
            item: item,
            timed: false,
          })
        })
      } finally {
        this.isLoading = false
        this.period = { start, end }
      }
    },
    async showEvent({ event, nativeEvent }) {
      const type = event.item.diff ? 'status' : 'note'
      this.book = await this.$store.dispatch(
        'bookList/getBookItem',
        event.item.book.id
      )

      if (type === 'status') {
        this.$refs.statusEdit.showStatusPostDialog({
          book: this.book,
          id: event.item.id,
        })
      } else {
        this.$refs.noteEdit.showNotePostDialog({
          book: this.book,
          id: event.item.id,
        })
      }
      nativeEvent.stopPropagation()
    },
    showMore({ date, nativeEvent }) {
      const open = () => {
        this.selectedDate = date
        this.selectedElement = nativeEvent.target
        requestAnimationFrame(() =>
          requestAnimationFrame(() => (this.selectedOpen = true))
        )
      }

      if (this.selectedOpen) {
        this.selectedOpen = false
        requestAnimationFrame(() => requestAnimationFrame(() => open()))
      } else {
        open()
      }

      const events = this.events.filter((event) =>
        event.item.created_at.startsWith(date)
      )
      Object.keys(this.selectedEvents).forEach((key) => {
        this.selectedEvents[key].events = events.filter(
          (event) => event.category === key
        )
      })

      nativeEvent.stopPropagation()
    },
    getEventColor(event) {
      return event.color
    },
    setToday() {
      this.value = moment().format('yyyy-MM-DD')
    },
    onEditProp(prop, data) {
      this.$store.dispatch('bookList/editProp', {
        book: this.book,
        prop,
        data,
      })
      this.getEvents(this.period)
    },
    onDeleteProp(prop, id) {
      this.$store.dispatch('bookList/deleteProp', {
        book: this.book,
        prop,
        id,
      })
      this.getEvents(this.period)
    },
  },
}
</script>
