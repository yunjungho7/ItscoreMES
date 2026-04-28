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
          <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th>품번</th><th>품명</th><th>단위</th><th>규격</th><th class="num" style="width:100px;">수량</th></tr></thead>
          <tbody><tr v-for="(p,i) in products" :key="i" :class="{selected:prodIdx===i}" @click="onProdClick(p,i)">
            <td><input type="checkbox" v-model="p.checked"/></td>
            <td>
              <div class="input-with-btn">
                <input type="text" v-model="p.PARTNO" readonly placeholder="품번 선택" @click="openProductPicker(i)" />
                <button class="btn-search-sm" @click="openProductPicker(i)">🔍</button>
              </div>
            </td>
            <td>{{ p.PARTNM }}</td>
            <td>{{ p.UNIT }}</td>
            <td>{{ p.STANDARD }}</td>
            <td class="num">
              <input type="number" v-model.number="p.QTY" class="qty-input" @input="onQtyChange" />
            </td>
          </tr></tbody></table>
        </div>
        <div class="sub-title">자재 목록 (BOM 전개)</div>
        <div class="tbl-wrap">
          <table class="sub-tbl"><thead><tr><th style="width:30px"></th><th>자재품번</th><th>품명</th><th>공급사</th><th>단위</th><th>단가</th><th>납기요청일</th><th class="num">필요수량</th><th class="num">발주수량</th><th class="num">재고수량</th><th>비고</th></tr></thead>
          <tbody><tr v-for="(m,i) in materials" :key="i">
            <td><input type="checkbox" v-model="m.checked"/></td>
            <td :style="{ paddingLeft: ((m.LEVEL || 1) - 1) * 16 + 8 + 'px' }">
              <span v-if="(m.LEVEL || 1) > 1" style="color:#94a3b8; margin-right:4px;">└</span>
              {{ m.PARTNO }}
            </td>
            <td>{{ m.PARTNM }}</td><td>{{ m.COMPANYNM }}</td><td>{{ m.UNIT }}</td><td>{{ m.UNIT_PRICE }}</td><td>{{ poForm.ADOFREQDT }}</td><td class="num">{{ m.NEEDQTY }}</td><td class="num red">{{ m.ORDERQTY }}</td><td class="num">{{ m.STOCKQTY }}</td><td></td></tr></tbody></table>
        </div>
      </div>
    </div>

    <!-- ═══ 품목 선택 팝업 ═══ -->
    <Teleport to="body">
      <div v-if="showGoodsPicker" class="modal-overlay-picker" @click.self="showGoodsPicker=false">
        <div class="picker-modal">
          <div class="picker-header">
            <h3>품목 선택 (완제품)</h3>
            <button class="btn-close-sm" @click="showGoodsPicker=false">✕</button>
          </div>
          <div class="picker-search">
            <input type="text" v-model="goodsSearch" placeholder="품번 또는 품명 검색" @keyup.enter="filterGoods" />
            <button class="btn-search" @click="filterGoods">조회</button>
          </div>
          <div class="picker-list">
            <table class="picker-tbl">
              <thead><tr><th>품번</th><th>품명</th><th>품목유형</th></tr></thead>
              <tbody>
                <tr v-for="g in filteredGoods" :key="g.PARTNO" @click="selectGoods(g)" class="clickable">
                  <td>{{ g.PARTNO }}</td><td>{{ g.PARTNM }}</td><td>{{ g.PARTTYPE }}</td>
                </tr>
                <tr v-if="filteredGoods.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Teleport>
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

// Picker state
const showGoodsPicker = ref(false);
const goodsSearch = ref('');
const pickingProdIdx = ref(-1);
const allGoods = ref<any[]>([]);
const filteredGoods = ref<any[]>([]);

async function fetchAllGoods() {
  try {
    const r = await api.get('/api/master/goods', { params: { size: 9999 } });
    allGoods.value = (r.data.data || []).filter((g: any) => g.PARTTYPE === '완제품');
    filterGoods();
  } catch {}
}

