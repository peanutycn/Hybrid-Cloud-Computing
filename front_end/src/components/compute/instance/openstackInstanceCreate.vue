<template>
  <div v-loading="loading">
    <el-divider></el-divider>
    <el-form ref = "instanceForm" :model="instanceForm" :rules="rules" class = "container" label-position = "left" label-width = "100px">
      <div class = "formGroup">
        <el-form-item label = "实例名称" prop="name">
          <el-input type = "text" class = "form-control" v-model="instanceForm.name"></el-input>
        </el-form-item>
        <el-form-item label = "描述" prop="description">
          <el-input type = "text" class = "form-control" v-model="instanceForm.description"></el-input>
        </el-form-item>
        <el-form-item label = "可用区" prop="availabilityZone">
          <el-select class = "form-control" v-model="instanceForm.availabilityZone">
            <el-option v-for="zone in parameters.availability_zones" :label="zone.name" :value="zone.name"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "镜像" prop="imageId">
          <el-select class = "form-control" v-model="instanceForm.imageId">
            <el-option v-for="image in parameters.images" :label="image.name" :value="image.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "实例类型" prop="flavorId">
          <el-select class = "form-control" v-model="instanceForm.flavorId">
            <el-option v-for="flavor in parameters.flavors" :label="flavor.name" :value="flavor.id">
              <span style="float: left">{{flavor.name}}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{flavor.vcpus}}核（vCPU）{{flavor.ram/1024}}GiB，磁盘大小{{flavor.disk}}Gib</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "网络" prop="network.id">
          <el-select class = "form-control" v-model="instanceForm.network.id">
            <el-option v-for="network in parameters.networks" :label="network.name" :value="network.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "指定IP" prop="fixed_ip">
          <el-input type = "text" class = "form-control" v-model="instanceForm.network.fixed_ip"></el-input>
        </el-form-item>
        <el-form-item label = "安全组" prop="securityGroup.name">
          <el-select class = "form-control" v-model="instanceForm.securityGroup.name">
            <el-option v-for="securityGroup in parameters.security_groups" :label="securityGroup.name" :value="securityGroup.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label = "密钥对" prop="keyName">
          <el-select class = "form-control" v-model="instanceForm.keyName" clearable >
            <el-option v-for="keyPair in parameters.key_pairs" :label="keyPair.name" :value="keyPair.name"></el-option>
          </el-select>
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
    name: "openstackInstanceCreate",
    data() {
      return {
        instanceForm: {
          name: "",
          description: "",
          availabilityZone: "",
          imageId: "",
          flavorId: "",
          network: {
            id: "",
            fixed_ip: ""
          },
          securityGroup: {
            name: "default"
          },
          keyName : "",
        },
        rules: {
          name: [
            { required: true, message: '请输入实例名称', trigger: 'blur' },
          ],
          availabilityZone: [
            { required: true, message: '请选择可用区', trigger: 'change' }
          ],
          imageId: [
            { required: true, message: '请选择镜像', trigger: 'change' }
          ],
          flavorId: [
            { required: true, message: '请选择实例类型', trigger: 'change' }
          ],
          'network.id': [
            { required: true, message: '请选择网络', trigger: 'change' }
          ],
          'securityGroup.name': [
            { required: true, message: '请选择安全组', trigger: 'change' }
          ],
        },
        parameters: {
          availability_zones: [{
            name: ""
          }],
          images: [{
            name: "",
            id: ""
          }],
          flavors: [{
            name: "",
            id: "",
            vcpus: 0,
            ram: 0,
            disk: 0
          }],
          networks: [{
            name: "",
            id: ""
          }],
          security_groups: [{
            name: "",
            id: ""
          }],
          key_pairs: [{
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
          item: "OpenStack",
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
        let url = '/v1/openstack/instances/create'
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
      createInstance(){
        this.loading = true
        let url = '/v1/openstack/instances'
        let instance = {
          name: this.instanceForm.name,
          availability_zone: this.instanceForm.availabilityZone,
          imageRef: this.instanceForm.imageId,
          flavorRef: this.instanceForm.flavorId,
          security_groups: [this.instanceForm.securityGroup],
        }
        if (this.instanceForm.description.length !== 0)
          instance["description"] = this.instanceForm.description
        if (this.instanceForm.network.fixed_ip.length !== 0)
          instance["networks"] = [{
            uuid: this.instanceForm.network.id,
            fixed_ip: this.instanceForm.network.fixed_ip
          }]
        else
          instance["networks"] = [{
            uuid: this.instanceForm.network.id,
          }]
        if (this.instanceForm.keyName.length !== 0){
          instance["key_name"] = this.instanceForm.keyName
        }

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

</style>
