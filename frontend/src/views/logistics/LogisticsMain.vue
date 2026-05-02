<template>
  <div class="logistics-page">
    <!-- Header -->
    <header class="logistics-header">
      <div class="header-left">
        <h1 class="page-title">재고/물류관리</h1>
      </div>
      <div class="header-right">
        <div class="printer-select">
          <label>📠 프린터</label>
          <select v-model="selectedPrinter">
            <option value="">(선택하세요)</option>
            <option v-for="p in printers" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="header-buttons">
          <button class="btn-icon" @click="fetchData">
            <span class="icon">🔍</span> 조회
          </button>
          <button class="btn-icon" @click="goToProduction">
            <span class="icon">🔄</span> 생산
          </button>
          <button class="btn-icon btn-close" @click="goBack">
            <span class="icon">❌</span> 종료
          </button>
          <button class="btn-icon" @click="toggleOptions">
            <span class="icon">⚙️</span> 옵션
          </button>
        </div>
      </div>
    </header>

    <!-- Search Section -->
    <section class="search-section">
      <div v-if="activeTab === 'receiving'" class="filter-grid">
        <div class="filter-item">
          <label>입고기간</label>
          <div class="date-range">
            <input type="date" v-model="filters.startDate" />
            <span>~</span>
            <input type="date" v-model="filters.endDate" />
          </div>
        </div>
        <div class="filter-item">
          <label>거래업체</label>
          <div class="search-input">
            <input type="text" v-model="filters.partner" placeholder="거래처 검색" @keyup.enter="fetchData" />
            <button class="btn-search-small">🔍</button>
          </div>
        </div>
        <div class="filter-item">
          <label>품번</label>
          <div class="search-input">
            <input type="text" v-model="filters.partNo" placeholder="품번 검색" @keyup.enter="fetchData" />
            <button class="btn-search-small">🔍</button>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'inspection'" class="filter-grid">
        <div class="filter-item">
          <label>입고일자</label>
          <div class="date-range">
            <input type="date" v-model="filters.startDate" />
            <span>~</span>
            <input type="date" v-model="filters.endDate" />
          </div>
        </div>
        <div class="filter-item">
          <label>LOT No.</label>
          <div class="search-input">
            <input type="text" v-model="filters.lotNo" placeholder="LOT 번호" @keyup.enter="fetchData" />
          </div>
        </div>
        <div class="filter-item">
          <label>자재품번</label>
          <div class="search-input">
            <input type="text" v-model="filters.partNo" placeholder="품번 검색" @keyup.enter="fetchData" />
            <button class="btn-search-small">🔍</button>
          </div>
        </div>
        <div class="filter-item">
          <label>업체코드</label>
          <div class="search-input">
            <input type="text" v-model="filters.partnerCode" placeholder="업체코드" @keyup.enter="fetchData" />
            <button class="btn-search-small">🔍</button>
          </div>
        </div>
      </div>

      <!-- Filters for Shipping -->
      <div v-else-if="activeTab === 'shipping'">
        <div class="filter-row-container">
          <div class="filter-grid">
            <div class="filter-item">
              <label>출하일</label>
              <div class="date-range">
                <input type="date" v-model="filters.startDate" />
                <span>~</span>
                <input type="date" v-model="filters.endDate" />
              </div>
            </div>
            <div class="filter-item">
              <label>고객사</label>
              <div class="search-input">
                <input type="text" v-model="filters.customer" placeholder="고객사 검색" @keyup.enter="fetchData" />
                <button class="btn-search-small">🔍</button>
              </div>
            </div>
            <div class="filter-item">
              <label>품번</label>
              <div class="search-input">
                <input type="text" v-model="filters.partNo" placeholder="품번 검색" @keyup.enter="fetchData" />
                <button class="btn-search-small">🔍</button>
              </div>
            </div>
          </div>
          
          <div class="action-buttons-inline">
            <button class="btn-action-small grey" @click="fetchData">
              <span class="icon">🔄</span> 다시조회
            </button>
            <button class="btn-action-small blue" @click="handleRegistration">
              <span class="icon">💾</span> 출하등록
            </button>
          </div>
        </div>
        
        <div class="filter-grid sub-filters">
          <div class="filter-item">
            <label>출하지시번호</label>
            <input type="text" v-model="filters.shipmentNo" readonly class="readonly-input" />
          </div>
          <div class="filter-item">
            <label>고객사</label>
            <input type="text" v-model="filters.customerName" readonly class="readonly-input" />
          </div>
          <div class="filter-item">
            <label>LOT No.</label>
            <input type="text" v-model="filters.lotNo" @keyup.enter="onLotScan" />
          </div>
          <div class="filter-item checkbox-item">
            <input type="checkbox" id="fifo-msg" v-model="filters.fifoMsg" />
            <label for="fifo-msg">선출 메시지</label>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content Area -->
    <main class="main-content">
      <div class="grid-container" :class="{ 'with-form': showForm }">
        <div class="grid-vertical-split">
          <!-- Top Grid (Main List) -->
          <div class="table-wrap top-grid">
            <DataGrid 
              :columns="masterColumns" 
              :rows="masterRows" 
              :loading="loading"
              :selectedIndex="selectedMasterIdx"
              @row-click="onMasterClick"
            />
            <div class="grid-footer">
              <div class="record-info">Record {{ masterRows.length }} items</div>
            </div>
          </div>

          <!-- Bottom Grid (Detail List) -->
          <div v-if="hasDetailGrid" class="table-wrap bottom-grid">
            <DataGrid 
              :columns="detailColumns" 
              :rows="detailRows" 
              :loading="detailLoading"
              @row-click="onDetailClick"
            >
              <!-- Checkbox Slot for Shipping -->
              <template #cell-CHECK="{ row }">
                <input 
                  type="checkbox" 
                  v-model="row.isChecked" 
                  @change="onRowCheckChange(row)"
                  @click.stop
                />
              </template>

              <!-- Editable SHIPQTY Slot for Shipping -->
              <template #cell-SHIPQTY="{ row }">
                <input 
                  v-if="activeTab === 'shipping'"
                  type="number" 
                  v-model="row.SHIPQTY" 
                  class="grid-input"
                  @input="onRowQtyInput(row)"
                  @click.stop
                />
                <span v-else>{{ row.SHIPQTY }}</span>
              </template>
            </DataGrid>
            <div class="grid-footer-summary" v-if="activeTab === 'shipping'">
              <div class="summary-item">
                <span class="label">Total</span>
                <span class="value">{{ totalShippingQty }}</span>
              </div>
            </div>
            <div class="grid-footer">
              <div class="record-info">Record {{ detailRows.length }} items</div>
            </div>
          </div>
        </div>

        <!-- Registration Form (Right Panel) - Hidden for Shipping -->
        <aside v-if="showForm" class="registration-form">
          <div class="form-header">
            <h3>{{ formTitle }}</h3>
            <button class="btn-save" @click="handleRegistration">💾 {{ activeTab === 'inspection' ? '합격등록' : '입고등록' }}</button>
          </div>
          <div class="form-body">
            <div v-if="activeTab === 'receiving'" class="form-grid">
              <div class="form-item"><label>자재품번</label><input type="text" v-model="form.partNo" readonly /></div>
              <div class="form-item"><label>품명</label><input type="text" v-model="form.partName" readonly /></div>
              <div class="form-item"><label>발주수량</label><input type="number" v-model="form.orderQty" readonly /></div>
              <div class="form-item"><label>입고수량</label><input type="number" v-model="form.recvQty" /></div>
              <div class="form-item"><label>업체LOTNo</label><input type="text" v-model="form.partnerLot" /></div>
              <div class="form-item full-width"><label>비고</label><textarea v-model="form.remark"></textarea></div>
            </div>
            <div v-else-if="activeTab === 'inspection'" class="form-grid">
              <p>선택된 LOT의 검사 결과를 등록합니다.</p>
              <div class="form-item"><label>LOT No.</label><input type="text" v-model="form.lotNo" readonly /></div>
              <div class="form-item"><label>검사결과</label>
                <select v-model="form.inspResult">
                  <option value="OK">합격</option>
                  <option value="NG">불합격</option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <button class="btn-action reset" @click="resetForm">🔄 초기화</button>
              <button class="btn-action apply" @click="handleApply">📥 적용</button>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <!-- Footer Tabs -->
    <footer class="logistics-footer">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-button"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </footer>

    <!-- Shipment Search Modal -->
    <div v-if="shipmentModalVisible" class="modal-overlay">
      <div class="modal-content shipment-modal">
        <header class="modal-header-custom">
          <h2>출하지시조회</h2>
          <div class="modal-header-btns">
            <button class="btn-modal-action confirm" @click="confirmShipmentSelection">
              <span class="icon">✅</span> 확인
            </button>
            <button class="btn-modal-action close" @click="shipmentModalVisible = false">
              <span class="icon">❌</span> 닫기
            </button>
          </div>
        </header>
        <div class="modal-body-grid">
          <DataGrid 
            :columns="shipmentModalColumns" 
            :rows="shipmentModalRows" 
            :loading="shipmentModalLoading"
            :selectedIndex="modalSelectedIndex"
            @row-click="onModalRowClick"
          />
        </div>
        <footer class="modal-footer-custom">
          <div class="record-info">Record {{ shipmentModalRows.length }} items</div>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataGrid from '../../components/common/DataGrid.vue';
