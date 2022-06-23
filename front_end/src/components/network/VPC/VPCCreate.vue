<template>
  <div v-loading="loading">
    <el-divider></el-divider>
    <el-form ref = "VPCForm" :model = "VPCForm" :rules="rules" class = "container" label-position = "left" label-width = "200px">
      <div class = "formGroup">
        <div style="font-size: 20px">VPC设置</div>
        <el-form-item label = "VPC名称" prop="vpc.name">
          <el-input type = "text" class = "form-control" v-model="VPCForm.vpc.name"></el-input>
        </el-form-item>
        <el-form-item label = "CIDR地址块" prop="vpc.cidr">
          <el-input type = "text" class = "form-control" v-model="VPCForm.vpc.cidr"></el-input>
        </el-form-item>
        <el-form-item label = "OpenStack CIDR地址块" prop="vpc.openstackCidr">
          <el-input type = "text" class = "form-control" v-model="VPCForm.vpc.openstackCidr"></el-input>
        </el-form-item>
        <el-form-item label = "阿里云CIDR地址块" prop="vpc.aliyunCidr">
          <el-input type = "text" class = "form-control" v-model="VPCForm.vpc.aliyunCidr"></el-input>
        </el-form-item>

        <el-divider></el-divider>
         <div style="font-size: 20px; margin: 5px">OpenStack子网设置</div>
        <el-form-item label = "子网名称" prop="subnet.openstack.name">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.openstack.name"></el-input>
        </el-form-item>
        <el-form-item label = "子网CIDR地址块" prop="subnet.openstack.cidr">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.openstack.cidr"></el-input>
        </el-form-item>
        <el-form-item label = "网关地址" prop="subnet.openstack.gatewayIp">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.openstack.gatewayIp"></el-input>
        </el-form-item>
        <el-form-item label = "分配地址池" prop="subnet.openstack.allocation_pools">
          <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 4}" class = "form-control" v-model="VPCForm.subnet.openstack.allocation_pools"></el-input>
          <div style="margin-top: 10px">每条记录是：开始IP,结束IP(例如192.168.1.100,192.168.1.120)，每行一条记录</div>
        </el-form-item>
        <el-form-item label = "DNS域名服务器" prop="subnet.openstack.dnsNameservers">
          <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 4}" class = "form-control" v-model="VPCForm.subnet.openstack.dnsNameservers"></el-input>
          <div style="margin-top: 10px">每行一条记录</div>
        </el-form-item>

        <el-divider></el-divider>
         <div style="font-size: 20px; margin: 5px">阿里云子网设置</div>
        <el-form-item label = "交换机名称" prop="subnet.aliyun.vSwitchName">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.aliyun.vSwitchName"></el-input>
        </el-form-item>
        <el-form-item label = "交换机CIDR地址块" prop="subnet.aliyun.cidr">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.aliyun.cidr"></el-input>
        </el-form-item>
        <el-form-item label = "可用区" prop="subnet.aliyun.zoneId">
          <el-select class = "form-control" v-model="VPCForm.subnet.aliyun.zoneId">
            <el-option v-for="zone in parameters.zones" :label="zone.id" :value="zone.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "描述" prop="subnet.aliyun.description">
          <el-input type = "text" class = "form-control" v-model="VPCForm.subnet.aliyun.description"></el-input>
        </el-form-item>

        <el-divider></el-divider>
         <div style="font-size: 20px; margin: 5px">OpenStack VPN实例设置</div>
        <el-form-item label = "私有网络IP" prop="instance.openstack.networks.fixed_ip">
          <el-input type = "text" class = "form-control" v-model="VPCForm.instance.openstack.networks.fixed_ip"></el-input>
          <div style="margin-top: 10px">默认地址块第一个地址分配给DHCP端口</div>
        </el-form-item>

        <el-divider></el-divider>
         <div style="font-size: 20px; margin: 5px">阿里云 VPN实例设置</div>
        <el-form-item label = "付费模式" prop="instance.aliyun.instanceChargeType">
          <el-radio v-model="VPCForm.instance.aliyun.instanceChargeType" label="PrePaid">包年包月</el-radio>
          <el-radio v-model="VPCForm.instance.aliyun.instanceChargeType" label="PostPaid">按量付费</el-radio>
        </el-form-item>
        <el-form-item v-if="VPCForm.instance.aliyun.instanceChargeType==='PrePaid'" label = "购买时长" prop="instance.aliyun.period">
          <el-select class = "form-control" v-model="VPCForm.instance.aliyun.period">
            <el-option label="1个月" :value="1"></el-option>
            <el-option label="2个月" :value="2"></el-option>
            <el-option label="3个月" :value="3"></el-option>
            <el-option label="半年" :value="6"></el-option>
            <el-option label="1年" :value="12"></el-option>
            <el-option label="2年" :value="24"></el-option>
            <el-option label="3年" :value="36"></el-option>
            <el-option label="4年" :value="48"></el-option>
            <el-option label="5年" :value="60"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "私有网络IP" prop="instance.aliyun.privateIpAddress">
          <el-input type = "text" class = "form-control" v-model="VPCForm.instance.aliyun.privateIpAddress"></el-input>
        </el-form-item>
        <el-form-item label = "带宽" style="width: 600px" prop="instance.aliyun.internetMaxBandwidthOut">
          <el-slider v-model="VPCForm.instance.aliyun.internetMaxBandwidthOut" show-input></el-slider>
        </el-form-item>
      </div>
      <div class = "formButton">
        <el-form-item label-width = "0px">
          <el-button type = "primary" style = "width:100%;" @click="submit">确认创建</el-button>
        </el-form-item>
      </div>
    </el-form>
  </div>

