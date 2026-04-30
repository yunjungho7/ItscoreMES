<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">작업 지시</div>
      <div class="search-row">
        <label>작업일시</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchData" />
        <label>근무조</label>
        <select v-model="shift">
          <option value="">(선택하세요)</option>
          <option value="주간">주간</option>
          <option value="야간">야간</option>
        </select>
        <label>작지상태</label>
        <select v-model="ordState">
          <option value="">(선택하세요)</option>
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
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onMaster" @page-change="onPg" />
      <div class="detail-wrap">
        <div class="dh">하위 작업지시 <span v-if="sel">- {{ sel.WORKORDNO }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>

    <!-- ═══ 작업지시 등록 모달 ═══ -->
    <div v-if="showReg" class="modal-overlay" @click.self="showReg=false">
      <div class="reg-modal">
        <div class="reg-header">
          <h2>작업 지시 등록</h2>
          <div class="reg-actions">
            <button class="btn-save" @click="handleSave">💾 저장</button>
            <button class="btn-del2" @click="handleRegDelete">🗑 삭제</button>
            <button class="btn-close" @click="showReg=false">❌ 닫기</button>
          </div>
        </div>
        <div class="reg-body">
          <fieldset class="reg-fieldset">
            <legend>작업 지시 정보</legend>
            <div class="reg-form-grid">
              <div class="form-field full-width">
                <label>작업 지시 번호</label>
                <input type="text" v-model="regForm.WORKORDNO" readonly placeholder="자동채번" />
              </div>
              <div class="form-field">
                <label>품번/품명</label>
                <div class="input-with-btn">
                  <input type="text" v-model="regForm.PARTNO" placeholder="품번" @blur="fetchPartInfo" />
                  <span class="part-name">{{ regForm.PARTNM }}</span>
                  <button class="btn-search-sm" @click="showItemPicker=true">🔍</button>
                </div>
              </div>
              <div class="form-field">
                <label>사업장</label>
                <select v-model="regForm.PLANTCD">
                  <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
                </select>
              </div>
              <div class="form-field">
                <label>작업지시일</label>
                <input type="date" v-model="regForm.ORDDATE" />
              </div>
              <div class="form-field">
                <label>작지구분</label>
                <select v-model="regForm.ORDTYPE">
                  <option value="일반">일반</option>
                  <option value="긴급">긴급</option>
                  <option value="재작업">재작업</option>
                </select>
              </div>
              <div class="form-field">
                <label>근무조</label>
                <select v-model="regForm.SHIFT">
                  <option value="주간">주간</option>
                  <option value="야간">야간</option>
                </select>
              </div>
              <div class="form-field">
                <label>단위</label>
                <input type="text" v-model="regForm.UNIT" readonly />
              </div>
              <div class="form-field">
                <label>지시 수량</label>
                <input type="number" v-model.number="regForm.ORDQTY" />
              </div>
              <div class="form-field">
                <label>우선순위</label>
                <input type="number" v-model.number="regForm.ORDpriority" />
              </div>
              <div class="form-field">
                <label>공정</label>
                <select v-model="regForm.PROCESSCD">
                  <option value="">선택</option>
                  <option v-for="pr in processes" :key="pr.PROCESSCD" :value="pr.PROCESSCD">{{ pr.PROCESSNM }}</option>
                </select>
              </div>
              <div class="form-field">
                <label>라인</label>
                <select v-model="regForm.LINECD">
                  <option value="">선택</option>
                  <option v-for="ln in lines" :key="ln.LINECD" :value="ln.LINECD">{{ ln.LINENM }}</option>
                </select>
              </div>
              <div class="form-field">
                <label>비고</label>
                <input type="text" v-model="regForm.REMARK" />
              </div>
            </div>
          </fieldset>
          <!-- 등록 하단 그리드 (등록된 품목) -->
          <div class="reg-grid-header"><span>등록 품목</span></div>
          <div class="reg-grid-wrap">
            <table class="reg-grid">
              <thead>
                <tr>
                  <th style="width:30px">선택</th>
                  <th style="width:90px">작업일자</th>
                  <th style="width:110px">품번</th>
                  <th style="width:130px">품명</th>
                  <th style="width:80px">규격</th>
                  <th style="width:60px">공정</th>
                  <th style="width:70px">라인</th>
                  <th style="width:60px">근무조</th>
                  <th style="width:70px">지시수량</th>
                  <th style="width:60px">상태</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="regItems.length===0">
                  <td colspan="10" class="empty">등록 후 추가 버튼으로 품목을 추가하세요.</td>
                </tr>
                <tr v-for="(item, i) in regItems" :key="i" :class="{'row-selected': item._sel}">
                  <td class="chk"><input type="checkbox" v-model="item._sel" /></td>
                  <td>{{ item.ORDDATE }}</td>
                  <td>{{ item.PARTNO }}</td>
                  <td>{{ item.PARTNM }}</td>
                  <td>{{ item.STANDARD }}</td>
                  <td>{{ item.PROCESSCD }}</td>
                  <td>{{ item.LINECD }}</td>
                  <td>{{ item.SHIFT }}</td>
                  <td class="num">{{ item.ORDQTY }}</td>
                  <td>{{ item.ORDSTATE }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="reg-btns">
            <button class="btn-add-item" @click="addItem">📥 추가</button>
            <button class="btn-del-item" @click="removeItems">🗑 삭제</button>
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
const window = globalThis.window;
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

const d = new Date(), m7 = new Date(d); m7.setDate(m7.getDate() - 2);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m7)), endDate = ref(f(d)), plantCd = ref('');
const searchText = ref(''), shift = ref(''), ordState = ref('');
const plants = ref<any[]>([]), processes = ref<any[]>([]), lines = ref<any[]>([]);

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

