<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">메뉴관리</div>
      <div class="search-row">
        <button class="btn-add" @click="openAdd">＋ 신규등록</button>
      </div>
    </section>

    <DataGrid
      :columns="columns"
      :rows="items"
      :loading="loading"
      :selectedIndex="selectedIdx"
      @row-click="onRowClick"
    >
      <!-- Custom rendering for 'Category' -->
      <template #cell-CATEGORY="{ }">
        <span class="category-label">관리용</span>
      </template>

      <!-- Custom rendering for 'Menu Name' to support indentation -->
      <template #cell-MENUNM="{ row }">
        <div :style="{ paddingLeft: row.PAR_MENUCD ? '20px' : '0px', fontWeight: row.PAR_MENUCD ? 'normal' : 'bold' }">
          <span v-if="row.PAR_MENUCD">↳ </span>
          {{ row.MENUNM }}
        </div>
      </template>

      <!-- Custom rendering for 'Use Y/N' to show a checkbox -->
      <template #cell-USE_YN="{ row }">
        <input type="checkbox" :checked="row.USE_YN" disabled />
      </template>
    </DataGrid>

    <FormModal
      :visible="showModal"
      :title="editMode ? '메뉴 수정' : '메뉴 등록'"
      width="500px"
      :showDelete="editMode"
      @close="showModal = false"
      @save="handleSave"
      @delete="handleDelete"
    >
      <div class="fg">
        <div class="ff">
          <label>상위메뉴</label>
          <select v-model="form.PAR_MENUCD">
            <option value="">(최상위 메뉴)</option>
            <option v-for="pm in parentMenus" :key="pm.MENUCD" :value="pm.MENUCD">
              {{ pm.MENUNM }}
            </option>
          </select>
        </div>

        <div class="ff">
          <label>메뉴코드</label>
          <input type="text" v-model="form.MENUCD" :disabled="editMode" placeholder="영문/숫자 코드" />
        </div>

        <div class="ff">
          <label>메뉴명</label>
          <input type="text" v-model="form.MENUNM" />
        </div>

        <div class="ff">
          <label>경로 (URL)</label>
          <input type="text" v-model="form.CLASS_PATH" placeholder="/system/menu" />
        </div>

        <div class="ff">
          <label>정렬 순서</label>
          <input type="number" v-model="form.ORD" min="0" />
        </div>

        <div class="ff" style="flex-direction: row; gap: 20px;">
          <label style="width: auto;">조회 권한</label>
          <input type="checkbox" v-model="form.SEARCH" style="width: auto; margin-right: 20px;" />
          
          <label style="width: auto;">등록/수정 권한</label>
          <input type="checkbox" v-model="form.REGEDIT" style="width: auto;" />
        </div>

        <div class="ff" style="flex-direction: row; gap: 20px;">
          <label style="width: auto;">사용여부</label>
          <input type="checkbox" v-model="form.USE_YN" style="width: auto;" />
        </div>
      </div>
    </FormModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../../api';
import DataGrid from '../../../components/common/DataGrid.vue';
import FormModal from '../../../components/common/FormModal.vue';

const columns = [
  { key: 'CATEGORY', label: '구분', width: '150px' },
  { key: 'ORD', label: '순번', width: '80px' },
  { key: 'MENUNM', label: '메뉴', minWidth: '250px' },
  { key: 'USE_YN', label: '사용여부', width: '100px' }
];

const items = ref<any[]>([]);
const loading = ref(false);
const selectedIdx = ref(-1);

const editMode = ref(false);
const showModal = ref(false);

const emptyForm = {
  MENUCD: '',
  PAR_MENUCD: '',
  MENUNM: '',
  CLASS_PATH: '',
  ORD: 0,
  SEARCH: false,
  REGEDIT: false,
  USE_YN: true
};

const form = reactive({ ...emptyForm });

const parentMenus = computed(() => {
  // Return only top-level menus for the parent dropdown
  return items.value.filter(item => !item.PAR_MENUCD);
});

async function fetchData() {
  loading.value = true;
  try {
    const r = await api.get('/api/system/menus');
    // API 응답 구조에 맞게 데이터 추출 (data.data 또는 data)
    items.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data) ? r.data : (r.data?.data?.data || []));
    selectedIdx.value = -1;
  } catch (e) {
    console.error('메뉴 조회 중 오류:', e);
  } finally {
    loading.value = false;
  }
}

function onRowClick(row: any, idx: number) {
  selectedIdx.value = idx;
  editMode.value = true;
  Object.assign(form, row);
  if (form.PAR_MENUCD === null) {
    form.PAR_MENUCD = '';
  }
  showModal.value = true;
}

function openAdd() {
  editMode.value = false;
  Object.assign(form, { ...emptyForm });
  showModal.value = true;
}

async function handleSave() {
  if (!form.MENUCD) { alert('메뉴코드를 입력하세요.'); return; }
  if (!form.MENUNM) { alert('메뉴명을 입력하세요.'); return; }

  try {
    if (editMode.value) {
      await api.put(`/api/system/menus/${form.MENUCD}`, form);
      alert('수정되었습니다.');
    } else {
      await api.post('/api/system/menus', form);
      alert('등록되었습니다.');
    }
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error('저장 중 오류:', e);
  }
}

async function handleDelete() {
  if (!confirm(`'${form.MENUNM}' 메뉴를 삭제하시겠습니까?`)) return;
  try {
    await api.delete(`/api/system/menus/${form.MENUCD}`);
    alert('삭제되었습니다.');
    showModal.value = false;
    fetchData();
  } catch (e: any) {
    console.error('삭제 중 오류:', e);
  }
}

onMounted(() => {
  fetchData();
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
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
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
}
.category-label {
  font-size: 0.85rem;
  color: #636e72;
}

.fg {
  display: flex;
  flex-direction: column;
  gap: 14px;
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
.ff input[type="text"],
.ff input[type="number"],
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
