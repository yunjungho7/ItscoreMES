<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">공정별 작업자</div>
      <div class="search-row">
        <label>사번/이름</label><input type="text" v-model="searchNm" placeholder="사번 검색" @keyup.enter="fetchData"/>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'작업자 수정':'작업자 등록'" width="520px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg"><div class="ff"><label>사번 (USER_ID)</label><input v-model="form.USER_ID" :disabled="editMode"/></div><div class="ff"><label>공정</label><select v-model="form.PROCESS_ID" :disabled="editMode"><option value="">선택</option><option v-for="p in processes" :key="p.PROCESSCD" :value="p.PROCESSCD">{{p.PROCESSNM}} ({{p.PROCESSCD}})</option></select></div><div class="ff"><label>부여권한</label><input v-model="form.GRANTED_FUNCS" placeholder="READ,WRITE,DELETE"/></div><div class="ff"><label>제외권한</label><input v-model="form.EXCEPTED_FUNCS" placeholder="DELETE"/></div></div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue'; import FormModal from '../../../components/common/FormModal.vue';
const columns=[{key:'PROCESS_ID',label:'공정',width:'120px'},{key:'USER_ID',label:'사번',width:'120px'},{key:'GRANTED_FUNCS',label:'부여권한',minWidth:'200px'},{key:'EXCEPTED_FUNCS',label:'제외권한',minWidth:'200px'}];
const searchNm=ref('');const items=ref<any[]>([]);const processes=ref<any[]>([]);const loading=ref(false);const page=ref(1);const totalPages=ref(0);const total=ref(0);const selectedIdx=ref(-1);const editMode=ref(false);const showModal=ref(false);
const emptyForm={USER_ID:'',PROCESS_ID:'',GRANTED_FUNCS:'',EXCEPTED_FUNCS:''};const form=reactive({...emptyForm});
async function fetchProcesses(){const r=await api.get('/api/master/process',{params:{size:999}});processes.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}
async function fetchData(){loading.value=true;try{const p:any={page:page.value,size:50};if(searchNm.value)p.search=searchNm.value;const r=await api.get('/api/master/process-user',{params:p});items.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));total.value=(r.data?.data?.total ?? r.data?.total ?? 0);totalPages.value=(r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);selectedIdx.value=-1;}finally{loading.value=false;}}
function onRowClick(row:any,idx:number){selectedIdx.value=idx;editMode.value=true;Object.assign(form,row);showModal.value=true;}
function onPageChange(p:number){page.value=p;fetchData();}
function openAdd(){editMode.value=false;Object.assign(form,{...emptyForm});showModal.value=true;}
async function handleSave(){if(!form.USER_ID||!form.PROCESS_ID){alert('사번과 공정을 입력하세요.');return;}try{if(editMode.value){await api.put(`/api/master/process-user/${form.USER_ID}/${form.PROCESS_ID}`,form);alert('수정되었습니다.');}else{await api.post('/api/master/process-user',form);alert('등록되었습니다.');}showModal.value=false;fetchData();}catch(e){}}
async function handleDelete(){if(!confirm('작업자를 삭제하시겠습니까?'))return;try{await api.delete(`/api/master/process-user/${form.USER_ID}/${form.PROCESS_ID}`);alert('삭제되었습니다.');showModal.value=false;fetchData();}catch(e){}}
onMounted(()=>{fetchProcesses();fetchData();});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px}.search-row label{font-size:.85rem;font-weight:600;color:#636e72;min-width:70px}.search-row input{flex:0 1 240px;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}.search-row input:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled,.ff select:disabled{background:#f8fafc;color:#94a3b8}
</style>
