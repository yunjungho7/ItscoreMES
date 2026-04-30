<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title"><i class="fas fa-list-alt"></i> 생산대상 (수주현황)</div>
      <div class="search-row">
        <label>수주일자</label>
        <input type="date" v-model="searchParams.startDate" />
        <span>~</span>
        <input type="date" v-model="searchParams.endDate" />
        
        <label style="margin-left: 12px;">사업장</label>
        <select v-model="searchParams.plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        
        <label style="margin-left: 12px;">고객사</label>
        <input type="text" v-model="searchParams.search" placeholder="고객사명 검색" @keyup.enter="fetchOrders" />
        
        <button class="btn-search" @click="fetchOrders"><i class="fas fa-search"></i> 조회</button>
      </div>
    </section>

    <!-- 마스터 그리드 (수주현황) -->
    <div class="grid-section" style="flex: 1;">
      <DataGrid
        :columns="orderCols"
        :rows="orders"
        :loading="loadingOrders"
        :selectedIndex="selOrderIdx"
        :page="page"
        :totalPages="totalPages"
        :total="total"
        @row-click="onOrderClick"
        @page-change="onPageChange"
      />
    </div>

    <!-- 상세 그리드 (수주 상세 및 생산계획 연동) -->
    <div class="detail-section">
      <div class="detail-header">
        <div class="detail-title"><i class="fas fa-cubes"></i> 수주 품목 및 생산계획 등록</div>
        <div class="detail-actions">
          <button class="btn-plan" @click="openPlanModal" :disabled="checkedDetails.length === 0">
            <i class="fas fa-calendar-check"></i> 생산계획
          </button>
        </div>
      </div>
      <div class="grid-wrapper" style="height: 250px;">
        <DataGrid
          :columns="detailCols"
          :rows="details"
          :loading="loadingDetails"
        >
          <!-- 체크박스 컬럼 -->
          <template #cell-checkbox="{ row }">
            <div style="text-align: center;">
              <input type="checkbox" v-model="row._checked" />
            </div>
          </template>
          
          <!-- 상태 뱃지 -->
          <template #cell-ORDERSTATE="{ row }">
            <span class="badge" :class="row.ORDERSTATE === 'NEW' ? 'active' : 'inactive'">
              {{ row.ORDERSTATE }}
            </span>
          </template>

          <!-- 계획수량 입력 컬럼 -->
          <template #cell-PLANQTY="{ row }">
            <input type="number" v-model.number="row._PLANQTY" class="qty-input" min="0" />
          </template>
        </DataGrid>
      </div>
    </div>

    <!-- ═══ 생산계획 등록 팝업 ═══ -->
    <ProdPlanPopup
      :visible="showPlanModal"
      :order-row="orders[selOrderIdx]"
      :detail-row="selectedDetailRow"
      @close="showPlanModal = false"
      @save="submitPlan"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';
import ProdPlanPopup from './ProdPlanPopup.vue';

const d = new Date();
const d30 = new Date(d);
d30.setDate(d.getDate() - 30);
const f = (v: Date) => v.toISOString().slice(0, 10);

const searchParams = ref({
  startDate: f(d30),
  endDate: f(d),
  plantCd: '',
  search: ''
});

const plants = ref<any[]>([]);

// Master Grid State
const orders = ref<any[]>([]);
const loadingOrders = ref(false);
const selOrderIdx = ref(-1);
const page = ref(1);
const size = ref(50);
const totalPages = ref(1);
const total = ref(0);

const orderCols = [
  { key: 'ORDERNO', label: '수주번호', width: '130px' },
  { key: 'PLANTNM', label: '사업장', width: '150px' },
  { key: 'COMPANYNM', label: '고객사', minWidth: '180px' },
  { key: 'ORDERDT', label: '수주일자', width: '110px', type: 'date' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '110px', type: 'date' },
  { key: 'TOTALAMT', label: '총금액', width: '120px' },
  { key: 'ORDERSTATE', label: '상태', width: '100px' },
];

// Detail Grid State
const details = ref<any[]>([]);
const loadingDetails = ref(false);

const detailCols = [
  { key: 'checkbox', label: '선택', width: '60px' },
  { key: 'PARTNO', label: '품번', width: '150px' },
  { key: 'PARTNM', label: '품명', minWidth: '180px' },
  { key: 'STANDARD', label: '규격', width: '120px' },
  { key: 'UNIT', label: '단위', width: '80px' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '110px', type: 'date' },
  { key: 'REQQTY', label: '수주수량', width: '100px' },
  { key: 'PLANQTY', label: '계획수량', width: '120px' },
  { key: 'REMARK', label: '비고', minWidth: '150px' },
];

const checkedDetails = computed(() => details.value.filter(d => d._checked));

