<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">생산 계획</div>
      <div class="search-row">
        <label>생산기준일</label>
        <input type="date" v-model="baseDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <div class="input-with-btn">
          <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchData" />
          <button class="btn-search-sm" @click="openItemLookup" title="검색">🔍</button>
        </div>
        <button class="btn-search" @click="fetchData">조회</button>
        
        <div class="act-right">
          <button class="btn-add" @click="openWoModal" :disabled="!hasChecked">✅ 작업 지시서 생성</button>
        </div>
      </div>
    </section>

    <!-- ═══ 메인 컨텐츠 영역 ═══ -->
    <div class="split-grids">
      <div class="grid-wrap">
        <div class="dh">생산 계획 현황 <span v-if="planData?.data?.length"> - Total {{ planData.data.length }}건</span></div>
        <div class="cal-grid-wrap">
          <table class="cal-grid" v-if="planData">
            <thead>
              <tr>
                <th class="fix center chk" style="padding:0"><input type="checkbox" v-model="allChecked" @change="toggleAll" /></th>
                <th class="fix">수주번호</th>
                <th class="fix">품번</th>
                <th class="fix">품명</th>
                <th class="fix center">규격</th>
                <th class="fix num">재고수량</th>
                <th class="fix num total-head">계획합계</th>
                <th v-for="dt in dates" :key="dt" class="date-col">
                  <div :class="[isToday(dt) ? 'today-text' : '', isWeekend(dt) ? 'weekend-text' : '']">{{ formatDateLabel(dt) }}</div>
                  <div class="sub">계획</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td :colspan="7 + (dates?.length || 0)" class="empty">데이터를 불러오는 중...</td>
              </tr>
              <tr v-else-if="!planData || planData.data.length === 0">
                <td :colspan="7 + (dates?.length || 0)" class="empty">조회된 생산계획이 없습니다.</td>
              </tr>
              <tr v-else v-for="(row, ri) in planData.data" :key="ri" 
                  :class="{'selected': row._checked}"
                  @click="row._checked = !row._checked">
                <td class="fix center chk"><input type="checkbox" v-model="row._checked" @click.stop /></td>
                <td class="fix">{{ row.ORDERNUM }}</td>
                <td class="fix font-bold">{{ row.PARTNO }}</td>
                <td class="fix">{{ row.PARTNM }}</td>
                <td class="fix center"><span class="badge-unit">{{ row.STANDARD }}</span></td>
                <td class="fix num">{{ row.STOCKQTY?.toLocaleString() || 0 }}</td>
                <td class="fix num total-cell">{{ row.TOTAL?.toLocaleString() || 0 }}</td>
                <td v-for="dt in dates" :key="dt"
                    :class="[
                      'num', 
                      row[dt] > 0 ? 'hasval' : '',
                      (selectedCell?.ri === ri && selectedCell?.dt === dt) ? 'selected-cell' : ''
                    ]"
                    @click.stop="onCellClick(row, ri, dt)">
                  {{ row[dt] > 0 ? row[dt].toLocaleString() : '' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ 작업지시서 생성 모달 연동 ═══ -->
    <WorkOrderRegModal 
      :visible="showWoModal"
      :form="woForm"
      :items="woItems"
      :plants="plants"
      :processes="processes"
      :lines="lines"
      @close="showWoModal = false"
      @save="handleWoSave"
      @open-picker="openWoPicker"
      @remove-items="removeWoItems"
    />

    <ItemPicker 
      :visible="isItemPickerOpen" 
      :initial-search="searchText || itemSearch"
      @close="isItemPickerOpen = false"
      @select="onItemPicked"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import api from '../../../api';
import ItemPicker from '../../pickers/ItemPicker.vue';
import WorkOrderRegModal from '../../modals/WorkOrderRegModal.vue';

const now = new Date();
const f = (v: Date) => v.toISOString().slice(0, 10);
const baseDate = ref(f(now));
const plantCd = ref(''), searchText = ref(''), plants = ref<any[]>([]);
const planData = ref<any>(null);
const allChecked = ref(false);
const processes = ref<any[]>([]), lines = ref<any[]>([]);

const isItemPickerOpen = ref(false);
const itemSearch = ref('');
const pickerTarget = ref<'header'|'grid'>('grid');

function openItemLookup() {
  pickerTarget.value = 'grid'; 
  isItemPickerOpen.value = true;
}

function openWoPicker(target: 'header'|'grid') {
  pickerTarget.value = target;
  isItemPickerOpen.value = true;
}

function onItemPicked(g: any) {
  if (pickerTarget.value === 'header') {
    alert('헤더 품목 변경은 수주 데이터를 기준으로 하므로, 그리드에 품목을 추가해 주세요.');
  } else {
    if (!showWoModal.value) {
      searchText.value = g.PARTNO;
      fetchData();
    } else {
      woItems.value.push({
        PARTNO: g.PARTNO, PARTNM: g.PARTNM,
        STANDARD: g.STANDARD || '', UNIT: g.UNIT || '',
        LOCATIONCD: g.LOCATIONCD || '',
        ORDDATE: woForm.value.ORDDATE, PROCESSCD: g.PROCESSCD || '', 
        LINECD: g.LINECD || '',
        SHIFT: woForm.value.SHIFT, ORDQTY: 0, STOCKQTY: 0,
        _sel: true, _level: 1
      });
    }
  }
}

const dates = computed(() => {
  if (!planData.value || !planData.value.dates) return [];
  return planData.value.dates;
});

function isToday(dtStr: string) {
  const dt = new Date(dtStr);
  return dt.getFullYear() === now.getFullYear() && dt.getMonth() === now.getMonth() && dt.getDate() === now.getDate();
}
function isWeekend(dtStr: string) {
  const dt = new Date(dtStr);
  return dt.getDay() === 0 || dt.getDay() === 6;
}
function formatDateLabel(dtStr: string) {
  const [, m, d] = dtStr.split('-');
  return `${parseInt(m)}/${parseInt(d)}`;
}

function toggleAll() {
  if (planData.value && Array.isArray(planData.value.data)) {
    planData.value.data.forEach((r: any) => {
      r._checked = allChecked.value;
    });
  }
}

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchProcesses() {
  try { const r = await api.get('/api/master/process', { params: { size: 200 } }); processes.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchLines() {
  try { const r = await api.get('/api/master/line', { params: { size: 200 } }); lines.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}

const loading = ref(false);
const lastFocusedDate = ref<string | null>(null);
const selectedCell = ref<{ ri: number, dt: string } | null>(null);

const hasChecked = computed(() => {
  return planData.value?.data?.some((r: any) => r._checked) || false;
});

function onCellClick(row: any, ri: number, dt: string) {
  row._checked = true;
  row._selectedDate = dt;
  lastFocusedDate.value = dt;
  selectedCell.value = { ri, dt };
}

async function fetchData() {
  loading.value = true;
  try {
    const params: any = { base_date: baseDate.value };
    if (plantCd.value) params.plant_cd = plantCd.value;
    if (searchText.value) params.search = searchText.value;
    const r = await api.get('/api/production/plan', { params });
    
    const res = r.data;
    if (res && res.data) {
      res.data.forEach((row: any) => {
        row._checked = false;
        row._selectedDate = null;
      });
      planData.value = res;
    } else {
      planData.value = { data: [], dates: [] };
    }
  } catch (e) {
    console.error('Fetch plan data error:', e);
    planData.value = { data: [], dates: [] };
  } finally {
    loading.value = false;
  }
}

// ═══ 작업지시서 생성 모달 ═══
const showWoModal = ref(false);
const woForm = ref({
  PLANTCD: '', ORDDATE: f(now), ORDTYPE: '일반', SHIFT: '주간',
  ORDpriority: 1, SAT: false, SUN: false
});
const woItems = ref<any[]>([]);

async function openWoModal() {
  if (!planData.value) return;
  const checked = planData.value.data.filter((r: any) => r._checked);
  if (checked.length === 0) { alert('생산계획에서 품목을 선택해 주세요.'); return; }

  woForm.value = {
    PLANTCD: plantCd.value || (plants.value.length ? plants.value[0].PLANTCD : ''),
    ORDDATE: lastFocusedDate.value || f(now), 
    ORDTYPE: '일반', SHIFT: '주간', ORDpriority: 1, SAT: false, SUN: false
  };

  const newItems: any[] = [];
  const visited = new Set<string>();

  const isRawMaterial = (type: any, name: string = '') => {
    const t = (type || '').toString().toUpperCase();
    const n = (name || '').toString().toUpperCase();
    return t === '3' || t === '4' || t === 'RAW' || t === 'SUB' || 
           t.includes('원자') || t.includes('부자') ||
           n.includes('원자재') || n.includes('부자재') || n.includes('원재료') || n.includes('부재료');
  };

  async function explodeBom(partNo: string, parentQty: number, level: number, defaultDate: string) {
    if (level > 10) return; 
    try {
      const bomRes = await api.get(`/api/master/bom/detail/${partNo}`);
      const resData = bomRes.data;
      const items = Array.isArray(resData?.data) ? resData.data : (Array.isArray(resData) ? resData : []);
      if (items && items.length > 0) {
        for (const child of items) {
          const childPartNo = child.CHILD_PARTNO;
          if (!childPartNo || visited.has(childPartNo)) continue;
          visited.add(childPartNo);
          const reqQty = Number(child.REQQTY || 1);
          const totalQty = Number(parentQty) * reqQty;
          if (!isRawMaterial(child.PARTTYPE, child.PARTNM)) {
            newItems.push({
              PARTNO: childPartNo, PARTNM: child.PARTNM,
              STANDARD: child.STANDARD || '', UNIT: child.UNIT || '',
              LOCATIONCD: child.LOCATIONCD || '',
              ORDDATE: defaultDate, PROCESSCD: child.PROCESSCD || '', 
              LINECD: child.LINECD || '',
              SHIFT: '주간', ORDQTY: Math.floor(totalQty), STOCKQTY: 0,
              _sel: true, _level: level + 1
            });
            await explodeBom(childPartNo, totalQty, level + 1, defaultDate);
          }
        }
      }
    } catch (e) { console.error(`BOM error for ${partNo}:`, e); }
  }
  
  for (const row of checked) {
    const rowDate = row._selectedDate || lastFocusedDate.value || f(now);
    const initialQty = row._selectedDate ? Number(row[rowDate] || 0) : Number(row.TOTAL || 0);
    const rootPartNo = row.PARTNO;
    const rootPartNm = row.PARTNM || '수주품목';

    if (!isRawMaterial(row.PARTTYPE, rootPartNm)) {
      newItems.push({
        PARTNO: rootPartNo, PARTNM: rootPartNm, 
        STANDARD: row.STANDARD || '', UNIT: row.UNIT || '', 
        LOCATIONCD: row.LOCATIONCD || '',
        ORDDATE: rowDate, PROCESSCD: row.PROCESSCD || '', 
        LINECD: row.LINECD || '',
        SHIFT: '주간', ORDQTY: initialQty, STOCKQTY: row.STOCKQTY || 0,
        _sel: true, _level: 0
      });
      visited.clear();
      visited.add(rootPartNo);
      await explodeBom(rootPartNo, initialQty, 0, rowDate);
    }
  }

  woItems.value = newItems;
  showWoModal.value = true;
}

function removeWoItems() {
  woItems.value = woItems.value.filter(r => !r._sel);
}

async function handleWoSave() {
  const selected = woItems.value.filter(r => r._sel);
  if (selected.length === 0) { alert('저장할 품목을 선택하세요.'); return; }

  if (!confirm(`${selected.length}건의 작업지시를 등록하시겠습니까?`)) return;

  try {
    const roots = selected.filter(i => i._level === 0);
    for (const root of roots) {
      const rootIdx = selected.indexOf(root);
      const nextRootIdx = selected.findIndex((item, idx) => idx > rootIdx && item._level === 0);
      const group = nextRootIdx === -1 ? selected.slice(rootIdx) : selected.slice(rootIdx, nextRootIdx);

      const payload = {
        header: {
          PLANTCD: woForm.value.PLANTCD,
          PARTNO: root.PARTNO,
          ORDDATE: root.ORDDATE || woForm.value.ORDDATE,
          ORDQTY: root.ORDQTY,
          PROCESSCD: root.PROCESSCD || null,
          LINECD: root.LINECD || null,
          SHIFT: root.SHIFT || woForm.value.SHIFT,
          ORDTYPE: woForm.value.ORDTYPE,
          ORDpriority: woForm.value.ORDpriority,
          REMARK: ''
        },
        items: group.map(item => ({
          PLANTCD: woForm.value.PLANTCD,
          PARTNO: item.PARTNO,
          ORDDATE: item.ORDDATE,
          ORDQTY: item.ORDQTY,
          PROCESSCD: item.PROCESSCD || null,
          LINECD: item.LINECD || null,
          SHIFT: item.SHIFT,
          ORDTYPE: woForm.value.ORDTYPE,
          ORDpriority: woForm.value.ORDpriority,
          REMARK: ''
        }))
      };

      await api.post('/api/production/workorder/batch', payload);
    }

    alert('작업지시가 등록되었습니다.');
    showWoModal.value = false;
    fetchData();
  } catch (e: any) {
    alert('등록 중 오류 발생: ' + (e.response?.data?.detail || e.message));
  }
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
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:6px;cursor:pointer;font-size:1rem;height:34px}
.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-add:disabled { background: #bdc3c7; cursor: not-allowed; opacity: 0.7; }
.btn-excel{background:#27ae60;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}

/* 그리드 레이아웃 */
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.grid-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden;flex:1}
.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.cal-grid-wrap{flex:1;overflow:auto}
.cal-grid{width:100%;border-collapse:collapse;font-size:.82rem}
.cal-grid thead{position:sticky;top:0;z-index:10}
.cal-grid th{background:#f8fafc;color:#64748b;font-weight:700;padding:12px 10px;border-bottom:2px solid #f1f5f9;text-align:left}
.cal-grid td{padding:10px;border-bottom:1px solid #f1f5f9;color:#334155}
.cal-grid .fix{position:sticky;background:#f8fafc;z-index:11;border-right:1px solid #f1f5f9}
.cal-grid tbody .fix{background:#fff}
.cal-grid .fix:nth-child(1){left:0;width:40px;min-width:40px}
.cal-grid .fix:nth-child(2){left:40px;width:110px;min-width:110px}
.cal-grid .fix:nth-child(3){left:150px;width:110px;min-width:110px}
.cal-grid .fix:nth-child(4){left:260px;width:160px;min-width:160px}
.cal-grid .fix:nth-child(5){left:420px;width:90px;min-width:90px}
.cal-grid .fix:nth-child(6){left:510px;width:80px;min-width:80px}
.cal-grid .fix:nth-child(7){left:590px;width:80px;min-width:80px}
.cal-grid th.fix, .cal-grid td.fix { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.cal-grid .num{text-align:right}
.cal-grid .center{text-align:center}
.cal-grid .total-head{background:#eff6ff!important;color:#1e40af}
.cal-grid .total-cell{color:#2563eb;font-weight:800;background:#eff6ff}
.date-col{min-width:70px;text-align:center;border-left:1px solid #f1f5f9}
.date-col .sub{font-size:.7rem;color:#94a3b8;font-weight:600}
.hasval{background:#f0fdf4;color:#166534;font-weight:700}
.badge-unit{background:#f1f5f9;color:#475569;padding:1px 6px;border-radius:8px;font-size:.68rem;font-weight:700}
.cal-grid tbody tr:hover td{background:#fbfcfe;cursor:pointer}
.cal-grid tbody tr.selected td{background:#f1f5f9!important}
.empty{text-align:center;padding:80px!important;color:#94a3b8;font-size:1rem}
.font-bold { font-weight: 700; }
.today-text { color: #d35400; font-weight: 800; }
.weekend-text { color: #c0392b; }
.selected-cell { background-color: #bbdefb !important; outline: 2px solid #2196f3; z-index: 4; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
</style>
