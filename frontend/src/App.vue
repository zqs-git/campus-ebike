<template>
  <div id="app">
    <router-view></router-view>
    <!-- ✅ 这里渲染 Vue Router -->
  </div>
</template>

<script setup></script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

/* 在 main.css 或 App.vue 的 style 中全局添加 */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
}

</style>
