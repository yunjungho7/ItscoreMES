<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">작업일보관리</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        
        <label>공정</label>
        <select v-model="processCd">
          <option value="">(선택하세요)</option>
          <option v-for="pr in processes" :key="pr.PROCESSCD" :value="pr.PROCESSCD">{{ pr.PROCESSNM }}</option>
        </select>
      </div>
      <div class="search-row" style="margin-top: 10px;">
        <label>작업일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        
        <label>근무조</label>
        <select v-model="shift">
          <option value="">(선택하세요)</option>
          <option value="주간">주간</option>
          <option value="야간">야간</option>
        </select>
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- ═══ 툴바 및 그리드 ═══ -->
    <div class="grid-wrap">
      <div class="toolbar">
        <div class="toolbar-actions">
          <button class="btn-edit" @click="editResult">📝 작업실적수정</button>
          <button class="btn-print" @click="printReport">🖨️ 작업일보 출력</button>
        </div>
      </div>
      <DataGrid :columns="cols" :rows="rows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onRow" @page-change="onPg" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

// ── 날짜 및 유틸 ──
const d = new Date(), m30 = new Date(d); m30.setDate(m30.getDate() - 30);
const f = (v: Date) => v.toISOString().slice(0, 10);

// ── 상태 및 검색 조건 ──
const startDate = ref(f(m30)), endDate = ref(f(d));
const plantCd = ref(''), processCd = ref(''), shift = ref('');
const plants = ref<any[]>([]), processes = ref<any[]>([]);

// ── 그리드 컬럼 ──
const cols = [
  { key: 'WORKDAY', label: '작업일자', width: '100px', align: 'center' },
  { key: 'WORKER', label: '작업자', width: '80px', align: 'center' },
  { key: 'PROCESSCD', label: '공정', width: '80px', align: 'center' },
  { key: 'LOTNO', label: '작업 LOT 번호', width: '150px' },
  { key: 'PARTNO', label: '품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'CUSTOMPARTNO', label: '고객사품번', width: '120px' },
  { key: 'UNIT', label: '단위', width: '60px', align: 'center' },
  { key: 'ORDQTY', label: '지시수량', width: '80px', align: 'right' },
  { key: 'PRODQTY', label: '생산실적수량', width: '90px', align: 'right' },
  { key: 'GOODQTY', label: '양품수량', width: '80px', align: 'right' },
  { key: 'FAILQTY', label: '불량수량', width: '80px', align: 'right' },
  { key: 'STATUS', label: '상태', width: '70px', align: 'center' }
];

const rows = ref<any[]>([]);
const ld = ref(false), si = ref(-1), sel = ref<any>(null);
const pg = ref(1), tp = ref(0), tot = ref(0);

// ── 데이터 가져오기 ──
async function fetchMasterData() {
  try {
    const [rp, rpr] = await Promise.all([
      api.get('/api/master/plant', { params: { size: 100 } }),
      api.get('/api/master/process', { params: { size: 100 } })
    ]);
    plants.value = rp.data.data || [];
    processes.value = rpr.data.data || [];
  } catch {}
}

async function fetchData() {
  ld.value = true; si.value = -1; sel.value = null;
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (processCd.value) p.process_cd = processCd.value;
    if (shift.value) p.shift = shift.value;
    
    const r = await api.get('/api/production/daily-report', { params: p });
    rows.value = r.data.data || [];
    tot.value = r.data.total; tp.value = r.data.totalPages;
  } finally { ld.value = false; }
}

function onPg(p: number) { pg.value = p; fetchData(); }
function onRow(row: any, idx: number) { si.value = idx; sel.value = row; }

function editResult() {
  if (!sel.value) return alert('수정할 항목을 선택하세요.');
  alert('작업실적 수정 팝업 호출 예정 (선택된 LOT: ' + sel.value.LOTNO + ')');
}

function printReport() {
  window.print();
}

onMounted(() => { fetchMasterData(); fetchData(); });
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.section-title { font-size: .85rem; font-weight: 700; color: #1a5276; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; margin-left: 8px; min-width: 60px; }
.search-row label:first-child { margin-left: 0; }
.search-row input, .search-row select { padding: 6px 10px; border: 1px solid #dfe6e9; border-radius: 4px; font-size: .85rem; min-width: 150px; }
.search-row input[type=date] { width: 140px; }
.btn-search { background: #2980b9; color: #fff; border: none; padding: 6px 16px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: flex-end; align-items: center; padding: 10px 16px; background: #eaf2f8; border-bottom: 1px solid #d6eaf8; }
.toolbar-actions { display: flex; gap: 8px; }
.btn-edit { background: #f39c12; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; font-weight: 600; }
.btn-print { background: #34495e; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; font-weight: 600; }

@media print {
  .search-section, .toolbar, .pagination { display: none !important; }
  .grid-wrap { box-shadow: none; border: none; }
}
</style>
