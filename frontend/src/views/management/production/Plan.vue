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
        <div class="input-search-wrap" style="display:inline-flex; align-items:stretch;">
          <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchData" style="border-radius: 3px 0 0 3px;" />
          <button class="btn-s" @click="openItemLookup" style="border-left:none; border:1px solid #bdc3c7; background:#f8fafc; cursor:pointer; padding:0 8px; border-radius:0 3px 3px 0;">🔍</button>
        </div>
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-wo" @click="openWoModal" :disabled="!hasChecked">✅ 작업 지시서 생성</button>
        </div>
      </div>
    </section>

    <!-- ═══ 달력형 그리드 ═══ -->
    <div class="plan-grid-wrap">
      <table class="plan-grid" v-if="planData">
        <thead>
          <tr class="day-num-row">
            <th class="freeze" style="width:40px"><input type="checkbox" v-model="allChecked" @change="toggleAll" /></th>
            <th class="freeze" style="min-width:100px">수주번호</th>
            <th class="freeze" style="min-width:100px">품번</th>
            <th class="freeze" style="min-width:130px">품명</th>
            <th class="freeze" style="min-width:70px">규격</th>
            <th class="freeze" style="min-width:60px">재고수량</th>
            <th class="freeze" style="min-width:60px">계획합계</th>
            <th v-for="dt in dates" :key="dt"
                :class="['day-col', isToday(dt) ? 'today' : '', isWeekend(dt) ? 'weekend' : '']"
                style="min-width:52px">{{ formatDateLabel(dt) }}</th>
          </tr>
          <tr class="day-label-row">
            <th class="freeze"></th><th class="freeze"></th><th class="freeze"></th><th class="freeze"></th>
            <th class="freeze"></th><th class="freeze"></th><th class="freeze"></th>
            <th v-for="dt in dates" :key="'l'+dt"
                :class="['day-col', isToday(dt) ? 'today' : '', isWeekend(dt) ? 'weekend' : '']">
              계획
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
              :class="{'row-selected': row._checked}"
              @click="row._checked = !row._checked">
            <td class="freeze chk"><input type="checkbox" v-model="row._checked" @click.stop /></td>
            <td class="freeze">{{ row.ORDERNUM }}</td>
            <td class="freeze">{{ row.PARTNO }}</td>
            <td class="freeze">{{ row.PARTNM }}</td>
            <td class="freeze">{{ row.STANDARD }}</td>
            <td class="freeze num">{{ row.STOCKQTY || 0 }}</td>
            <td class="freeze num total-cell">{{ row.TOTAL || 0 }}</td>
            <td v-for="dt in dates" :key="dt"
                :class="[
                  'day-col', 
                  isToday(dt)?'today':'', 
                  isWeekend(dt)?'weekend':'',
                  (selectedCell?.ri === ri && selectedCell?.dt === dt) ? 'selected-cell' : ''
                ]"
                class="num"
                @click.stop="onCellClick(row, ri as number, dt)">
              {{ row[dt] || 0 }}
            </td>
          </tr>
        </tbody>
      </table>
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
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#2980b9;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #d6eaf8}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.btn-search{background:#2980b9;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-wo{background:linear-gradient(135deg,#27ae60,#219a52);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-wo:disabled { background: #bdc3c7; cursor: not-allowed; opacity: 0.7; }

/* 달력 그리드 */
.plan-grid-wrap{flex:1;overflow:auto;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.plan-grid{width:100%;border-collapse:collapse;font-size:.82rem}
.plan-grid thead{position:sticky;top:0;z-index:5}
.day-num-row th{background:linear-gradient(180deg,#d6eaf8,#aed6f1);color:#1a5276;font-weight:700;padding:8px 4px;text-align:center;border-bottom:1px solid #85c1e9;white-space:nowrap}
.day-label-row th{background:#eaf2f8;color:#5d6d7e;font-size:.75rem;font-weight:600;padding:4px;text-align:center;border-bottom:2px solid #85c1e9}
.plan-grid td{padding:2px 3px;border-bottom:1px solid #f0f2f5;text-align:center}
.freeze{position:sticky;background:#fff;z-index:3}
.freeze:nth-child(1){left:0;width:40px}.freeze:nth-child(2){left:40px;width:100px}.freeze:nth-child(3){left:140px;width:100px}
.freeze:nth-child(4){left:240px;width:130px}.freeze:nth-child(5){left:370px;width:70px}
.freeze:nth-child(6){left:440px;width:60px}.freeze:nth-child(7){left:500px;width:60px}
thead .freeze{background:linear-gradient(180deg,#d6eaf8,#aed6f1)!important;z-index:6}
.day-label-row .freeze{background:#eaf2f8!important}
.num{text-align:right;padding-right:6px!important}
.total-cell{font-weight:700;color:#2980b9}
.today{background:#fff8e1!important}
.weekend{background:#fef0f0!important}
.cell-input{width:100%;min-width:46px;box-sizing:border-box;padding:4px;border:1px solid #e2e8f0;border-radius:4px;font-size:.82rem;text-align:right;background:#fafbfc}
.cell-input:focus{border-color:#2980b9;outline:none;background:#fff}
.empty{text-align:center;color:#b2bec3;padding:60px!important}
.row-selected{background:#e8f4fd!important}
.row-selected .freeze{background:#e8f4fd!important}
.selected-cell { background-color: #bbdefb !important; outline: 2px solid #2196f3; z-index: 4; }

/* ═══ 작업지시 모달 (기존 스타일 제거됨) ═══ */
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
</style>
