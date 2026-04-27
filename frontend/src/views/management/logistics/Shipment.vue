<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">출하지시 현황</div>
      <div class="search-row">
        <label>출하계획일</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>고객사</label>
        <input type="text" v-model="searchText" placeholder="고객사명" @keyup.enter="fetchData" />
        <label>수주번호</label>
        <input type="text" v-model="orderNo" placeholder="수주번호" style="width:100px" />
        <label><input type="checkbox" v-model="includeDone" /> 완료포함</label>
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-add" @click="openRegister">＋ 출하지시등록</button>
          <button class="btn-complete" @click="handleComplete" :disabled="!sel">출하완료</button>
          <button class="btn-del" @click="handleDelete">삭제이력</button>
        </div>
      </div>
    </section>

    <!-- ═══ 마스터-디테일 그리드 ═══ -->
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onMaster" @page-change="onPg" />
      <div class="detail-wrap">
        <div class="dh">출하 상세 <span v-if="sel">- {{ sel.SHIPMENTINDICATIONNO }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>

    <!-- ═══ 출하지시 등록 모달 ═══ -->
    <div v-if="showReg" class="modal-overlay" @click.self="showReg=false">
      <div class="reg-modal">
        <div class="reg-header">
          <h2>출하 지시 등록</h2>
          <div class="reg-actions">
            <button class="btn-row-add2" @click="fetchOrderItems">🔍 조회</button>
            <button class="btn-save" @click="handleSave">💾 저장</button>
            <button class="btn-close" @click="showReg=false">❌ 닫기</button>
          </div>
        </div>
        <!-- 폼 -->
        <div class="reg-form">
          <div class="form-field">
            <label class="required">고객사</label>
            <div class="input-with-btn">
              <input type="text" v-model="regForm.COMPANYNM" readonly placeholder="고객사 선택" />
              <button class="btn-search-sm" @click="showCompanyPicker=true">🔍</button>
            </div>
          </div>
          <div class="form-field">
            <label class="required">납기요청일</label>
            <div class="date-range">
              <input type="date" v-model="regForm.REQ_START" />
              <span>~</span>
              <input type="date" v-model="regForm.REQ_END" />
            </div>
          </div>
          <div class="form-field">
            <label class="required">사업장</label>
            <select v-model="regForm.PLANTCD">
              <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
            </select>
          </div>
          <div class="form-field">
            <label>출하지시일</label>
            <input type="date" v-model="regForm.SHIPMENTPLANDAY" />
          </div>
          <div class="form-field">
            <label>지시번호</label>
            <input type="text" v-model="regForm.SHIPMENTINDICATIONNO" readonly placeholder="자동채번" />
          </div>
          <div class="form-field">
            <label>비고</label>
            <input type="text" v-model="regForm.REMARK" placeholder="비고" />
          </div>
        </div>
        <!-- 품목 그리드 -->
        <div class="reg-grid-header">
          <span>수주 품목</span>
        </div>
        <div class="reg-grid-wrap">
          <table class="reg-grid">
            <thead>
              <tr>
                <th style="width:32px"><input type="checkbox" v-model="allChecked" @change="toggleAll" /></th>
                <th style="width:80px">수주번호</th>
                <th style="width:110px">제품품번</th>
                <th style="width:130px">품명</th>
                <th style="width:80px">규격</th>
                <th style="width:50px">단위</th>
                <th style="width:80px">단가</th>
                <th style="width:90px">납기요청일</th>
                <th style="width:70px">주문수량</th>
                <th style="width:80px">금액</th>
                <th style="width:80px">출하지시수량</th>
                <th style="width:80px">기출하지시</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="regItems.length===0">
                <td colspan="12" class="empty">조회 버튼을 눌러 수주 품목을 불러오세요.</td>
              </tr>
              <tr v-for="(item, i) in regItems" :key="i" :class="{'row-selected': item._checked}">
                <td class="chk"><input type="checkbox" v-model="item._checked" /></td>
                <td>{{ item.ORDERNO }}</td>
                <td>{{ item.PARTNO }}</td>
                <td>{{ item.PARTNM }}</td>
                <td>{{ item.STANDARD }}</td>
                <td>{{ item.UNIT }}</td>
                <td class="num">{{ item.UNIT_PRICE }}</td>
                <td>{{ item.ADOFREQDT }}</td>
                <td class="num">{{ item.ORDERQTY }}</td>
                <td class="num">{{ ((item.UNIT_PRICE||0) * (item.SHIPMENTINDICATIONQTY||0)).toLocaleString() }}</td>
                <td><input type="number" v-model.number="item.SHIPMENTINDICATIONQTY" class="cell-input num" /></td>
                <td class="num readonly">{{ item.PREV_SHIPQTY || 0 }}</td>
              </tr>
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
                <td>{{ c.COMPANYCD }}</td><td>{{ c.COMPANYNM }}</td><td>{{ c.BUSINESSNO }}</td>
              </tr>
              <tr v-if="companies.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
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

const d = new Date(), m = new Date(d); m.setDate(m.getDate() - 7);
const f = (v: Date) => v.toISOString().slice(0, 10);

// ── 현황 조회 ──
const startDate = ref(f(m)), endDate = ref(f(d)), plantCd = ref(''), searchText = ref('');
const orderNo = ref(''), includeDone = ref(false), plants = ref<any[]>([]);

const mCols = [
  { key: 'SHIPMENTINDICATIONNO', label: '출하지시번호', width: '130px' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '고객사', width: '140px' },
  { key: 'SHIPMENTPLANDAY', label: '출하계획일', width: '110px', type: 'date' },
  { key: 'SHIPMENTDAY', label: '출하일자', width: '110px', type: 'date' },
  { key: 'SHIPMENTGUBUN', label: '출하구분', width: '90px' },
  { key: 'SHIPMENTSTATUS', label: '상태', width: '80px' },
];
const dCols = [
  { key: 'ORDERNO', label: '수주번호', width: '80px' },
  { key: 'PARTNO', label: '제품품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'UNIT', label: '단위', width: '50px' },
  { key: 'UNIT_PRICE', label: '단가', width: '80px' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '100px', type: 'date' },
  { key: 'SHIPMENTINDICATIONQTY', label: '지시수량', width: '80px' },
  { key: 'SHIPMENTQTY', label: '출하수량', width: '80px' },
  { key: 'SHIPMENTSTATUS', label: '상태', width: '80px' },
  { key: 'REMARK', label: '비고', minWidth: '100px' },
];

const mRows = ref<any[]>([]), dRows = ref<any[]>([]);
const ld = ref(false), dl = ref(false), si = ref(-1), sel = ref<any>(null);
const pg = ref(1), tp = ref(0), tot = ref(0);

async function fetchPlants() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = r.data.data || []; } catch {}
}
async function fetchData() {
  ld.value = true; si.value = -1; sel.value = null; dRows.value = [];
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchText.value) p.search = searchText.value;
    if (orderNo.value) p.order_no = orderNo.value;
    if (includeDone.value) p.include_done = '1';
    const r = await api.get('/api/shipment/list', { params: p });
    mRows.value = r.data.data || [];
    tot.value = r.data.total; tp.value = r.data.totalPages;
  } finally { ld.value = false; }
}
async function onMaster(row: any, idx: number) {
  si.value = idx; sel.value = row; dl.value = true;
  try { const r = await api.get(`/api/shipment/detail/${row.SHIPMENTINDICATIONNO}/items`); dRows.value = r.data || []; }
  finally { dl.value = false; }
}
function onPg(p: number) { pg.value = p; fetchData(); }

