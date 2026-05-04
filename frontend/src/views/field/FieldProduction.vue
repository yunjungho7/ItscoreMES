<template>
  <div class="field-page logistics-style">
    <!-- ═══ 헤더 바 ═══ -->
    <header class="field-header">
      <div class="header-left">
        <h1 class="page-title">현장 생산관리</h1>
      </div>
      <div class="header-right">
        <div class="worker-info">
          <label>👤 작업자</label>
          <div class="search-input">
            <input type="text" v-model="worker" placeholder="작업자" />
            <button class="btn-search-small" @click="fetchData">🔍</button>
          </div>
        </div>
        <div class="printer-select">
          <label>📠 프린터</label>
          <select v-model="printer">
            <option value="">(선택하세요)</option>
            <option v-for="p in printerList" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="header-buttons">
          <button class="btn-icon" @click="fetchData">
            <span class="icon">🔍</span> 조회
          </button>
          <button class="btn-icon" @click="$router.push('/logistics')">
            <span class="icon">📦</span> 물류
          </button>
          <button class="btn-icon btn-close" @click="$router.push('/select-mode')">
            <span class="icon">❌</span> 종료
          </button>
          <button class="btn-icon" @click="showPrinterSetting = true">
            <span class="icon">⚙️</span> 옵션
          </button>
        </div>
      </div>
    </header>

    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="filter-grid">
        <div class="filter-item">
          <label>작업일</label>
          <div class="date-range">
            <input type="date" v-model="startDate" />
            <span>~</span>
            <input type="date" v-model="endDate" />
          </div>
        </div>
        <div class="filter-item">
          <label>상태</label>
          <select v-model="ordState" class="s-select">
            <option value="">(선택...)</option>
            <option value="NEW">신규</option>
            <option value="SETTING">시세팅</option>
            <option value="STARTED">작업중</option>
            <option value="DONE">완료</option>
          </select>
        </div>
        <div class="filter-item checkbox-item">
          <input type="checkbox" id="include-done" v-model="includeDone" />
          <label for="include-done">완료포함</label>
        </div>
        <div class="filter-item">
          <label>주/야</label>
          <select v-model="shift" class="s-select">
            <option value="">(선택...)</option>
            <option value="주간">주간</option>
            <option value="야간">야간</option>
          </select>
        </div>
        <div class="filter-item">
          <label>작지번호</label>
          <div class="search-input">
            <input type="text" v-model="searchWorkordNo" placeholder="작지번호" @keyup.enter="fetchData" />
            <button class="btn-search-small" @click="fetchData">🔍</button>
          </div>
        </div>
        <div class="filter-item">
          <label>품번</label>
          <div class="search-input">
            <input type="text" v-model="searchPartNo" placeholder="품번 검색" @keyup.enter="fetchData" />
            <button class="btn-search-small" @click="showItemPicker = true">🔍</button>
          </div>
        </div>
        <div class="filter-item">
          <label>라인</label>
          <div class="search-input">
            <select v-model="lineCd">
              <option value="">(선택하세요)</option>
              <option v-for="l in lines" :key="l.LINECD" :value="l.LINECD">{{ l.LINENM }}</option>
            </select>
            <button class="btn-search-small" @click="showLinePicker = true">🔍</button>
          </div>
        </div>
        <div class="filter-item">
          <label>공정</label>
          <div class="search-input">
            <select v-model="processCd">
              <option value="">(선택하세요)</option>
              <option v-for="p in processes" :key="p.PROCESSCD" :value="p.PROCESSCD">{{ p.PROCESSNM }}</option>
            </select>
            <button class="btn-search-small" @click="showProcessPicker = true">🔍</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ 마스터 그리드 ═══ -->
    <div class="main-content">
      <div class="table-wrap master-table-wrap">
        <table class="master-grid">
          <thead>
            <tr>
            <th style="width:55px">주/야</th>
            <th style="width:130px">하위작지번호</th>
            <th style="width:65px">라인</th>
            <th style="width:65px">공정</th>
            <th style="width:110px">공정품번</th>
            <th style="width:130px">공정품명</th>
            <th style="width:80px">공정품규격</th>
            <th style="width:50px">우선도</th>
            <th style="width:65px">수량</th>
            <th style="width:45px">단위</th>
            <th style="width:60px">상태</th>
            <th style="width:110px">품번</th>
            <th style="width:120px">품명</th>
            <th style="width:130px">LOT No.</th>
            <th style="min-width:80px">수주정보</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="masterRows.length === 0">
            <td colspan="15" class="empty">데이터 없음</td>
          </tr>
          <tr v-for="(row, idx) in masterRows" :key="idx"
              :class="{ 'row-selected': selectedIdx === idx }"
              @click="onSelectMaster(row, idx)">
            <td class="center">{{ row.SHIFT }}</td>
            <td>{{ row.WORKORDNO }}</td>
            <td class="center">{{ row.LINECD }}</td>
            <td class="center">{{ row.PROCESSCD }}</td>
            <td>{{ row.PROC_PARTNO }}</td>
            <td>{{ row.PROC_PARTNM }}</td>
            <td>{{ row.PROC_STANDARD }}</td>
            <td class="center">{{ row.ORDpriority }}</td>
            <td class="right">{{ row.ORDQTY }}</td>
            <td class="center">{{ row.UNIT }}</td>
            <td class="center">{{ row.ORDSTATE }}</td>
            <td>{{ row.PARTNO }}</td>
            <td>{{ row.PARTNM }}</td>
            <td>{{ row.LOTNO }}</td>
            <td>{{ row.REMARK }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

    <!-- ═══ 하단 탭 영역 ═══ -->
    <div class="tab-section">
      <!-- 탭 바 -->
      <div class="tab-bar">
        <button v-for="t in tabs" :key="t.key"
                :class="['tab-btn', { active: activeTab === t.key }]"
                @click="activeTab = t.key">{{ t.label }}</button>
      </div>

      <!-- 탭 1: 생산실적 -->
      <div v-if="activeTab === 'result'" class="tab-content">
        <div class="result-top">
          <div class="result-info-cards">
            <div class="info-card">
              <span class="card-label">총생산실적</span>
              <span class="card-value">{{ summary.TOT_PROD_QTY || 0 }}</span>
            </div>
            <div class="info-card highlight">
              <span class="card-label">잔량</span>
              <span class="card-value">{{ (summary.ORD_QTY || 0) - (summary.TOT_PROD_QTY || 0) }}</span>
            </div>
          </div>
          <div class="result-actions">
            <button class="btn-status mat-input" @click="toggleInputMode">📦 자재투입</button>
            <button class="btn-status start" :disabled="selectedRow?.ORDSTATE !== 'NEW'" @click="changeStatus('STARTED')">▶ 작업시작</button>
            <button class="btn-status cancel" :disabled="selectedRow?.ORDSTATE !== 'STARTED' || (summary.TOT_PROD_QTY || 0) > 0" @click="cancelProduction">⟲ 작업취소</button>
            <button class="btn-status mid" :disabled="!canSaveIntermediate" @click="saveIntermediateResult">✚ 중간실적</button>
            <button class="btn-status done" :disabled="!canFinishWork" @click="changeStatus('DONE')">■ 작업완료</button>
          </div>
        </div>

        <div class="metric-container">
          <div class="metric-card">
            <label>작업지시수량</label>
            <div class="metric-val">{{ summary.ORD_QTY || 0 }}</div>
          </div>
          <div class="metric-card">
            <label>총생산실적수량</label>
            <div class="metric-val">{{ summary.TOT_PROD_QTY || 0 }}</div>
          </div>
          <div class="metric-card">
            <label>총양품수량</label>
            <div class="metric-val success">{{ summary.TOT_GOOD_QTY || 0 }}</div>
          </div>
          <div class="metric-card">
            <label>총불량수량</label>
            <div class="metric-val danger">{{ summary.TOT_FAIL_QTY || 0 }}</div>
          </div>
          <div class="metric-card action">
            <label>금회 생산실적</label>
            <input type="number" v-model.number="summary.PROD_QTY" class="metric-input" />
          </div>
          <div class="metric-card action">
            <label>금회 양품수량</label>
            <div class="metric-val success">{{ summary.GOOD_QTY }}</div>
          </div>
          <div class="metric-card action">
            <label>금회 불량수량</label>
            <input type="number" v-model.number="summary.FAIL_QTY" class="metric-input danger" />
          </div>
        </div>

        <!-- 메인 화면 생산실적 상세 그리드 (투입된 자재 목록) -->
        <div class="detail-grid-wrap mat-list-section">
          <div class="sub-title">
            <span class="icon">📋</span> 투입된 자재 목록 (작업 진행중)
          </div>
          <div class="table-wrap mini">
            <table class="detail-grid">
              <thead>
                <tr>
                  <th>품번</th><th>품명</th><th>규격</th><th>단위</th><th>투입수량</th><th>투입LOT</th><th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="resultRows.filter(r => r.RECORD_GUBUN === 'INPUT').length === 0">
                  <td colspan="7" class="empty">투입된 자재가 없습니다. [자재투입] 버튼을 눌러 등록하세요.</td>
                </tr>
                <tr v-for="(r, i) in resultRows.filter(r => r.RECORD_GUBUN === 'INPUT')" :key="i">
                  <td>{{ r.PARTNO }}</td><td>{{ r.PARTNM }}</td><td>{{ r.STANDARD }}</td>
                  <td class="center">{{ r.UNIT }}</td><td class="right" style="color: #2ecc71; font-weight: bold;">{{ r.INPUT_QTY }}</td>
                  <td>{{ r.LOTNO }}</td>
                  <td class="center">
                    <button class="btn-grid-del" @click="deleteInput(r)">삭제</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 자재투입 모달 -->
      <MaterialInputModal 
        :visible="isInputMode"
        :rows="resultRows"
        @close="isInputMode = false"
        @save="onSaveMaterialInput"
        @delete="deleteInput"
      />

      <!-- 탭 2: 생산이력 -->
      <div v-if="activeTab === 'history'" class="tab-content">
        <div class="result-top">
          <div class="toolbar-left">
            <span class="icon">📜</span>
            <span class="toolbar-title">생산이력 현황</span>
          </div>
          <div class="result-actions">
            <button class="btn-status done">
              <span class="icon">⚠️</span> 비가동 등록
            </button>
            <button class="btn-status mid">
              <span class="icon">🖨️</span> 라벨출력
            </button>
          </div>
        </div>
        <div class="detail-grid-wrap">
          <div class="table-wrap">
            <table class="detail-grid">
              <thead>
                <tr>
                  <th>품번</th><th>품명</th><th>규격</th><th>라인</th><th>공정</th><th>근무조</th>
                  <th>LOT번호</th><th>양품수량</th><th>불량LOT수량</th><th>단위</th><th>시작일자</th><th>완료일자</th><th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="historyRows.length === 0"><td colspan="13" class="empty">데이터 없음</td></tr>
                <tr v-for="(r, i) in historyRows" :key="i">
                  <td>{{ r.PARTNO }}</td><td>{{ r.PARTNM }}</td><td>{{ r.STANDARD }}</td>
                  <td class="center">{{ r.LINECD }}</td><td class="center">{{ r.PROCESSCD }}</td><td class="center">{{ r.SHIFT }}</td>
                  <td>{{ r.LOTNO }}</td><td class="right">{{ r.GOOD_QTY }}</td><td class="right">{{ r.FAIL_QTY }}</td>
                  <td class="center">{{ r.UNIT }}</td><td class="center">{{ r.START_DATE }}</td><td class="center">{{ r.END_DATE }}</td>
                  <td class="center">
                    <button class="btn-grid-del" @click="deleteHistoryRow(r)">삭제</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 탭 3: 불량이력 -->
      <div v-if="activeTab === 'defect'" class="tab-content">
        <div class="tab-toolbar-modern danger">
          <div class="toolbar-left">
            <span class="icon">🚫</span>
            <span class="toolbar-title">불량이력 현황</span>
          </div>
          <div class="toolbar-actions">
            <button class="btn-action-small blue">
              <span class="icon">🖨️</span> 라벨출력
            </button>
          </div>
        </div>
        <div class="detail-grid-wrap">
          <div class="table-wrap">
            <table class="detail-grid">
              <thead>
                <tr>
                  <th>품번</th><th>품명</th><th>규격</th><th>라인</th><th>공정</th><th>근무조</th>
                  <th>LOT번호</th><th>불량LOT수량</th><th>단위</th><th>불량유실</th><th>불량위인</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="defectRows.length === 0"><td colspan="11" class="empty">데이터 없음</td></tr>
                <tr v-for="(r, i) in defectRows" :key="i">
                  <td>{{ r.PARTNO }}</td><td>{{ r.PARTNM }}</td><td>{{ r.STANDARD }}</td>
                  <td class="center">{{ r.LINECD }}</td><td class="center">{{ r.PROCESSCD }}</td><td class="center">{{ r.SHIFT }}</td>
                  <td>{{ r.LOTNO }}</td><td class="right">{{ r.FAIL_LOT_QTY }}</td>
                  <td class="center">{{ r.UNIT }}</td><td>{{ r.FAIL_REASON }}</td><td>{{ r.FAIL_CAUSE }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 상태바 -->
    <div class="status-bar">
      Record {{ masterRows.length }} of {{ totalRecords }}
    </div>

    <ItemPicker 
      :visible="showItemPicker" 
      :initial-search="searchPartNo"
      @close="showItemPicker = false"
      @select="onItemSelect"
    />

    <LinePicker 
      :visible="showLinePicker" 
      :initial-search="lineCd"
      @close="showLinePicker = false"
      @select="onLineSelect"
    />

    <ProcessPicker 
      :visible="showProcessPicker" 
      :initial-search="processCd"
      @close="showProcessPicker = false"
      @select="onProcessSelect"
    />

    <PrinterSettingModal 
      :visible="showPrinterSetting"
      @close="showPrinterSetting = false"
      @saved="onPrinterSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import api from '../../api';
import MaterialInputModal from '../modals/MaterialInputModal.vue';
import PrinterSettingModal from '../modals/PrinterSettingModal.vue';
import ItemPicker from '../pickers/ItemPicker.vue';
import LinePicker from '../pickers/LinePicker.vue';
import ProcessPicker from '../pickers/ProcessPicker.vue';

// ── 검색 조건 ──
const d = new Date();
const fmt = (v: Date) => v.toISOString().slice(0, 10);
const startDate = ref(fmt(d)), endDate = ref(fmt(d));
const ordState = ref(''), shift = ref('');
const includeDone = ref(false);
const searchWorkordNo = ref(''), searchPartNo = ref('');
const lineCd = ref(''), processCd = ref('');
const worker = ref(''), printer = ref('');
const printerList = ref<string[]>([]);
const lines = ref<any[]>([]), processes = ref<any[]>([]);

// Printer/Option States
const showPrinterSetting = ref(false);

function loadPrinterSettings() {
  const savedList = localStorage.getItem('local_printer_list');
  if (savedList) printerList.value = JSON.parse(savedList);
  printer.value = localStorage.getItem('selected_printer') || '';
}

function onPrinterSaved(newPrinter: string) {
  printer.value = newPrinter;
  loadPrinterSettings(); // 목록 갱신
}

// Picker States
const showItemPicker = ref(false);
const showLinePicker = ref(false);
const showProcessPicker = ref(false);

function onItemSelect(item: any) {
  searchPartNo.value = item.PARTNO;
}

function onLineSelect(item: any) {
  lineCd.value = item.LINECD;
}

function onProcessSelect(item: any) {
  processCd.value = item.PROCESSCD;
}

// ── 마스터 그리드 ──
const masterRows = ref<any[]>([]);
const selectedIdx = ref(-1);
const selectedRow = ref<any>(null);
const totalRecords = ref(0);

// ── 탭 ──
const tabs = [
  { key: 'result', label: '생산실적' },
  { key: 'history', label: '생산이력' },
  { key: 'defect', label: '불량이력' },
];
const activeTab = ref('result');

// ── 탭 데이터 ──
const summary = ref<any>({});
const resultRows = ref<any[]>([]);
const historyRows = ref<any[]>([]);
const defectRows = ref<any[]>([]);

// ── 버튼 활성화 조건 ──
const remainingQty = computed(() => {
  const ord = Number(summary.value.ORD_QTY || 0);
  const tot = Number(summary.value.TOT_PROD_QTY || 0);
  return ord - tot;
});

const canSaveIntermediate = computed(() => {
  if (!selectedRow.value || selectedRow.value.ORDSTATE !== 'STARTED') return false;
  const prod = Number(summary.value.PROD_QTY || 0);
  return prod > 0 && prod < remainingQty.value;
});

const canFinishWork = computed(() => {
  if (!selectedRow.value || selectedRow.value.ORDSTATE !== 'STARTED') return false;
  const prod = Number(summary.value.PROD_QTY || 0);
  // 작업지시수량 - 총생산실적수량 <= 생산실적수량 (즉, 이번 생산으로 목표 달성 또는 초과)
  return prod >= remainingQty.value && prod > 0;
});

// ── 자재 투입 관련 ──
const isInputMode = ref(false);
const matInput = ref({ MAT_LOTNO: '', INPUT_QTY: 0 });
const isLoading = ref(false);

// UNUSED REMOVED

function toggleInputMode() {
  if (!selectedRow.value) { alert('작업지시를 선택하세요.'); return; }
  
  if (selectedRow.value.ORDSTATE !== 'STARTED') {
    alert('자재 투입은 [작업중] 상태에서만 가능합니다.');
    return;
  }

  isInputMode.value = !isInputMode.value;
  if (isInputMode.value) {
    matInput.value = { MAT_LOTNO: '', INPUT_QTY: 0 };
    loadTabData(); // 모달 오픈 시 데이터 갱신 (BOM 및 투입 내역)
  }
}

async function deleteInput(row: any) {
  if (!confirm(`투입된 '${row.LOTNO}' 자재를 삭제하시겠습니까?`)) return;

  try {
    await api.delete('/api/production/field/input-material', {
      params: {
        workordno: selectedRow.value.WORKORDNO,
        mat_lotno: row.LOTNO
      }
    });
    alert('자재 투입이 삭제되었습니다.');
    await loadTabData();
  } catch (err: any) {
    alert('삭제 실패: ' + (err.response?.data?.message || err.message));
  }
}

async function onSaveMaterialInput(inputData: any) {
  matInput.value = inputData;
  await saveInputMaterial();
}

async function saveInputMaterial() {
  const checkedRows = resultRows.value.filter(r => r.RECORD_GUBUN === 'STOCK' && r._checked);
  
  if (isLoading.value) return;
  isLoading.value = true;

  if (checkedRows.length > 0) {
    try {
      // 체크된 모든 항목 투입 처리
      await Promise.all(checkedRows.map(r => 
        api.post('/api/production/field/input-material', {
          WORKORDNO: selectedRow.value.WORKORDNO,
          MAT_LOTNO: r.LOTNO,
          INPUT_QTY: r.STOCK_QTY
        })
      ));
      alert('선택된 자재들이 투입되었습니다.');
      isInputMode.value = false; // 모달 닫기
      await loadTabData(); // 메인 화면 갱신
      return;
    } catch (err: any) {
      alert('일괄 투입 실패: ' + (err.response?.data?.message || err.message));
      await loadTabData();
      return;
    } finally {
      isLoading.value = false;
    }
  }

  // 수동 입력 처리 (체크박스가 없는 경우)
  if (!matInput.value.MAT_LOTNO) { alert('투입할 자재를 선택하거나 LOT 번호를 입력하세요.'); isLoading.value = false; return; }
  if (!matInput.value.INPUT_QTY || matInput.value.INPUT_QTY <= 0) { alert('투입수량을 입력하세요.'); isLoading.value = false; return; }

  const stockRow = resultRows.value.find(r => r.LOTNO === matInput.value.MAT_LOTNO && r.RECORD_GUBUN === 'STOCK');
  if (stockRow && matInput.value.INPUT_QTY > stockRow.STOCK_QTY) {
    alert(`투입수량이 가용재고(${stockRow.STOCK_QTY})를 초과할 수 없습니다.`);
    isLoading.value = false;
    return;
  }

  try {
    await api.post('/api/production/field/input-material', {
      WORKORDNO: selectedRow.value.WORKORDNO,
      MAT_LOTNO: matInput.value.MAT_LOTNO,
      INPUT_QTY: matInput.value.INPUT_QTY
    });
    alert('자재가 투입되었습니다.');
    isInputMode.value = false; // 모달 닫기
    matInput.value = { MAT_LOTNO: '', INPUT_QTY: 0 };
    await loadTabData(); // 메인 화면 갱신
  } catch (err: any) {
    alert('투입 실패: ' + (err.response?.data?.message || err.message));
  } finally {
    isLoading.value = false;
  }
}

// ── 마스터 데이터 로드 ──
async function fetchMasterData() {
  try {
    const [rl, rp] = await Promise.all([
      api.get('/api/master/line', { params: { size: 200 } }),
      api.get('/api/master/process', { params: { size: 200 } })
    ]);
    lines.value = rl.data.data || [];
    processes.value = rp.data.data || [];
  } catch {}
}

// ── 작업지시 목록 조회 ──
async function fetchData() {
  selectedIdx.value = -1; selectedRow.value = null;
  clearDetail();
  try {
    const p: any = { page: 1, size: 100 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (shift.value) p.shift = shift.value;
    if (ordState.value) p.ord_state = ordState.value;
    if (lineCd.value) p.line_cd = lineCd.value;
    if (processCd.value) p.process_cd = processCd.value;
    if (searchWorkordNo.value) p.workord_no = searchWorkordNo.value;
    if (searchPartNo.value) p.search = searchPartNo.value;
    if (includeDone.value) p.include_done = true;
    const r = await api.get('/api/production/field/workorders', { params: p });
    masterRows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    totalRecords.value = (r.data?.data?.total ?? r.data?.total ?? 0) || 0;
  } catch {}
}

// ── 마스터 선택 ──
function onSelectMaster(row: any, idx: number) {
  selectedIdx.value = idx;
  selectedRow.value = row;
  loadTabData();
}

// ── 탭 데이터 로드 ──
async function loadTabData() {
  if (!selectedRow.value) return;
  const wno = selectedRow.value.WORKORDNO;
  console.log('Loading tab data for:', wno, 'Tab:', activeTab.value);
  if (activeTab.value === 'result') {
    try {
      const [rs, rr] = await Promise.all([
        api.get(`/api/production/field/summary/${wno}`),
        api.get(`/api/production/field/result/${wno}`)
      ]);
      summary.value = rs.data || {};
      // 체크 상태 초기화 속성 추가
      resultRows.value = (rr.data || []).map((r: any) => ({ ...r, _checked: false }));
    } catch {}
  } else if (activeTab.value === 'history') {
    try {
      const r = await api.get(`/api/production/field/history/${wno}`);
      historyRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []);
      console.log('History data:', historyRows.value);
    } catch {}
  } else if (activeTab.value === 'defect') {
    try {
      const r = await api.get(`/api/production/field/defect/${wno}`);
      defectRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []);
    } catch {}
  }
}

function clearDetail() {
  summary.value = {};
  resultRows.value = [];
  historyRows.value = [];
  defectRows.value = [];
}

// ── 상태 변경 ──
async function changeStatus(status: string) {
  if (!selectedRow.value) { alert('작업지시를 선택하세요.'); return; }
  if (isLoading.value) return;
  
  const currentStatus = selectedRow.value.ORDSTATE;
  
  if (status === 'STARTED' && currentStatus !== 'NEW') {
    alert('작업 시작은 [신규] 상태에서만 가능합니다.');
    return;
  }
  
  if (status === 'DONE' && currentStatus !== 'STARTED') {
    alert('작업 완료는 [작업중] 상태에서만 가능합니다.');
    return;
  }

  // 작업 완료 시 생산실적 수량이 입력되어 있으면 자동 저장 시도
  if (status === 'DONE' && (summary.value.PROD_QTY > 0)) {
    if (confirm(`입력된 생산실적(${summary.value.PROD_QTY})을 저장하고 작업을 종료하시겠습니까?`)) {
      isLoading.value = true;
      try {
        await api.post('/api/production/field/result-save', {
          WORKORDNO: selectedRow.value.WORKORDNO,
          PROD_QTY: summary.value.PROD_QTY,
          FAIL_QTY: summary.value.FAIL_QTY || 0
        });
        // 저장 후 입력 필드 초기화
        summary.value.PROD_QTY = 0;
        summary.value.FAIL_QTY = 0;
      } catch (err: any) {
        alert('실적 저장 실패로 작업을 종료할 수 없습니다: ' + (err.response?.data?.message || err.message));
        isLoading.value = false;
        return;
      }
    }
  }

  isLoading.value = true;
  try {
    await api.post('/api/production/field/status-change', {
      WORKORDNO: selectedRow.value.WORKORDNO,
      STATUS: status
    });
    alert(`상태가 변경되었습니다.`);
    await fetchData();
  } catch (err: any) {
    alert('상태 변경 실패: ' + (err.response?.data?.message || err.message));
  } finally {
    isLoading.value = false;
  }
}

// ── 중간 실적 저장 ──
async function saveIntermediateResult() {
  if (!selectedRow.value) { alert('작업지시를 선택하세요.'); return; }
  if (isLoading.value) return;

  if (selectedRow.value.ORDSTATE !== 'STARTED') {
    alert('작업중 상태에서만 중간실적 등록이 가능합니다.');
    return;
  }
  if (!summary.value.PROD_QTY || summary.value.PROD_QTY <= 0) {
    alert('생산실적 수량을 입력하세요.');
    return;
  }

  // 지시수량과 생산수량 비교 체크
  const ordQty = Number(summary.value.ORD_QTY || 0);
  const totProdQty = Number(summary.value.TOT_PROD_QTY || 0);
  const currentProdQty = Number(summary.value.PROD_QTY || 0);

  if (totProdQty + currentProdQty >= ordQty) {
    alert('총 생산수량이 지시수량과 같거나 초과되었습니다. [작업완료] 처리를 이용해 주세요.');
    return;
  }

  isLoading.value = true;
  try {
    await api.post('/api/production/field/result-save', {
      WORKORDNO: selectedRow.value.WORKORDNO,
      PROD_QTY: summary.value.PROD_QTY,
      FAIL_QTY: summary.value.FAIL_QTY || 0
    });
    
    // UI 즉시 반영을 위해 로컬 값 초기화 및 데이터 갱신
    summary.value.PROD_QTY = 0;
    summary.value.FAIL_QTY = 0;
    summary.value.GOOD_QTY = 0;

    alert('중간 실적이 저장되었습니다.');
    await fetchData(); // 마스터 그리드 갱신 (신규 LOT번호 확인)
    await loadTabData(); // 집계 데이터 갱신
  } catch (err: any) {
    alert('저장 실패: ' + (err.response?.data?.message || err.message));
  } finally {
    isLoading.value = false;
  }
}

// ── 작업 취소 ──
async function cancelProduction() {
  if (!selectedRow.value) { alert('작업지시를 선택하세요.'); return; }
  
  const currentStatus = selectedRow.value.ORDSTATE;
  if (currentStatus !== 'STARTED') {
    alert('작업 취소는 [작업중] 상태에서만 가능합니다.');
    return;
  }

  const totalQty = summary.value.TOT_PROD_QTY || 0;
  if (totalQty > 0) {
    alert('이미 등록된 생산 실적이 있어 작업을 취소할 수 없습니다. 실적 삭제 후 취소해 주세요.');
    return;
  }

  if (!confirm('정말로 작업을 취소하시겠습니까? 상태가 [신규]로 변경됩니다.')) {
    return;
  }

  try {
    await api.post('/api/production/field/cancel-production', {
      WORKORDNO: selectedRow.value.WORKORDNO
    });
    alert('작업이 취소되었습니다.');
    fetchData();
  } catch (err: any) {
    alert('취소 실패: ' + (err.response?.data?.message || err.message));
  }
}

// ── 실적 행 삭제 ──
async function deleteHistoryRow(row: any) {
  if (!confirm(`'${row.LOTNO}' 실적을 삭제하시겠습니까?`)) return;

  try {
    await api.delete(`/api/production/status/result/${row.LOTNO}`);
    alert('실적이 삭제되었습니다.');
    loadTabData(); // 상세 갱신
    fetchData(); // 마스터 그리드 갱신
  } catch (err: any) {
    alert('삭제 실패: ' + (err.response?.data?.message || err.message));
  }
}

// ── 탭 변경 시 데이터 로드 ──
watch(activeTab, () => { if (selectedRow.value) loadTabData(); });
watch(includeDone, () => { fetchData(); });

// ── 생산수량 변경 시 양품수량 자동 계산 ──
watch(
  () => [summary.value.PROD_QTY, summary.value.FAIL_QTY],
  ([prod, fail]) => {
    summary.value.GOOD_QTY = (Number(prod) || 0) - (Number(fail) || 0);
  }
);

onMounted(() => { 
  fetchMasterData(); 
  fetchData(); 
  loadPrinterSettings(); 
});
</script>

<style scoped>
.field-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f4f6f9;
  font-family: 'Malgun Gothic', sans-serif;
  color: #333;
}

