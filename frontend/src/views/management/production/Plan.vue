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
        <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchData" />
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
                :class="['day-col', isToday(dt)?'today':'', isWeekend(dt)?'weekend':'']"
                @click.stop="onCellClick(row, dt)">
              <input type="number" class="cell-input"
                     :value="row[dt] || ''"
                     @click.stop="onCellClick(row, dt)"
                     @focus="onCellClick(row, dt)"
                     @change="onCellChange(row, dt, $event)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══ 작업지시서 생성 모달 ═══ -->
    <div v-if="showWoModal" class="modal-overlay" @click.self="showWoModal=false">
      <div class="modal-container">
        <!-- ═══ 헤더 ═══ -->
        <div class="modal-header">
          <div class="title">
            작업 지시 등록<span class="sub-title">[frmWorkOrderRegPopUp]</span>
          </div>
          <div class="header-actions">
            <button class="btn-action" @click="handleWoSave">
              <i class="fas fa-save"></i> 저장
            </button>
            <button class="btn-action" @click="removeWoItems">
              <i class="fas fa-cut"></i> 삭제
            </button>
            <button class="btn-action btn-close" @click="showWoModal=false">
              <i class="fas fa-times-circle"></i> 닫기
            </button>
          </div>
        </div>

        <!-- ═══ 바디 ═══ -->
        <div class="modal-body">
          <!-- 1. 작업 지시 정보 (폼) -->
          <fieldset class="info-fieldset">
            <legend>작업 지시 정보</legend>
            <div class="form-container">
              <!-- Left Column -->
              <div class="form-col">
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet green"></span>작업 지시 번호</label>
                  <div class="input-group">
                    <input type="text" readonly style="flex:1" placeholder="자동채번" />
                    <button class="btn-icon">>></button>
                  </div>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>품번/품명</label>
                  <div class="input-group multi-input">
                    <input type="text" :value="woItems[0]?.PARTNO || ''" style="flex:1" readonly />
                    <input type="text" :value="woItems[0]?.PARTNM || ''" style="flex:1" readonly />
                    <button class="btn-icon" @click="openPicker('header')"><i class="fas fa-binoculars" style="color: #64748b;"></i></button>
                  </div>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>작업지시일</label>
                  <div class="input-group multi-input">
                    <input type="date" v-model="woForm.ORDDATE" style="width: 140px;" />
                    <label class="chk-label"><input type="checkbox" v-model="woForm.SAT" /> 토요일</label>
                    <label class="chk-label"><input type="checkbox" v-model="woForm.SUN" /> 일요일</label>
                  </div>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>근무조</label>
                  <select v-model="woForm.SHIFT">
                    <option value="주간">주간</option>
                    <option value="야간">야간</option>
                  </select>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>지시 수량</label>
                  <input type="number" :value="woItems[0]?.ORDQTY || 0" readonly />
                </div>
              </div>

              <!-- Right Column -->
              <div class="form-col">
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>사업장</label>
                  <select v-model="woForm.PLANTCD">
                    <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
                  </select>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>작지구분</label>
                  <select v-model="woForm.ORDTYPE">
                    <option value="일반">일반</option>
                    <option value="긴급">긴급</option>
                    <option value="재작업">재작업</option>
                  </select>
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet green"></span>단위</label>
                  <input type="text" :value="woItems[0]?.UNIT || ''" readonly />
                </div>
                <div class="form-row">
                  <label class="bullet-label"><span class="bullet orange"></span>우선순위</label>
                  <input type="number" v-model.number="woForm.ORDpriority" />
                </div>
              </div>
            </div>
          </fieldset>

          <!-- 2. 그리드 툴바 -->
          <div class="toolbar">
            <button class="btn-grid-action" @click="openPicker('grid')">
              <i class="fas fa-download"></i> 추가
            </button>
            <button class="btn-grid-action" @click="removeWoItems">
              <i class="fas fa-cut"></i> 삭제
            </button>
          </div>

          <!-- 3. 품목 그리드 -->
          <div class="grid-container">
            <table class="data-grid">
              <thead>
                <tr>
                  <th style="width: 40px">선택</th>
                  <th style="width: 100px">작업일자</th>
                  <th style="width: 120px">품번</th>
                  <th style="width: 180px">품목명</th>
                  <th style="width: 80px">규격</th>
                  <th style="width: 60px">단위</th>
                  <th style="width: 80px">로케이션</th>
                  <th style="width: 100px">공정</th>
                  <th style="width: 100px">라인</th>
                  <th style="width: 70px">근무조</th>
                  <th style="width: 80px">지시수량</th>
                  <th style="width: 60px">상태</th>
                  <th style="width: 70px">재고수량</th>
                  <th style="width: 70px">소요량</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, i) in woItems" :key="i" :class="{'selected-row': item._sel, 'parent-row': item._level === 0}">
                  <td class="text-center"><input type="checkbox" v-model="item._sel" /></td>
                  <td class="text-center"><input type="date" v-model="item.ORDDATE" class="grid-edit-input" /></td>
                  <td class="text-center">{{ item.PARTNO }}</td>
                  <td>{{ item.PARTNM }}</td>
                  <td>{{ item.STANDARD }}</td>
                  <td class="text-center">{{ item.UNIT }}</td>
                  <td class="text-center">
                    <select v-model="item.PROCESSCD" class="grid-edit-select">
                      <option value="">선택</option>
                      <option v-for="pr in processes" :key="pr.PROCESSCD" :value="pr.PROCESSCD">{{ pr.PROCESSNM }}</option>
                    </select>
                  </td>
                  <td class="text-center">
                    <select v-model="item.LINECD" class="grid-edit-select">
                      <option value="">선택</option>
                      <option v-for="ln in lines" :key="ln.LINECD" :value="ln.LINECD">{{ ln.LINENM }}</option>
                    </select>
                  </td>
                  <td class="text-center">
                    <select v-model="item.SHIFT" class="grid-edit-select">
                      <option value="주간">주간</option>
                      <option value="야간">야간</option>
                    </select>
                  </td>
                  <td class="text-right">
                    <input type="number" v-model.number="item.ORDQTY" class="grid-edit-input text-right" />
                  </td>
                  <td class="text-center"><span class="status-new">신규</span></td>
                  <td class="text-right">{{ item.STOCKQTY || 0 }}</td>
                  <td class="text-right">{{ item.ORDQTY || 0 }}</td>
                </tr>
                <tr v-if="woItems.length === 0">
                  <td colspan="14" class="empty-msg">선택된 품목이 없습니다.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ 품목 선택 팝업 ═══ -->
    <div v-if="showItemPicker" class="modal-overlay" @click.self="showItemPicker=false">
      <div class="picker-modal">
        <div class="picker-header">
          <h3>품목 선택</h3>
          <button class="btn-close-sm" @click="showItemPicker=false">✕</button>
        </div>
        <div class="picker-search">
          <input type="text" v-model="itemSearch" placeholder="품번/품명 검색" @keyup.enter="fetchItems" />
          <button class="btn-search" @click="fetchItems">조회</button>
        </div>
        <div class="picker-list">
          <table class="picker-tbl">
            <thead><tr><th>품번</th><th>품명</th><th>규격</th><th>단위</th></tr></thead>
            <tbody>
              <tr v-for="g in itemsList" :key="g.PARTNO" @click="selectItem(g)" class="clickable">
                <td>{{ g.PARTNO }}</td><td>{{ g.PARTNM }}</td><td>{{ g.STANDARD }}</td><td>{{ g.UNIT }}</td>
              </tr>
              <tr v-if="itemsList.length===0"><td colspan="4" class="empty">결과 없음</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import api from '../../../api';

