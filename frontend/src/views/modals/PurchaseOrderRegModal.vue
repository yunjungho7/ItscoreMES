<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="reg-modal">
      <!-- 타이틀바 -->
      <div class="reg-header">
        <h2>발주 등록</h2>
        <div class="reg-actions">
          <button class="btn-save" @click="handleSave"><span>💾</span> 저장</button>
          <button class="btn-close" @click="$emit('close')"><span>❌</span> 닫기</button>
        </div>
      </div>
      
      <!-- 폼 영역 -->
      <div class="reg-form">
        <div class="form-field">
          <label class="required">사업장</label>
          <div class="input-with-btn">
            <input type="text" :value="plantName" readonly placeholder="사업장 선택" />
            <button class="btn-search-sm" @click="$emit('open-plant-picker')">🔍</button>
          </div>
        </div>
        <div class="form-field">
          <label class="required">공급사(대표)</label>
          <div class="input-with-btn">
            <input type="text" v-model="form.COMPANYNM" readonly placeholder="공급사 선택" />
            <button class="btn-search-sm" @click="$emit('open-company-picker', -1)">🔍</button>
          </div>
        </div>
        <div class="form-field">
          <label class="required">납기요청일</label>
          <input type="date" v-model="form.ADOFREQDT" />
        </div>
        <div class="form-field">
          <label>비고</label>
          <input type="text" v-model="form.REMARK" placeholder="비고 입력" />
        </div>
      </div>

      <!-- 생산 품목 섹션 -->
      <div class="reg-grid-header">
        <span>생산 품목 선택</span>
        <div class="grid-btns">
          <button class="btn-row-add" @click="$emit('add-product')">📥 추가</button>
          <button class="btn-row-del" @click="$emit('remove-product')">✂️ 제거</button>
        </div>
      </div>
      <div class="reg-grid-wrap" style="max-height: 160px;">
        <table class="reg-grid">
          <thead>
            <tr>
              <th style="width:32px"></th>
              <th style="width:160px" class="req-th">품번</th>
              <th>품명</th>
              <th style="width:60px">단위</th>
              <th style="width:100px">규격</th>
              <th style="width:120px" class="req-th">발주대상수량</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p,i) in products" :key="i" :class="{selected: prodIdx === i}" @click="$emit('prod-click', p, i)">
              <td class="chk"><input type="checkbox" v-model="p.checked" @click.stop /></td>
              <td>
                <div class="cell-input-with-btn">
                  <input type="text" v-model="p.PARTNO" class="cell-input" readonly />
                  <button class="btn-cell-search" @click="$emit('open-product-picker', i)">🔍</button>
                </div>
              </td>
              <td><input type="text" v-model="p.PARTNM" class="cell-input" readonly /></td>
              <td><input type="text" v-model="p.UNIT" class="cell-input center" readonly /></td>
              <td><input type="text" v-model="p.STANDARD" class="cell-input" readonly /></td>
              <td><input type="number" v-model.number="p.QTY" class="cell-input num req-val" @input="$emit('refresh-materials')" /></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="splitter-bar">BOM 자재 자동 전개 내역</div>

      <!-- 자재 그리드 -->
      <div class="reg-grid-wrap flex-1">
        <table class="reg-grid">
          <thead>
            <tr>
              <th style="width:32px"><input type="checkbox" :checked="materials.length > 0 && materials.every(m=>m.checked)" @change="toggleAllMaterials" /></th>
              <th style="width:110px">자재품번</th>
              <th style="width:150px">품명</th>
              <th style="width:160px" class="req-th">공급사</th>
              <th style="width:50px">단위</th>
              <th style="width:80px">단가</th>
              <th style="width:110px">납기요청일</th>
              <th style="width:80px">필요</th>
              <th style="width:90px" class="req-th">발주수량</th>
              <th style="width:80px">재고</th>
              <th>비고</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m,i) in materials" :key="i" :class="{'checked-row': m.checked}">
              <td class="chk"><input type="checkbox" v-model="m.checked" /></td>
              <td class="font-bold">{{ m.PARTNO }}</td>
              <td>{{ m.PARTNM }}</td>
              <td>
                <div class="cell-input-with-btn">
                  <input type="text" v-model="m.COMPANYNM" class="cell-input" readonly />
                  <button class="btn-cell-search" @click="$emit('open-company-picker', i)">🔍</button>
                </div>
              </td>
              <td class="center">{{ m.UNIT }}</td>
              <td class="num">{{ m.UNIT_PRICE?.toLocaleString() }}</td>
              <td><input type="date" v-model="m.ADOFREQDT" class="cell-input" /></td>
              <td class="num">{{ m.NEEDQTY?.toLocaleString() }}</td>
              <td><input type="number" v-model.number="m.ORDERQTY" class="cell-input num req-val" /></td>
              <td class="num readonly">{{ m.STOCKQTY?.toLocaleString() }}</td>
              <td><input type="text" class="cell-input" /></td>
            </tr>
            <tr v-if="materials.length===0"><td colspan="11" class="empty">데이터가 없습니다.</td></tr>
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
  plantName: string;
  products: any[];
  materials: any[];
  prodIdx: number;
}>();

