<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">검사성적서 현황</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="searchPlant" style="width:150px;">
          <option value="">(전체)</option>
          <option value="P001">(주)동우에이치티</option>
        </select>
        
        <label style="margin-left:20px;">성적서구분</label>
        <select v-model="searchTestGubun" style="width:150px;">
          <option value="">(전체)</option>
          <option value="1">일반검사</option>
          <option value="2">정밀검사</option>
        </select>
        
        <label style="margin-left:20px;">등록일자</label>
        <input type="date" v-model="searchStartDate" />
        <span>~</span>
        <input type="date" v-model="searchEndDate" />
      </div>
      <div class="search-row" style="margin-top: 10px;">
        <label>공정</label>
        <select v-model="searchProcess" style="width:150px;">
          <option value="">(선택하세요)</option>
          <option value="PRC01">조립공정</option>
          <option value="PRC02">검사공정</option>
        </select>
        
        <label style="margin-left:20px;">품번/품명</label>
        <input type="text" v-model="searchPart" style="width:150px;" @keyup.enter="fetchList" />
        <button class="btn-search-icon" title="품목 검색">🔍</button>
        
        <label style="margin-left:20px;">LOT NO</label>
        <input type="text" v-model="searchLotNo" style="width:150px;" @keyup.enter="fetchList" />
        
        <button class="btn-search" @click="fetchList">조회</button>
      </div>
    </section>

    <!-- ═══ 마스터 그리드 (검사성적서) ═══ -->
    <div class="grid-wrap" style="flex: 2;">
      <div class="toolbar">
        <div class="toolbar-title">검사성적서 목록</div>
        <button class="btn-print" @click="printSheet">🖨️ 성적서 출력</button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>성적서구분</th>
              <th>사업장</th>
              <th>품번</th>
              <th>품명</th>
              <th>공정</th>
              <th>라인</th>
              <th>LOT NO.</th>
              <th>주/야 구분</th>
              <th>종합판정</th>
              <th>등록자</th>
              <th>등록일자</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="testScores.length === 0">
              <td colspan="11" class="empty-msg">데이터가 없습니다.</td>
            </tr>
            <tr v-for="score in testScores" :key="score.CODE" 
                @click="selectScore(score)"
                :class="{ 'row-selected': selectedScore?.CODE === score.CODE }"
                class="clickable-row">
              <td class="text-center">{{ formatTestGubun(score.TESTGUBUN) }}</td>
              <td class="text-center">{{ formatPlant(score.PLANT) }}</td>
              <td class="text-center">{{ score.PARTNO }}</td>
              <td>{{ score.PARTNM }}</td>
              <td class="text-center">{{ score.PROD_CD === 'PRC01' ? '조립공정' : (score.PROD_CD === 'PRC02' ? '검사공정' : score.PROD_CD) }}</td>
              <td class="text-center">{{ score.LINE_CD }}</td>
              <td class="text-center">{{ score.LOT_NO }}</td>
              <td class="text-center">{{ score.AMPM === 1 ? '주간' : (score.AMPM === 2 ? '야간' : '') }}</td>
              <td class="text-center">
                <span :class="['badge', score.RESULT === 1 ? 'badge-ok' : (score.RESULT === 2 ? 'badge-ng' : '')]">
                  {{ score.RESULT === 1 ? '합격' : (score.RESULT === 2 ? '불합격' : '') }}
                </span>
              </td>
              <td class="text-center">{{ score.WRITERID }}</td>
              <td class="text-center">{{ score.WDATE }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ═══ 디테일 그리드 (검사항목 및 측정값) ═══ -->
    <div class="grid-wrap" style="flex: 1; margin-top: 10px;">
      <div class="toolbar">
        <div class="toolbar-title">검사항목별 측정 데이터 <span v-if="selectedScore" class="sel-info">[{{ selectedScore.CODE }}]</span></div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>검사구분</th>
              <th>검사항목</th>
              <th>검사기준</th>
              <th>검사도구</th>
              <th>주기</th>
              <th>X1</th>
              <th>X2</th>
              <th>X3</th>
              <th>X4</th>
              <th>X5</th>
              <th>XBAR</th>
              <th>RBAR</th>
              <th>판정</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="details.length === 0">
              <td colspan="13" class="empty-msg">측정 항목이 없습니다. 마스터를 선택해주세요.</td>
            </tr>
            <tr v-for="(item, idx) in details" :key="idx">
              <td class="text-center">{{ item.ITEMCODE === 'I01' ? '외관검사' : (item.ITEMCODE === 'I02' ? '치수검사' : item.ITEMCODE) }}</td>
              <td class="text-center">{{ item.BIGO }}</td> <!-- 원래 TESTITEM 컬럼이나 MOCK으로 BIGO 활용 -->
              <td class="text-center">{{ item.OUTWARDVALUE || item.DIMSVALUE }}</td>
              <td class="text-center">버니어캘리퍼스</td>
              <td class="text-center">{{ item.PERIOD }}</td>
              <!-- X1~X5는 현재 스키마에 없으므로 UI만 제공 -->
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
              <td class="text-center mock-value"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';

// 검색 조건
const searchPlant = ref('P001');
const searchTestGubun = ref('');
const searchProcess = ref('');
const searchPart = ref('');
const searchLotNo = ref('');
const searchStartDate = ref('');
const searchEndDate = ref('');

const testScores = ref<any[]>([]);
const selectedScore = ref<any>(null);
const details = ref<any[]>([]);

function formatTestGubun(code: string) {
  if (code === '1') return '일반검사';
  if (code === '2') return '정밀검사';
  return code;
}
function formatPlant(code: string) {
  if (code === 'P001') return '(주)동우에이치티';
  return code;
}

// 초기 한 달 범위 세팅
function initDateRange() {
  const end = new Date();
  const start = new Date();
  start.setMonth(start.getMonth() - 3);
  searchEndDate.value = end.toISOString().slice(0, 10);
  searchStartDate.value = start.toISOString().slice(0, 10);
}

async function fetchList() {
  try {
    selectedScore.value = null;
    details.value = [];
    const params: any = {};
    if (searchPlant.value) params.plant = searchPlant.value;
    if (searchTestGubun.value) params.test_gubun = searchTestGubun.value;
    if (searchProcess.value) params.prod_cd = searchProcess.value;
    if (searchPart.value) params.part_no_nm = searchPart.value;
    if (searchLotNo.value) params.lot_no = searchLotNo.value;
    if (searchStartDate.value) params.start_date = searchStartDate.value;
    if (searchEndDate.value) params.end_date = searchEndDate.value;

    const res = await api.get('/api/inspection/testscore', { params });
    testScores.value = Array.isArray(res.data) ? res.data : (res.data?.data || []);
  } catch (err) {
    console.error(err);
  }
}

async function selectScore(score: any) {
  selectedScore.value = score;
  try {
    // PCODE(기준서 코드)를 통해 검사항목 조회 (상세 데이터 대용)
    const res = await api.get(`/api/inspection/testscore/${score.PCODE}/details`);
    details.value = Array.isArray(res.data) ? res.data : (res.data?.data || []);
  } catch (err) {
    console.error(err);
  }
}

function printSheet() {
  if (!selectedScore.value) {
    alert("출력할 성적서를 먼저 선택하세요.");
    return;
  }
  alert(`[성적서 출력] CODE: ${selectedScore.value.CODE}\n실제 리포팅 툴과 연동될 위치입니다.`);
}

onMounted(() => {
  initDateRange();
  fetchList();
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); border-top: 4px solid #73b3a6; margin-bottom: 10px; }
.section-title { font-size: 1rem; font-weight: 700; color: #333; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #2c3e50; min-width: 70px; text-align: right;}
.search-row input[type=text], .search-row input[type=date], .search-row select { padding: 4px 8px; border: 1px solid #ccd1d1; border-radius: 2px; font-size: .85rem; }
.btn-search-icon { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 2px; padding: 3px 6px; cursor: pointer; }
.btn-search { background: #73b3a6; color: #fff; border: none; padding: 6px 20px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #f4f6f7; border-bottom: 1px solid #e5e8e8; }
.toolbar-title { font-weight: 700; color: #2c3e50; font-size: .95rem; }
.sel-info { color: #e67e22; font-size: 0.85rem; margin-left: 8px; }
.btn-print { background: #fff; color: #2c3e50; border: 1px solid #bdc3c7; padding: 4px 12px; border-radius: 4px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.table-container { flex: 1; overflow: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-table th { background: #eef2f5; color: #444; font-weight: 600; padding: 8px; border: 1px solid #dfe6e9; text-align: center; white-space: nowrap; position: sticky; top: 0; }
.data-table td { padding: 6px 8px; border: 1px solid #dfe6e9; vertical-align: middle; }
.text-center { text-align: center; }

.clickable-row { cursor: pointer; }
.clickable-row:hover { background-color: #f9fbfc; }
.row-selected { background-color: #e8f6f3 !important; font-weight: 600; }

.badge { padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
.badge-ok { background: #d4efdf; color: #196f3d; }
.badge-ng { background: #fadbd8; color: #943126; }

.mock-value { background-color: #fafafa; color: #aaa; }
.empty-msg { text-align: center; padding: 20px; color: #999; }
</style>
