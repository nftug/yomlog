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
      <v-overlay absolute v-show="isLoading" color="grey">
        <v-progress-circular
          indeterminate
          color="white"
          size="100"
          width="5"
        ></v-progress-circular>
      </v-overlay>

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

      <v-menu
        v-model="selectedOpen"
        :close-on-content-click="false"
        :activator="selectedElement"
        offset-x
      >
        <v-card
          color="grey lighten-4"
          min-width="350px"
          max-height="300px"
          flat
          class="overflow-y-auto"
        >
          <v-toolbar color="primary" dark>
            <v-btn icon @click="selectedOpen = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title v-html="selectedDate"></v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <div v-for="(item, key) in selectedEvents" :key="key" class="pb-3">
              <template v-if="item.events.length">
                <v-list dense :color="item.events[0].color" dark two-line>
                  <v-subheader>
                    {{ item.label }}
                    <v-chip small class="ma-2" light>
                      {{ item.events.length }}
                    </v-chip>
                  </v-subheader>
                  <v-list-item
                    v-for="(event, i) in item.events"
                    :key="i"
                    :color="getEventColor(event)"
                    link
                    @click="showEvent({ event: event, nativeEvent: $event })"
                  >
                    <v-list-item-content>
                      <v-list-item-title>
                        {{ event.item | getSubtitle }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{ event.item.book.title }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </template>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </v-sheet>
  </div>
</template>

<script>
import api from '@/services/api'
import moment from 'moment'

export default {
  props: {
    height: {
      type: String,
      default: '82vh',
    },
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
  }),
  computed: {
    title() {
      return moment(this.value).format('yyyy年 M月')
    },
  },
  filters: {
    getSubtitle(item) {
      return `${item.position}${!item.book.format_type ? 'ページ' : ''}`
    },
  },
  methods: {
    async getEvents({ start, end }) {
      try {
        this.isLoading = true

        const params = {
          no_pagination: true,
          created_at__gte: start.date,
          created_at__lte: end.date,
        }
        const events = []

        const { data: status } = await api.get('/status/', { params: params })
        status.forEach((item) => {
          events.push({
            name: `${item.book.title} (+${item.diff.percent})`,
            start: new Date(item.created_at),
            end: new Date(item.created_at),
            color: 'blue',
            category: 'status',
            item: item,
            timed: false,
          })
        })

        const { data: note } = await api.get('/note/', { params: params })
        note.forEach((item) => {
          events.push({
            name: `${item.book.title} (${item.position})`,
            start: new Date(item.created_at),
            end: new Date(item.created_at),
            color: 'green',
            category: 'note',
            item: item,
            timed: false,
          })
        })

        this.events = events
      } finally {
        this.isLoading = false
      }
    },
    showEvent({ event, nativeEvent }) {
      console.log(event.item)

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
  },
}
</script>
