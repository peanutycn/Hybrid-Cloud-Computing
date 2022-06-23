<template>
  <div  v-loading="loading">
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">基本信息</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle="labelStyle">
      <el-descriptions-item label="所属云" >阿里云</el-descriptions-item>
      <el-descriptions-item label="实例ID" >{{instanceId}}</el-descriptions-item>
      <el-descriptions-item label="状态" >{{status}}</el-descriptions-item>
      <el-descriptions-item label="资源组ID" >{{resourceGroupId}}</el-descriptions-item>
      <el-descriptions-item label="创建时间" >{{createdTime}}</el-descriptions-item>
      <el-descriptions-item label="所在可用区" >{{availabilityZone}}</el-descriptions-item>
      <el-descriptions-item label="主机名" >{{hostName}}</el-descriptions-item>
      <el-descriptions-item label="地域ID" >{{regionId}}</el-descriptions-item>
      <el-descriptions-item label="密钥对" >{{keyPairName}}</el-descriptions-item>
      <el-descriptions-item label="安全组" >
        <span v-for="sg in securityGroups">{{sg}} </span>
      </el-descriptions-item>
      <el-descriptions-item label="描述" >{{description}}</el-descriptions-item>
      <el-descriptions-item label="自动释放时间" >{{autoReleaseTime}}</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">规格</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle="labelStyle">
      <el-descriptions-item label="实例类型名称" >{{flavor.name}}</el-descriptions-item>
      <el-descriptions-item label="实例规格族" >{{flavor.family}}</el-descriptions-item>
      <el-descriptions-item label="CPU&内存" >{{flavor.cpu}}核（vCPU）{{flavor.ram}}GiB</el-descriptions-item>
      <el-descriptions-item label="镜像ID" >{{image.id}}</el-descriptions-item>
      <el-descriptions-item label="系统名称" >{{image.osName}}</el-descriptions-item>
      <el-descriptions-item label="当前带宽大小" >{{bandwidth}}Mbps（峰值）</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">网络信息</div>
    <el-descriptions v-if="publicIpAddress" style="margin: 20px" :column=1 :labelStyle="labelStyle" border>
      <el-descriptions-item label="公网IP" >
        <span v-for="ip in publicIpAddress">{{ip}} </span>
      </el-descriptions-item>
    </el-descriptions>
    <el-descriptions v-if="privateIpAddress" style="margin: 20px" :column=3 :labelStyle="labelStyle" :content-style="contentStyle" border>
      <el-descriptions-item label="专有网络" >{{vpcId}}</el-descriptions-item>
      <el-descriptions-item label="虚拟交换机" >{{vSwitchId}}</el-descriptions-item>
      <el-descriptions-item label="IP" >
        <span v-for="ip in privateIpAddress">{{ip}} </span>
      </el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">付费信息</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle=labelStyle>
      <el-descriptions-item label="实例计费方式" >{{instanceChargeType}}</el-descriptions-item>
      <el-descriptions-item label="带宽计费方式" >{{internetChargeType}}</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">其他信息</div>
    <el-descriptions style="margin: 20px" :column=2 :labelStyle=labelStyle>
      <el-descriptions-item label="释放保护" >{{deletionProtection}}</el-descriptions-item>
      <el-descriptions-item label="停机模式" >{{stoppedMode}}</el-descriptions-item>
    </el-descriptions>
  </div>

</template>

<script>
  export default {
    name: "aliyunInstanceDetail",
    data() {
      return {
        cloudId: "aliyun",
        instanceId: "",
        instanceName: "",
        status: "",
        resourceGroupId: "",
        createdTime: "",
        availabilityZone: "",
        hostName: "",
        regionId: "",
        keyPairName: "",
        securityGroups: [],
        description: "",
        autoReleaseTime: "",
        flavor: {
          name: "",
          family: "",
          ram: "",
          cpu: "",
        },
        image: {
          id: "",
          osName: ""
        },
        bandwidth: "",
        publicIpAddress : [],
        privateIpAddress: [],
        vpcId: "",
        vSwitchId: "",
        instanceChargeType: "",
        internetChargeType: "",
        deletionProtection: "",
        stoppedMode: "",
        labelStyle: {
          fontWeight : "bold",
          width : "100px"
        },
        contentStyle: {
          minWidth: "200px"
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
            this.instanceName = instance["InstanceName"]
            switch (instance["Status"]){
              case "Building":
                this.status = "创建中"
                break
              case "Running":
                this.status = "运行中"
                break
              case "Starting":
                this.status = "启动中"
                break
              case "Stopping":
                this.status = "停止中"
                break
              case "Stopped":
                this.status = "已停止"
                break
              default:
                this.status = "错误"
            }
            this.resourceGroupId = instance["ResourceGroupId"]
            let time = new Date(instance["CreationTime"])
            this.createdTime = time.getFullYear() + "年" + (time.getMonth() + 1) + "月" +
                time.getDate() + "日 " + time.toLocaleTimeString()
            this.availabilityZone = instance["ZoneId"]
            this.hostName = instance["HostName"]
            this.regionId = instance["RegionId"]
            this.keyPairName = instance["KeyPairName"]
            this.securityGroups = instance["SecurityGroupIds"]["SecurityGroupId"]
            this.description = instance["Description"]
            if (instance["autoReleaseTime"]){
              let time = new Date(instance["AutoReleaseTime"])
              this.autoReleaseTime = time.getFullYear() + "年" + (time.getMonth() + 1) + "月" +
                  time.getDate() + "日 " + time.toLocaleTimeString()
            }
            this.image.id = instance["ImageId"]
            this.image.osName = instance["OSName"]
            this.flavor.name = instance["InstanceType"]
            this.flavor.family = instance["InstanceTypeFamily"]
            this.flavor.ram = (parseInt(instance["Memory"]) / 1024).toString()
            this.flavor.cpu = instance["Cpu"]
            this.bandwidth = instance["InternetMaxBandwidthOut"]
            this.publicIpAddress = instance["PublicIpAddress"]["IpAddress"]
            this.privateIpAddress = instance["VpcAttributes"]["PrivateIpAddress"]["IpAddress"]
            this.vpcId = instance["VpcAttributes"]["VpcId"]
            this.vSwitchId = instance["VpcAttributes"]["VSwitchId"]
            switch (instance["InstanceChargeType"]) {
              case "PostPaid":
                this.instanceChargeType = "按量"
                break
              case "PrePaid":
                this.instanceChargeType = "包年包月"
                break
            }
            switch (instance["InternetChargeType"]) {
              case "PayByBandwidth":
                this.internetChargeType = "按固定带宽"
                break
              case "PayByTraffic":
                this.internetChargeType = "按使用流量"
                break
            }
            switch (instance["DeletionProtection"]) {
              case true:
                this.deletionProtection = "已开启"
                break
              case false:
                this.deletionProtection = "未开启"
                break
            }
            switch (instance["StoppedMode"]) {
              case "KeepCharging":
                this.stoppedMode = "普通停机模式"
                break
              case "StopCharging":
                this.stoppedMode = "节省停机模式"
                break
              case "Not-applicable":
                this.stoppedMode = "暂未停机"
                break
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
