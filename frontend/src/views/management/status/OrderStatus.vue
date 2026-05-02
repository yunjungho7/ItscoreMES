<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">수주 현황</div>
      <div class="search-row">
        <label>수주일자</label>
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
        <label>수주상태</label>
        <select v-model="state">
          <option value="">전체</option>
          <option value="NEW">신규</option>
          <option value="CONFIRMED">확정</option>
          <option value="DONE">완료</option>
          <option value="CANCEL">취소</option>
        </select>
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- 요약 카드 -->
    <div class="summary-cards">
      <div class="card card-total"><div class="card-label">전체 건수</div><div class="card-val">{{ summary.total }}</div></div>
      <div class="card card-new"><div class="card-label">신규</div><div class="card-val">{{ summary.newCnt }}</div></div>
      <div class="card card-confirm"><div class="card-label">확정</div><div class="card-val">{{ summary.confirmed }}</div></div>
      <div class="card card-done"><div class="card-label">완료</div><div class="card-val">{{ summary.done }}</div></div>
      <div class="card card-amt"><div class="card-label">수주 금액</div><div class="card-val">{{ summary.totalAmt?.toLocaleString() || 0 }}<small>원</small></div></div>
    </div>

    <!-- 그리드 -->
    <div class="grid-area">
      <DataGrid :columns="cols" :rows="rows" :loading="loading"
                :page="page" :totalPages="totalPages" :total="total"
                @page-change="onPage" />
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
const rows = ref<any[]>([]), loading = ref(false);
const page = ref(1), totalPages = ref(0), total = ref(0);

const cols = [
  { key: 'ORDERNO', label: '수주번호', width: '90px' },
  { key: 'ORDERDT', label: '수주일자', width: '100px', type: 'date' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '고객사', width: '140px' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '100px', type: 'date' },
  { key: 'ORDERSTATE', label: '수주상태', width: '80px' },
  { key: 'ITEM_COUNT', label: '품목수', width: '60px' },
  { key: 'TOTAL_QTY', label: '총수량', width: '80px' },
  { key: 'TOTAL_AMT', label: '총금액', width: '100px' },
  { key: 'REMARK', label: '비고', minWidth: '120px' },
];

const summary = computed(() => {
  const data = rows.value;
  return {
    total: total.value,
    newCnt: data.filter(r => r.ORDERSTATE === 'NEW' || !r.ORDERSTATE).length,
    confirmed: data.filter(r => r.ORDERSTATE === 'CONFIRMED' || r.ORDERSTATE === '확정').length,
    done: data.filter(r => r.ORDERSTATE === 'DONE' || r.ORDERSTATE === '완료').length,
    totalAmt: data.reduce((s, r) => s + (Number(r.TOTAL_AMT) || 0), 0)
  };
});

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchData() {
  loading.value = true;
  try {
    const p: any = { page: page.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    if (state.value) p.state = state.value;
    const r = await api.get('/api/order/list', { params: p });
    const result = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    rows.value = result;
    total.value = (r.data?.data?.total ?? r.data?.total ?? 0);
    totalPages.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { loading.value = false; }
}
function onPage(p: number) { page.value = p; fetchData(); }

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
.page-view{display:flex;flex-direction:column;gap:12px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#8e44ad;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e8daef}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:100px}
.sep{color:#b2bec3;font-weight:600}
.btn-search{background:#8e44ad;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 요약 카드 */
.summary-cards{display:flex;gap:12px;flex-wrap:wrap}
.card{flex:1;min-width:140px;background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:4px}
.card-label{font-size:.78rem;font-weight:600;color:#95a5a6;text-transform:uppercase;letter-spacing:.5px}
.card-val{font-size:1.4rem;font-weight:800;color:#2c3e50}
.card-val small{font-size:.7rem;font-weight:600;color:#95a5a6;margin-left:2px}
.card-total{border-left:4px solid #8e44ad}.card-total .card-val{color:#8e44ad}
.card-new{border-left:4px solid #3498db}.card-new .card-val{color:#3498db}
.card-confirm{border-left:4px solid #e67e22}.card-confirm .card-val{color:#e67e22}
.card-done{border-left:4px solid #27ae60}.card-done .card-val{color:#27ae60}
.card-amt{border-left:4px solid #2c3e50}

/* 그리드 */
.grid-area{flex:1;min-height:0}
</style>