import api from '../../api';
import { useNotification } from '../../composables/useNotification';

const router = useRouter();
const { notifySuccess, notifyError } = useNotification();

const selectedPrinter = ref('');
const printers = ref(['Label Printer 1', 'Office Laser 1', 'TSC-244 Pro']);
const activeTab = ref('receiving');

const loading = ref(false);
const detailLoading = ref(false);
const masterRows = ref<any[]>([]);
const detailRows = ref<any[]>([]);
const selectedMasterIdx = ref(-1);
const selectedMaster = ref<any>(null);

// Shipment Modal State
const shipmentModalVisible = ref(false);
const shipmentModalRows = ref<any[]>([]);
const shipmentModalLoading = ref(false);
const modalSelectedIndex = ref(-1);
const selectedShipmentInModal = ref<any>(null);

const tabs = [
  { id: 'receiving', label: '입고등록' },
  { id: 'inspection', label: '수입검사' },
  { id: 'receiving-history', label: '입고이력' },
  { id: 'shipping', label: '출하등록' },
  { id: 'shipping-history', label: '출하이력' },
];

const filters = ref({
  startDate: new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10),
  endDate: new Date().toISOString().slice(0, 10),
  partner: '',
  partNo: '',
  lotNo: '',
  partnerCode: '',
  customer: '',
  shipmentNo: '',
  customerName: '',
  fifoMsg: true,
});

