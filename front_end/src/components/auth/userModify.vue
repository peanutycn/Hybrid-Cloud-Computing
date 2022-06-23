<template>
  <div>
    <el-divider></el-divider>
    <div style="font-size: 24px; display: inline-block">更改密码</div>
    <el-form ref = "PasswordForm" :model = "PasswordForm"  :rules = "passwordRules"  class = "login-container" label-position = "left" label-width = "100px">
      <div class = "formGroup">
        <el-form-item label = "当前密码" prop = "OriginPassword" >
          <el-input type = "text"  autocomplete = "off" placeholder = "请输入当前密码" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="PasswordForm.OriginPassword" show-password></el-input>
        </el-form-item>
        <el-form-item label = "新密码" prop = "NewPassword" >
          <el-input type = "password" autocomplete = "off" placeholder = "请输入新密码" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="PasswordForm.NewPassword" show-password></el-input>
        </el-form-item>
        <el-form-item label = "确认密码" prop = "ConfirmPassword" >
          <el-input type = "password" autocomplete = "off" placeholder = "请确认密码" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="PasswordForm.ConfirmPassword" show-password></el-input>
        </el-form-item>
      </div>
      <div class = "formButton">
        <el-form-item label-width = "0px">
          <el-button type = "primary" style = "width:100%;" @click="submitPasswordForm('PasswordForm')">确认更改</el-button>
        </el-form-item>
      </div>
    </el-form>
    <el-divider></el-divider>
    <div style="margin-right: 20px; font-size: 24px; display: inline-block">更改阿里云AccessKey</div>
    <el-link type="primary" href="https://ram.console.aliyun.com/manage/ak" target="_blank" :underline="false"><i class="el-icon-link"></i> 获取AccessKey</el-link>
    <el-form ref = "aliyunForm" :model = "aliyunForm"  :rules = "aliyunRules"  class = "login-container" label-position = "left" label-width = "150px">
      <div class = "formGroup">
        <el-form-item label = "AccessKey ID" prop = "accessKeyId" >
          <el-input type = "text"  autocomplete = "off" placeholder = "请输入AccessKey ID" @keyup.native="replaceCharacter"
                    class = "form-control-AK" v-model="aliyunForm.accessKeyId"></el-input>
        </el-form-item>
        <el-form-item label = "AccessKey Secret" prop = "accessKeySecret" >
          <el-input type = "password" autocomplete = "off" placeholder = "请输入AccessKey Secret" @keyup.native="replaceCharacter"
                    class = "form-control-AK" v-model="aliyunForm.accessKeySecret" show-password></el-input>
        </el-form-item>
        <el-form-item label = "Region ID" prop = "regionId" >
          <el-select class = "form-control-AK" v-model="aliyunForm.regionId" placeholder="请选择Region ID">
            <el-option label="华北1（青岛）" value="cn-qingdao"></el-option>
            <el-option label="华北2（北京）" value="cn-beijing"></el-option>
            <el-option label="华北3（张家口）" value="cn-zhangjiakou"></el-option>
            <el-option label="华北5（呼和浩特）" value="cn-huhehaote"></el-option>
            <el-option label="华北6（乌兰察布）" value="cn-wulanchabu"></el-option>
            <el-option label="华东1（杭州）" value="cn-hangzhou"></el-option>
            <el-option label="华东2（上海）" value="cn-shanghai"></el-option>
            <el-option label="华南1（深圳）" value="cn-shenzhen"></el-option>
            <el-option label="华南2（河源）" value="cn-heyuan"></el-option>
            <el-option label="华南3（广州）" value="cn-guangzhou"></el-option>
            <el-option label="华西1（成都）" value="cn-chengdu"></el-option>
          </el-select>
        </el-form-item>
      </div>
      <div class = "formButton">
        <el-form-item label-width = "0px">
          <el-button type = "primary" style = "width:100%;" @click="submitAliyunForm('aliyunForm')">确认更改</el-button>
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script>
  import { mapMutations}  from "vuex";

  export default {
    name: "userModify",
    data() {
      let validatePassword = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('不能为空'));
        } else {
          setTimeout(() => {
            if (value.length < 6) {
              callback(new Error('密码长度不小于6位'));
            } else if (value.length > 16) {
              callback(new Error('密码长度不大于16位'));
            } else {
              /*账号密码校验*/
              callback();
            }
          }, 1000);
        }
      };
      let validateConfirm = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('密码不能为空'));
        }
        else {
          setTimeout(() => {
            if (value !== this.PasswordForm.NewPassword) {
              callback(new Error('两次密码不一致'))
            }
            else {
              callback();
            }
          }, 1000);
        }
      };
      let validateEmpty = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('不能为空！'));
        }
        else {
          callback()
        }
      };
      return {
        logoUrl: "/image/logo.png",
        /*表单字段双向绑定*/
        PasswordForm:{
          OriginPassword:"",
          NewPassword:"",
          ConfirmPassword:""
        },
        aliyunForm:{
          accessKeyId : "",
          accessKeySecret : "",
          regionId : ""
        },
        passwordRules: {
          OriginPassword :[
            { validator: validatePassword,trigger: 'blur' }
          ],
          NewPassword: [
            { validator: validatePassword,trigger: 'blur' }
          ],
          ConfirmPassword: [
            { validator: validateConfirm,trigger: 'blur' }
          ]
        },
        aliyunRules: {
          accessKeyId: [
            { validator: validateEmpty,trigger: 'blur' }
          ],
          accessKeySecret: [
            { validator: validateEmpty,trigger: 'blur' }
          ],
          regionId: [
            { validator: validateEmpty,trigger: 'blur' }
          ],
        },
      };
    },
    created() {
      this.$emit("change", [
        {
          item: "鉴权管理",
          path: ""
        },
        {
          item: "更改信息",
          path: ""
        },
      ])
    },
    methods:{
      ...mapMutations(['updateUserStatus']),
      updatePassword() {
        let url = '/v1/auth/password'
        let params =
            {
              user: {
                password : this.PasswordForm.NewPassword,
                original_password : this.PasswordForm.OriginPassword
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
            this.$message.error("当前密码或其他错误，请重试")
            this.resetInput()
          }
          else if(res.data.code === 200){
            let user = null
            this.updateUserStatus(user)
            this.$message({message: "更改密码成功！3秒后跳转到登录界面", type: "success"})
            setTimeout(() =>{
              this.$router.push("/login")
            }, 3000)
          }
          else {
            this.$message.error("未知错误，请重试")
            this.resetInput()
          }
        }).catch(function (error) {
          that.$message.error(error)
        });
      },
      updateAliyunAccessKey() {
        let url = '/v1/aliyun/auth/access-keys'
        let params =
            {
              access_key : {
                id : this.aliyunForm.accessKeyId,
                secret: this.aliyunForm.accessKeySecret
              },
              region_id : this.aliyunForm.regionId
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
            this.$message.error("AccessKey或其他错误，请重试")
            this.resetInput()
          }
          else if(res.data.code === 200){
            this.$message({message: "更改AccessKey成功！", type: "success"})
          }
          else {
            this.$message.error("未知错误，请重试")
            this.resetInput()
          }
        }).catch(function (error) {
          that.$message.error(error)
        });
      },
      /*登陆按钮提交事件*/
      submitPasswordForm(form) {
        this.$refs[form].validate((valid) => {
          if (valid) {
            this.updatePassword()
          } else {
            return false;
          }
        });
      },
      submitAliyunForm(form) {
        this.$refs[form].validate((valid) => {
          if (valid) {
            this.updateAliyunAccessKey()
          } else {
            return false;
          }
        });
      },
      replaceCharacter() {
        if(this.PasswordForm.OriginPassword!=null){
          if(this.PasswordForm.OriginPassword.length > 16){
            this.PasswordForm.OriginPassword = this.PasswordForm.OriginPassword.slice(0,16)
          }
        }
        if(this.PasswordForm.NewPassword!=null){
          if(this.PasswordForm.NewPassword.length > 16){
            this.PasswordForm.NewPassword = this.PasswordForm.NewPassword.slice(0,16)
          }
        }
        if(this.PasswordForm.ConfirmPassword!=null){
          if(this.PasswordForm.ConfirmPassword.length > 16){
            this.PasswordForm.ConfirmPassword = this.PasswordForm.ConfirmPassword.slice(0,16)
          }
        }
        if(this.aliyunForm.accessKeyId!=null){
          if(this.aliyunForm.accessKeyId.length > 36){
            this.aliyunForm.accessKeyId = this.aliyunForm.accessKeyId.slice(0,36)
          }
        }
        if(this.aliyunForm.accessKeySecret!=null){
          if(this.aliyunForm.accessKeySecret.length > 36){
            this.aliyunForm.accessKeySecret = this.aliyunForm.accessKeySecret.slice(0,36)
          }
        }
      },
      resetInput() {
        this.PasswordForm.OriginPassword = ""
        this.PasswordForm.NewPassword = ""
        this.PasswordForm.ConfirmPassword = ""
        this.aliyunForm.accessKeyId = ""
        this.aliyunForm.accessKeySecret = ""
        this.aliyunForm.regionId = null
      }
    },
    mounted(){
    }
  }
</script>
<!--全局属性-->
<style>
</style>
<style scoped>
  .form-control{
    width:400px;
    flex: 1;
    -webkit-flex: 1;
    -ms-flex: 1;
  }
  .form-control-AK{
    width:350px;
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
