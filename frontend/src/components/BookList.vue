<template>
  <div id="book-list">
    <v-row v-if="items.length">
      <v-col v-for="item in items" :key="item.id" cols="12" md="6" xl="4">
        <v-card class="mx-auto">
          <v-card-text>
            <v-list-item two-line>
              <slot name="header" :item="item">
                <v-list-item-content>
                  <v-list-item-title class="font-weight-medium">
                    <router-link
                      v-if="detailLink"
                      :to="`/book/detail/${item.id}`"
                      class="black--text"
                    >
                      {{ item.title }}
                    </router-link>
                    <template v-else>
                      {{ item.title }}
                    </template>
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <span v-for="(author, index) in item.authors" :key="index">
                      <router-link
                        :to="`/shelf/all/?authors=${author}`"
                        v-text="author"
                      ></router-link>
                      <span
                        v-if="index + 1 < item.authors.length"
                        v-text="', '"
                      ></span>
                    </span>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </slot>
            </v-list-item>

            <v-row no-gutters>
              <v-col cols="8">
                <slot name="content" :item="item"></slot>
              </v-col>

              <v-col cols="4">
                <router-link v-if="detailLink" :to="`/book/detail/${item.id}`">
                  <v-img
                    contain
                    :src="item.thumbnail || noImage"
                    max-height="185"
                    min-height="185"
                  ></v-img>
                </router-link>
                <template v-else>
                  <v-img
                    contain
                    :src="item.thumbnail || noImage"
                    max-height="185"
                    min-height="185"
                  ></v-img>
                </template>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <div v-else-if="!loading" class="text-center text-body-2">
      <p class="mt-4 mb-5">データが見つかりません</p>
    </div>
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
    loading: {
      type: Boolean,
      default: false,
    },
    detailLink: {
      type: Boolean,
      default: false,
    },
  },
}
</script>
