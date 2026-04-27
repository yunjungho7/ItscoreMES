<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">생산 현황</div>
      <div class="search-row">
        <label>생산일자</label>
        <input type="date" v-model="startDate" />
        <span class="sep">~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>검색</label>
        <input type="text" v-model="searchText" placeholder="품번, 품명, LOT" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- 요약 카드 -->
    <div class="summary-cards">
      <div class="card card-total">
        <div class="card-label">전체 생산 건수</div>
        <div class="card-val">{{ total }}</div>
      </div>
      <div class="card card-qty">
        <div class="card-label">총 생산수량</div>
        <div class="card-val">{{ totalQty.toLocaleString() }}</div>
      </div>
      <div class="card card-done">
        <div class="card-label">평균 생산량</div>
        <div class="card-val">{{ avgQty.toFixed(1) }}</div>
      </div>
    </div>

    <!-- 마스터-디테일 그리드 -->
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="loading" :selectedIndex="si"
                :page="page" :totalPages="totalPages" :total="total"
                @row-click="onMaster" @page-change="onPage" />
      <div class="detail-wrap">
        <div class="dh">불량 상세 <span v-if="sel">- {{ sel.LOTNO }}</span></div>
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
const searchText = ref(''), plants = ref<any[]>([]);
const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const loading = ref(false), dl = ref(false), si = ref(-1), sel = ref<any>(null);
const page = ref(1), totalPages = ref(0), total = ref(0);

const mCols = [
  { key: 'WORKDAY', label: '생산일자', width: '100px' },
  { key: 'LOTNO', label: 'LOT번호', width: '150px' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '160px' },
  { key: 'STANDARD', label: '규격', width: '100px' },
  { key: 'LOTQTY', label: '생산수량', width: '90px', align: 'right' },
  { key: 'UNIT', label: '단위', width: '60px', align: 'center' },
  { key: 'LINECD', label: '라인', width: '80px' },
  { key: 'PROCESSCD', label: '공정', width: '80px' },
  { key: 'SHIFT', label: '근무조', width: '80px' },
  { key: 'LOTSTATE', label: '상태', width: '80px' },
  { key: 'WORKORDNO', label: '작지번호', width: '130px' },
];

const dCols = [
  { key: 'FAILTYPE', label: '불량유형', width: '120px' },
  { key: 'FAILQTY', label: '불량수량', width: '100px', align: 'right' },
  { key: 'FAILBREAKDOWN', label: '불량상세', minWidth: '150px' },
  { key: 'REGDTM', label: '등록일시', width: '150px', type: 'datetime' },
];

const totalQty = computed(() => mRows.value.reduce((s, r) => s + (Number(r.LOTQTY) || 0), 0));
const avgQty = computed(() => total.value > 0 ? totalQty.value / total.value : 0);

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
    const r = await api.get('/api/status/production', { params: p });
    mRows.value = r.data.data || [];
    total.value = r.data.total;
    totalPages.value = r.data.totalPages;
  } finally { loading.value = false; }
}

async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try {
    const r = await api.get(`/api/status/production/${row.LOTNO}/defects`);
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
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:160px}.search-row select{min-width:100px}
.sep{color:#b2bec3;font-weight:600}
.btn-search{background:#2980b9;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

.summary-cards{display:flex;gap:12px;flex-wrap:wrap}
.card{flex:1;min-width:130px;background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:4px}
.card-label{font-size:.78rem;font-weight:600;color:#95a5a6;text-transform:uppercase;letter-spacing:.5px}
.card-val{font-size:1.4rem;font-weight:800;color:#2c3e50}
.card-total{border-left:4px solid #2980b9}.card-total .card-val{color:#2980b9}
.card-qty{border-left:4px solid #8e44ad}.card-qty .card-val{color:#8e44ad}
.card-done{border-left:4px solid #27ae60}.card-done .card-val{color:#27ae60}

.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#eaf2f8;font-size:.85rem;font-weight:600;color:#1a5276;border-bottom:1px solid #d6eaf8}
.dh span{color:#2980b9}
</style>
