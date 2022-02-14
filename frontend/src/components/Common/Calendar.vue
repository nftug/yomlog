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
        v-model="date"
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
                            {{ getEventTitle(event) }}
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            {{ getBookTitle(event) }}
                          </v-list-item-subtitle>
                        </v-list-item-content>

                        <v-list-item-action v-if="!hasBookProp">
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

    <StatusEditDialog
      ref="statusEdit"
      hash="edit-status"
      @post="getEvents()"
    ></StatusEditDialog>
    <NotePostDialog
      ref="noteEdit"
      hash="edit-note"
      @post="getEvents()"
      @delete="getEvents()"
    ></NotePostDialog>
  </div>
</template>

<script>
import { BookListMixin } from '@/mixins'
import api from '@/services/api'
import moment from 'moment'
import StatusEditDialog from '@/components/Dialog/StatusPostDialog.vue'
import NotePostDialog from '@/components/Dialog/NotePostDialog.vue'

export default {
  mixins: [BookListMixin],
  props: {
    height: {
      type: String,
      default: '82vh',
    },
    value: {
      type: String,
      require: true,
    },
    query: {
      type: Object,
      default: () => ({}),
    },
    book: {
      type: Object,
      default: () => ({}),
    },
  },
  components: {
    StatusEditDialog,
    NotePostDialog,
  },
  data: () => ({
    isLoading: false,
    events: [],
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
    eventBook: {},
    period: { start: '', end: '' },
  }),
  computed: {
    date: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
    title() {
      return moment(this.date).format('yyyy年 M月')
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
    hasBookProp() {
      return Object.keys(this.book).length > 0
    },
    getEventTitle() {
      return function (event) {
        // TODO: ノートにもページ数表記を返すようにNoteSerializerを変更する
        const { item } = event
        if (item.diff) {
          return `${item.position.page}ページ (+${item.diff.page}ページ)`
        } else {
          const book = this.hasBookProp ? this.book : item.book
          return `${item.position}${book.format_type === 1 ? '' : 'ページ'}`
        }
      }
    },
    getBookTitle() {
      return function ({ item }) {
        if (this.hasBookProp) {
          return this.book.title
        } else {
          return item.book.title
        }
      }
    },
  },
  methods: {
    async getEvents({ start, end } = this.period) {
      this.events = []
      this.period = { start, end }
      const startDate = moment(start.date).subtract(1, 'M').date(26)
      const endDate = moment(end.date).add(1, 'M').date(6)

      const pushItems = (items) => {
        items.forEach((item) => {
          const bookTitle = this.book.title || item.book.title
          const isStatus = item.diff !== undefined

          this.events.push({
            name:
              `${bookTitle} ` +
              (isStatus ? `(+${item.diff.page})` : `(${item.position})`),
            start: new Date(item.created_at),
            end: new Date(item.created_at),
            color: isStatus ? 'blue' : 'green',
            category: isStatus ? 'status' : 'note',
            item: item,
            timed: false,
          })
        })
      }

      if (this.hasBookProp) {
        // propsでbookが設定されていた場合、propsからデータを読み込む
        const status = this.book.status.filter((item) => {
          if (startDate <= item.created_at <= endDate && item.diff.value > 0) {
            return true
          }
        })
        const notes = this.book.note.filter((item) => {
          if (startDate <= item.created_at <= endDate) {
            return true
          }
        })
        pushItems(status)
        pushItems(notes)
      } else {
        // 通常時はAPIからデータを読み込む
        try {
          this.isLoading = true

          const params = {
            no_pagination: true,
            state_not: 'to_be_read',
            created_at_after: startDate.format('yyyy-MM-DD'),
            created_at_before: endDate.format('yyyy-MM-DD'),
            ...this.query,
          }

          await Promise.any([
            api.get('/status/', { params }).then(({ data }) => {
              pushItems(data)
            }),
            api.get('/note/', { params }).then(({ data }) => {
              pushItems(data)
            }),
          ])
        } finally {
          this.isLoading = false
        }
      }
    },
    async showEvent({ event, nativeEvent }) {
      const type = event.item.diff ? 'status' : 'note'

      if (this.hasBookProp) {
        this.eventBook = this.book
      } else {
        this.eventBook = await this.$store.dispatch('bookList/getBookItem', {
          id: event.item.book.id,
        })
      }

      if (type === 'status') {
        this.$refs.statusEdit.showStatusPostDialog({
          book: this.eventBook,
          status: event.item,
        })
      } else {
        this.$refs.noteEdit.showNotePostDialog({
          book: this.eventBook,
          note: event.item,
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
      this.date = moment().format('yyyy-MM-DD')
    },
  },
}
</script>
