<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">공통코드 (Tree Grid)</div>
      <div class="search-row">
        <button class="btn-search" @click="expandAll">전체 펼침</button>
        <button class="btn-search" @click="collapseAll">전체 닫기</button>
        <button class="btn-add" @click="openAddRoot">＋ 최상위 그룹 추가</button>
      </div>
    </section>

    <div class="grid-container">
      <div v-if="loading" class="loading-msg">데이터를 불러오는 중...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="min-width: 200px">코드</th>
            <th style="min-width: 150px">코드명</th>
            <th style="width: 100px">상위코드</th>
            <th style="width: 60px; text-align: center;">순서</th>
            <th style="width: 120px">텍스트값</th>
            <th style="width: 80px; text-align: right;">숫자값</th>
            <th style="width: 90px; text-align: center;">시스템상수</th>
            <th style="width: 80px; text-align: center;">사용여부</th>
            <th style="width: 160px; text-align: center;">작업</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="flatRows.length === 0">
            <td colspan="9" class="empty-td">등록된 공통코드가 없습니다.</td>
          </tr>
          <tr v-for="node in flatRows" :key="node.data.CODECD" class="data-row">
            <!-- 트리 컬럼 -->
            <td class="tree-cell" :style="{ paddingLeft: `${node.level * 20 + 12}px` }">
              <span 
                class="toggle-icon" 
                :class="{ 'has-children': node.children.length > 0, 'expanded': node.expanded }"
                @click.stop="toggleExpand(node)"
              >
                <span v-if="node.children.length > 0">▶</span>
                <span v-else class="bullet">•</span>
              </span>
              <span class="code-text">{{ node.data.CODECD }}</span>
            </td>
            
            <!-- 나머지 컬럼 -->
            <td>{{ node.data.CODENM }}</td>
            <td>{{ node.data.PAR_CODECD || '' }}</td>
            <td style="text-align: center;">{{ node.data.ORD }}</td>
            <td>{{ node.data.TEXTVAL }}</td>
            <td style="text-align: right;">{{ node.data.NUMVAL }}</td>
            <td style="text-align: center;">
              <span :class="['status-badge', node.data.SYS_CONST ? 'active' : 'inactive']">
                {{ node.data.SYS_CONST ? 'YES' : 'NO' }}
              </span>
            </td>
            <td style="text-align: center;">
              <span :class="['status-badge', node.data.USEYN ? 'active' : 'inactive']">
                {{ node.data.USEYN ? '사용' : '미사용' }}
              </span>
            </td>
            
            <!-- 작업 -->
            <td style="text-align: center;">
              <button class="btn-action add" title="하위 추가" @click.stop="openAddChild(node)">＋</button>
              <button class="btn-action edit" title="수정" @click.stop="openEditNode(node)">✎</button>
              <button class="btn-action delete" title="삭제" @click.stop="deleteNode(node)">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal for Code Add/Edit -->
    <FormModal :visible="showModal" :title="editMode ? '공통코드 수정' : '공통코드 등록'" width="580px" :showDelete="false" @close="showModal = false" @save="handleSave">
      <div class="fg">
        <div class="ff">
          <label>상위코드</label>
          <select v-model="form.PAR_CODECD" :disabled="editMode">
            <option value="">(없음 - 최상위 그룹)</option>
            <option v-for="code in allCodes" :key="code.CODECD" :value="code.CODECD">
              {{ code.CODENM }} ({{ code.CODECD }})
            </option>
          </select>
        </div>
        <div class="ff">
          <label>코드</label>
          <input v-model="form.CODECD" :disabled="editMode" placeholder="코드 입력"/>
        </div>
        <div class="ff">
          <label>코드명</label>
          <input v-model="form.CODENM"/>
        </div>
        <div class="ff">
          <label>순서</label>
          <input type="number" v-model.number="form.ORD"/>
        </div>
        <div class="ff">
          <label>텍스트값</label>
          <input v-model="form.TEXTVAL"/>
        </div>
        <div class="ff">
          <label>숫자값</label>
          <input type="number" step="0.001" v-model.number="form.NUMVAL"/>
        </div>
        <div class="ff">
          <label>시스템상수</label>
          <select v-model="form.SYS_CONST">
            <option :value="false">NO</option>
            <option :value="true">YES</option>
          </select>
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
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../../api'; 
import FormModal from '../../../components/common/FormModal.vue';

