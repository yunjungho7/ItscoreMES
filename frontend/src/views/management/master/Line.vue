<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">라인관리</div>
      <div class="search-row">
        <label>라인명</label><input type="text" v-model="searchNm" placeholder="라인명 검색" @keyup.enter="fetchData"/>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'라인 수정':'라인 등록'" width="560px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg"><div class="ff"><label>라인코드</label><input v-model="form.LINECD" :disabled="editMode"/></div><div class="ff"><label>라인명</label><input v-model="form.LINENM"/></div><div class="ff"><label>공장</label><select v-model="form.FACTORYCD"><option value="">선택</option><option v-for="f in factories" :key="f.FACTORYCD" :value="f.FACTORYCD">{{f.FACTORYNM}}</option></select></div><div class="ff"><label>라인구분</label><input v-model="form.LINEDIV"/></div><div class="ff"><label>상위라인</label><select v-model="form.PAR_LINECD"><option value="">없음</option><option v-for="l in allLines" :key="l.LINECD" :value="l.LINECD">{{l.LINENM}}</option></select></div><div class="ff"><label>사용여부</label><select v-model="form.USEYN"><option value="Y">사용</option><option value="N">미사용</option></select></div></div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue'; import FormModal from '../../../components/common/FormModal.vue';
const columns=[{key:'FACTORYCD',label:'공장',width:'100px'},{key:'LINECD',label:'라인코드',width:'120px'},{key:'LINENM',label:'라인명',minWidth:'160px'},{key:'LINEDIV',label:'라인구분',width:'100px'},{key:'USEYN',label:'사용여부',width:'80px'},{key:'REGDTM',label:'등록일',width:'110px',type:'date'},{key:'REGUSERID',label:'등록자',width:'80px'}];
const searchNm=ref('');const items=ref<any[]>([]);const factories=ref<any[]>([]);const allLines=ref<any[]>([]);const loading=ref(false);const page=ref(1);const totalPages=ref(0);const total=ref(0);const selectedIdx=ref(-1);const editMode=ref(false);const showModal=ref(false);
const emptyForm={LINECD:'',LINENM:'',FACTORYCD:'',LINEDIV:'',PAR_LINECD:'',USEYN:'Y'};const form=reactive({...emptyForm});
async function fetchFactories(){const r=await api.get('/api/master/factory',{params:{size:999}});factories.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}
async function fetchAllLines(){const r=await api.get('/api/master/line',{params:{size:999}});allLines.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}
async function fetchData(){loading.value=true;try{const p:any={page:page.value,size:50};if(searchNm.value)p.search=searchNm.value;const r=await api.get('/api/master/line',{params:p});items.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));total.value=(r.data?.data?.total ?? r.data?.total ?? 0);totalPages.value=(r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);selectedIdx.value=-1;}finally{loading.value=false;}}
function onRowClick(row:any,idx:number){selectedIdx.value=idx;editMode.value=true;Object.assign(form,row);showModal.value=true;}
function onPageChange(p:number){page.value=p;fetchData();}
function openAdd(){editMode.value=false;Object.assign(form,{...emptyForm});showModal.value=true;}
async function handleSave(){if(!form.LINECD||!form.LINENM){alert('라인코드와 라인명을 입력하세요.');return;}try{if(editMode.value){await api.put(`/api/master/line/${form.LINECD}`,form);alert('수정되었습니다.');}else{await api.post('/api/master/line',form);alert('등록되었습니다.');}showModal.value=false;fetchData();fetchAllLines();}catch(e){}}
async function handleDelete(){if(!confirm(`'${form.LINENM}' 삭제하시겠습니까?`))return;try{await api.delete(`/api/master/line/${form.LINECD}`);alert('삭제되었습니다.');showModal.value=false;fetchData();fetchAllLines();}catch(e){}}
onMounted(()=>{fetchFactories();fetchAllLines();fetchData();});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px}.search-row label{font-size:.85rem;font-weight:600;color:#636e72}.search-row input{flex:0 1 200px;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}.search-row input:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled{background:#f8fafc;color:#94a3b8}
</style>
