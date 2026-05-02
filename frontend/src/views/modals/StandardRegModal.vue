<template>
  <div class="modal-overlay" v-if="isOpen" @click.self="closeModal">
    <div class="modal-container standard-modal">
      <header class="modal-header">
        <div class="header-title-wrap">
          <span class="header-icon">📝</span>
          <div class="title-text">
            <h3>기준서 초기등록</h3>
            <p class="sub-title">Inspection Standard Registration</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-save-main" @click="saveStandard">💾 저장하기</button>
          <button class="btn-close-x" @click="closeModal">✕</button>
        </div>
      </header>
      
      <div class="modal-body">
        <!-- 마스터 정보 카드 -->
        <section class="info-card master-card">
          <div class="card-header">
            <span class="dot"></span>
            <h4>기본 정보</h4>
          </div>
          <div class="form-grid-layout">
            <div class="form-group">
              <label>Rev.No</label>
              <input type="text" v-model="master.REVNO" disabled class="input-disabled" />
            </div>
            <div class="form-group">
              <label>등록일자</label>
              <input type="date" v-model="master.WDAY" />
            </div>
            <div class="form-group span-2">
              <label>품번/품명</label>
              <div class="search-input-group">
                <input type="text" v-model="master.PARTNO" placeholder="품번" class="part-no" />
                <input type="text" v-model="master.PARTNM" placeholder="자동입력 품명" disabled class="input-disabled part-nm" />
                <button class="btn-lookup" @click="openPartSearch" title="품목 검색">🔍</button>
              </div>
            </div>
            <div class="form-group">
              <label>공정</label>
              <select v-model="master.PROCESSCD">
                <option value="PRC01">조립공정</option>
                <option value="PRC02">검사공정</option>
              </select>
            </div>
            <div class="form-group span-3">
              <label>비고</label>
              <input type="text" v-model="master.BIGO" placeholder="추가 참고사항" />
            </div>
            <div class="form-group span-3">
              <label>개정내용</label>
              <input type="text" v-model="master.REVCONT" placeholder="금번 개정 사유 및 내용" />
            </div>
          </div>
        </section>

        <!-- 디테일 내역 카드 -->
        <section class="info-card detail-card">
          <div class="card-header">
            <div class="header-left">
              <span class="dot"></span>
              <h4>검사 항목 설정</h4>
            </div>
            <div class="header-right">
              <button class="btn-tool" @click="addItem"><span>➕</span> 항목추가</button>
              <button class="btn-tool danger" @click="removeItem"><span>✂️</span> 항목삭제</button>
            </div>
          </div>

          <div class="grid-table-wrap">
            <table class="styled-table">
              <thead>
                <tr>
                  <th width="40"></th>
                  <th width="50">NO</th>
                  <th width="120">검사구분</th>
                  <th width="70">초중종</th>
                  <th width="70">자주</th>
                  <th>검사항목</th>
                  <th width="100">검사도구</th>
                  <th width="120">기준(정성)</th>
                  <th width="80">시료수</th>
                  <th width="100">주기</th>
                  <th width="80">단위</th>
                  <th width="90">기준(정량)</th>
                  <th width="80">상한(+)</th>
                  <th width="80">하한(-)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in items" :key="idx" :class="{ 'row-selected': item._selected }">
                  <td class="center"><input type="checkbox" v-model="item._selected" /></td>
                  <td class="center font-bold">{{ idx + 1 }}</td>
                  <td>
                    <select v-model="item.ITEMCODE" class="cell-select">
                      <option value="">선택</option>
                      <option value="I01">외관검사</option>
                      <option value="I02">치수검사</option>
                    </select>
                  </td>
                  <td class="center"><input type="checkbox" v-model="item.CHOYN" class="styled-chk" /></td>
                  <td class="center"><input type="checkbox" v-model="item.SELFYN" class="styled-chk" /></td>
                  <td><input type="text" v-model="item.TESTITEM_NM" class="cell-input" /></td>
                  <td><input type="text" v-model="item.GAUGE" class="cell-input" /></td>
                  <td><input type="text" v-model="item.OUTWARDVALUE" class="cell-input" /></td>
                  <td><input type="number" v-model="item.SAMPLEQTY" class="cell-input right" /></td>
                  <td><input type="text" v-model="item.PERIOD" class="cell-input" /></td>
                  <td><input type="text" v-model="item.UNIT" class="cell-input center" /></td>
                  <td><input type="number" step="0.01" v-model="item.DIMSVALUE" class="cell-input right font-bold" /></td>
                  <td><input type="number" step="0.01" v-model="item.PLUS" class="cell-input right" /></td>
                  <td><input type="number" step="0.01" v-model="item.MINUS" class="cell-input right" /></td>
                </tr>
                <tr v-if="items.length === 0">
                  <td colspan="14" class="empty-row">추가 버튼을 눌러 검사 항목을 등록하세요.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
      
      <footer class="modal-footer">
        <div class="tip">※ 품목과 공정을 선택한 후 세부 검사 항목을 구성해 주세요.</div>
        <div class="spacer"></div>
        <button class="btn-cancel" @click="closeModal">취소</button>
        <button class="btn-save-bottom" @click="saveStandard">저장 완료</button>
      </footer>
    </div>
    
    <ItemPicker 
      :visible="showItemPicker" 
      :initial-search="master.PARTNO"
      @close="showItemPicker = false"
      @select="onItemSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../../api';