async function handleComplete() {
  if (!sel.value) return;
  if (!confirm(`${sel.value.SHIPMENTINDICATIONNO} 출하완료 처리하시겠습니까?`)) return;
  try {
    await api.put(`/api/shipment/complete/${sel.value.SHIPMENTINDICATIONNO}`);
    alert('출하완료 처리되었습니다.');
    fetchData();
  } catch {}
}
function handleDelete() { alert('삭제이력 화면 준비중'); }

// ── 등록 모달 ──
const showReg = ref(false);
const regForm = ref({
  PLANTCD: '', COMPANYCD: '', COMPANYNM: '',
  REQ_START: f(d), REQ_END: f(new Date(d.getTime() + 86400000)),
  SHIPMENTPLANDAY: f(d), SHIPMENTINDICATIONNO: '', REMARK: ''
});
const regItems = ref<any[]>([]);
const allChecked = ref(false);

function openRegister() {
  regForm.value = {
    PLANTCD: plants.value.length ? plants.value[0].PLANTCD : '',
    COMPANYCD: '', COMPANYNM: '',
    REQ_START: f(d), REQ_END: f(new Date(d.getTime() + 86400000)),
    SHIPMENTPLANDAY: f(d), SHIPMENTINDICATIONNO: '', REMARK: ''
  };
  regItems.value = [];
  allChecked.value = false;
  showReg.value = true;
}

