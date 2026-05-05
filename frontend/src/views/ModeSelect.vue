<template>
  <div class="mode-select-page">
    <div class="mode-container">
      <div class="mode-header">
        <span class="mode-logo">🏭</span>
        <h1>PFMES</h1>
        <p class="mode-subtitle">Manufacturing Execution System</p>
      </div>
      <div class="mode-cards">
        <div class="mode-card management" @click="goTo('/management')">
          <div class="card-icon-wrap">
            <span class="card-icon">🖥️</span>
          </div>
          <h2>관리 모드</h2>
          <p>생산계획, 작업지시, 물류, 검사,<br/>기준정보 등 관리 업무</p>
          <div class="card-arrow">→</div>
        </div>
        <div class="mode-card field" @click="goTo('/field')">
          <div class="card-icon-wrap">
            <span class="card-icon">🏭</span>
          </div>
          <h2>현장 모드</h2>
          <p>현장 생산실적 등록,<br/>생산이력 및 불량이력 조회</p>
          <div class="card-arrow">→</div>
        </div>
        <div class="mode-card logistics" @click="goTo('/logistics')">
          <div class="card-icon-wrap">
            <span class="card-icon">🚛</span>
          </div>
          <h2>물류 모드</h2>
          <p>입고등록, 수입검사,<br/>출하등록 등 물류 업무</p>
          <div class="card-arrow">→</div>
        </div>
      </div>
      <div class="mode-footer">
        <span class="user-greeting">{{ userName }}님 환영합니다</span>
        <button class="btn-logout" @click="handleLogout">로그아웃</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const userStr = localStorage.getItem('user');
const userObj = userStr ? JSON.parse(userStr) : null;
const userName = userObj ? userObj.name : '사용자';

function goTo(path: string) {
  router.push(path);
}

async function handleLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  try {
    if (userObj && userObj.empid) {
      await api.post(`/api/auth/logout?empid=${userObj.empid}`);
    }
  } catch (e) {
    console.error('Logout error:', e);
  } finally {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    router.push('/login');
  }
}
</script>

<style scoped>
.mode-select-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f171e 0%, #1a252f 40%, #2c3e50 100%);
  font-family: 'Segoe UI', sans-serif;
}

.mode-container {
  text-align: center;
  padding: 40px;
}

.mode-header {
  margin-bottom: 48px;
}

.mode-logo {
  font-size: 3rem;
  display: block;
  margin-bottom: 12px;
}

.mode-header h1 {
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px;
  letter-spacing: 3px;
}

.mode-subtitle {
  color: #8e99a4;
  font-size: 0.95rem;
  margin: 0;
  letter-spacing: 1px;
}

.mode-cards {
  display: flex;
  gap: 32px;
  justify-content: center;
  margin-bottom: 48px;
}

.mode-card {
  width: 280px;
  padding: 40px 32px 32px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.mode-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 2px;
  background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

.mode-card.management {
  background: linear-gradient(145deg, rgba(102,126,234,0.15), rgba(102,126,234,0.05));
}

.mode-card.field {
  background: linear-gradient(145deg, rgba(39,174,96,0.15), rgba(39,174,96,0.05));
}

.mode-card.logistics {
  background: linear-gradient(145deg, rgba(230,126,34,0.15), rgba(230,126,34,0.05));
}

.mode-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
}

.mode-card.management:hover {
  background: linear-gradient(145deg, rgba(102,126,234,0.25), rgba(102,126,234,0.1));
}

.mode-card.field:hover {
  background: linear-gradient(145deg, rgba(39,174,96,0.25), rgba(39,174,96,0.1));
}

.mode-card.logistics:hover {
  background: linear-gradient(145deg, rgba(230,126,34,0.25), rgba(230,126,34,0.1));
}

.card-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.management .card-icon-wrap {
  background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.2));
}

.field .card-icon-wrap {
  background: linear-gradient(135deg, rgba(39,174,96,0.3), rgba(46,204,113,0.2));
}

.logistics .card-icon-wrap {
  background: linear-gradient(135deg, rgba(230,126,34,0.3), rgba(211,84,0,0.2));
}

.card-icon {
  font-size: 2rem;
}

.mode-card h2 {
  color: #ecf0f1;
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 12px;
}

.mode-card p {
  color: #8e99a4;
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0 0 16px;
}

.card-arrow {
  font-size: 1.4rem;
  color: #5d6d7e;
  transition: all 0.3s;
}

.mode-card:hover .card-arrow {
  color: #ecf0f1;
  transform: translateX(6px);
}

.mode-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.user-greeting {
  color: #8e99a4;
  font-size: 0.9rem;
}

.btn-logout {
  background: rgba(255,255,255,0.08);
  color: #aeb6bf;
  border: 1px solid rgba(255,255,255,0.1);
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(231,76,60,0.2);
  color: #e74c3c;
  border-color: rgba(231,76,60,0.3);
}
</style>