const form = ref({
  partNo: '',
  partName: '',
  orderQty: 0,
  recvQty: 0,
  partnerLot: '',
  remark: '',
  lotNo: '',
  inspResult: 'OK',
});

const showForm = computed(() => {
  return ['receiving', 'inspection'].includes(activeTab.value);
});

const hasDetailGrid = computed(() => {
  return ['receiving', 'shipping'].includes(activeTab.value);
});

const formTitle = computed(() => {
  if (activeTab.value === 'receiving') return '입고등록';
  if (activeTab.value === 'inspection') return '합격등록';
  if (activeTab.value === 'shipping') return '출하등록';
  return '';
});

const totalShippingQty = computed(() => {
  return detailRows.value.reduce((sum, row) => sum + (Number(row.SHIPQTY) || 0), 0);
});

const shipmentModalColumns = [
  { key: 'index', label: '순번', width: '60px' },
  { key: 'SHIPMENT_NO', label: '출하지시번호', width: '150px' },
  { key: 'SHIP_PLAN_DATE', label: '출하계획일', width: '120px', type: 'date' },
  { key: 'COMPANYNM', label: '고객사', width: '180px' },
  { key: 'PARTNO', label: '제품품번', width: '150px' },
  { key: 'PARTNM', label: '품명', width: '180px' },
];

