<template>
  <div class="layout">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo" @click="sidebarCollapsed = !sidebarCollapsed">
        <span class="logo-icon">🏭</span>
        <span class="logo-text" v-show="!sidebarCollapsed">PFMES</span>
      </div>
      <nav class="nav-menu">
        <!-- Dashboard -->
        <router-link to="/management" class="nav-item nav-single">
          <span class="nav-icon">📊</span>
          <span class="nav-label" v-show="!sidebarCollapsed">대시보드</span>
        </router-link>

        <!-- Menu Groups -->
        <div class="nav-group" v-for="group in menuGroups" :key="group.key">
          <div class="nav-group-title" @click="toggleGroup(group.key)">
            <span class="nav-icon">{{ group.icon }}</span>
            <span class="nav-label" v-show="!sidebarCollapsed">{{ group.label }}</span>
            <span class="nav-arrow" v-show="!sidebarCollapsed" :class="{ open: openGroups.includes(group.key) }">▸</span>
          </div>
          <transition name="slide">
            <ul class="nav-sub-list" v-show="openGroups.includes(group.key) && !sidebarCollapsed">
              <li v-for="item in group.children" :key="item.path">
                <router-link :to="item.path" class="nav-sub-item">
                  {{ item.label }}
                </router-link>
              </li>
            </ul>
          </transition>
        </div>
      </nav>
    </aside>

    <div class="main-content">
      <header class="header">
        <div class="header-left">
          <button class="btn-toggle" @click="sidebarCollapsed = !sidebarCollapsed">☰</button>
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        <div class="user-info">
          <div class="user-badge">
            <span class="user-avatar-initials">{{ userInitial }}</span>
          </div>
          <div class="user-details">
            <span class="user-name">{{ userName }}</span>
            <span class="user-role">사용자</span>
          </div>
          <div class="divider-v"></div>
          <button class="btn-logout" @click="handleLogout">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>로그아웃</span>
          </button>
        </div>
      </header>
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../api';

const route = useRoute();
const router = useRouter();
const sidebarCollapsed = ref(false);
const openGroups = ref<string[]>([]);
const menuGroups = ref<any[]>([]);

const userStr = localStorage.getItem('user');
const userObj = userStr ? JSON.parse(userStr) : null;
const userName = ref(userObj ? userObj.name : 'Unknown');
const userInitial = computed(() => userName.value ? userName.value.charAt(0).toUpperCase() : 'U');

async function handleLogout() {
  if (!confirm('로그아웃 하시겠습니까?')) return;
  try {
    if (userObj && userObj.empid) {
      await api.post(`/api/auth/logout?empid=${userObj.empid}`);
    }
  } catch (e) {
    console.error('로그아웃 처리 중 오류:', e);
  } finally {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    router.push('/login');
  }
}
const currentPageTitle = computed(() => {
  return (route.meta?.title as string) || (route.name as string) || 'PFMES';
});

function toggleGroup(key: string) {
  if (sidebarCollapsed.value) {
    sidebarCollapsed.value = false;
    openGroups.value = [key];
    return;
  }
  const idx = openGroups.value.indexOf(key);
  if (idx >= 0) {
    openGroups.value.splice(idx, 1);
  } else {
    openGroups.value.push(key);
  }
}

