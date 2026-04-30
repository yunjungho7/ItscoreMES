<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="visible" @click.self="$emit('close')">
      <div class="modal-container">
        <!-- 헤더 -->
        <div class="modal-header">
          <div class="title">
            생산계획<span class="sub-title">[frmProdPlanPopup]</span>
          </div>
          <div class="header-actions">
            <button class="btn-save" @click="handleSave">
              <i class="fas fa-save"></i> 저장
            </button>
            <button class="btn-close" @click="$emit('close')">
              <i class="fas fa-times-circle"></i> 닫기
            </button>
          </div>
        </div>

        <!-- 바디 -->
        <div class="modal-body">
          <!-- 정보 패널 -->
          <div class="info-panel">
            <div class="info-item">
              <label><i class="fas fa-chevron-circle-right text-green"></i> 품번</label>
              <div class="info-value">{{ detailRow?.PARTNO }}</div>
            </div>
            <div class="info-item">
              <label><i class="fas fa-chevron-circle-right text-green"></i> 수주번호</label>
              <div class="info-value">{{ detailRow?.ORDERNO }}</div>
            </div>
            <div class="info-item">
              <label><i class="fas fa-chevron-circle-right text-green"></i> 납기요청일</label>
              <div class="info-value">{{ formatDate(detailRow?.ADOFREQDT) }}</div>
            </div>
            <div class="info-item">
              <label><i class="fas fa-chevron-circle-right text-green"></i> 수주수량</label>
              <div class="info-value text-right highlight-qty">{{ detailRow?.REQQTY }}</div>
            </div>
          </div>

          <!-- 툴바 -->
          <div class="toolbar">
            <div class="checkbox-group">
              <label class="custom-checkbox">
                <input type="checkbox" v-model="skipSat" />
                <span class="checkmark"></span>
                토요일
              </label>
              <label class="custom-checkbox">
                <input type="checkbox" v-model="skipSun" />
                <span class="checkmark"></span>
                일요일
              </label>
            </div>
            <div class="action-buttons">
              <button class="btn-add" @click="addPlanRow">
                <i class="fas fa-download"></i> 추가
              </button>
              <button class="btn-delete" @click="removePlanRows">
                <i class="fas fa-scissors"></i> 삭제
              </button>
            </div>
          </div>

          <!-- 그리드 -->
          <div class="grid-container">
            <table class="plan-table">
              <thead>
                <tr>
                  <th width="40px">
                    <input type="checkbox" :checked="isAllSelected" @change="toggleAll" />
                  </th>
                  <th>계획일</th>
                  <th>품번</th>
                  <th>계획수량</th>
                  <th>수주번호</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in planList" :key="index" :class="{ 'selected': row._selected }">
                  <td class="text-center">
                    <input type="checkbox" v-model="row._selected" />
                  </td>
                  <td>
                    <input type="date" v-model="row.PRODUCEDT" class="grid-input" />
                  </td>
                  <td class="text-center">{{ detailRow?.PARTNO }}</td>
                  <td>
                    <input type="number" v-model.number="row.PRODUCEQTY" class="grid-input text-right" min="0" />
                  </td>
                  <td class="text-center">{{ detailRow?.ORDERNO }}</td>
                </tr>
                <tr v-if="planList.length === 0">
                  <td colspan="5" class="empty-msg">추가 버튼을 눌러 계획을 등록하세요.</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="text-right font-bold">합계</td>
                  <td class="text-right font-bold text-blue">{{ totalPlanQty }}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps<{
  visible: boolean;
  orderRow: any;
  detailRow: any;
}>();

const emit = defineEmits(['close', 'save']);

const skipSat = ref(false);
const skipSun = ref(false);

interface PlanRow {
  _selected: boolean;
  PRODUCEDT: string;
  PRODUCEQTY: number;
}

const planList = ref<PlanRow[]>([]);

// Reset when opened
watch(() => props.visible, (newVal) => {
  if (newVal) {
    planList.value = [];
    skipSat.value = false;
    skipSun.value = false;
  }
});

const isAllSelected = computed(() => {
  return planList.value.length > 0 && planList.value.every(r => r._selected);
});

const totalPlanQty = computed(() => {
  return planList.value.reduce((sum, r) => sum + (Number(r.PRODUCEQTY) || 0), 0);
});

function toggleAll(e: Event) {
  const checked = (e.target as HTMLInputElement).checked;
  planList.value.forEach(r => r._selected = checked);
}

function formatDate(dateStr: string) {
  if (!dateStr) return '';
  return dateStr.slice(0, 10);
}

function getNextDate(baseDateStr: string): Date {
  const d = new Date(baseDateStr);
  d.setDate(d.getDate() + 1);
  
  // Loop until we find a valid day
  while (true) {
    const day = d.getDay();
    let skip = false;
    if (skipSat.value && day === 6) skip = true;
    if (skipSun.value && day === 0) skip = true;
    
    if (!skip) break;
    d.setDate(d.getDate() + 1);
  }
  return d;
}

