<template>
  <v-container fluid>
    <Calendar v-model="date"></Calendar>
  </v-container>
</template>

<script>
import Calendar from '@/components/Calendar.vue'
import moment from 'moment'

export default {
  components: {
    Calendar,
  },
  data() {
    return {
      date: moment().format('yyyy-MM-DD'),
    }
  },
  watch: {
    date(value) {
      if (this.$route.query.date !== value) {
        this.$router.push({
          ...this.$route,
          query: { date: value },
        })
      }
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.setDateFromQuery({ route: to })
    next()
  },
  created() {
    this.setDateFromQuery()
  },
  methods: {
    setDateFromQuery({ route = this.$route } = {}) {
      this.date = route.query.date
    },
  },
}
</script>