interface TreeNode {
  data: any; // The original code record
  children: TreeNode[];
  expanded: boolean;
  level: number;
}

// ─────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────
const loading = ref(false);
const allCodes = ref<any[]>([]);
const treeData = ref<TreeNode[]>([]);

// Modal Form State
const emptyForm = { 
  CODECD: '', PAR_CODECD: '', CODENM: '', ORD: 0, 
  TEXTVAL: '', NUMVAL: null as number | null, 
  USEYN: true as boolean, SYS_CONST: false as boolean 
};
const form = reactive({ ...emptyForm });
const editMode = ref(false);
const showModal = ref(false);

// ─────────────────────────────────────────────────────────
// Computed Flat Rows for Grid
// ─────────────────────────────────────────────────────────
const flatRows = computed(() => {
  const rows: TreeNode[] = [];
  function traverse(nodes: TreeNode[]) {
    for (const node of nodes) {
      rows.push(node);
      if (node.expanded && node.children.length > 0) {
        traverse(node.children);
      }
    }
  }
  traverse(treeData.value);
  return rows;
});

// ─────────────────────────────────────────────────────────
// API Calls & Tree Logic
// ─────────────────────────────────────────────────────────
async function fetchAllCodes() {
  loading.value = true;
  try {
    const r = await api.get('/api/master/code', { params: { size: 9999 } });
    allCodes.value = r.data.data || [];
    buildTree();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function buildTree() {
  const adjList: Record<string, any[]> = {};
  const roots: any[] = [];

  // Group by Parent Code
  allCodes.value.forEach(code => {
    const par = code.PAR_CODECD ? code.PAR_CODECD.trim() : null;
    if (!par) {
      roots.push(code);
    } else {
      if (!adjList[par]) adjList[par] = [];
      adjList[par].push(code);
    }
  });

  // Sort
  roots.sort((a, b) => a.ORD - b.ORD);
  Object.keys(adjList).forEach(key => {
    adjList[key].sort((a, b) => a.ORD - b.ORD);
  });

  // Recursive Build
  // We keep track of existing expanded states if re-building
  function createNode(codeRecord: any, level: number): TreeNode {
    const childrenRecords = adjList[codeRecord.CODECD] || [];
    const children = childrenRecords.map(childRec => createNode(childRec, level + 1));
    
    // Preserve existing expanded state if possible
    const existingNode = findNodeByCodeCd(treeData.value, codeRecord.CODECD);
    const expanded = existingNode ? existingNode.expanded : true;

    return {
      data: codeRecord,
      children,
      expanded,
      level
    };
  }

  treeData.value = roots.map(rootRec => createNode(rootRec, 0));
}

function findNodeByCodeCd(nodes: TreeNode[], codeCd: string): TreeNode | null {
  for (const node of nodes) {
    if (node.data.CODECD === codeCd) return node;
    if (node.children.length > 0) {
      const found = findNodeByCodeCd(node.children, codeCd);
      if (found) return found;
    }
  }
  return null;
}

// ─────────────────────────────────────────────────────────
// Tree Interaction
// ─────────────────────────────────────────────────────────
function toggleExpand(node: TreeNode) {
  if (node.children.length > 0) {
    node.expanded = !node.expanded;
  }
}

function traverseTree(nodes: TreeNode[], action: (node: TreeNode) => void) {
  for (const node of nodes) {
    action(node);
    if (node.children) traverseTree(node.children, action);
  }
}

function expandAll() { traverseTree(treeData.value, node => node.expanded = true); }
function collapseAll() { traverseTree(treeData.value, node => node.expanded = false); }

// ─────────────────────────────────────────────────────────
// CRUD Actions (Modal)
// ─────────────────────────────────────────────────────────
function openAddRoot() {
  editMode.value = false;
  Object.assign(form, { ...emptyForm });
  form.PAR_CODECD = '';
  showModal.value = true;
}

function openAddChild(node: TreeNode) {
  editMode.value = false;
  Object.assign(form, { ...emptyForm });
  form.PAR_CODECD = node.data.CODECD;
  showModal.value = true;
}

function openEditNode(node: TreeNode) {
  editMode.value = true;
  Object.assign(form, node.data);
  // ensure null text displays as empty string
  if (form.PAR_CODECD === null) form.PAR_CODECD = '';
  showModal.value = true;
}

async function deleteNode(node: TreeNode) {
  if (!confirm(`'${node.data.CODENM}' 공통코드를 삭제하시겠습니까?\n하위 코드가 있다면 먼저 삭제해야 합니다.`)) return;
  try {
    await api.delete(`/api/master/code/${node.data.CODECD}`);
    alert('삭제되었습니다.');
    fetchAllCodes();
  } catch (e) {
    console.error(e);
  }
}

async function handleSave() {
  if (!form.CODECD || !form.CODENM) {
    alert('코드와 코드명을 입력하세요.');
    return;
  }
  
  const payload = { ...form };
  if (!payload.PAR_CODECD) payload.PAR_CODECD = null as any;

  try {
    if (editMode.value) {
      await api.put(`/api/master/code/${form.CODECD}`, payload);
      alert('수정되었습니다.');
    } else {
      await api.post('/api/master/code', payload);
      alert('등록되었습니다.');
      // Expand the parent if a child was added
      if (payload.PAR_CODECD) {
        const parentNode = findNodeByCodeCd(treeData.value, payload.PAR_CODECD);
        if (parentNode) parentNode.expanded = true;
      }
    }
    showModal.value = false;
    fetchAllCodes();
  } catch (e) {
    console.error(e);
  }
}

onMounted(() => {
  fetchAllCodes();
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 16px; height: 100%; }

.search-section { background: #fff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 1px 6px rgba(0,0,0,.04); }
.section-title { font-size: .82rem; font-weight: 700; color: #667eea; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #f0f4ff; }

.search-row { display: flex; align-items: center; gap: 10px; }
.btn-search { background: #fff; color: #64748b; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: .8rem; transition: all 0.2s; white-space: nowrap; }
.btn-search:hover { background: #f1f5f9; border-color: #94a3b8; }

.btn-add { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: .85rem; margin-left: auto; }

.grid-container {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,.04);
}

.loading-msg { padding: 40px; text-align: center; color: #64748b; font-size: 0.95rem; }

.data-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.data-table thead { position: sticky; top: 0; z-index: 2; }
.data-table th { background: #f8fafc; color: #3a4a6b; font-weight: 600; padding: 10px 12px; text-align: left; border-bottom: 2px solid #d0d7e8; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #f1f5f9; color: #2d3436; vertical-align: middle; }
.data-table tbody tr:hover { background: #f4f6ff; }
.empty-td { text-align: center !important; padding: 40px !important; color: #94a3b8; }

/* Tree Cell Styles */
.tree-cell { display: flex; align-items: center; gap: 6px; }
.toggle-icon {
  display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; font-size: 0.75rem; color: #94a3b8; transition: transform 0.2s; flex-shrink: 0;
}
.toggle-icon.has-children { cursor: pointer; }
.toggle-icon.has-children:hover { color: #4f46e5; }
.toggle-icon.expanded { transform: rotate(90deg); }
.bullet { font-size: 1.2rem; line-height: 1; }
.code-text { font-weight: 500; color: #1e293b; }

.status-badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.status-badge.active { background: #dcfce7; color: #0f172a; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }

/* Action Buttons */
.btn-action { background: #fff; border: 1px solid #cbd5e1; border-radius: 4px; width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.85rem; margin: 0 3px; transition: all 0.2s; }
.btn-action.add { color: #059669; border-color: #86efac; }
.btn-action.add:hover { background: #dcfce7; }
.btn-action.edit { color: #2563eb; border-color: #93c5fd; }
.btn-action.edit:hover { background: #dbeafe; }
.btn-action.delete { color: #dc2626; border-color: #fca5a5; }
.btn-action.delete:hover { background: #fee2e2; }

/* Form Styles */
.fg { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px 18px; }
.ff { display: flex; flex-direction: column; gap: 5px; }
.ff label { font-size: .82rem; font-weight: 600; color: #64748b; }
.ff input, .ff select { padding: 9px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: .88rem; transition: border-color .15s; }
.ff input:focus, .ff select:focus { border-color: #667eea; outline: none; box-shadow: 0 0 0 3px rgba(102,126,234,.1); }
.ff input:disabled { background: #f8fafc; color: #94a3b8; }
</style>