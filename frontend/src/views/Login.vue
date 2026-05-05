<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="login-header">
        <h1>PFMES</h1>
        <p>생산 및 물류 관리 시스템</p>
      </div>
      
      <form v-if="status !== 'requires_2fa'" class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="empid">아이디</label>
          <input 
            type="text" 
            id="empid" 
            v-model="empid" 
            placeholder="사번을 입력하세요"
            required
            autocomplete="username"
          />
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="비밀번호를 입력하세요"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="errorMessage" class="error-msg">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <!-- OTP 입력 양식 -->
      <form v-else class="login-form" @submit.prevent="handleVerifyOTP">
        <div class="otp-info">
          <p>등록된 이메일로 인증번호가 발송되었습니다.</p>
          <p class="email-hint">{{ userInfo?.email }}</p>
        </div>
        <div class="form-group">
          <label for="otp">인증번호 (6자리)</label>
          <input 
            type="text" 
            id="otp" 
            v-model="otp" 
            placeholder="인증번호 6자리를 입력하세요"
            required
            maxlength="6"
            class="otp-input"
          />
        </div>

        <div v-if="errorMessage" class="error-msg">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '인증 중...' : '인증하기' }}
        </button>
        <button type="button" class="btn-back" @click="status = 'login'">
          뒤로 가기
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';    
import api from '../api';

const router = useRouter();
const empid = ref('');
const password = ref('');
const otp = ref('');
const status = ref('login'); // 'login', 'requires_2fa'
const userInfo = ref<any>(null);
const errorMessage = ref('');
const loading = ref(false);

async function handleLogin() {
  if (!empid.value || !password.value) return;
  
  loading.value = true;
  errorMessage.value = '';
  
  try {
    const res = await api.post('/api/auth/login', {
      empid: empid.value,
      password: password.value
    });
    
    if (res.data.status === 'success') {
      localStorage.setItem('user', JSON.stringify(res.data.user));
      localStorage.setItem('access_token', res.data.access_token);
      router.push('/select-mode');
    } else if (res.data.status === 'requires_2fa') {
      status.value = 'requires_2fa';
      userInfo.value = res.data.user;
      errorMessage.value = res.data.message;
    } else {
      errorMessage.value = res.data.message || '로그인에 실패했습니다.';
    }
  } catch (error: any) {
    // Error notification handled by global interceptor
    console.error('Login error:', error);
  } finally {
    loading.value = false;
  }
}

async function handleVerifyOTP() {
  if (!otp.value) return;
  
  loading.value = true;
  errorMessage.value = '';
  
  try {
    const res = await api.post('/api/auth/verify-otp', {
      empid: empid.value,
      otp: otp.value
    });
    
    if (res.data.status === 'success') {
      localStorage.setItem('user', JSON.stringify(res.data.user));
      localStorage.setItem('access_token', res.data.access_token);
      router.push('/select-mode');
    } else {
      errorMessage.value = res.data.message || '인증에 실패했습니다.';
    }
  } catch (error: any) {
    console.error('OTP verify error:', error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #f6f8fd 0%, #e9eef7 100%);
}

.login-card {
  background: white;
  width: 100%;
  max-width: 400px;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 2.2rem;
  font-weight: 800;
  color: #3b82f6;
  margin: 0;
  letter-spacing: -0.5px;
}

.login-header p {
  color: #64748b;
  margin-top: 5px;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.otp-info {
  text-align: center;
  background: #eff6ff;
  padding: 15px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #1e40af;
}

.email-hint {
  font-weight: 700;
  margin-top: 5px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: #f8fafc;
}

.otp-input {
  text-align: center;
  letter-spacing: 0.5rem;
  font-size: 1.5rem !important;
  font-weight: 700;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.error-msg {
  color: #ef4444;
  font-size: 0.85rem;
  text-align: center;
  padding: 10px;
  background: #fef2f2;
  border-radius: 6px;
}

.btn-login {
  margin-top: 10px;
  background: #3b82f6;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-login:hover:not(:disabled) {
  background: #2563eb;
}

.btn-login:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.btn-back {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-back:hover {
  background: #f8fafc;
}
</style>
