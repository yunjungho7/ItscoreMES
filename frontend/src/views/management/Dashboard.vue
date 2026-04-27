<template>
  <div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <span>{{ stat.icon }}</span>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>
    <div class="dashboard-section">
      <h2>최근 활동</h2>
      <p class="placeholder-text">데이터베이스 연결 후 실시간 데이터가 표시됩니다.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const stats = [
  { label: '총 품목 수', value: '0', icon: '📦', color: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { label: '공정 수', value: '0', icon: '⚙️', color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
  { label: '작업 지시', value: '0', icon: '📋', color: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
  { label: '재고 현황', value: '0', icon: '🏭', color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
];
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 18px;
  background: #fff;
  border-radius: 14px;
  padding: 22px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: transform 0.18s, box-shadow 0.18s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.7rem;
  font-weight: 700;
  color: #1a252f;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 2px;
}

.dashboard-section {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.dashboard-section h2 {
  margin: 0 0 12px 0;
  font-size: 1.15rem;
  color: #2c3e50;
}

.placeholder-text {
  color: #95a5a6;
  font-size: 0.95rem;
}
</style>
