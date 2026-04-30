<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">수주 현황</div>
      <div class="search-row">
        <label>수주일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>고객사</label>
        <input type="text" v-model="searchText" placeholder="고객사명" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-add" @click="openRegister">＋ 수주등록</button>
          <button class="btn-del" @click="()=>window.alert('삭제이력')">삭제이력</button>
          <button class="btn-excel">엑셀등록</button>
        </div>
      </div>
    </section>
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si" :page="pg" :totalPages="tp" :total="tot" @row-click="onMaster" @page-change="onPg" />
      <div class="detail-wrap">
        <div class="dh">수주 상세 <span v-if="sel">- No.{{ sel.ORDERNO }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>

    <!-- ═══ 수주등록 모달 ═══ -->
    <div v-if="showReg" class="modal-overlay" @click.self="showReg=false">
      <div class="reg-modal">
        <!-- 타이틀바 -->
        <div class="reg-header">
          <h2>수주 등록</h2>
          <div class="reg-actions">
            <button class="btn-save" @click="handleSave"><span>💾</span> 저장</button>
            <button class="btn-remove" @click="handleRegDelete" v-if="regEdit"><span>✂️</span> 삭제</button>
            <button class="btn-close" @click="showReg=false"><span>❌</span> 닫기</button>
          </div>
        </div>
        <!-- 폼 영역 -->
        <div class="reg-form">
          <div class="form-field">
            <label class="required">사업장</label>
            <div class="input-with-btn">
              <input type="text" v-model="regForm.PLANTNM" readonly placeholder="사업장 선택" />
              <button class="btn-search-sm" @click="openPlantPicker" title="검색">🔍</button>
            </div>
          </div>
          <div class="form-field">
            <label class="required">납기요청일</label>
            <input type="date" v-model="regForm.ADOFREQDT" />
          </div>
          <div class="form-field">
            <label class="required">고객사</label>
            <div class="input-with-btn">
              <input type="text" v-model="regForm.COMPANYNM" readonly placeholder="고객사 선택" />
              <button class="btn-search-sm" @click="openCompanyPicker" title="검색">🔍</button>
            </div>
          </div>
          <div class="form-field">
            <label>비고</label>
            <input type="text" v-model="regForm.REMARK" placeholder="비고" />
          </div>
        </div>
        <!-- 품목 그리드 -->
        <div class="reg-grid-header">
          <span>수주 품목</span>
          <div class="grid-btns">
            <button class="btn-row-add" @click="addRow">📥 추가</button>
            <button class="btn-row-del" @click="removeRows">✂️ 제거</button>
          </div>
        </div>
        <div class="reg-grid-wrap">
          <table class="reg-grid">
            <thead>
              <tr>
                <th style="width:32px"><input type="checkbox" v-model="allChecked" @change="toggleAll" /></th>
                <th style="width:130px" class="req-th">제품품번</th>
                <th style="width:140px">품명</th>
                <th style="width:90px">규격</th>
                <th style="width:100px">납기요청일</th>
                <th style="width:60px">단위</th>
                <th style="width:90px">단가</th>
                <th style="width:80px">재고수량</th>
                <th style="width:80px" class="req-th">수량</th>
                <th style="min-width:100px">비고</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="regItems.length === 0">
                <td colspan="10" class="empty">품목을 추가하세요.</td>
              </tr>
              <tr v-for="(item, i) in regItems" :key="i">
                <td class="chk"><input type="checkbox" v-model="item._checked" /></td>
                <td>
                  <div class="cell-input-with-btn">
                    <input type="text" v-model="item.PARTNO" class="cell-input" placeholder="품번 입력" @blur="onPartBlur(item)" />
                    <button class="btn-cell-search" @click="openGoodsPicker(i)">🔍</button>
                  </div>
                </td>
                <td><input type="text" v-model="item.PARTNM" class="cell-input" readonly /></td>
                <td><input type="text" v-model="item.STANDARD" class="cell-input" readonly /></td>
                <td><input type="date" v-model="item.ADOFREQDT" class="cell-input" /></td>
                <td><input type="text" v-model="item.UNIT" class="cell-input" readonly /></td>
                <td><input type="number" v-model.number="item.UNIT_PRICE" class="cell-input num" /></td>
                <td class="num readonly">{{ item.STOCKQTY || 0 }}</td>
                <td><input type="number" v-model.number="item.REQQTY" class="cell-input num" /></td>
                <td><input type="text" v-model="item.REMARK" class="cell-input" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ 사업장 선택 팝업 ═══ -->
    <div v-if="showPlantPicker" class="modal-overlay" @click.self="showPlantPicker=false">
      <div class="picker-modal">
        <div class="picker-header">
          <h3>사업장 선택</h3>
          <button class="btn-close-sm" @click="showPlantPicker=false">✕</button>
        </div>
        <div class="picker-search">
          <input type="text" v-model="plantPickerSearch" placeholder="사업장명 검색" @keyup.enter="fetchPlantsForPicker" />
          <button class="btn-search" @click="fetchPlantsForPicker">조회</button>
        </div>
        <div class="picker-list">
          <table class="picker-tbl">
            <thead><tr><th>코드</th><th>사업장명</th><th>대표자</th></tr></thead>
            <tbody>
              <tr v-for="p in pickerPlants" :key="p.PLANTCD" @click="selectPlant(p)" class="clickable">
                <td>{{ p.PLANTCD }}</td><td>{{ p.PLANTNM }}</td><td>{{ p.BOSSNM }}</td>
              </tr>
              <tr v-if="pickerPlants.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ 고객사 선택 팝업 ═══ -->
    <div v-if="showCompanyPicker" class="modal-overlay" @click.self="showCompanyPicker=false">
      <div class="picker-modal">
        <div class="picker-header">
          <h3>고객사 선택</h3>
          <button class="btn-close-sm" @click="showCompanyPicker=false">✕</button>
        </div>
        <div class="picker-search">
          <input type="text" v-model="companySearch" placeholder="고객사명 검색" @keyup.enter="fetchCompanies" />
          <button class="btn-search" @click="fetchCompanies">조회</button>
        </div>
        <div class="picker-list">
          <table class="picker-tbl">
            <thead><tr><th>코드</th><th>고객사명</th><th>사업자번호</th></tr></thead>
            <tbody>
              <tr v-for="c in companies" :key="c.COMPANYCD" @click="selectCompany(c)" class="clickable">
                <td>{{ c.COMPANYCD }}</td><td>{{ c.COMPANYNM }}</td><td>{{ c.BSNO }}</td>
              </tr>
              <tr v-if="companies.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ 품목 선택 팝업 ═══ -->
    <div v-if="showGoodsPicker" class="modal-overlay" @click.self="showGoodsPicker=false">
      <div class="picker-modal">
        <div class="picker-header">
          <h3>품목 선택</h3>
          <button class="btn-close-sm" @click="showGoodsPicker=false">✕</button>
        </div>
        <div class="picker-search">
          <input type="text" v-model="goodsSearch" placeholder="품번 또는 품명 검색" @keyup.enter="fetchGoods" />
          <button class="btn-search" @click="fetchGoods">조회</button>
        </div>
        <div class="picker-list">
          <table class="picker-tbl">
            <thead><tr><th>품번</th><th>품명</th><th>규격</th><th>단위</th></tr></thead>
            <tbody>
              <tr v-for="g in goods" :key="g.PARTNO" @click="selectGoods(g)" class="clickable">
                <td>{{ g.PARTNO }}</td><td>{{ g.PARTNM }}</td><td>{{ g.STANDARD }}</td><td>{{ g.UNIT }}</td>
              </tr>
              <tr v-if="goods.length===0"><td colspan="4" class="empty">결과 없음</td></tr>
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

const d = new Date(), m = new Date(d); m.setMonth(m.getMonth() - 1);
const f = (v: Date) => v.toISOString().slice(0, 10);

// ── 현황 조회 ──
const startDate = ref(f(m)), endDate = ref(f(d)), plantCd = ref(''), searchText = ref(''), plants = ref<any[]>([]);
const mCols = [
  { key: 'ORDERNO', label: '수주번호', width: '90px' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '고객사', width: '140px' },
  { key: 'ORDERDT', label: '수주일자', width: '110px', type: 'date' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '110px', type: 'date' },
  { key: 'TOTALAMT', label: '총금액', width: '120px' },
  { key: 'ORDERSTATE', label: '상태', width: '80px' },
];
const dCols = [
  { key: 'PARTNO', label: '제품품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '90px' },
  { key: 'UNIT', label: '단위', width: '60px' },
  { key: 'UNIT_PRICE', label: '단가', width: '90px' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '100px', type: 'date' },
  { key: 'REQQTY', label: '수주수량', width: '90px' },
  { key: 'AMT', label: '금액', width: '100px' },
  { key: 'REMARK', label: '비고', minWidth: '100px' },
];
const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const ld = ref(false), dl = ref(false), si = ref(-1), sel = ref<any>(null);
const pg = ref(1), tp = ref(0), tot = ref(0);

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}
async function fetchData() {
  ld.value = true; si.value = -1; sel.value = null; dRows.value = [];
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    const r = await api.get('/api/order/list', { params: p });
    mRows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    tot.value = (r.data?.data?.total ?? r.data?.total ?? 0); tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { ld.value = false; }
}
async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try { const r = await api.get(`/api/order/detail/${row.ORDERNO}/items`); dRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []); }
  finally { dl.value = false; }
}
function onPg(p: number) { pg.value = p; fetchData(); }

