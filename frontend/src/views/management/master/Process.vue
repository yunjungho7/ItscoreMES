<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">공정관리</div>
      <div class="search-row">
        <label>공정명</label><input type="text" v-model="searchNm" placeholder="공정명 검색" @keyup.enter="fetchData"/>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'공정 수정':'공정 등록'" width="640px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg">
        <div class="ff"><label>공정코드</label><input v-model="form.PROCESSCD" :disabled="editMode"/></div>
        <div class="ff"><label>공정명</label><input v-model="form.PROCESSNM"/></div>
        <div class="ff"><label>라인</label><select v-model="form.LINECD"><option value="">선택</option><option v-for="l in lines" :key="l.LINECD" :value="l.LINECD">{{l.LINENM}}</option></select></div>
        <div class="ff"><label>공장</label><select v-model="form.FACTORYCD"><option value="">선택</option><option v-for="f in factories" :key="f.FACTORYCD" :value="f.FACTORYCD">{{f.FACTORYNM}}</option></select></div>
        <div class="ff s2"><label>공정설명</label><input v-model="form.CONTENTS"/></div>
        <div class="ff"><label>사용여부</label><select v-model="form.USEYN"><option :value="true">사용</option><option :value="false">미사용</option></select></div>
      </div>
      <div class="opt-row">
        <label class="ck"><input type="checkbox" v-model="form.OEMYN"/>외주여부</label>
        <label class="ck"><input type="checkbox" v-model="form.MANUALGENERATEYN"/>개별작업지시</label>
        <label class="ck"><input type="checkbox" v-model="form.INSPECT_CREATEREPORTYN"/>자주검사성적서</label>
        <label class="ck"><input type="checkbox" v-model="form.INSPECT_APPLYFAILYN"/>자주검사불량실적</label>
        <label class="ck"><input type="checkbox" v-model="form.MOLDYN"/>금형사용</label>
        <label class="ck"><input type="checkbox" v-model="form.EXTERNALBARCODEYN"/>외부바코드</label>
      </div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../../../api'; import DataGrid from '../../../components/common/DataGrid.vue'; import FormModal from '../../../components/common/FormModal.vue';
const columns=[{key:'LINECD',label:'라인',width:'90px'},{key:'PROCESSCD',label:'공정코드',width:'110px'},{key:'PROCESSNM',label:'공정명',width:'140px'},{key:'CONTENTS',label:'공정설명',minWidth:'160px'},{key:'OEMYN',label:'외주',width:'65px',type:'boolean'},{key:'MANUALGENERATEYN',label:'개별작업',width:'75px',type:'boolean'},{key:'INSPECT_CREATEREPORTYN',label:'검사성적서',width:'85px',type:'boolean'},{key:'INSPECT_APPLYFAILYN',label:'검사불량',width:'75px',type:'boolean'},{key:'USEYN',label:'사용',width:'60px',type:'boolean'},{key:'REGDTM',label:'등록일',width:'100px',type:'date'}];
const searchNm=ref('');const items=ref<any[]>([]);const lines=ref<any[]>([]);const factories=ref<any[]>([]);const loading=ref(false);const page=ref(1);const totalPages=ref(0);const total=ref(0);const selectedIdx=ref(-1);const editMode=ref(false);const showModal=ref(false);
const emptyForm={PROCESSCD:'',PROCESSNM:'',LINECD:'',FACTORYCD:'',CONTENTS:'',USEYN:true as boolean,OEMYN:false as boolean,MANUALGENERATEYN:false as boolean,INSPECT_CREATEREPORTYN:false as boolean,INSPECT_APPLYFAILYN:false as boolean,MOLDYN:false as boolean,EXTERNALBARCODEYN:false as boolean};const form=reactive({...emptyForm});
async function fetchLines(){const r=await api.get('/api/master/line',{params:{size:999}});lines.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}
async function fetchFactories(){const r=await api.get('/api/master/factory',{params:{size:999}});factories.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));}
async function fetchData(){loading.value=true;try{const p:any={page:page.value,size:50};if(searchNm.value)p.search=searchNm.value;const r=await api.get('/api/master/process',{params:p});items.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));total.value=(r.data?.data?.total ?? r.data?.total ?? 0);totalPages.value=(r.data?.data?.totalPages ?? r.data?.totalPages ?? 0);selectedIdx.value=-1;}finally{loading.value=false;}}
function onRowClick(row:any,idx:number){selectedIdx.value=idx;editMode.value=true;Object.assign(form,row);showModal.value=true;}
function onPageChange(p:number){page.value=p;fetchData();}
function openAdd(){editMode.value=false;Object.assign(form,{...emptyForm});showModal.value=true;}
async function handleSave(){if(!form.PROCESSCD||!form.PROCESSNM){alert('공정코드와 공정명을 입력하세요.');return;}try{if(editMode.value){await api.put(`/api/master/process/${form.PROCESSCD}`,form);alert('수정되었습니다.');}else{await api.post('/api/master/process',form);alert('등록되었습니다.');}showModal.value=false;fetchData();}catch(e){}}
async function handleDelete(){if(!confirm(`'${form.PROCESSNM}' 삭제하시겠습니까?`))return;try{await api.delete(`/api/master/process/${form.PROCESSCD}`);alert('삭제되었습니다.');showModal.value=false;fetchData();}catch(e){}}
onMounted(()=>{fetchLines();fetchFactories();fetchData();});
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px}.search-row label{font-size:.85rem;font-weight:600;color:#636e72}.search-row input{flex:0 1 240px;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}.search-row input:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff.s2{grid-column:span 2}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled{background:#f8fafc;color:#94a3b8}
.opt-row{display:flex;flex-wrap:wrap;gap:16px;margin-top:16px;padding-top:14px;border-top:1px solid #f1f5f9}.ck{display:flex;align-items:center;gap:6px;font-size:.85rem;color:#334155;cursor:pointer}.ck input[type="checkbox"]{accent-color:#667eea;width:16px;height:16px}
</style>
