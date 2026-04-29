<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title"><i class="fas fa-list-alt"></i> 발주 대상 (생산계획)</div>
      <div class="search-row">
        <label>생산기준일</label>
        <input type="date" v-model="baseDate" />
        <label>사업장</label>
        <select v-model="plantCd"><option value="">전체</option><option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option></select>
        <label>품번/품명</label>
        <input type="text" v-model="searchText" placeholder="검색어 입력" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData"><i class="fas fa-search"></i> 조회</button>
        <div class="act-right">
          <button class="btn-po" @click="openRegister"><i class="fas fa-plus"></i> 발주등록</button>
          <button class="btn-excel"><i class="fas fa-file-excel"></i> 엑셀다운로드</button>
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
      <div class="modal-box">
        <div class="modal-title">
          <span><i class="fas fa-file-invoice" style="margin-right:8px; color:#60a5fa;"></i>발주 등록</span>
          <div class="modal-actions">
            <button class="btn-po" @click="submitPO"><i class="fas fa-save" style="margin-right:4px;"></i>발주등록</button>
            <button class="btn-close" @click="showReg=false"><i class="fas fa-times" style="margin-right:4px;"></i>닫기</button>
          </div>
        </div>
        
        <div class="modal-content-wrap">
          <div class="form-row">
            <div class="lbl-wrap"><i class="fas fa-circle-notch text-green"></i> 사업장</div>
            <div class="form-input-search" style="width:160px;">
              <input type="text" :value="getPlantName(poForm.PLANTCD)" readonly placeholder="선택" @click="openPlantPicker" />
              <button class="btn-search-form" @click="openPlantPicker">🔍</button>
            </div>
            
            <div class="lbl-wrap" style="margin-left: 10px;"><i class="fas fa-circle-notch text-green"></i> 납기요청일</div>
            <input type="date" v-model="poForm.ADOFREQDT" style="width:140px;"/>
            
            <div class="lbl-wrap" style="margin-left: 10px;"><i class="fas fa-circle-notch text-green"></i> 비고</div>
            <input type="text" v-model="poForm.REMARK" style="flex:1" placeholder="특이사항 입력" />
            
            <div style="display:flex; gap:8px; margin-left: 16px;">
              <button class="btn-add-row" @click="addProduct"><i class="fas fa-arrow-down" style="margin-right:6px;"></i> 추가</button>
              <button class="btn-del-row" @click="removeProduct"><i class="fas fa-cut" style="margin-right:6px;"></i> 제거</button>
            </div>
          </div>
          
          <!-- Upper Grid: Products -->
          <div class="tbl-wrap" style="height: 180px;">
            <table class="sub-tbl"><thead><tr>
              <th style="width:40px; text-align:center;">선택</th>
              <th style="width:200px;">품번</th>
              <th style="min-width:200px;">품명</th>
              <th style="width:80px; text-align:center;">단위</th>
              <th style="width:120px;">규격</th>
              <th style="width:130px;" class="num red">발주대상 수량</th>
            </tr></thead>
            <tbody><tr v-for="(p,i) in products" :key="i" :class="{selected:prodIdx===i}" @click="onProdClick(p,i)">
              <td style="text-align:center;">
                <span v-if="prodIdx===i" class="row-indicator">▶</span>
              </td>
              <td>
                <div class="input-with-btn">
                  <input type="text" v-model="p.PARTNO" readonly placeholder="품번 선택" @click="openProductPicker(i)" />
                  <button class="btn-search-sm" @click="openProductPicker(i)"><i class="fas fa-search"></i></button>
                </div>
              </td>
              <td>{{ p.PARTNM }}</td>
              <td><span class="badge">{{ p.UNIT }}</span></td>
              <td><span class="text-muted">{{ p.STANDARD }}</span></td>
              <td class="num">
                <input type="number" v-model.number="p.QTY" class="qty-input" @input="refreshMaterials" />
              </td>
            </tr>
            <tr v-if="products.length===0"><td colspan="6" class="empty">위 [추가] 버튼을 눌러 생산품목을 선택하세요.</td></tr>
            </tbody></table>
          </div>
          
          <div class="splitter"><i class="fas fa-link" style="color:#cbd5e1; margin:0 8px;"></i> BOM 소요 자재 전개</div>

          <!-- Lower Grid: Materials -->
          <div class="tbl-wrap" style="flex: 1;">
            <table class="sub-tbl"><thead><tr>
              <th style="width:40px; text-align:center;">
                <input type="checkbox" :checked="materials.length > 0 && materials.every(m=>m.checked)" @change="materials.forEach(m => m.checked = ($event.target as HTMLInputElement).checked)" />
              </th>
              <th style="width:110px;">자재품번</th>
              <th style="min-width:160px;">품명</th>
              <th style="width:180px;" class="red">공급사</th>
              <th style="width:60px; text-align:center;">단위</th>
              <th style="width:90px;" class="num red">단가</th>
              <th style="width:140px;" class="red">납기요청일</th>
              <th style="width:80px;" class="num">박스당수량</th>
              <th style="width:80px;" class="num">필요수량</th>
              <th style="width:100px;" class="num red">발주수량</th>
              <th style="width:80px;" class="num">재고수량</th>
              <th style="width:140px;">비고</th>
            </tr></thead>
            <tbody>
              <tr v-for="(m,i) in materials" :key="i" :class="{'checked-row': m.checked}">
                <td style="text-align:center;">
                  <input type="checkbox" v-model="m.checked"/>
                </td>
                <td class="font-bold">{{ m.PARTNO }}</td>
                <td>{{ m.PARTNM }}</td>
                <td>
                  <div class="input-with-btn" style="height:26px;">
                    <input type="text" v-model="m.COMPANYNM" readonly placeholder="공급사 선택" @click="openCompanyPicker(i)" style="font-size:0.8rem; padding:0 6px;" />
                    <button class="btn-search-sm" @click="openCompanyPicker(i)" style="padding:0 8px;"><i class="fas fa-search"></i></button>
                  </div>
                </td>
                <td><span class="badge">{{ m.UNIT }}</span></td>
                <td class="num">{{ m.UNIT_PRICE?.toLocaleString() }}</td>
                <td>
                  <input type="date" v-model="m.ADOFREQDT" class="qty-input" style="width:120px; text-align:left; font-size:0.8rem; font-weight:normal;" />
                </td>
                <td class="num text-muted">-</td>
                <td class="num">{{ m.NEEDQTY?.toLocaleString() }}</td>
                <td class="num">
                  <input type="number" v-model.number="m.ORDERQTY" class="qty-input highlight" />
                </td>
                <td class="num text-muted">{{ m.STOCKQTY?.toLocaleString() }}</td>
                <td><input type="text" class="ghost-input" placeholder="비고" /></td>
              </tr>
              <tr v-if="materials.length===0"><td colspan="12" class="empty">생산품목을 선택하고 수량을 입력하면 자재가 자동으로 전개됩니다.</td></tr>
            </tbody></table>
          </div>
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

    <!-- ═══ 사업장 선택 팝업 ═══ -->
    <Teleport to="body">
      <div v-if="showPlantPicker" class="modal-overlay-picker" @click.self="showPlantPicker=false">
        <div class="picker-modal" style="width: 400px;">
          <div class="picker-header">
            <h3>사업장 선택</h3>
            <button class="btn-close-sm" @click="showPlantPicker=false">✕</button>
          </div>
          <div class="picker-search">
            <input type="text" v-model="plantSearch" placeholder="사업장코드 또는 명 검색" @keyup.enter="filterPlants" />
            <button class="btn-search" @click="filterPlants">조회</button>
          </div>
          <div class="picker-list">
            <table class="picker-tbl">
              <thead><tr><th>사업장코드</th><th>사업장명</th></tr></thead>
              <tbody>
                <tr v-for="p in filteredPlants" :key="p.PLANTCD" @click="selectPlant(p)" class="clickable">
                  <td>{{ p.PLANTCD }}</td><td>{{ p.PLANTNM }}</td>
                </tr>
                <tr v-if="filteredPlants.length===0"><td colspan="2" class="empty">결과 없음</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Teleport>
    <!-- ═══ 공급사 선택 팝업 ═══ -->
    <Teleport to="body">
      <div v-if="showCompanyPicker" class="modal-overlay-picker" @click.self="showCompanyPicker=false">
        <div class="picker-modal" style="width: 500px;">
          <div class="picker-header">
            <h3>공급사 선택</h3>
            <button class="btn-close-sm" @click="showCompanyPicker=false">✕</button>
          </div>
          <div class="picker-search">
            <input type="text" v-model="companySearch" placeholder="공급사코드 또는 명 검색" @keyup.enter="filterCompanies" />
            <button class="btn-search" @click="filterCompanies">조회</button>
          </div>
          <div class="picker-list">
            <table class="picker-tbl">
              <thead><tr><th>공급사코드</th><th>공급사명</th><th>대표자명</th></tr></thead>
              <tbody>
                <tr v-for="c in filteredCompanies" :key="c.COMPANYCD" @click="selectCompany(c)" class="clickable">
                  <td>{{ c.COMPANYCD }}</td><td>{{ c.COMPANYNM }}</td><td>{{ c.CEONM }}</td>
                </tr>
                <tr v-if="filteredCompanies.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
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