</template>

<script>
  export default {
    name: "VPCCreate",
    data() {
      return {
        VPCForm: {
          vpc: {
            name: "",
            cidr: "",
            openstackCidr: "",
            aliyunCidr: ""
          },
          subnet: {
            openstack: {
              name: "",
              cidr: "",
              gatewayIp: "",
              allocation_pools: "",
              dnsNameservers: ""
            },
            aliyun: {
              vSwitchName: "",
              zoneId: "",
              cidr: "",
              description: ""
            }
          },
          instance: {
            openstack: {
              networks: {
                fixed_ip: ""
              }
            },
            aliyun: {
              instanceChargeType: "PrePaid",
              period: 1,
              privateIpAddress: "",
              internetMaxBandwidthOut: 1,
            }
          }
        },
        rules: {
          'vpc.name': [
            { required: true, message: '请输入VPC名称', trigger: 'blur' },
          ],
          'vpc.cidr': [
            { required: true, message: '请输入VPC CIDR地址', trigger: 'blur' },
          ],
          'vpc.openstackCidr': [
            { required: true, message: '请输入OpenStack CIDR地址', trigger: 'blur' },
          ],
          'vpc.aliyunCidr': [
            { required: true, message: '请输入阿里云 CIDR地址', trigger: 'blur' },
          ],
          'subnet.openstack.name': [
            { required: true, message: '请输入OpenStack子网名称', trigger: 'blur' },
          ],
          'subnet.openstack.cidr': [
            { required: true, message: '请输入OpenStack子网CIDR地址', trigger: 'blur' },
          ],
          'subnet.openstack.gatewayIp': [
            { required: true, message: '请输入OpenStack子网网关IP', trigger: 'blur' },
          ],
          'subnet.aliyun.vSwitchName': [
            { required: true, message: '请输入阿里云交换机名称', trigger: 'blur' },
          ],
          'subnet.aliyun.cidr': [
            { required: true, message: '请输入阿里云交换机CIDR地址块', trigger: 'blur' },
          ],
          'subnet.aliyun.zoneId': [
            { required: true, message: '请选择可用区', trigger: 'change' }
          ],
          'instance.openstack.networks.fixed_ip': [
            { required: true, message: '请输入OpenStack VPN IP', trigger: 'blur' },
          ],
          'instance.aliyun.privateIpAddress': [
            { required: true, message: '请输入阿里云 VPN IP', trigger: 'blur' },
          ],
        },
        parameters: {
          zones: [{
            id: ""
          }],
        },
        loading: false
      }
    },
    created() {
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
          item: "创建VPC",
          path: ""
        }
      ])
      this.getCreateParameters()
    },
    mounted(){
    },
    methods: {
      getCreateParameters(){
        this.parameters = {}
        this.loading = true
        let url = '/v1/vpcs/create'
        let that = this
        this.axios.get(url, {
          headers: {
            token : sessionStorage.getItem("token")
          },
          timeout: 1000*60*5
        }).then(res => {
          if(res.data.code === 401){
            this.$message.error("身份验证过期，请重新登录")
            sessionStorage.removeItem("token");
            this.$router.push("/login")
          }
          else if(res.data.code === 200){
            this.parameters = res.data.data
          }
          else this.$message.error(res.data.msg)
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.loading = false
        });
      },
      createVPC() {
        this.loading = true
        let url = '/v1/vpcs'
        let vpc = {
          name: this.VPCForm.vpc.name,
          cidr: this.VPCForm.vpc.cidr,
          sub_vpc: {
            openstack: {
              cidr: this.VPCForm.vpc.openstackCidr
            },
            aliyun: {
              cidr: this.VPCForm.vpc.aliyunCidr
            },
          }
        }
        let subnet = {
          openstack: {
            name: this.VPCForm.subnet.openstack.name,
            cidr: this.VPCForm.subnet.openstack.cidr,
            gateway_ip: this.VPCForm.subnet.openstack.gatewayIp,
          },
          aliyun: {
            VSwitchName: this.VPCForm.subnet.aliyun.vSwitchName,
            ZoneId: this.VPCForm.subnet.aliyun.zoneId,
            CidrBlock: this.VPCForm.subnet.aliyun.cidr,
            Description: this.VPCForm.subnet.aliyun.description
          }
        }
        if (this.VPCForm.subnet.openstack.allocation_pools.length !== 0){
          subnet.openstack["allocation_pools"] = []
          let str = this.VPCForm.subnet.openstack.allocation_pools
          let poolList=str.split(/[(\r\n)\r\n]+/);
          poolList.forEach((item,index)=>{
            if(!item){
              poolList.splice(index,1);
            }
          })
          for(let i in poolList){
            let pool = {
              start: poolList[i].split(',')[0],
              end: poolList[i].split(',')[1],
            }
            subnet.openstack["allocation_pools"].push(pool)
          }
        }
        if (this.VPCForm.subnet.openstack.dnsNameservers !== 0){
          let str = this.VPCForm.subnet.openstack.dnsNameservers
          subnet.openstack["dns_nameservers"] = str.split(/[(\r\n)\r\n]+/);
        }
        let instance = {
          openstack: this.VPCForm.instance.openstack,
          aliyun: {
            InstanceChargeType: this.VPCForm.instance.aliyun.instanceChargeType,
            PrivateIpAddress: this.VPCForm.instance.aliyun.privateIpAddress,
            InternetMaxBandwidthOut: this.VPCForm.instance.aliyun.internetMaxBandwidthOut,
          }
        }
        if (this.VPCForm.instance.aliyun.instanceChargeType === "PrePaid"){
          instance.aliyun["Period"] = this.VPCForm.instance.aliyun.period
        }
        let params = {
          "vpc": vpc,
          "subnet": subnet,
          "instance": instance
        }
        let that = this
        this.axios.post(url, params,{
          headers: {
            token : sessionStorage.getItem("token")
          }
        }).then(res => {
          if(res.data.code === 401){
            this.$message.error("身份验证过期，请重新登录")
            sessionStorage.removeItem("token");
            this.$router.push("/login")
          }
          else if(res.data.code === 403){
            this.$notify.error("创建VPC失败")
          }
          else if(res.data.code === 400){
            this.$notify.error("创建VPC失败，请检查参数")
          }
          else if(res.data.code === 200){
            this.$notify({title: "成功", message: "创建VPC成功", type: "success"});
            this.$router.push("/network/vpcs")
          }
          else this.$message.error(res.data.msg)
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.loading = false
        });
      },
      submit(){
        this.createVPC()
      }
    }
  }
</script>
<style scoped>

.container{
  margin: 20px;
}
.form-control{
  width:400px;
  flex: 1;
  -webkit-flex: 1;
  -ms-flex: 1;
}
.formGroup{
  margin-top: 20px;
}
.formButton{
  margin-top: 20px;
  margin-left: 500px;
  width: 100px;
}

</style>