async function fetchPartInfo() {
  if (!regForm.value.PARTNO) return;
  try {
    const r = await api.get('/api/master/goods', { params: { search: regForm.value.PARTNO, size: 1 } });
    const rows = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    if (rows.length > 0) {
      const g = rows[0];
      regForm.value.PARTNM = g.PARTNM || '';
      regForm.value.UNIT = g.UNIT || '';
    }
  } catch {}
}

function addItem() {
  if (!regForm.value.PARTNO) { window.alert('품번을 입력하세요.'); return; }
  if (!regForm.value.ORDQTY || regForm.value.ORDQTY <= 0) { window.alert('지시수량을 입력하세요.'); return; }
  regItems.value.push({
    ORDDATE: regForm.value.ORDDATE, PARTNO: regForm.value.PARTNO,
    PARTNM: regForm.value.PARTNM, STANDARD: '', UNIT: regForm.value.UNIT,
    PROCESSCD: regForm.value.PROCESSCD, LINECD: regForm.value.LINECD,
    SHIFT: regForm.value.SHIFT, ORDQTY: regForm.value.ORDQTY,
    ORDSTATE: 'NEW', _sel: false
  });
}
function removeItems() {
  regItems.value = regItems.value.filter(r => !r._sel);
}

async function handleSave() {
  if (regItems.value.length === 0) { window.alert('추가 버튼으로 품목을 먼저 추가하세요.'); return; }
  let savedCount = 0;
  try {
    for (const item of regItems.value) {
      await api.post('/api/production/workorder', {
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
      });
      savedCount++;
    }
    window.alert(`${savedCount}건 작업지시가 등록되었습니다.`);
    showReg.value = false;
    fetchData();
  } catch {}
}

function handleRegDelete() {
  regItems.value = [];
}

