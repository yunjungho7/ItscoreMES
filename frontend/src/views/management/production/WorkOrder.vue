<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 (SalesOrder 스타일) ═══ -->
    <section class="search-section">
      <div class="section-title">작업 지시 현황</div>
      <div class="search-row">
        <label>작업기간</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        
        <label>품번/품명</label>
        <div class="input-with-btn">
          <input type="text" v-model="searchText" placeholder="검색어 입력" @keyup.enter="fetchData" />
          <button class="btn-search-sm" @click="isMainItemPickerOpen = true">🔍</button>
        </div>
        
        <label>근무조</label>
        <select v-model="shift">
          <option value="">전체</option>
          <option value="주간">주간</option>
          <option value="야간">야간</option>
        </select>
        
        <label>상태</label>
        <select v-model="ordState">
          <option value="">전체</option>
          <option value="NEW">신규</option>
          <option value="STARTED">작업중</option>
          <option value="DONE">완료</option>
          <option value="HOLD">보류</option>
        </select>
        
        <button class="btn-search" @click="fetchData">조회</button>
        
        <div class="act-right">
          <button class="btn-add" @click="openRegister">＋ 작업지시 등록</button>
        </div>
      </div>
    </section>

    <!-- ═══ 마스터 그리드 ═══ -->
    <div class="split-grids">
      <div class="grid-wrap">
        <div class="dh">작업지시 목록 <span v-if="tot"> - Total {{ tot }}건</span></div>
        <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si"
                  :page="pg" :totalPages="tp" :total="tot"
                  @row-click="onMaster" @page-change="onPg" />
      </div>
      
      <div class="detail-wrap">
        <div class="dh">하위 작업지시 상세 <span v-if="sel"> [{{ sel.WORKORDNO }}]</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>

    <!-- ═══ 작업지시 등록 모달 연동 ═══ -->
    <WorkOrderModal 
      :visible="showReg"
      :form="regForm"
      :items="regItems"
      :plants="plants"
      :processes="processes"
      :lines="lines"
      @close="showReg = false"
      @save="handleSave"
      @clear="regItems = []"
      @open-item-picker="showItemPicker = true"
      @add-item="addItem"
      @remove-items="removeItems"
    />

    <!-- 공용 피커 -->
    <ItemPicker 
      :visible="showItemPicker" 
      @close="showItemPicker = false"
      @select="selectItem"
    />
    <ItemPicker 
      :visible="isMainItemPickerOpen" 
      @close="isMainItemPickerOpen = false" 
      @select="(g) => searchText = g.PARTNO" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';
import ItemPicker from '../../pickers/ItemPicker.vue';
import WorkOrderModal from '../../modals/WorkOrderModal.vue';

const d = new Date(), m7 = new Date(d); m7.setDate(m7.getDate() - 2);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m7)), endDate = ref(f(d)), plantCd = ref('');
const searchText = ref(''), shift = ref(''), ordState = ref('');
const plants = ref<any[]>([]), processes = ref<any[]>([]), lines = ref<any[]>([]);

const isMainItemPickerOpen = ref(false);

const mCols = [
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'ORDDATE', label: '작업일자', width: '100px' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '130px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'PROCESSNM', label: '공정', width: '90px' },
  { key: 'LINENM', label: '라인', width: '90px' },
  { key: 'EQUIPNM', label: '설비', width: '90px' },
  { key: 'ORDQTY', label: '지시수량', width: '70px' },
  { key: 'ORDTYPE', label: '작업구분', width: '70px' },
  { key: 'SHIFT', label: '근무조', width: '60px' },
  { key: 'ORDpriority', label: '우선순위', width: '60px' },
  { key: 'ORDSTATE', label: '상태', width: '60px' },
];
const dCols = [
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'ORDDATE', label: '작업일자', width: '100px' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '130px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'PROCESSNM', label: '공정', width: '90px' },
  { key: 'LINENM', label: '라인', width: '90px' },
  { key: 'ORDQTY', label: '지시수량', width: '70px' },
  { key: 'ORDSTATE', label: '상태', width: '60px' },
];

