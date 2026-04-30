<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">사용자 관리 [frmUserList]</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="searchPlant" @change="fetchData">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
        </select>
        
        <label>부서</label>
        <select v-model="searchDeptcd" @change="fetchData">
          <option value="">전체</option>
          <option v-for="d in depts" :key="d.DEPT_CD" :value="d.DEPT_CD">{{ d.NAME }}</option>
        </select>

        <label>이름</label>
        <input type="text" v-model="searchName" placeholder="사용자 명 검색" @keyup.enter="fetchData" />

        <label>사용여부</label>
        <select v-model="searchShowYn" @change="fetchData">
          <option value="">(선택하세요)</option>
          <option :value="true">사용</option>
          <option :value="false">미사용</option>
        </select>

        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-add" @click="openAdd">사용자 메뉴</button>
        <button class="btn-add" style="margin-left: 5px;" @click="openAdd">신규 등록</button>
      </div>
    </section>

    <DataGrid
      :columns="columns"
      :rows="items"
      :loading="loading"
      :selectedIndex="selectedIdx"
      :page="page"
      :totalPages="totalPages"
      :total="total"
      @row-click="onRowClick"
      @page-change="onPageChange"
    />

    <FormModal
      :visible="showModal"
      :title="editMode ? '사용자 수정[frmUserRegPopUp]' : '사용자 등록[frmUserRegPopUp]'"
      width="700px"
      :showDelete="editMode"
      @close="showModal = false"
      @save="handleSave"
      @delete="handleDelete"
    >
      <div class="fg">
        <div class="ff">
          <label>사업장</label>
          <select v-model="form.PLANT" :disabled="editMode">
            <option value="">(선택하세요)</option>
            <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{ p.PLANTNM }}</option>
          </select>
        </div>
        <div class="ff">
          <label>사용자 구분</label>
          <select v-model="form.GUBUN">
            <option value="">(선택하세요)</option>
            <option value="1">내부직원</option>
            <option value="2">외부직원</option>
          </select>
        </div>

        <div class="ff">
          <label>사용자 명</label>
          <input type="text" v-model="form.NAME" />
        </div>
        <div class="ff">
          <label>사번</label>
          <input type="text" v-model="form.EMPID" :disabled="editMode" />
        </div>

        <div class="ff">
          <label>비밀번호</label>
          <input type="password" v-model="form.PASS" />
        </div>
        <div class="ff">
          <label>비밀번호 확인</label>
          <input type="password" v-model="form.PASS_CONFIRM" />
        </div>

        <div class="ff">
          <label>부서</label>
          <select v-model="form.DEPTCD">
            <option value="">(선택하세요)</option>
            <option v-for="d in depts" :key="d.DEPT_CD" :value="d.DEPT_CD">{{ d.NAME }}</option>
          </select>
        </div>
        <div class="ff">
          <label>직급</label>
          <input type="text" v-model="form.JIKGUB" />
        </div>

        <div class="ff">
          <label>전화</label>
          <input type="text" v-model="form.TEL" />
        </div>
        <div class="ff">
          <label>휴대폰</label>
          <input type="text" v-model="form.MOBILE" />
        </div>

        <div class="ff">
          <label>E-Mail</label>
          <input type="text" v-model="form.EMAIL" />
        </div>
        <div class="ff">
          <label>사용여부</label>
          <select v-model="form.SHOWYN">
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
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';
import FormModal from '../../../components/common/FormModal.vue';

const plants = ref<any[]>([]);
const depts = ref<any[]>([]);

const columns = [
  { key: 'PLANT', label: '사업장', width: '120px' },
  { key: 'EMPID', label: '사번', width: '100px' },
  { key: 'NAME', label: '이름', width: '100px' },
  { key: 'DEPT_NAME', label: '부서', minWidth: '150px' },
  { key: 'JIKGUB', label: '직급', width: '100px' },
  { key: 'TEL', label: '전화', width: '120px' },
  { key: 'EMAIL', label: 'E-Mail', width: '150px' },
  { key: 'GUBUN', label: '권한', width: '80px' },
  { key: 'SHOWYN', label: '사용여부', width: '80px', type: 'boolean' },
];

const searchPlant = ref('');
const searchDeptcd = ref('');
const searchName = ref('');
const searchShowYn = ref<any>('');