// ── 품목 선택 ──
const showItemPicker = ref(false), itemSearch = ref(''), itemsList = ref<any[]>([]);
async function fetchItems() {
  try {
    const r = await api.get('/api/master/goods', { params: { search: itemSearch.value, size: 50 } });
    itemsList.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch {}
}
function selectItem(g: any) {
  regForm.value.PARTNO = g.PARTNO;
  regForm.value.PARTNM = g.PARTNM || '';
  regForm.value.UNIT = g.UNIT || '';
  showItemPicker.value = false;
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
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:110px}
.btn-search{background:#2980b9;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#2980b9,#1a5276);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#eaf2f8;font-size:.85rem;font-weight:600;color:#1a5276;border-bottom:1px solid #d6eaf8}.dh span{color:#2980b9}

/* 등록 모달 */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.reg-modal{background:#fff;border-radius:12px;width:1050px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.reg-header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:linear-gradient(135deg,#1a5276,#2980b9);color:#fff}
.reg-header h2{margin:0;font-size:1.15rem;font-weight:700}
.reg-actions{display:flex;gap:8px}
.btn-save{background:#27ae60;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-del2{background:#e74c3c;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-close{background:#c0392b;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.reg-body{flex:1;overflow:auto;display:flex;flex-direction:column}
.reg-fieldset{margin:16px 24px 0;padding:16px 20px;border:1px solid #d6eaf8;border-radius:8px}
.reg-fieldset legend{color:#1a5276;font-weight:700;font-size:.9rem;padding:0 8px}
.reg-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px 24px}
.form-field{display:flex;flex-direction:column;gap:5px}
.form-field.full-width{grid-column:1/3}
.form-field label{font-size:.82rem;font-weight:600;color:#64748b}
.form-field input,.form-field select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem}
.form-field input:focus,.form-field select:focus{border-color:#2980b9;outline:none;box-shadow:0 0 0 3px rgba(41,128,185,.1)}
.form-field input[readonly]{background:#f1f5f9;color:#64748b}
.input-with-btn{display:flex;gap:4px;align-items:center}
.input-with-btn input{flex:0 0 150px}
.part-name{font-size:.88rem;color:#636e72;flex:1}
.btn-search-sm{background:#2980b9;color:#fff;border:none;padding:6px 10px;border-radius:8px;cursor:pointer;font-size:.9rem}

/* 등록 그리드 */
.reg-grid-header{display:flex;align-items:center;padding:10px 24px;background:#eaf2f8;border-bottom:1px solid #d6eaf8;margin-top:8px}
.reg-grid-header span{font-size:.88rem;font-weight:700;color:#1a5276}
.reg-grid-wrap{flex:1;overflow:auto;min-height:130px;max-height:250px}
.reg-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.reg-grid thead{position:sticky;top:0;z-index:2}
.reg-grid th{background:linear-gradient(180deg,#d6eaf8,#aed6f1);color:#1a5276;font-weight:600;padding:9px 6px;text-align:left;border-bottom:2px solid #85c1e9;white-space:nowrap;font-size:.82rem}
.reg-grid td{padding:5px 6px;border-bottom:1px solid #f0f2f5}
.reg-grid .chk{text-align:center}
.reg-grid .empty{text-align:center;color:#b2bec3;padding:40px 16px!important}
.num{text-align:right}
.row-selected{background:#eaf2f8}
.reg-btns{display:flex;gap:8px;padding:8px 24px 16px;justify-content:flex-end}
.btn-add-item{background:#27ae60;color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-del-item{background:#e74c3c;color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}

/* 품목 선택 */
.picker-modal{background:#fff;border-radius:12px;width:560px;max-height:70vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#eaf2f8;border-bottom:1px solid #d6eaf8}
.picker-header h3{margin:0;font-size:1rem;font-weight:700;color:#1a5276}
.btn-close-sm{background:none;border:none;font-size:1.1rem;cursor:pointer;color:#636e72}
.picker-search{display:flex;gap:8px;padding:12px 20px}
.picker-search input{flex:1;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.88rem}
.picker-list{flex:1;overflow:auto;padding:0 20px 16px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{background:#f8f9fa;padding:8px 10px;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#eaf2f8}
</style>
