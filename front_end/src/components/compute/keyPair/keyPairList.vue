<template>
  <div>
    <div class="actionBar">
      <el-dropdown @command="handleCommand">
        <el-button type="primary" icon="el-icon-plus" style="margin-right: 10px">创建密钥对</el-button>
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
      <el-button type="primary" icon="el-icon-refresh-right" @click="getKeyPairList">刷新</el-button>
    </div>
    <!--表格数据及操作-->
    <el-table v-loading="loading" :data="tableData" style="width: auto" stripe ref="multipleTable" tooltip-effect="dark" @selection-change="changeSelected">
      <!--勾选框-->
      <el-table-column type="selection" width="50">
      </el-table-column>
      <!--索引-->
      <el-table-column prop="keyPairName" label="密钥对名称" min-width="200"></el-table-column>
      <el-table-column prop="keyPairFingerprint" label="密钥对指纹" min-width="400"></el-table-column>
      <el-table-column prop="createdTime" label="创建时间" min-width="300"></el-table-column>
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
      <el-form :model="form" label-position="top" label-width="100px">
        <el-form-item label="密钥对名称" :required=true>
          <el-input v-model="form.name" class = "form-control"></el-input>
        </el-form-item>
        <el-form-item label="密钥对公钥" :required=true>
          <el-input v-model="form.publicKey" type="textarea" :rows="5" ></el-input>
        </el-form-item>
        <el-divider></el-divider>
        <el-form-item>
          <el-button type="primary" icon="el-icon-check" style="position:absolute; right:100px" @click="createKeyPair">确定</el-button>
          <el-button icon="el-icon-close" style="position:absolute; right:0" @click="createDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="删除密钥对" :visible.sync="delDialogVisible" :close-on-click-modal="false" width="600px">
      <div style="margin-bottom: 60px">您选择的密钥对 <span class="keyPair" v-for="i in selectedData.slice(0, selectedData.length - 1)">{{i.keyPairName}}，</span>
        <span class="keyPair" v-if="selectedData[selectedData.length - 1]">
          {{selectedData[selectedData.length - 1].keyPairName}}
        </span> 将执行删除操作，密钥对删除后无法恢复，是否确定？</div>
      <el-button type="primary" icon="el-icon-check" style="position:absolute; right:120px; bottom: 20px" @click="del">确定</el-button>
      <el-button icon="el-icon-close" style="position:absolute; right:20px; bottom: 20px" @click="delDialogVisible = false">取消</el-button>
    </el-dialog>

  </div>


</template>

<script>
export default {
  name: "keyPairList",
  data() {
    return {
      //表格数据
      tableData: [],
      totalData: [],
      selectedData: [],
      searchOptions: [
        {
          value: "keyPairName",
          label: "密钥对名称"
        },
        {
          value: "keyPairFingerprint",
          label: "密钥对指纹"
        },
        {
          value: "cloudId",
          label: "所属云"
        },
      ],
      searchSelect: "keyPairName",
      searchInput: "",
      createDialogVisible: false,
      createDialogTitle: "",
      delDialogVisible: false,
      selectCloudId: "",
      form: {
        name: "",
        publicKey: "",
      },
      delDisabled: true,
      loading: false,
    }
  },
  created() {
    this.$emit("change", [
      {
        item: "计算管理",
        path: ""
      },
      {
        item: "密钥对",
        path: ""
      },
    ])
    this.getKeyPairList()
  },
  mounted(){
  },
  methods: {
    getKeyPairList(){
      this.tableData = []
      this.loading = true
      let url = '/v1/key-pairs'
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
          let key_pairs = res.data.data
          for (let i in key_pairs) {
            let key_pair =  {
              keyPairName : "",
              keyPairFingerprint : "",
              createdTime : "",
              cloudId : "",
            }
            key_pair["keyPairName"] = key_pairs[i]["key_pair_name"]
            key_pair["keyPairFingerprint"] = key_pairs[i]["key_pair_fingerprint"]
            key_pair["cloudId"] = key_pairs[i]["cloud_id"]
            let time
            switch (key_pair["cloudId"]){
              case "openstack":
                time = new Date(key_pairs[i]["created_time"]+"z")
                break;
              case "aliyun":
                time = new Date(key_pairs[i]["created_time"])
                break;
            }
            key_pair["createdTime"] = time.getFullYear() + "年" + (time.getMonth() + 1) + "月" +
                time.getDate() + "日 " + time.getHours() + ":" + time.getMinutes()
            this.tableData.push(key_pair)
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
      this.createDialogTitle = "创建密钥对——" + command
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
    createKeyPair(){
      let url = "/v1/" + this.selectCloudId + "/key-pairs"
      let params =
          {
            key_pair: {
              name : this.form.name,
              publicKey : this.form.publicKey
            }
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
        else if(res.data.code === 400){
          this.$notify.error("请检查密钥对名称是否合法和重复，密钥对公钥是否正确")
          this.resetInput()
        }
        else if(res.data.code === 200){
          this.getKeyPairList()
          this.$notify({title: "成功", message: "创建密钥对成功！", type: "success"})
          this.createDialogVisible = false
          this.resetInput()
        }
        else this.$notify.error(res.data.msg)
      }).catch(function (error) {
        that.$notify.error(error)
      });
    },
    deleteKeyPairs(keyPairList){
      for(let i in keyPairList){
        let url = "/v1/" + keyPairList[i].cloudId + "/key-pairs/" + keyPairList[i].keyPairName
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
            this.$notify.error("删除密钥对" + keyPairList[i].keyPairName + "失败，请检查密钥对是否正在使用")
          }
          else if(res.data.code === 404){
            this.$notify.error("删除密钥对" + keyPairList[i].keyPairName + "失败，目标密钥对不存在")
          }
          else if(res.data.code === 204){
            this.$notify({title: "成功", message: "删除密钥对" + keyPairList[i].keyPairName + "成功", type: "success"});
            this.totalData.forEach((item,index)=>{
              if(item["keyPairName"]===keyPairList[i].keyPairName){
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
      this.deleteKeyPairs(this.selectedData)
      this.delDialogVisible = false
    },
    multiDel(){
      this.delDialogVisible = true
    },
    resetInput() {
      this.form.name = ""
      this.form.publicKey = ""
    }
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
.keyPair{
  font-weight: bold;
}
</style>
