<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">거래처관리</div>
      <div class="search-row">
        <label>업체코드</label><input type="text" v-model="searchCd" placeholder="업체코드"/>
        <label>업체명</label><input type="text" v-model="searchNm" placeholder="업체명" @keyup.enter="fetchData"/>
        <label>업체구분</label>
        <select v-model="searchType" @change="fetchData">
          <option value="">전체</option>
          <option v-for="c in companyTypes" :key="c.CODECD" :value="c.CODENM">{{ c.CODENM }}</option>
        </select>
        <label>사용여부</label>
<select v-model="searchUse"><option value="">전체</option><option value="1">사용</option><option value="0">미사용</option></select>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'거래처 수정':'거래처 등록'" width="720px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg3">
        <div class="ff"><label class="required">업체코드</label><input v-model="form.COMPANYCD" :disabled="editMode"/></div>
        <div class="ff">
          <label class="required">사업장</label>
          <select v-model="form.PLANTCD">
            <option value="">선택</option>
            <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
          </select>
        </div>
        <div class="ff">
          <label>업체구분</label>
          <select v-model="form.COMPANYTYPE">
            <option value="">선택</option>
            <option v-for="c in companyTypes" :key="c.CODECD" :value="c.CODENM">{{ c.CODENM }}</option>
          </select>
        </div>
        <div class="ff s2"><label class="required">업체명</label><input v-model="form.COMPANYNM"/></div>
        <div class="ff"><label>업체약칭</label><input v-model="form.COMPANYNM2"/></div>
        <div class="ff"><label>사업자번호</label><input v-model="form.BSNO"/></div>
        <div class="ff"><label>업종</label><input v-model="form.BSSECTORS"/></div>
        <div class="ff"><label>대표자</label><input v-model="form.CEONM"/></div>
        <div class="ff s3"><label>주소</label><input v-model="form.ADDR1"/></div>
        <div class="ff"><label>담당자</label><input v-model="form.MANAGER"/></div>
        <div class="ff"><label>전화번호</label><input v-model="form.TEL"/></div>
        <div class="ff"><label>이메일</label><input v-model="form.EMAIL"/></div>
        <div class="ff"><label>사용여부</label><select v-model="form.USEYN"><option :value="true">사용</option><option :value="false">미사용</option></select></div>
      </div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue'; import FormModal from '../../../components/common/FormModal.vue';
const columns=[{key:'COMPANYCD',label:'업체코드',width:'110px'},{key:'COMPANYNM',label:'업체명',minWidth:'160px'},{key:'COMPANYTYPE',label:'업체구분',width:'90px'},{key:'BSNO',label:'사업자번호',width:'130px'},{key:'BSSECTORS',label:'업종',width:'120px'},{key:'MANAGER',label:'담당자',width:'90px'},{key:'USEYN',label:'사용여부',width:'80px',type:'boolean'}];
const searchCd=ref('');const searchNm=ref('');const searchType=ref('');const searchUse=ref('');const items=ref<any[]>([]);const loading=ref(false);const page=ref(1);const totalPages=ref(0);const total=ref(0);const selectedIdx=ref(-1);const editMode=ref(false);const showModal=ref(false);
const allCodes=ref<any[]>([]);
const plants=ref<any[]>([]);
const companyTypes = computed(() => allCodes.value.filter(c => c.PAR_CODECD === 'CMPGUBUN000').sort((a,b)=>a.ORD - b.ORD));

const emptyForm={COMPANYCD:'',PLANTCD:'',COMPANYTYPE:'',COMPANYNM:'',COMPANYNM2:'',BSNO:'',BSSECTORS:'',CEONM:'',ADDR1:'',MANAGER:'',TEL:'',EMAIL:'',USEYN:true as boolean};const form=reactive({...emptyForm});

async function fetchCodes(){
  try{
    const r=await api.get('/api/master/code',{params:{size:9999}});
    allCodes.value=r.data.data||[];
  }catch(e){console.error(e);}
}

async function fetchPlants(){
  try{
    const r=await api.get('/api/master/plant',{params:{size:100}});
    plants.value=r.data.data||[];
  }catch(e){console.error(e);}
}

async function fetchData(){loading.value=true;try{const p:any={page:page.value,size:50};if(searchNm.value)p.search=searchNm.value;if(searchType.value)p.company_type=searchType.value;const r=await api.get('/api/master/company',{params:p});items.value=r.data.data;total.value=r.data.total;totalPages.value=r.data.totalPages;selectedIdx.value=-1;}finally{loading.value=false;}}
function onRowClick(row:any,idx:number){selectedIdx.value=idx;editMode.value=true;Object.assign(form,row);showModal.value=true;}
function onPageChange(p:number){page.value=p;fetchData();}
function openAdd(){editMode.value=false;Object.assign(form,{...emptyForm});showModal.value=true;}
async function handleSave(){
  if(!form.COMPANYCD){alert('업체코드를 입력하세요.');return;}
  if(!form.PLANTCD){alert('사업장을 선택하세요.');return;}
  if(!form.COMPANYTYPE){alert('업체구분을 선택하세요.');return;}
  if(!form.COMPANYNM){alert('업체명을 입력하세요.');return;}
  try{
    if(editMode.value){await api.put(`/api/master/company/${form.COMPANYCD}`,form);alert('수정되었습니다.');}
    else{await api.post('/api/master/company',form);alert('등록되었습니다.');}
    showModal.value=false;fetchData();
  }catch(e){}
}
async function handleDelete(){if(!confirm(`'${form.COMPANYNM}' 삭제하시겠습니까?`))return;try{await api.delete(`/api/master/company/${form.COMPANYCD}`);alert('삭제되었습니다.');showModal.value=false;fetchData();}catch(e){}}
onMounted(()=>{
  Promise.all([fetchCodes(), fetchPlants()]).then(fetchData);
});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.search-row label{font-size:.85rem;font-weight:600;color:#636e72}.search-row input,.search-row select{padding:7px 10px;border:1px solid #dfe6e9;border-radius:6px;font-size:.88rem}.search-row input{width:140px}.search-row input:focus,.search-row select:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff.s2{grid-column:span 2}.ff.s3{grid-column:span 3}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff label.required::before{content:'◎ ';color:#27ae60}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled{background:#f8fafc;color:#94a3b8}
</style>
