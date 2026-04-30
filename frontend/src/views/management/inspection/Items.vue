<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">검사 항목 등록</div>
      <div class="search-row">
        <label>검사구분</label>
        <select v-model="searchInspTp">
          <option value="">(선택하세요)</option>
          <option v-for="c in codes.INSP_TP" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
        </select>
        
        <label>검사항목 그룹</label>
        <select v-model="searchItemGp">
          <option value="">(선택하세요)</option>
          <option v-for="c in codes.TEST_ITEM_GP" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
        </select>
        
        <label>검사항목</label>
        <input type="text" v-model="searchTestItem" style="width:200px;" @keyup.enter="fetchData" />
      </div>
      <div class="search-row" style="margin-top: 10px;">
        <label>검사도구</label>
        <input type="text" v-model="searchGauge" style="width:200px;" @keyup.enter="fetchData" />
        
        <label>검사기준</label>
        <input type="text" v-model="searchStandard" style="width:200px;" @keyup.enter="fetchData" />
        
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- ═══ 그리드 ═══ -->
    <div class="grid-wrap">
      <div class="toolbar">
        <div class="toolbar-title">검사항목 목록</div>
        <button class="btn-add" @click="addRow">➕ 추가</button>
      </div>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>검사구분</th>
              <th>검사항목 그룹</th>
              <th>검사항목</th>
              <th>검사도구</th>
              <th>검사기준</th>
              <th>불량유형</th>
              <th>불량원인</th>
              <th>사용여부</th>
              <th width="60">저장</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="rows.length === 0">
              <td colspan="9" class="empty-msg">데이터가 없습니다.</td>
            </tr>
            <tr v-for="(row, idx) in rows" :key="idx" :class="{ 'row-new': !row.CODE }">
              <td>
                <select v-model="row.ITEMGUBUN" class="grid-input">
                  <option value="">(선택)</option>
                  <option v-for="c in codes.INSP_TP" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
                </select>
              </td>
              <td>
                <select v-model="row.TESTITEMGP" class="grid-input">
                  <option value="">(선택)</option>
                  <option v-for="c in codes.TEST_ITEM_GP" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
                </select>
              </td>
              <td><input type="text" v-model="row.TESTITEM" class="grid-input" /></td>
              <td><input type="text" v-model="row.GAUGE" class="grid-input" /></td>
              <td><input type="text" v-model="row.STANDARD" class="grid-input" /></td>
              <td>
                <select v-model="row.FAILTYPE" class="grid-input">
                  <option value="">(선택)</option>
                  <option v-for="c in codes.FAIL_TYPE" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
                </select>
              </td>
              <td>
                <select v-model="row.FAILBREAKDOWN" class="grid-input">
                  <option value="">(선택)</option>
                  <option v-for="c in codes.FAIL_BREAKDOWN" :key="c.DTL_CD" :value="c.DTL_CD">{{ c.DTL_NM }}</option>
                </select>
              </td>
              <td class="text-center">
                <input type="checkbox" v-model="row.USEYN" />
              </td>
              <td class="text-center">
                <button class="btn-save" @click="saveRow(row)" title="저장">💾</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 간단한 페이징 -->
      <div class="pagination" v-if="tp > 1">
        <button :disabled="pg === 1" @click="pg--; fetchData()">&lt;</button>
        <span>{{ pg }} / {{ tp }}</span>
        <button :disabled="pg === tp" @click="pg++; fetchData()">&gt;</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';

// ── 공통코드 Mock / Fetch ──
const codes = ref({
  INSP_TP: [
    { DTL_CD: '1', DTL_NM: '수입검사' },
    { DTL_CD: '2', DTL_NM: '공정검사' },
    { DTL_CD: '3', DTL_NM: '출하검사' }
  ],
  TEST_ITEM_GP: [
    { DTL_CD: 'G1', DTL_NM: '외관검사' },
    { DTL_CD: 'G2', DTL_NM: '치수검사' },
    { DTL_CD: 'G3', DTL_NM: '성능검사' }
  ],
  FAIL_TYPE: [
    { DTL_CD: 'F1', DTL_NM: '파손' },
    { DTL_CD: 'F2', DTL_NM: '오염' },
    { DTL_CD: 'F3', DTL_NM: '치수불량' }
  ],
  FAIL_BREAKDOWN: [
    { DTL_CD: 'B1', DTL_NM: '작업자 부주의' },
    { DTL_CD: 'B2', DTL_NM: '설비 이상' },
    { DTL_CD: 'B3', DTL_NM: '자재 불량' }
  ]
});

