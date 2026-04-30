<template>
  <div class="popup-picker-trigger" @click="showModal = true">
    <div class="input-wrap">
      <input type="text" :value="modelValue" readonly :placeholder="placeholder" />
      <button type="button" class="btn-open"><i class="fas fa-search"></i></button>
    </div>
    <span v-if="displayValue" class="display-text">{{ displayValue }}</span>
  </div>

  <FormModal :visible="showModal" :title="title" width="600px" @close="showModal = false" :showSave="false">
    <div class="picker-content">
      <div class="picker-search">
        <input type="text" v-model="searchText" :placeholder="searchPlaceholder" @keyup.enter="fetchData" />
        <button class="btn-search" @click="fetchData">검색</button>
      </div>
      <div class="picker-grid">
        <DataGrid 
          :columns="columns" 
          :rows="items" 
          :loading="loading" 
          :page="page"
          :totalPages="totalPages"
          :total="total"
          @row-click="selectItem"
          @page-change="onPageChange"
        />
      </div>
    </div>
  </FormModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../../api';
import FormModal from './FormModal.vue';
import DataGrid from './DataGrid.vue';

const props = defineProps<{
  modelValue?: string | number | null;
  displayValue?: string;
  title: string;
  placeholder?: string;
  apiPath: string;
  columns: any[];
  valueField: string;
  searchPlaceholder?: string;
}>();

const emit = defineEmits(['update:modelValue', 'select']);

const showModal = ref(false);
const items = ref<any[]>([]);
const loading = ref(false);
const searchText = ref('');
const page = ref(1);
const totalPages = ref(0);
const total = ref(0);

async function fetchData() {
  loading.value = true;
  try {
    const p: any = { page: page.value, size: 10 };
    if (searchText.value) p.search = searchText.value;
    const r = await api.get(props.apiPath, { params: p });
    
    // API response formats vary in this project, handling them:
    const raw = r.data;
    if (Array.isArray(raw)) {
      items.value = raw;
      total.value = raw.length;
      totalPages.value = 1;
    } else if (raw?.data) {
      if (Array.isArray(raw.data)) {
        items.value = raw.data;
        total.value = raw.total || raw.data.length;
        totalPages.value = raw.totalPages || 1;
      } else if (Array.isArray(raw.data.data)) {
        items.value = raw.data.data;
        total.value = raw.data.total || 0;
        totalPages.value = raw.data.totalPages || 1;
      }
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function selectItem(row: any) {
  emit('update:modelValue', row[props.valueField]);
  emit('select', row);
  showModal.value = false;
}

function onPageChange(p: number) {
  page.value = p;
  fetchData();
}

watch(showModal, (val) => {
  if (val && items.value.length === 0) {
    fetchData();
  }
});
</script>

<style scoped>
.popup-picker-trigger {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.input-wrap {
  display: flex;
  position: relative;
}
.input-wrap input {
  flex: 1;
  padding-right: 36px !important;
  cursor: pointer;
  background: #fff !important;
}
.btn-open {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 36px;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.display-text {
  font-size: 0.75rem;
  color: #3b82f6;
  font-weight: 600;
  margin-left: 2px;
}
.picker-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 450px;
}
.picker-search {
  display: flex;
  gap: 8px;
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
  padding: 0 16px;
  border-radius: 6px;
  cursor: pointer;
}
.picker-grid {
  flex: 1;
  overflow: hidden;
}
</style>