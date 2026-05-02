<template>
  <FormModal :visible="visible" title="거래처 선택" icon="🏢" width="800px" @close="$emit('close')" :showSave="false">
    <div class="picker-content">
      <div class="picker-search">
        <input type="text" v-model="searchText" placeholder="거래처코드 또는 거래처명 입력" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">🔍 검색</button>
      </div>
      <div class="picker-grid">
        <DataGrid 
          :columns="columns" 
          :rows="items" 
          :loading="loading" 
          @row-click="selectItem"
        />
      </div>
    </div>
  </FormModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../../api';
import FormModal from '../../components/common/FormModal.vue';
import DataGrid from '../../components/common/DataGrid.vue';

const props = defineProps<{
  visible: boolean;
  initialSearch?: string;
  isSupplier?: boolean;
  isCustomer?: boolean;
}>();

const emit = defineEmits(['close', 'select']);

const searchText = ref(props.initialSearch || '');
const items = ref<any[]>([]);
const loading = ref(false);

const columns = [
  { key: 'COMPANYCD', label: '거래처코드', width: '120px' },
  { key: 'COMPANYNM', label: '거래처명', width: '200px' },
  { key: 'BUSINESSNO', label: '사업자번호', width: '150px' },
  { key: 'CEO', label: '대표자', width: '100px' },
  { key: 'ADDR1', label: '주소', width: '250px' },
];

async function fetchData() {
  loading.value = true;
  try {
    const p: any = { size: 100 };
    if (searchText.value) p.search = searchText.value;
    if (props.isSupplier) p.is_supplier = 1;
    if (props.isCustomer) p.is_customer = 1;
    
    const r = await api.get('/api/master/company', { params: p });
    
    const rawData = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
    items.value = rawData;
  } catch (e) {
    console.error('거래처 조회 중 오류:', e);
  } finally {
    loading.value = false;
  }
}

function selectItem(row: any) {
  emit('select', row);
  emit('close');
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (props.initialSearch) searchText.value = props.initialSearch;
    fetchData();
  }
});
</script>

<style scoped>
.picker-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 500px;
}
.picker-search {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
}
.picker-search input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  outline: none;
}
.btn-search {
  background: #64748b;
  color: #fff;
  border: none;
  padding: 0 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.picker-grid {
  flex: 1;
  overflow: auto;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
}
</style>
