<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">발주 현황 및 등록</div>
      <div class="search-row">
        <label>발주일자</label>
        <input type="date" v-model="startDate" />
        <span class="sep">~</span>
        <input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <input type="text" v-model="searchText" placeholder="품번 또는 품명" @keyup.enter="fetchOrders" />
        <label>공급사</label>
        <input type="text" v-model="companySearch" placeholder="공급사" @keyup.enter="fetchOrders" />
        <label class="checkbox-label">
          <input type="checkbox" v-model="includeCompleted" /> 완료포함
        </label>
        <div class="act-right">
          <button class="btn-search" @click="fetchOrders">조회</button>
          <button class="btn-success" @click="processReceiving">입고완료</button>
          <button class="btn-excel">엑셀등록</button>
          <button class="btn-print">발주서인쇄</button>
        </div>
      </div>
    </section>

    <!-- Master Grid (Purchase Orders) -->
    <div class="grid-area master-grid" style="flex: 1; min-height: 250px;">
      <DataGrid 
        :columns="masterCols" 
        :rows="orders" 
        :loading="loadingOrders" 
        @row-click="onOrderSelect"
        :selected-index="selectedOrderIdx"
      />
    </div>

    <!-- Detail Grid (Purchase Order Items) -->
    <div class="grid-area detail-grid" style="flex: 1; min-height: 200px; margin-top: 10px;">
      <div class="sub-title">발주 품목 상세 <span v-if="selectedOrderNum">[{{ selectedOrderNum }}]</span></div>
      <DataGrid 
        :columns="detailCols" 
        :rows="orderDetails" 
        :loading="loadingDetails" 
      />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';
import { useNotification } from '../../../composables/useNotification';

const { notifySuccess, notifyError } = useNotification();

const d = new Date();
const m14 = new Date(d); m14.setDate(m14.getDate() - 14);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m14));
const endDate = ref(f(d));
const plantCd = ref('');
const searchText = ref('');
const companySearch = ref('');
const includeCompleted = ref(false);
const plants = ref<any[]>([]);

const orders = ref<any[]>([]);
const orderDetails = ref<any[]>([]);
const loadingOrders = ref(false);
const loadingDetails = ref(false);
const selectedOrderIdx = ref(-1);
const selectedOrderNum = ref('');

// Master Grid Columns
const masterCols = [
  { key: 'ORDERNUM', label: '발주번호', width: '130px' },
  { key: 'PLANTNM', label: '사업장', width: '120px' },
  { key: 'COMPANYNM', label: '공급사', width: '150px' },
  { key: 'ORDERDT', label: '발주일자', width: '110px', type: 'date' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '110px', type: 'date' },
  { key: 'TOTALAMT', label: '총금액', width: '110px', type: 'number' },
  { key: 'ORDERSTATE', label: '상태', width: '90px' },
  { key: 'REGUSERNM', label: '등록자', width: '90px' },
  { key: 'REMARK', label: '비고', width: '150px' },
];

// Detail Grid Columns
const detailCols = [
  { key: 'PARTNO', label: '자재품번', width: '130px' },
  { key: 'PARTNM', label: '품명', width: '150px' },
  { key: 'STANDARD', label: '규격', width: '100px' },
  { key: 'UNIT', label: '단위', width: '60px' },
  { key: 'UNIT_PRICE', label: '단가', width: '90px', type: 'number' },
  { key: 'ORDERQTY', label: '발주수량', width: '90px', type: 'number' },
  { key: 'ADOFREQDT', label: '납기요청일', width: '110px', type: 'date' },
  { key: 'AMT', label: '금액', width: '100px', type: 'number' },
  { key: 'INQTY', label: '입고수량', width: '90px', type: 'number' },
  { key: 'STOCKQTY', label: '재고수량', width: '90px', type: 'number' },
  { key: 'REMARK', label: '비고', width: '150px' },
];

// --- API Fetching ---

async function fetchPlants() {
  try {
    const r = await api.get('/api/master/plant', { params: { size: 100 } });
    plants.value = r.data.data || [];
    if (plants.value.length > 0) plantCd.value = plants.value[0].PLANTCD;
  } catch (e) {
    console.error(e);
  }
}

async function fetchOrders() {
  loadingOrders.value = true;
  orderDetails.value = [];
  selectedOrderIdx.value = -1;
  selectedOrderNum.value = '';
  
  try {
    const params: any = {
      start_date: startDate.value,
      end_date: endDate.value,
      include_completed: includeCompleted.value
    };
    if (plantCd.value) params.plant_cd = plantCd.value;
    if (searchText.value) params.search = searchText.value;
    if (companySearch.value) params.company_cd = companySearch.value;

    const r = await api.get('/api/purchase/list', { params });
    let data = r.data || [];

    // 완료포함 체크가 해제되어 있으면 COMPLETED 상태 제외
    if (!includeCompleted.value) {
      data = data.filter((o: any) => o.ORDERSTATE !== 'COMPLETED');
    }

    orders.value = data;
  } catch (e) {
    notifyError('발주 목록 조회 중 오류가 발생했습니다.');
  } finally {
    loadingOrders.value = false;
  }
}

async function onOrderSelect(row: any, index: number) {
  selectedOrderIdx.value = index;
  selectedOrderNum.value = row.ORDERNUM;
  await fetchOrderDetails(row.ORDERNUM);
}

