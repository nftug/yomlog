import { render, fireEvent } from '@testing-library/vue'
import Component from '@/App.vue'

import store from '@/store'
import router from '@/router'

import Vuetify from 'vuetify'

describe('render App', () => {
  let vuetify, wrapper

  beforeEach(() => {
    vuetify = new Vuetify()
    wrapper = render(Component, { store, router, vuetify })
  })

  test('マウントと環境引数のテスト', () => {
    const { getAllByText } = wrapper
    getAllByText('YomLog')
  })

  test('ログインのテスト', async () => {
    const { getByRole, getByLabelText, getByText } = wrapper

    const loginButton = getByRole('button', { name: 'login' })
    const usernameInput = getByLabelText(/ユーザー名/i)
    const passwordInput = getByLabelText(/パスワード/i)

    await fireEvent.update(usernameInput, 'admin')
    await fireEvent.update(passwordInput, 'test1234')
    await fireEvent.click(loginButton)

    await new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, 1000)
    })

    getByText('ログインしました。')
  })
})
