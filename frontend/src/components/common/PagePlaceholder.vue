<template>
  <div class="page-placeholder">
    <div class="placeholder-card">
      <div class="placeholder-icon">{{ icon }}</div>
      <h2>{{ title }}</h2>
      <p class="placeholder-desc">{{ description }}</p>
      <div class="placeholder-badges">
        <span class="badge">API 연동 대기</span>
        <span class="badge outline">DB 테이블 설계 필요</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  icon?: string;
  description?: string;
}>();
</script>

<style scoped>
.page-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 140px);
}

.placeholder-card {
  text-align: center;
  background: #fff;
  border-radius: 18px;
  padding: 48px 56px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  max-width: 460px;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.placeholder-card h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 8px;
}

.placeholder-desc {
  color: #95a5a6;
  font-size: 0.93rem;
  margin-bottom: 20px;
}

.placeholder-badges {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.badge {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.badge.outline {
  background: transparent;
  border: 1px solid #dfe6e9;
  color: #636e72;
}
</style>
