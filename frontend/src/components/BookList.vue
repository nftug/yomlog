<template>
  <div id="book-list">
    <v-row>
      <v-col v-for="item in items" :key="item.id" cols="12" md="6" lg="4">
        <v-card class="mx-auto" height="185">
          <v-row no-gutters>
            <v-col cols="8">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title
                    v-text="item.title"
                    class="font-weight-medium"
                  ></v-list-item-title>
                  <v-list-item-subtitle
                    v-text="item.authors.join(', ')"
                  ></v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>

              <slot name="actions" :item="item"></slot>
            </v-col>

            <v-col cols="4">
              <v-img
                contain
                :src="item.thumbnail || noImage"
                max-height="185"
                min-height="185"
              ></v-img>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      type: Array,
      required: true,
    },
    noImage: {
      type: String,
      default: 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=NoImage',
    },
  },
}
</script>
