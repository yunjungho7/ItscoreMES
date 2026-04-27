<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">발주 현황</div>
      <div class="search-row">
        <label>생산계획일</label>
        <input type="date" v-model="startDate" />
        <span class="sep">~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- 요약 카드 -->
    <div class="summary-cards">
      <div class="card card-total"><div class="card-label">전체 건수</div><div class="card-val">{{ summary.total }}</div></div>
      <div class="card card-item"><div class="card-label">품목 종류</div><div class="card-val">{{ summary.items }}</div></div>
      <div class="card card-qty"><div class="card-label">총 계획수량</div><div class="card-val">{{ summary.totalQty?.toLocaleString() || 0 }}</div></div>
    </div>

    <!-- 그리드 -->
    <div class="grid-area">
      <DataGrid :columns="cols" :rows="rows" :loading="loading" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

const d = new Date(), m14 = new Date(d); m14.setDate(m14.getDate() + 14);
const f = (v: Date) => v.toISOString().slice(0, 10);
const startDate = ref(f(d)), endDate = ref(f(m14)), plantCd = ref('');
const searchText = ref(''), plants = ref<any[]>([]);
const rows = ref<any[]>([]), loading = ref(false);

const cols = [
  { key: 'PRODUCEDT', label: '생산계획일', width: '110px', type: 'date' },
  { key: 'PLANTCD', label: '사업장코드', width: '90px' },
  { key: 'PARTNO', label: '품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'STANDARD', label: '규격', width: '100px' },
  { key: 'UNIT', label: '단위', width: '60px' },
  { key: 'ORDERNUM', label: '수주번호', width: '100px' },
  { key: 'ORDERSEQ', label: '순번', width: '50px' },
  { key: 'PRODUCEQTY', label: '계획수량', width: '90px' },
];

const summary = computed(() => {
  const data = rows.value;
  const parts = new Set(data.map(r => r.PARTNO));
  return {
    total: data.length,
    items: parts.size,
    totalQty: data.reduce((s, r) => s + (Number(r.PRODUCEQTY) || 0), 0)
  };
});

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}
async function fetchData() {
  loading.value = true;
  try {
    const p: any = {};
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (searchText.value) p.search = searchText.value;
    const r = await api.get('/api/purchase/plan', { params: p });
    rows.value = r.data || [];
  } finally { loading.value = false; }
}

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
.page-view{display:flex;flex-direction:column;gap:12px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#16a085;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #d1f2eb}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:100px}
.sep{color:#b2bec3;font-weight:600}
.btn-search{background:#16a085;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 요약 카드 */
.summary-cards{display:flex;gap:12px;flex-wrap:wrap}
.card{flex:1;min-width:140px;background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:4px}
.card-label{font-size:.78rem;font-weight:600;color:#95a5a6;text-transform:uppercase;letter-spacing:.5px}
.card-val{font-size:1.4rem;font-weight:800;color:#2c3e50}
.card-total{border-left:4px solid #16a085}.card-total .card-val{color:#16a085}
.card-item{border-left:4px solid #2980b9}.card-item .card-val{color:#2980b9}
.card-qty{border-left:4px solid #e67e22}.card-qty .card-val{color:#e67e22}

/* 그리드 */
.grid-area{flex:1;min-height:0}
</style>
