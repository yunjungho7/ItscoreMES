<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">발주 현황</div>
      <div class="search-row">
        <label>발주일자</label>
        <input type="date" v-model="startDate" /><span>~</span><input type="date" v-model="endDate" />
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>검색</label>
        <input type="text" v-model="searchText" placeholder="발주번호/공급사/품번" @keyup.enter="fetchData" />
        <label class="chk-label"><input type="checkbox" v-model="includeCompleted" @change="fetchData" /> 완료포함</label>
        <button class="btn-search" @click="fetchData">조회</button>
        <div class="act-right">
          <button class="btn-recv" @click="handleReceiveComplete">입고완료</button>
          <button class="btn-cancel" @click="openBomRegister">BOM발주등록</button>
        </div>
      </div>
    </section>
    <div class="split-grids">
      <DataGrid :columns="mCols" :rows="mRows" :loading="ld" :selectedIndex="si" @row-click="onMaster" />
      <div class="detail-wrap">
        <div class="dh">발주 품목 상세 <span v-if="sel">- {{ sel.ORDERNUM }}</span>
          <span v-if="dRows.length > 0" class="chk-actions">
            <label class="chk-all-label"><input type="checkbox" :checked="isAllChecked" @change="toggleAllDetails" class="detail-chk" /> 전체선택</label>
            <span class="checked-count">{{ checkedDetailCount }} / {{ dRows.length }}건 선택</span>
          </span>
        </div>
        <DataGrid :columns="dCols" :rows="dRows" :loading="dl">
          <template #cell-CHK="{ row }">
            <input type="checkbox" v-model="row._checked" @click.stop class="detail-chk" />
          </template>
        </DataGrid>
      </div>
    </div>

    <!-- BOM 발주등록 모달 (기존 기능 유지하되 디자인 통일) -->
    <div v-if="showReg" class="modal-overlay" @click.self="showReg=false">
      <div class="modal-box" style="width:1000px;">
        <div class="modal-title">BOM 발주 등록<div class="modal-actions"><button class="btn-po" @click="submitPO">발주등록</button><button class="btn-close" @click="showReg=false">닫기</button></div></div>
        <div class="form-row">
          <label>사업장</label><select v-model="poForm.PLANTCD"><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
          <label>납기요청일</label><input type="date" v-model="poForm.ADOFREQDT" />
          <label>비고</label><input type="text" v-model="poForm.REMARK" style="flex:1" />
        </div>
        <div class="dual-grids">
           <div class="sub-grid-wrap">
              <div class="sub-title">완제품 목록 <button class="btn-sm" @click="addProduct">추가</button><button class="btn-sm-del" @click="removeProduct">제거</button></div>
              <div class="tbl-wrap">
                <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th style="width:150px">품번</th><th>품명</th><th class="num" style="width:100px">수량</th></tr></thead>
                <tbody><tr v-for="(p,i) in products" :key="i" :class="{selected:prodIdx===i}" @click="onProdClick(p,i)"><td><input type="checkbox" v-model="p.checked" @click.stop/></td><td><div class="input-with-btn"><input type="text" v-model="p.PARTNO" class="cell-input" @blur="onPartBlur(p)"/><button class="btn-grid-search" @click.stop="openPartPicker(i)">🔍</button></div></td><td>{{ p.PARTNM }}</td><td class="num red"><input type="number" v-model.number="p.QTY" class="cell-input num" @input="updateMaterials"/></td></tr></tbody></table>
              </div>
           </div>
           <div class="sub-grid-wrap">
              <div class="sub-title">자재 목록 (BOM 전개)</div>
              <div class="tbl-wrap">
                <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th>자재품번</th><th>품명</th><th class="num">발주수량</th><th class="num">현재고</th></tr></thead>
                <tbody><tr v-for="(m,i) in materials" :key="i"><td><input type="checkbox" v-model="m.checked"/></td><td>{{ m.PARTNO }}</td><td>{{ m.PARTNM }}</td><td class="num red">{{ m.ORDERQTY }}</td><td class="num">{{ m.STOCKQTY }}</td></tr></tbody></table>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- 품목 선택 팝업 -->
    <div v-if="showPartPicker" class="modal-overlay" @click.self="showPartPicker=false">
      <div class="picker-modal">
        <div class="picker-header"><h3>품목 선택</h3><button class="btn-close-sm" @click="showPartPicker=false">✕</button></div>
        <div class="picker-search">
          <input type="text" v-model="partSearch" placeholder="품번 또는 품명 검색" @keyup.enter="fetchParts" />
          <button class="btn-search" @click="fetchParts">조회</button>
        </div>
        <div class="picker-list">
          <table class="picker-tbl">
            <thead><tr><th>품번</th><th>품명</th><th>규격</th><th>단위</th></tr></thead>
            <tbody>
              <tr v-for="p in parts" :key="p.PARTNO" @click="selectPart(p)" class="clickable">
                <td>{{ p.PARTNO }}</td><td>{{ p.PARTNM }}</td><td>{{ p.STANDARD }}</td><td>{{ p.UNIT }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';

const d=new Date(),m=new Date(d);m.setMonth(m.getMonth()-1);const f=(v:Date)=>v.toISOString().slice(0,10);
const startDate=ref(f(m)),endDate=ref(f(d)),plantCd=ref(''),searchText=ref(''),includeCompleted=ref(false),plants=ref<any[]>([]);

const mCols=[
  {key:'ORDERNUM',label:'발주번호',width:'140px'},
  {key:'PLANTNM',label:'사업장',width:'120px'},
  {key:'COMPANYNM',label:'공급사',width:'140px'},
  {key:'ORDERDT',label:'발주일자',width:'110px'},
  {key:'ADOFREQDT',label:'납기요청일',width:'110px'},
  {key:'TOTALAMT',label:'총금액',width:'120px',type:'number'},
  {key:'ORDERSTATE',label:'상태',width:'100px'},
  {key:'REGUSERNM',label:'등록자',width:'90px'}
];
const dCols=[
  {key:'CHK',label:'선택',width:'50px'},
  {key:'PARTNO',label:'자재품번',width:'130px'},
  {key:'PARTNM',label:'품명',width:'150px'},
  {key:'STANDARD',label:'규격',width:'100px'},
  {key:'UNIT',label:'단위',width:'60px'},
  {key:'UNIT_PRICE',label:'단가',width:'90px',type:'number'},
  {key:'ORDERQTY',label:'발주수량',width:'90px',type:'number'},
  {key:'ADOFREQDT',label:'납기요청일',width:'110px'},
  {key:'AMT',label:'금액',width:'100px',type:'number'},
  {key:'INQTY',label:'입고수량',width:'90px',type:'number'},
  {key:'REMAINQTY',label:'미입고잔량',width:'100px',type:'number'},
  {key:'STOCKQTY',label:'현재고',width:'90px',type:'number'}
];

const mRows=ref<any[]>([]),dRows=ref<any[]>([]),ld=ref(false),dl=ref(false),si=ref(-1),sel=ref<any>(null);

async function fetchPlants(){try{const r=await api.get('/api/master/plant',{params:{size:100}});plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}catch{}}

async function fetchData(){
  ld.value=true; si.value=-1; sel.value=null; dRows.value=[];
  try{
    const p:any={
      start_date:startDate.value,
      end_date:endDate.value,
      plant_cd:plantCd.value,
      search:searchText.value,
      include_completed:includeCompleted.value
    };
    const r=await api.get('/api/purchase/list',{params:p});
    mRows.value = Array.isArray(r.data) ? r.data : (r.data?.data || []);
  }finally{ld.value=false;}}

// 체크박스 관련
const checkedDetailCount = computed(() => dRows.value.filter((d: any) => d._checked).length);
const isAllChecked = computed(() => dRows.value.length > 0 && dRows.value.every((d: any) => d._checked));
function toggleAllDetails(e: Event) {
  const checked = (e.target as HTMLInputElement).checked;
  dRows.value.forEach((d: any) => { d._checked = checked; });
}

async function onMaster(row:any,idx:number){
  si.value=idx; sel.value=row; dl.value=true;
  try{
    const r=await api.get(`/api/purchase/detail/${row.ORDERNUM}`);
    // 입고 완료된 품목(REMAINQTY <= 0) 제외
    dRows.value=(r.data||[])
      .filter((d:any)=>{
        const remain = d.REMAINQTY !== undefined ? Number(d.REMAINQTY) : (Number(d.ORDERQTY) - Number(d.INQTY || 0));
        return remain > 0;
      })
      .map((d:any)=>({...d, _checked: false}));
  }finally{dl.value=false;}}

// --- 입고완료 기능 ---
async function handleReceiveComplete(){
  if(!sel.value){alert('발주 건을 선택하세요.');return;}
  if(dRows.value.length===0){alert('상세 품목이 없습니다.');return;}
  
  const checkedItems = dRows.value.filter((d:any) => d._checked);
  if(checkedItems.length===0){alert('입고 처리할 품목을 선택(체크)해주세요.');return;}
  
  if(!confirm(`발주번호 [${sel.value.ORDERNUM}] 건을 입고 처리하시겠습니까?\n선택 품목 수: ${checkedItems.length}건 / 전체 ${dRows.value.length}건`)) return;
  
  try{
    const body={
      PLANTCD: sel.value.PLANTCD,
      ORDERNUM: sel.value.ORDERNUM,
      COMPANYCD: sel.value.COMPANYCD,
      INGUBUN: 'PURCHASE',
      INDAY: f(new Date()),
      details: checkedItems.map((d:any)=>({
        PARTNO:d.PARTNO,
        INLOTQTY: Number(d.REMAINQTY) > 0 ? Number(d.REMAINQTY) : (Number(d.ORDERQTY) || 0),
        ORDERQTY: Number(d.ORDERQTY) || 0,
        UNIT_PRICE: Number(d.UNIT_PRICE) || 0
      }))
    };
    await api.post('/api/receive/order', body);
    alert(`입고 처리가 완료되었습니다. (${checkedItems.length}건)`);
    fetchData();
  }catch(e){alert('오류가 발생했습니다.');}
}

// --- BOM 발주 등록 기능 (디자인만 통일) ---
const showReg=ref(false), poForm=ref({PLANTCD:'',ADOFREQDT:f(new Date(new Date().getTime()+86400000)),REMARK:''});
const products=ref<any[]>([]), materials=ref<any[]>([]), prodIdx=ref(-1);
function openBomRegister(){
  poForm.value.PLANTCD=plants.value[0]?.PLANTCD||'';
  products.value=[]; materials.value=[]; showReg.value=true;
}
function addProduct(){products.value.push({PARTNO:'',PARTNM:'',QTY:1,checked:false});}
function removeProduct(){products.value=products.value.filter(p=>!p.checked); materials.value=[]; prodIdx.value=-1;}
async function updateMaterials(){ if(prodIdx.value>=0) onProdClick(products.value[prodIdx.value], prodIdx.value); }
async function onProdClick(p:any,i:number){
  prodIdx.value=i; if(!p.PARTNO)return;
  try{const r=await api.get(`/api/purchase/bom/${p.PARTNO}`);
    materials.value=(r.data||[]).map((m:any)=>({...m,ORDERQTY:Math.ceil((m.REQQTY||1)*(p.QTY||1)),checked:true}));
  }catch{}}
async function onPartBlur(p:any){
  if(!p.PARTNO)return;
  try{const r=await api.get('/api/master/goods',{params:{search:p.PARTNO,size:1}});
    if(r.data.data?.length){p.PARTNM=r.data.data[0].PARTNM; updateMaterials();}
  }catch{}}
async function submitPO(){
  const vm=materials.value.filter(m=>m.checked && m.ORDERQTY>0);
  if(!vm.length){alert('발주할 자재가 없습니다.');return;}
  try{
    await api.post('/api/purchase/order', {
      PLANTCD:poForm.value.PLANTCD, COMPANYCD:vm[0].COMPANYCD, ADOFREQDT:poForm.value.ADOFREQDT, REMARK:poForm.value.REMARK,
      details: vm.map(m=>({PARTNO:m.PARTNO, ORDERQTY:m.ORDERQTY, UNIT_PRICE:m.UNIT_PRICE||0}))
    });
    alert('등록되었습니다.'); showReg.value=false; fetchData();
  }catch{alert('오류 발생');}}

// 품목 선택 팝업 관련
const showPartPicker=ref(false), partSearch=ref(''), parts=ref<any[]>([]), activeItemIdx=ref(-1);
function openPartPicker(idx:number){ activeItemIdx.value=idx; partSearch.value=''; parts.value=[]; showPartPicker.value=true; }
async function fetchParts(){ const r=await api.get('/api/master/goods',{params:{search:partSearch.value,size:50}}); parts.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || [])); }
function selectPart(p:any){ if(activeItemIdx.value>-1){ products.value[activeItemIdx.value].PARTNO=p.PARTNO; products.value[activeItemIdx.value].PARTNM=p.PARTNM; updateMaterials(); } showPartPicker.value=false; }