/* Header */
.field-header {
  background-color: #4b8a3e; /* Logistics Green */
  color: white;
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  z-index: 10;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.worker-info, .printer-select {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.15);
  padding: 5px 15px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.search-input {
  display: flex;
  align-items: center;
}

.search-input input, .search-input select {
  padding: 4px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px 0 0 4px;
  width: 120px;
  font-size: 0.9rem;
}

.printer-select select {
  padding: 3px 8px;
  border-radius: 4px;
  border: none;
  font-size: 0.9rem;
}

.btn-search-small {
  padding: 4px 10px;
  border: 1px solid #ced4da;
  border-left: none;
  background: #e9ecef;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.btn-icon {
  background: white;
  color: #2c3e50;
  border: 1px solid #ddd;
  padding: 6px 15px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.btn-icon.btn-close {
  background: #dc3545;
  color: white;
  border-color: #c82333;
}

/* Search Section */
.search-section {
  background: #f8f9fa;
  padding: 12px 20px;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px 25px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-item label {
  font-weight: 700;
  color: #495057;
  font-size: 0.9rem;
  white-space: nowrap;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-range input {
  padding: 5px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  width: 130px;
}

.s-select {
  padding: 5px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  min-width: 100px;
}

.checkbox-item {
  gap: 5px;
}

.checkbox-item input {
  width: 18px;
  height: 18px;
}

/* Main Content (Top Master Grid) */
.main-content {
  flex: 2; /* 상단 그리드 영역을 2/5 비율로 설정 */
  padding: 10px 15px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-wrap {
  flex: 1;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: auto;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.master-grid {
  width: 100%;
  border-collapse: collapse;
}

.master-grid th {
  background: #f1f3f5;
  color: #495057;
  font-weight: 700;
  padding: 10px 8px;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 1;
  white-space: nowrap;
}

.master-grid td {
  padding: 8px;
  border-bottom: 1px solid #eee;
  font-size: 0.9rem;
  white-space: nowrap;
}

.master-grid tr:hover {
  background-color: #f8f9fa;
}

.master-grid .row-selected {
  background-color: #e7f5ff !important;
}

.center { text-align: center; }
.right { text-align: right; }
.empty { text-align: center; color: #adb5bd; padding: 40px !important; }

/* Tab Section (Bottom Area) */
.tab-section {
  flex: 3; /* 하단 영역을 3/5 비율로 설정하여 더 넓게 배분 */
  display: flex;
  flex-direction: column;
  min-height: 0;
  margin: 0 15px 15px 15px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.tab-bar {
  display: flex;
  background: #e9ecef;
  padding: 5px 5px 0 5px;
  gap: 2px;
}

.tab-btn {
  padding: 8px 20px;
  border: none;
  background: #dee2e6;
  font-weight: 700;
  color: #495057;
  cursor: pointer;
  border-radius: 6px 6px 0 0;
  transition: all 0.2s;
}

.tab-btn.active {
  background: white;
  color: #2c3e50;
  position: relative;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #4b8a3e;
  border-radius: 3px 3px 0 0;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
}

/* Result Styles */
.result-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  background: #fff;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.result-info-cards {
  display: flex;
  gap: 10px;
}

.info-card {
  display: flex;
  flex-direction: column;
  padding: 4px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #adb5bd;
}

.info-card.highlight {
  border-left-color: #4b8a3e;
  background: #e7f5ff;
}

.card-label {
  font-size: 0.7rem;
  font-weight: 800;
  color: #6c757d;
  text-transform: uppercase;
}

.card-value {
  font-size: 1.1rem;
  font-weight: 800;
  color: #2c3e50;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.btn-status {
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid #ddd;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
}

.btn-status.mat-input { background: #fd7e14; color: white; border-color: #e8590c; }
.btn-status.start { background: #40c057; color: white; border-color: #2f9e44; }
.btn-status.mid { background: #339af0; color: white; border-color: #1c7ed6; }
.btn-status.done { background: #868e96; color: white; border-color: #495057; }
.btn-status.cancel { background: #fa5252; color: white; border-color: #e03131; }

/* Metric Grid */
.metric-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.metric-card {
  background: white;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  min-height: 50px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.metric-card.action {
  border: 2px solid #fd7e14;
  background: linear-gradient(135deg, #fffaf0 0%, #fff 100%);
  box-shadow: 0 4px 6px -1px rgba(253, 126, 20, 0.2);
}

.metric-card label {
  font-size: 0.8rem;
  font-weight: 800;
  color: #868e96;
  margin-bottom: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.metric-val {
  font-size: 1.25rem;
  font-weight: 900;
  color: #212529;
  text-align: right;
}

.metric-val.success { color: #2f9e44; }
.metric-val.danger { color: #e03131; }

.metric-input {
  width: 90px;
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 1.2rem;
  font-weight: 900;
  text-align: right;
  color: #fd7e14;
  background: white;
  transition: border-color 0.2s;
}

.metric-input:focus {
  outline: none;
  border-color: #fd7e14;
  box-shadow: 0 0 0 3px rgba(253, 126, 20, 0.1);
}

.metric-input.danger {
  color: #e03131;
  border-color: #ffa8a8;
}

.metric-input.danger:focus {
  border-color: #e03131;
  box-shadow: 0 0 0 3px rgba(224, 49, 49, 0.1);
}

/* Tab Toolbars */
.tab-toolbar-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background: #f1f3f5;
  border-bottom: 1px solid #dee2e6;
  margin: -15px -15px 12px -15px;
}

.tab-toolbar-modern.danger {
  background: #fff5f5;
  border-bottom-color: #ffc9c9;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-title {
  font-size: 1rem;
  font-weight: 800;
  color: #343a40;
}

.btn-action-small {
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-action-small:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
}

.btn-action-small:active {
  transform: translateY(0);
}

.btn-action-small.grey {
  background: #f8f9fa;
  color: #495057;
  border-color: #dee2e6;
}

.btn-action-small.grey:hover {
  background: #e9ecef;
  border-color: #ced4da;
}

.btn-action-small.blue {
  background: #339af0;
  color: white;
  border-color: #228be6;
  box-shadow: 0 2px 4px rgba(51, 154, 240, 0.2);
}

.btn-action-small.blue:hover {
  background: #228be6;
  box-shadow: 0 4px 8px rgba(51, 154, 240, 0.3);
}

/* Sub sections */
.sub-title {
  font-weight: 800;
  font-size: 0.85rem;
  color: #495057;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mat-list-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.table-wrap.mini {
  flex: 1;
  max-height: none;
}

.detail-grid-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-grid {
  width: 100%;
  border-collapse: collapse;
}

.detail-grid th {
  background: #f1f3f5;
  padding: 10px 8px;
  border-bottom: 2px solid #dee2e6;
  font-size: 0.85rem;
  font-weight: 700;
  text-align: left;
}

.detail-grid td {
  padding: 8px;
  border-bottom: 1px solid #eee;
  font-size: 0.85rem;
}

.btn-grid-del {
  background: #fff;
  border: 1px solid #ffc9c9;
  color: #fa5252;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-grid-del:hover {
  background: #fa5252;
  color: #fff;
  border-color: #fa5252;
  box-shadow: 0 2px 4px rgba(250, 82, 82, 0.2);
}

/* Status Bar */
.status-bar {
  padding: 6px 20px;
  background: #e9ecef;
  border-top: 1px solid #dee2e6;
  font-size: 0.85rem;
  font-weight: 700;
  color: #495057;
  flex-shrink: 0;
}
</style>