const showPlantPicker = ref(false);
const plantSearch = ref('');
const filteredPlants = ref<any[]>([]);

const showCompanyPicker = ref(false);
const companySearch = ref('');
const pickingMatIdx = ref(-1);
const allCompanies = ref<any[]>([]);
const filteredCompanies = ref<any[]>([]);

function openPlantPicker() {
  plantSearch.value = '';
  filteredPlants.value = [...plants.value];
  showPlantPicker.value = true;
}

function filterPlants() {
  const s = plantSearch.value.toLowerCase();
  if (s) {
    filteredPlants.value = plants.value.filter(p => 
      (p.PLANTCD && p.PLANTCD.toLowerCase().includes(s)) ||
      (p.PLANTNM && p.PLANTNM.toLowerCase().includes(s))
    );
  } else {
    filteredPlants.value = [...plants.value];
  }
}

function getPlantName(cd: string) {
  const p = plants.value.find((x: any) => x.PLANTCD === cd);
  return p ? p.PLANTNM : '';
}

function selectPlant(p: any) {
  poForm.value.PLANTCD = p.PLANTCD;
  showPlantPicker.value = false;
}

async function fetchAllGoods() {
  try {
    const r = await api.get('/api/master/goods', { params: { size: 9999 } });
    allGoods.value = (r.data.data || []).filter((g: any) => g.PARTTYPE === 'PARTGUBUN001');
    filterGoods();
  } catch {}
}