// 검색 조건
const searchInspTp = ref('');
const searchItemGp = ref('');
const searchTestItem = ref('');
const searchGauge = ref('');
const searchStandard = ref('');

const rows = ref<any[]>([]);
const pg = ref(1), tp = ref(0);

async function fetchCodes() {
  try {
    // 실제 API 연동 시 주석 해제 (코드그룹 조회)
    // const res = await api.get('/api/master/common-code/details'); ...
  } catch {}
}

async function fetchData() {
  try {
    const p: any = { page: pg.value, size: 50 };
    if (searchInspTp.value) p.item_gubun = searchInspTp.value;
    if (searchItemGp.value) p.test_item_gp = searchItemGp.value;
    if (searchTestItem.value) p.test_item = searchTestItem.value;
    if (searchGauge.value) p.gauge = searchGauge.value;
    // (서버 검색 파라미터 맞춤)

    const r = await api.get('/api/inspection/items', { params: p });
    rows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } catch (err) {
    console.error(err);
  }
}

function addRow() {
  rows.value.unshift({
    CODE: '',
    ITEMGUBUN: '',
    TESTITEMGP: '',
    TESTITEM: '',
    GAUGE: '',
    STANDARD: '',
    FAILTYPE: '',
    FAILBREAKDOWN: '',
    USEYN: true
  });
}

async function saveRow(row: any) {
  if (!row.TESTITEM) {
    alert("검사항목을 입력하세요.");
    return;
  }
  try {
    const res = await api.post('/api/inspection/items', row);
    if (res.data.status === 'success') {
      alert("저장되었습니다.");
      if (!row.CODE) {
        row.CODE = res.data.code; // 새 코드 반영
      }
    }
  } catch (err: any) {
    alert("저장 실패: " + (err.response?.data?.message || err.message));
  }
}

onMounted(() => {
  fetchCodes();
  fetchData();
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); border-top: 4px solid #73b3a6; }
.section-title { font-size: 1rem; font-weight: 700; color: #333; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #2c3e50; min-width: 90px; }
.search-row input[type=text], .search-row select { padding: 4px 8px; border: 1px solid #ccd1d1; border-radius: 2px; font-size: .85rem; }
.btn-search { background: #73b3a6; color: #fff; border: none; padding: 6px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #f4f6f7; border-bottom: 1px solid #e5e8e8; }
.toolbar-title { font-weight: 700; color: #2c3e50; font-size: .95rem; }
.btn-add { background: #bdc3c7; color: #333; border: none; padding: 4px 12px; border-radius: 4px; font-weight: 600; cursor: pointer; }

.table-container { flex: 1; overflow: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-table th { background: #eef2f5; color: #444; font-weight: 600; padding: 8px; border: 1px solid #dfe6e9; text-align: center; white-space: nowrap; }
.data-table td { padding: 4px; border: 1px solid #dfe6e9; vertical-align: middle; }
.text-center { text-align: center; }

.grid-input { width: 100%; box-sizing: border-box; padding: 4px; border: 1px solid transparent; font-size: 0.85rem; background: transparent; }
.grid-input:focus { border-color: #73b3a6; outline: none; background: #fff; }
select.grid-input { cursor: pointer; }

.row-new { background-color: #fdfefe; }
.empty-msg { text-align: center; padding: 20px; color: #999; }

.btn-save { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 1rem; }
.btn-save:hover { background: #dfe6e9; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 10px; padding: 10px; background: #fbfcfc; border-top: 1px solid #ecf0f1; }
.pagination button { padding: 4px 10px; border: 1px solid #dcdde1; background: #fff; cursor: pointer; border-radius: 4px; }
.pagination button:disabled { background: #f5f6fa; cursor: not-allowed; color: #a4b0be; }
</style>
