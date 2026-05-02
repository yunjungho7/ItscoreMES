<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="reg-modal">
      <!-- 타이틀바 (SalesOrder 스타일) -->
      <div class="reg-header">
        <h2>작업 지시 등록</h2>
        <div class="reg-actions">
          <button class="btn-save" @click="$emit('save')"><span>💾</span> 저장</button>
          <button class="btn-close" @click="$emit('close')"><span>❌</span> 닫기</button>
        </div>
      </div>
      
      <!-- 폼 영역 -->
      <div class="reg-form">
        <div class="form-field">
          <label class="required">사업장</label>
          <select v-model="form.PLANTCD">
            <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
          </select>
        </div>
        <div class="form-field">
          <label class="required">작업지시일</label>
          <div class="input-with-btns">
            <input type="date" v-model="form.ORDDATE" />
            <label class="chk-label"><input type="checkbox" v-model="form.SAT" /> 토</label>
            <label class="chk-label"><input type="checkbox" v-model="form.SUN" /> 일</label>
          </div>
        </div>
        <div class="form-field">
          <label class="required">근무조</label>
          <select v-model="form.SHIFT">
            <option value="주간">주간</option>
            <option value="야간">야간</option>
          </select>
        </div>
        <div class="form-field">
          <label class="required">작지구분</label>
          <select v-model="form.ORDTYPE">
            <option value="일반">일반</option>
            <option value="긴급">긴급</option>
            <option value="재작업">재작업</option>
          </select>
        </div>
      </div>

      <!-- 그리드 툴바 -->
      <div class="reg-grid-header">
        <span>지시 품목 및 공정 구성</span>
        <div class="grid-btns">
          <button class="btn-row-add" @click="$emit('open-picker', 'grid')">📥 추가</button>
          <button class="btn-row-del" @click="$emit('remove-items')">✂️ 제거</button>
        </div>
      </div>

      <!-- 메인 그리드 -->
      <div class="reg-grid-wrap flex-1">
        <table class="reg-grid">
          <thead>
            <tr>
              <th style="width:32px"></th>
              <th style="width:100px">작업일자</th>
              <th style="width:120px" class="req-th">품번</th>
              <th style="width:160px">품목명</th>
              <th style="width:80px">규격</th>
              <th style="width:60px">단위</th>
              <th style="width:100px" class="req-th">공정</th>
              <th style="width:100px">라인</th>
              <th style="width:70px">근무조</th>
              <th style="width:80px" class="req-th">지시수량</th>
              <th style="width:60px">상태</th>
              <th style="width:80px">재고수량</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in items" :key="i" :class="{'selected-row': item._sel, 'parent-row': item._level === 0}">
              <td class="chk"><input type="checkbox" v-model="item._sel" /></td>
              <td><input type="date" v-model="item.ORDDATE" class="cell-input" /></td>
              <td>
                <div class="cell-input-with-btn">
                  <input type="text" v-model="item.PARTNO" class="cell-input" readonly />
                  <button class="btn-cell-search" @click="$emit('open-picker', 'grid', i)">🔍</button>
                </div>
              </td>
              <td><input type="text" v-model="item.PARTNM" class="cell-input" readonly /></td>
              <td><input type="text" v-model="item.STANDARD" class="cell-input" readonly /></td>
              <td><input type="text" v-model="item.UNIT" class="cell-input center" readonly /></td>
              <td>
                <select v-model="item.PROCESSCD" class="cell-input">
                  <option value="">선택</option>
                  <option v-for="pr in processes" :key="pr.PROCESSCD" :value="pr.PROCESSCD">{{ pr.PROCESSNM }}</option>
                </select>
              </td>
              <td>
                <select v-model="item.LINECD" class="cell-input">
                  <option value="">선택</option>
                  <option v-for="ln in lines" :key="ln.LINECD" :value="ln.LINECD">{{ ln.LINENM }}</option>
                </select>
              </td>
              <td>
                <select v-model="item.SHIFT" class="cell-input">
                  <option value="주간">주간</option>
                  <option value="야간">야간</option>
                </select>
              </td>
              <td><input type="number" v-model.number="item.ORDQTY" class="cell-input num req-val" /></td>
              <td class="center"><span class="status-badge">신규</span></td>
              <td class="num readonly">{{ item.STOCKQTY || 0 }}</td>
            </tr>
            <tr v-if="items.length === 0">
              <td colspan="12" class="empty">지시 품목을 추가하거나 생산계획에서 선택해 주세요.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps<{
  visible: boolean;
  form: any;
  items: any[];
  plants: any[];
  processes: any[];
  lines: any[];
}>();

const emit = defineEmits([
  'close', 
  'save', 
  'open-picker', 
  'remove-items'
]);
</script>

<style scoped>
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.reg-modal{background:#fff;border-radius:12px;width:1200px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
.reg-header{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:linear-gradient(135deg,#2c5f2d,#4a8c3f);color:#fff}
.reg-header h2{margin:0;font-size:1.15rem;font-weight:700}
.reg-actions{display:flex;gap:8px}
.btn-save{background:#2980b9;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:4px}
.btn-close{background:#c0392b;color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;gap:4px}

.reg-form{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 20px;padding:18px 24px;background:#fafbfc;border-bottom:1px solid #eee}
.form-field{display:flex;flex-direction:column;gap:5px}
.form-field label{font-size:.82rem;font-weight:600;color:#64748b}
.form-field label.required::before{content:'◎ ';color:#27ae60}
.form-field input,.form-field select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}
.input-with-btns{display:flex;gap:8px;align-items:center}
.chk-label{font-size:0.8rem;display:flex;align-items:center;gap:4px;white-space:nowrap}

.reg-grid-header{display:flex;justify-content:space-between;align-items:center;padding:10px 24px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.reg-grid-header span{font-size:.88rem;font-weight:700;color:#3a4a6b}
.grid-btns{display:flex;gap:6px}
.btn-row-add{background:#27ae60;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}
.btn-row-del{background:#e74c3c;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}

.reg-grid-wrap{flex:1;overflow:auto;min-height:300px}
.reg-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.reg-grid thead{position:sticky;top:0;z-index:2}
.reg-grid th{background:linear-gradient(180deg,#e8f5e9,#c8e6c9);color:#2e7d32;font-weight:600;padding:9px 8px;text-align:left;border-bottom:2px solid #a5d6a7;white-space:nowrap;font-size:.82rem}
.reg-grid th.req-th::before{content:'* ';color:#e74c3c}
.reg-grid td{padding:4px 4px;border-bottom:1px solid #f0f2f5}
.reg-grid .chk{text-align:center}

.cell-input{width:100%;padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:.83rem;background:#fff}
.cell-input[readonly]{background:#f8fafc;color:#94a3b8;border-color:#f0f2f5}
.req-val{border-color:#fecaca;background:#fff5f5;font-weight:700;color:#e74c3c}
.num{text-align:right}
.cell-input-with-btn{display:flex;gap:2px}
.cell-input-with-btn input{flex:1}
.btn-cell-search{background:#636e72;color:#fff;border:none;padding:0 6px;border-radius:4px;cursor:pointer;font-size:.8rem}

.parent-row{background:#f8fafc;font-weight:700}
.status-badge{background:#fff1f1;color:#dc2626;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;border:1px solid #fecaca}
.flex-1{flex:1}
.center{text-align:center}
.empty{text-align:center;padding:60px;color:#94a3b8}
</style>
