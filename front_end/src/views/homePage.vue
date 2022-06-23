<template>
  <div class="MainPage">
    <el-container>
      <el-header style="height: 50px; background: rgb(235,235,235)" >
        <div style="display: inline-block">
          <el-image
            style="width: 40px; height: 40px; top: 5px"
            :src= "logoUrl"
            fit= "fill">
          </el-image>
        </div>
        <div style="position: absolute; left: 80px; top: 10px; font-size: 20px; height: 50px; line-height: 50px">混合云计算平台</div>
        <el-dropdown trigger="click" style="position: absolute; right: 20px; height: 50px">
          <div class="circular" style="display: inline-block; cursor: pointer; text-align: center; font-size: 20px; margin: 10px">
            <i class="el-icon-user-solid"></i> <span slot="title">{{user.userName}}</span> <i class="el-icon-caret-bottom"></i>
          </div>
          <el-dropdown-menu slot="dropdown" >
            <el-dropdown-item @click.native="showPersonalInfo">查看个人信息</el-dropdown-item>
            <el-dropdown-item @click.native="modifyPersonalInfo">更改个人信息</el-dropdown-item>
            <el-dropdown-item @click.native="signOut">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </el-header>
      <el-container>
        <el-aside style="max-width: 200px; min-height: 800px">
          <el-menu default-active="" :default-openeds="menuOpen" class="el-menu-vertical" @select="handleSelect"
                   text-color="#000"  active-text-color="#ffd04bz" >
            <el-submenu index="1">
              <template slot="title"><i class="el-icon-monitor"></i><span slot="title">计算管理</span></template>
              <el-menu-item index="1-1">实例</el-menu-item>
              <el-menu-item index="1-2">密钥对</el-menu-item>
            </el-submenu>
            <el-submenu index="2">
              <template slot="title"><i class="el-icon-cloudy"></i><span slot="title">网络管理</span></template>
              <el-menu-item index="2-1">专有网络</el-menu-item>
              <el-menu-item index="2-2">路由</el-menu-item>
              <el-menu-item index="2-3">安全组</el-menu-item>
            </el-submenu>
            <el-submenu index="3">
              <template slot="title"><i class="el-icon-user"></i><span slot="title">鉴权管理</span></template>
              <el-menu-item index="3-1">个人信息</el-menu-item>
              <el-menu-item index="3-2">更改信息</el-menu-item>
            </el-submenu>
          </el-menu>
        </el-aside>
        <!--右侧主体部分-->
        <el-main style="width: 80% ">
          <div>
            <el-breadcrumb separator="/" class="breadcrumb-inner">
              <el-breadcrumb-item>{{breadcrumbItems[0]["item"]}}</el-breadcrumb-item>
              <el-breadcrumb-item v-if="breadcrumbItems[1]" :to="{path: breadcrumbItems[1]['path']}">{{breadcrumbItems[1]["item"]}}</el-breadcrumb-item>
              <el-breadcrumb-item v-for="item in breadcrumbItems.slice(2)">{{item["item"]}}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div v-if="breadcrumbItems.length === 2" style="margin-top: 40px; font-size: 30px">{{breadcrumbItems[1]["item"]}}</div>
          <div v-else-if="breadcrumbItems.length > 2" style="margin-top: 50px">
            <el-page-header title="" @back="goBack(breadcrumbItems[1]['path'])" :content="breadcrumbItems[2]['item']"></el-page-header>
          </div>
          <div>
            <!--右侧主题内容-->
            <transition name="el-fade-in">
              <router-view  @change="setBreadcrumb"></router-view>
            </transition>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapMutations}  from "vuex";
export default {
  name: "home",
  data() {
    return {
      user: {
        userId:  sessionStorage.getItem("userId"),
        userName:  sessionStorage.getItem("userName"),
        domainId: sessionStorage.getItem("domainId"),
        domainName: sessionStorage.getItem("domainName"),
        projectId: sessionStorage.getItem("projectId"),
        projectName: sessionStorage.getItem("projectName"),
        token: sessionStorage.getItem("token"),
      },
      logoUrl: "/image/logo.svg",
      breadcrumbItems: [
        {
          item : "",
          path : ""
        },
      ],
      menuObject:{
        1 : {
          menuName:"计算管理",
          menuItems:{
            1:"实例",
            2:"密钥对"
          }
        },
        2 : {
          menuName:"网络管理",
          menuItems:{
            1:"专有网络",
            2:"路由",
            3:"安全组",
          }
        },
        3 : {
          menuName:"鉴权管理",
          menuItems:{
            1:"个人信息",
            2:"更改信息",
          }
        }
      },
      menuOpen: ["1", "2", "3"]
    }
  },
  methods:{
    ...mapMutations(['updateUserStatus']),
    showPersonalInfo() {
      this.$router.push("/user/detail")
    },
    modifyPersonalInfo() {
      this.$router.push("/user/modify")
    },
    signOut() {
      let user = null
      this.updateUserStatus(user)
      this.$message({message: "退出成功！", type: "success"})
      this.$router.push("/login")
    },
    async setBreadcrumb(value){
      this.breadcrumbItems = value
    },
    goBack(path){
      this.$router.push(path)
    },
    handleSelect(key) {
      switch (key) {
        case '1-1':
          this.$router.push('/compute/instances');
          break;
        case '1-2':
          this.$router.push('/compute/key-pairs')
          break;
        case '2-1':
          this.$router.push('/network/vpcs')
          break;
        case '2-2':
          this.$router.push('/network/routers')
          break;
        case '2-3':
          this.$router.push('/network/security-groups')
          break;
        case '3-1':
          this.$router.push('/user/detail')
          break;
        case '3-2':
          this.$router.push('/user/modify')
          break;
      }
    }
  },
  created(){
  },
  mounted(){
  },

}
</script>

<style>
.el-page-header__content {
  font-size: 30px !important;
}
</style>

<style scoped>

.MainPage {
  height: 95vh;
}

.el-submenu .el-menu-item{
  min-width: 180px;
}

.breadcrumb-inner {
  width: 600px;
  float: left;
  font-size: 16px;
  padding: 5px;
}
</style>
