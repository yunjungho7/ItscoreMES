<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">발주 대상 (생산계획)</div>
      <div class="search-row">
        <label>생산기준일</label>
        <input type="date" v-model="baseDate" />
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>품번/품명</label>
        <input type="text" v-model="searchText" placeholder="품번/품명" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-po" @click="openRegister">발주등록</button>
          <button class="btn-excel">엑셀</button>
        </div>
      </div>
    </section>
    <!-- 캘린더 그리드 -->
    <div class="cal-grid-wrap">
      <table class="cal-grid">
        <thead>
          <tr>
            <th class="fix">품번</th><th class="fix">품명</th><th class="fix">규격</th>
            <th class="fix num">재고수량</th><th class="fix num">계획합계</th>
            <th v-for="dt in dateCols" :key="dt" class="date-col">
              <div>{{ dt.slice(5) }}</div><div class="sub">계획</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="pivotRows.length===0"><td :colspan="5+dateCols.length" class="empty">데이터가 없습니다.</td></tr>
          <tr v-for="(row,i) in pivotRows" :key="i" :class="{selected:selIdx===i}" @click="selIdx=i">
            <td>{{ row.PARTNO }}</td><td>{{ row.PARTNM }}</td><td>{{ row.STANDARD }}</td>
            <td class="num">{{ row.STOCKQTY }}</td>
            <td class="num total">{{ row.PLANTOTAL }}</td>
            <td v-for="dt in dateCols" :key="dt" class="num" :class="{hasval:row.dates[dt]>0}">
              {{ row.dates[dt] || '' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- 발주등록 모달 -->
    <div v-if="showReg" class="modal-overlay" @click.self="showReg=false">
      <div class="modal-box" style="width:900px;">
        <div class="modal-title">발주 등록<div class="modal-actions"><button class="btn-po" @click="submitPO">발주등록</button><button class="btn-close" @click="showReg=false">닫기</button></div></div>
        <div class="form-row">
          <label>사업장</label><select v-model="poForm.PLANTCD"><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
          <label>납기요청일</label><input type="date" v-model="poForm.ADOFREQDT" />
          <label>비고</label><input type="text" v-model="poForm.REMARK" style="flex:1" />
        </div>
        <div class="sub-title">완제품 목록 <button class="btn-sm" @click="addProduct">추가</button><button class="btn-sm-del" @click="removeProduct">제거</button></div>
        <div class="tbl-wrap">
          <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th>품번</th><th>품명</th><th>단위</th><th>규격</th><th class="num">수량</th></tr></thead>
          <tbody><tr v-for="(p,i) in products" :key="i" :class="{selected:prodIdx===i}" @click="onProdClick(p,i)"><td><input type="checkbox" v-model="p.checked"/></td><td>{{ p.PARTNO }}</td><td>{{ p.PARTNM }}</td><td>{{ p.UNIT }}</td><td>{{ p.STANDARD }}</td><td class="num red">{{ p.QTY }}</td></tr></tbody></table>
        </div>
        <div class="sub-title">자재 목록 (BOM 전개)</div>
        <div class="tbl-wrap">
          <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th>자재품번</th><th>품명</th><th>공급사</th><th>단위</th><th>단가</th><th>납기요청일</th><th class="num">필요수량</th><th class="num">발주수량</th><th class="num">재고수량</th><th>비고</th></tr></thead>
          <tbody><tr v-for="(m,i) in materials" :key="i"><td><input type="checkbox" v-model="m.checked"/></td><td>{{ m.PARTNO }}</td><td>{{ m.PARTNM }}</td><td>{{ m.COMPANYNM }}</td><td>{{ m.UNIT }}</td><td>{{ m.UNIT_PRICE }}</td><td>{{ poForm.ADOFREQDT }}</td><td class="num">{{ m.NEEDQTY }}</td><td class="num red">{{ m.ORDERQTY }}</td><td class="num">{{ m.STOCKQTY }}</td><td></td></tr></tbody></table>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'; import api from '../../../api';
const d=new Date(); const f=(v:Date)=>v.toISOString().slice(0,10);
const baseDate=ref(f(d)),plantCd=ref(''),searchText=ref(''),plants=ref<any[]>([]);
const dateCols=ref<string[]>([]),pivotRows=ref<any[]>([]),selIdx=ref(-1);
const showReg=ref(false);
const poForm=ref({PLANTCD:'',ADOFREQDT:f(new Date(d.getTime()+86400000)),REMARK:''});
const products=ref<any[]>([]),materials=ref<any[]>([]),prodIdx=ref(-1);

function genDateCols(){const cols:string[]=[];const b=new Date(baseDate.value);for(let i=0;i<14;i++){const dd=new Date(b);dd.setDate(dd.getDate()+i);cols.push(f(dd));}dateCols.value=cols;}

async function fetchPlants(){try{const r=await api.get('/api/master/plant',{params:{size:100}});plants.value=r.data.data||[];}catch{}}

async function fetchData(){
  genDateCols();
  try{
    const p:any={};if(plantCd.value)p.plant_cd=plantCd.value;
    p.start_date=dateCols.value[0];p.end_date=dateCols.value[dateCols.value.length-1];
    if(searchText.value)p.search=searchText.value;
    const r=await api.get('/api/purchase/plan',{params:p});
    const raw=r.data||[];
    const map:Record<string,any>={};
    for(const row of raw){
      if(!map[row.PARTNO])map[row.PARTNO]={PARTNO:row.PARTNO,PARTNM:row.PARTNM,STANDARD:row.STANDARD,STOCKQTY:row.STOCKQTY||0,PLANTOTAL:0,dates:{}};
      const dt=typeof row.PRODUCEDT==='string'?row.PRODUCEDT.slice(0,10):f(new Date(row.PRODUCEDT));
      map[row.PARTNO].dates[dt]=(map[row.PARTNO].dates[dt]||0)+(row.PRODUCEQTY||0);
      map[row.PARTNO].PLANTOTAL+=(row.PRODUCEQTY||0);
    }
    pivotRows.value=Object.values(map);
  }catch{}
}

function openRegister(){
  if(selIdx.value>=0){
    const r=pivotRows.value[selIdx.value];
    products.value=[{PARTNO:r.PARTNO,PARTNM:r.PARTNM,UNIT:'',STANDARD:r.STANDARD,QTY:r.PLANTOTAL,checked:false}];
  }else{products.value=[];}
  materials.value=[];showReg.value=true;
}
function addProduct(){products.value.push({PARTNO:'',PARTNM:'',UNIT:'',STANDARD:'',QTY:0,checked:false});}
function removeProduct(){products.value=products.value.filter(p=>!p.checked);}
async function onProdClick(p:any,i:number){
  prodIdx.value=i;
  if(!p.PARTNO)return;
  try{const r=await api.get(`/api/purchase/bom/${p.PARTNO}`);
    materials.value=(r.data||[]).map((m:any)=>({...m,NEEDQTY:Math.ceil((m.REQQTY||1)*(p.QTY||0)),ORDERQTY:Math.max(0,Math.ceil((m.REQQTY||1)*(p.QTY||0))-(m.STOCKQTY||0)),checked:false}));
  }catch{}
}
function submitPO(){alert('발주가 등록되었습니다.');showReg.value=false;}
onMounted(()=>{fetchPlants();fetchData();});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}.search-row input[type=date]{width:140px}.search-row input[type=text]{width:150px}.search-row select{min-width:130px}.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.act-right{display:flex;gap:6px;margin-left:auto}
.btn-po{background:linear-gradient(135deg,#27ae60,#2ecc71);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.btn-excel{background:#3498db;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.cal-grid-wrap{flex:1;overflow:auto;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05)}.cal-grid{width:100%;border-collapse:collapse;font-size:.83rem}.cal-grid thead{position:sticky;top:0;z-index:2}.cal-grid th{background:linear-gradient(180deg,#f0f4ff,#e8ecf5);color:#3a4a6b;font-weight:600;padding:8px 10px;border-bottom:2px solid #d0d7e8;white-space:nowrap;text-align:left}.cal-grid td{padding:7px 10px;border-bottom:1px solid #f0f2f5}.cal-grid .fix{position:sticky;left:0;background:#fff;z-index:1}.cal-grid .num{text-align:right}.cal-grid .total{color:#667eea;font-weight:700}.date-col{min-width:60px;text-align:center}.date-col .sub{font-size:.72rem;color:#b2bec3}.hasval{background:#e8f5e9;color:#2e7d32;font-weight:600}.cal-grid tbody tr{cursor:pointer;transition:background .12s}.cal-grid tbody tr:hover{background:#f4f6ff}.cal-grid tbody tr.selected{background:#e8edff}.empty{text-align:center;color:#b2bec3;padding:60px 16px!important}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1000;display:flex;align-items:center;justify-content:center}.modal-box{background:#fff;border-radius:12px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.2)}.modal-title{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;font-size:1.1rem;font-weight:700;border-bottom:2px solid #f0f4ff}.modal-actions{display:flex;gap:8px}.btn-close{background:#e74c3c;color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer}.form-row{display:flex;align-items:center;gap:10px;padding:14px 20px;flex-wrap:wrap}.form-row label{font-size:.85rem;font-weight:600;color:#636e72}.form-row input,.form-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.sub-title{padding:10px 20px;font-size:.85rem;font-weight:600;color:#3a4a6b;background:#f8f9fa;border-top:1px solid #eee;border-bottom:1px solid #eee;display:flex;align-items:center;gap:10px}.btn-sm{background:#27ae60;color:#fff;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:.78rem;font-weight:600}.btn-sm-del{background:#e74c3c;color:#fff;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:.78rem;font-weight:600}
.tbl-wrap{max-height:200px;overflow:auto;padding:0 20px 10px}.sub-tbl{width:100%;border-collapse:collapse;font-size:.83rem}.sub-tbl th{background:#f0f4ff;padding:7px 8px;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #d0d7e8;white-space:nowrap}.sub-tbl td{padding:6px 8px;border-bottom:1px solid #f0f2f5}.sub-tbl .num{text-align:right}.sub-tbl .red{color:#e74c3c;font-weight:600}.sub-tbl tr{cursor:pointer}.sub-tbl tr:hover{background:#f4f6ff}.sub-tbl tr.selected{background:#e8edff}
</style>
