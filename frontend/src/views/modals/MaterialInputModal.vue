<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-container material-modal">
        <header class="modal-header">
          <div class="header-title-wrap">
            <span class="header-icon">📥</span>
            <div class="title-text">
              <h3>자재투입등록</h3>
              <p class="sub-title">Material Input Registration</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn-save-main" @click="save">
              <span class="icon">✔️</span> 적용하기
            </button>
            <button class="btn-close-x" @click="$emit('close')">✕</button>
          </div>
        </header>

        <div class="modal-body">
          <!-- 상단 입력 폼 -->
          <section class="info-card input-card">
            <div class="form-layout">
              <div class="form-group">
                <label>투입 LOT No.</label>
                <div class="search-input-wrap">
                  <input type="text" v-model="matInput.MAT_LOTNO" @keyup.enter="save" placeholder="LOT 번호를 입력하거나 그리드에서 선택" />
                  <button class="btn-lookup-inner">🔍</button>
                </div>
              </div>
              <div class="form-group">
                <label>적용 수량</label>
                <input type="number" v-model.number="matInput.INPUT_QTY" class="qty-input" />
              </div>
              <div class="tip-box">
                <p>💡 <b>Tip:</b> 아래 가용재고 목록에서 행을 클릭하면 LOT 번호와 수량이 자동 입력됩니다.</p>
              </div>
            </div>
          </section>

          <!-- 그리드 영역 -->
          <section class="info-card grid-card">
            <div class="card-header">
              <span class="dot"></span>
              <h4>투입 내역 및 가용 재고</h4>
            </div>
            <div class="grid-table-wrap">
              <table class="styled-table">
                <thead>
                  <tr>
                    <th width="40"><input type="checkbox" :checked="isAllChecked" @change="toggleAll" class="styled-chk" /></th>
                    <th width="100">상태</th>
                    <th>LOT No.</th>
                    <th>품번</th>
                    <th>품명</th>
                    <th width="60">단위</th>
                    <th width="90">투입수량</th>
                    <th width="90">소요량</th>
                    <th width="90">재고수량</th>
                    <th width="120">위치</th>
                    <th width="80">관리</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(r, i) in rows" :key="i" 
                      :class="{ 'row-input': r.RECORD_GUBUN === 'INPUT', 'row-stock': r.RECORD_GUBUN === 'STOCK' }"
                      @click="onRowClick(r)">
                    <td class="center" @click.stop>
                      <input type="checkbox" v-model="r._checked" v-if="r.RECORD_GUBUN === 'STOCK'" class="styled-chk" />
                    </td>
                    <td class="center">
                      <span v-if="r.RECORD_GUBUN === 'INPUT'" class="badge badge-success">투입완료</span>
                      <span v-else class="badge badge-info">가용재고</span>
                    </td>
                    <td class="font-bold">{{ r.LOTNO || '-' }}</td>
                    <td>{{ r.PARTNO }}</td>
                    <td>{{ r.PARTNM }}</td>
                    <td class="center">{{ r.UNIT }}</td>
                    <td class="right font-bold text-success">{{ r.INPUT_QTY || 0 }}</td>
                    <td class="right text-muted">{{ r.NEED_QTY }}</td>
                    <td class="right font-bold">{{ r.STOCK_QTY || 0 }}</td>
                    <td><span class="loc-tag">{{ r.LOCATIONNAME }}</span></td>
                    <td class="center" @click.stop>
                      <button v-if="r.RECORD_GUBUN === 'INPUT'" class="btn-del-row" @click="$emit('delete', r)">삭제</button>
                    </td>
                  </tr>
                  <tr v-if="rows.length === 0">
                    <td colspan="11" class="empty-row">표시할 데이터가 없습니다.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <footer class="modal-footer">
          <div class="record-count">Total <b>{{ rows.length }}</b> items found</div>
          <div class="spacer"></div>
          <button class="btn-cancel" @click="$emit('close')">닫기</button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps<{
  visible: boolean;
  rows: any[];
}>();

const emit = defineEmits(['close', 'save', 'delete']);

const matInput = ref({ MAT_LOTNO: '', INPUT_QTY: 0 });

const isAllChecked = computed(() => {
  const stockRows = props.rows.filter(r => r.RECORD_GUBUN === 'STOCK');
  return stockRows.length > 0 && stockRows.every(r => r._checked);
});

function toggleAll() {
  const targetValue = !isAllChecked.value;
  props.rows.forEach(r => {
    if (r.RECORD_GUBUN === 'STOCK') r._checked = targetValue;
  });
}