const masterColumns = computed(() => {
  if (activeTab.value === 'receiving') {
    return [
      { key: 'COMPANYNM', label: '공급사', width: '150px' },
      { key: 'INDAY', label: '발주일', width: '120px' },
      { key: 'RECV_PLAN_DATE', label: '입고예정일', width: '120px' },
      { key: 'ORDERNUM', label: '발주번호', width: '150px' },
      { key: 'REMARK', label: '비고', width: '200px' },
    ];
  } else if (activeTab.value === 'inspection') {
    return [
      { key: 'INDAY', label: '입고일자', width: '120px' },
      { key: 'WAREHOUSENUM', label: '입고번호', width: '150px' },
      { key: 'LOTNO', label: 'LOT No.', width: '150px' },
      { key: 'PARTNO', label: '자재품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '150px' },
      { key: 'STANDARD', label: '규격', width: '100px' },
      { key: 'INLOTQTY', label: '가입고수량', width: '100px' },
      { key: 'UNIT', label: '단위', width: '80px' },
    ];
  } else if (activeTab.value === 'receiving-history') {
    return [
      { key: 'WAREHOUSENUM', label: '입고번호', width: '150px' },
      { key: 'INDAY', label: '입고일자', width: '120px' },
      { key: 'COMPANYNM', label: '공급사', width: '150px' },
      { key: 'PARTNO', label: '자재품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '180px' },
      { key: 'INLOTQTY', label: '입고수량', width: '100px' },
      { key: 'LOTNO', label: 'LOT No.', width: '150px' },
    ];
  } else if (activeTab.value === 'shipping') {
    return [
      { key: 'PARTNO', label: '제품품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '180px' },
      { key: 'STANDARD', label: '규격', width: '120px' },
      { key: 'UNIT', label: '단위', width: '80px' },
      { key: 'ORDERQTY', label: '지시수량', width: '100px' },
      { key: 'SHIPPEDQTY', label: '기출하수량', width: '100px' },
      { key: 'CUR_SHIPQTY', label: '출하수량', width: '100px' },
    ];
  } else if (activeTab.value === 'shipping-history') {
    return [
      { key: 'SHIPMENT_NO', label: '출하번호', width: '150px' },
      { key: 'SHIP_DATE', label: '출하일자', width: '120px' },
      { key: 'COMPANYNM', label: '고객사', width: '150px' },
      { key: 'PARTNO', label: '제품품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '180px' },
      { key: 'SHIPQTY', label: '출하수량', width: '100px' },
      { key: 'LOTNO', label: 'LOT No.', width: '150px' },
    ];
  }
  return [];
});

const detailColumns = computed(() => {
  if (activeTab.value === 'receiving') {
    return [
      { key: 'PARTNO', label: '자재품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '180px' },
      { key: 'STANDARD', label: '규격', width: '120px' },
      { key: 'UNIT', label: '단위', width: '80px' },
      { key: 'ORDERQTY', label: '발주수량', width: '100px' },
      { key: 'ALREADYQTY', label: '기입고수량', width: '100px' },
      { key: 'INQTY', label: '입고수량', width: '100px' },
      { key: 'STOCKQTY', label: '재고수량', width: '100px' },
      { key: 'WHNM', label: '창고', width: '120px' },
      { key: 'LOCNM', label: '위치명', width: '120px' },
    ];
  } else if (activeTab.value === 'shipping') {
    return [
      { key: 'CHECK', label: '선택', width: '50px' },
      { key: 'LOTNO', label: 'LOT No.', width: '180px' },
      { key: 'PARTNO', label: '제품품번', width: '150px' },
      { key: 'PARTNM', label: '품명', width: '180px' },
      { key: 'STANDARD', label: '규격', width: '120px' },
      { key: 'UNIT', label: '단위', width: '80px' },
      { key: 'SHIPQTY', label: '출하수량', width: '100px' },
      { key: 'STOCKQTY', label: '재고수량', width: '100px' },
      { key: 'LOCNM', label: '재고위치', width: '120px' },
    ];
  }
  return [];
});

async function fetchData() {
  if (activeTab.value === 'shipping') {
    openShipmentSearch();
    return;
  }

  loading.value = true;
  selectedMasterIdx.value = -1;
  selectedMaster.value = null;
  detailRows.value = [];
  
  try {
    let endpoint = '';
    const params: any = {
      start_date: filters.value.startDate,
      end_date: filters.value.endDate,
    };

    if (activeTab.value === 'receiving') {
      endpoint = '/api/purchase/list';
      params.search = filters.value.partner || filters.value.partNo;
    } else if (activeTab.value === 'inspection') {
      endpoint = '/api/receive/list'; 
      params.search = filters.value.lotNo || filters.value.partNo;
    }

    if (endpoint) {
      const r = await api.get(endpoint, { params });
      // Robust data extraction
      masterRows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    }
  } catch (e) {
    notifyError('데이터 조회 중 오류가 발생했습니다.');
  } finally {
    loading.value = false;
  }
}

async function openShipmentSearch() {
  shipmentModalVisible.value = true;
  shipmentModalLoading.value = true;
  modalSelectedIndex.value = -1;
  selectedShipmentInModal.value = null;
  
  try {
    const r = await api.get('/api/shipment/list', {
      params: {
        start_date: filters.value.startDate,
        end_date: filters.value.endDate,
        search: filters.value.customer || filters.value.partNo
      }
    });
    
    // Robust data extraction
    const rawData = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    
    shipmentModalRows.value = Array.isArray(rawData) ? rawData.map((item: any, idx: number) => ({
      ...item,
      index: idx + 1
    })) : [];
    
  } catch (e) {
    notifyError('출하지시 목록 조회 중 오류가 발생했습니다.');
  } finally {
    shipmentModalLoading.value = false;
  }
}

function onModalRowClick(row: any, idx: number) {
  modalSelectedIndex.value = idx;
  selectedShipmentInModal.value = row;
}

async function confirmShipmentSelection() {
  if (!selectedShipmentInModal.value) {
    notifyError('출하지시 건을 선택해주세요.');
    return;
  }

  const row = selectedShipmentInModal.value;
  filters.value.shipmentNo = row.SHIPMENT_NO;
  filters.value.customerName = row.COMPANYNM;
  filters.value.endDate = row.SHIP_PLAN_DATE || filters.value.endDate;
  
  // Set Main Grid
  masterRows.value = [{
    PARTNO: row.PARTNO,
    PARTNM: row.PARTNM,
    STANDARD: row.STANDARD,
    UNIT: row.UNIT,
    ORDERQTY: row.SHIPQTY || row.ORDERQTY || 0,
    SHIPPEDQTY: 0,
    CUR_SHIPQTY: row.SHIPQTY || row.ORDERQTY || 0
  }];
  selectedMasterIdx.value = 0;
  selectedMaster.value = masterRows.value[0];

  // Fetch Detail Grid (LOTs)
  detailLoading.value = true;
  try {
    const r = await api.get(`/api/inventory/detail/${row.PARTNO}`);
    const lotData = Array.isArray(r.data) ? r.data : (Array.isArray(r.data?.data) ? r.data.data : []);
    detailRows.value = lotData.map((item: any) => ({
      ...item,
      SHIPQTY: 0 
    }));
  } catch (e) {
    notifyError('재고 정보 조회 중 오류가 발생했습니다.');
  } finally {
    detailLoading.value = false;
    shipmentModalVisible.value = false;
  }
}

async function onMasterClick(row: any, idx: number) {
  selectedMasterIdx.value = idx;
  selectedMaster.value = row;
  
  if (activeTab.value === 'receiving') {
    detailLoading.value = true;
    try {
      const r = await api.get(`/api/purchase/detail/${row.ORDERNUM}`);
      detailRows.value = Array.isArray(r.data?.data) ? r.data.data : (r.data?.data || []);
    } finally {
      detailLoading.value = false;
    }
  } else if (activeTab.value === 'inspection') {
    form.value.lotNo = row.LOTNO;
  }
}

function onDetailClick(row: any) {
  if (activeTab.value === 'receiving') {
    form.value.partNo = row.PARTNO;
    form.value.partName = row.PARTNM;
    form.value.orderQty = row.ORDERQTY;
    form.value.recvQty = row.ORDERQTY - (row.ALREADYQTY || 0);
  }
}

function onRowCheckChange(row: any) {
  if (row.isChecked) {
    row.SHIPQTY = row.STOCKQTY;
  } else {
    row.SHIPQTY = 0;
  }
}

function onRowQtyInput(row: any) {
  row.isChecked = Number(row.SHIPQTY) > 0;
}

function handleApply() {
  if (activeTab.value === 'receiving') {
    if (!form.value.partNo) return notifyError('품목을 선택해주세요.');
    notifySuccess('품목 정보가 적용되었습니다.');
  }
}

async function handleRegistration() {
  if (activeTab.value === 'receiving') {
    if (!form.value.partNo) return notifyError('등록할 품목을 선택해주세요.');
    try {
      // API call to register receiving
      notifySuccess('입고 등록이 완료되었습니다.');
      fetchData();
    } catch (e) {
      notifyError('입고 등록 중 오류가 발생했습니다.');
    }
  } else if (activeTab.value === 'inspection') {
    if (!form.value.lotNo) return notifyError('검사할 LOT를 선택해주세요.');
    notifySuccess('합격 등록이 완료되었습니다.');
    fetchData();
  } else if (activeTab.value === 'shipping') {
    const selectedLots = detailRows.value.filter(row => row.isChecked && Number(row.SHIPQTY) > 0);
    
    if (selectedLots.length === 0) {
      return notifyError('출하할 LOT를 선택하고 수량을 입력해주세요.');
    }

    if (!filters.value.shipmentNo) {
      return notifyError('출하지시를 먼저 조회해주세요.');
    }

    try {
      loading.value = true;
      const payload = {
        shipment_indication_no: filters.value.shipmentNo,
        company_cd: selectedMaster.value.COMPANYCD || '', 
        plant_cd: selectedMaster.value.PLANTCD || 'P1',
        unit: selectedMaster.value.UNIT || 'EA',
        user_id: 1, // Current user
        lots: selectedLots.map(lot => ({
          part_no: lot.PARTNO,
          lot_no: lot.LOTNO,
          qty: Number(lot.SHIPQTY)
        }))
      };

      const r = await api.post('/api/shipment/register', payload);
      if (r.data.statusCode === 200) {
        notifySuccess(`출하 등록 완료 (번호: ${r.data.shipment_no})`);
        // Refresh grids
        masterRows.value = [];
        detailRows.value = [];
        filters.value.shipmentNo = '';
        filters.value.customerName = '';
      }
    } catch (e: any) {
      notifyError(e.response?.data?.detail || '출하 등록 중 오류가 발생했습니다.');
    } finally {
      loading.value = false;
    }
  }
}

function resetForm() {
  form.value = {
    partNo: '',
    partName: '',
    orderQty: 0,
    recvQty: 0,
    partnerLot: '',
    remark: '',
    lotNo: '',
    inspResult: 'OK',
  };
}

function onLotScan() {
  if (filters.value.lotNo) {
    notifySuccess(`LOT [${filters.value.lotNo}] 스캔 완료`);
    // Handle lot scan logic
    filters.value.lotNo = '';
  }
}

function goBack() {
  router.push('/select-mode');
}

function goToProduction() {
  router.push('/field');
}

function toggleOptions() {
  // Option logic
}

watch(activeTab, (newTab) => {
  if (newTab !== 'shipping') {
    fetchData();
  } else {
    masterRows.value = [];
    detailRows.value = [];
  }
});

onMounted(() => {
  if (activeTab.value !== 'shipping') {
    fetchData();
  }
});
</script>

<style scoped>
.logistics-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f4f6f9;
  font-family: 'Malgun Gothic', sans-serif;
  color: #333;
}

/* Header */
.logistics-header {
  background-color: #4b8a3e;
  color: white;
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  z-index: 10;
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

.printer-select {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.15);
  padding: 5px 15px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.printer-select select {
  padding: 3px 8px;
  border-radius: 4px;
  border: none;
  font-size: 0.9rem;
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

.btn-icon.btn-close:hover {
  background: #c82333;
}

/* Search Section */
.search-section {
  background: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #dee2e6;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.sub-filters {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ccc;
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
  padding: 6px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-input {
  display: flex;
  align-items: center;
}

.search-input input {
  padding: 6px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px 0 0 4px;
  width: 160px;
  font-size: 0.9rem;
}

.btn-search-small {
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-left: none;
  background: #e9ecef;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.readonly-input {
  background: #e9ecef;
  border: 1px solid #ced4da;
  padding: 6px 10px;
  border-radius: 4px;
  width: 160px;
  font-size: 0.9rem;
}

/* Action Buttons in Search Row */
.filter-row-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.action-buttons-inline {
  display: flex;
  gap: 8px;
}

.btn-action-small {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
}

.btn-action-small.grey {
  background: #f8f9fa;
  color: #333;
}

.btn-action-small.blue {
  background: #339af0;
  color: white;
  border-color: #228be6;
}

.checkbox-item {
  gap: 5px;
}

.checkbox-item input {
  width: 18px;
  height: 18px;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 15px;
  overflow: hidden;
}

.grid-container {
  display: flex;
  gap: 15px;
  height: 100%;
}

.grid-vertical-split {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-width: 0;
}

.table-wrap {
  flex: 1;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.top-grid {
  flex: 1;
}

.bottom-grid {
  flex: 1;
}

.grid-footer {
  padding: 6px 12px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  font-size: 0.8rem;
  font-weight: 600;
  color: #6c757d;
}

/* Registration Form */
.registration-form {
  width: 380px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}

.form-header {
  padding: 12px 20px;
  background: #f1f3f5;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.form-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #343a40;
}

.btn-save {
  background: #339af0;
  color: white;
  border: none;
  padding: 7px 15px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-save:hover {
  background: #228be6;
}

.form-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-item label {
  font-weight: 800;
  color: #fd7e14;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.form-item input, .form-item textarea, .form-item select {
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
}

.form-item input[readonly] {
  background: #f1f3f5;
  color: #495057;
}

.form-item textarea {
  min-height: 80px;
  resize: vertical;
}

.form-actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
  padding-top: 15px;
}

.btn-action {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-action.reset {
  background: #adb5bd;
  color: white;
}

.btn-action.reset:hover {
  background: #868e96;
}

.btn-action.apply {
  background: #40c057;
  color: white;
}

.btn-action.apply:hover {
  background: #37b24d;
}

/* Footer Tabs */
.logistics-footer {
  display: flex;
  background: #ced4da;
  padding: 5px;
  gap: 4px;
}

.tab-button {
  flex: 1;
  padding: 15px;
  border: none;
  background: #e9ecef;
  font-weight: 800;
  color: #495057;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
  border-radius: 4px;
}

.tab-button:hover {
  background: #f8f9fa;
}

.tab-button.active {
  background: white;
  color: #2c3e50;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  position: relative;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: #4b8a3e;
  border-radius: 0 0 4px 4px;
}

/* Summary Row Styling */
.grid-footer-summary {
  display: flex;
  justify-content: flex-end;
  padding: 8px 20px;
  background: #f8f9fa;
  border-top: 2px solid #dee2e6;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-weight: 800;
  font-size: 1rem;
}

.summary-item .label {
  color: #495057;
}

.summary-item .value {
  color: #d63384;
  min-width: 100px;
  text-align: right;
  border: 1px solid #ced4da;
  padding: 4px 10px;
  background: white;
  border-radius: 4px;
}

.grid-input {
  width: 80px;
  padding: 4px 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  text-align: right;
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content.shipment-modal {
  background: white;
  width: 900px;
  max-width: 95vw;
  height: 600px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 5px 25px rgba(0,0,0,0.3);
}

.modal-header-custom {
  background-color: #6ca0a0;
  color: white;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header-custom h2 {
  margin: 0;
  font-size: 1.2rem;
}

.modal-header-btns {
  display: flex;
  gap: 10px;
}

.btn-modal-action {
  padding: 6px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.btn-modal-action.confirm {
  background: white;
  color: #2c3e50;
}

.btn-modal-action.close {
  background: #e74c3c;
  color: white;
  border-color: #c0392b;
}

.modal-body-grid {
  flex: 1;
  padding: 10px;
  overflow: hidden;
}

.modal-footer-custom {
  padding: 10px 20px;
  background: #f8f9fa;
  border-top: 1px solid #ddd;
  font-size: 0.9rem;
  color: #666;
}
</style>
