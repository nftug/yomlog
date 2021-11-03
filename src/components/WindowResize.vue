<script>
export default {
  props: {
    value: Number,
  },
  computed: {
    size: {
      get() {
        return this.value
      },
      set(val) {
        this.$emit('input', val)
      },
    },
  },
  created() {
    this.onWindowResize()
    window.addEventListener('resize', this.onWindowResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
  },
  methods: {
    onWindowResize: function () {
      this.size = window.innerWidth
    },
  },
}
</script>
