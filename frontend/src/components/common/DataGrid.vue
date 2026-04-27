<template>
  <div class="data-grid-wrapper">
    <div class="grid-header" v-if="$slots.header">
      <slot name="header" />
    </div>
    <div class="grid-table-wrap">
      <table class="grid-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width || 'auto', minWidth: col.minWidth || '80px' }">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns.length" class="grid-empty">데이터 로딩 중...</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td :colspan="columns.length" class="grid-empty">데이터가 없습니다.</td>
          </tr>
          <tr
            v-else
            v-for="(row, idx) in rows"
            :key="idx"
            :class="{ selected: selectedIndex === idx }"
            @click="$emit('row-click', row, idx)"
          >
            <td v-for="col in columns" :key="col.key">
              <slot :name="'cell-' + col.key" :row="row" :index="idx">
                <template v-if="col.type === 'boolean'">
                  <span class="badge" :class="row[col.key] ? 'active' : 'inactive'">
                    {{ row[col.key] ? '사용' : '미사용' }}
                  </span>
                </template>
                <template v-else-if="col.type === 'date'">
                  {{ formatDate(row[col.key]) }}
                </template>
                <template v-else>
                  {{ row[col.key] ?? '' }}
                </template>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="grid-footer" v-if="totalPages > 1">
      <button class="page-btn" :disabled="page <= 1" @click="$emit('page-change', page - 1)">◀</button>
      <span class="page-info">{{ page }} / {{ totalPages }} (총 {{ total }}건)</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="$emit('page-change', page + 1)">▶</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  columns: Array<{ key: string; label: string; width?: string; minWidth?: string; type?: string }>;
  rows: Array<any>;
  loading?: boolean;
  selectedIndex?: number;
  page?: number;
  totalPages?: number;
  total?: number;
}>(), {
  loading: false,
  selectedIndex: -1,
  page: 1,
  totalPages: 1,
  total: 0
});

defineEmits(['row-click', 'page-change']);

function formatDate(val: any) {
  if (!val) return '';
  const d = new Date(val);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}
</script>

<style scoped>
.data-grid-wrapper { background: #fff; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; }
.grid-header { padding: 14px 18px; border-bottom: 1px solid #eee; }
.grid-table-wrap { flex: 1; overflow: auto; }
.grid-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.grid-table thead { position: sticky; top: 0; z-index: 2; }
.grid-table th { background: linear-gradient(180deg, #f0f4ff 0%, #e8ecf5 100%); color: #3a4a6b; font-weight: 600; padding: 10px 12px; text-align: left; border-bottom: 2px solid #d0d7e8; white-space: nowrap; font-size: 0.83rem; }
.grid-table td { padding: 9px 12px; border-bottom: 1px solid #f0f2f5; color: #2d3436; }
.grid-table tbody tr { cursor: pointer; transition: background 0.12s; }
.grid-table tbody tr:hover { background: #f4f6ff; }
.grid-table tbody tr.selected { background: #e8edff; }
.grid-empty { text-align: center; color: #b2bec3; padding: 60px 16px !important; font-size: 0.92rem; }
.badge { padding: 3px 10px; border-radius: 10px; font-size: 0.78rem; font-weight: 600; }
.badge.active { background: #dff9e8; color: #27ae60; }
.badge.inactive { background: #fde8e8; color: #e74c3c; }
.grid-footer { display: flex; justify-content: center; align-items: center; gap: 12px; padding: 12px; border-top: 1px solid #f0f2f5; }
.page-btn { background: #f0f4ff; border: 1px solid #d0d7e8; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; color: #3a4a6b; }
.page-btn:disabled { opacity: 0.4; cursor: default; }
.page-info { font-size: 0.85rem; color: #636e72; }
</style>
