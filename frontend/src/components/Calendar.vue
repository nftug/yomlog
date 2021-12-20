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
      ></v-calendar>
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
    categories: { status: 'status', note: 'note' },
  }),
  computed: {
    title() {
      return moment(this.value).format('yyyy年 M月')
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
            color: 'blue',
            category: this.categories.status,
            item: item,
            timed: false,
          })
        })

        const { data: note } = await api.get('/note/', { params: params })
        note.forEach((item) => {
          events.push({
            name: `${item.book.title} (${item.position})`,
            start: new Date(item.created_at),
            color: 'green',
            category: this.categories.note,
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
    getEventColor(event) {
      return event.color
    },
    setToday() {
      this.value = moment().format('yyyy-MM-DD')
    },
  },
}
</script>
