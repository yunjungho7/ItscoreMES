<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">투입 자재</div>
      <div class="search-row">
        <label>작업일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <div class="input-with-btn" style="width: 250px;">
          <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchMaster" />
          <button class="btn-search-sm" @click="fetchMaster">🔍</button>
        </div>
        <label>근무조</label>
        <select v-model="shift">
          <option value="">(선택하세요)</option>
          <option value="주간">주간</option>
          <option value="야간">야간</option>
        </select>
        <button class="btn-search" @click="fetchMaster">조회</button>
      </div>
    </section>

    <!-- ═══ 그리드 영역 ═══ -->
    <div class="split-grids">
      <!-- 마스터 그리드: 작업 지시 목록 -->
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onMaster" @page-change="onPg" />
      
      <!-- 디테일 그리드: 자재 투입 내역 -->
      <div class="detail-wrap">
        <div class="dh">자재 투입 내역 <span v-if="sel">- {{ sel.WORKORDNO }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" :selectedIndex="di"
                  @row-click="onDetail" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

// ── 상태 및 검색 조건 ──
const d = new Date(), m30 = new Date(d); m30.setDate(m30.getDate() - 30);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m30)), endDate = ref(f(d)), plantCd = ref('');
const searchText = ref(''), shift = ref('');
const plants = ref<any[]>([]);

// ── 그리드 컬럼 ──
const mCols = [
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'SHIFT', label: '근무조', width: '60px' },
  { key: 'ORDpriority', label: '우선순위', width: '60px', align: 'center' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'ORDDATE', label: '작업일자', width: '100px', align: 'center' },
  { key: 'ORDQTY', label: '지시수량', width: '70px', align: 'right' },
  { key: 'UNIT', label: '단위', width: '50px', align: 'center' },
  { key: 'ORDSTATE', label: '상태', width: '60px', align: 'center' },
];

const dCols = [
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'WORKLOTNO', label: '작업 LOT 번호', width: '130px' },
  { key: 'PROCESSCD', label: '공정', width: '70px', align: 'center' },
  { key: 'MAT_PARTNO', label: '자재품번', width: '120px' },
  { key: 'MAT_PARTNM', label: '자재품명', width: '150px' },
  { key: 'MAT_LOTNO', label: '자재 LOT 번호', width: '150px' },
  { key: 'INPUT_QTY', label: '투입수량', width: '80px', align: 'right' },
  { key: 'UNIT', label: '단위', width: '50px', align: 'center' },
];

// ── 데이터 상태 ──
const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const ld = ref(false), dl = ref(false);
const si = ref(-1), sel = ref<any>(null); // 마스터 선택
const di = ref(-1), selResult = ref<any>(null); // 디테일 선택
const pg = ref(1), tp = ref(0), tot = ref(0);

// ── 데이터 가져오기 ──
async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}

async function fetchMaster() {
  ld.value = true; si.value = -1; sel.value = null; 
  dRows.value = []; di.value = -1; selResult.value = null;
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    if (shift.value) p.shift = shift.value;
    
    // 작업지시 목록 재사용
    const r = await api.get('/api/production/workorder', { params: p });
    mRows.value = r.data.data || [];
    tot.value = r.data.total; tp.value = r.data.totalPages;
  } finally { ld.value = false; }
}

async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row;
  di.value = -1; selResult.value = null;
  await fetchDetail(row.WORKORDNO);
}

async function fetchDetail(workordno: string) {
  dl.value = true;
  try {
    const r = await api.get(`/api/production/input-material/${workordno}`);
    dRows.value = r.data || [];
  } finally { dl.value = false; }
}

function onPg(p: number) { pg.value = p; fetchMaster(); }

function onDetail(row: any, idx: number) {
  di.value = idx; selResult.value = row;
}

onMounted(() => { fetchPlants(); fetchMaster(); });
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 6px rgba(0,0,0,.04); }
.section-title { font-size: .82rem; font-weight: 700; color: #2980b9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #d6eaf8; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; white-space: nowrap; margin-left: 8px; }
.search-row label:first-child { margin-left: 0; }
.search-row input, .search-row select { padding: 7px 10px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: .85rem; }
.search-row input[type=date] { width: 140px; }
.search-row select { min-width: 110px; }
.btn-search { background: #2980b9; color: #fff; border: none; padding: 7px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: .85rem; margin-left: auto; }

.input-with-btn { display: flex; align-items: stretch; }
.input-with-btn input { flex: 1; border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: none; }
.btn-search-sm { background: #eaf2f8; color: #2980b9; border: 1px solid #dfe6e9; border-left: none; padding: 0 10px; border-top-right-radius: 6px; border-bottom-right-radius: 6px; cursor: pointer; display: flex; align-items: center; }

.split-grids { flex: 1; display: flex; flex-direction: column; gap: 8px; min-height: 0; }
.split-grids > * { flex: 1; min-height: 0; }
.detail-wrap { display: flex; flex-direction: column; background: #fff; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,.05); overflow: hidden; }
.dh { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #eaf2f8; border-bottom: 1px solid #d6eaf8; font-size: .85rem; font-weight: 600; color: #1a5276; }
.dh span { color: #2980b9; }
</style>