async function fetchOrderDetails(orderNum: string) {
  loadingDetails.value = true;
  try {
    const r = await api.get(`/api/purchase/detail/${orderNum}`);
    orderDetails.value = r.data || [];
  } catch (e) {
    notifyError('상세 품목 조회 중 오류가 발생했습니다.');
  } finally {
    loadingDetails.value = false;
  }
}

async function processReceiving() {
  if (selectedOrderIdx.value < 0 || !selectedOrderNum.value) {
    notifyError('입고 처리할 발주를 선택해주세요.');
    return;
  }
  
  const order = orders.value[selectedOrderIdx.value];
  if (order.ORDERSTATE === 'COMPLETED') {
    notifyError('이미 입고 완료된 발주입니다.');
    return;
  }

  // 상세 품목이 로드되지 않았으면 다시 조회
  if (!orderDetails.value || orderDetails.value.length === 0) {
    await fetchOrderDetails(order.ORDERNUM);
  }

  if (!orderDetails.value || orderDetails.value.length === 0) {
    notifyError('입고 처리할 품목이 없습니다. 발주를 다시 선택해주세요.');
    return;
  }
  
  if (!confirm(`선택한 발주(${order.ORDERNUM})를 입고 처리하시겠습니까?\n품목 수: ${orderDetails.value.length}건`)) {
    return;
  }
  
  try {
    const details = orderDetails.value.map((d: any) => {
      const remain = d.REMAINQTY > 0 ? d.REMAINQTY : (d.ORDERQTY || 0);
      return {
        PARTNO: d.PARTNO,
        INLOTQTY: Number(remain) || 0,
        ORDERQTY: Number(d.ORDERQTY) || 0,
        UNIT_PRICE: Number(d.UNIT_PRICE) || 0,
      };
    });

    const payload = {
      ORDERNUM: order.ORDERNUM,
      PLANTCD: order.PLANTCD || '',
      COMPANYCD: order.COMPANYCD || '',
      INDAY: new Date().toISOString().slice(0, 10),
      details
    };
    
    console.log('입고완료 payload:', JSON.stringify(payload));
    const res = await api.post('/api/receive/order', payload);
    console.log('입고완료 응답:', res.data);
    notifySuccess(`입고 처리가 완료되었습니다. (${res.data?.WAREHOUSENUM || ''})`);
    fetchOrders();
  } catch (e: any) {
    console.error('입고 처리 오류:', e);
    const msg = e?.response?.data?.detail || e?.message || '알 수 없는 오류';
    notifyError(`입고 처리 중 오류: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`);
  }
}

onMounted(() => {
  fetchPlants().then(() => {
    fetchOrders();
  });
});
</script>

<style scoped>
.page-view { display:flex; flex-direction:column; gap:10px; height:100%; }
.search-section { background:#fff; border-radius:10px; padding:14px 18px; box-shadow:0 1px 6px rgba(0,0,0,.04); }
.section-title { font-size:.85rem; font-weight:700; color:#34495e; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; padding-bottom:6px; border-bottom:2px solid #ecf0f1; }
.search-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.search-row label { font-size:.85rem; font-weight:600; color:#636e72; white-space:nowrap; }
.search-row input, .search-row select { padding:7px 10px; border:1px solid #dfe6e9; border-radius:6px; font-size:.85rem; }
.search-row input[type=date] { width:140px; }
.search-row input[type=text] { width:150px; }
.search-row select { min-width:130px; }
.sep { color:#b2bec3; font-weight:600; }
.checkbox-label { display:flex; align-items:center; gap:4px; cursor:pointer; }
.act-right { display:flex; gap:6px; margin-left:auto; }

.btn-search { background:#667eea; color:#fff; border:none; padding:7px 18px; border-radius:6px; font-weight:600; cursor:pointer; font-size:.85rem; transition: background 0.2s; }
.btn-search:hover { background:#5a6ecc; }
.btn-po { background:linear-gradient(135deg,#27ae60,#2ecc71); color:#fff; border:none; padding:7px 16px; border-radius:6px; font-weight:600; cursor:pointer; font-size:.85rem; transition: transform 0.1s; }
.btn-success { background:linear-gradient(135deg,#2980b9,#3498db); color:#fff; border:none; padding:7px 16px; border-radius:6px; font-weight:600; cursor:pointer; font-size:.85rem; transition: transform 0.1s; }
.btn-po:active, .btn-success:active { transform: scale(0.98); }
.btn-po:disabled, .btn-success:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-excel { background:#3498db; color:#fff; border:none; padding:7px 14px; border-radius:6px; font-weight:600; cursor:pointer; font-size:.85rem; }
.btn-print { background:#95a5a6; color:#fff; border:none; padding:7px 14px; border-radius:6px; font-weight:600; cursor:pointer; font-size:.85rem; }

.sub-title { padding:8px 12px; font-size:.85rem; font-weight:700; color:#2c3e50; background:#f8f9fa; border:1px solid #e9ecef; border-bottom: none; display:flex; align-items:center; border-radius: 6px 6px 0 0; }
.grid-area { display:flex; flex-direction:column; background:#fff; border:1px solid #e9ecef; border-radius:6px; overflow:hidden; }

.grid-area { display:flex; flex-direction:column; background:#fff; border:1px solid #e9ecef; border-radius:6px; overflow:hidden; }
</style>