async function fetchOrderItems() {
  if (!regForm.value.COMPANYCD) { alert('고객사를 먼저 선택하세요.'); return; }
  try {
    const p: any = { company_cd: regForm.value.COMPANYCD };
    if (regForm.value.PLANTCD) p.plant_cd = regForm.value.PLANTCD;
    if (regForm.value.REQ_START) p.start_date = regForm.value.REQ_START;
    if (regForm.value.REQ_END) p.end_date = regForm.value.REQ_END;
    const r = await api.get('/api/shipment/order-items', { params: p });
    regItems.value = (r.data || []).map((row: any) => ({
      ...row, _checked: false, SHIPMENTINDICATIONQTY: (row.ORDERQTY || 0) - (row.PREV_SHIPQTY || 0)
    }));
  } catch {}
}

function toggleAll() { regItems.value.forEach(r => r._checked = allChecked.value); }

async function handleSave() {
  if (!regForm.value.COMPANYCD) { alert('고객사를 선택하세요.'); return; }
  const checked = regItems.value.filter(r => r._checked && r.SHIPMENTINDICATIONQTY > 0);
  if (checked.length === 0) { alert('출하지시할 품목을 선택하세요.'); return; }
  try {
    const body = {
      PLANTCD: regForm.value.PLANTCD,
      COMPANYCD: regForm.value.COMPANYCD,
      SHIPMENTPLANDAY: regForm.value.SHIPMENTPLANDAY,
      REMARK: regForm.value.REMARK,
      details: checked.map(r => ({
        PARTNO: r.PARTNO, ORDERNO: String(r.ORDERNO),
        SHIPMENTINDICATIONQTY: r.SHIPMENTINDICATIONQTY,
        ADOFREQDT: r.ADOFREQDT, UNIT_PRICE: r.UNIT_PRICE
      }))
    };
    const res = await api.post('/api/shipment/create', body);
    alert(`출하지시가 등록되었습니다.\n지시번호: ${res.data.SHIPMENTINDICATIONNO}`);
    showReg.value = false;
    fetchData();
  } catch {}
}

// ── 고객사 선택 ──
const showCompanyPicker = ref(false), companySearch = ref(''), companies = ref<any[]>([]);
async function fetchCompanies() {
  try {
    const r = await api.get('/api/master/company', { params: { search: companySearch.value, size: 50 } });
    companies.value = r.data.data || [];
  } catch {}
}
function selectCompany(c: any) {
  regForm.value.COMPANYCD = c.COMPANYCD;
  regForm.value.COMPANYNM = c.COMPANYNM;
  showCompanyPicker.value = false;
}

onMounted(() => { fetchPlants(); fetchData(); });
</script>