// ── 수주등록 모달 ──
const showReg = ref(false), regEdit = ref(false);
const regForm = ref({ PLANTCD: '', PLANTNM: '', COMPANYCD: '', COMPANYNM: '', ADOFREQDT: f(d), REMARK: '' });
const regItems = ref<any[]>([]);
const allChecked = ref(false);

function emptyRow() {
  return { _checked: false, PARTNO: '', PARTNM: '', STANDARD: '', ADOFREQDT: regForm.value.ADOFREQDT, UNIT: '', UNIT_PRICE: 0, STOCKQTY: 0, REQQTY: 0, REMARK: '' };
}

function openRegister() {
  regEdit.value = false;
  const defPlant = plants.value.length ? plants.value[0] : { PLANTCD: '', PLANTNM: '' };
  regForm.value = { 
    PLANTCD: defPlant.PLANTCD, 
    PLANTNM: defPlant.PLANTNM,
    COMPANYCD: '', 
    COMPANYNM: '', 
    ADOFREQDT: f(d), 
    REMARK: '' 
  };
  regItems.value = [emptyRow()];
  allChecked.value = false;
  showReg.value = true;
}

function addRow() { regItems.value.push(emptyRow()); }
function removeRows() {
  regItems.value = regItems.value.filter(r => !r._checked);
  allChecked.value = false;
}
function toggleAll() { regItems.value.forEach(r => r._checked = allChecked.value); }