function onRowClick(row: any) {
  if (row.RECORD_GUBUN === 'STOCK') {
    matInput.value.MAT_LOTNO = row.LOTNO;
    matInput.value.INPUT_QTY = row.STOCK_QTY;
  }
}

function save() {
  emit('save', { ...matInput.value });
  matInput.value = { MAT_LOTNO: '', INPUT_QTY: 0 };
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    matInput.value = { MAT_LOTNO: '', INPUT_QTY: 0 };
  }
});
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-container { background: #f8fafc; border-radius: 24px; max-width: 95vw; width: 1100px; height: 800px; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid #e2e8f0; overflow: hidden; }
@keyframes modalIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 32px; background: #fff; border-bottom: 1px solid #f1f5f9; }
.header-title-wrap { display: flex; align-items: center; gap: 16px; }
.header-icon { font-size: 1.6rem; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #eff6ff; border-radius: 14px; }
.title-text h3 { margin: 0; font-size: 1.25rem; font-weight: 800; color: #0f172a; }
.title-text .sub-title { margin: 2px 0 0 0; font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }

.header-actions { display: flex; align-items: center; gap: 16px; }
.btn-save-main { background: #2563eb; color: #fff; border: none; padding: 10px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.btn-save-main:hover { background: #1d4ed8; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
.btn-close-x { background: #f1f5f9; border: none; width: 40px; height: 40px; border-radius: 12px; font-size: 1.2rem; cursor: pointer; color: #94a3b8; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-close-x:hover { background: #fee2e2; color: #ef4444; transform: rotate(90deg); }

.modal-body { padding: 24px 32px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }

.info-card { background: #fff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.card-header { padding: 16px 24px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; gap: 10px; }
.card-header h4 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #334155; }
.dot { width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; }

.form-layout { padding: 24px; display: flex; align-items: flex-end; gap: 24px; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.82rem; font-weight: 700; color: #64748b; margin-left: 2px; }

.search-input-wrap { display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; width: 350px; transition: border-color 0.2s; }
.search-input-wrap:focus-within { border-color: #3b82f6; background: #fff; }
.search-input-wrap input { border: none; padding: 10px 16px; font-size: 0.95rem; flex: 1; outline: none; background: transparent; }
.btn-lookup-inner { background: #eff6ff; border: none; padding: 0 16px; height: 44px; color: #3b82f6; cursor: pointer; }

.qty-input { padding: 10px 16px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 1.1rem; font-weight: 800; color: #ef4444; width: 120px; text-align: right; outline: none; background: #f8fafc; }
.qty-input:focus { border-color: #ef4444; background: #fff; }

.tip-box { flex: 1; min-width: 300px; padding: 12px 20px; background: #f0f9ff; border-radius: 12px; border: 1px solid #bae6fd; }
.tip-box p { margin: 0; font-size: 0.85rem; color: #0369a1; line-height: 1.5; }

.grid-table-wrap { padding: 12px; }
.styled-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.85rem; }
.styled-table th { background: #f8fafc; padding: 12px 8px; text-align: center; font-weight: 700; color: #64748b; border-bottom: 2px solid #f1f5f9; }
.styled-table td { padding: 10px 8px; border-bottom: 1px solid #f1f5f9; cursor: pointer; }
.styled-table tr:hover td { background: #f8fafc; }

.row-input { background: #f0fdf4; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 800; }
.badge-success { background: #dcfce7; color: #166534; }
.badge-info { background: #e0f2fe; color: #0369a1; }

.font-bold { font-weight: 700; }
.center { text-align: center; }
.right { text-align: right; }
.text-success { color: #10b981; }
.text-muted { color: #94a3b8; }
.loc-tag { background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; color: #475569; }

.btn-del-row { background: #fff; color: #ef4444; border: 1px solid #fecaca; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-del-row:hover { background: #ef4444; color: #fff; }

.modal-footer { padding: 20px 32px; background: #fff; border-top: 1px solid #f1f5f9; display: flex; align-items: center; }
.record-count { font-size: 0.88rem; color: #64748b; }
.record-count b { color: #0f172a; }
.btn-cancel { background: #fff; color: #64748b; border: 1px solid #e2e8f0; padding: 10px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-cancel:hover { background: #f8fafc; border-color: #cbd5e1; }

.styled-chk { width: 16px; height: 16px; cursor: pointer; }
.empty-row { text-align: center; padding: 40px; color: #94a3b8; font-style: italic; }
</style>
