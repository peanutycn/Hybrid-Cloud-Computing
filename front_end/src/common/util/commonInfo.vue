<script type="text/javascript">
// 定义一些公共的属性和方法
import axios from "axios";

function get_csrf_token() {
  let url = '/api/v1/auth/csrf'
  axios.get(url).then(res => {
  }).catch(function (error) {
    console.log(error)
  });
}
// 暴露出这些属性和方法
export default {
  get_csrf_token,
}
</script>
