<template>
  <li class="tree-item">
    <div class="tree-node" :class="{ 'selected': selectedPartNo === node.partNo }" @click.stop="selectNode">
      <span 
        class="toggle-icon" 
        :class="{ 'has-children': node.children && node.children.length > 0, 'expanded': node.expanded }"
        @click.stop="toggleExpand"
      >
        <span v-if="node.children && node.children.length > 0">▶</span>
        <span v-else class="bullet">•</span>
      </span>
      <span class="node-label">{{ node.partNo }}</span>
      <span v-if="node.data" class="node-qty">
        (소요량: {{ node.data.REQQTY }} | 순서: {{ node.data.ORD }} | {{ node.data.USEYN ? '사용' : '미사용' }})
      </span>
      <div class="node-actions" v-if="selectedPartNo === node.partNo">
        <button class="action-btn add" title="자식 추가" @click.stop="$emit('add', node)">＋</button>
        <button v-if="node.data" class="action-btn edit" title="수정" @click.stop="$emit('edit', node)">✎</button>
        <button v-if="node.data" class="action-btn delete" title="삭제" @click.stop="$emit('delete', node)">✕</button>
      </div>
    </div>
    
    <ul v-if="node.children && node.children.length > 0 && node.expanded" class="tree-children">
      <BomTreeItem 
        v-for="child in node.children" 
        :key="child.partNo" 
        :node="child" 
        :selectedPartNo="selectedPartNo"
        @select="$emit('select', $event)"
        @add="$emit('add', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
const props = defineProps<{
  node: any;
  selectedPartNo: string;
}>();

const emit = defineEmits(['select', 'add', 'edit', 'delete']);

function toggleExpand() {
  if (props.node.children && props.node.children.length > 0) {
    props.node.expanded = !props.node.expanded;
  }
}

function selectNode() {
  emit('select', props.node.partNo);
}
</script>

<style scoped>
.tree-item { list-style: none; margin: 0; padding: 0; }
.tree-node {
  display: flex; align-items: center; padding: 6px 8px; cursor: pointer; border-radius: 4px; transition: background-color 0.2s; position: relative;
}
.tree-node:hover { background-color: #f1f5f9; }
.tree-node.selected { background-color: #e0e7ff; color: #4f46e5; font-weight: 600; }
.toggle-icon {
  display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; margin-right: 6px; font-size: 0.75rem; color: #94a3b8; transition: transform 0.2s;
}
.toggle-icon.has-children { cursor: pointer; }
.toggle-icon.has-children:hover { color: #4f46e5; }
.toggle-icon.expanded { transform: rotate(90deg); }
.bullet { font-size: 1.2rem; line-height: 1; }
.node-label { font-size: 0.95rem; }
.node-qty { font-size: 0.8rem; color: #64748b; margin-left: 8px; font-weight: normal; }
.tree-children { padding-left: 20px; margin: 0; border-left: 1px dashed #cbd5e1; margin-left: 10px; }

.node-actions {
  display: flex; gap: 4px; margin-left: auto;
}
.action-btn {
  background: #fff; border: 1px solid #cbd5e1; border-radius: 4px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.8rem; color: #475569;
}
.action-btn:hover { background: #f8fafc; }
.action-btn.add { color: #059669; border-color: #86efac; }
.action-btn.add:hover { background: #dcfce7; }
.action-btn.edit { color: #2563eb; border-color: #93c5fd; }
.action-btn.edit:hover { background: #dbeafe; }
.action-btn.delete { color: #dc2626; border-color: #fca5a5; }
.action-btn.delete:hover { background: #fee2e2; }
</style>