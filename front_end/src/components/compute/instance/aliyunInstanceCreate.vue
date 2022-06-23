<template>
  <div v-loading="loading">
    <el-divider></el-divider>
    <el-form ref = "instanceForm" :model="instanceForm" :rules="rules" class = "container" label-position = "left" label-width = "100px">
      <div class = "formGroup">
        <el-form-item label = "付费模式" prop="instanceChargeType">
          <el-radio v-model="instanceForm.instanceChargeType" label="PrePaid">包年包月</el-radio>
          <el-radio v-model="instanceForm.instanceChargeType" label="PostPaid">按量付费</el-radio>
        </el-form-item>
        <el-form-item v-if="instanceForm.instanceChargeType==='PrePaid'" label = "购买时长" prop="period">
          <el-select class = "form-control" v-model="instanceForm.period">
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
        <el-form-item label = "实例类型" prop="instanceType">
          <el-select class = "form-control" v-model="instanceForm.instanceType">
            <el-option v-for="type in parameters.instanceTypes" :label="type.id" :value="type.id">
              <span style="float: left">{{type.id}}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{type.vcpus}}核（vCPU）{{type.ram}}GiB</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "镜像" prop="imageId">
          <el-select class = "form-control" v-model="instanceForm.imageId">
            <el-option v-for="image in parameters.images" :label="image.name" :value="image.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "系统盘种类" prop="systemDisk.category">
          <el-select class = "form-control" v-model="instanceForm.systemDisk.category">
            <el-option label="高效云盘" value="cloud_efficiency"></el-option>
            <el-option label="SSD云盘" value="cloud_ssd"></el-option>
            <el-option label="ESSD云盘" value="cloud_essd"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "系统盘大小" prop="systemDisk.size">
          <el-input-number v-model="instanceForm.systemDisk.size" :min="20" :max="500"></el-input-number>
        </el-form-item>
        <el-form-item label = "交换机" prop="vSwitch.vSwitchId">
          <el-select class = "form-control" v-model="instanceForm.vSwitch" value-key="vSwitchId" >
              <el-option v-for="vSwitch in parameters.vSwitchs" :key="vSwitch.vSwitchId" :label="vSwitch.vSwitchName" :value="vSwitch">
              <div style="float: left">{{vSwitch.vSwitchName}}</div>
              <div style="float: right; color: #8492a6; font-size: 13px">{{vSwitch.vpcId}}</div>
            </el-option>
          </el-select>
        </el-form-item>
        <div class="vSwitchLabel" v-if="instanceForm.vSwitch.vSwitchId!==''">
          交换机所在可用区：<span class="vSwitchValue">{{instanceForm.vSwitch.zoneId}}</span>
          交换机网段：<span class="vSwitchValue">{{instanceForm.vSwitch.cidrBlock}}</span>
        </div>
        <el-form-item label = "私有网络IP" prop="privateIpAddress">
          <el-input type = "text" class = "form-control" v-model="instanceForm.privateIpAddress"></el-input>
        </el-form-item>
        <el-form-item label = "安全组" prop="securityGroupId">
          <el-select class = "form-control" v-model="instanceForm.securityGroupId">
            <el-option v-for="securityGroup in parameters.securityGroups" v-if="securityGroup.vpcId === instanceForm.vSwitch.vpcId"
                       :label="securityGroup.name" :value="securityGroup.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "带宽" style="width: 500px" prop="internetMaxBandwidthOut">
          <el-slider v-model="instanceForm.internetMaxBandwidthOut" show-input :min="1" :max="100"></el-slider>
        </el-form-item>
        <el-form-item label = "登录凭证" prop="authMethod">
          <el-radio v-model="instanceForm.authMethod" label="keyPair">密钥对</el-radio>
          <el-radio v-model="instanceForm.authMethod" label="password">密码</el-radio>
        </el-form-item>
        <el-form-item v-if="instanceForm.authMethod==='keyPair'" label = "密钥对" prop="keyPairName">
          <el-select class = "form-control" v-model="instanceForm.keyPairName">
            <el-option v-for="keyPair in parameters.keyPairs" :label="keyPair.name" :value="keyPair.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-else label = "密码" prop="password">
          <el-input type = "text" class = "form-control" v-model="instanceForm.password"></el-input>
          <div style="margin-top: 10px">长度为8至30个字符，必须同时包含大小写英文字母、数字和特殊符号中的三类字符。</div>
        </el-form-item>
        <el-form-item label = "实例名称" prop="instanceName">
          <el-input type = "text" class = "form-control" v-model="instanceForm.instanceName"></el-input>
        </el-form-item>
        <el-form-item label = "描述" prop="description">
          <el-input type = "text" class = "form-control" v-model="instanceForm.description"></el-input>
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
    name: "aliyunInstanceCreate",
    data() {
      return {
        instanceForm: {
          instanceChargeType: "PrePaid",
          period: 1,
          instanceType: "",
          imageId: "",
          systemDisk: {
            size: "20",
            category: "cloud_efficiency"
          },
          vSwitch: {
            vpcId: "",
            vSwitchName: "",
            vSwitchId: "",
            zoneId: "",
            cidrBlock: ""
          },
          privateIpAddress: "",
          securityGroupId: "",
          internetMaxBandwidthOut: 1,
          authMethod: "keyPair",
          password: "",
          keyPairName: "",
          instanceName: "",
          description: "",
        },
        rules: {
          imageId: [
            { required: true, message: '请选择镜像', trigger: 'change' }
          ],
          instanceType: [
            { required: true, message: '请选择实例类型', trigger: 'change' }
          ],
          'vSwitch.vSwitchId': [
            { required: true, message: '请选择交换机', trigger: 'change' }
          ],
          securityGroupId: [
            { required: true, message: '请选择安全组', trigger: 'change' }
          ],
          keyPairName: [
            { required: true, message: '请选择密钥对', trigger: 'change' }
          ],
          password: [
            { required: true, message: '请输入密码', trigger: 'blur' },
          ],
          instanceName: [
            { required: true, message: '请输入实例名称', trigger: 'blur' },
          ],
        },
        parameters: {
          images: [{
            name: "",
            id: ""
          }],
          instanceTypes: [{
            id: "",
            vcpus: 0,
            ram: 0,
          }],
          vSwitchs: [{
            vpcId: "",
            vSwitchName: "",
            vSwitchId: "",
            zoneId: "",
            cidrBlock: ""
          }],
          securityGroups: [{
            vpcId: "",
            name: "",
            id: ""
          }],
          keyPairs: [{
            name: ""
          }],
        },
        loading: false
      }
    },
    created() {
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
          item: "创建实例",
          path: ""
        },
        {
          item: "阿里云",
          path: ""
        },
      ])
      this.getCreateParameters()
    },
    mounted(){
    },
    methods: {
      getCreateParameters(){
        this.parameters = {}
        this.loading = true
        let url = '/v1/aliyun/instances/create'
        let that = this
        this.axios.get(url, {
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
            this.parameters = res.data.data
          }
          else this.$message.error(res.data.msg)
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.loading = false
        });
      },
      createInstance() {
        this.loading = true
        let url = '/v1/aliyun/instances'
        let instance = {
          InstanceChargeType: this.instanceForm.instanceChargeType,
          ZoneId: this.instanceForm.vSwitch.zoneId,
          InstanceType: this.instanceForm.instanceType,
          ImageId: this.instanceForm.imageId,
          SystemDisk: {
            Size: this.instanceForm.systemDisk.size,
            Category: this.instanceForm.systemDisk.category,
          },
          VSwitchId: this.instanceForm.vSwitch.vSwitchId,
          SecurityGroupId: this.instanceForm.securityGroupId,
          InternetMaxBandwidthOut: this.instanceForm.internetMaxBandwidthOut,
          InstanceName: this.instanceForm.instanceName,
        }
        if (this.instanceForm.privateIpAddress.length !== 0)
          instance["PrivateIpAddress"] = this.instanceForm.privateIpAddress
        if (this.instanceForm.description.length !== 0)
          instance["Description"] = this.instanceForm.description
        if (this.instanceForm.instanceChargeType === "PrePaid")
          instance["Period"] = this.instanceForm.period
        if (this.instanceForm.authMethod === "keyPair")
          instance["KeyPairName"] = this.instanceForm.keyPairName
        else
          instance["Password"] = this.instanceForm.password

        let params = {
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
          else if(res.data.code === 400 || res.data.code === 403){
            this.$notify.error("创建实例失败")
          }
          else if(res.data.code === 200){
            this.$notify({title: "成功", message: "创建实例成功", type: "success"});
            this.$router.push("/compute/instances")
          }
          else this.$message.error(res.data.msg)
          this.loading = false
        }).catch(function (error) {
          that.$message.error(error)
          this.loading = false
        });
      },
      submit(){
        this.$refs["instanceForm"].validate((valid) => {
          if (valid) {
            this.createInstance()
          } else {
            return false;
          }
        });
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
  margin-left: 400px;
  width: 100px;
}
.vSwitchLabel{
  color: #606266;
  margin-bottom: 20px;
  font-size: 13px;
}
.vSwitchValue{
  color: #333;
  font-weight: bold;
  margin-right: 10px;
}
</style>
