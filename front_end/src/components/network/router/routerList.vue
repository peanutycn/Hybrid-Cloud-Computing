<template>
  <div>
    <div class="actionBar">
      <el-dropdown @command="handleCommand">
        <el-button type="primary" icon="el-icon-plus" style="margin-right: 10px">创建路由</el-button>
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
      <el-button type="primary" icon="el-icon-refresh-right" @click="getRouterList">刷新</el-button>
    </div>
    <!--表格数据及操作-->
    <el-table v-loading="loading" :data="tableData" style="width: auto" stripe ref="multipleTable" tooltip-effect="dark" @selection-change="changeSelected">
      <!--勾选框-->
      <el-table-column type="selection" min-width="50">
      </el-table-column>
      <!--索引-->
      <el-table-column label="路由ID" min-width="400">
        <template v-slot="scope">
<!--          <el-link type="primary" :href="'/network/routers/' + scope.row.cloudId + '/' + scope.row.routerId">{{scope.row.routerId}}</el-link>-->
          <el-link type="primary" href="">{{scope.row.routerId}}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="所属云" min-width="200">
        <template v-slot="scope">
          <span>{{cloudIdToString(scope.row.cloudId)}}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template v-slot="scope">
          <el-button type="danger" icon="el-icon-delete" size="mini" @click="handleDel(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button type="danger" :disabled="delDisabled" icon="el-icon-delete" @click="multiDel" style="margin-top: 20px">删除</el-button>

    <el-dialog :title="createDialogTitle" :visible.sync="createDialogVisible" :close-on-click-modal="false" width="800px">
      <el-form :model="createForm" label-position="top" label-width="100px">
        <el-form-item label="路由名称" :required=true>
          <el-input v-model="createForm.name" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="createRouter">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="createDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="删除路由" :visible.sync="delDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的路由 <span class="router" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.routerId}}，</span>
        <span class="router" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].routerId}}
        </span> 将执行删除操作，路由删除后无法恢复，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="del">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="delDialogVisible = false">取消</el-button>
    </el-dialog>

  </div>

</template>

<script>
export default {
  name: "routerList",
  data() {
    return {
      //表格数据
      tableData: [],
      totalData: [],
      selectedData: [],
      searchOptions: [
        {
          value: "routerId",
          label: "路由ID"
        },
        {
          value: "cloudId",
          label: "所属云"
        },
      ],
      searchSelect: "routerId",
      searchInput: "",
      createDialogVisible: false,
      createDialogTitle: "",
      delDialogVisible: false,
      selectCloudId: "",
      createForm: {
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
        item: "路由",
        path: ""
      },
    ])
    this.getRouterList()
  },
  mounted(){
  },
  methods: {
    getRouterList(){
      this.tableData = []
      this.loading = true
      let url = '/v1/routers'
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
          let routers = res.data.data
          for (let i in routers) {
            let router =  {
              routerId : "",
              cloudId : "",
            }
            router["routerId"] = routers[i]["id"]
            router["cloudId"] = routers[i]["cloud_id"]
            this.tableData.push(router)
          }
          this.totalData = this.tableData
        }
        else this.$notify.error(res.data.msg)
        this.loading = false
      }).catch(function (error) {
        that.$notify.error(error)
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
      this.createDialogTitle = "创建路由——" + command
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
    createRouter(){
      this.createDialogVisible = false
    },
    deleteRouters(routerList){
      for(let i in routerList){
        let url = "/v1/" + routerList[i].cloudId + "/routers/" + routerList[i].routerId
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
            this.$notify.error("删除路由" + routerList[i].routerId + "失败，请检查路由是否正在使用")
          }
          else if(res.data.code === 404){
            this.$notify.error("删除路由" + routerList[i].routerId + "失败，目标路由不存在")
          }
          else if(res.data.code === 204){
            this.$notify({title: "成功", message: "删除路由" + routerList[i].routerId + "成功", type: "success"});
            this.totalData.forEach((item,index)=>{
              if(item["routerId"]===routerList[i].routerId){
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
    del(){
      this.deleteRouters(this.selectedData)
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
.router{
  font-weight: bold;
}
</style>
