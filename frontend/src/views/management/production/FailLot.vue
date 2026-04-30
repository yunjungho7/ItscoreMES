<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">불량 전환</div>
      <div class="search-row">
        <label>일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
      </div>
      <div class="search-row" style="margin-top: 10px;">
        <label>LOT No.</label>
        <input type="text" v-model="searchLotNo" placeholder="LOT No 입력" @keyup.enter="fetchData" />
        
        <label>불량구분</label>
        <label class="chk-label"><input type="checkbox" value="공정불량" v-model="failGubuns" /> 공정불량</label>
        <label class="chk-label"><input type="checkbox" value="반품불량" v-model="failGubuns" /> 반품불량</label>
        <label class="chk-label"><input type="checkbox" value="입고불량" v-model="failGubuns" /> 입고불량</label>
        
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- ═══ 툴바 및 그리드 ═══ -->
    <div class="grid-wrap">
      <div class="toolbar">
        <div class="toolbar-title">불량 LOT 관리</div>
        <div class="toolbar-actions">
          <button class="btn-recover" @click="processItems('recover')">♻️ 양품처리</button>
          <button class="btn-scrap" @click="processItems('scrap')">🗑️ 폐기처리</button>
        </div>
      </div>
      <DataGrid :columns="cols" :rows="rows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onRow" @page-change="onPg">
        <template #cell-SELECT="{ index }">
          <input type="checkbox" v-model="selectedItems[index]" @click.stop />
        </template>
        <template #cell-CONVERT_QTY="{ row }">
          <input type="number" v-model.number="row.CONVERT_QTY" class="grid-input" @click.stop />
        </template>
      </DataGrid>
    </div>
  </div>
</template>

<script setup lang="ts">
const window = globalThis.window;
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

// ── 유틸 및 상태 ──
const d = new Date(), m1 = new Date(d); m1.setMonth(m1.getMonth() - 1);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m1)), endDate = ref(f(d));
const plantCd = ref(''), searchLotNo = ref('');
const failGubuns = ref<string[]>(['공정불량', '반품불량', '입고불량']);
const plants = ref<any[]>([]);

// ── 컬럼 ──
const cols = [
  { key: 'SELECT', label: '선택', width: '50px', align: 'center' },
  { key: 'LOTNO', label: 'Lot No.', width: '150px' },
  { key: 'FAILGUBUN', label: '불량구분', width: '80px', align: 'center' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'FAILQTY', label: '불량수량', width: '80px', align: 'right' },
  { key: 'FAILTYPE', label: '불량유형', width: '80px' },
  { key: 'FAILBREAKDOWN', label: '불량원인', width: '100px' },
  { key: 'CONVERT_QTY', label: '전환수량', width: '80px', align: 'center' },
  { key: 'REMARK', label: '비고', width: '120px' },
  { key: 'IN_WAREHOUSE', label: '입고창고', width: '80px' },
  { key: 'REGDATE', label: '일자', width: '100px', align: 'center' },
  { key: 'CUSTOMPARTNO', label: '고객사품번', width: '100px' },
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'LINECD', label: '라인', width: '70px', align: 'center' },
];

const rows = ref<any[]>([]);
const ld = ref(false), si = ref(-1);
const selectedItems = ref<boolean[]>([]);
const pg = ref(1), tp = ref(0), tot = ref(0);

// ── 데이터 처리 ──
async function fetchMaster() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}

async function fetchData() {
  ld.value = true; si.value = -1;
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchLotNo.value) p.lot_no = searchLotNo.value;
    if (failGubuns.value.length > 0) p.fail_gubuns = failGubuns.value.join(',');

    const r = await api.get('/api/production/fail-lot', { params: p });
    rows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    selectedItems.value = new Array(rows.value.length).fill(false);
    tot.value = (r.data?.data?.total ?? r.data?.total ?? 0); tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { ld.value = false; }
}

function onPg(p: number) { pg.value = p; fetchData(); }
function onRow(_row: any, idx: number) { si.value = idx; selectedItems.value[idx] = !selectedItems.value[idx]; }

// ── 양품/폐기 처리 ──
async function processItems(action: 'recover' | 'scrap') {
  const itemsToProcess = rows.value.filter((_, idx) => selectedItems.value[idx]);
  if (itemsToProcess.length === 0) return window.alert('처리할 항목을 선택하세요.');
  
  const actionName = action === 'recover' ? '양품처리' : '폐기처리';
  if (!window.confirm(`선택한 ${itemsToProcess.length}개 항목을 ${actionName} 하시겠습니까?`)) return;

  try {
    await api.post(`/api/production/fail-lot/${action}`, itemsToProcess);
    window.alert(`${actionName}가 완료되었습니다.`);
    fetchData();
  } catch (e: any) { window.alert(`처리 실패: ${e.message}`); }
}

onMounted(() => { fetchMaster(); fetchData(); });
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.section-title { font-size: .85rem; font-weight: 700; color: #1a5276; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; margin-left: 8px; min-width: 50px; }
.search-row label:first-child { margin-left: 0; }
.search-row input[type=text], .search-row select, .search-row input[type=date] { padding: 6px 10px; border: 1px solid #dfe6e9; border-radius: 4px; font-size: .85rem; }
.chk-label { display: flex; align-items: center; gap: 4px; font-weight: 500 !important; cursor: pointer; color: #2d3436 !important; }
.btn-search { background: #2980b9; color: #fff; border: none; padding: 6px 16px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #eaf2f8; border-bottom: 1px solid #d6eaf8; }
.toolbar-title { font-weight: 700; color: #2c3e50; font-size: .95rem; }
.toolbar-actions { display: flex; gap: 8px; }
.btn-recover { background: #27ae60; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; font-weight: 600; }
.btn-scrap { background: #7f8c8d; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; font-weight: 600; }

.grid-input { width: 100%; padding: 4px; border: 1px solid #ccc; text-align: right; border-radius: 2px; }
</style>
