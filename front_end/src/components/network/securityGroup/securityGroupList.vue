<template>
  <div>
    <div class="actionBar">
      <el-dropdown @command="handleCommand">
        <el-button type="primary" icon="el-icon-plus" style="margin-right: 10px">创建安全组</el-button>
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
      <el-button type="primary" icon="el-icon-refresh-right" @click="getSecurityGroupList">刷新</el-button>
    </div>
    <!--表格数据及操作-->
    <el-table v-loading="loading" :data="tableData" style="width: auto" stripe ref="multipleTable" tooltip-effect="dark" @selection-change="changeSelected">
      <!--勾选框-->
      <el-table-column type="selection" width="50">
      </el-table-column>
      <!--索引-->
      <el-table-column prop="securityGroupName" label="安全组名称" min-width="200"></el-table-column>
      <el-table-column prop="securityGroupId" label="安全组ID" min-width="400"></el-table-column>
      <el-table-column label="所属云" min-width="200">
        <template v-slot="scope">
          <span>{{cloudIdToString(scope.row.cloudId)}}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template v-slot="scope">
          <el-button type="primary" icon="el-icon-edit" size="mini" @click="handleModify(scope.row)">编辑</el-button>
          <el-button type="danger" icon="el-icon-delete" size="mini" @click="handleDel(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="danger" :disabled="delDisabled" icon="el-icon-delete" @click="multiDel" style="margin-top: 20px">删除</el-button>

    <el-dialog title="编辑安全组" :visible.sync="modifyDialogVisible" :close-on-click-modal="false" width="600px">
      <el-form :model="modifyForm" label-position="top" label-width="100px">
        <el-form-item label="安全组名称" :required=true>
          <el-input v-model="modifyForm.name" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="modifySecurityGroup">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="modifyDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog :title="createDialogTitle" :visible.sync="createDialogVisible" :close-on-click-modal="false" width="800px">
      <el-form :model="createForm" label-position="top" label-width="100px">
        <el-form-item label="安全组名称" :required=true>
          <el-input v-model="createForm.name" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="createSecurityGroup">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="createDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="删除安全组" :visible.sync="delDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的安全组 <span class="securityGroup" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.securityGroupId}} / {{i.securityGroupName}}，</span>
        <span class="securityGroup" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].securityGroupId}} / {{selectedData[selectedData.length - 1].securityGroupName}}
        </span> 将执行删除操作，安全组删除后无法恢复，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="del">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="delDialogVisible = false">取消</el-button>
    </el-dialog>

  </div>

</template>

<script>
export default {
  name: "securityGroupList",
  data() {
    return {
      //表格数据
      tableData: [],
      totalData: [],
      selectedData: [],
      searchOptions: [
        {
          value: "securityGroupName",
          label: "安全组名称"
        },
        {
          value: "securityGroupId",
          label: "安全组ID"
        },
        {
          value: "cloudId",
          label: "所属云"
        },
      ],
      searchSelect: "securityGroupName",
      searchInput: "",
      createDialogVisible: false,
      createDialogTitle: "",
      modifyDialogVisible: false,
      delDialogVisible: false,
      selectCloudId: "",
      createForm: {
        name: "",
      },
      modifyForm: {
        name: "",
      },
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
        item: "安全组",
        path: ""
      },
    ])
    this.getSecurityGroupList()
  },
  mounted(){
  },
  methods: {
    getSecurityGroupList(){
      this.tableData = []
      this.loading = true
      let url = '/v1/security-groups'
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
          let security_groups = res.data.data
          for (let i in security_groups) {
            let security_group =  {
              securityGroupId : "",
              securityGroupName : "",
              cloudId : "",
            }
            security_group["securityGroupId"] = security_groups[i]["security_group_id"]
            security_group["securityGroupName"] = security_groups[i]["security_group_name"]
            security_group["cloudId"] = security_groups[i]["cloud_id"]
            this.tableData.push(security_group)
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
      this.createDialogVisible = true
      this.selectCloudId = command
      this.createDialogTitle = "创建安全组——" + command
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
    createSecurityGroup(){
      this.createDialogVisible = false
    },
    modifySecurityGroup(){
      this.modifyDialogVisible = false
    },
    deleteSecurityGroups(securityGroupList){
    },
    handleModify(securityGroup){
      this.modifyDialogVisible = true
      this.modifyForm.name = securityGroup.securityGroupName
      this.selectedData = []
      this.selectedData.push(securityGroup)
    },
    del(){
      this.deleteSecurityGroups(this.selectedData)
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
.securityGroup{
  font-weight: bold;
}
</style>
