<template>
  <div class="page-view">
    <!-- ═══ 검색 영역 ═══ -->
    <section class="search-section">
      <div class="section-title">발주 현황 (생산계획 대비)</div>
      <div class="search-row">
        <label>생산기준일</label>
        <input type="date" v-model="baseDate" />
        <label>사업장</label>
        <select v-model="plantCd">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>품번/품명</label>
        <div class="input-with-btn">
          <input type="text" v-model="searchText" placeholder="품번/품명 입력" @keyup.enter="fetchData" />
          <button class="btn-search-sm" @click="isMainItemPickerOpen = true" title="검색">🔍</button>
        </div>
        <button class="btn-search" @click="fetchData">조회</button>
        
        <div class="act-right">
          <button class="btn-add" @click="openRegister">＋ 발주등록</button>
          <button class="btn-excel">엑셀출력</button>
        </div>
      </div>
    </section>

    <!-- ═══ 메인 컨텐츠 영역 (SalesOrder 스타일) ═══ -->
    <div class="split-grids">
      <div class="grid-wrap">
        <div class="dh">발주 대상 계획 현황 <span v-if="pivotRows.length"> - Total {{ pivotRows.length }}건</span></div>
        <div class="cal-grid-wrap">
          <table class="cal-grid">
            <thead>
              <tr>
                <th class="fix">수주번호</th>
                <th class="fix">고객사</th>
                <th class="fix">품번</th>
                <th class="fix">품명</th>
                <th class="fix center">단위</th>
                <th class="fix num">재고</th>
                <th class="fix num total-head">계획합계</th>
                <th v-for="dt in dateCols" :key="dt" class="date-col">
                  <div>{{ dt.slice(5) }}</div>
                  <div class="sub">계획</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading"><td :colspan="7+dateCols.length" class="empty">조회 중...</td></tr>
              <tr v-else-if="pivotRows.length===0"><td :colspan="7+dateCols.length" class="empty">데이터가 없습니다.</td></tr>
              <tr v-for="(row,i) in pivotRows" :key="i" :class="{selected:selIdx===i}" @click="selIdx=i">
                <td class="fix">{{ row.ORDERNUM }}</td>
                <td class="fix">{{ row.COMPANYNM }}</td>
                <td class="fix font-bold">{{ row.PARTNO }}</td>
                <td class="fix">{{ row.PARTNM }}</td>
                <td class="fix center"><span class="badge-unit">{{ row.UNIT }}</span></td>
                <td class="fix num">{{ row.STOCKQTY?.toLocaleString() }}</td>
                <td class="fix num total-cell">{{ row.PLANTOTAL?.toLocaleString() }}</td>
                <td v-for="dt in dateCols" :key="dt" class="num" :class="{hasval:row.dates[dt]>0}">
                  {{ row.dates[dt] > 0 ? row.dates[dt].toLocaleString() : '' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ═══ 발주등록 모달 연동 ═══ -->
    <PurchaseOrderRegModal 
      :visible="showReg"
      :form="poForm"
      :plant-name="getPlantName(poForm.PLANTCD)"
      :products="products"
      :materials="materials"
      :prod-idx="prodIdx"
      @close="showReg = false"
      @save="submitPO"
      @open-plant-picker="openPlantPicker"
      @open-company-picker="openCompanyPicker"
      @add-product="addProduct"
      @remove-product="removeProduct"
      @open-product-picker="openProductPicker"
      @refresh-materials="refreshMaterials"
      @prod-click="onProdClick"
    />

    <!-- 공용 피커 -->
    <ItemPicker :visible="isGoodsPickerOpen" @close="isGoodsPickerOpen = false" @select="selectGoods" />
    <ItemPicker :visible="isMainItemPickerOpen" @close="isMainItemPickerOpen = false" @select="(g) => searchText = g.PARTNO" />
    <CompanyPicker :visible="isCompanyPickerOpen" :is-supplier="true" @close="isCompanyPickerOpen = false" @select="selectCompany" />
    
    <FormModal :visible="showPlantPicker" title="사업장 선택" icon="🏭" width="400px" @close="showPlantPicker=false" :showSave="false">
      <div class="picker-content">
        <div class="picker-search">
          <input type="text" v-model="plantSearch" placeholder="사업장코드 또는 명 검색" @keyup.enter="filterPlants" />
          <button class="btn-search" @click="filterPlants">조회</button>
        </div>
        <div class="picker-grid" style="height:300px;">
          <DataGrid :columns="[{key:'PLANTCD', label:'코드', width:'100px'}, {key:'PLANTNM', label:'사업장명'}]" :rows="filteredPlants" @row-click="selectPlant" />
        </div>
      </div>
    </FormModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'; 
import api from '../../../api';
import FormModal from '../../../components/common/FormModal.vue';
import DataGrid from '../../../components/common/DataGrid.vue';
import ItemPicker from '../../pickers/ItemPicker.vue';
import CompanyPicker from '../../pickers/CompanyPicker.vue';
import PurchaseOrderRegModal from '../../modals/PurchaseOrderRegModal.vue';

const d=new Date(); const f=(v:Date)=>v.toISOString().slice(0,10);
const baseDate=ref(f(d)),plantCd=ref(''),searchText=ref(''),plants=ref<any[]>([]);
const dateCols=ref<string[]>([]),pivotRows=ref<any[]>([]),selIdx=ref(-1);
const showReg=ref(false), loading=ref(false);
const poForm=ref({PLANTCD:'',COMPANYCD:'',COMPANYNM:'',ADOFREQDT:f(new Date(d.getTime()+86400000)),REMARK:''});
const products=ref<any[]>([]),materials=ref<any[]>([]),prodIdx=ref(-1);

const isGoodsPickerOpen = ref(false);
const isMainItemPickerOpen = ref(false);
const pickingProdIdx = ref(-1);
const showPlantPicker = ref(false);
const plantSearch = ref('');
const filteredPlants = ref<any[]>([]);
const isCompanyPickerOpen = ref(false);
const pickingMatIdx = ref(-1);

function openPlantPicker() { plantSearch.value = ''; filteredPlants.value = [...plants.value]; showPlantPicker.value = true; }
function filterPlants() { const s = plantSearch.value.toLowerCase(); filteredPlants.value = plants.value.filter(p => (p.PLANTCD?.toLowerCase().includes(s)) || (p.PLANTNM?.toLowerCase().includes(s))); }
function getPlantName(cd: string) { return plants.value.find((x: any) => x.PLANTCD === cd)?.PLANTNM || ''; }
function selectPlant(p: any) { poForm.value.PLANTCD = p.PLANTCD; showPlantPicker.value = false; }
function openProductPicker(idx: number) { pickingProdIdx.value = idx; isGoodsPickerOpen.value = true; }
function selectGoods(g: any) {
  if (pickingProdIdx.value >= 0) {
    const p = products.value[pickingProdIdx.value];
    p.PARTNO = g.PARTNO; p.PARTNM = g.PARTNM; p.UNIT = g.UNIT || ''; p.STANDARD = g.STANDARD || '';
    refreshMaterials();
  }
}
function openCompanyPicker(idx: number) { pickingMatIdx.value = idx; isCompanyPickerOpen.value = true; }
function selectCompany(c: any) {
  if (pickingMatIdx.value === -1) { poForm.value.COMPANYCD = c.COMPANYCD; poForm.value.COMPANYNM = c.COMPANYNM; }
  else { const m = materials.value[pickingMatIdx.value]; if (m) { m.COMPANYCD = c.COMPANYCD; m.COMPANYNM = c.COMPANYNM; } }
}
function genDateCols(){const cols:string[]=[];const b=new Date(baseDate.value);for(let i=0;i<14;i++){const dd=new Date(b);dd.setDate(dd.getDate()+i);cols.push(f(dd));}dateCols.value=cols;}
async function fetchPlants(){try{const r=await api.get('/api/master/plant',{params:{size:100}});plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}catch{}}
async function fetchData(){
  genDateCols();
  loading.value = true;
  try{
    const p:any={};if(plantCd.value)p.plant_cd=plantCd.value;
    p.start_date=dateCols.value[0];p.end_date=dateCols.value[dateCols.value.length-1];
    if(searchText.value)p.search=searchText.value;
    const r=await api.get('/api/purchase/plan',{params:p});
    const raw = Array.isArray(r.data) ? r.data : (r.data?.data || []);
    const map:Record<string,any>={};
    for(const row of raw){
      const key = `${row.ORDERNUM}_${row.PARTNO}`;
      if(!map[key]) {
        map[key]={ ORDERNUM:row.ORDERNUM, COMPANYNM:row.COMPANYNM, PARTNO:row.PARTNO, PARTNM:row.PARTNM, UNIT:row.UNIT, STANDARD:row.STANDARD, STOCKQTY:row.STOCKQTY||0, PLANTCD:row.PLANTCD||'', PLANTOTAL:0, dates:{} };
      }
      const dt=typeof row.PRODUCEDT==='string'?row.PRODUCEDT.slice(0,10):f(new Date(row.PRODUCEDT));
      map[key].dates[dt]=(map[key].dates[dt]||0)+(row.PRODUCEQTY||0);
      map[key].PLANTOTAL+=(row.PRODUCEQTY||0);
    }
    pivotRows.value=Object.values(map);
  }catch(e){
    console.error('Fetch data error:', e);
  }finally{
    loading.value = false;
  }
}
async function openRegister(){
  if(selIdx.value >= 0 && pivotRows.value[selIdx.value]?.PLANTCD) { poForm.value.PLANTCD = pivotRows.value[selIdx.value].PLANTCD; }
  else if(plantCd.value) { poForm.value.PLANTCD = plantCd.value; }
  poForm.value.COMPANYCD = ''; poForm.value.COMPANYNM = ''; poForm.value.REMARK = '';
  if(selIdx.value>=0){
    const r=pivotRows.value[selIdx.value];
    products.value=[{PARTNO:r.PARTNO,PARTNM:r.PARTNM,UNIT:r.UNIT||'',STANDARD:r.STANDARD,QTY:r.PLANTOTAL,checked:false}];
    await refreshMaterials();
  }else{ products.value=[]; materials.value=[]; }
  showReg.value=true;
}
function addProduct(){ products.value.push({PARTNO:'',PARTNM:'',UNIT:'',STANDARD:'',QTY:0,checked:false}); }
function removeProduct(){ products.value=products.value.filter(p=>!p.checked); refreshMaterials(); }
async function refreshMaterials() {
  const matMap = new Map();
  for (const p of products.value) {
    if (!p.PARTNO || p.QTY <= 0) continue;
    try {
      const r = await api.get(`/api/purchase/bom/${p.PARTNO}`);
      const bomData = Array.isArray(r.data) ? r.data : (r.data?.data || []);
      for (const m of bomData) {
        const need = Math.ceil((m.REQQTY || 0) * (p.QTY || 0));
        if (matMap.has(m.PARTNO)) {
          const ext = matMap.get(m.PARTNO); ext.NEEDQTY += need;
          ext.ORDERQTY = Math.max(0, ext.NEEDQTY - (ext.STOCKQTY || 0));
        } else {
          matMap.set(m.PARTNO, { ...m, NEEDQTY: need, ORDERQTY: Math.max(0, need - (m.STOCKQTY || 0)), ADOFREQDT: poForm.value.ADOFREQDT, checked: true });
        }
      }
    } catch (e) { console.error(`Error fetching BOM for ${p.PARTNO}:`, e); }
  }
  materials.value = Array.from(matMap.values());
}
async function onProdClick(_:any,i:number){ prodIdx.value=i; }
async function submitPO() {
  if (!poForm.value.PLANTCD) { alert('사업장을 선택하세요.'); return; }
  const validMaterials = materials.value.filter((m:any) => m.checked && m.ORDERQTY > 0);
  if (validMaterials.length === 0) { alert('체크된 발주 대상 자재가 없거나 수량이 0입니다.'); return; }
  if (poForm.value.COMPANYCD) { validMaterials.forEach(m => { if (!m.COMPANYCD) { m.COMPANYCD = poForm.value.COMPANYCD; m.COMPANYNM = poForm.value.COMPANYNM; } }); }
  const suppliers = new Set(validMaterials.map((m:any) => m.COMPANYCD).filter(Boolean));
  if (suppliers.size === 0) { alert('선택된 자재에 공급사가 지정되지 않았습니다.'); return; }
  try {
    for (const compCd of suppliers) {
      const compMats = validMaterials.filter((m:any) => m.COMPANYCD === compCd);
      const payload = {
        PLANTCD: poForm.value.PLANTCD, COMPANYCD: compCd, ADOFREQDT: poForm.value.ADOFREQDT, REMARK: poForm.value.REMARK,
        details: compMats.map((m:any) => ({ PARTNO: m.PARTNO, ORDERQTY: m.ORDERQTY, UNIT_PRICE: m.UNIT_PRICE || 0, ADOFREQDT: m.ADOFREQDT || poForm.value.ADOFREQDT, REMARK: '' }))
      };
      await api.post('/api/purchase/order', payload);
    }
    alert('발주가 정상적으로 등록되었습니다.'); showReg.value = false; fetchData();
  } catch (e) { alert('발주 등록 중 오류가 발생했습니다.'); }
}
onMounted(()=>{fetchPlants();fetchData();});
</script>

<style scoped>
/* 페이지 레이아웃 */
.page-view{display:flex;flex-direction:column;gap:10px;height:100%}
.search-section{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}
.search-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.search-row label{font-size:.85rem;font-weight:600;color:#636e72;white-space:nowrap}
.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.85rem}
.input-with-btn{display:flex;gap:4px;align-items:center}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:6px;cursor:pointer;font-size:1rem;height:34px}
.btn-search{background:#667eea;color:#fff;border:none;padding:7px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}
.act-right{display:flex;gap:6px;margin-left:auto}
.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:7px 16px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}
.btn-excel{background:#27ae60;color:#fff;border:none;padding:7px 14px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.84rem}

/* 그리드 레이아웃 */
.split-grids{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.grid-wrap{display:flex;flex-direction:column;background:#fff;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden;flex:1}
.dh{padding:10px 16px;background:#f8f9fa;font-size:.85rem;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.cal-grid-wrap{flex:1;overflow:auto}
.cal-grid{width:100%;border-collapse:collapse;font-size:.82rem}
.cal-grid thead{position:sticky;top:0;z-index:10}
.cal-grid th{background:#f8fafc;color:#64748b;font-weight:700;padding:12px 10px;border-bottom:2px solid #f1f5f9;text-align:left}
.cal-grid td{padding:10px;border-bottom:1px solid #f1f5f9;color:#334155}
.cal-grid .fix{position:sticky;left:0;background:#f8fafc;z-index:11;border-right:1px solid #f1f5f9}
.cal-grid tbody .fix{background:#fff}
.cal-grid .num{text-align:right}
.cal-grid .center{text-align:center}
.cal-grid .total-head{background:#eff6ff!important;color:#1e40af}
.cal-grid .total-cell{color:#2563eb;font-weight:800;background:#eff6ff}
.date-col{min-width:70px;text-align:center;border-left:1px solid #f1f5f9}
.date-col .sub{font-size:.7rem;color:#94a3b8;font-weight:600}
.hasval{background:#f0fdf4;color:#166534;font-weight:700}
.badge-unit{background:#f1f5f9;color:#475569;padding:1px 6px;border-radius:8px;font-size:.68rem;font-weight:700}
.cal-grid tbody tr:hover td{background:#fbfcfe;cursor:pointer}
.cal-grid tbody tr.selected td{background:#f1f5f9!important}
.empty{text-align:center;padding:80px!important;color:#94a3b8;font-size:1rem}

/* Picker Specific */
.picker-content { display: flex; flex-direction: column; gap: 12px; }
.picker-search { display: flex; gap: 8px; padding: 12px 20px; }
.picker-search input { flex: 1; padding: 8px 12px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: .88rem; }
.picker-grid { flex: 1; overflow: auto; padding: 0 20px 16px; }
</style>
