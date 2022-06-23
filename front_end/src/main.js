import Vue from 'vue'
import App from './App.vue'
import router from './router'
import './plugins/element.js'
import axios from "axios";
import store from "./store/index.js";
import commonInfo from './common/util/commonInfo.vue'
import VueCookies  from 'vue-cookies'

Vue.use(VueCookies)
commonInfo.get_csrf_token()
Vue.config.productionTip = false
axios.defaults.headers = {
  'Content-type': 'application/json',
  'X-CSRFToken': VueCookies.get('csrftoken')
}
Vue.prototype.axios = axios
Vue.prototype.store = store
axios.defaults.baseURL = '/api'
Vue.directive('title', {
  inserted: function (el, binding) {
    document.title = el.dataset.title
  }
})

new Vue({
  router,
  store: store,
  components: {App},
  template: '<App/>',
  render: h => h(App)
}).$mount('#app')
