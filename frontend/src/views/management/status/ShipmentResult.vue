<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">출하 실적</div>
      <div class="search-row">
        <label>출하일자</label>
        <input type="date" v-model="startDate" />
        <span class="sep">~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>고객사</label>
        <input type="text" v-model="searchText" placeholder="고객사명" @keyup.enter="fetchData" />
        <label>출하상태</label>
        <select v-model="state">
          <option value="">전체</option>
          <option value="대기">대기</option>
          <option value="출하">출하완료</option>
          <option value="반품">반품</option>
        </select>
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- 요약 카드 -->
    <div class="summary-cards">
      <div class="card card-total">
        <div class="card-label">전체 건수</div>
        <div class="card-val">{{ summary.total }}</div>
      </div>
      <div class="card card-wait">
        <div class="card-label">출하대기</div>
        <div class="card-val">{{ summary.waiting }}</div>
      </div>
      <div class="card card-done">
        <div class="card-label">출하완료</div>
        <div class="card-val">{{ summary.done }}</div>
      </div>
      <div class="card card-qty">
        <div class="card-label">총 출하수량</div>
        <div class="card-val">{{ summary.totalQty?.toLocaleString() || 0 }}</div>
      </div>
      <div class="card card-amt">
        <div class="card-label">출하 금액</div>
        <div class="card-val">{{ summary.totalAmt?.toLocaleString() || 0 }}<small>원</small></div>
      </div>
    </div>

    <!-- 마스터-디테일 그리드 -->
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="loading" :selectedIndex="si"
                :page="page" :totalPages="totalPages" :total="total"
                @row-click="onMaster" @page-change="onPage" />
      <div class="detail-wrap">
        <div class="dh">출하 상세 <span v-if="sel">- {{ sel.SHIPMENTINDICATIONNO }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

const d = new Date(), m30 = new Date(d); m30.setDate(m30.getDate() - 30);
const f = (v: Date) => v.toISOString().slice(0, 10);
const startDate = ref(f(m30)), endDate = ref(f(d)), plantCd = ref('');
const searchText = ref(''), state = ref(''), plants = ref<any[]>([]);
const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const loading = ref(false), dl = ref(false), si = ref(-1), sel = ref<any>(null);
const page = ref(1), totalPages = ref(0), total = ref(0);

const mCols = [
  { key: 'SHIPMENTINDICATIONNO', label: '출하지시번호', width: '130px' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '고객사', width: '140px' },
  { key: 'SHIPMENTPLANDAY', label: '출하계획일', width: '100px', type: 'date' },
  { key: 'SHIPMENTDAY', label: '출하일자', width: '100px', type: 'date' },
  { key: 'SHIPMENTGUBUN', label: '출하구분', width: '80px' },
  { key: 'SHIPMENTSTATUS', label: '상태', width: '80px' },
  { key: 'ORDERNO', label: '수주번호', width: '90px' },
  { key: 'REMARK', label: '비고', minWidth: '120px' },
];
const dCols = [
  { key: 'ORDERNO', label: '수주번호', width: '80px' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'UNIT', label: '단위', width: '50px' },
  { key: 'UNIT_PRICE', label: '단가', width: '80px' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '100px', type: 'date' },
  { key: 'SHIPMENTINDICATIONQTY', label: '지시수량', width: '80px' },
  { key: 'SHIPMENTQTY', label: '출하수량', width: '80px' },
  { key: 'SHIPMENTSTATUS', label: '상태', width: '80px' },
  { key: 'REMARK', label: '비고', minWidth: '100px' },
];

const summary = computed(() => {
  const data = mRows.value;
  return {
    total: total.value,
    waiting: data.filter(r => !r.SHIPMENTSTATUS || r.SHIPMENTSTATUS === '대기' || r.SHIPMENTSTATUS === 'NEW').length,
    done: data.filter(r => r.SHIPMENTSTATUS === '출하' || r.SHIPMENTSTATUS === '완료' || r.SHIPMENTSTATUS === 'DONE').length,
    totalQty: 0,
    totalAmt: 0
  };
});

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}

async function fetchData() {
  loading.value = true; si.value = -1; sel.value = null; dRows.value = [];
  try {
    const p: any = { page: page.value, size: 50, include_done: '1' };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    const r = await api.get('/api/shipment/list', { params: p });
    mRows.value = r.data.data || [];
    total.value = r.data.total;
    totalPages.value = r.data.totalPages;
  } finally { loading.value = false; }
}

async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try {
    const r = await api.get(`/api/shipment/detail/${row.SHIPMENTINDICATIONNO}/items`);
    dRows.value = r.data || [];
  } finally { dl.value = false; }
}

function onPage(p: number) { page.value = p; fetchData(); }

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
.page-view{display:flex;flex-direction:column;gap:12px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#e67e22;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #fef0e3}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:100px}
.sep{color:#b2bec3;font-weight:600}
.btn-search{background:#e67e22;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 요약 카드 */
.summary-cards{display:flex;gap:12px;flex-wrap:wrap}
.card{flex:1;min-width:130px;background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:4px}
.card-label{font-size:.78rem;font-weight:600;color:#95a5a6;text-transform:uppercase;letter-spacing:.5px}
.card-val{font-size:1.4rem;font-weight:800;color:#2c3e50}
.card-val small{font-size:.7rem;font-weight:600;color:#95a5a6;margin-left:2px}
.card-total{border-left:4px solid #e67e22}.card-total .card-val{color:#e67e22}
.card-wait{border-left:4px solid #f39c12}.card-wait .card-val{color:#f39c12}
.card-done{border-left:4px solid #27ae60}.card-done .card-val{color:#27ae60}
.card-qty{border-left:4px solid #8e44ad}.card-qty .card-val{color:#8e44ad}
.card-amt{border-left:4px solid #2c3e50}

/* 마스터-디테일 */
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#fef9f3;font-size:.85rem;font-weight:600;color:#8b5e34;border-bottom:1px solid #f5e6d3}
.dh span{color:#e67e22}
</style>