async function fetchAllCompanies() {
  try {
    const r = await api.get('/api/master/company', { params: { size: 9999 } });
    allCompanies.value = r.data.data || [];
    filterCompanies();
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

function openCompanyPicker(idx: number) {
  pickingMatIdx.value = idx;
  companySearch.value = '';
  filterCompanies();
  showCompanyPicker.value = true;
}

function filterCompanies() {
  const s = companySearch.value.toLowerCase();
  if (s) {
    filteredCompanies.value = allCompanies.value.filter(c => 
      (c.COMPANYCD && c.COMPANYCD.toLowerCase().includes(s)) ||
      (c.COMPANYNM && c.COMPANYNM.toLowerCase().includes(s))
    );
  } else {
    filteredCompanies.value = [...allCompanies.value];
  }
}

function selectCompany(c: any) {
  const m = materials.value[pickingMatIdx.value];
  if (m) {
    m.COMPANYCD = c.COMPANYCD;
    m.COMPANYNM = c.COMPANYNM;
  }
  showCompanyPicker.value = false;
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
  const matMap = new Map();
  
  for (const p of products.value) {
    if (!p.PARTNO || p.QTY <= 0) continue;
    
    try {
      const r = await api.get(`/api/purchase/bom/${p.PARTNO}`);
      const bomData = r.data || [];
      
      for (const m of bomData) {
        const need = Math.ceil((m.REQQTY || 0) * (p.QTY || 0));
        if (matMap.has(m.PARTNO)) {
          const ext = matMap.get(m.PARTNO);
          ext.NEEDQTY += need;
          ext.ORDERQTY = Math.max(0, ext.NEEDQTY - (ext.STOCKQTY || 0));
        } else {
          matMap.set(m.PARTNO, {
            ...m,
            NEEDQTY: need,
            ORDERQTY: Math.max(0, need - (m.STOCKQTY || 0)),
            ADOFREQDT: poForm.value.ADOFREQDT,
            checked: true
          });
        }
      }
    } catch (e) {
      console.error(`Error fetching BOM for ${p.PARTNO}:`, e);
    }
  }
  
  materials.value = Array.from(matMap.values());
}

async function onProdClick(_:any,i:number){
  prodIdx.value=i;
}

async function submitPO() {
  if (!poForm.value.PLANTCD) {
    alert('사업장을 선택하세요.');
    return;
  }

  const validMaterials = materials.value.filter((m:any) => m.checked && m.ORDERQTY > 0);
  if (validMaterials.length === 0) {
    alert('체크된 발주 대상 자재가 없거나 수량이 0입니다.');
    return;
  }
  
  const suppliers = new Set(validMaterials.map((m:any) => m.COMPANYCD).filter(Boolean));
  if (suppliers.size === 0) {
    alert('선택된 자재에 공급사가 지정되지 않았습니다.');
    return;
  }

  try {
    for (const compCd of suppliers) {
      const compMats = validMaterials.filter((m:any) => m.COMPANYCD === compCd);
      const payload = {
        PLANTCD: poForm.value.PLANTCD,
        COMPANYCD: compCd,
        ADOFREQDT: poForm.value.ADOFREQDT,
        REMARK: poForm.value.REMARK,
        details: compMats.map((m:any) => ({
          PARTNO: m.PARTNO,
          ORDERQTY: m.ORDERQTY,
          UNIT_PRICE: m.UNIT_PRICE || 0,
          ADOFREQDT: m.ADOFREQDT || poForm.value.ADOFREQDT,
          REMARK: ''
        }))
      };
      await api.post('/api/purchase/order', payload);
    }
    alert('발주가 정상적으로 등록되었습니다.');
    showReg.value = false;
    fetchData();
  } catch (e) {
    alert('발주 등록 중 오류가 발생했습니다.');
  }
}
onMounted(()=>{fetchPlants();fetchData();fetchAllGoods();fetchAllCompanies();});
</script>
<style scoped>
.page-view { display: flex; flex-direction: column; gap: 16px; height: 100%; background: #f8fafc; }
.search-section { background: #fff; border-radius: 12px; padding: 18px 24px; box-shadow: 0 4px 12px rgba(0,0,0,.03); border: 1px solid #e2e8f0; }
.section-title { font-size: 1.1rem; font-weight: 800; color: #1e293b; letter-spacing: 0.5px; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; display:flex; align-items:center; }
.section-title i { margin-right: 8px; color: #3b82f6; }
.search-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.search-row label { font-size: 0.9rem; font-weight: 700; color: #475569; white-space: nowrap; }
.search-row input, .search-row select { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem; outline:none; transition: all 0.2s; background: #fff; }
.search-row input:focus, .search-row select:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
.search-row input[type=date] { width: 140px; }
.search-row input[type=text] { width: 160px; }
.search-row select { min-width: 130px; }
.btn-search { flex-shrink: 0; background: #64748b; color: #fff; border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.9rem; transition: background 0.2s; display:flex; align-items:center; gap:6px; }
.btn-search:hover { background: #475569; }
.act-right { display: flex; gap: 8px; margin-left: auto; }
.btn-excel { background: #10b981; color: #fff; border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.95rem; box-shadow: 0 4px 6px -1px rgba(16,185,129,0.2); transition: all 0.2s; display:flex; align-items:center; gap:6px; }
.btn-excel:hover { transform: translateY(-1px); box-shadow: 0 6px 8px -1px rgba(16,185,129,0.3); }

.cal-grid-wrap { flex: 1; overflow: auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.03); border: 1px solid #e2e8f0; }
.cal-grid { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.85rem; }
.cal-grid thead { position: sticky; top: 0; z-index: 2; }
.cal-grid th { background: #f1f5f9; color: #334155; font-weight: 700; padding: 12px 10px; border-bottom: 2px solid #cbd5e1; white-space: nowrap; text-align: left; }
.cal-grid td { padding: 10px 10px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.cal-grid .fix { position: sticky; left: 0; background: #f1f5f9; z-index: 3; }
.cal-grid .num { text-align: right; }
.cal-grid .total { color: #3b82f6; font-weight: 800; background: #eff6ff; }
.date-col { min-width: 60px; text-align: center; }
.date-col .sub { font-size: 0.75rem; color: #94a3b8; font-weight: 600; margin-top: 2px; }
.hasval { background: #f0fdf4; color: #166534; font-weight: 700; }
.cal-grid tbody tr { cursor: pointer; transition: background 0.15s; }
.cal-grid tbody tr:hover { background: #f8fafc; }
.cal-grid tbody tr.selected { background: #eff6ff; }
.empty { text-align: center; color: #94a3b8; padding: 60px 16px !important; font-size: 0.95rem; }.modal-overlay {
  position:fixed; inset:0; background:rgba(15, 23, 42, 0.4); z-index:1000;
  display:flex; align-items:center; justify-content:center;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-box {
  background:#ffffff; border-radius:16px; width:1000px; height:85vh; max-height:85vh;
  display:flex; flex-direction:column;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  overflow:hidden;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-title {
  display:flex; justify-content:space-between; align-items:center;
  padding:16px 24px; font-size:1.25rem; font-weight:800;
  background: linear-gradient(135deg, #1e293b, #0f172a);
  color: #fff;
  letter-spacing: 0.5px;
}
.modal-actions { display:flex; gap:8px; }
.btn-po {
  background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff;
  border: none; padding: 8px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 10px rgba(59,130,246,0.3); transition: all 0.2s; font-size: 0.95rem;
  display:flex; align-items:center;
}
.btn-po:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(59,130,246,0.4); }
.btn-close {
  background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2);
  padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s;
  display:flex; align-items:center;
}
.btn-close:hover { background: rgba(255,255,255,0.2); }

.modal-content-wrap {
  padding: 24px; overflow-y:auto; flex:1; background: #f8fafc;
  display: flex; flex-direction: column; gap: 16px;
}

.form-row {
  display:flex; align-items:center; gap:8px;
  background:#fff; border-radius: 12px; padding: 14px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0;
}
.lbl-wrap { display:flex; align-items:center; gap:6px; font-size:0.9rem; font-weight:700; color:#334155; }
.text-green { color: #10b981; font-size: 0.8rem; }
.form-row input[type=text], .form-row input[type=date] {
  padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem;
  transition: all 0.2s ease; outline: none; background: #f8fafc;
}
.form-row input:focus { background: #fff; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }
.form-input-search { display:flex; gap:6px; }
.form-input-search input { flex:1; min-width:0; cursor:pointer; }
.btn-search-form { flex-shrink:0; background:#64748b; color:#fff; border:none; padding:0 12px; border-radius:8px; cursor:pointer; transition: background 0.2s; }
.btn-search-form:hover { background:#475569; }

.btn-add-row {
  background: linear-gradient(135deg, #10b981, #059669); color: #fff;
  border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 6px -1px rgba(16,185,129,0.2); transition: all 0.2s; display:flex; align-items:center;
}
.btn-add-row:hover { transform: translateY(-1px); box-shadow: 0 6px 8px -1px rgba(16,185,129,0.3); }

.btn-del-row {
  background: #fff; color: #ef4444; border: 1px solid #fca5a5; padding: 8px 16px; border-radius: 8px; 
  font-weight: 600; cursor: pointer; transition: all 0.2s; display:flex; align-items:center;
}
.btn-del-row:hover { background: #fef2f2; border-color: #ef4444; }

.tbl-wrap {
  background: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0; overflow-y: auto; display:flex; flex-direction: column;
}
.sub-tbl { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.sub-tbl thead { position: sticky; top: 0; z-index: 2; }
.sub-tbl thead th {
  background: #f1f5f9; color: #475569; font-weight: 700; padding: 12px 10px;
  border-bottom: 2px solid #cbd5e1; text-align: left; white-space: nowrap;
}
.sub-tbl thead th.red { color: #ef4444; }
.sub-tbl tbody td {
  padding: 10px 10px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle;
}
.sub-tbl tbody tr { transition: background 0.15s; }
.sub-tbl tbody tr:hover { background: #f8fafc; }
.sub-tbl tbody tr.selected { background: #eff6ff; }
.sub-tbl tbody tr.checked-row { background: #f0fdf4; }

.qty-input {
  width: 100%; padding: 6px 8px; border: 1px solid #cbd5e1; border-radius: 6px;
  text-align: right; font-weight: 700; color: #0f172a; outline: none; transition: all 0.2s;
}
.qty-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.qty-input.highlight { border-color: #fca5a5; color: #ef4444; background: #fff5f5; }
.qty-input.highlight:focus { border-color: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.1); }

.ghost-input {
  width: 100%; border: none; background: transparent; padding: 4px; font-size: 0.85rem;
  border-bottom: 1px solid transparent; transition: all 0.2s; outline:none;
}
.ghost-input:focus { border-bottom-color: #3b82f6; }

.splitter {
  text-align: center; color: #64748b; font-size: 0.8rem; font-weight:600;
  display: flex; align-items: center; justify-content: center; margin: 4px 0;
}
.splitter::before, .splitter::after { content: ""; flex: 1; height: 1px; background: #e2e8f0; margin: 0 16px; }

.badge { background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight:600; }
.text-muted { color: #94a3b8; }
.font-bold { font-weight: 700; color: #0f172a; }
.row-indicator { font-size: 0.8rem; color: #3b82f6; }
/* ═══ 품목 선택 팝업 ═══ */
.modal-overlay-picker{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1100;display:flex;align-items:center;justify-content:center}
.picker-modal{background:#fff;border-radius:10px;width:500px;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.2);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.picker-header h3{margin:0;font-size:1.05rem;font-weight:700;color:#2c3e50}
.btn-close-sm{background:none;border:none;font-size:1.2rem;cursor:pointer;color:#95a5a6}
.btn-close-sm:hover{color:#e74c3c}
.picker-search{display:flex;gap:8px;padding:14px 20px;background:#fff;border-bottom:1px solid #e9ecef}
.picker-search input{flex:1;min-width:0;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}
.picker-list{flex:1;overflow-y:auto;padding:10px 20px 20px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{padding:8px 10px;background:#f1f5f9;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#e8f5e9}
.input-with-btn{display:flex;gap:4px;height: 30px;}
.input-with-btn input{flex:1;min-width:0;cursor:pointer;background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:0 8px;}
.btn-search-sm{flex-shrink:0;background:#667eea;color:#fff;border:none;padding:0 10px;border-radius:4px;cursor:pointer;font-size:0.9rem;}
.text-blue { color: #3b82f6; font-size: 0.75rem; }
.modal-box { display:flex; flex-direction:column; }

</style>