import ItemPicker from '../pickers/ItemPicker.vue';

const props = defineProps<{ isOpen: boolean, partNo?: string, processCd?: string }>();
const emit = defineEmits(['close', 'saved']);

const showItemPicker = ref(false);

const master = ref<any>({
  REVNO: 0,
  WDAY: new Date().toISOString().slice(0, 10),
  PARTNO: '',
  PARTNM: '',
  PROCESSCD: 'PRC01',
  BIGO: '',
  REVCONT: ''
});
const items = ref<any[]>([]);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    master.value = {
      REVNO: 0,
      WDAY: new Date().toISOString().slice(0, 10),
      PARTNO: props.partNo || '',
      PARTNM: '',
      PROCESSCD: props.processCd || 'PRC01',
      BIGO: '',
      REVCONT: ''
    };
    items.value = [];
  }
});

function closeModal() { emit('close'); }
function openPartSearch() { showItemPicker.value = true; }
function onItemSelect(item: any) { master.value.PARTNO = item.PARTNO; master.value.PARTNM = item.PARTNM; }

function addItem() {
  items.value.push({
    _selected: false, ITEMCODE: '', CHOYN: false, SELFYN: false, TESTITEM_NM: '', GAUGE: '',
    OUTWARDVALUE: '', SAMPLEQTY: 0, PERIOD: '', UNIT: '', DIMSVALUE: 0, PLUS: 0, MINUS: 0, BIGO: ''
  });
}
function removeItem() { items.value = items.value.filter(it => !it._selected); }

