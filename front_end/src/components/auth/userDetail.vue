<template>
  <div>
    <el-descriptions v-loading="loading" style="margin: 40px" :column=1 :labelStyle=label_style>
      <el-descriptions-item label="用户名" >{{userName}}</el-descriptions-item>
      <el-descriptions-item label="ID">{{userId}}</el-descriptions-item>
      <el-descriptions-item label="所属域名称">{{domainName}}</el-descriptions-item>
      <el-descriptions-item label="所属域ID">{{domainId}}</el-descriptions-item>
      <el-descriptions-item label="所属项目名称">{{projectName}}</el-descriptions-item>
      <el-descriptions-item label="所属项目ID">{{projectId}}</el-descriptions-item>
      <el-descriptions-item label="阿里云accessKey ID"><el-tag type="info" effect="plain">{{aliyun.access_key.id}}</el-tag></el-descriptions-item>
      <el-descriptions-item label="阿里云Region ID"><el-tag type="info" effect="plain">{{aliyun.region_id}}</el-tag></el-descriptions-item>
    </el-descriptions>
  </div>

</template>

<script>
  export default {
    name: "userDetail",
    data() {
      return {
        userName : sessionStorage.getItem("userName"),
        userId : sessionStorage.getItem("userId"),
        domainName: sessionStorage.getItem("domainName"),
        domainId: sessionStorage.getItem("domainId"),
        projectName: sessionStorage.getItem("projectName"),
        projectId: sessionStorage.getItem("projectId"),
        aliyun: {
          access_key : {
            id : ""
          },
          region_id : ""
        },
        label_style : {
          fontWeight : "bold",
          width : "150px"
        },
        loading: true,
      }
    },
    created() {
      this.get_access_key()
      this.$emit("change", [
        {
          item: "鉴权管理",
          path: ""
        },
        {
          item: "个人信息",
          path: ""
        },
      ])
    },
    mounted(){
    },
    methods: {
      get_access_key(){
        this.loading = true
        let url = '/v1/auth/access-keys'
        let that = this
        this.axios.get(url,{
          headers: {
            token : sessionStorage.getItem("token")
          }
        }).then(res => {
          if(res.data.code === 401){
            this.$message.error("身份验证过期，请重新登录")
            sessionStorage.removeItem("token");
            this.$router.push("/login")
          }
          else if(res.data.code === 200){
            if (res.data.data)
              this.aliyun = res.data.data.aliyun
          }
          else this.$message.error(res.data.msg)
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.loading = false
        });
      },
    }
  }
</script>
<style scoped>
</style>
