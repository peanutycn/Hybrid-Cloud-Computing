<template>
  <div>
    <div class="actionBar">
      <el-dropdown @command="handleCommand">
        <el-button type="primary" icon="el-icon-plus" style="margin-right: 10px">创建实例</el-button>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item command="openstack">OpenStack</el-dropdown-item>
          <el-dropdown-item command="aliyun">阿里云</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
      <el-select style="width: 120px; margin-right: 10px" v-model="searchSelect" placeholder="请选择">
        <el-option v-for="item in searchOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
      </el-select>
      <el-input
          placeholder="输入筛选条件进行查询"
          prefix-icon="el-icon-search"
          v-model="searchInput" class="input-suffix"
          style="margin-right: 10px"
          clearable>
      </el-input>
      <el-button type="primary" icon="el-icon-search" @click="search">筛选</el-button>
      <el-button type="primary" icon="el-icon-refresh-right" @click="getInstanceList">刷新</el-button>
    </div>
    <!--表格数据及操作-->
    <el-table v-loading="loading" :data="tableData" style="width: auto" stripe ref="multipleTable" tooltip-effect="dark" @selection-change="changeSelected">
      <!--勾选框-->
      <el-table-column type="selection" width="50">
      </el-table-column>
      <!--索引-->
      <el-table-column prop="instanceName" label="实例名称" min-width="150"></el-table-column>
      <el-table-column label="实例ID" min-width="300">
        <template v-slot="scope">
          <el-link type="primary" :href="'/compute/instances/' + scope.row.cloudId + '/' + scope.row.instanceId">{{scope.row.instanceId}}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="所属云" min-width="150">
        <template v-slot="scope">
          <span>{{cloudIdToString(scope.row.cloudId)}}</span>
        </template>
      </el-table-column>
      <el-table-column prop="IPAddress" label="IP地址" min-width="250"></el-table-column>
      <el-table-column label="状态" min-width="100">
        <template v-slot="scope">
          <el-tag :type="scope.row.status.type"><i :class="scope.row.status.icon"></i> {{scope.row.status.content}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="availabilityZone" label="可用区" min-width="150"></el-table-column>
      <el-table-column label="操作" width="250">
        <template v-slot="scope">
          <el-dropdown split-button size="medium" type="primary" style="margin-right: 10px" @command="operateCommand" @click="handleModify(scope.row)">编辑
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item :command="{operation: 'start' , instance: scope.row}">启动实例</el-dropdown-item>
              <el-dropdown-item :command="{operation: 'stop' , instance: scope.row}">停止实例</el-dropdown-item>
              <el-dropdown-item :command="{operation: 'reboot' , instance: scope.row}">重启实例</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          <el-button type="danger" icon="el-icon-delete" size="mini" @click="handleDel(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="danger" :disabled="operateDisabled" icon="el-icon-delete" @click="multiDel" style="margin-top: 20px">删除</el-button>
    <el-button :disabled="operateDisabled" icon="el-icon-video-play" @click="multiStart">启动</el-button>
    <el-button :disabled="operateDisabled" icon="el-icon-video-pause" @click="multiStop">停止</el-button>
    <el-button :disabled="operateDisabled" icon="el-icon-refresh" @click="multiReboot">重启</el-button>

    <el-dialog title="编辑实例" :visible.sync="modifyDialogVisible" :close-on-click-modal="false" width="600px">
      <el-form :model="modifyForm" label-position="top" label-width="100px">
        <el-form-item label="实例名称" :required=true>
          <el-input v-model="modifyForm.instanceName" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="modifyInstance">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="modifyDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="删除实例" :visible.sync="delDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的实例 <span class="instance" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.instanceId}} / {{i.instanceName}}，</span>
        <span class="instance" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].instanceId}} / {{selectedData[selectedData.length - 1].instanceName}}
        </span> 将执行删除操作，实例删除后无法恢复，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="del">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="delDialogVisible = false">取消</el-button>
    </el-dialog>

    <el-dialog title="启动实例" :visible.sync="startDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的实例 <span class="instance" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.instanceId}} / {{i.instanceName}}，</span>
        <span class="instance" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].instanceId}} / {{selectedData[selectedData.length - 1].instanceName}}
        </span> 将执行启动操作，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="start">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="startDialogVisible = false">取消</el-button>
    </el-dialog>

    <el-dialog title="停止实例" :visible.sync="stopDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 30px">您选择的实例 <span class="instance" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.instanceId}} / {{i.instanceName}}，</span>
        <span class="instance" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].instanceId}} / {{selectedData[selectedData.length - 1].instanceName}}
        </span> 将执行停止操作，是否确定？</div>
      <el-form :model="stopForm" label-position="top" label-width="100px">
        <el-form-item label="停止方式：">
          <el-radio v-model="stopForm.force" :label="false">停止</el-radio>
          <el-radio v-model="stopForm.force" :label="true">强制停止</el-radio>
        </el-form-item>
        <el-divider></el-divider>
        <el-form-item  label="停止模式（对阿里云实例）：">
          <el-radio v-model="stopForm.mode" label="KeepCharging">普通停机模式</el-radio>
          <el-radio v-model="stopForm.mode" label="StopCharging">节省停机模式</el-radio>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="stop">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="stopDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="重启实例" :visible.sync="rebootDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 30px">您选择的实例 <span class="instance" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.instanceId}} / {{i.instanceName}}，</span>
        <span class="instance" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].instanceId}} / {{selectedData[selectedData.length - 1].instanceName}}
        </span> 将执行重启操作，是否确定？</div>
      <el-form :model="rebootForm" label-position="top" label-width="100px">
        <el-form-item label="重启方式：">
          <el-radio v-model="rebootForm.force" :label="false">重启</el-radio>
          <el-radio v-model="rebootForm.force" :label="true">强制重启</el-radio>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="reboot">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="rebootDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

  </div>