onMounted(()=>{fetchPlants();fetchData();});
</script>

<style scoped>
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}.search-row input[type=date]{width:140px}.search-row input[type=text]{width:150px}.search-row select{min-width:130px}.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.act-right{display:flex;gap:6px;margin-left:auto}.btn-recv{background:#3498db;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.btn-cancel{background:#27ae60;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}.chk-label{font-size:.85rem;display:flex;align-items:center;gap:4px;color:#636e72;cursor:pointer}
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}.split-grids>*{flex:1;min-height:0}.detail-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef;display:flex;align-items:center;gap:10px}.dh span{color:#667eea}
.chk-actions{display:flex;align-items:center;gap:10px;margin-left:auto}.chk-all-label{display:flex;align-items:center;gap:4px;font-size:.8rem;font-weight:600;color:#475569;cursor:pointer}.checked-count{font-size:.78rem;font-weight:600;color:#2980b9;background:#ebf5fb;padding:2px 10px;border-radius:10px}.detail-chk{width:16px;height:16px;cursor:pointer;accent-color:#3498db}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1000;display:flex;align-items:center;justify-content:center}.modal-box{background:#fff;border-radius:12px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.2)}.modal-title{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;font-size:1.1rem;font-weight:700;border-bottom:2px solid #f0f4ff}.modal-actions{display:flex;gap:8px}.btn-close{background:#e74c3c;color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer}.form-row{display:flex;align-items:center;gap:10px;padding:14px 20px;flex-wrap:wrap}.form-row label{font-size:.85rem;font-weight:600;color:#636e72}.form-row input,.form-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}.dual-grids{display:flex;gap:10px;padding:0 20px 20px}.sub-grid-wrap{flex:1;display:flex;flex-direction:column;gap:10px;border:1px solid #eee;border-radius:8px;padding:10px}.sub-title{font-size:.85rem;font-weight:700;color:#3a4a6b;display:flex;align-items:center;gap:10px}.btn-sm{background:#27ae60;color:#fff;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:.75rem}.btn-sm-del{background:#e74c3c;color:#fff;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:.75rem}.tbl-wrap{max-height:300px;overflow:auto}.sub-tbl{width:100%;border-collapse:collapse;font-size:.82rem}.sub-tbl th{background:#f8f9fa;padding:8px;text-align:left;border-bottom:1px solid #eee}.sub-tbl td{padding:6px 8px;border-bottom:1px solid #f9f9f9}.input-with-btn{display:flex;gap:4px}.cell-input{width:100%;padding:4px;border:1px solid #ddd;border-radius:4px}.btn-grid-search{background:#667eea;color:#fff;border:none;border-radius:4px;cursor:pointer}.btn-po{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer}
.picker-modal{background:#fff;border-radius:12px;width:500px;max-height:500px;display:flex;flex-direction:column;overflow:hidden}.picker-header{padding:15px 20px;background:#f8f9fa;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center}.btn-close-sm{background:none;border:none;font-size:1.2rem;cursor:pointer}.picker-search{padding:15px;display:flex;gap:10px}.picker-list{flex:1;overflow:auto;padding:0 15px 15px}.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}.picker-tbl th{background:#f8f9fa;padding:10px;text-align:left;border-bottom:2px solid #eee}.picker-tbl td{padding:10px;border-bottom:1px solid #eee}.clickable{cursor:pointer}.clickable:hover{background:#f0f4ff}
</style>
