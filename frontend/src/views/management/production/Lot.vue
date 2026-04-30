<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">LOT 관리</div>
      <div class="search-row">
        <label>생성일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        <label>LOT No.</label>
        <input type="text" v-model="searchLotNo" placeholder="LOT No 입력" @keyup.enter="fetchData" />
        <label>품번/품명</label>
        <div class="input-with-btn">
          <input type="text" v-model="searchPartNo" placeholder="품번 또는 품명" @keyup.enter="fetchData" />
          <button class="btn-search-sm" @click="fetchData">🔍</button>
        </div>
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- ═══ 툴바 및 마스터 그리드 ═══ -->
    <div class="grid-wrap">
      <div class="toolbar">
        <div class="toolbar-title">LOT 정보</div>
        <div class="toolbar-actions">
          <button class="btn-track" @click="openTrackModal">🔍 Lot 추적</button>
          <button class="btn-create" @click="openCreateModal">⚙️ Lot 생성</button>
        </div>
      </div>
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onRow" @page-change="onPg" />
    </div>

    <!-- ═══ LOT 생성 모달 ═══ -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate=false">
      <div class="modal create-modal">
        <div class="modal-header">
          <h2>LOT생성정보</h2>
          <div class="modal-actions">
            <button class="btn-init" @click="resetCreateForm">초기화</button>
            <button class="btn-save" @click="handleCreate">생성</button>
            <button class="btn-close" @click="showCreate=false">닫기</button>
          </div>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <label>LOT구분</label>
            <select v-model="cForm.LOTTYPE"><option value="일반">일반</option><option value="재작업">재작업</option></select>
            
            <label>품번</label>
            <div class="input-with-btn">
              <input type="text" v-model="cForm.PARTNO" placeholder="품번" style="width:100px" />
              <input type="text" v-model="cForm.PARTNM" readonly placeholder="품명" />
              <button class="btn-search-sm" @click="showItemPicker=true">🔍</button>
            </div>
            
            <label>단위</label>
            <input type="text" v-model="cForm.UNIT" readonly />
            
            <label>LOT기준수량</label>
            <input type="number" value="0" readonly />
            
            <label>생성LOT수량</label>
            <input type="number" v-model.number="cForm.LOTQTY" />
            
            <label>창고</label>
            <select v-model="cForm.WAREHOUSECODE">
              <option value="">선택</option>
              <option v-for="w in warehouses" :key="w.WAREHOUSECODE" :value="w.WAREHOUSECODE">{{ w.WAREHOUSENAME }}</option>
            </select>
            
            <label>로케이션</label>
            <select v-model="cForm.LOCATIONCODE">
              <option value="">선택</option>
              <option v-for="l in locations" :key="l.LOCATIONCODE" :value="l.LOCATIONCODE">{{ l.LOCATIONNAME }}</option>
            </select>
            
            <label>생성일시</label>
            <div class="datetime-inputs">
              <input type="date" v-model="cForm.LOTCREATIONDAY" />
            </div>
            
            <label>비고</label>
            <input type="text" v-model="cForm.REMARK" class="full-width" />
          </div>
          
          <div class="sub-info">
            <h3>부가정보</h3>
            <div class="form-grid">
              <label>작업지시서No</label><input type="text" v-model="cForm.WORKORDNO" />
              <label>라인</label><input type="text" v-model="cForm.LINECD" />
              <label>공정</label><input type="text" v-model="cForm.PROCESSCD" />
              <label>근무조</label><select v-model="cForm.SHIFT"><option value="">선택</option><option value="주간">주간</option><option value="야간">야간</option></select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ LOT 추적 모달 ═══ -->
    <div v-if="showTrack" class="modal-overlay" @click.self="showTrack=false">
      <div class="modal track-modal">
        <div class="modal-header">
          <h2>LOT추적정보</h2>
          <div class="modal-actions">
            <button class="btn-track" @click="fetchTracking">조회</button>
            <button class="btn-close" @click="showTrack=false">닫기</button>
          </div>
        </div>
        <div class="modal-body track-body">
          <div class="track-filters">
            <label>LOT No.</label><input type="text" v-model="trackLotNo" @keyup.enter="fetchTracking" />
            <label>추적구분</label>
            <select v-model="trackType">
              <option value="정방향">정방향</option>
              <option value="역방향">역방향</option>
            </select>
            <label><input type="checkbox" /> 입고정보포함</label>
          </div>
          <div class="track-grid-wrap">
            <DataGrid :columns="tCols" :rows="tRows" :loading="tl" />
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ 품목 선택 팝업 ═══ -->
    <div v-if="showItemPicker" class="modal-overlay" @click.self="showItemPicker=false" style="z-index: 2000;">
      <div class="picker-modal">
        <div class="picker-header"><h3>품목 선택</h3><button @click="showItemPicker=false">✕</button></div>
        <div class="picker-search">
          <input type="text" v-model="itemSearch" placeholder="검색" @keyup.enter="fetchItems" />
          <button @click="fetchItems">조회</button>
        </div>
        <div class="picker-list">
          <table>
            <thead><tr><th>품번</th><th>품명</th><th>단위</th></tr></thead>
            <tbody>
              <tr v-for="g in itemsList" :key="g.PARTNO" @click="selectItem(g)">
                <td>{{ g.PARTNO }}</td><td>{{ g.PARTNM }}</td><td>{{ g.UNIT }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

// ── 날짜 및 유틸 ──
const d = new Date(), m30 = new Date(d); m30.setMonth(m30.getMonth() - 3);
const f = (v: Date) => v.toISOString().slice(0, 10);

// ── 조회 조건 ──
const startDate = ref(f(m30)), endDate = ref(f(d));
const searchLotNo = ref(''), searchPartNo = ref('');

// ── 목록 컬럼 ──
const mCols = [
  { key: 'LOTNO', label: 'Lot No.', width: '160px' },
  { key: 'LOTHISTORYNO', label: '이력순번', width: '80px', align: 'right' },
  { key: 'PARTNO', label: '품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'LOTQTY', label: 'LOT 수량', width: '80px', align: 'right' },
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'LINECD', label: '라인', width: '70px', align: 'center' },
  { key: 'PROCESSCD', label: '공정', width: '70px', align: 'center' },
  { key: 'MERGELOTNO', label: '병합 Lot No.', width: '140px' },
  { key: 'SEPARATELOTNO', label: '분할 Lot No.', width: '140px' },
];

const mRows = ref<any[]>([]);
const ld = ref(false), si = ref(-1), sel = ref<any>(null);
const pg = ref(1), tp = ref(0), tot = ref(0);

async function fetchData() {
  ld.value = true; si.value = -1; sel.value = null;
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (searchLotNo.value) p.lot_no = searchLotNo.value;
    if (searchPartNo.value) p.part_no = searchPartNo.value;
    const r = await api.get('/api/production/lot', { params: p });
    mRows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    tot.value = (r.data?.data?.total ?? r.data?.total ?? 0); tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { ld.value = false; }
}

function onPg(p: number) { pg.value = p; fetchData(); }
function onRow(row: any, idx: number) { si.value = idx; sel.value = row; }

// ── LOT 생성 모달 ──
const showCreate = ref(false);
const cForm = ref({
  LOTTYPE: '일반', PARTNO: '', PARTNM: '', UNIT: '', LOTQTY: 0,
  WAREHOUSECODE: '', LOCATIONCODE: '', LOTCREATIONDAY: f(new Date()), REMARK: '',
  WORKORDNO: '', LINECD: '', PROCESSCD: '', SHIFT: ''
});
const warehouses = ref<any[]>([]), locations = ref<any[]>([]);

async function fetchMasterData() {
  try {
    const [rw, rl] = await Promise.all([
      api.get('/api/master/warehouse', { params: { size: 100 } }),
      api.get('/api/master/location', { params: { size: 200 } })
    ]);
    warehouses.value = rw.data.data || [];
    locations.value = rl.data.data || [];
  } catch {}
}

function openCreateModal() { resetCreateForm(); showCreate.value = true; }
function resetCreateForm() {
  cForm.value = {
    LOTTYPE: '일반', PARTNO: '', PARTNM: '', UNIT: '', LOTQTY: 0,
    WAREHOUSECODE: '', LOCATIONCODE: '', LOTCREATIONDAY: f(new Date()), REMARK: '',
    WORKORDNO: '', LINECD: '', PROCESSCD: '', SHIFT: ''
  };
}

async function handleCreate() {
  if (!cForm.value.PARTNO || cForm.value.LOTQTY <= 0) { alert('품번과 수량을 입력하세요.'); return; }
  try {
    await api.post('/api/production/lot', cForm.value);
    alert('LOT이 생성되었습니다.');
    showCreate.value = false;
    fetchData();
  } catch (e: any) { alert('생성 실패: ' + e.message); }
}

// 품목 팝업
const showItemPicker = ref(false), itemSearch = ref(''), itemsList = ref<any[]>([]);
async function fetchItems() {
  const r = await api.get('/api/master/goods', { params: { search: itemSearch.value, size: 50 } });
  itemsList.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
}
function selectItem(g: any) {
  cForm.value.PARTNO = g.PARTNO; cForm.value.PARTNM = g.PARTNM; cForm.value.UNIT = g.UNIT;
  showItemPicker.value = false;
}

// ── LOT 추적 모달 ──
const showTrack = ref(false), trackLotNo = ref(''), trackType = ref('정방향');
const tl = ref(false), tRows = ref<any[]>([]);
const tCols = [
  { key: 'MAT_LOTNO', label: 'LOT No.', width: '150px' },
  { key: 'DEPTH', label: 'Depth', width: '60px', align: 'center' },
  { key: 'PARTNO', label: '품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'CREATIONDAY', label: '생성일자', width: '100px' },
  { key: 'UNIT', label: '단위', width: '60px' },
  { key: 'LOTQTY', label: 'LOT수량', width: '80px', align: 'right' },
  { key: 'REL_INFO', label: '관련정보', width: '100px' },
  { key: 'PROCESSCD', label: '공정', width: '80px' },
  { key: 'REL_TARGET', label: '관련처', width: '140px' }
];

function openTrackModal() {
  if (!sel.value) { alert('추적할 LOT를 선택하세요.'); return; }
  trackLotNo.value = sel.value.LOTNO;
  tRows.value = [];
  showTrack.value = true;
  fetchTracking();
}

async function fetchTracking() {
  if (!trackLotNo.value) return;
  tl.value = true;
  try {
    const r = await api.get(`/api/production/lot/tracking/${trackLotNo.value}`);
    tRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []);
  } catch (e: any) { alert('추적 실패'); }
  finally { tl.value = false; }
}

onMounted(() => { fetchMasterData(); fetchData(); });
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.section-title { font-size: .85rem; font-weight: 700; color: #1a5276; margin-bottom: 8px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; margin-left: 8px; }
.search-row input { padding: 6px 10px; border: 1px solid #dfe6e9; border-radius: 4px; font-size: .85rem; }
.input-with-btn { display: flex; align-items: stretch; }
.input-with-btn input { flex: 1; border-radius: 4px 0 0 4px; border-right: none; }
.btn-search-sm { background: #eaf2f8; color: #2980b9; border: 1px solid #dfe6e9; padding: 0 10px; border-radius: 0 4px 4px 0; cursor: pointer; }
.btn-search { background: #2980b9; color: #fff; border: none; padding: 6px 16px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #eaf2f8; border-bottom: 1px solid #d6eaf8; }
.toolbar-title { font-weight: 700; color: #1a5276; }
.toolbar-actions { display: flex; gap: 8px; }
.btn-track { background: #34495e; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; }
.btn-create { background: #27ae60; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: .85rem; }

/* 모달 공통 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.modal { background: #fff; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,.2); overflow: hidden; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #5f9ea0; color: #fff; }
.modal-header h2 { margin: 0; font-size: 1.1rem; }
.modal-actions button { margin-left: 6px; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }
.btn-init { background: #f1f2f6; color: #2f3640; }
.btn-save { background: #2980b9; color: #fff; }
.btn-close { background: #e74c3c; color: #fff; }
.modal-body { padding: 20px; flex: 1; overflow-y: auto; background: #f8f9fa; }

/* 생성 모달 */
.create-modal { width: 600px; max-height: 90vh; }
.form-grid { display: grid; grid-template-columns: 100px 1fr; gap: 10px; align-items: center; margin-bottom: 20px; }
.form-grid label { font-size: .85rem; font-weight: 600; color: #2c3e50; text-align: right; padding-right: 10px; }
.form-grid input, .form-grid select { padding: 6px; border: 1px solid #ced4da; border-radius: 4px; font-size: .85rem; width: 100%; }
.full-width { grid-column: 2; }
.sub-info { background: #e9ecef; padding: 15px; border-radius: 6px; }
.sub-info h3 { font-size: .9rem; margin-top: 0; margin-bottom: 10px; color: #6c757d; }

/* 추적 모달 */
.track-modal { width: 900px; max-height: 85vh; }
.track-body { display: flex; flex-direction: column; gap: 10px; }
.track-filters { display: flex; align-items: center; gap: 12px; padding: 10px; background: #fff; border-radius: 4px; border: 1px solid #dee2e6; }
.track-filters label { font-size: .85rem; font-weight: 600; }
.track-filters input[type=text], .track-filters select { padding: 4px 8px; border: 1px solid #ced4da; border-radius: 4px; }
.track-grid-wrap { flex: 1; min-height: 400px; background: #fff; }

/* 팝업 */
.picker-modal { background: #fff; width: 400px; border-radius: 6px; display: flex; flex-direction: column; }
.picker-header { padding: 10px; background: #eaf2f8; display: flex; justify-content: space-between; }
.picker-search { padding: 10px; display: flex; gap: 5px; }
.picker-list { max-height: 300px; overflow: auto; padding: 0 10px 10px; }
.picker-list table { width: 100%; border-collapse: collapse; }
.picker-list th, .picker-list td { border-bottom: 1px solid #eee; padding: 6px; font-size: .85rem; }
.picker-list tr:hover { background: #f1f2f6; cursor: pointer; }
</style>
