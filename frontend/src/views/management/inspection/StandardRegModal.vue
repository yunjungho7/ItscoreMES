<template>
  <div class="modal-overlay" v-if="isOpen">
    <div class="modal-content">
      <div class="modal-header">
        <h2>기준서 초기등록</h2>
        <div class="header-buttons">
          <button class="btn-save" @click="saveStandard">💾 저장</button>
          <button class="btn-close" @click="closeModal">❌ 닫기</button>
        </div>
      </div>
      
      <div class="modal-body">
        <!-- 마스터 정보 -->
        <section class="master-section">
          <div class="form-row">
            <label>Rev.No</label>
            <input type="text" v-model="master.REVNO" disabled class="input-disabled" style="width:100px;" />
            <label style="margin-left:20px;">등록일자</label>
            <input type="date" v-model="master.WDAY" />
          </div>
          <div class="form-row">
            <label>품번/품명</label>
            <input type="text" v-model="master.PARTNO" placeholder="품번" style="width:150px;" />
            <input type="text" v-model="master.PARTNM" placeholder="품명" disabled class="input-disabled" style="width:150px; margin-left:4px;" />
            <button class="btn-search-icon" @click="openPartSearch" title="품목 검색">🔍</button>
            <label style="margin-left:20px;">공정</label>
            <select v-model="master.PROCESSCD">
              <option value="PRC01">조립공정</option>
              <option value="PRC02">검사공정</option>
            </select>
          </div>
          <div class="form-row">
            <label>비고</label>
            <textarea v-model="master.BIGO" rows="2" style="flex:1; resize:none;"></textarea>
          </div>
          <div class="form-row">
            <label>개정내용</label>
            <textarea v-model="master.REVCONT" rows="2" style="flex:1; resize:none;"></textarea>
          </div>
          <div class="form-row">
            <label>기준서 이미지</label>
            <input type="text" v-model="imageFile" placeholder="이미지 파일명 또는 경로" style="flex:1;" />
          </div>
        </section>

        <!-- 디테일 툴바 -->
        <div class="detail-toolbar">
          <button class="btn-action">📄 가져오기</button>
          <button class="btn-action" @click="addItem">➕ 추가</button>
          <button class="btn-action" @click="removeItem">✂️ 제거</button>
        </div>

        <!-- 디테일 그리드 -->
        <div class="detail-grid">
          <table class="data-table">
            <thead>
              <tr>
                <th width="40">선택</th>
                <th>항목NO</th>
                <th>검사구분</th>
                <th>초중종</th>
                <th>자주검사</th>
                <th>검사항목</th>
                <th>검사도구</th>
                <th>검사기준(정성)</th>
                <th>시료수</th>
                <th>주기</th>
                <th>단위</th>
                <th>기준값(정량)</th>
                <th>상한(+)</th>
                <th>하한(-)</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in items" :key="idx">
                <td class="text-center">
                  <input type="checkbox" v-model="item._selected" />
                </td>
                <td class="text-center">{{ idx + 1 }}</td>
                <td>
                  <select v-model="item.ITEMCODE" class="grid-input">
                    <option value="">(선택)</option>
                    <option value="I01">외관검사</option>
                    <option value="I02">치수검사</option>
                  </select>
                </td>
                <td class="text-center"><input type="checkbox" v-model="item.CHOYN" /></td>
                <td class="text-center"><input type="checkbox" v-model="item.SELFYN" /></td>
                <td><input type="text" v-model="item.TESTITEM_NM" class="grid-input" placeholder="(참조용)항목명" /></td>
                <td><input type="text" v-model="item.GAUGE" class="grid-input" /></td>
                <td><input type="text" v-model="item.OUTWARDVALUE" class="grid-input" /></td>
                <td><input type="number" v-model="item.SAMPLEQTY" class="grid-input" style="width:60px;" /></td>
                <td><input type="text" v-model="item.PERIOD" class="grid-input" /></td>
                <td><input type="text" v-model="item.UNIT" class="grid-input" style="width:60px;" /></td>
                <td><input type="number" step="0.01" v-model="item.DIMSVALUE" class="grid-input" style="width:80px;" /></td>
                <td><input type="number" step="0.01" v-model="item.PLUS" class="grid-input" style="width:80px;" /></td>
                <td><input type="number" step="0.01" v-model="item.MINUS" class="grid-input" style="width:80px;" /></td>
                <td><input type="text" v-model="item.BIGO" class="grid-input" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../../../api';

