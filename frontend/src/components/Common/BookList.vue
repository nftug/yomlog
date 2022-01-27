<template>
  <div id="book-list">
    <v-row v-if="books.length">
      <v-col v-for="book in books" :key="book.id" cols="12" md="6" xl="4">
        <v-card class="mx-auto">
          <v-card-text>
            <v-list-item two-line>
              <slot name="header" :book="book">
                <v-list-item-content>
                  <v-list-item-title class="font-weight-medium">
                    <router-link
                      v-if="state"
                      :to="`/book/detail/${book.id}`"
                      class="black--text"
                    >
                      {{ book.title }}
                    </router-link>
                    <template v-else>
                      {{ book.title }}
                    </template>
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <span v-for="(author, index) in book.authors" :key="index">
                      <router-link
                        :to="`/shelf/all/?authors=${author}`"
                        v-text="author"
                      ></router-link>
                      <span
                        v-if="index + 1 < book.authors.length"
                        v-text="', '"
                      ></span>
                    </span>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </slot>
            </v-list-item>

            <v-row no-gutters>
              <v-col cols="8">
                <slot name="content" :book="book"></slot>
              </v-col>

              <v-col cols="4">
                <router-link v-if="state" :to="`/book/detail/${book.id}`">
                  <v-img
                    contain
                    :src="book.thumbnail"
                    max-height="185"
                    min-height="185"
                  ></v-img>
                </router-link>
                <template v-else>
                  <v-img
                    contain
                    :src="book.thumbnail"
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
      <p class="mt-4 mb-5">データが見つかりません。</p>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    books: {
      type: Array,
      required: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    state: {
      type: String,
      require: false,
    },
  },
}
</script>