const emit = defineEmits([
  'close', 
  'save', 
  'open-plant-picker', 
  'open-company-picker', 
  'add-product', 
  'remove-product', 
  'open-product-picker', 
  'refresh-materials', 
  'prod-click'
]);

function handleSave() {
  emit('save');
}

function toggleAllMaterials(e: any) {
  const checked = e.target.checked;
  props.materials.forEach(m => m.checked = checked);
}
</script>

<style scoped>
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;display:flex;align-items:center;justify-content:center}
.reg-modal{background:#fff;border-radius:12px;width:1100px;max-height:90vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25);overflow:hidden}
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
.form-field input[readonly]{background:#f1f5f9;color:#64748b}

.input-with-btn{display:flex;gap:4px;align-items:center}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:6px;cursor:pointer;font-size:1rem;height:34px}

.reg-grid-header{display:flex;justify-content:space-between;align-items:center;padding:10px 24px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.reg-grid-header span{font-size:.88rem;font-weight:700;color:#3a4a6b}
.grid-btns{display:flex;gap:6px}
.btn-row-add{background:#27ae60;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}
.btn-row-del{background:#e74c3c;color:#fff;border:none;padding:6px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.82rem;display:flex;align-items:center;gap:4px}

.reg-grid-wrap{flex:1;overflow:auto;min-height:150px}
.reg-grid{width:100%;border-collapse:collapse;font-size:.83rem}
.reg-grid thead{position:sticky;top:0;z-index:2}
.reg-grid th{background:linear-gradient(180deg,#e8f5e9,#c8e6c9);color:#2e7d32;font-weight:600;padding:9px 8px;text-align:left;border-bottom:2px solid #a5d6a7;white-space:nowrap;font-size:.82rem}
.reg-grid th.req-th::before{content:'* ';color:#e74c3c}
.reg-grid td{padding:4px 4px;border-bottom:1px solid #f0f2f5}
.cell-input{width:100%;padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:.83rem;background:#fff}
.cell-input[readonly]{background:#f8fafc;color:#94a3b8;border-color:#f0f2f5}
.req-val{border-color:#fecaca;background:#fff5f5;font-weight:700;color:#e74c3c}
.num{text-align:right}
.cell-input-with-btn{display:flex;gap:2px}
.cell-input-with-btn input{flex:1}
.btn-cell-search{background:#636e72;color:#fff;border:none;padding:0 6px;border-radius:4px;cursor:pointer;font-size:.8rem}

.splitter-bar{padding:6px 24px;background:#f0f4ff;color:#1e40af;font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.checked-row td{background:#f0fdf4}
.flex-1{flex:1}
.center{text-align:center}
.font-bold{font-weight:700}
.empty{text-align:center;padding:40px;color:#94a3b8}
</style>