// Plan Modal State
const showPlanModal = ref(false);
const selectedDetailRow = ref<any>(null);

async function fetchPlants() {
  try {
    const r = await api.get('/api/master/plant', { params: { size: 100 } });
    plants.value = r.data.data || [];
  } catch {}
}

async function fetchOrders() {
  loadingOrders.value = true;
  selOrderIdx.value = -1;
  details.value = [];
  try {
    const p: any = { page: page.value, size: size.value };
    if (searchParams.value.startDate) p.start_date = searchParams.value.startDate;
    if (searchParams.value.endDate) p.end_date = searchParams.value.endDate;
    if (searchParams.value.plantCd) p.plant_cd = searchParams.value.plantCd;
    if (searchParams.value.search) p.search = searchParams.value.search;

    const r = await api.get('/api/order/list', { params: p });
    orders.value = r.data.data || [];
    total.value = r.data.total || 0;
    totalPages.value = r.data.totalPages || 1;
  } catch (e) {
    alert('수주 현황을 불러오지 못했습니다.');
  } finally {
    loadingOrders.value = false;
  }
}

function onPageChange(p: number) {
  page.value = p;
  fetchOrders();
}

async function onOrderClick(row: any, idx: number) {
  selOrderIdx.value = idx;
  await fetchDetails(row.ORDERNO);
}

async function fetchDetails(orderNo: string) {
  loadingDetails.value = true;
  try {
    const r = await api.get(`/api/order/detail/${orderNo}/items`);
    // Add reactivity for checkbox and plan qty
    details.value = (r.data || []).map((d: any) => ({
      ...d,
      _checked: false,
      _PLANQTY: d.REQQTY || 0
    }));
  } catch (e) {
    details.value = [];
    alert('수주 상세를 불러오지 못했습니다.');
  } finally {
    loadingDetails.value = false;
  }
}

function openPlanModal() {
  if (checkedDetails.value.length !== 1) {
    alert('단일 품목에 대해서만 상세 생산계획을 수립할 수 있습니다. 하나의 품목만 선택하세요.');
    return;
  }
  selectedDetailRow.value = checkedDetails.value[0];
  showPlanModal.value = true;
}

async function submitPlan(payloads: any[]) {
  try {
    await api.post('/api/production/plan/batch', payloads);
    alert('생산계획이 성공적으로 등록되었습니다.');
    showPlanModal.value = false;
    // Uncheck and reset
    details.value.forEach(d => d._checked = false);
    // Optionally refresh something
  } catch (e) {
    alert('생산계획 등록 중 오류가 발생했습니다.');
  }
}

onMounted(() => {
  fetchPlants();
  fetchOrders();
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 16px; height: 100%; background: #f8fafc; padding: 16px; }
.search-section { background: #fff; border-radius: 12px; padding: 18px 24px; box-shadow: 0 2px 8px rgba(0,0,0,.04); border: 1px solid #e2e8f0; }
.section-title { font-size: 1.1rem; font-weight: 800; color: #1e293b; letter-spacing: 0.5px; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; display:flex; align-items:center; }
.section-title i { margin-right: 8px; color: #3b82f6; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: 0.9rem; font-weight: 700; color: #475569; white-space: nowrap; }
.search-row input, .search-row select { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem; outline:none; transition: all 0.2s; background: #fff; }
.search-row input:focus, .search-row select:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
.btn-search { flex-shrink: 0; background: #64748b; color: #fff; border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.9rem; transition: background 0.2s; display:flex; align-items:center; gap:6px; margin-left: auto; }
.btn-search:hover { background: #475569; }

.grid-section { display: flex; flex-direction: column; min-height: 200px; }
.detail-section { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.04); border: 1px solid #e2e8f0; overflow: hidden; display: flex; flex-direction: column; }
.detail-header { padding: 14px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.detail-title { font-weight: 700; color: #334155; display:flex; align-items:center; gap:8px; }
.detail-title i { color: #8b5cf6; }

.btn-plan { background: #8b5cf6; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; display:flex; align-items:center; gap:6px; }
.btn-plan:hover:not(:disabled) { background: #7c3aed; transform: translateY(-1px); box-shadow: 0 4px 6px rgba(139,92,246,0.3); }
.btn-plan:disabled { background: #cbd5e1; cursor: not-allowed; }

.qty-input { width: 100%; padding: 6px 8px; border: 1px solid #cbd5e1; border-radius: 6px; text-align: right; font-weight: 700; color: #0f172a; outline: none; transition: all 0.2s; }
.qty-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

.badge { background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight:600; }
.badge.active { background: #dff9e8; color: #27ae60; }
.badge.inactive { background: #f1f5f9; color: #64748b; }

</style>
