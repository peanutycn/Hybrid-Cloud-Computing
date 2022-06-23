import Vue from 'vue';
import Vuex from 'vuex';
Vue.use(Vuex);
//使用方法this.$store
const state={//要设置的全局访问的state对象
  token: sessionStorage.getItem('token') ? sessionStorage.getItem('token') : '',
  currentUser: {
    userId: "",
    userName: "",
    domainId: "",
    domainName: "",
    projectId: "",
    projectName: ""
  },
};


const getters = {
  token: state => state.token,
};

/* this.$store.commit('show') 或 this.$store.commit('hide') 以及 this.$store.commit('newNum',6) */
const mutations = {
  updateUserStatus(state, user) {
    if (user) {
      state.currentUser = user
      sessionStorage.setItem("userId",user.userId)
      sessionStorage.setItem("userName",user.userName)
      sessionStorage.setItem("domainId",user.domainId)
      sessionStorage.setItem("domainName",user.domainName)
      sessionStorage.setItem("projectId",user.projectId)
      sessionStorage.setItem("projectName",user.projectName)
      sessionStorage.setItem('token', user.token);
    }
    else if (user == null){
      state.currentUser = user
      sessionStorage.removeItem("userId")
      sessionStorage.removeItem("userName")
      sessionStorage.removeItem("domainId")
      sessionStorage.removeItem("domainName")
      sessionStorage.removeItem("projectId")
      sessionStorage.removeItem("projectName")
      sessionStorage.removeItem("token");
    }
  },
};



//把对象扔里面
const store = new Vuex.Store({
  state,
  getters,
  mutations,
});

export default store;
