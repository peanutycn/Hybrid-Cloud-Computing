import Vue from 'vue';
import VueRouter from 'vue-router';
import login from "../views/loginPage";
import home from "../views/homePage"
import instanceList from "../components/compute/instance/instanceList";
import openstackInstanceDetail from "../components/compute/instance/openstackInstanceDetail";
import aliyunInstanceDetail from "../components/compute/instance/aliyunInstanceDetail";
import openstackInstanceCreate from "../components/compute/instance/openstackInstanceCreate";
import aliyunInstanceCreate from "../components/compute/instance/aliyunInstanceCreate";
import keyPairList from "../components/compute/keyPair/keyPairList";
import VPCList from "../components/network/VPC/VPCList";
import VPCDetail from "../components/network/VPC/VPCDetail";
import VPCCreate from "../components/network/VPC/VPCCreate";
import routerList from "../components/network/router/routerList";
import securityGroupList from "../components/network/securityGroup/securityGroupList";
import userDetail from "../components/auth/userDetail";
import userModify from "../components/auth/userModify";
Vue.use(VueRouter)

const originalPush = VueRouter.prototype.push
//修改原型对象中的push方法
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
}

const routes = [
  {
    path: '/login',
    name: 'login',
    component: login,
  },
  {
    path:'/',
    name: 'home',
    component: home,
    children:[
      {
        path:'/compute/instances',
        name:'instanceList',
        component:instanceList
      },
      {
        path:'/compute/instances/openstack/:id',
        name:'openstackInstanceDetail',
        component:openstackInstanceDetail
      },
      {
        path:'/compute/instances/aliyun/:id',
        name:'aliyunInstanceDetail',
        component:aliyunInstanceDetail
      },
      {
        path:'/compute/instances/new/openstack',
        name:'openstackInstanceCreate',
        component:openstackInstanceCreate
      },
      {
        path:'/compute/instances/new/aliyun',
        name:'aliyunInstanceCreate',
        component:aliyunInstanceCreate
      },
      {
        path:'/compute/key-pairs',
        name:'keyPairList',
        component:keyPairList
      },
      {
        path:'/network/vpcs',
        name:'VPCList',
        component:VPCList
      },
      {
        path:'/network/vpcs/details/:id',
        name:'VPCDetail',
        component:VPCDetail
      },
      {
        path:'/network/vpcs/new',
        name:'VPCCreate',
        component:VPCCreate
      },
      {
        path:'/network/routers',
        name:'routerList',
        component:routerList
      },
      {
        path:'/network/security-groups',
        name:'securityGroupList',
        component:securityGroupList
      },
      {
        path:'/user/detail',
        name:'userDetail',
        component:userDetail
      },
      {
        path:'/user/modify',
        name:'userModify',
        component:userModify
      },
    ]
  },
  {
    path: '*',
    redirect: '/login'
  },


]

const router = new VueRouter({
  base:'',
  mode:'history',
  routes
})


router.beforeEach((to, from, next) => {
  if (to.path === '/login') {
    next();
  } else {
    let token = sessionStorage.getItem('token');
    if (token === null || token === '') {
      sessionStorage.removeItem("token");
      next('/login');
    } else {
      next();
    }
  }
});
export default router
