<template>
  <!--login框，表单+tab标签页的组合-->
  <div class = "loginFrame" @keyup.enter="submitForm('AccountForm')">
    <!--表单组件放在外面，标签栏在里面-->
     <!--rules属性传入验证规则-->
    <el-form ref = "AccountForm" :model = "AccountForm"  :rules = "rules"  class = "login-container" label-position = "left" label-width = "60px">
      <div class="title">
        <el-image
          style="width: 200px; height: 200px; margin-bottom:-5px; position: relative;"
          :src= "logoUrl"
          fit= "fill">
        </el-image>
        <div style="font-size: 24px ;font-weight: 600 ;font-family:'等线',serif ;margin: 20px">混合云计算平台</div>
      </div>
      <!--账号密码输入框-->
      <div class = "formGroup">
        <!--prop属性设置需要校验的字段名，表单验证时，就会验证el-input元素绑定的变量AccountForm.username的值是否符合验证规则-->
        <el-form-item label = "账号" prop = "Username" >
          <el-input type = "text"  autocomplete = "off" placeholder = "请输入账号" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="AccountForm.Username"></el-input>
        </el-form-item>
        <el-form-item label = "密码" prop = "Password" class = "form-inline">
          <el-input type = "password" autocomplete = "off" placeholder = "请输入密码" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="AccountForm.Password" show-password></el-input>
        </el-form-item>
        <el-form-item label = "域" prop = "Domain" class = "form-inline">
          <el-input type = "text" autocomplete = "off" placeholder = "请输入域" @keyup.native="replaceCharacter"
                    class = "form-control" v-model="AccountForm.Domain"></el-input>
        </el-form-item>
      </div>
      <!--登陆按钮-->
      <div class = "formButton">
        <el-form-item style = "width:100%;" label-width = "0px">
          <el-button type = "primary" style = "width:100%;" @click="submitForm('AccountForm')">登录</el-button>
        </el-form-item>
      </div>
      <div class="copyright">
        <div  style="display: inline-block ;margin-right: 20px">copyright©</div>
        <div  style="display: inline-block">Peanuty(杨涛)</div>
      </div>
    </el-form>
  </div>
</template>

<script>
  import { mapMutations}  from "vuex";

  export default {
    name: "login",
    data() {
      /*自定义检验账号方法*/
      let validateUsername = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('不能为空'));
        } else {
          setTimeout(() => {
            if (value.length < 4) {
              callback(new Error('账号长度不小于4位'));
            } else if (value.length > 16) {
              callback(new Error('账号长度不大于16位'));
            } else {
              /*账号密码校验*/
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
        logoUrl: "/image/logo.svg",
        /*表单字段双向绑定*/
        AccountForm:{
          Username:"",
          Password:"",
          Domain:"default"
        },
        rules: {
          Username :[
            { validator: validateUsername,trigger: 'blur' }
          ],
          Password: [
            { validator: validateEmpty,trigger: 'blur' }
          ],
          Domain: [
            { validator: validateEmpty,trigger: 'blur' }
          ]
        },
        checked: false,
        project: null
      };
    },
    created() {
    },
    activated(){
      this.resetInput()
    },
    methods:{
      ...mapMutations(['updateUserStatus']),
      login() {
        let url = '/v1/auth/token'
        let params = {
          methods: [
              "password"
          ],
          password: {
            user: {
              name: this.AccountForm.Username,
              domain: {
                name: this.AccountForm.Domain
              },
              password: this.AccountForm.Password
            }
          }
        }
        let that = this
        this.axios.post(url, params).then(res => {
          if(res.data.code === 200){
            const user = {
              userId:  res.data.data.token.user.id,
              userName:  res.data.data.token.user.name,
              domainId: res.data.data.token.user.domain.id,
              domainName: res.data.data.token.user.domain.name,
              projectId: res.data.data.token.project.id,
              projectName: res.data.data.token.project.name,
              token: res.headers.token,
            };
            that.updateUserStatus(user)
            this.$message({message: '登录成功', type: 'success'})
            this.$router.push("/user/detail")
          }
          else {
            this.$message.error('身份验证错误，请重新输入')
            this.resetInput()
          }
        }).catch(function (error) {
          that.$message.error(error)
        });
      },
      /*登陆按钮提交事件*/
      submitForm(AccountForm) {
        this.$refs[AccountForm].validate((valid) => {
          if (valid) {
            this.login()
          } else {
            return false;
          }
        });
      },
      replaceCharacter() {
        if(this.AccountForm.Username!=null){
          this.AccountForm.Username=this.AccountForm.Username.replace(/[^a-z0-9A-Z]/g,'')
          if(this.AccountForm.Username.length > 16){
            this.AccountForm.Username = this.AccountForm.Username.slice(0,16)
          }
        }
        if(this.AccountForm.Password!=null){
          if(this.AccountForm.Password.length > 16){
            this.AccountForm.Password = this.AccountForm.Password.slice(0,16)
          }
        }
        if(this.AccountForm.Domain!=null){
          if(this.AccountForm.Domain.length > 16){
            this.AccountForm.Domain = this.AccountForm.Domain.slice(0,16)
          }
        }
      },
      resetInput() {
        this.AccountForm.Username = ""
        this.AccountForm.Password = ""
        this.AccountForm.Domain = "default"
      }
    },
  }
</script>
<!--全局属性-->
<style>
  .loginFrame .el-form-item__label{
    font-size: 20px;
    text-align:right;
    margin-left: 10px;
  }
  .loginFrame .el-tabs__item {
    font-size: 20px;
  }
</style>
<style scoped>
  /*整个登录页面*/
  .login-container {
    -webkit-border-radius: 5px;
    border-radius: 15px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    margin: 100px auto;
    width: 360px;
    text-align: center;
    padding: 20px 35px 15px 35px;
    background: rgba(255,255,255,0.8);
    border: 1px solid #eaeaea;
    box-shadow: 0 0 25px #cac6c6;
  }
  .title {
    font-size: 28px;
    font-family: "Microsoft YaHei UI",serif;
    margin: 0 0 20px 0;
  }
  .tab{
    display: inline-block;
  }
  /*输入框*/
  .form-control{
    width:280px;
    flex: 1;
    -webkit-flex: 1;
    -ms-flex: 1;
  }
  /*账号密码输入框*/
  .formGroup{
    margin-top: 30px;
  }
  /*登录按钮*/
  .formButton{
    margin: 40px 20px;
  }

</style>