</template>

<script>
export default {
  name: "instanceList",
  data() {
    return {
      //表格数据
      tableData: [],
      totalData: [],
      selectedData: [],
      searchOptions: [
        {
          value: "instanceName",
          label: "实例名称"
        },
        {
          value: "instanceId",
          label: "实例ID"
        },
        {
          value: "cloudId",
          label: "所属云"
        },
        {
          value: "availabilityZone",
          label: "可用区"
        },
      ],
      searchSelect: "instanceName",
      searchInput: "",
      modifyDialogVisible: false,
      modifyForm: {
        instanceName: ""
      },
      delDialogVisible: false,
      startDialogVisible: false,
      stopDialogVisible: false,
      stopForm: {
        force: false,
        mode: "KeepCharging",
      },
      rebootDialogVisible: false,
      rebootForm: {
        force: false,
      },
      operateDisabled: true,
      loading: true,
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
        path: ""
      },
    ])
    this.getInstanceList()
  },
  mounted(){
  },
  methods: {
    getInstanceList(){
      this.tableData = []
      this.loading = true
      let url = '/v1/instances'
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
          let instances = res.data.data
          for (let i in instances) {
            let instance =  {
              instanceName : "",
              instanceId : "",
              cloudId : "",
              IPAddress : "",
              status : {
                type: "",
                content: "",
                icon: ""
              },
              availabilityZone : "",
            }
            instance["instanceName"] = instances[i]["instance_name"]
            instance["instanceId"] = instances[i]["instance_id"]
            instance["availabilityZone"] = instances[i]["availability_zone"]
            instance["cloudId"] = instances[i]["cloud_id"]
            let addresses = instances[i]["addresses"]["private"]
            for (let j in addresses){
              instance["IPAddress"] += addresses[j] + "（私有）"
              if (parseInt(j) !== addresses.length - 1){
                instance["IPAddress"] += "，"
              }
            }
            addresses = instances[i]["addresses"]["public"]
            for (let j in addresses){
              instance["IPAddress"] += "，" + addresses[j] + "（公/浮动）"
            }
            switch (instances[i]["status"]){
              case "building":
                instance.status.content = "创建中"
                instance.status.type = "info"
                instance.status.icon = "el-icon-loading"
                break
              case "running":
                instance.status.content = "运行中"
                instance.status.type = "success"
                instance.status.icon = "el-icon-success"
                break
              case "starting":
                instance.status.content = "启动中"
                instance.status.type = "info"
                instance.status.icon = "el-icon-loading"
                break
              case "stopping":
                instance.status.content = "停止中"
                instance.status.type = "info"
                instance.status.icon = "el-icon-loading"
                break
              case "stopped":
                instance.status.content = "已停止"
                instance.status.type = "warning"
                instance.status.icon = "el-icon-remove"
                break
              default:
                instance.status.content = "错误"
                instance.status.type = "danger"
                instance.status.icon = "el-icon-error"
            }
            this.tableData.push(instance)
          }
          this.totalData = this.tableData
        }
        else this.$message.error(res.data.msg)
        this.loading = false
      }).catch(function (error) {
        that.$message.error(error)
        this.loading = false
      });
    },
    cloudIdToString(id){
      switch (id){
        case "openstack":
          return "OpenStack"
        case "aliyun":
          return "阿里云"
      }
    },
    search(){
      if(this.searchInput!==""){
        this.tableData = []
        this.totalData.forEach((item,index)=>{
          if(item[this.searchSelect]===this.searchInput){
            this.tableData.push(this.totalData[index])
          }
        })
      }
      else{
        this.tableData = this.totalData
      }
    },
    handleCommand(command){
      this.$router.push("/compute/instances/new/" + command)
    },
    operateCommand(command){
      this.selectedData = []
      this.selectedData.push(command.instance)
      switch (command.operation){
        case "start":
          this.startDialogVisible = true
          break
        case "stop":
          this.stopDialogVisible = true
          break
        case "reboot":
          this.rebootDialogVisible = true
          break
      }
    },
    handleDel(value){
      this.selectedData = []
      this.selectedData.push(value)
      this.delDialogVisible = true
    },
    changeSelected(value){
      this.selectedData = []
      value.forEach((item) => {
        this.selectedData.push(item)
      })
      this.operateDisabled = !this.selectedData.length;
    },
    operateInstances(instanceList, operation){
      let operationString
      let params
      switch (operation){
        case "start":
          operationString = "启动"
          params = {
            start: null
          }
          break
        case "stop":
          operationString = "停止"
          params = {
                stop: {
                  force: this.stopForm.force,
                  mode: this.stopForm.mode
                }
              }
          break
        case "reboot":
          operationString = "重启"
          params = {
            reboot: {
              force: this.rebootForm.force,
            }
          }
          break
      }
      for(let i in instanceList){
        let url = "/v1/" + instanceList[i].cloudId + "/instances/" + instanceList[i].instanceId + "/action"
        let that = this
        this.axios.post(url, params, {
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
            this.$notify.error(operationString + "实例" + instanceList[i].instanceId + "失败")
          }
          else if(res.data.code === 404){
            this.$notify.error(operationString + "实例" + instanceList[i].instanceId + "失败，目标实例不存在")
          }
          else if(res.data.code === 202){
            this.$notify({title: "成功", message: operationString + "实例" + instanceList[i].instanceId + "成功", type: "success"});
          }
          else this.$notify.error(res.data.msg)
        }).catch(function (error) {
          that.$notify.error(error)
        });
      }
      setTimeout(() =>{
        this.getInstanceList()
      }, 1000)
      setTimeout(() =>{
        this.getInstanceList()
      }, 5000)
    },
    modifyInstance(){
      let instance = this.selectedData[0]
      let url = "/v1/" + instance.cloudId + "/instances/" + instance.instanceId
      let params = {
        instance: {
          name: this.modifyForm.instanceName
        }
      }
      let that = this
      this.axios.put(url, params,{
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
          this.$notify.error("错误！编辑实例" + instance.instanceId + "失败")
        }
        else if(res.data.code === 404){
          this.$notify.error("编辑实例" + instance.instanceId + "失败，目标密钥对不存在")
        }
        else if(res.data.code === 200){
          this.$notify({title: "成功", message: "编辑实例" + instance.instanceId + "成功", type: "success"});
          setTimeout(() =>{
            this.getInstanceList()
          }, 1000)
        }
        else this.$notify.error(res.data.msg)
        this.modifyDialogVisible = false
      }).catch(function (error) {
        that.$notify.error(error)
        this.modifyDialogVisible = false
      });
    },
    deleteInstances(instanceList){
      for(let i in instanceList){
        let url = "/v1/" + instanceList[i].cloudId + "/instances/" + instanceList[i].instanceId
        let that = this
        this.axios.delete(url, {
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
            this.$notify.error("错误！删除实例" + instanceList[i].instanceId + "失败")
          }
          else if(res.data.code === 404){
            this.$notify.error("删除实例" + instanceList[i].instanceId + "失败，目标实例不存在")
          }
          else if(res.data.code === 204){
            this.$notify({title: "成功", message: "删除实例" + instanceList[i].instanceId + "成功", type: "success"});
            this.totalData.forEach((item,index)=>{
              if(item["instanceId"]===instanceList[i].instanceId){
                this.tableData.splice(index, 1)
              }
            })
          }
          else this.$notify.error(res.data.msg)
        }).catch(function (error) {
          that.$notify.error(error)
        });
      }
    },
    handleModify(instance){
      this.modifyDialogVisible = true
      this.modifyForm.instanceName = instance.instanceName
      this.selectedData = []
      this.selectedData.push(instance)
    },
    del(){
      this.deleteInstances(this.selectedData)
      this.delDialogVisible = false
    },
    multiDel(){
      this.delDialogVisible = true
    },
    start(){
      this.operateInstances(this.selectedData, "start")
      this.startDialogVisible = false
    },
    multiStart(){
      this.startDialogVisible = true
    },
    stop(){
      this.operateInstances(this.selectedData, "stop")
      this.stopDialogVisible = false
    },
    multiStop(){
      this.stopDialogVisible = true
    },
    reboot(){
      this.operateInstances(this.selectedData, "reboot")
      this.rebootDialogVisible = false
    },
    multiReboot(){
      this.rebootDialogVisible = true
    },
  }
}
</script>
<style>
</style>
<style scoped>
.el-button{
  padding: 10px 15px;
}

.actionBar {
  margin: 20px 0 20px 0;
}

.input-suffix {
  max-width:450px;
  margin: 0 auto;
}

.el-table {
  font-size: 12px;
}

.el-link{
  font-size: 12px;
}

.instance{
  font-weight: bold;
}
</style>
