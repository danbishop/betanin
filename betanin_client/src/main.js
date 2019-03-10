/* eslint-disable import/first */

// vue
import Vue from 'vue'
Vue.config.productionTip = false

// betanin
import App from '@/views/App.vue'
import router from '@/router'
import store from '@/store/main'
import { SOCKET_URL } from '@/constants'
import './filters'

// buefy
import Buefy from 'buefy'
import '@mdi/font/css/materialdesignicons.css'
Vue.use(
  Buefy,
  {
    defaultIconPack: 'mdi',
    defaultContainerElement: 'app'
  }
)

// socketio
import VueSocketio from 'vue-socket.io-extended'
import IO from 'socket.io-client'
Vue.use(
  VueSocketio,
  IO(SOCKET_URL),
  {
    store,
    actionPrefix: 'doSocket__',
    mutationPrefix: 'SOCKET__'
  }
)

// vee
import VeeValidate, { Validator } from 'vee-validate'
Vue.use(VeeValidate)
Validator.localize('en', {
  custom: {
    protocol: {
      required: 'protocol required'
    },
    notProtocol: {
      required: 'url required'
    }
  }
})

// chat-scroll
import VueChatScroll from 'vue-chat-scroll'
Vue.use(VueChatScroll)

// start
const view = new Vue({
  router,
  store,
  render: h => h(App)
})
view.$mount('#app')
