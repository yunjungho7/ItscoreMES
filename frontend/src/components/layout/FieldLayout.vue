<template>
  <div class="field-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.field-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f4f6f9;
  display: flex;
  flex-direction: column;
}
</style>
