<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container shipment-modal">
      <header class="modal-header">
        <div class="header-title-wrap">
          <span class="header-icon">🚢</span>
          <h3>출하지시조회</h3>
        </div>
        <div class="header-actions">
          <button class="btn-confirm" @click="confirmSelection">
            <span class="icon">✅</span> 확인
          </button>
          <button class="btn-close-x" @click="$emit('close')">✕</button>
        </div>
      </header>

      <div class="search-bar">
        <div class="filter-group">
          <div class="filter-item">
            <label>조회기간</label>
            <div class="date-wrap">
              <input type="date" v-model="filters.startDate" />
              <span class="sep">~</span>
              <input type="date" v-model="filters.endDate" />
            </div>
          </div>
          <div class="filter-item">
            <label>검색어</label>
            <div class="search-input-wrap">
              <input type="text" v-model="filters.search" placeholder="고객사 또는 품번" @keyup.enter="fetchData" />
              <button class="btn-search-inner" @click="fetchData">🔍 조회</button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-body">
        <div class="grid-card">
          <DataGrid 
            :columns="columns" 
            :rows="rows" 
            :loading="loading"
            :selectedIndex="selectedIndex"
            @row-click="onRowClick"
          />
        </div>
      </div>

      <footer class="modal-footer">
        <div class="record-info">
          <span class="count">{{ rows.length }}</span> items found
        </div>
        <div class="spacer"></div>
        <button class="btn-secondary" @click="$emit('close')">닫기</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import DataGrid from '../../components/common/DataGrid.vue';
import api from '../../api';

const props = defineProps<{
  visible: boolean;
  initialStartDate?: string;
  initialEndDate?: string;
  initialSearch?: string;
}>();

const emit = defineEmits(['close', 'confirm']);

const loading = ref(false);
const rows = ref<any[]>([]);
const selectedIndex = ref(-1);
const selectedItem = ref<any>(null);

const filters = ref({
  startDate: props.initialStartDate || new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10),
  endDate: props.initialEndDate || new Date().toISOString().slice(0, 10),
  search: props.initialSearch || ''
});

const columns = [
  { key: 'index', label: '순번', width: '60px' },
  { key: 'SHIPMENT_NO', label: '출하지시번호', width: '150px' },
  { key: 'SHIP_PLAN_DATE', label: '출하계획일', width: '120px', type: 'date' },
  { key: 'COMPANYNM', label: '고객사', width: '180px' },
  { key: 'PARTNO', label: '제품품번', width: '150px' },
  { key: 'PARTNM', label: '품명', width: '180px' },
];

async function fetchData() {
  loading.value = true;
  selectedIndex.value = -1;
  selectedItem.value = null;
  
  try {
    const r = await api.get('/api/shipment/list', {
      params: {
        start_date: filters.value.startDate,
        end_date: filters.value.endDate,
        search: filters.value.search
      }
    });
    
    const rawData = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    
    rows.value = Array.isArray(rawData) ? rawData.map((item: any, idx: number) => ({
      ...item,
      index: idx + 1
    })) : [];
    
  } catch (e) {
    console.error('출하지시 목록 조회 중 오류:', e);
  } finally {
    loading.value = false;
  }
}

function onRowClick(row: any, idx: number) {
  selectedIndex.value = idx;
  selectedItem.value = row;
}

function confirmSelection() {
  if (!selectedItem.value) {
    alert('출하지시 건을 선택해주세요.');
    return;
  }
  emit('confirm', selectedItem.value);
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    fetchData();
  }
});
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-container { background: #fff; border-radius: 20px; max-width: 95vw; width: 950px; height: 750px; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid #e2e8f0; overflow: hidden; }
@keyframes modalIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px; border-bottom: 1px solid #f1f5f9; }
.header-title-wrap { display: flex; align-items: center; gap: 12px; }
.header-icon { font-size: 1.4rem; display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: #f8fafc; border-radius: 12px; border: 1px solid #f1f5f9; }
.modal-header h3 { margin: 0; font-size: 1.15rem; font-weight: 800; color: #0f172a; letter-spacing: -0.025em; }

.header-actions { display: flex; align-items: center; gap: 12px; }
.btn-confirm { background: #0f172a; color: #fff; border: none; padding: 8px 18px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.9rem; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-confirm:hover { background: #1e293b; transform: translateY(-1px); }
.btn-close-x { background: #f8fafc; border: 1px solid #f1f5f9; width: 36px; height: 36px; border-radius: 10px; font-size: 1.1rem; cursor: pointer; color: #94a3b8; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
.btn-close-x:hover { background: #fee2e2; color: #ef4444; transform: rotate(90deg); }

.search-bar { padding: 20px 28px; background: #f8fafc; border-bottom: 1px solid #f1f5f9; }
.filter-group { display: flex; gap: 24px; }
.filter-item { display: flex; flex-direction: column; gap: 6px; }
.filter-item label { font-size: 0.82rem; font-weight: 700; color: #64748b; margin-left: 2px; }

.date-wrap { display: flex; align-items: center; gap: 8px; background: #fff; border: 1px solid #e2e8f0; padding: 4px 12px; border-radius: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.date-wrap input { border: none; font-size: 0.9rem; color: #1e293b; font-weight: 500; outline: none; }
.sep { color: #cbd5e1; font-weight: 700; }

.search-input-wrap { display: flex; align-items: center; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); overflow: hidden; }
.search-input-wrap input { border: none; padding: 8px 14px; font-size: 0.9rem; width: 220px; outline: none; }
.btn-search-inner { background: #64748b; color: #fff; border: none; padding: 8px 16px; font-weight: 700; cursor: pointer; font-size: 0.88rem; transition: background 0.2s; }
.btn-search-inner:hover { background: #475569; }

.modal-body { padding: 20px 28px; flex: 1; overflow: hidden; background: #fff; }
.grid-card { height: 100%; border: 1px solid #f1f5f9; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }

.modal-footer { display: flex; align-items: center; gap: 12px; padding: 16px 28px; border-top: 1px solid #f1f5f9; background: #f8fafc; }
.record-info { font-size: 0.88rem; color: #64748b; font-weight: 500; }
.record-info .count { color: #0f172a; font-weight: 800; }
.spacer { flex: 1; }
.btn-secondary { background: #fff; color: #475569; border: 1px solid #e2e8f0; padding: 9px 20px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.92rem; transition: all 0.2s; }
.btn-secondary:hover { background: #f8fafc; border-color: #cbd5e1; }
</style>
