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
          <button class="btn-wo" @click="openWoModal">✅ 작업 지시서 생성</button>
        </div>
      </div>
    </section>

    <!-- ═══ 달력형 그리드 ═══ -->
    <div class="plan-grid-wrap">
      <table class="plan-grid" v-if="planData">
        <thead>
          <tr class="day-num-row">
            <th class="freeze chk-col"><input type="checkbox" v-model="allChecked" @change="toggleAll" /></th>
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
            <th class="freeze"></th>
            <th class="freeze"></th><th class="freeze"></th><th class="freeze"></th>
            <th class="freeze"></th><th class="freeze"></th><th class="freeze"></th>
            <th v-for="dt in dates" :key="'l'+dt"
                :class="['day-col', isToday(dt) ? 'today' : '', isWeekend(dt) ? 'weekend' : '']">
              계획
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="planData.data.length===0">
            <td :colspan="7+dates.length" class="empty">데이터 없음</td>
          </tr>
          <tr v-for="(row, ri) in planData.data" :key="ri" :class="{'row-selected': row._checked}">
            <td class="freeze chk-col"><input type="checkbox" v-model="row._checked" /></td>
            <td class="freeze">{{ row.ORDERNUM }}</td>
            <td class="freeze">{{ row.PARTNO }}</td>
            <td class="freeze">{{ row.PARTNM }}</td>
            <td class="freeze">{{ row.STANDARD }}</td>
            <td class="freeze num">{{ row.STOCKQTY || 0 }}</td>
            <td class="freeze num total-cell">{{ row.TOTAL || 0 }}</td>
            <td v-for="dt in dates" :key="dt"
                :class="['day-col', isToday(dt)?'today':'', isWeekend(dt)?'weekend':'']">
              <input type="number" class="cell-input"
                     :value="row[dt] || ''"
                     @change="onCellChange(row, dt, $event)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══ 작업지시서 생성 모달 ═══ -->
    <div v-if="showWoModal" class="modal-overlay" @click.self="showWoModal=false">
      <div class="wo-modal">
        <div class="wo-header">
          <h2>작업 지시 등록</h2>
          <div class="wo-actions">
            <button class="btn-wo-save" @click="handleWoSave">💾 저장</button>
            <button class="btn-wo-close" @click="showWoModal=false">❌ 닫기</button>
          </div>
        </div>

        <!-- 작업지시 정보 폼 -->
        <fieldset class="wo-fieldset">
          <legend>작업 지시 정보</legend>
          <div class="wo-form">
            <div class="form-field">
              <label>작업 지시 번호</label>
              <input type="text" readonly placeholder="자동채번" />
            </div>
            <div class="form-field">
              <label>사업장</label>
              <select v-model="woForm.PLANTCD">
                <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
              </select>
            </div>
            <div class="form-field">
              <label>작업지시일</label>
              <input type="date" v-model="woForm.ORDDATE" />
              <div class="chk-row">
                <label><input type="checkbox" v-model="woForm.SAT" /> 토요일</label>
                <label><input type="checkbox" v-model="woForm.SUN" /> 일요일</label>
              </div>
            </div>
            <div class="form-field">
              <label>작지구분</label>
              <select v-model="woForm.ORDTYPE">
                <option value="일반">일반</option>
                <option value="긴급">긴급</option>
                <option value="재작업">재작업</option>
              </select>
            </div>
            <div class="form-field">
              <label>근무조</label>
              <select v-model="woForm.SHIFT">
                <option value="주간">주간</option>
                <option value="야간">야간</option>
              </select>
            </div>
            <div class="form-field">
              <label>우선순위</label>
              <input type="number" v-model.number="woForm.ORDpriority" />
            </div>
          </div>
        </fieldset>

        <!-- 품목 목록 -->
        <div class="wo-grid-header">
          <span>출력 품목 (선택한 생산계획 품목)</span>
          <span class="wo-count">{{ woItems.length }}건</span>
        </div>
        <div class="wo-grid-wrap">
          <table class="wo-grid">
            <thead>
              <tr>
                <th style="width:32px">선택</th>
                <th style="width:90px">작업일자</th>
                <th style="width:120px">품번</th>
                <th style="width:140px">품명</th>
                <th style="width:80px">규격</th>
                <th style="width:80px">공정</th>
                <th style="width:80px">라인</th>
                <th style="width:60px">근무조</th>
                <th style="width:80px">지시수량</th>
                <th style="width:60px">상태</th>
                <th style="width:70px">재고수량</th>
                <th style="width:70px">소요량</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="woItems.length===0">
                <td colspan="12" class="empty">생산계획에서 품목을 선택한 후 이 모달을 열어주세요.</td>
              </tr>
              <tr v-for="(item, i) in woItems" :key="i" :class="{'row-selected': item._sel}">
                <td class="chk"><input type="checkbox" v-model="item._sel" /></td>
                <td>{{ item.ORDDATE }}</td>
                <td>{{ item.PARTNO }}</td>
                <td>{{ item.PARTNM }}</td>
                <td>{{ item.STANDARD }}</td>
                <td>
                  <select v-model="item.PROCESSCD" class="cell-select">
                    <option value="">선택</option>
                    <option v-for="pr in processes" :key="pr.PROCESSCD" :value="pr.PROCESSCD">{{ pr.PROCESSNM }}</option>
                  </select>
                </td>
                <td>
                  <select v-model="item.LINECD" class="cell-select">
                    <option value="">선택</option>
                    <option v-for="ln in lines" :key="ln.LINECD" :value="ln.LINECD">{{ ln.LINENM }}</option>
                  </select>
                </td>
                <td>{{ item.SHIFT }}</td>
                <td><input type="number" class="cell-input-wo" v-model.number="item.ORDQTY" /></td>
                <td><span class="badge-new">신규</span></td>
                <td class="num">{{ item.STOCKQTY || 0 }}</td>
                <td class="num">{{ item.ORDQTY || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="wo-footer">
          <button class="btn-remove-items" @click="removeWoItems">🗑 선택 삭제</button>
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
  if (planData.value) planData.value.data.forEach((r: any) => r._checked = allChecked.value);
}

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}
async function fetchProcesses() {
  try { const r = await api.get('/api/master/process', { params: { size: 200 } }); processes.value = r.data.data || []; } catch {}
}
async function fetchLines() {
  try { const r = await api.get('/api/master/line', { params: { size: 200 } }); lines.value = r.data.data || []; } catch {}
}

