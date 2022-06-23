<template>
  <div  v-loading="loading">
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">基本信息</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle="labelStyle">
      <el-descriptions-item label="所属云" >OpenStack</el-descriptions-item>
      <el-descriptions-item label="实例ID" >{{instanceId}}</el-descriptions-item>
      <el-descriptions-item label="状态" >{{status}}</el-descriptions-item>
      <el-descriptions-item label="项目ID" >{{projectId}}</el-descriptions-item>
      <el-descriptions-item label="创建时间" >{{createdTime}}</el-descriptions-item>
      <el-descriptions-item label="所在可用区" >{{availabilityZone}}</el-descriptions-item>
      <el-descriptions-item label="密钥对" >{{keyPairName}}</el-descriptions-item>
      <el-descriptions-item label="安全组" >
        <span v-for="sg in securityGroups">{{sg["name"]}} </span>
      </el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">规格</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle="labelStyle">
      <el-descriptions-item label="实例类型名称" >{{flavor.name}}</el-descriptions-item>
      <el-descriptions-item label="实例类型ID" >{{flavor.id}}</el-descriptions-item>
      <el-descriptions-item label="CPU&内存" >{{flavor.cpu}}核（vCPU）{{flavor.ram}}GiB</el-descriptions-item>
      <el-descriptions-item label="硬盘大小" >{{flavor.disk}}GiB</el-descriptions-item>
      <el-descriptions-item label="镜像名称" >{{image.name}}</el-descriptions-item>
      <el-descriptions-item label="镜像ID" >{{image.id}}</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">网络信息</div>
    <el-descriptions v-for="(value, key) in IPAddress" style="margin: 20px" :column=2 :labelStyle="labelStyle" border>
      <el-descriptions-item label="专有网络" >{{key}}</el-descriptions-item>
      <el-descriptions-item label="IP" >
        <span v-for="ip in value">
          <span v-if="ip.type === 'fixed'">{{ip.address}}（私有） </span>
          <span v-else>{{ip.address}}（浮动） </span>
        </span>
      </el-descriptions-item>
    </el-descriptions>
  </div>

</template>

<script>
  export default {
    name: "openstackInstanceDetail",
    data() {
      return {
        cloudId: "openstack",
        instanceId: "",
        instanceName: "",
        projectId: "",
        status: "",
        createdTime: "",
        availabilityZone: "",
        keyPairName: "",
        securityGroups: [],
        image: {
          id: "",
          name: ""
        },
        flavor: {
          id: "",
          name: "",
          ram: "",
          disk: "",
          cpu: "",
        },
        IPAddress: {},
        labelStyle : {
          fontWeight : "bold",
          width : "100px"
        },
        loading: true,
      }
    },
    created() {
      this.instanceId = this.$route.params.id
      this.getInstanceDetails()
    },
    mounted(){
    },
    methods: {
      getInstanceDetails(){
        this.loading = true
        let url = '/v1/' + this.cloudId + '/instances/' + this.instanceId
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
            let instance = res.data.data
            this.instanceName = instance["name"]
            this.projectId = instance["tenant_id"]
            switch (instance["status"]){
              case "building":
                this.status = "创建中"
                break
              case "running":
                this.status = "运行中"
                break
              case "starting":
                this.status = "启动中"
                break
              case "stopping":
                this.status = "停止中"
                break
              case "stopped":
                this.status = "已停止"
                break
              default:
                this.status = "错误"
            }
            let time = new Date(instance["created"])
            this.createdTime = time.getFullYear() + "年" + (time.getMonth() + 1) + "月" +
                time.getDate() + "日 " + time.toLocaleTimeString()
            this.availabilityZone = instance["OS-EXT-AZ:availability_zone"]
            this.keyPairName = instance["key_name"]
            this.securityGroups = instance["security_groups"]
            this.image.id = instance["image"]["id"]
            this.image.name = instance["image"]["name"]
            this.flavor.id = instance["flavor"]["id"]
            this.flavor.name = instance["flavor"]["name"]
            this.flavor.ram = (parseInt(instance["flavor"]["ram"]) / 1024).toString()
            this.flavor.disk = instance["flavor"]["disk"]
            this.flavor.cpu = instance["flavor"]["vcpus"]
            let addresses = instance["addresses"]
            for (let key in addresses){
              let ips = []
              for (let i in addresses[key]){
                let ip = {
                  address: addresses[key][i]["addr"],
                  type: addresses[key][i]["OS-EXT-IPS:type"]
                }
                ips.push(ip)
              }
              this.IPAddress[key] = ips
            }
          }
          else this.$message.error(res.data.msg)
          this.setBreadcrumb()
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.setBreadcrumb()
          this.loading = false
        });
      },
      setBreadcrumb(){
        this.$emit("change", [
          {
            item: "计算管理",
            path: ""
          },
          {
            item: "实例",
            path: "/compute/instances"
          },
          {
            item: this.instanceName,
            path: ""
          },
        ])
      }
    }
  }
</script>
<style scoped>
</style>