function filterGoods() {
  const s = goodsSearch.value.toLowerCase();
  if (s) {
    filteredGoods.value = allGoods.value.filter(g => 
      (g.PARTNO && g.PARTNO.toLowerCase().includes(s)) || 
      (g.PARTNM && g.PARTNM.toLowerCase().includes(s))
    );
  } else {
    filteredGoods.value = allGoods.value;
  }
}

function openProductPicker(idx: number) {
  pickingProdIdx.value = idx;
  goodsSearch.value = '';
  fetchAllGoods();
  showGoodsPicker.value = true;
}

function selectGoods(g: any) {
  if (pickingProdIdx.value >= 0) {
    const p = products.value[pickingProdIdx.value];
    p.PARTNO = g.PARTNO;
    p.PARTNM = g.PARTNM;
    p.UNIT = g.UNIT || '';
    p.STANDARD = g.STANDARD || '';
    refreshMaterials();
  }
  showGoodsPicker.value = false;
}

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

async function openRegister(){
  if(selIdx.value>=0){
    const r=pivotRows.value[selIdx.value];
    products.value=[{PARTNO:r.PARTNO,PARTNM:r.PARTNM,UNIT:r.UNIT||'',STANDARD:r.STANDARD,QTY:r.PLANTOTAL,checked:false}];
    // Automatically fetch BOM for the initially selected product
    await refreshMaterials();
  }else{
    products.value=[];
    materials.value=[];
  }
  showReg.value=true;
}

function addProduct(){
  products.value.push({PARTNO:'',PARTNM:'',UNIT:'',STANDARD:'',QTY:0,checked:false});
}

function removeProduct(){
  products.value=products.value.filter(p=>!p.checked);
  refreshMaterials();
}

// Create a flat list of materials showing the BOM tree structure
async function refreshMaterials() {
  const newMaterials: any[] = [];
  
  for (const p of products.value) {
    if (!p.PARTNO || p.QTY <= 0) continue;
    
    try {
      const r = await api.get(`/api/purchase/bom/${p.PARTNO}`);
      const bomData = r.data || [];
      
      for (const m of bomData) {
        const need = Math.ceil((m.REQQTY || 0) * (p.QTY || 0));
        newMaterials.push({
          ...m,
          NEEDQTY: need,
          ORDERQTY: Math.max(0, need - (m.STOCKQTY || 0)),
          checked: false
        });
      }
    } catch (e) {
      console.error(`Error fetching BOM for ${p.PARTNO}:`, e);
    }
  }
  
  materials.value = newMaterials;
}

async function onProdClick(p:any,i:number){
  prodIdx.value=i;
  // Previously this was the only way to load materials, but now we use refreshMaterials()
}

// Add a helper to handle product quantity changes
function onQtyChange() {
  refreshMaterials();
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

/* ═══ 품목 선택 팝업 ═══ */
.modal-overlay-picker{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1100;display:flex;align-items:center;justify-content:center}
.picker-modal{background:#fff;border-radius:10px;width:500px;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.2);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.picker-header h3{margin:0;font-size:1.05rem;font-weight:700;color:#2c3e50}
.btn-close-sm{background:none;border:none;font-size:1.2rem;cursor:pointer;color:#95a5a6}
.btn-close-sm:hover{color:#e74c3c}
.picker-search{display:flex;gap:8px;padding:14px 20px;background:#fff;border-bottom:1px solid #e9ecef}
.picker-search input{flex:1;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}
.picker-list{flex:1;overflow-y:auto;padding:10px 20px 20px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{padding:8px 10px;background:#f1f5f9;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#e8f5e9}
.input-with-btn{display:flex;gap:4px;height: 30px;}
.input-with-btn input{flex:1;cursor:pointer;background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:0 8px;}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:4px;cursor:pointer;font-size:0.9rem;}
.qty-input{width:100%;padding:4px 6px;border:1px solid #e2e8f0;border-radius:4px;text-align:right;}
</style>