const props = defineProps<{ isOpen: boolean, partNo?: string, processCd?: string }>();
const emit = defineEmits(['close', 'saved']);

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
const imageFile = ref('');

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // 팝업 열릴 때 초기화
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
    imageFile.value = '';
    
    // 신규 등록이 아닌, 품번을 받아오는 경우라면 서버에서 REVNO 등을 세팅할 수도 있음.
  }
});

function closeModal() {
  emit('close');
}

function openPartSearch() {
  // 실제 프로젝트라면 품목 검색 팝업 호출
  alert("품목 검색 팝업 호출 예정");
}

function addItem() {
  items.value.push({
    _selected: false,
    ITEMCODE: '',
    CHOYN: false,
    SELFYN: false,
    TESTITEM_NM: '',
    GAUGE: '',
    OUTWARDVALUE: '',
    SAMPLEQTY: 0,
    PERIOD: '',
    UNIT: '',
    DIMSVALUE: 0,
    PLUS: 0,
    MINUS: 0,
    BIGO: ''
  });
}

function removeItem() {
  items.value = items.value.filter(it => !it._selected);
}

async function saveStandard() {
  if (!master.value.PARTNO) {
    alert("품번을 입력해주세요.");
    return;
  }
  
  const payload = {
    master: {
      PARTNO: master.value.PARTNO,
      PROCESSCD: master.value.PROCESSCD,
      WDAY: master.value.WDAY,
      REVCONT: master.value.REVCONT,
      BIGO: master.value.BIGO
    },
    items: items.value.map((it, idx) => ({
      ITEMCODE: it.ITEMCODE,
      ITEMSTEP: idx + 1,
      CHOYN: it.CHOYN,
      SELFYN: it.SELFYN,
      SAMPLEQTY: it.SAMPLEQTY,
      PERIOD: it.PERIOD,
      UNIT: it.UNIT,
      OUTWARDVALUE: it.OUTWARDVALUE,
      DIMSVALUE: it.DIMSVALUE || null,
      PLUS: it.PLUS || null,
      MINUS: it.MINUS || null,
      BIGO: it.BIGO
    }))
  };

  try {
    const res = await api.post('/api/inspection/standard', payload);
    if (res.data.status === 'success') {
      alert("성공적으로 저장되었습니다.");
      emit('saved');
      closeModal();
    }
  } catch (err: any) {
    alert("저장 오류: " + (err.response?.data?.message || err.message));
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-content {
  background: #fff; width: 1200px; max-width: 95vw; height: 80vh; max-height: 900px;
  border-radius: 6px; display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.modal-header {
  background: #73b3a6; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;
}
.modal-header h2 { margin: 0; font-size: 1.1rem; color: #fff; }
.header-buttons button { margin-left: 8px; padding: 6px 12px; border: 1px solid rgba(255,255,255,0.4); border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-save { background: #fff; color: #2c3e50; }
.btn-close { background: #e74c3c; color: #fff; border: none; }

.modal-body {
  flex: 1; padding: 16px; display: flex; flex-direction: column; gap: 16px; overflow: hidden; background: #fdfdfd;
}

.master-section {
  background: #f4f6f7; border: 1px solid #d5dbdb; padding: 12px; border-radius: 4px; display: flex; flex-direction: column; gap: 8px;
}
.form-row { display: flex; align-items: center; gap: 8px; }
.form-row label { width: 100px; text-align: right; font-size: 0.85rem; font-weight: bold; color: #2c3e50; margin-right: 8px; }
.form-row input, .form-row select, .form-row textarea { padding: 4px 8px; border: 1px solid #bdc3c7; border-radius: 2px; font-size: 0.85rem; }
.input-disabled { background: #eaeded; color: #7f8c8d; }
.btn-search-icon { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 2px; padding: 3px 6px; cursor: pointer; }

.detail-toolbar { display: flex; justify-content: flex-end; gap: 8px; padding-bottom: 8px; border-bottom: 2px solid #eaeded; }
.btn-action { background: #ecf0f1; border: 1px solid #bdc3c7; padding: 4px 10px; border-radius: 3px; font-weight: bold; cursor: pointer; font-size: 0.85rem; }

.detail-grid { flex: 1; overflow: auto; border: 1px solid #d5dbdb; background: #fff; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.data-table th { background: #eaeded; color: #333; padding: 6px; border: 1px solid #d5dbdb; position: sticky; top: 0; z-index: 1; }
.data-table td { border: 1px solid #eaeded; padding: 2px; text-align: center; }
.text-center { text-align: center; }
.grid-input { width: 100%; box-sizing: border-box; padding: 4px; border: 1px solid transparent; font-size: 0.8rem; }
.grid-input:focus { border: 1px solid #73b3a6; outline: none; }
</style>