async function fetchData() {
  try {
    const params: any = { base_date: baseDate.value };
    if (plantCd.value) params.plant_cd = plantCd.value;
    if (searchText.value) params.search = searchText.value;
    const r = await api.get('/api/production/plan', { params });
    // 각 행에 _checked 추가
    (r.data.data || []).forEach((row: any) => row._checked = false);
    planData.value = r.data;
  } catch {}
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
      PRODUCEDT: dt, PLANTCD: plantCd.value || plants.value[0]?.PLANTCD || '',
      PARTNO: row.PARTNO, ORDERNUM: row.ORDERNUM || '', ORDERSEQ: row.ORDERSEQ || 1, PRODUCEQTY: val
    });
  } catch {}
}

// ═══ 작업지시서 생성 모달 ═══
const showWoModal = ref(false);
const woForm = ref({
  PLANTCD: '', ORDDATE: f(now), ORDTYPE: '일반', SHIFT: '주간',
  ORDpriority: 1, SAT: false, SUN: false
});
const woItems = ref<any[]>([]);

function openWoModal() {
  if (!planData.value) return;
  const checked = planData.value.data.filter((r: any) => r._checked);
  if (checked.length === 0) { alert('생산계획에서 품목을 선택해 주세요.'); return; }

  woForm.value = {
    PLANTCD: plantCd.value || (plants.value.length ? plants.value[0].PLANTCD : ''),
    ORDDATE: f(now), ORDTYPE: '일반', SHIFT: '주간', ORDpriority: 1, SAT: false, SUN: false
  };

  // 선택된 품목을 작업지시 품목으로 변환
  woItems.value = checked.map((row: any) => ({
    PARTNO: row.PARTNO, PARTNM: row.PARTNM, STANDARD: row.STANDARD,
    UNIT: row.UNIT, ORDDATE: f(now), PROCESSCD: '', LINECD: '',
    SHIFT: '주간', ORDQTY: row.TOTAL || 0, STOCKQTY: row.STOCKQTY || 0,
    _sel: true
  }));
  showWoModal.value = true;
}

function removeWoItems() {
  woItems.value = woItems.value.filter(r => !r._sel);
}