async function fetchMenus() {
  try {
    const res = await api.get('/api/system/menus');
    // axios res.data => { data: [...] }, 실제 배열은 res.data.data
    const rawMenus = Array.isArray(res.data) ? res.data : (res.data?.data || []);
    // USE_YN이 0(거짓)이 아닌 모든 경우(1, null, undefined)를 허용
    const allMenus = rawMenus.filter((m: any) => m.USE_YN !== 0 && m.USE_YN !== false); 

    const map = new Map();
    const tree: any[] = [];
    
    // 기본 아이콘 매핑
    const iconMap: Record<string, string> = {
      'M01': '📦',
      'M02': '🏭',
      'M03': '🔍',
      'M04': '📋',
      'M05': '⚙️',
      'M06': '💻',
    };

    allMenus.forEach((m: any) => {
      if (!m.PAR_MENUCD) {
        // 부모 메뉴
        const parent = {
          key: m.MENUCD,
          label: m.MENUNM,
          icon: iconMap[m.MENUCD] || '📁',
          children: [] as any[]
        };
        map.set(m.MENUCD, parent);
        // 대시보드는 별도 렌더링되므로 그룹 목록에서 제외
        if (m.MENUCD !== 'M00') {
          tree.push(parent);
        }
      } else {
        // 자식 메뉴
        const parent = map.get(m.PAR_MENUCD);
        if (parent) {
          parent.children.push({
            path: '/management' + (m.CLASS_PATH.startsWith('/') ? '' : '/') + m.CLASS_PATH,
            label: m.MENUNM
          });
        }
      }
    });
    
    menuGroups.value = tree;
  } catch (e) {
    console.error('메뉴 데이터를 불러오는 중 오류 발생:', e);
  }
}

onMounted(() => {
  fetchMenus();
});
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f4f6f9;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: linear-gradient(180deg, #0f171e 0%, #1a252f 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 20px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}

.logo-icon { font-size: 1.5rem; }

.logo-text {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ── Navigation ── */
.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.nav-single {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #aeb6bf;
  text-decoration: none;
  transition: all 0.18s ease;
  border-left: 3px solid transparent;
  font-size: 0.93rem;
}

.nav-single:hover, .nav-single.router-link-exact-active {
  background: rgba(255,255,255,0.05);
  color: #fff;
  border-left-color: #667eea;
}

.nav-icon {
  font-size: 1.15rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.nav-group-title {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #aeb6bf;
  cursor: pointer;
  user-select: none;
  transition: all 0.18s ease;
  border-left: 3px solid transparent;
  font-size: 0.93rem;
}

.nav-group-title:hover {
  background: rgba(255,255,255,0.05);
  color: #fff;
}

.nav-arrow {
  margin-left: auto;
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

.nav-arrow.open {
  transform: rotate(90deg);
}

.nav-sub-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-sub-item {
  display: block;
  padding: 9px 20px 9px 56px;
  color: #8e99a4;
  text-decoration: none;
  font-size: 0.88rem;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
}

.nav-sub-item:hover {
  background: rgba(255,255,255,0.04);
  color: #d5dbe0;
}

.nav-sub-item.router-link-exact-active {
  background: rgba(102, 126, 234, 0.12);
  color: #667eea;
  border-left-color: #667eea;
  font-weight: 600;
}

/* Slide Transition */
.slide-enter-active, .slide-leave-active {
  transition: max-height 0.25s ease, opacity 0.2s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-enter-to, .slide-leave-from {
  max-height: 600px;
  opacity: 1;
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 56px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.btn-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #636e72;
  padding: 4px;
}

.page-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #2c3e50;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.user-avatar-initials {
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.user-details {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: #2c3e50;
}

.user-role {
  font-size: 0.72rem;
  color: #95a5a6;
  font-weight: 400;
}

.divider-v {
  width: 1px;
  height: 28px;
  background: #e8ecf0;
  margin: 0 4px;
}

.page-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f8fafc;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 8px rgba(238, 90, 36, 0.35);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.btn-logout::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.btn-logout:hover::before {
  opacity: 1;
}

.btn-logout:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(238, 90, 36, 0.5);
}

.btn-logout:active {
  transform: translateY(0px);
  box-shadow: 0 2px 6px rgba(238, 90, 36, 0.3);
}

.logout-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.btn-logout:hover .logout-icon {
  transform: translateX(2px);
}

/* Scrollbar */
.nav-menu::-webkit-scrollbar { width: 4px; }
.nav-menu::-webkit-scrollbar-track { background: transparent; }
.nav-menu::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
</style>
