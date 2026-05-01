<template>
  <div class="field-page">
    <!-- ═══ 헤더 바 ═══ -->
    <header class="field-header">
      <div class="header-left">
        <span class="header-title">생산관리</span>
        <label class="hdr-label">작업자</label>
        <input type="text" v-model="worker" class="hdr-input" style="width:100px" />
        <button class="hdr-btn-search" @click="fetchData">🔍</button>
      </div>
      <div class="header-right">
        <label class="hdr-label">프린터</label>
        <select v-model="printer" class="hdr-select">
          <option value="">(선택하세요)</option>
        </select>
        <button class="hdr-btn action" @click="fetchData">조회</button>
        <button class="hdr-btn">분류</button>
        <button class="hdr-btn finish" @click="$router.push('/select-mode')">종료</button>
        <button class="hdr-btn">옵션</button>
      </div>
    </header>

    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="search-row">
        <label>작업일</label>
        <input type="date" v-model="startDate" class="s-input" />
        <span>~</span>
        <input type="date" v-model="endDate" class="s-input" />
        <label>상태</label>
        <select v-model="ordState" class="s-select">
          <option value="">(선택...)</option>
          <option value="NEW">신규</option>
          <option value="SETTING">시세팅</option>
          <option value="STARTED">작업중</option>
          <option value="DONE">완료</option>
        </select>
        <label class="chk-wrap"><input type="checkbox" v-model="includeDone" /> 완료포함</label>
        <label>주/야</label>
        <select v-model="shift" class="s-select">
          <option value="">(선택...)</option>
          <option value="주간">주간</option>
          <option value="야간">야간</option>
        </select>
        <label>구분</label>
        <select v-model="gubun" class="s-select" style="width:80px">
          <option value="정상">정상</option>
        </select>
      </div>
      <div class="search-row">
        <label>작지번호</label>
        <div class="input-search-wrap">
          <input type="text" v-model="searchWorkordNo" class="s-input" @keyup.enter="fetchData" />
          <button class="btn-s" @click="fetchData">🔍</button>
        </div>
        <label>품번</label>
        <div class="input-search-wrap">
          <input type="text" v-model="searchPartNo" class="s-input" @keyup.enter="fetchData" />
          <button class="btn-s" @click="fetchData">🔍</button>
        </div>
        <label>라인</label>
        <select v-model="lineCd" class="s-select">
          <option value="">(선택하세요)</option>
          <option v-for="l in lines" :key="l.LINECD" :value="l.LINECD">{{ l.LINENM }}</option>
        </select>
        <label>공정</label>
        <select v-model="processCd" class="s-select">
          <option value="">(선택하세요)</option>
          <option v-for="p in processes" :key="p.PROCESSCD" :value="p.PROCESSCD">{{ p.PROCESSNM }}</option>
        </select>
      </div>
    </section>

    <!-- ═══ 마스터 그리드 ═══ -->
    <div class="master-grid-wrap">
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
          <div class="result-info">
            <span>총생산실적 <b>{{ summary.TOT_PROD_QTY || 0 }}</b></span>
            <span>잔량 <b>{{ (summary.ORD_QTY || 0) - (summary.TOT_PROD_QTY || 0) }}</b></span>
          </div>
          <div class="result-actions">
            <button class="btn-status mat-input" @click="toggleInputMode">📦 자재투입</button>
            <button class="btn-status start" :disabled="selectedRow?.ORDSTATE !== 'NEW'" @click="changeStatus('STARTED')">▶ 작업시작</button>
            <button class="btn-status cancel" :disabled="selectedRow?.ORDSTATE !== 'STARTED' || (summary.TOT_PROD_QTY || 0) > 0" @click="cancelProduction">⟲ 작업취소</button>
            <button class="btn-status mid" :disabled="!canSaveIntermediate" @click="saveIntermediateResult">✚ 중간실적</button>
            <button class="btn-status done" :disabled="!canFinishWork" @click="changeStatus('DONE')">■ 작업완료</button>
          </div>
        </div>

        <table class="summary-table">
          <thead>
            <tr>
              <th>작업지시수량</th><th>총생산실적수량</th><th>총양품수량</th><th>총불량수량</th>
              <th class="italic-head">생산실적수량</th><th class="italic-head">양품수량</th><th class="italic-head">불량수량</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ summary.ORD_QTY || 0 }}</td>
              <td>{{ summary.TOT_PROD_QTY || 0 }}</td>
              <td>{{ summary.TOT_GOOD_QTY || 0 }}</td>
              <td>{{ summary.TOT_FAIL_QTY || 0 }}</td>
              <td class="italic-val"><input type="number" v-model.number="summary.PROD_QTY" class="edit-input" /></td>
              <td class="italic-val">{{ summary.GOOD_QTY }}</td>
              <td class="italic-val"><input type="number" v-model.number="summary.FAIL_QTY" class="edit-input" /></td>
            </tr>
          </tbody>
        </table>

        <!-- 메인 화면 생산실적 상세 그리드 (투입된 자재 목록) -->
        <div class="detail-grid-wrap" style="margin-top: 10px; border-top: 1px solid #cbd5e0;">
          <div class="sub-title" style="padding: 8px 12px; font-weight: bold; font-size: 0.82rem; color: #4a5568; background: #f8f9fa;">
            투입된 자재 목록 (작업 진행중)
          </div>
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

      <!-- 자재투입 모달 -->
      <Teleport to="body">
        <div v-if="isInputMode" class="mat-modal-overlay">
          <div class="mat-modal-window">
            <div class="mat-modal-header">
              <span class="mat-modal-title">자재투입등록</span>
              <div class="mat-modal-actions">
                <button class="mat-btn-apply" @click="saveInputMaterial">
                  <span class="icon-v">✔️</span> 적용
                </button>
                <button class="mat-btn-close" @click="isInputMode = false">
                  <span class="icon-x">❌</span> 닫기
                </button>
              </div>
            </div>
            <div class="mat-modal-content">
              <div class="mat-sub-header">
                <span class="sub-icon">🔄</span>
                <span class="sub-title">자재투입</span>
              </div>

              <div class="mat-input-form">
                <div class="form-group">
                  <label><span class="dot"></span> 투입LOT No.</label>
                  <div class="input-with-btn">
                    <input type="text" v-model="matInput.MAT_LOTNO" @keyup.enter="saveInputMaterial" placeholder="LOT 번호를 입력하세요" />
                    <button class="btn-lookup">🔍</button>
                  </div>
                </div>
                <div class="form-group">
                  <label><span class="dot"></span> 적용수량</label>
                  <input type="number" v-model.number="matInput.INPUT_QTY" class="qty-input" />
                </div>
              </div>

              <div class="mat-sub-header">
                <span class="sub-icon">🔄</span>
                <span class="sub-title">자재투입내역 및 가용재고 (행 클릭 시 자동 선택)</span>
              </div>

              <div class="mat-grid-area">
                <table class="mat-grid">
                  <thead>
                    <tr>
                      <th style="width:30px"><input type="checkbox" :checked="isAllMatChecked" @change="toggleAllMat" /></th>
                      <th style="width:80px">구분</th>
                      <th>LOT No.</th>
                      <th>품번</th>
                      <th>품명</th>
                      <th style="width:40px">단위</th>
                      <th>투입수량</th>
                      <th>소요량</th>
                      <th>재고수량</th>
                      <th>위치</th>
                      <th style="width:60px">관리</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="resultRows.length === 0">
                      <td colspan="11" style="text-align:center; padding:20px; color:#999;">데이터 없음</td>
                    </tr>
                    <tr v-for="(r, i) in resultRows" :key="i" 
                        :class="{ 'row-input': r.RECORD_GUBUN === 'INPUT', 'row-stock': r.RECORD_GUBUN === 'STOCK', 'row-clickable': true }"
                        @click="onRowClick(r)">
                      <td class="center" @click.stop>
                        <input type="checkbox" v-model="r._checked" v-if="r.RECORD_GUBUN === 'STOCK'" />
                      </td>
                      <td class="center">
                        <span v-if="r.RECORD_GUBUN === 'INPUT'" class="badge-input">투입완료</span>
                        <span v-else class="badge-stock">가용재고</span>
                      </td>
                      <td :style="{ fontWeight: r.RECORD_GUBUN === 'INPUT' ? '700' : 'normal' }">{{ r.LOTNO || '-' }}</td>
                      <td>{{ r.PARTNO }}</td>
                      <td>{{ r.PARTNM }}</td>
                      <td class="center">{{ r.UNIT }}</td>
                      <td class="right" :style="{ color: r.RECORD_GUBUN === 'INPUT' ? '#2ecc71' : 'inherit', fontWeight: 'bold' }">{{ r.INPUT_QTY || 0 }}</td>
                      <td class="right">{{ r.NEED_QTY }}</td>
                      <td class="right">{{ r.STOCK_QTY || 0 }}</td>
                      <td>{{ r.LOCATIONNAME }}</td>
                      <td class="center" @click.stop>
                        <button v-if="r.RECORD_GUBUN === 'INPUT'" class="btn-grid-del" @click="deleteInput(r)">삭제</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="mat-modal-footer">
                <div class="record-info">
                  <button class="btn-nav">|◀</button>
                  <button class="btn-nav">◀</button>
                  <input type="text" :value="'Record ' + (resultRows.length > 0 ? '1' : '0') + ' of ' + resultRows.length" readonly class="nav-text" />
                  <button class="btn-nav">▶</button>
                  <button class="btn-nav">▶|</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- 탭 2: 생산이력 -->
      <div v-if="activeTab === 'history'" class="tab-content">
        <div class="tab-toolbar">
          <span class="toolbar-title">생산이력</span>
          <div class="toolbar-actions">
            <button class="btn-toolbar">비가동 등록</button>
            <button class="btn-toolbar">라벨출력</button>
          </div>
        </div>
        <div class="detail-grid-wrap">
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

      <!-- 탭 3: 불량이력 -->
      <div v-if="activeTab === 'defect'" class="tab-content">
        <div class="tab-toolbar">
          <span class="toolbar-title">불량비역조회</span>
          <div class="toolbar-actions">
            <button class="btn-toolbar">라벨출력</button>
          </div>
        </div>
        <div class="detail-grid-wrap">
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

    <!-- 하단 상태바 -->
    <div class="status-bar">
      Record {{ masterRows.length }} of {{ totalRecords }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import api from '../../api';

// ── 검색 조건 ──
const d = new Date();
const fmt = (v: Date) => v.toISOString().slice(0, 10);
const startDate = ref(fmt(d)), endDate = ref(fmt(d));
const ordState = ref(''), shift = ref(''), gubun = ref('정상');
const includeDone = ref(false);
const searchWorkordNo = ref(''), searchPartNo = ref('');
const lineCd = ref(''), processCd = ref('');
const worker = ref(''), printer = ref('');
const lines = ref<any[]>([]), processes = ref<any[]>([]);

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

const isAllMatChecked = computed(() => {
  const stockRows = resultRows.value.filter(r => r.RECORD_GUBUN === 'STOCK');
  return stockRows.length > 0 && stockRows.every(r => r._checked);
});

function toggleAllMat(e: any) {
  const chk = e.target.checked;
  resultRows.value.forEach(r => {
    if (r.RECORD_GUBUN === 'STOCK') r._checked = chk;
  });
}

function onRowClick(row: any) {
  // 가용재고 항목을 클릭한 경우 해당 LOT 정보와 수량을 폼에 자동 입력
  if (row.RECORD_GUBUN === 'STOCK') {
    matInput.value.MAT_LOTNO = row.LOTNO;
    matInput.value.INPUT_QTY = row.STOCK_QTY; // 기본적으로 전체 가용 수량 제안
  }
}

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
      alert('일부 자재 투입 실패: ' + (err.response?.data?.message || err.message));
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

onMounted(() => { fetchMasterData(); fetchData(); });
</script>

<style scoped>
.field-page { display:flex; flex-direction:column; height:100vh; font-family:'Segoe UI',sans-serif; font-size:.85rem; background:#f0f2f5; }

/* 헤더 */
.field-header { display:flex; justify-content:space-between; align-items:center; padding:6px 12px; background:linear-gradient(180deg,#e8edf2,#d0d8e0); border-bottom:1px solid #b0b8c0; flex-shrink:0; }
.header-left,.header-right { display:flex; align-items:center; gap:6px; }
.header-title { font-size:1rem; font-weight:800; color:#1a3a5c; margin-right:12px; }
.hdr-label { font-size:.82rem; color:#4a5568; font-weight:600; }
.hdr-input { padding:3px 6px; border:1px solid #b0b8c0; border-radius:3px; font-size:.82rem; }
.hdr-btn-search { background:#fff; border:1px solid #b0b8c0; border-radius:3px; cursor:pointer; padding:2px 6px; }
.hdr-select { padding:3px 6px; border:1px solid #b0b8c0; border-radius:3px; font-size:.82rem; min-width:100px; }
.hdr-btn { background:linear-gradient(180deg,#f8f9fa,#e2e6ea); border:1px solid #b0b8c0; padding:4px 14px; border-radius:3px; font-size:.82rem; font-weight:600; cursor:pointer; color:#2d3748; }
.hdr-btn.action { background:linear-gradient(180deg,#d6eaf8,#aed6f1); color:#1a5276; }
.hdr-btn.finish { background:linear-gradient(180deg,#fde8e8,#f5b7b1); color:#922b21; }

/* 검색 */
.search-section { padding:6px 12px; background:#fff; border-bottom:1px solid #dde1e6; flex-shrink:0; }
.search-row { display:flex; align-items:center; gap:6px; margin-bottom:4px; flex-wrap:wrap; }
.search-row:last-child { margin-bottom:0; }
.search-row label { font-size:.82rem; font-weight:600; color:#4a5568; white-space:nowrap; }
.s-input { padding:3px 6px; border:1px solid #cbd5e0; border-radius:3px; font-size:.82rem; width:120px; }
.s-select { padding:3px 6px; border:1px solid #cbd5e0; border-radius:3px; font-size:.82rem; min-width:90px; }
.chk-wrap { display:flex; align-items:center; gap:3px; font-weight:500!important; cursor:pointer; }
.input-search-wrap { display:flex; align-items:stretch; }
.input-search-wrap input { border-radius:3px 0 0 3px; border-right:none; }
.btn-s { background:#eaf2f8; border:1px solid #cbd5e0; border-left:none; border-radius:0 3px 3px 0; padding:0 6px; cursor:pointer; }

/* 마스터 그리드 */
.master-grid-wrap { flex:1; overflow:auto; border-bottom:2px solid #85c1e9; background:#fff; min-height:0; }
.master-grid { width:max-content; min-width:100%; border-collapse:collapse; }
.master-grid thead { position:sticky; top:0; z-index:2; }
.master-grid th { background:linear-gradient(180deg,#d6eaf8,#aed6f1); color:#1a5276; font-weight:600; padding:6px 8px; text-align:left; border-bottom:2px solid #85c1e9; white-space:nowrap; font-size:.8rem; }
.master-grid td { padding:4px 8px; border-bottom:1px solid #edf0f3; white-space:nowrap; font-size:.8rem; }
.master-grid .center { text-align:center; }
.master-grid .right { text-align:right; }
.master-grid .empty { text-align:center; color:#a0aec0; padding:30px!important; }
.master-grid tr:hover { background:#f7fafc; }
.master-grid .row-selected { background:#d6eaf8!important; }

/* 탭 영역 */
.tab-section { flex:1; display:flex; flex-direction:column; min-height:0; background:#fff; }
.tab-bar { display:flex; border-bottom:2px solid #d6eaf8; background:#eaf2f8; flex-shrink:0; padding-left:8px; }
.tab-btn { padding:8px 18px; border:none; background:transparent; font-size:.84rem; font-weight:600; color:#5d6d7e; cursor:pointer; border-bottom:3px solid transparent; margin-bottom:-2px; transition:all .15s; }
.tab-btn.active { color:#1a5276; border-bottom-color:#2980b9; background:#fff; }
.tab-btn:hover:not(.active) { color:#2c3e50; background:rgba(255,255,255,.5); }

/* 탭 컨텐트 */
.tab-content { flex:1; display:flex; flex-direction:column; overflow:hidden; }

/* 생산실적 상단 */
.result-top { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; border-bottom:1px solid #edf0f3; flex-shrink:0; }
.result-info { display:flex; gap:16px; font-size:.85rem; color:#4a5568; }
.result-info b { color:#1a5276; font-weight:700; }
.result-actions { display:flex; gap:6px; }
.btn-status { padding:5px 14px; border:1px solid #b0b8c0; border-radius:4px; font-size:.82rem; font-weight:600; cursor:pointer; }
.btn-status.mat-input { background:linear-gradient(180deg,#ebf5fb,#d6eaf8); color:#1a5276; border-color:#aed6f1; }
.btn-status.setting { background:linear-gradient(180deg,#fef9e7,#f9e79f); color:#7d6608; }

/* 자재투입 박스 */
.material-input-box { background:#f7fafc; padding:10px 15px; border-bottom:1px solid #e2e8f0; animation:slideDown 0.2s ease-out; }
.mi-row { display:flex; align-items:center; gap:10px; }
.mi-row label { font-size:.82rem; font-weight:700; color:#4a5568; }
.mi-input { padding:5px 8px; border:1px solid #cbd5e0; border-radius:4px; font-size:.82rem; }
.btn-mi-save { background:#3182ce; color:#fff; border:none; padding:5px 15px; border-radius:4px; font-weight:600; cursor:pointer; }
.btn-mi-close { background:none; border:none; font-size:1.1rem; color:#a0aec0; cursor:pointer; margin-left:auto; }
@keyframes slideDown { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }

.btn-status.start { background:linear-gradient(180deg,#d5f5e3,#82e0aa); color:#1e8449; }
.btn-status.mid { background:linear-gradient(180deg,#e8f8f5,#a3e4d7); color:#117a65; }
.btn-status.cancel { background:linear-gradient(180deg,#f2f4f4,#ccd1d1); color:#424949; }
.btn-status.done { background:linear-gradient(180deg,#fde8e8,#f5b7b1); color:#922b21; }
.btn-status:disabled { background:#bdc3c7 !important; border-color:#bdc3c7 !important; color:#fff !important; cursor:not-allowed; opacity:0.6; }

/* 집계 테이블 */
.summary-table { width:100%; border-collapse:collapse; flex-shrink:0; }
.summary-table th { background:linear-gradient(180deg,#2980b9,#1a6fa0); color:#fff; font-weight:600; padding:8px 6px; text-align:center; font-size:.82rem; border:1px solid #1a5276; }
.summary-table td { padding:8px 6px; text-align:center; font-size:.9rem; font-weight:700; color:#2c3e50; border:1px solid #dde1e6; background:#fff; }
.italic-head { font-style:italic; background:linear-gradient(180deg,#5dade2,#3498db)!important; }
.italic-val { font-style:italic; color:#2980b9; }
.edit-input { width: 60px; text-align: center; border: 1px solid #b0b8c0; border-radius: 3px; padding: 2px 4px; font-size: .9rem; font-weight: 700; color: #2980b9; }
.edit-input:focus { outline: none; border-color: #3498db; box-shadow: 0 0 3px rgba(52, 152, 219, 0.5); }

/* 상세 그리드 */
.detail-grid-wrap { flex:1; overflow:auto; }
.detail-grid { width:100%; border-collapse:collapse; }
.detail-grid thead { position:sticky; top:0; z-index:1; }
.detail-grid th { background:#eaf2f8; color:#1a5276; font-weight:600; padding:6px 8px; text-align:left; border-bottom:1px solid #d6eaf8; font-size:.8rem; white-space:nowrap; }
.detail-grid td { padding:4px 8px; border-bottom:1px solid #f0f2f5; font-size:.8rem; white-space:nowrap; }
.detail-grid .center { text-align:center; }
.detail-grid .right { text-align:right; }
.detail-grid .empty { text-align:center; color:#a0aec0; padding:30px!important; }

/* 자재투입 모달 스타일 */
.mat-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.mat-modal-window {
  width: 900px; max-width: 95vw; background: #fff; border: 1px solid #777; box-shadow: 5px 5px 20px rgba(0,0,0,0.3);
  display: flex; flex-direction: column; animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

.mat-modal-header {
  background: #5d9b9d; padding: 5px 12px; display: flex; justify-content: space-between; align-items: center;
  color: #000; font-weight: bold; border-bottom: 1px solid #4a7d7e;
}
.mat-modal-title { font-size: 0.95rem; }
.mat-modal-actions { display: flex; gap: 5px; }
.mat-modal-actions button {
  padding: 2px 12px; border: 1px solid #777; border-radius: 2px; cursor: pointer;
  display: flex; align-items: center; gap: 6px; font-weight: bold; font-size: 0.85rem; background: #fdfdfd; box-shadow: 1px 1px 1px rgba(0,0,0,0.1);
}
.mat-modal-actions button:hover { background: #eee; }
.icon-v { color: #2ecc71; font-size: 0.9rem; }
.icon-x { color: #e74c3c; font-size: 0.9rem; }

.mat-modal-content { padding: 8px; background: #e0e6e9; flex: 1; display: flex; flex-direction: column; gap: 8px; }
.mat-sub-header { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.sub-title { font-weight: bold; font-size: 0.9rem; color: #333; }
.sub-icon { color: #5d9b9d; font-size: 1rem; }

.mat-input-form {
  background: #f8f9fa; border: 1px solid #b0c4de; padding: 12px 20px; display: flex; gap: 50px; flex-shrink: 0;
}
.form-group { display: flex; align-items: center; gap: 12px; }
.form-group label { display: flex; align-items: center; gap: 6px; font-weight: bold; white-space: nowrap; font-size: 0.85rem; color: #444; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: #90be6d; display: inline-block; border: 1px solid #7fb05e; }

.input-with-btn { display: flex; align-items: stretch; }
.input-with-btn input { width: 280px; padding: 4px 8px; border: 1px solid #aebac1; font-size: 0.9rem; }
.btn-lookup { padding: 0 8px; background: #f0f0f0; border: 1px solid #aebac1; border-left: none; cursor: pointer; font-size: 0.8rem; }
.qty-input { width: 100px; padding: 4px 8px; border: 1px solid #aebac1; text-align: right; font-weight: bold; font-size: 1.1rem; color: #2c3e50; }

.mat-grid-area { background: #fff; border: 1px solid #b0c4de; flex: 1; overflow: auto; min-height: 250px; }
.mat-grid { width: 100%; border-collapse: collapse; min-width: 800px; }
.mat-grid thead { position: sticky; top: 0; z-index: 1; }
.mat-grid th { background: #f0f4f7; border: 1px solid #cbd5e0; padding: 6px; font-size: 0.8rem; color: #333; font-weight: 600; text-align: left; }
.mat-grid td { border: 1px solid #edf2f7; padding: 4px 8px; font-size: 0.8rem; color: #444; }
.mat-grid tr:nth-child(even) { background: #fafbfc; }
.mat-grid .center { text-align: center; }
.mat-grid .right { text-align: right; }

.row-clickable { cursor: pointer; transition: background 0.2s; }
.row-clickable:hover { background: #eaf2f8 !important; }
.row-input { background: #fff; }
.row-stock { background: #fdfdfd; color: #666; }

.badge-input { background: #2ecc71; color: #fff; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }
.badge-stock { background: #95a5a6; color: #fff; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }

.mat-modal-footer {
  background: #f0f4f7; border-top: 1px solid #cbd5e0; padding: 4px 10px; flex-shrink: 0;
}
.record-info { display: flex; align-items: center; gap: 2px; }
.btn-nav { padding: 2px 6px; background: #fff; border: 1px solid #cbd5e0; cursor: pointer; font-size: 0.75rem; color: #555; }
.nav-text { width: 120px; text-align: center; font-size: 0.75rem; padding: 2px; border: 1px solid #cbd5e0; background: #f9fafb; outline: none; }

/* 탭 툴바 */
.tab-toolbar { display:flex; justify-content:space-between; align-items:center; padding:6px 12px; border-bottom:1px solid #edf0f3; flex-shrink:0; }
.toolbar-title { font-weight:700; color:#1a5276; font-size:.88rem; }
.toolbar-actions { display:flex; gap:6px; }
.btn-toolbar { background:#fff; border:1px solid #b0b8c0; padding:4px 12px; border-radius:3px; font-size:.82rem; font-weight:600; cursor:pointer; color:#2d3748; }
.btn-toolbar:hover { background:#eaf2f8; }

/* 그리드 내 삭제 버튼 */
.btn-grid-del { background:#fff; border:1px solid #e74c3c; color:#e74c3c; padding:2px 8px; border-radius:3px; font-size:.75rem; font-weight:600; cursor:pointer; }
.btn-grid-del:hover { background:#e74c3c; color:#fff; }

/* 상태바 */
.status-bar { padding:4px 12px; background:#e8edf2; border-top:1px solid #cbd5e0; font-size:.78rem; color:#718096; flex-shrink:0; }
</style>
