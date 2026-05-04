<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">사업장관리</div>
      <div class="search-row">
        <label>사업장명</label>
        <input type="text" v-model="searchNm" placeholder="사업장명 검색" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx"
      :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange" />
    <FormModal :visible="showModal" :title="editMode ? '사업장 수정' : '사업장 등록'" width="680px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg"><div class="ff"><label>사업장코드</label><input v-model="form.PLANTCD" :disabled="editMode"/></div><div class="ff"><label>사업장명</label><input v-model="form.PLANTNM"/></div><div class="ff"><label>사업장구분</label><input v-model="form.PLANTTYPE"/></div><div class="ff"><label>사업자번호</label><input v-model="form.BUSINESSNO"/></div><div class="ff"><label>대표전화</label><input v-model="form.TEL"/></div><div class="ff"><label>FAX</label><input v-model="form.FAX"/></div><div class="ff s2"><label>주소</label><input v-model="form.ADDR1"/></div><div class="ff"><label>대표자명</label><input v-model="form.BOSSNM"/></div><div class="ff"><label>담당자</label><input v-model="form.PERSON_CHARGE"/></div><div class="ff"><label>사용여부</label><select v-model="form.USEYN"><option :value="true">사용</option><option :value="false">미사용</option></select></div></div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { 
  getPlantsApiMasterPlantGet, 
  createPlantApiMasterPlantPost,
  updatePlantApiMasterPlantPlantCdPut,
  deletePlantApiMasterPlantPlantCdDelete
} from '../../../api/generated/sdk.gen';
import DataGrid from '../../../components/common/DataGrid.vue';
import FormModal from '../../../components/common/FormModal.vue';

const columns = [
  { key: 'PLANTCD', label: '사업장코드', width: '120px' },{ key: 'PLANTNM', label: '사업장명', width: '150px' },{ key: 'PLANTTYPE', label: '사업장구분', width: '100px' },{ key: 'BUSINESSNO', label: '사업자번호', width: '130px' },{ key: 'TEL', label: '대표전화', width: '130px' },{ key: 'ADDR1', label: '주소', minWidth: '200px' },{ key: 'PERSON_CHARGE', label: '담당자', width: '100px' },{ key: 'USEYN', label: '사용여부', width: '80px', type: 'boolean' },
];
const searchNm = ref(''); const items = ref<any[]>([]); const loading = ref(false);
const page = ref(1); const totalPages = ref(0); const total = ref(0);
const selectedIdx = ref(-1); const editMode = ref(false); const showModal = ref(false);
const emptyForm = { PLANTCD:'',PLANTNM:'',PLANTTYPE:'',BUSINESSNO:'',TEL:'',FAX:'',ADDR1:'',ADDR2:'',BOSSNM:'',PERSON_CHARGE:'',USEYN:true as boolean };
const form = reactive({...emptyForm});

async function fetchData(){ 
  loading.value=true; 
  try { 
    const { data } = await getPlantsApiMasterPlantGet({
      query: {
        page: page.value,
        size: 50,
        search: searchNm.value || undefined
      }
    });
    if (data) {
      items.value = (data as any).data || [];
      total.value = (data as any).total || 0;
      totalPages.value = (data as any).totalPages || 1;
    }
    selectedIdx.value=-1; 
  } finally { 
    loading.value=false; 
  } 
}

function onRowClick(row:any,idx:number){ selectedIdx.value=idx; editMode.value=true; Object.assign(form,row); showModal.value=true; }
function onPageChange(p:number){ page.value=p; fetchData(); }
function openAdd(){ editMode.value=false; Object.assign(form,{...emptyForm}); showModal.value=true; }

async function handleSave(){ 
  if(!form.PLANTCD){alert('사업장코드를 입력하세요.');return;} 
  try { 
    if (editMode.value) {
      await updatePlantApiMasterPlantPlantCdPut({
        path: { plant_cd: form.PLANTCD },
        body: form as any
      });
      alert('수정되었습니다.');
    } else {
      await createPlantApiMasterPlantPost({
        body: form as any
      });
      alert('등록되었습니다.');
    } 
    showModal.value=false; 
    fetchData(); 
  } catch(e) {} 
}

async function handleDelete(){ 
  if(!confirm(`'${form.PLANTNM}' 삭제하시겠습니까?`))return; 
  try {
    await deletePlantApiMasterPlantPlantCdDelete({
      path: { plant_cd: form.PLANTCD }
    });
    alert('삭제되었습니다.');
    showModal.value=false;
    fetchData();
  } catch(e) {} 
}
onMounted(fetchData);
</script>
<style scoped>
.page-view{display:flex;flex-direction:column;gap:16px;height:100%}.search-section{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.04)}.section-title{font-size:.82rem;font-weight:700;color:#667eea;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid #f0f4ff}.search-row{display:flex;align-items:center;gap:10px}.search-row label{font-size:.88rem;font-weight:600;color:#636e72}.search-row input{flex:0 1 240px;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}.search-row input:focus{border-color:#667eea;outline:none}.btn-search{background:#667eea;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem}.btn-add{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;padding:8px 18px;border-radius:6px;font-weight:600;cursor:pointer;font-size:.88rem;margin-left:auto}
.fg{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 18px}.ff{display:flex;flex-direction:column;gap:5px}.ff.s2{grid-column:span 2}.ff label{font-size:.82rem;font-weight:600;color:#64748b}.ff input,.ff select{padding:9px 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:.88rem;transition:border-color .15s}.ff input:focus,.ff select:focus{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,.1)}.ff input:disabled{background:#f8fafc;color:#94a3b8}
</style>
