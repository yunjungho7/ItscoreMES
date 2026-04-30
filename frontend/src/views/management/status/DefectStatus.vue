<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">불량현황</div>
      <div class="search-row">
        <label>일자</label>
        <input type="date" v-model="startDate" />
        <span>~</span>
        <input type="date" v-model="endDate" />
        
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        
        <label>처리상태</label>
        <select v-model="processStatus">
          <option value="전체">전체</option>
          <option value="대기">대기</option>
          <option value="처리완료">처리완료</option>
        </select>
      </div>
      <div class="search-row" style="margin-top: 10px;">
        <label>LOT No.</label>
        <input type="text" v-model="searchLotNo" placeholder="LOT No 입력" @keyup.enter="fetchData" />
        
        <label>품번</label>
        <input type="text" v-model="searchPartNo" placeholder="품번 입력" @keyup.enter="fetchData" />
        
        <button class="btn-search" @click="fetchData">조회</button>
      </div>
    </section>

    <!-- ═══ 그리드 ═══ -->
    <div class="grid-wrap">
      <div class="toolbar">
        <div class="toolbar-title">불량 이력 전체 조회</div>
      </div>
      <DataGrid :columns="cols" :rows="rows" :loading="ld" :selectedIndex="si"
                :page="pg" :totalPages="tp" :total="tot"
                @row-click="onRow" @page-change="onPg">
        <template #cell-PROCESS_STATUS="{ row }">
          <span :class="['status-badge', row.PROCESS_STATUS === '처리완료' ? 'status-done' : 'status-wait']">
            {{ row.PROCESS_STATUS }}
          </span>
        </template>
      </DataGrid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

// ── 날짜 설정 ──
const d = new Date(), m1 = new Date(d); m1.setMonth(m1.getMonth() - 1);
const f = (v: Date) => v.toISOString().slice(0, 10);

const startDate = ref(f(m1)), endDate = ref(f(d));
const plantCd = ref(''), searchLotNo = ref(''), searchPartNo = ref('');
const processStatus = ref('전체');
const plants = ref<any[]>([]);

// ── 컬럼 정의 ──
const cols = [
  { key: 'REGDATE', label: '등록일자', width: '100px', align: 'center' },
  { key: 'PROCESS_STATUS', label: '처리상태', width: '80px', align: 'center' },
  { key: 'LOTNO', label: 'Lot No.', width: '150px' },
  { key: 'FAILGUBUN', label: '불량구분', width: '80px', align: 'center' },
  { key: 'PARTNO', label: '품번', width: '120px' },
  { key: 'PARTNM', label: '품명', width: '140px' },
  { key: 'STANDARD', label: '규격', width: '80px' },
  { key: 'FAILQTY', label: '불량수량', width: '80px', align: 'right' },
  { key: 'FAILTYPE', label: '불량유형', width: '80px' },
  { key: 'FAILBREAKDOWN', label: '불량원인', width: '100px' },
  { key: 'WORKORDNO', label: '작업지시번호', width: '130px' },
  { key: 'LINECD', label: '라인', width: '70px', align: 'center' },
  { key: 'REMARK', label: '비고', width: '150px' },
];

const rows = ref<any[]>([]);
const ld = ref(false), si = ref(-1);
const pg = ref(1), tp = ref(0), tot = ref(0);

// ── 데이터 처리 ──
async function fetchMaster() {
  try { const r = await api.get('/api/master/plant', { params: { size: 100 } }); plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); } catch {}
}

async function fetchData() {
  ld.value = true; si.value = -1;
  try {
    const p: any = { page: pg.value, size: 50 };
    if (startDate.value) p.start_date = startDate.value;
    if (endDate.value) p.end_date = endDate.value;
    if (plantCd.value) p.plant_cd = plantCd.value;
    if (searchLotNo.value) p.lot_no = searchLotNo.value;
    if (searchPartNo.value) p.part_no = searchPartNo.value;
    if (processStatus.value !== '전체') p.process_status = processStatus.value;

    const r = await api.get('/api/status/defect', { params: p });
    rows.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    tot.value = (r.data?.data?.total ?? r.data?.total ?? 0); tp.value = (r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);
  } finally { ld.value = false; }
}

function onPg(p: number) { pg.value = p; fetchData(); }
function onRow(_row: any, idx: number) { si.value = idx; }

onMounted(() => { fetchMaster(); fetchData(); });
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.search-section { background: #fff; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.section-title { font-size: .85rem; font-weight: 700; color: #1a5276; margin-bottom: 12px; }
.search-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; margin-left: 8px; min-width: 50px; }
.search-row label:first-child { margin-left: 0; }
.search-row input[type=text], .search-row select, .search-row input[type=date] { padding: 6px 10px; border: 1px solid #dfe6e9; border-radius: 4px; font-size: .85rem; }
.btn-search { background: #2980b9; color: #fff; border: none; padding: 6px 16px; border-radius: 4px; font-weight: 600; cursor: pointer; margin-left: auto; }

.grid-wrap { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.05); overflow: hidden; min-height: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #eaf2f8; border-bottom: 1px solid #d6eaf8; }
.toolbar-title { font-weight: 700; color: #2c3e50; font-size: .95rem; }

.status-badge { padding: 4px 8px; border-radius: 4px; font-size: .75rem; font-weight: 600; }
.status-wait { background: #ffeaa7; color: #d35400; }
.status-done { background: #e0f7fa; color: #00796b; }
</style>
