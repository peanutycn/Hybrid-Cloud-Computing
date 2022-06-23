<template>
  <div id="app" v-title data-title="混合云计算平台">
    <keep-alive>
      <router-view v-if="isRouterAlive"></router-view>
    </keep-alive>
  </div>
</template>

<script>

export default {
  name: 'app',
  components: {
  },
  data() {
    return {
      isRouterAlive: true
    };
  },
  provide() {
    return {
      reload: this.reload
    };
  },
  methods: {
    reload() {
      this.isRouterAlive = false;
      this.$nextTick(() => {
        this.isRouterAlive = true;
      });
    }
  }
}
</script>

<style>
#app {
  font-family: "Microsoft YaHei","微软雅黑","PingFang SC","Hiragino Sans GB",sans-serif;
}
</style>
