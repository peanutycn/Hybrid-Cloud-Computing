<template>
  <div  v-loading="loading">
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">基本信息</div>
    <el-descriptions style="margin: 20px" :column=1 :labelStyle="labelStyle">
      <el-descriptions-item label="VPC ID" >{{VPCId}}</el-descriptions-item>
      <el-descriptions-item label="网段" >{{cidr}}</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">OpenStack网络信息</div>
    <el-descriptions style="margin: 20px" :column=1 :labelStyle="labelStyle">
      <el-descriptions-item label="网络ID" >{{subVPC.openstack.VPCId}}</el-descriptions-item>
      <el-descriptions-item label="网段" >{{subVPC.openstack.cidr}}</el-descriptions-item>
      <el-descriptions-item label="VPN ID" >
        <el-link type="primary" :href="'/compute/instances/openstack/' + subVPC.openstack.vpn.id">{{subVPC.openstack.vpn.id}}</el-link>
      </el-descriptions-item>
      <el-descriptions-item label="WireGuard密钥对公钥" >{{subVPC.openstack.keyPair.publicKey}}</el-descriptions-item>
    </el-descriptions>
    <el-divider></el-divider>
    <div style="font-size: 20px; display: inline-block">阿里云VPC信息</div>
    <el-descriptions style="margin: 20px" :column=1 :labelStyle="labelStyle">
      <el-descriptions-item label="VPC ID" >{{subVPC.aliyun.VPCId}}</el-descriptions-item>
      <el-descriptions-item label="网段" >{{subVPC.aliyun.cidr}}</el-descriptions-item>
      <el-descriptions-item label="VPN ID" >
        <el-link type="primary" :href="'/compute/instances/aliyun/' + subVPC.aliyun.vpn.id">{{subVPC.aliyun.vpn.id}}</el-link>
      </el-descriptions-item>
      <el-descriptions-item label="WireGuard密钥对公钥" >{{subVPC.aliyun.keyPair.publicKey}}</el-descriptions-item>
    </el-descriptions>
  </div>

</template>

<script>
  export default {
    name: "VPCDetail",
    data() {
      return {
        VPCId: "",
        VPCName: "",
        cidr: "",
        subVPC: {
          openstack: {
            cidr: "",
            vpn: {
              id: ""
            },
            keyPair: {
              publicKey: ""
            },
            VPCId: ""
          },
          aliyun: {
            cidr: "",
            vpn: {
              id: ""
            },
            keyPair: {
              publicKey: ""
            },
            VPCId: ""
          }
        },
        labelStyle: {
          fontWeight : "bold",
          width : "200px"
        },
        contentStyle: {
          minWidth: "200px"
        },
        loading: true,
      }
    },
    created() {
      this.VPCId = this.$route.params.id
      this.getVPCDetails()
    },
    mounted(){
    },
    methods: {
      getVPCDetails(){
        this.loading = true
        let url = '/v1/vpcs/' + this.VPCId
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
            let VPC = res.data.data
            this.VPCId = VPC["vpcId"]
            this.VPCName = VPC["vpcName"]
            this.cidr = VPC["cidr"]
            this.subVPC.openstack.cidr = VPC["subVpc"]["openstack"]["cidr"]
            this.subVPC.openstack.keyPair.publicKey = VPC["subVpc"]["openstack"]["key_pair"]["public_key"]
            this.subVPC.openstack.VPCId = VPC["subVpc"]["openstack"]["vpc_id"]
            this.subVPC.aliyun.cidr = VPC["subVpc"]["aliyun"]["cidr"]
            this.subVPC.aliyun.keyPair.publicKey = VPC["subVpc"]["aliyun"]["key_pair"]["public_key"]
            this.subVPC.aliyun.VPCId = VPC["subVpc"]["aliyun"]["vpc_id"]
            let vpnList = VPC["vpn"]
            for(let i in vpnList){
              if(vpnList[i]["cloudId"] === "openstack")
                this.subVPC.openstack.vpn.id = vpnList[i]["instanceId"]
              else if(vpnList[i]["cloudId"] === "aliyun")
                this.subVPC.aliyun.vpn.id = vpnList[i]["instanceId"]
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
            item: "网络管理",
            path: ""
          },
          {
            item: "专有网络",
            path: "/network/vpcs"
          },
          {
            item: this.VPCName,
            path: ""
          },
        ])
      },
    }
  }
</script>
<style>
</style>
<style scoped>
.el-button{
  padding: 0!important;
  line-height: 21px!important;
}
</style>