async function onPartBlur(item: any) {
  if (!item.PARTNO) return;
  try {
    const r = await api.get('/api/master/goods', { params: { search: item.PARTNO, size: 1 } });
    const rows = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    if (rows.length > 0) {
      const g = rows[0];
      item.PARTNM = g.PARTNM || '';
      item.STANDARD = g.STANDARD || '';
      item.UNIT = g.UNIT || '';
      item.UNIT_PRICE = g.UNIT_PRICE || 0;
    }
  } catch {}
}

async function handleSave() {
  if (!regForm.value.COMPANYCD) { alert('고객사를 선택하세요.'); return; }
  if (!regForm.value.PLANTCD) { alert('사업장을 선택하세요.'); return; }
  
  const validItems = regItems.value.filter(r => r.PARTNO || r.REQQTY);
  if (validItems.length === 0) { alert('품목을 1건 이상 입력하세요.'); return; }
  
  for (const item of validItems) {
    if (!item.PARTNO) { alert('제품품번을 입력하세요.'); return; }
    if (!item.REQQTY || item.REQQTY <= 0) { alert('수량을 입력하세요.'); return; }
  }

  try {
    const body = {
      PLANTCD: regForm.value.PLANTCD,
      COMPANYCD: regForm.value.COMPANYCD,
      ADOFREQDT: regForm.value.ADOFREQDT,
      ORDERDT: f(new Date()),
      ORDERSTATE: 'NEW',
      REMARK: regForm.value.REMARK,
      details: validItems.map(r => ({
        PARTNO: r.PARTNO, ADOFREQDT: r.ADOFREQDT || regForm.value.ADOFREQDT,
        REQQTY: r.REQQTY, UNIT_PRICE: r.UNIT_PRICE, REMARK: r.REMARK
      }))
    };
    await api.post('/api/order/create', body);
    alert('수주가 등록되었습니다.');
    showReg.value = false;
    fetchData();
  } catch {}
}
function handleRegDelete() { alert('삭제 기능'); }

