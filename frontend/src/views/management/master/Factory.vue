<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">공장관리</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="searchPlantCd" @change="fetchData">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        <label>공장명</label><input type="text" v-model="searchNm" placeholder="공장명 검색" @keyup.enter="fetchData"/>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>
    <DataGrid :columns="columns" :rows="items" :loading="loading" :selectedIndex="selectedIdx" :page="page" :totalPages="totalPages" :total="total" @row-click="onRowClick" @page-change="onPageChange"/>
    <FormModal :visible="showModal" :title="editMode?'공장 수정':'공장 등록'" width="480px" :showDelete="editMode" @close="showModal=false" @save="handleSave" @delete="handleDelete">
      <div class="fg">
        <div class="ff">
          <label>사업장</label>
          <select v-model="form.PLANTCD" :disabled="editMode" @change="onPlantChange">
            <option value="">사업장 선택</option>
            <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }} ({{ p.PLANTCD }})</option>
          </select>
        </div>
        <div class="ff">
          <label>공장코드</label>
          <input v-model="form.FACTORYCD" :disabled="editMode" placeholder="자동 생성되거나 직접 입력할 수 있습니다."/>
        </div>
        <div class="ff">
          <label>공장명</label>
          <input v-model="form.FACTORYNM" placeholder="공장명 입력"/>
        </div>
        <div class="ff">
          <label>사용여부</label>
          <select v-model="form.USEYN">
            <option :value="true">사용</option>
            <option :value="false">미사용</option>
          </select>
        </div>
      </div>
    </FormModal>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { 
  getPlantsApiMasterPlantGet, 
  getFactoriesApiMasterFactoryGet,
  createFactoryApiMasterFactoryPost,
  updateFactoryApiMasterFactoryFactoryCdPut,
  deleteFactoryApiMasterFactoryFactoryCdDelete,
  getNextCodeApiMasterFactoryNextCodePlantCdGet
} from '../../../api/generated/sdk.gen';
import DataGrid from '../../../components/common/DataGrid.vue'; 
import FormModal from '../../../components/common/FormModal.vue';

const plants = ref<any[]>([]);
const columns = [
  { key: 'PLANTCD', label: '사업장', width: '120px' },
  { key: 'FACTORYCD', label: '공장코드', width: '140px' },
  { key: 'FACTORYNM', label: '공장명', minWidth: '200px' },
  { key: 'USEYN', label: '사용여부', width: '90px', type: 'boolean' },
  { key: 'REGDTM', label: '등록일', width: '110px', type: 'date' },
  { key: 'REGUSERID', label: '등록자', width: '80px' }
];

const searchPlantCd = ref('');
const searchNm = ref('');
const items = ref<any[]>([]);
const loading = ref(false);
const page = ref(1);
const totalPages = ref(0);
const total = ref(0);
const selectedIdx = ref(-1);
const editMode = ref(false);
const showModal = ref(false);

const emptyForm = { PLANTCD: '', FACTORYCD: '', FACTORYNM: '', USEYN: true as boolean };
const form = reactive({ ...emptyForm });

async function fetchPlants() {
  try {
    const { data } = await getPlantsApiMasterPlantGet({ query: { size: 100 } });
    if (data) {
      plants.value = (data as any).data || [];
    }
  } catch (e) {
    console.error('사업장 조회 중 오류:', e);
  }
}

async function fetchData() {
  loading.value = true;
  try {
    const { data } = await getFactoriesApiMasterFactoryGet({
      query: {
        page: page.value,
        size: 50,
        search: searchNm.value || undefined,
        plant_cd: searchPlantCd.value || undefined
      }
    });
    if (data) {
      items.value = (data as any).data || [];
      total.value = (data as any).total || 0;
      totalPages.value = (data as any).totalPages || 1;
    }
    selectedIdx.value = -1;
  } catch (e) {
    console.error('공장 조회 중 오류:', e);
  } finally {
    loading.value = false;
  }
}

async function onPlantChange() {
  if (editMode.value) return;
  if (!form.PLANTCD) {
    form.FACTORYCD = '';
    return;
  }
  try {
    const { data } = await getNextCodeApiMasterFactoryNextCodePlantCdGet({
      path: { plant_cd: form.PLANTCD }
    });
    if (data) {
      form.FACTORYCD = (data as any).nextCode;
    }
  } catch (e) {
    console.error('공장코드 채번 중 오류:', e);
  }
}

function onRowClick(row: any, idx: number) {
  selectedIdx.value = idx;
  editMode.value = true;
  Object.assign(form, row);
  showModal.value = true;
}

function onPageChange(p: number) {
  page.value = p;
  fetchData();
}

function openAdd() {
  editMode.value = false;
  Object.assign(form, { ...emptyForm });
  showModal.value = true;
}

async function handleSave() {
  if (!form.PLANTCD) { alert('사업장을 선택하세요.'); return; }
  if (!form.FACTORYCD) { alert('공장코드를 입력하세요.'); return; }
  if (!form.FACTORYNM) { alert('공장명을 입력하세요.'); return; }

  try {
    if (editMode.value) {
      await updateFactoryApiMasterFactoryFactoryCdPut({
        path: { factory_cd: form.FACTORYCD },
        body: form as any
      });
      alert('수정되었습니다.');
    } else {
      await createFactoryApiMasterFactoryPost({
        body: form as any
      });
      alert('등록되었습니다.');
    }
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error('저장 중 오류:', e);
  }
}

async function handleDelete() {
  if (!confirm(`'${form.FACTORYNM}' 삭제하시겠습니까?`)) return;
  try {
    await deleteFactoryApiMasterFactoryFactoryCdDelete({
      path: { factory_cd: form.FACTORYCD }
    });
    alert('삭제되었습니다.');
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error('삭제 중 오류:', e);
  }
}

onMounted(() => {
  fetchPlants().then(() => fetchData());
});
</script>
<style scoped>
.page-view { display: flex; flex-direction: column; gap: 16px; height: 100%; }
.search-section { background: #fff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 1px 6px rgba(0,0,0,.04); }
.section-title { font-size: 0.82rem; font-weight: 700; color: #667eea; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #f0f4ff; }
.search-row { display: flex; align-items: center; gap: 10px; }
.search-row label { font-size: 0.88rem; font-weight: 600; color: #636e72; }
.search-row select, .search-row input { flex: 0 1 auto; min-width: 150px; padding: 8px 12px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: 0.9rem; }
.search-row select:focus, .search-row input:focus { border-color: #667eea; outline: none; }
.btn-search { background: #667eea; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.88rem; }
.btn-add { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.88rem; margin-left: auto; }

.fg { display: grid; grid-template-columns: repeat(1, 1fr); gap: 14px; }
.ff { display: flex; flex-direction: column; gap: 5px; }
.ff label { font-size: 0.82rem; font-weight: 600; color: #64748b; }
.ff input, .ff select { padding: 9px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.88rem; transition: border-color .15s; }
.ff input:focus, .ff select:focus { border-color: #667eea; outline: none; box-shadow: 0 0 0 3px rgba(102,126,234,.1); }
.ff input:disabled, .ff select:disabled { background: #f8fafc; color: #94a3b8; }
</style>
