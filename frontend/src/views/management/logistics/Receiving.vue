<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">입고 현황</div>
      <div class="search-row">
        <label>입고일자</label>
        <input type="date" v-model="startDate" /><span>~</span><input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>공급사</label>
        <input type="text" v-model="searchText" placeholder="공급사명" @keyup.enter="fetchData" />
        <label>발주번호</label>
        <input type="text" v-model="orderNum" placeholder="발주번호" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-recv" @click="()=>window.alert('반품입고')">반품입고</button>
          <button class="btn-cancel" @click="cancelReceive">입고취소</button>
          <button class="btn-del" @click="()=>window.alert('삭제이력')">삭제이력</button>
        </div>
      </div>
    </section>
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si" :page="pg" :totalPages="tp" :total="tot" @row-click="onMaster" @page-change="onPg" />
      <div class="detail-wrap">
        <div class="dh">입고 상세 <span v-if="sel">- {{ sel.WAREHOUSENUM }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
const window = globalThis.window;
import { ref, onMounted } from 'vue'; 
import api from '../../../api'; 
import DataGrid from '../../../components/common/DataGrid.vue';
import { useNotification } from '../../../composables/useNotification';

const { notifySuccess, notifyError } = useNotification();

const d=new Date(),m=new Date(d);m.setMonth(m.getMonth()-1);const f=(v:Date)=>v.toISOString().slice(0,10);
const startDate=ref(f(m)),endDate=ref(f(d)),plantCd=ref(''),searchText=ref(''),orderNum=ref(''),plants=ref<any[]>([]);
const mCols=[{key:'WAREHOUSENUM',label:'입고번호',width:'120px'},{key:'PLANTNM',label:'사업장',width:'120px'},{key:'COMPANYNM',label:'공급사',width:'140px'},{key:'ORDERNUM',label:'발주번호',width:'100px'},{key:'INDAY',label:'입고일자',width:'110px',type:'date'},{key:'TOTALAMT',label:'총금액',width:'120px'},{key:'INGUBUN',label:'구분',width:'80px'}];
const dCols=[{key:'PARTNO',label:'자재품번',width:'130px'},{key:'PARTNM',label:'품명',width:'140px'},{key:'STANDARD',label:'규격',width:'90px'},{key:'UNIT',label:'단위',width:'60px'},{key:'UNIT_PRICE',label:'단가',width:'80px'},{key:'INLOTQTY',label:'입고수량',width:'90px'},{key:'FAILQTY',label:'불량수량',width:'80px'},{key:'LOTNO',label:'LOTNO',width:'110px'},{key:'WHSTATE',label:'입고상태',width:'80px'},{key:'LOCATIONNAME',label:'입고위치',width:'100px'}];
const mRows=ref<any[]>([]),dRows=ref<any[]>([]),ld=ref(false),dl=ref(false),si=ref(-1),sel=ref<any>(null),pg=ref(1),tp=ref(0),tot=ref(0);
async function fetchPlants(){try{const r=await api.get('/api/master/plant',{params:{size:100}});plants.value=r.data.data||[];}catch{}}
async function fetchData(){ld.value=true;si.value=-1;sel.value=null;dRows.value=[];try{const p:any={page:pg.value,size:50};if(startDate.value)p.start_date=startDate.value;if(endDate.value)p.end_date=endDate.value;if(plantCd.value)p.plant_cd=plantCd.value;if(searchText.value)p.search=searchText.value;if(orderNum.value)p.order_num=orderNum.value;const r=await api.get('/api/receive/list',{params:p});mRows.value=r.data.data||[];tot.value=r.data.total;tp.value=r.data.totalPages;}finally{ld.value=false;}}
async function onMaster(row:any,idx:number){si.value=idx;sel.value=row;dl.value=true;try{const r=await api.get(`/api/receive/detail/${row.WAREHOUSENUM}/items`);dRows.value=r.data||[];}finally{dl.value=false;}}
function onPg(p:number){pg.value=p;fetchData();}

async function cancelReceive() {
  if (!sel.value) {
    notifyError('입고 취소할 건을 선택해주세요.');
    return;
  }
  const whNum = sel.value.WAREHOUSENUM;
  const orderInfo = sel.value.ORDERNUM ? ` (발주번호: ${sel.value.ORDERNUM})` : '';
  if (!confirm(`입고번호 [${whNum}]${orderInfo} 건을 취소하시겠습니까?\n\n※ 관련 재고가 삭제되고 발주 현황이 복원됩니다.`)) {
    return;
  }
  try {
    await api.delete(`/api/receive/delete/${whNum}`);
    notifySuccess(`입고 취소가 완료되었습니다. (${whNum})`);
    sel.value = null;
    si.value = -1;
    dRows.value = [];
    fetchData();
  } catch (e: any) {
    const msg = e?.response?.data?.detail || e?.message || '알 수 없는 오류';
    notifyError(`입고 취소 중 오류: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`);
  }
}

onMounted(()=>{fetchPlants();fetchData();});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}.search-row input[type=date]{width:140px}.search-row input[type=text]{width:130px}.search-row select{min-width:130px}.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.act-right{display:flex;gap:6px;margin-left:auto}.btn-recv{background:#3498db;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.btn-cancel{background:#e67e22;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.btn-del{background:#e74c3c;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}.split-grids>*{flex:1;min-height:0}.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}.dh span{color:#667eea}
</style>