// ── 사업장 선택 ──
const showPlantPicker = ref(false), plantPickerSearch = ref(''), pickerPlants = ref<any[]>([]);
function openPlantPicker() {
  plantPickerSearch.value = '';
  showPlantPicker.value = true;
  fetchPlantsForPicker();
}
async function fetchPlantsForPicker() {
  try {
    const r = await api.get('/api/master/plant', { params: { search: plantPickerSearch.value, size: 50 } });
    pickerPlants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch {}
}
function selectPlant(p: any) {
  if (regForm.value.PLANTCD !== p.PLANTCD) {
    regForm.value.COMPANYCD = '';
    regForm.value.COMPANYNM = '';
  }
  regForm.value.PLANTCD = p.PLANTCD;
  regForm.value.PLANTNM = p.PLANTNM;
  showPlantPicker.value = false;
}

// ── 고객사 선택 ──
const showCompanyPicker = ref(false), companySearch = ref(''), companies = ref<any[]>([]);
function openCompanyPicker() {
  if (!regForm.value.PLANTCD) {
    alert('사업장을 먼저 선택하세요.');
    return;
  }
  companySearch.value = '';
  showCompanyPicker.value = true;
  fetchCompanies();
}
async function fetchCompanies() {
  try {
    const params: any = { search: companySearch.value, is_customer: 1, size: 50 };
    if (regForm.value.PLANTCD) {
      params.plant_cd = regForm.value.PLANTCD;
    }
    const r = await api.get('/api/master/company', { params });
    companies.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch {}
}
function selectCompany(c: any) {
  regForm.value.COMPANYCD = c.COMPANYCD;
  regForm.value.COMPANYNM = c.COMPANYNM;
  showCompanyPicker.value = false;
}

// ── 품목 선택 ──
const showGoodsPicker = ref(false), goodsSearch = ref(''), goods = ref<any[]>([]), pickingIdx = ref(-1);
function openGoodsPicker(idx: number) {
  pickingIdx.value = idx;
  goodsSearch.value = regItems.value[idx].PARTNO || '';
  goods.value = [];
  showGoodsPicker.value = true;
  if (goodsSearch.value) fetchGoods();
}
async function fetchGoods() {
  try {
    const r = await api.get('/api/master/goods', { params: { search: goodsSearch.value, parttype: 'PARTGUBUN001', size: 50 } });
    goods.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch {}
}
function selectGoods(g: any) {
  if (pickingIdx.value > -1) {
    const item = regItems.value[pickingIdx.value];
    item.PARTNO = g.PARTNO;
    item.PARTNM = g.PARTNM;
    item.STANDARD = g.STANDARD;
    item.UNIT = g.UNIT;
    item.UNIT_PRICE = g.UNIT_PRICE || 0;
  }
  showGoodsPicker.value = false;
}

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
/* 페이지 레이아웃 */
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:150px}.search-row select{min-width:130px}
.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-del{background:#e74c3c;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-excel{background:#27ae60;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}.dh span{color:#667eea}

/* ═══ 수주등록 모달 ═══ */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.reg-modal{background:#fff;border-radius:12px;width:960px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.reg-header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:linear-gradient(135deg,#2c5f2d,#4a8c3f);color:#fff}
.reg-header h2{margin:0;font-size:1.15rem;font-weight:700}
.reg-actions{display:flex;gap:8px}
.btn-save{background:#2980b9;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:4px}
.btn-save:hover{background:#2471a3}
.btn-remove{background:#e67e22;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:4px}
.btn-close{background:#c0392b;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:4px}
.btn-close:hover{background:#a93226}

/* 폼 영역 */
.reg-form{display:grid;grid-template-columns:1fr 1fr;gap:14px 24px;padding:18px 24px;background:#fafbfc;border-bottom:1px solid #eee}
.form-field{display:flex;flex-direction:column;gap:5px}
.form-field label{font-size:.82rem;font-weight:600;color:#64748b}
.form-field label.required::before{content:'◎ ';color:#27ae60}
.form-field input,.form-field select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}
.form-field input:focus,.form-field select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}
.form-field input[readonly]{background:#f1f5f9;color:#64748b}
.input-with-btn{display:flex;gap:4px}
.input-with-btn input{flex:1}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 12px;border-radius:8px;cursor:pointer;font-size:1rem}

/* 품목 그리드 */
.reg-grid-header{display:flex;justify-content:space-between;align-items:center;padding:12px 24px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.reg-grid-header span{font-size:.88rem;font-weight:700;color:#3a4a6b}
.grid-btns{display:flex;gap:6px}
.btn-row-add{background:#27ae60;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}
.btn-row-del{background:#e74c3c;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}
.reg-grid-wrap{flex:1;overflow:auto;min-height:200px;max-height:380px}
.reg-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.reg-grid thead{position:sticky;top:0;z-index:2}
.reg-grid th{background:linear-gradient(180deg,#e8f5e9,#c8e6c9);color:#2e7d32;font-weight:600;padding:9px 8px;text-align:left;border-bottom:2px solid #a5d6a7;white-space:nowrap;font-size:.82rem}
.reg-grid th.req-th::before{content:'* ';color:#e74c3c}
.reg-grid td{padding:4px 4px;border-bottom:1px solid #f0f2f5}
.reg-grid .chk{text-align:center}
.reg-grid .empty{text-align:center;color:#b2bec3;padding:50px 16px!important;font-size:.9rem}
.cell-input{width:100%;padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:.83rem;background:#fff;transition:border-color .12s}
.cell-input:focus{border-color:#27ae60;outline:none}
.cell-input[readonly]{background:#f8fafc;color:#94a3b8;border-color:#f0f2f5}
.num{text-align:right}.readonly{padding:6px 8px;color:#636e72;font-size:.83rem}
.cell-input-with-btn{display:flex;gap:2px}
.cell-input-with-btn input{flex:1}
.btn-cell-search{background:#636e72;color:#fff;border:none;padding:0 6px;border-radius:4px;cursor:pointer;font-size:.8rem}

/* 고객사 선택 팝업 */
.picker-modal{background:#fff;border-radius:12px;width:520px;max-height:70vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#f0f4ff;border-bottom:1px solid #d0d7e8}
.picker-header h3{margin:0;font-size:1rem;font-weight:700;color:#3a4a6b}
.btn-close-sm{background:none;border:none;font-size:1.1rem;cursor:pointer;color:#636e72}
.picker-search{display:flex;gap:8px;padding:12px 20px}
.picker-search input{flex:1;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.88rem}
.picker-list{flex:1;overflow:auto;padding:0 20px 16px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{background:#f8f9fa;padding:8px 10px;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#e8f5e9}
</style>
