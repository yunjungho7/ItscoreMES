<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">품목관리</div>
      <div class="search-row">
        <label>품목코드</label><input type="text" v-model="searchCd" placeholder="품번" @keyup.enter="fetchData"/>
        <label>품목명</label><input type="text" v-model="searchNm" placeholder="품명" @keyup.enter="fetchData"/>
        <label>규격</label><input type="text" v-model="searchStd" placeholder="규격" @keyup.enter="fetchData"/>
        <label>품목구분</label>
        <select v-model="searchType" @change="fetchData">
          <option value="">전체</option>
          <option v-for="code in partTypes" :key="code.CODECD" :value="code.CODENM">{{ code.CODENM }}</option>
        </select>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'품목 수정':'품목 등록'" width="960px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg4">
        <div class="ff"><label>품번</label><input v-model="form.PARTNO" :disabled="editMode"/></div>
        <div class="ff"><label>품명</label><input v-model="form.PARTNM"/></div>
        <div class="ff"><label>규격</label><input v-model="form.STANDARD"/></div>
        <div class="ff">
          <label>품목구분</label>
          <select v-model="form.PARTTYPE">
            <option value="">선택</option>
            <option v-for="code in partTypes" :key="code.CODECD" :value="code.CODENM">{{ code.CODENM }}</option>
          </select>
        </div>
        <div class="ff"><label>단위</label><input v-model="form.UNIT"/></div>
        <div class="ff"><label>LOT기준수량</label><input type="number" v-model.number="form.LOTSTDQTY"/></div>
        <div class="ff"><label>박스당수량</label><input type="number" v-model.number="form.QTYPERBOX"/></div>
        <div class="ff"><label>안전재고</label><input type="number" v-model.number="form.SAFETYSTOCK"/></div>
        <div class="ff"><label>단가</label><input type="number" v-model.number="form.UNIT_PRICE"/></div>
        <div class="ff"><label>공정</label><input v-model="form.PROCESSCD"/></div>
        <div class="ff"><label>Location(보관)</label><input v-model="form.LOCATIONCD"/></div>
        <div class="ff"><label>Location(투입)</label><input v-model="form.LOCATIONCD_PROD"/></div>
        <div class="ff"><label>거래처</label><input v-model="form.COMPANYCD"/></div>
        <div class="ff"><label>차종</label><input v-model="form.CARTYPE"/></div>
        <div class="ff"><label>재질</label><input v-model="form.TEXTURE"/></div>
        <div class="ff"><label>사용여부</label><select v-model="form.USEYN"><option :value="true">사용</option><option :value="false">미사용</option></select></div>
      </div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue'; import FormModal from '../../../components/common/FormModal.vue';
const columns=[{key:'PARTNO',label:'품번',width:'130px'},{key:'PARTNM',label:'품명',minWidth:'140px'},{key:'STANDARD',label:'규격',width:'120px'},{key:'PARTTYPE',label:'품목구분',width:'90px'},{key:'UNIT',label:'단위',width:'60px'},{key:'LOTSTDQTY',label:'LOT기준수량',width:'100px'},{key:'QTYPERBOX',label:'박스당수량',width:'90px'},{key:'INTESTYN',label:'수입검사',width:'80px',type:'boolean'},{key:'LOCATIONCD',label:'Location(보관)',width:'110px'},{key:'PROCESSCD',label:'공정',width:'90px'}];
const searchCd=ref('');const searchNm=ref('');const searchStd=ref('');const searchType=ref('');const items=ref<any[]>([]);const loading=ref(false);const page=ref(1);const totalPages=ref(0);const total=ref(0);const selectedIdx=ref(-1);const editMode=ref(false);const showModal=ref(false);
const allCodes=ref<any[]>([]);

const partTypes = computed(() => allCodes.value.filter(c => c.PAR_CODECD === 'PARTGUBUN000').sort((a,b)=>a.ORD - b.ORD));

const emptyForm={PARTNO:'',PARTNM:'',STANDARD:'',PARTTYPE:'',UNIT:'',LOTSTDQTY:0,QTYPERBOX:0,SAFETYSTOCK:0,UNIT_PRICE:0,PROCESSCD:'',LOCATIONCD:'',LOCATIONCD_PROD:'',COMPANYCD:'',CARTYPE:'',TEXTURE:'',USEYN:true as boolean};const form=reactive({...emptyForm});

async function fetchCodes(){
  try{
    const r=await api.get('/api/master/code',{params:{size:9999}});
    allCodes.value=r.data.data||[];
  }catch(e){console.error(e);}
}

async function fetchData(){loading.value=true;try{const p:any={page:page.value,size:50};if(searchNm.value)p.search=searchNm.value;if(searchType.value)p.parttype=searchType.value;const r=await api.get('/api/master/goods',{params:p});items.value=r.data.data;total.value=r.data.total;totalPages.value=r.data.totalPages;selectedIdx.value=-1;}finally{loading.value=false;}}
function onRowClick(row:any,idx:number){selectedIdx.value=idx;editMode.value=true;Object.assign(form,row);showModal.value=true;}
function onPageChange(p:number){page.value=p;fetchData();}
function openAdd(){editMode.value=false;Object.assign(form,{...emptyForm});showModal.value=true;}
async function handleSave(){if(!form.PARTNO){alert('품번을 입력하세요.');return;}try{if(editMode.value){await api.put(`/api/master/goods/${form.PARTNO}`,form);alert('수정되었습니다.');}else{await api.post('/api/master/goods',form);alert('등록되었습니다.');}showModal.value=false;fetchData();}catch(e){}}
async function handleDelete(){if(!confirm(`'${form.PARTNM}' 삭제하시겠습니까?`))return;try{await api.delete(`/api/master/goods/${form.PARTNO}`);alert('삭제되었습니다.');showModal.value=false;fetchData();}catch(e){}}
onMounted(()=>{
  fetchCodes().then(fetchData);
});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.88rem}.search-row input{width:130px}.search-row input:focus,.search-row select:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled{background:#f8fafc;color:#94a3b8}
</style>
