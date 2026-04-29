<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">기준서관리</div>
      <div class="search-row">
        <label>품번/품명</label>
        <input type="text" v-model="searchPart" style="width:200px;" @keyup.enter="fetchStandards" />
        <button class="btn-search-icon" title="품목 검색">🔍</button>
        
        <label style="margin-left:20px;">품목구분</label>
        <select v-model="searchGubun">
          <option value="">(선택하세요)</option>
          <option v-for="code in partTypes" :key="code.CODECD" :value="code.CODECD">{{ code.CODENM }}</option>
        </select>
        
        <button class="btn-search" @click="fetchStandards">조회</button>
      </div>
    </section>

    <!-- ═══ 마스터 그리드 (최신 기준서) ═══ -->
    <div class="grid-wrap" style="flex: 2;">
      <div class="toolbar">
        <div class="toolbar-title">최신 기준서 목록</div>
        <button class="btn-add" @click="openModal">📝 기준서 등록</button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>품번</th>
              <th>품명</th>
              <th>품목구분</th>
              <th>공정</th>
              <th>Rev.번호</th>
              <th>제/개정일</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="standards.length === 0">
              <td colspan="6" class="empty-msg">데이터가 없습니다.</td>
            </tr>
            <tr v-for="std in standards" :key="std.CODE" 
                @click="selectStandard(std)"
                :class="{ 'row-selected': selectedStd?.CODE === std.CODE }"
                class="clickable-row">
              <td class="text-center">{{ std.PARTNO }}</td>
              <td>{{ std.PARTNM }}</td>
              <td class="text-center">{{ formatGubun(std.PARTTYPE) }}</td>
              <td class="text-center">{{ std.PROCESSCD === 'PRC01' ? '조립공정' : (std.PROCESSCD === 'PRC02' ? '검사공정' : std.PROCESSCD) }}</td>
              <td class="text-center">{{ std.REVNO }}</td>
              <td class="text-center">{{ std.WDAY }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ═══ 디테일 그리드 (개정 이력) ═══ -->
    <div class="grid-wrap" style="flex: 1; margin-top: 10px;">
      <div class="toolbar">
        <div class="toolbar-title">개정이력현황 <span v-if="selectedStd" class="sel-info">[{{ selectedStd.PARTNO }}]</span></div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Rev.번호</th>
              <th>개정일자</th>
              <th>개정내용</th>
              <th>사업장</th>
              <th>품번</th>
              <th>품명</th>
              <th>품목구분</th>
              <th>공정</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="history.length === 0">
              <td colspan="8" class="empty-msg">개정 이력이 없습니다. 마스터를 선택해주세요.</td>
            </tr>
            <tr v-for="h in history" :key="h.CODE">
              <td class="text-center">{{ h.REVNO }}</td>
              <td class="text-center">{{ h.WDAY }}</td>
              <td>{{ h.REVCONT }}</td>
              <td class="text-center">{{ h.PLANTCD }}</td>
              <td class="text-center">{{ h.PARTNO }}</td>
              <td>{{ h.PARTNM }}</td>
              <td class="text-center">{{ formatGubun(h.PARTTYPE) }}</td>
              <td class="text-center">{{ h.PROCESSCD === 'PRC01' ? '조립공정' : (h.PROCESSCD === 'PRC02' ? '검사공정' : h.PROCESSCD) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 등록/개정 모달 -->
    <StandardRegModal 
      :is-open="isModalOpen" 
      :part-no="selectedStd?.PARTNO"
      :process-cd="selectedStd?.PROCESSCD"
      @close="isModalOpen = false" 
      @saved="onModalSaved" 
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../../../api';
import StandardRegModal from './StandardRegModal.vue';

const searchPart = ref('');
const searchGubun = ref('');

const standards = ref<any[]>([]);
const selectedStd = ref<any>(null);
const history = ref<any[]>([]);

const isModalOpen = ref(false);
const allCodes = ref<any[]>([]);
const partTypes = computed(() => allCodes.value.filter(c => c.PAR_CODECD === 'PARTGUBUN000').sort((a,b) => a.ORD - b.ORD));

function formatGubun(code: string) {
  if (!code) return '';
  const found = partTypes.value.find(c => c.CODECD === code);
  if (found) return found.CODENM;
  // 기존 숫자 코드 호환
  if(code === '1') return '제품';
  if(code === '2') return '반제품';
  if(code === '3') return '원자재';
  return code;
}

async function fetchStandards() {
  try {
    selectedStd.value = null;
    history.value = [];
    const params: any = {};
    if (searchPart.value) params.part_no_nm = searchPart.value;
    if (searchGubun.value) params.part_gubun = searchGubun.value;

    const res = await api.get('/api/inspection/standard', { params });
    standards.value = res.data;
  } catch (err) {
    console.error(err);
  }
}

async function selectStandard(std: any) {
  selectedStd.value = std;
  try {
    const res = await api.get(`/api/inspection/standard/${std.PARTNO}/history`, {
      params: { process_cd: std.PROCESSCD }
    });
    history.value = res.data;
  } catch (err) {
    console.error(err);
  }
}

function openModal() {
  isModalOpen.value = true;
}

function onModalSaved() {
  fetchStandards();
}

async function fetchCodes() {
  try {
    const r = await api.get('/api/master/code', { params: { size: 9999 } });
    allCodes.value = r.data.data || [];
  } catch {}
}

onMounted(() => {
  fetchCodes().then(fetchStandards);
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); border-top: 4px solid #73b3a6; margin-bottom: 10px; }
.section-title { font-size: 1rem; font-weight: 700; color: #333; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #2c3e50; min-width: 70px; }
.search-row input[type=text], .search-row select { padding: 4px 8px; border: 1px solid #ccd1d1; border-radius: 2px; font-size: .85rem; }
.btn-search-icon { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 2px; padding: 3px 6px; cursor: pointer; }
.btn-search { background: #73b3a6; color: #fff; border: none; padding: 6px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #f4f6f7; border-bottom: 1px solid #e5e8e8; }
.toolbar-title { font-weight: 700; color: #2c3e50; font-size: .95rem; }
.sel-info { color: #e67e22; font-size: 0.85rem; margin-left: 8px; }
.btn-add { background: #3498db; color: #fff; border: none; padding: 4px 12px; border-radius: 4px; font-weight: 600; cursor: pointer; }

.table-container { flex: 1; overflow: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-table th { background: #eef2f5; color: #444; font-weight: 600; padding: 8px; border: 1px solid #dfe6e9; text-align: center; white-space: nowrap; position: sticky; top: 0; }
.data-table td { padding: 6px 8px; border: 1px solid #dfe6e9; vertical-align: middle; }
.text-center { text-align: center; }

.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f9fbfc; }
.row-selected { background-color: #e8f6f3 !important; font-weight: 600; }

.empty-msg { text-align: center; padding: 20px; color: #999; }
</style>