const items = ref<any[]>([]);
const loading = ref(false);
const page = ref(1);
const totalPages = ref(1);
const total = ref(0);
const selectedIdx = ref(-1);

const editMode = ref(false);
const showModal = ref(false);

const emptyForm = {
  PLANT: '',
  GUBUN: '1',
  NAME: '',
  EMPID: '',
  PASS: '',
  PASS_CONFIRM: '',
  DEPTCD: '',
  JIKGUB: '',
  TEL: '',
  MOBILE: '',
  EMAIL: '',
  SHOWYN: true
};

const form = reactive({ ...emptyForm });

async function fetchMasterData() {
  try {
    const [pRes, dRes] = await Promise.all([
      api.get('/api/master/plant', { params: { size: 100 } }),
      api.get('/api/master/dept', { params: { size: 100 } })
    ]);
    plants.value = pRes.data.data || [];
    depts.value = dRes.data.data || [];
  } catch (e) {
    console.error('기준 정보 조회 중 오류:', e);
  }
}

async function fetchData() {
  loading.value = true;
  try {
    const p: any = {};
    if (searchPlant.value) p.plant = searchPlant.value;
    if (searchName.value) p.name = searchName.value;
    if (searchDeptcd.value) p.deptcd = searchDeptcd.value;
    if (searchShowYn.value !== '') p.showyn = searchShowYn.value;

    const r = await api.get('/api/system/users', { params: p });
    items.value = Array.isArray(r.data) ? r.data : (r.data?.data || []);
    total.value = items.value.length;
    totalPages.value = 1;
    selectedIdx.value = -1;
  } catch (e) {
    console.error('조회 중 오류:', e);
  } finally {
    loading.value = false;
  }
}

function onRowClick(row: any, idx: number) {
  selectedIdx.value = idx;
  editMode.value = true;
  Object.assign(form, row);
  form.PASS_CONFIRM = form.PASS || '';
  showModal.value = true;
}

function onPageChange(p: number) {
  page.value = p;
}

function openAdd() {
  editMode.value = false;
  Object.assign(form, { ...emptyForm });
  showModal.value = true;
}

async function handleSave() {
  if (!form.PLANT) { alert('사업장을 선택하세요.'); return; }
  if (!form.EMPID) { alert('사번을 입력하세요.'); return; }
  if (!form.NAME) { alert('사용자 명을 입력하세요.'); return; }
  if (form.PASS !== form.PASS_CONFIRM) { alert('비밀번호가 일치하지 않습니다.'); return; }

  try {
    if (editMode.value) {
      await api.put(`/api/system/users/${form.EMPID}`, form);
      alert('수정되었습니다.');
    } else {
      await api.post('/api/system/users', form);
      alert('등록되었습니다.');
    }
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error('저장 중 오류:', e);
  }
}

async function handleDelete() {
  if (!confirm(`'${form.NAME}' 사용자를 삭제하시겠습니까?`)) return;
  try {
    await api.delete(`/api/system/users/${form.EMPID}`);
    alert('삭제되었습니다.');
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error('삭제 중 오류:', e);
  }
}

onMounted(() => {
  fetchMasterData().then(() => fetchData());
});
</script>

<style scoped>
.page-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}
.search-section {
  background: #fff;
  border-radius: 10px;
  padding: 16px 20px;
  box-shadow: 0 1px 6px rgba(0,0,0,.04);
}
.section-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #667eea;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid #f0f4ff;
}
.search-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.search-row label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #636e72;
}
.search-row select,
.search-row input {
  flex: 0 1 auto;
  min-width: 150px;
  padding: 8px 12px;
  border: 1px solid #dfe6e9;
  border-radius: 6px;
  font-size: 0.9rem;
}
.search-row select:focus,
.search-row input:focus {
  border-color: #667eea;
  outline: none;
}
.btn-search {
  background: #667eea;
  color: #fff;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.88rem;
}
.btn-add {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.88rem;
  margin-left: auto;
}

.fg {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 24px;
}
.ff {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ff label {
  width: 100px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #64748b;
  text-align: right;
  flex-shrink: 0;
}
.ff input,
.ff select {
  flex: 1;
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.88rem;
  transition: border-color .15s;
}
.ff input:focus,
.ff select:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102,126,234,.1);
}
.ff input:disabled,
.ff select:disabled {
  background: #f8fafc;
  color: #94a3b8;
}
</style>