<style scoped>
/* 페이지 레이아웃 */
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#e67e22;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #fef0e3}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:130px}
.btn-search{background:#e67e22;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#e67e22,#d35400);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-complete{background:#27ae60;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-complete:disabled{opacity:.5;cursor:not-allowed}
.btn-del{background:#e74c3c;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.split-grids>*{flex:1;min-height:0}
.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.dh{padding:10px 16px;background:#fef9f3;font-size:.85rem;font-weight:600;color:#8b5e34;border-bottom:1px solid #f5e6d3}.dh span{color:#e67e22}

/* ═══ 등록 모달 ═══ */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.reg-modal{background:#fff;border-radius:12px;width:1050px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.reg-header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:linear-gradient(135deg,#d35400,#e67e22);color:#fff}
.reg-header h2{margin:0;font-size:1.15rem;font-weight:700}
.reg-actions{display:flex;gap:8px}
.btn-save{background:#2980b9;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-save:hover{background:#2471a3}
.btn-close{background:#c0392b;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.btn-close:hover{background:#a93226}
.btn-row-add2{background:#27ae60;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}

/* 폼 영역 */
.reg-form{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px 24px;padding:18px 24px;background:#fafbfc;border-bottom:1px solid #eee}
.form-field{display:flex;flex-direction:column;gap:5px}
.form-field label{font-size:.82rem;font-weight:600;color:#64748b}
.form-field label.required::before{content:'◎ ';color:#e67e22}
.form-field input,.form-field select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}
.form-field input:focus,.form-field select:focus{border-color:#e67e22;outline:none;box-shadow:0 0 0 3px rgba(230,126,34,.1)}
.form-field input[readonly]{background:#f1f5f9;color:#64748b}
.input-with-btn{display:flex;gap:4px}
.input-with-btn input{flex:1}
.btn-search-sm{background:#e67e22;color:#fff;border:none;padding:0 12px;border-radius:8px;cursor:pointer;font-size:1rem}
.date-range{display:flex;align-items:center;gap:6px}
.date-range input{flex:1}
.date-range span{color:#b2bec3;font-weight:600}

/* 품목 그리드 */
.reg-grid-header{display:flex;justify-content:space-between;align-items:center;padding:10px 24px;background:#fef9f3;border-bottom:1px solid #f5e6d3}
.reg-grid-header span{font-size:.88rem;font-weight:700;color:#8b5e34}
.reg-grid-wrap{flex:1;overflow:auto;min-height:200px;max-height:380px}
.reg-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.reg-grid thead{position:sticky;top:0;z-index:2}
.reg-grid th{background:linear-gradient(180deg,#fef0e3,#fde2c8);color:#8b5e34;font-weight:600;padding:9px 6px;text-align:left;border-bottom:2px solid #f5c896;white-space:nowrap;font-size:.82rem}
.reg-grid td{padding:5px 6px;border-bottom:1px solid #f0f2f5}
.reg-grid .chk{text-align:center}
.reg-grid .empty{text-align:center;color:#b2bec3;padding:50px 16px!important;font-size:.9rem}
.cell-input{width:100%;padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:.83rem;background:#fff;transition:border-color .12s}
.cell-input:focus{border-color:#e67e22;outline:none}
.num{text-align:right}.readonly{padding:6px 8px;color:#636e72;font-size:.83rem}
.row-selected{background:#fef9f3}

/* 고객사 선택 팝업 */
.picker-modal{background:#fff;border-radius:12px;width:520px;max-height:70vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#fef0e3;border-bottom:1px solid #f5c896}
.picker-header h3{margin:0;font-size:1rem;font-weight:700;color:#8b5e34}
.btn-close-sm{background:none;border:none;font-size:1.1rem;cursor:pointer;color:#636e72}
.picker-search{display:flex;gap:8px;padding:12px 20px}
.picker-search input{flex:1;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.88rem}
.picker-list{flex:1;overflow:auto;padding:0 20px 16px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{background:#f8f9fa;padding:8px 10px;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#fef9f3}
</style>