const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const ld = ref(false), dl = ref(false), si = ref(-1), sel = ref<any>(null);
const pg = ref(1), tp = ref(0), tot = ref(0);

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchProcesses() {
  try { const r = await api.get('/api/master/process', { params: { size: 200 } }); processes.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchLines() {
  try { const r = await api.get('/api/master/line', { params: { size: 200 } }); lines.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}

async function fetchData() {
  ld.value = true; si.value = -1; sel.value = null; dRows.value = [];
  try {
    const p: any = { page: pg.value, size: 50, parent_only: true };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    if (shift.value) p.shift = shift.value;
    if (ordState.value) p.ord_state = ordState.value;
    const r = await api.get('/api/production/workorder', { params: p });
    mRows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    tot.value = (r.data?.data?.total ?? r.data?.total ?? 0); tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { ld.value = false; }
}

async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try { const r = await api.get(`/api/production/workorder/${row.WORKORDNO}/children`); dRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []); }
  finally { dl.value = false; }
}
function onPg(p: number) { pg.value = p; fetchData(); }

// ── 등록 모달 ──
const showReg = ref(false);
const regForm = ref({
  WORKORDNO: '', PARTNO: '', PARTNM: '', UNIT: '',
  PLANTCD: '', ORDDATE: f(d), ORDTYPE: '일반', SHIFT: '주간',
  ORDQTY: 0, ORDpriority: 1, PROCESSCD: '', LINECD: '', REMARK: ''
});
const regItems = ref<any[]>([]);

function openRegister() {
  regForm.value = {
    WORKORDNO: '', PARTNO: '', PARTNM: '', UNIT: '',
    PLANTCD: plants.value.length ? plants.value[0].PLANTCD : '',
    ORDDATE: f(d), ORDTYPE: '일반', SHIFT: '주간',
    ORDQTY: 0, ORDpriority: 1, PROCESSCD: '', LINECD: '', REMARK: ''
  };
  regItems.value = [];
  showReg.value = true;
}

async function loadBomItems(partNo: string) {
  if (!partNo) return;
  try {
    const r = await api.get(`/api/master/bom/detail/${partNo}`);
    const rows = Array.isArray(r.data?.data) ? r.data.data : (r.data?.data?.data || []);
    const filtered = rows.filter((b: any) => {
      const type = b.PARTTYPE || '';
      const nm = b.PARTNM || '';
      const isRaw = type === 'PARTGUBUN003' || nm.includes('원자재') || nm.includes('원재료');
      const isSub = type === 'PARTGUBUN004' || nm.includes('부자재') || nm.includes('부재료');
      return !isRaw && !isSub;
    });

    const topItem = {
      ORDDATE: regForm.value.ORDDATE,
      PARTNO: regForm.value.PARTNO,
      PARTNM: regForm.value.PARTNM,
      STANDARD: '', 
      UNIT: regForm.value.UNIT,
      PROCESSCD: regForm.value.PROCESSCD || '', 
      LINECD: regForm.value.LINECD || '',
      SHIFT: regForm.value.SHIFT,
      ORDQTY: regForm.value.ORDQTY || 0,
      ORDSTATE: 'NEW',
      _sel: true,
      _isTop: true,
      _reqQty: 1
    };

    const childItems = filtered.map((b: any) => ({
      ORDDATE: regForm.value.ORDDATE,
      PARTNO: b.CHILD_PARTNO,
      PARTNM: b.PARTNM,
      STANDARD: b.STANDARD,
      UNIT: b.UNIT,
      PROCESSCD: b.PROCESSCD || '', 
      LINECD: '',
      SHIFT: regForm.value.SHIFT,
      ORDQTY: (regForm.value.ORDQTY || 0) * (b.REQQTY || 1),
      ORDSTATE: 'NEW',
      _sel: true,
      _reqQty: b.REQQTY || 1
    }));

    regItems.value = [topItem, ...childItems];
  } catch (err) { console.error('BOM 로드 실패:', err); }
}

function addItem() {
  if (!regForm.value.PARTNO) { alert('품번을 입력하세요.'); return; }
  regItems.value.push({
    ORDDATE: regForm.value.ORDDATE, PARTNO: regForm.value.PARTNO,
    PARTNM: regForm.value.PARTNM, STANDARD: '', UNIT: regForm.value.UNIT,
    PROCESSCD: regForm.value.PROCESSCD, LINECD: regForm.value.LINECD,
    SHIFT: regForm.value.SHIFT, ORDQTY: regForm.value.ORDQTY || 0,
    ORDSTATE: 'NEW', _sel: true
  });
}
function removeItems() {
  regItems.value = regItems.value.filter(r => !r._sel);
}

// 상단 폼 변경 시 그리드 동기화
watch(() => regForm.value.ORDQTY, (newQty) => {
  regItems.value.forEach(item => { if (item._reqQty) item.ORDQTY = (newQty || 0) * item._reqQty; });
});
watch(() => regForm.value.ORDDATE, (v) => {
  regItems.value.forEach(item => { if (item._isTop) item.ORDDATE = v; });
});
watch(() => regForm.value.SHIFT, (v) => {
  regItems.value.forEach(item => { if (item._isTop) item.SHIFT = v; });
});
watch(() => regForm.value.PROCESSCD, (v) => {
  regItems.value.forEach(item => { if (item._isTop) item.PROCESSCD = v; });
});
watch(() => regForm.value.LINECD, (v) => {
  regItems.value.forEach(item => { if (item._isTop) item.LINECD = v; });
});

async function handleSave() {
  const selected = regItems.value.filter(r => r._sel);
  if (selected.length === 0) { alert('저장할 품목을 선택하세요.'); return; }
  
  const payload = {
    header: {
      PLANTCD: regForm.value.PLANTCD,
      PARTNO: regForm.value.PARTNO,
      ORDDATE: regForm.value.ORDDATE,
      ORDQTY: regForm.value.ORDQTY,
      PROCESSCD: regForm.value.PROCESSCD || null,
      LINECD: regForm.value.LINECD || null,
      SHIFT: regForm.value.SHIFT,
      ORDTYPE: regForm.value.ORDTYPE,
      ORDpriority: regForm.value.ORDpriority,
      REMARK: regForm.value.REMARK
    },
    items: selected.map(item => ({
      PLANTCD: regForm.value.PLANTCD,
      PARTNO: item.PARTNO,
      ORDDATE: item.ORDDATE,
      ORDQTY: item.ORDQTY,
      PROCESSCD: item.PROCESSCD || null,
      LINECD: item.LINECD || null,
      SHIFT: item.SHIFT,
      ORDTYPE: regForm.value.ORDTYPE,
      ORDpriority: regForm.value.ORDpriority,
      REMARK: regForm.value.REMARK
    }))
  };

  try {
    const r = await api.post('/api/production/workorder/batch', payload);
    alert(`작업지시가 등록되었습니다. (상위: ${r.data.parent_workordno}, 하위: ${r.data.child_count}건)`);
    showReg.value = false;
    fetchData();
  } catch (err: any) {
    alert('등록 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
  }
}

// ── 품목 선택 ──
const showItemPicker = ref(false);
function selectItem(g: any) {
  regForm.value.PARTNO = g.PARTNO;
  regForm.value.PARTNM = g.PARTNM || '';
  regForm.value.UNIT = g.UNIT || '';
  showItemPicker.value = false;
  loadBomItems(g.PARTNO);
}

onMounted(() => { fetchPlants(); fetchProcesses(); fetchLines(); fetchData(); });
</script>

<style scoped>
/* 페이지 레이아웃 */
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.input-with-btn{display:flex;gap:4px;align-items:center}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:8px;cursor:pointer;font-size:1rem;height:34px}
.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}

/* 그리드 레이아웃 */
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.grid-wrap,.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden;flex:1}
.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}.dh span{color:#667eea}
</style>
