<template>
<div class="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: "FrontOffice",
};
</script>

<style>
/* Global styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Inter", sans-serif;
}

.app {
  width: 100%;
  min-height: 100vh;
}
</style>
