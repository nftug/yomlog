<script>
import { Doughnut } from 'vue-chartjs'

export default {
  extends: Doughnut,
  props: {
    data: {
      type: Object,
      require: true,
    },
    options: {
      type: Object,
      default: () => ({
        responsive: true,
      }),
    },
    width: {
      type: Number,
      require: false,
    },
    height: {
      type: Number,
      require: false,
    },
  },
  mounted() {
    if (process.env.NODE_ENV !== 'test') {
      this.renderChart(this.data, this.options)
    }
  },
}
</script>
