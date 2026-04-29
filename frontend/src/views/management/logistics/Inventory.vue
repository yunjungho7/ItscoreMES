<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">재고 현황</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>창고</label>
        <select v-model="warehouseCd"><option value="">전체</option><option v-for="w in warehouses" :key="w.WAREHOUSECODE" :value="w.WAREHOUSECODE">{{ w.WAREHOUSENAME }}</option></select>
        <label>라인</label>
        <select v-model="lineCd"><option value="">전체</option></select>
        <label>품목구분</label>
        <select v-model="partType"><option value="">전체</option><option v-for="code in partTypes" :key="code.CODECD" :value="code.CODECD">{{ code.CODENM }}</option></select>
        <label>공정</label>
        <select v-model="processCd"><option value="">전체</option></select>
      </div>
      <div class="search-row" style="margin-top:6px">
        <label>품번</label>
        <input type="text" v-model="searchText" placeholder="품번/품명" @keyup.enter="fetchData" />
        <label>위치(Loc)</label>
        <input type="text" v-model="locationCd" placeholder="위치코드" />
        <label>LOT번호</label>
        <input type="text" v-model="lotNo" placeholder="LOT번호" />
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-move" @click="()=>window.alert('재고이동')">재고이동</button>
          <button class="btn-edit" @click="()=>window.alert('재고수정')">재고수정</button>
        </div>
      </div>
    </section>
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si" :page="pg" :totalPages="tp" :total="tot" @row-click="onMaster" @page-change="onPg" />
      <div class="detail-wrap">
        <div class="dh">LOT별 재고 상세 <span v-if="sel">- {{ sel.PARTNO }} {{ sel.PARTNM }}</span></div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl" />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
const window = globalThis.window;
import { ref, computed, onMounted } from 'vue'; import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue';
const plantCd=ref(''),warehouseCd=ref(''),lineCd=ref(''),partType=ref(''),processCd=ref(''),searchText=ref(''),locationCd=ref(''),lotNo=ref('');
const plants=ref<any[]>([]),warehouses=ref<any[]>([]),allCodes=ref<any[]>([]);
const partTypes = computed(() => allCodes.value.filter(c => c.PAR_CODECD === 'PARTGUBUN000').sort((a,b)=>a.ORD - b.ORD));
function getPartTypeName(cd: string) {
  if (!cd) return '';
  const found = partTypes.value.find(c => c.CODECD === cd);
  if (found) return found.CODENM;
  return cd;
}
const mCols=[{key:'PARTNO',label:'품번',width:'130px'},{key:'PARTNM',label:'품명',width:'150px'},{key:'STANDARD',label:'규격',width:'100px'},{key:'PARTTYPE_NM',label:'품목구분',width:'80px'},{key:'UNIT',label:'단위',width:'60px'},{key:'SAFETYSTOCK',label:'안전재고',width:'80px'},{key:'GOODQTY',label:'양품수량',width:'90px'},{key:'FAILQTY',label:'불량수량',width:'80px'},{key:'TOTALQTY',label:'현재고수량',width:'100px'}];
const dCols=[{key:'PLANTNM',label:'사업장',width:'110px'},{key:'WAREHOUSENAME',label:'창고',width:'110px'},{key:'LOCATIONNAME',label:'로케이션명',width:'120px'},{key:'LOTCREATIONDAY',label:'LOT생성일자',width:'110px'},{key:'LOTNO',label:'LOT번호',width:'120px'},{key:'STOCKQTY',label:'재고수량',width:'90px'},{key:'ETCINFO',label:'기타정보',minWidth:'120px'}];
const mRows=ref<any[]>([]),dRows=ref<any[]>([]),ld=ref(false),dl=ref(false),si=ref(-1),sel=ref<any>(null),pg=ref(1),tp=ref(0),tot=ref(0);
async function fetchPlants(){try{const r=await api.get('/api/master/plant',{params:{size:100}});plants.value=r.data.data||[];}catch{}}
async function fetchWarehouses(){try{const r=await api.get('/api/master/warehouse',{params:{size:100}});warehouses.value=r.data.data||[];}catch{}}
async function fetchCodes(){try{const r=await api.get('/api/master/code',{params:{size:9999}});allCodes.value=r.data.data||[];}catch{}}
async function fetchData(){ld.value=true;si.value=-1;sel.value=null;dRows.value=[];try{const p:any={page:pg.value,size:50};if(plantCd.value)p.plant_cd=plantCd.value;if(warehouseCd.value)p.warehouse_cd=warehouseCd.value;if(lineCd.value)p.line_cd=lineCd.value;if(processCd.value)p.process_cd=processCd.value;if(partType.value)p.part_type=partType.value;if(lotNo.value)p.lot_no=lotNo.value;if(locationCd.value)p.location_cd=locationCd.value;if(searchText.value)p.search=searchText.value;const r=await api.get('/api/inventory/list',{params:p});const raw=r.data.data||[];mRows.value=raw.map((item:any)=>({...item,PARTTYPE_NM:getPartTypeName(item.PARTTYPE)}));tot.value=r.data.total;tp.value=r.data.totalPages;}finally{ld.value=false;}}
async function onMaster(row:any,idx:number){si.value=idx;sel.value=row;dl.value=true;try{const r=await api.get(`/api/inventory/detail/${row.PARTNO}`);dRows.value=r.data||[];}finally{dl.value=false;}}
function onPg(p:number){pg.value=p;fetchData();}
onMounted(()=>{fetchPlants();fetchWarehouses();fetchCodes().then(fetchData);});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}.search-row input[type=text]{width:130px}.search-row select{min-width:110px}.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.act-right{display:flex;gap:6px;margin-left:auto}.btn-move{background:#3498db;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.btn-edit{background:#e67e22;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}.split-grids>*{flex:1;min-height:0}.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}.dh span{color:#667eea}
</style>
