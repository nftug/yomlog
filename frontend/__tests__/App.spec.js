import { mount } from '@vue/test-utils'
import Component from '@/App.vue'

import store from '@/store'
import router from '@/router'

import Vuetify from 'vuetify'

describe('Testing App component', () => {
  let vuetify

  beforeEach(() => {
    vuetify = new Vuetify()
  })

  it('is a Vue instance', () => {
    const wrapper = mount(Component, { store, router, vuetify })
    expect(wrapper.isVueInstance).toBeTruthy()
  })
})