async function handleWoSave() {
  if (woItems.value.length === 0) { alert('저장할 품목이 없습니다.'); return; }
  if (!confirm(`${woItems.value.length}건의 작업지시를 등록하시겠습니까?`)) return;

  let saved = 0;
  try {
    for (const item of woItems.value) {
      await api.post('/api/production/workorder', {
        PLANTCD: woForm.value.PLANTCD,
        PARTNO: item.PARTNO,
        ORDDATE: item.ORDDATE || woForm.value.ORDDATE,
        ORDQTY: item.ORDQTY,
        PROCESSCD: item.PROCESSCD || null,
        LINECD: item.LINECD || null,
        SHIFT: item.SHIFT || woForm.value.SHIFT,
        ORDTYPE: woForm.value.ORDTYPE,
        ORDpriority: woForm.value.ORDpriority,
      });
      saved++;
    }
    alert(`${saved}건의 작업지시가 등록되었습니다.`);
    showWoModal.value = false;
  } catch (e: any) {
    alert(`${saved}건 저장 후 오류 발생: ${e.message || '알 수 없는 오류'}`);
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

/* 달력 그리드 */
.plan-grid-wrap{flex:1;overflow:auto;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.plan-grid{width:100%;border-collapse:collapse;font-size:.82rem}
.plan-grid thead{position:sticky;top:0;z-index:5}
.day-num-row th{background:linear-gradient(180deg,#d6eaf8,#aed6f1);color:#1a5276;font-weight:700;padding:8px 4px;text-align:center;border-bottom:1px solid #85c1e9;white-space:nowrap}
.day-label-row th{background:#eaf2f8;color:#5d6d7e;font-size:.75rem;font-weight:600;padding:4px;text-align:center;border-bottom:2px solid #85c1e9}
.plan-grid td{padding:2px 3px;border-bottom:1px solid #f0f2f5;text-align:center}
.freeze{position:sticky;background:#fff;z-index:3}
.chk-col{width:32px;min-width:32px;text-align:center}
.freeze:nth-child(1){left:0}.freeze:nth-child(2){left:32px}.freeze:nth-child(3){left:132px}
.freeze:nth-child(4){left:232px}.freeze:nth-child(5){left:362px}.freeze:nth-child(6){left:432px}.freeze:nth-child(7){left:492px}
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
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.wo-modal{background:#fff;border-radius:12px;width:1100px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.wo-header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:linear-gradient(135deg,#1a5276,#2980b9);color:#fff}
.wo-header h2{margin:0;font-size:1.15rem;font-weight:700}
.wo-actions{display:flex;gap:8px}
.btn-wo-save{background:#27ae60;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-wo-save:hover{background:#219a52}
.btn-wo-close{background:#c0392b;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 폼 */
.wo-fieldset{margin:14px 24px 0;padding:14px 18px;border:1px solid #d6eaf8;border-radius:8px}
.wo-fieldset legend{color:#1a5276;font-weight:700;font-size:.9rem;padding:0 8px}
.wo-form{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px 24px}
.form-field{display:flex;flex-direction:column;gap:5px}
.form-field label{font-size:.82rem;font-weight:600;color:#64748b}
.form-field input,.form-field select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem}
.form-field input:focus,.form-field select:focus{border-color:#2980b9;outline:none;box-shadow:0 0 0 3px rgba(41,128,185,.1)}
.form-field input[readonly]{background:#f1f5f9;color:#64748b}
.chk-row{display:flex;gap:14px;margin-top:4px}
.chk-row label{font-size:.82rem;display:flex;align-items:center;gap:4px;color:#636e72;font-weight:500}

/* 품목 그리드 */
.wo-grid-header{display:flex;justify-content:space-between;align-items:center;padding:10px 24px;background:#eaf2f8;border-bottom:1px solid #d6eaf8;margin-top:10px}
.wo-grid-header span{font-size:.88rem;font-weight:700;color:#1a5276}
.wo-count{color:#2980b9;font-weight:600}
.wo-grid-wrap{flex:1;overflow:auto;min-height:180px;max-height:400px}
.wo-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.wo-grid thead{position:sticky;top:0;z-index:2}
.wo-grid th{background:linear-gradient(180deg,#d6eaf8,#aed6f1);color:#1a5276;font-weight:600;padding:9px 6px;text-align:left;border-bottom:2px solid #85c1e9;white-space:nowrap;font-size:.82rem}
.wo-grid td{padding:5px 6px;border-bottom:1px solid #f0f2f5}
.wo-grid .chk{text-align:center}
.wo-grid .empty{text-align:center;color:#b2bec3;padding:50px 16px!important;font-size:.9rem}
.cell-input-wo{width:72px;padding:5px 6px;border:1px solid #e2e8f0;border-radius:5px;font-size:.83rem;text-align:right;background:#fff}
.cell-input-wo:focus{border-color:#2980b9;outline:none}
.cell-select{width:80px;padding:4px;border:1px solid #e2e8f0;border-radius:5px;font-size:.82rem;background:#fff}
.badge-new{display:inline-block;padding:2px 8px;background:#27ae60;color:#fff;border-radius:10px;font-size:.75rem;font-weight:600}
.wo-footer{display:flex;justify-content:flex-end;padding:10px 24px 16px;gap:8px}
.btn-remove-items{background:#e74c3c;color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
</style>