async function saveStandard() {
  if (!master.value.PARTNO) { alert("품번을 입력해주세요."); return; }
  const payload = {
    master: { ...master.value },
    items: items.value.map((it, idx) => ({ ...it, ITEMSTEP: idx + 1 }))
  };
  try {
    const res = await api.post('/api/inspection/standard', payload);
    if (res.data.status === 'success') {
      alert("성공적으로 저장되었습니다.");
      emit('saved');
      closeModal();
    }
  } catch (err: any) { alert("저장 오류: " + (err.response?.data?.message || err.message)); }
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-container { background: #f8fafc; border-radius: 24px; max-width: 95vw; width: 1300px; height: 850px; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid #e2e8f0; overflow: hidden; }
@keyframes modalIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 32px; background: #fff; border-bottom: 1px solid #f1f5f9; }
.header-title-wrap { display: flex; align-items: center; gap: 16px; }
.header-icon { font-size: 1.6rem; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #f1f5f9; border-radius: 14px; }
.title-text h3 { margin: 0; font-size: 1.25rem; font-weight: 800; color: #0f172a; }
.title-text .sub-title { margin: 2px 0 0 0; font-size: 0.75rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }

.header-actions { display: flex; align-items: center; gap: 16px; }
.btn-save-main { background: #0f172a; color: #fff; border: none; padding: 10px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-save-main:hover { background: #1e293b; transform: translateY(-1px); }
.btn-close-x { background: #f1f5f9; border: none; width: 40px; height: 40px; border-radius: 12px; font-size: 1.2rem; cursor: pointer; color: #94a3b8; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-close-x:hover { background: #fee2e2; color: #ef4444; transform: rotate(90deg); }

.modal-body { padding: 24px 32px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }

.info-card { background: #fff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.card-header { padding: 16px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.card-header .header-left { display: flex; align-items: center; gap: 10px; }
.card-header h4 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #334155; }
.dot { width: 8px; height: 8px; background: #6366f1; border-radius: 50%; }

.form-grid-layout { padding: 20px 24px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px 24px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group.span-2 { grid-column: span 2; }
.form-group.span-3 { grid-column: span 3; }
.form-group label { font-size: 0.82rem; font-weight: 700; color: #64748b; margin-left: 2px; }
.form-group input, .form-group select { padding: 9px 14px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem; color: #1e293b; outline: none; transition: border-color 0.2s; }
.form-group input:focus { border-color: #6366f1; }
.input-disabled { background: #f8fafc; color: #94a3b8; }

.search-input-group { display: flex; align-items: center; gap: 8px; }
.search-input-group .part-no { width: 140px; }
.search-input-group .part-nm { flex: 1; }
.btn-lookup { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; width: 38px; height: 38px; cursor: pointer; transition: all 0.2s; }
.btn-lookup:hover { background: #e2e8f0; }

.header-right { display: flex; gap: 8px; }
.btn-tool { background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; color: #475569; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-tool:hover { background: #fff; border-color: #cbd5e1; transform: translateY(-1px); }
.btn-tool.danger:hover { color: #ef4444; border-color: #fecaca; background: #fff1f1; }

.grid-table-wrap { overflow-x: auto; padding: 12px; }
.styled-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.85rem; }
.styled-table th { background: #f8fafc; padding: 12px 8px; text-align: center; font-weight: 700; color: #64748b; border-bottom: 2px solid #f1f5f9; white-space: nowrap; position: sticky; top: 0; }
.styled-table td { padding: 6px 4px; border-bottom: 1px solid #f1f5f9; transition: background 0.2s; }
.styled-table tr:hover td { background: #fbfcfe; }
.styled-table .row-selected td { background: #f5f3ff; }

.cell-input, .cell-select { width: 100%; border: 1px solid transparent; background: transparent; padding: 6px 8px; border-radius: 6px; font-size: 0.85rem; transition: all 0.2s; }
.cell-input:focus, .cell-select:focus { background: #fff; border-color: #c7d2fe; box-shadow: 0 0 0 3px rgba(199, 210, 254, 0.3); outline: none; }
.center { text-align: center; }
.right { text-align: right; }
.font-bold { font-weight: 700; }
.styled-chk { width: 16px; height: 16px; cursor: pointer; }
.empty-row { text-align: center; padding: 40px; color: #94a3b8; font-style: italic; }

.modal-footer { padding: 20px 32px; background: #fff; border-top: 1px solid #f1f5f9; display: flex; align-items: center; }
.tip { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }
.btn-cancel { background: #fff; color: #64748b; border: 1px solid #e2e8f0; padding: 10px 24px; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-cancel:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-save-bottom { background: #6366f1; color: #fff; border: none; padding: 10px 32px; border-radius: 12px; font-weight: 700; cursor: pointer; margin-left: 12px; transition: all 0.2s; box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4); }
.btn-save-bottom:hover { background: #4f46e5; transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4); }
</style>
