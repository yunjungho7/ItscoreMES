<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">입고 실적</div>
      <div class="search-row">
        <label>입고일자</label>
        <input type="date" v-model="startDate" />
        <span class="sep">~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>거래처</label>
        <input type="text" v-model="searchText" placeholder="거래처명" @keyup.enter="fetchData" />
        <label>입고상태</label>
        <select v-model="state">
          <option value="">전체</option>
          <option value="입고">입고완료</option>
          <option value="검사대기">검사대기</option>
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
      <div class="card card-done">
        <div class="card-label">입고완료</div>
        <div class="card-val">{{ summary.done }}</div>
      </div>
      <div class="card card-wait">
        <div class="card-label">검사대기</div>
        <div class="card-val">{{ summary.waiting }}</div>
      </div>
      <div class="card card-qty">
        <div class="card-label">총 입고수량</div>
        <div class="card-val">{{ summary.totalQty?.toLocaleString() || 0 }}</div>
      </div>
      <div class="card card-amt">
        <div class="card-label">입고 금액</div>
        <div class="card-val">{{ summary.totalAmt?.toLocaleString() || 0 }}<small>원</small></div>
      </div>
    </div>

    <!-- 마스터-디테일 그리드 -->
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="loading" :selectedIndex="si"
                :page="page" :totalPages="totalPages" :total="total"
                @row-click="onMaster" @page-change="onPage" />
      <div class="detail-wrap">
        <div class="dh">입고 상세 <span v-if="sel">- {{ sel.RECEIVENO }}</span></div>
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
  { key: 'RECEIVENO', label: '입고번호', width: '120px' },
  { key: 'RECEIVEDT', label: '입고일자', width: '100px', type: 'date' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '거래처', width: '140px' },
  { key: 'PURCHASEORDERNO', label: '발주번호', width: '100px' },
  { key: 'RECEIVESTATE', label: '입고상태', width: '80px' },
  { key: 'REMARK', label: '비고', minWidth: '120px' },
];
const dCols = [
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'UNIT', label: '단위', width: '50px' },
  { key: 'RECEIVEQTY', label: '입고수량', width: '80px' },
  { key: 'UNIT_PRICE', label: '단가', width: '80px' },
  { key: 'INSPECTIONSTATE', label: '검사상태', width: '80px' },
  { key: 'WAREHOUSECD', label: '창고', width: '80px' },
  { key: 'REMARK', label: '비고', minWidth: '100px' },
];

const summary = computed(() => {
  const data = mRows.value;
  return {
    total: total.value,
    done: data.filter(r => r.RECEIVESTATE === '입고' || r.RECEIVESTATE === '완료').length,
    waiting: data.filter(r => r.RECEIVESTATE === '검사대기').length,
    totalQty: data.reduce((s, r) => s + (Number(r.TOTAL_QTY) || 0), 0),
    totalAmt: data.reduce((s, r) => s + (Number(r.TOTAL_AMT) || 0), 0)
  };
});

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}

async function fetchData() {
  loading.value = true; si.value = -1; sel.value = null; dRows.value = [];
  try {
    const p: any = { page: page.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    const r = await api.get('/api/receive/list', { params: p });
    mRows.value = r.data.data || [];
    total.value = r.data.total;
    totalPages.value = r.data.totalPages;
  } finally { loading.value = false; }
}

async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try {
    const r = await api.get(`/api/receive/detail/${row.RECEIVENO}/items`);
    dRows.value = r.data || [];
  } finally { dl.value = false; }
}

function onPage(p: number) { page.value = p; fetchData(); }

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
.page-view{display:flex;flex-direction:column;gap:12px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#2980b9;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #d6eaf8}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:100px}
.sep{color:#b2bec3;font-weight:600}
.btn-search{background:#2980b9;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 요약 카드 */
.summary-cards{display:flex;gap:12px;flex-wrap:wrap}
.card{flex:1;min-width:130px;background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:4px}
.card-label{font-size:.78rem;font-weight:600;color:#95a5a6;text-transform:uppercase;letter-spacing:.5px}
.card-val{font-size:1.4rem;font-weight:800;color:#2c3e50}
.card-val small{font-size:.7rem;font-weight:600;color:#95a5a6;margin-left:2px}
.card-total{border-left:4px solid #2980b9}.card-total .card-val{color:#2980b9}
.card-done{border-left:4px solid #27ae60}.card-done .card-val{color:#27ae60}
.card-wait{border-left:4px solid #f39c12}.card-wait .card-val{color:#f39c12}
.card-qty{border-left:4px solid #8e44ad}.card-qty .card-val{color:#8e44ad}
.card-amt{border-left:4px solid #2c3e50}

/* 마스터-디테일 */
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#eaf2f8;font-size:.85rem;font-weight:600;color:#1a5276;border-bottom:1px solid #d6eaf8}
.dh span{color:#2980b9}
</style>