function addPlanRow() {
  let nextDateStr = '';
  
  if (planList.value.length > 0) {
    // Get last date
    const lastDate = planList.value[planList.value.length - 1].PRODUCEDT;
    if (lastDate) {
      const nextDate = getNextDate(lastDate);
      nextDateStr = nextDate.toISOString().slice(0, 10);
    } else {
      nextDateStr = new Date().toISOString().slice(0, 10);
    }
  } else {
    // Start from today or next valid date
    let startD = new Date();
    while (true) {
      const day = startD.getDay();
      if ((skipSat.value && day === 6) || (skipSun.value && day === 0)) {
        startD.setDate(startD.getDate() + 1);
      } else {
        break;
      }
    }
    nextDateStr = startD.toISOString().slice(0, 10);
  }

  // Calculate default quantity: remaining qty
  const reqQty = Number(props.detailRow?.REQQTY || 0);
  const currentTotal = totalPlanQty.value;
  const remaining = Math.max(0, reqQty - currentTotal);

  planList.value.push({
    _selected: false,
    PRODUCEDT: nextDateStr,
    PRODUCEQTY: remaining > 0 ? remaining : 0
  });
}

function removePlanRows() {
  const prevLen = planList.value.length;
  planList.value = planList.value.filter(r => !r._selected);
  if (prevLen === planList.value.length) {
    alert('삭제할 행을 선택하세요.');
  }
}

function handleSave() {
  if (planList.value.length === 0) {
    alert('계획을 추가해주세요.');
    return;
  }
  
  // Validate
  const emptyDates = planList.value.filter(r => !r.PRODUCEDT);
  if (emptyDates.length > 0) {
    alert('계획일이 누락된 항목이 있습니다.');
    return;
  }
  
  // Validate total qty against req qty? Warning or block?
  // Usually, users can underplan or overplan, but let's give a warning if they overplan.
  const reqQty = Number(props.detailRow?.REQQTY || 0);
  if (totalPlanQty.value > reqQty) {
    if (!confirm('계획수량 합계가 수주수량을 초과합니다. 계속하시겠습니까?')) {
      return;
    }
  }

  const payloads = planList.value.map((row) => ({
    PRODUCEDT: row.PRODUCEDT,
    PLANTCD: props.orderRow?.PLANTCD,
    PARTNO: props.detailRow?.PARTNO,
    ORDERNUM: String(props.detailRow?.ORDERNO || ''),
    ORDERSEQ: Number(props.detailRow?.SEQ || 1),
    PRODUCEQTY: Number(row.PRODUCEQTY || 0),
    REGUSERID: 1,
    EDITUSERID: 1
  }));

  emit('save', payloads);
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  width: 750px;
  background: #f8fafc;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid #94a3b8;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-header {
  background: #629b9b;
  color: white;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.25rem;
  font-weight: 800;
  display: flex;
  align-items: baseline;
  gap: 8px;
  letter-spacing: -0.5px;
}

.sub-title {
  font-size: 0.85rem;
  font-weight: 500;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-save, .btn-close {
  background: #f8fafc;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 6px 14px;
  border-radius: 4px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.btn-save:hover {
  background: #ffffff;
  color: #0ea5e9;
  border-color: #0ea5e9;
}

.btn-close:hover {
  background: #fee2e2;
  color: #ef4444;
  border-color: #ef4444;
}

.modal-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 24px;
  background: white;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item label {
  width: 100px;
  font-weight: 700;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 6px;
}

.text-green {
  color: #84cc16;
}

.info-value {
  flex: 1;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 6px 12px;
  font-weight: 600;
  color: #0f172a;
}

.text-right {
  text-align: right;
}

.highlight-qty {
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 800;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 24px;
  padding: 8px 0;
}

.checkbox-group {
  display: flex;
  gap: 16px;
}

.custom-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #334155;
  user-select: none;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-add, .btn-delete {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  transition: all 0.2s;
}

.btn-add:hover { background: #dcfce7; color: #16a34a; border-color: #16a34a; }
.btn-delete:hover { background: #fee2e2; color: #dc2626; border-color: #dc2626; }

.grid-container {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  overflow: hidden;
  min-height: 200px;
  max-height: 350px;
  overflow-y: auto;
}

.plan-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.plan-table th, .plan-table td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
}

.plan-table th {
  background: #f1f5f9;
  color: #334155;
  font-weight: 700;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 10;
}

.plan-table tbody tr:hover {
  background: #f8fafc;
}

.plan-table tbody tr.selected {
  background: #eff6ff;
}

.text-center { text-align: center; }
.font-bold { font-weight: 700; }
.text-blue { color: #2563eb; }

.grid-input {
  width: 100%;
  border: 1px solid #cbd5e1;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}

.grid-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
}

.empty-msg {
  text-align: center;
  color: #94a3b8;
  padding: 40px !important;
  font-style: italic;
}
</style>