const now = new Date();
const f = (v: Date) => v.toISOString().slice(0, 10);
const baseDate = ref(f(now));
const plantCd = ref(''), searchText = ref(''), plants = ref<any[]>([]);
const planData = ref<any>(null);
const allChecked = ref(false);
const processes = ref<any[]>([]), lines = ref<any[]>([]);

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

const hasChecked = computed(() => {
  return planData.value?.data?.some((r: any) => r._checked) || false;
});

function onCellClick(row: any, dt: string) {
  row._checked = true;
  lastFocusedDate.value = dt;
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
      res.data.forEach((row: any) => row._checked = false);
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

// 셀 수정 시 즉시 저장
async function onCellChange(row: any, dt: string, event: Event) {
  const val = parseInt((event.target as HTMLInputElement).value) || 0;
  row[dt] = val;
  let total = 0;
  for (const d of planData.value.dates) total += (row[d] || 0);
  row.TOTAL = total;

  try {
    await api.post('/api/production/plan', {
      PRODUCEDT: dt, 
      PLANTCD: row.PLANTCD || plantCd.value || plants.value[0]?.PLANTCD || '',
      PARTNO: row.PARTNO, 
      ORDERNUM: row.ORDERNUM || '', 
      ORDERSEQ: row.ORDERSEQ || 1, 
      PRODUCEQTY: val
    });
  } catch (e) {
    console.error('Cell change save error:', e);
  }
}

// ═══ 작업지시서 생성 모달 ═══
const showWoModal = ref(false);
const woForm = ref({
  PLANTCD: '', ORDDATE: f(now), ORDTYPE: '일반', SHIFT: '주간',
  ORDpriority: 1, SAT: false, SUN: false
});
const woItems = ref<any[]>([]);

// ── 품목 선택 ──
const showItemPicker = ref(false), itemSearch = ref(''), itemsList = ref<any[]>([]);
const pickerTarget = ref<'header'|'grid'>('grid');

function openPicker(target: 'header'|'grid') {
  pickerTarget.value = target;
  itemSearch.value = '';
  itemsList.value = [];
  showItemPicker.value = true;
}

async function fetchItems() {
  try {
    const r = await api.get('/api/master/goods', { params: { search: itemSearch.value, size: 50 } });
    itemsList.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch (e) { console.error('Fetch items error:', e); }
}

async function selectItem(g: any) {
  if (pickerTarget.value === 'header') {
    alert('헤더 품목 변경은 수주 데이터를 기준으로 하므로, 그리드에 품목을 추가해 주세요.');
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
  showItemPicker.value = false;
}

async function openWoModal() {
  console.log('openWoModal called');
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
    const defaultDate = lastFocusedDate.value || f(now);
    const initialQty = Number(row.TOTAL || 0);
    const rootPartNo = row.PARTNO;
    const rootPartNm = row.PARTNM || '수주품목';

    if (!isRawMaterial(row.PARTTYPE, rootPartNm)) {
      newItems.push({
        PARTNO: rootPartNo, PARTNM: rootPartNm, 
        STANDARD: row.STANDARD || '', UNIT: row.UNIT || '', 
        LOCATIONCD: row.LOCATIONCD || '',
        ORDDATE: defaultDate, PROCESSCD: row.PROCESSCD || '', 
        LINECD: row.LINECD || '',
        SHIFT: '주간', ORDQTY: initialQty, STOCKQTY: row.STOCKQTY || 0,
        _sel: true, _level: 0
      });
      visited.clear();
      visited.add(rootPartNo);
      await explodeBom(rootPartNo, initialQty, 0, defaultDate);
    }
  }

  woItems.value = newItems;
  showWoModal.value = true;
}

function removeWoItems() {
  woItems.value = woItems.value.filter(r => !r._sel);
}

async function handleWoSave() {
  console.log('handleWoSave called');
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

      console.log('Sending Batch Payload (Plan):', payload);
      const res = await api.post('/api/production/workorder/batch', payload);
      console.log('Batch response:', res.data);
    }

    alert('작업지시가 등록되었습니다.');
    showWoModal.value = false;
    fetchData();
  } catch (e: any) {
    console.error('Work order save error:', e);
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

/* ═══ 작업지시 모달 ═══ */
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-container { width: 1050px; background: #f4f6f8; border: 1px solid #94a3b8; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); display: flex; flex-direction: column; }
.modal-header { background: #629b9b; color: white; padding: 6px 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #4d7c7c; }
.title { font-size: 1.15rem; font-weight: bold; }
.sub-title { font-size: 0.9rem; font-weight: normal; margin-left: 6px; opacity: 0.9; }
.header-actions { display: flex; gap: 4px; }
.btn-action { background: #f8fafc; border: 1px solid #cbd5e1; color: #334155; padding: 4px 10px; font-size: 0.9rem; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.btn-action:hover { background: #e2e8f0; }
.btn-close { color: #dc2626; }
.btn-close:hover { background: #fee2e2; }
.modal-body { padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.info-fieldset { border: 1px solid #cbd5e1; padding: 12px; margin: 0; background: #fff; }
.info-fieldset legend { padding: 0 4px; color: #334155; font-weight: bold; }
.form-container { display: flex; gap: 40px; }
.form-col { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.form-row { display: flex; align-items: center; height: 26px; }
.bullet-label { width: 100px; display: flex; align-items: center; font-size: 0.85rem; color: #334155; font-weight: bold; }
.bullet { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; border: 3px solid; border-right-color: transparent; transform: rotate(-45deg); }
.bullet.green { border-color: #84cc16; }
.bullet.orange { border-color: #f97316; }
.form-row input, .form-row select { height: 24px; border: 1px solid #cbd5e1; padding: 0 4px; font-size: 0.85rem; }
.form-row input:read-only { background: #f1f5f9; }
.input-group { display: flex; flex: 1; gap: 4px; }
.btn-icon { height: 24px; padding: 0 6px; background: #e2e8f0; border: 1px solid #cbd5e1; cursor: pointer; font-size: 0.8rem; }
.chk-label { display: flex; align-items: center; font-size: 0.85rem; gap: 2px; margin-left: 6px; }
.toolbar { display: flex; justify-content: flex-end; gap: 4px; }
.btn-grid-action { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 4px 10px; font-size: 0.85rem; cursor: pointer; color: #475569; display: flex; align-items: center; gap: 4px; }
.grid-container { background: #fff; border: 1px solid #cbd5e1; height: 250px; overflow-y: auto; }
.data-grid { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-grid th, .data-grid td { border: 1px solid #e2e8f0; padding: 4px; }
.data-grid th { background: #f8fafc; color: #334155; font-weight: normal; position: sticky; top: 0; z-index: 10; }
.selected-row { background: #eff6ff; }
.parent-row { font-weight: bold; background: #f8fafc; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.grid-edit-input, .grid-edit-select { width: 100%; border: 1px solid #e2e8f0; border-radius: 4px; padding: 2px 4px; font-size: 0.8rem; }
.status-new { font-size: 0.75rem; color: #dc2626; }
.empty-msg { text-align: center; color: #94a3b8; padding: 30px !important; }
</style>
