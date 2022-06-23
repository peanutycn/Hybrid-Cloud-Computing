<template>
  <div>
    <div class="actionBar">
      <el-button type="primary" icon="el-icon-plus" style="margin-right: 10px" @click="handleCreate">创建专有网络</el-button>
      <el-select style="width: 160px; margin-right: 10px" v-model="searchSelect" placeholder="请选择">
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
      <el-button type="primary" icon="el-icon-refresh-right" @click="getVPCList">刷新</el-button>
    </div>
    <!--表格数据及操作-->
    <el-table v-loading="loading" :data="tableData" style="width: auto" stripe ref="multipleTable" tooltip-effect="dark" @selection-change="changeSelected">
      <!--勾选框-->
      <el-table-column type="selection" width="50">
      </el-table-column>
      <!--索引-->
      <el-table-column prop="VPCName" label="VPC名称" min-width="200"></el-table-column>
      <el-table-column label="VPC ID" min-width="300">
        <template v-slot="scope">
          <el-link type="primary" :href="'/network/vpcs/details/' + scope.row.VPCId">{{scope.row.VPCId}}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="OpenStack网络ID" min-width="300">
        <template v-slot="scope">
          <el-link type="primary" href="">{{scope.row.networkId}}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="阿里云VPC ID" min-width="300">
        <template v-slot="scope">
          <el-link type="primary" href="">{{scope.row.aliyunVPCId}}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="cidr" label="网段" min-width="150"></el-table-column>
      <el-table-column label="操作" width="200">
        <template v-slot="scope">
          <el-button type="primary" icon="el-icon-edit" size="mini" @click="handleModify(scope.row)">编辑</el-button>
          <el-button type="danger" icon="el-icon-delete" size="mini" @click="handleDel(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="danger" :disabled="delDisabled" icon="el-icon-delete" @click="multiDel" style="margin-top: 20px">删除</el-button>

    <el-dialog title="编辑专有网络" :visible.sync="modifyDialogVisible" :close-on-click-modal="false" width="600px">
      <el-form :model="modifyForm" label-position="top" label-width="100px">
        <el-form-item label="专有网络名称" :required=true>
          <el-input v-model="modifyForm.VPCName" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="modifyVPC">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="modifyDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="删除专有网络" :visible.sync="delDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的专有网络 <span class="VPC" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.VPCId}} / {{i.VPCName}}，</span>
        <span class="VPC" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].VPCId}} / {{selectedData[selectedData.length - 1].VPCName}}
        </span> 将执行删除操作，专有网络删除后无法恢复，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="del">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="delDialogVisible = false">取消</el-button>
    </el-dialog>

  </div>

</template>

<script>
export default {
  name: "VPCList",
  data() {
    return {
      //表格数据
      tableData: [],
      totalData: [],
      selectedData: [],
      searchOptions: [
        {
          value: "VPCName",
          label: "VPC名称"
        },
        {
          value: "VPCId",
          label: "VPC ID"
        },
        {
          value: "networkId",
          label: "OpenStack网络ID"
        },
        {
          value: "aliyunVPCId",
          label: "阿里云VPC ID"
        },
      ],
      searchSelect: "VPCName",
      searchInput: "",
      modifyDialogVisible: false,
      modifyForm: {
        VPCName: ""
      },
      delDialogVisible: false,
      delDisabled: true,
      loading: false,
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
        path: ""
      },
    ])
    this.getVPCList()
  },
  mounted(){
  },
  methods: {
    getVPCList(){
      this.tableData = []
      this.loading = true
      let url = '/v1/vpcs'
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
          let VPCs = res.data.data
          for (let i in VPCs) {
            let VPC = {
              VPCName : "",
              VPCId : "",
              networkId : "",
              aliyunVPCId : "6",
              cidr : ""
            }
            VPC["VPCName"] = VPCs[i]["vpcName"]
            VPC["VPCId"] = VPCs[i]["vpcId"]
            VPC["networkId"] = VPCs[i]["subVpc"]["openstack"]["vpc_id"]
            VPC["aliyunVPCId"] = VPCs[i]["subVpc"]["aliyun"]["vpc_id"]
            VPC["cidr"] = VPCs[i]["cidr"]
            this.tableData.push(VPC)
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
    modifyVPC() {
      let vpc = this.selectedData[0]
      let url = '/v1/vpcs/' + vpc.VPCId
      let params = {
        vpc: {
          name: this.modifyForm.VPCName
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
          this.$notify.error("错误！编辑VPC" + vpc.VPCId + "失败")
        }
        else if(res.data.code === 404){
          this.$notify.error("编辑VPC" + vpc.VPCId + "失败，目标VPC不存在")
        }
        else if(res.data.code === 200){
          this.$notify({title: "成功", message: "编辑VPC" + vpc.VPCId + "成功", type: "success"});
          setTimeout(() =>{
            this.getVPCList()
          }, 1000)
        }
        else this.$notify.error(res.data.msg)
        this.modifyDialogVisible = false
      }).catch(function (error) {
        that.$notify.error(error)
        this.modifyDialogVisible = false
      });
    },
    deleteVPCs(VPCList) {
      for(let i in VPCList) {
        let url = '/v1/vpcs/' + VPCList[i].VPCId
        let that = this
        this.axios.delete(url, {
          headers: {
            token: sessionStorage.getItem("token")
          }
        }).then(res => {
          if (res.data.code === 401) {
            this.$message.error("身份验证过期，请重新登录")
            sessionStorage.removeItem("token");
            this.$router.push("/login")
          } else if (res.data.code === 403) {
            this.$notify.error("错误！删除VPC" + VPCList[i].VPCId + "失败")
          } else if (res.data.code === 404) {
            this.$notify.error("删除VPC" + VPCList[i].VPCId + "失败，目标VPC不存在")
          } else if (res.data.code === 204) {
            this.$notify({title: "成功", message: "删除VPC" + VPCList[i].VPCId + "成功", type: "success"});
            this.totalData.forEach((item,index)=>{
              if(item["VPCId"]===VPCList[i].VPCId){
                this.tableData.splice(index, 1)
              }
            })
          } else this.$notify.error(res.data.msg)
          this.modifyDialogVisible = false
        }).catch(function (error) {
          that.$notify.error(error)
          this.modifyDialogVisible = false
        });
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
    handleCreate(command){
      this.$router.push("/network/vpcs/new")
    },
    handleModify(value){
      this.modifyDialogVisible = true
      this.modifyForm.VPCName = value.VPCName
      this.selectedData = []
      this.selectedData.push(value)
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
      this.delDisabled = !this.selectedData.length;
    },
    del(){
      this.deleteVPCs(this.selectedData)
      this.delDialogVisible = false
    },
    multiDel(){
      this.delDialogVisible = true
    },
  }
}
</script>
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
.VPC{
  font-weight: bold;
}
</style>
