<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">부서관리 (Tree Grid)</div>
      <div class="search-row">
        <label>사업장</label>
        <select v-model="searchPlantCd" @change="onSearchPlantChange">
          <option value="">전체</option>
          <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{p.PLANTNM}}</option>
        </select>
        <label>공장</label>
        <select v-model="searchFactoryCd" @change="fetchData">
          <option value="">전체</option>
          <option v-for="f in factoriesForSearch" :key="f.FACTORYCD" :value="f.FACTORYCD">{{f.FACTORYNM}}</option>
        </select>
        <label>부서명</label>
        <input type="text" v-model="searchNm" placeholder="부서명 검색" @keyup.enter="fetchData"/>
        <button class="btn-search" @click="fetchData">조회</button>
        <button class="btn-search" @click="expandAll">전체 펼침</button>
        <button class="btn-search" @click="collapseAll">전체 닫기</button>
        <button class="btn-add" @click="openAddRoot">＋ 신규등록</button>
      </div>
    </section>

    <div class="grid-container">
      <div v-if="loading" class="loading-msg">데이터를 불러오는 중...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="min-width: 200px">부서코드</th>
            <th style="min-width: 150px">부서명</th>
            <th style="width: 120px">사업장</th>
            <th style="width: 140px">공장</th>
            <th style="width: 100px; text-align: center;">사용여부</th>
            <th style="width: 160px; text-align: center;">작업</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="flatRows.length === 0">
            <td colspan="6" class="empty-td">등록된 부서가 없습니다.</td>
          </tr>
          <tr v-for="node in flatRows" :key="node.data.DEPTCD" class="data-row">
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
              <span class="code-text">{{ node.data.DEPTCD }}</span>
            </td>
            
            <!-- 나머지 컬럼 -->
            <td>{{ node.data.DEPTNM }}</td>
            <td>{{ node.data.PLANTNM }}</td>
            <td>{{ node.data.FACTORYNM }}</td>
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

    <!-- Modal for Dept Add/Edit -->
    <FormModal :visible="showModal" :title="editMode ? '부서 수정' : '부서 등록'" width="580px" :showDelete="false" @close="showModal = false" @save="handleSave">
      <div class="fg">
        <div class="ff">
          <label>사업장</label>
          <select v-model="formPlantCd" :disabled="editMode || lockParentFactory" @change="onFormPlantChange">
            <option value="">선택하세요</option>
            <option v-for="p in plants" :key="p.PLANTCD" :value="p.PLANTCD">{{p.PLANTNM}}</option>
          </select>
        </div>
        <div class="ff">
          <label>공장</label>
          <select v-model="form.FACTORYCD" :disabled="editMode || lockParentFactory">
            <option value="">선택하세요</option>
            <option v-for="f in formFactories" :key="f.FACTORYCD" :value="f.FACTORYCD">{{f.FACTORYNM}}</option>
          </select>
        </div>

        <div class="ff">
          <label>부서코드</label>
          <input v-model="form.DEPTCD" :disabled="editMode" placeholder="부서코드 입력"/>
        </div>
        <div class="ff">
          <label>부서명</label>
          <input v-model="form.DEPTNM"/>
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
  data: any; // The original dept record
  children: TreeNode[];
  expanded: boolean;
  level: number;
}

// ─────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────
const loading = ref(false);
const allDepts = ref<any[]>([]);
const treeData = ref<TreeNode[]>([]);

const plants = ref<any[]>([]);
const factoriesForSearch = ref<any[]>([]);

const searchPlantCd = ref('');
const searchFactoryCd = ref('');
const searchNm = ref('');

// Modal Form State
const emptyForm = { DEPTCD: '', FACTORYCD: '', DEPTNM: '', PAR_DEPTCD: '', USEYN: true as boolean };
const form = reactive({ ...emptyForm });
const formPlantCd = ref('');
const formFactories = ref<any[]>([]);
const editMode = ref(false);
const showModal = ref(false);
const lockParentFactory = ref(false);
const lockParentDept = ref(false);

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
async function fetchPlants() {
  try {
    const r = await api.get('/api/master/plant', { params: { size: 100 } });
    plants.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
  } catch (e) {
    console.error(e);
  }
}

async function fetchFactoriesByPlant(plantCd: string) {
  if (!plantCd) return [];
  try {
    const r = await api.get('/api/master/factory', { params: { plant_cd: plantCd, size: 100 } });
    return r.data.data || [];
  } catch (e) {
    console.error(e);
    return [];
  }
}

async function onSearchPlantChange() {
  searchFactoryCd.value = '';
  factoriesForSearch.value = await fetchFactoriesByPlant(searchPlantCd.value);
  fetchData();
}

async function onFormPlantChange() {
  if (formPlantCd.value) {
    formFactories.value = await fetchFactoriesByPlant(formPlantCd.value);
    form.FACTORYCD = ''; 
  } else {
    formFactories.value = [];
    form.FACTORYCD = '';
  }
}

async function fetchData() {
  loading.value = true;
  try {
    const p: any = { size: 9999 };
    if (searchNm.value) p.search = searchNm.value;
    if (searchPlantCd.value) p.plant_cd = searchPlantCd.value;
    if (searchFactoryCd.value) p.factory_cd = searchFactoryCd.value;
    
    const r = await api.get('/api/master/dept', { params: p });
    allDepts.value = Array.isArray(r.data?.data) ? r.data.data : (Array.isArray(r.data?.data?.data) ? r.data.data.data : (r.data?.data || []));
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

  // Group by Parent Dept
  allDepts.value.forEach(dept => {
    const par = dept.PAR_DEPTCD ? dept.PAR_DEPTCD.trim() : null;
    if (!par) {
      roots.push(dept);
    } else {
      if (!adjList[par]) adjList[par] = [];
      adjList[par].push(dept);
    }
  });

  // If a child's parent is not in the fetched list (e.g. due to filtering), make it a root
  allDepts.value.forEach(dept => {
    const par = dept.PAR_DEPTCD ? dept.PAR_DEPTCD.trim() : null;
    if (par) {
      const parentExists = allDepts.value.some(d => d.DEPTCD === par);
      if (!parentExists) {
        roots.push(dept);
        if (adjList[par]) {
          adjList[par] = adjList[par].filter(d => d.DEPTCD !== dept.DEPTCD);
        }
      }
    }
  });

  // Recursive Build
  function createNode(deptRecord: any, level: number): TreeNode {
    const childrenRecords = adjList[deptRecord.DEPTCD] || [];
    const children = childrenRecords.map(childRec => createNode(childRec, level + 1));
    
    // Preserve existing expanded state if possible
    const existingNode = findNodeByDeptCd(treeData.value, deptRecord.DEPTCD);
    const expanded = existingNode ? existingNode.expanded : true;

    return {
      data: deptRecord,
      children,
      expanded,
      level
    };
  }

  const uniqueRoots = Array.from(new Set(roots));
  treeData.value = uniqueRoots.map(rootRec => createNode(rootRec, 0));
}

function findNodeByDeptCd(nodes: TreeNode[], deptCd: string): TreeNode | null {
  for (const node of nodes) {
    if (node.data.DEPTCD === deptCd) return node;
    if (node.children.length > 0) {
      const found = findNodeByDeptCd(node.children, deptCd);
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
async function openAddRoot() {
  editMode.value = false;
  lockParentFactory.value = false;
  lockParentDept.value = false;
  Object.assign(form, { ...emptyForm });
  formPlantCd.value = '';
  formFactories.value = [];
  showModal.value = true;
}

async function openAddChild(node: TreeNode) {
  editMode.value = false;
  lockParentFactory.value = true;
  lockParentDept.value = true;
  Object.assign(form, { ...emptyForm });
  form.PAR_DEPTCD = node.data.DEPTCD;
  form.FACTORYCD = node.data.FACTORYCD;
  
  if (node.data.PLANTCD) {
    formPlantCd.value = node.data.PLANTCD;
    formFactories.value = await fetchFactoriesByPlant(node.data.PLANTCD);
  } else {
    formPlantCd.value = '';
    formFactories.value = [];
  }
  
  showModal.value = true;
}

async function openEditNode(node: TreeNode) {
  editMode.value = true;
  lockParentFactory.value = true;
  lockParentDept.value = false; 
  Object.assign(form, node.data);
  if (!form.PAR_DEPTCD) form.PAR_DEPTCD = '';

  if (node.data.PLANTCD) {
    formPlantCd.value = node.data.PLANTCD;
    formFactories.value = await fetchFactoriesByPlant(node.data.PLANTCD);
  } else {
    formPlantCd.value = '';
    formFactories.value = [];
  }
  showModal.value = true;
}

async function deleteNode(node: TreeNode) {
  if (!confirm(`'${node.data.DEPTNM}' 부서를 삭제하시겠습니까?\n하위 부서가 있다면 먼저 삭제해야 합니다.`)) return;
  try {
    await api.delete(`/api/master/dept/${node.data.DEPTCD}`);
    alert('삭제되었습니다.');
    fetchData();
  } catch (e) {
    console.error(e);
  }
}

async function handleSave() {
  if (!form.DEPTCD) { alert('부서코드를 입력하세요.'); return; }
  
  const payload = { ...form };
  if (!payload.PAR_DEPTCD) payload.PAR_DEPTCD = null as any;

  try {
    if (editMode.value) {
      await api.put(`/api/master/dept/${form.DEPTCD}`, payload);
      alert('수정되었습니다.');
    } else {
      await api.post('/api/master/dept', payload);
      alert('등록되었습니다.');
      // Expand the parent if a child was added
      if (payload.PAR_DEPTCD) {
        const parentNode = findNodeByDeptCd(treeData.value, payload.PAR_DEPTCD);
        if (parentNode) parentNode.expanded = true;
      }
    }
    showModal.value = false;
    fetchData();
  } catch (e) {
    console.error(e);
  }
}

onMounted(() => {
  fetchPlants().then(() => fetchData());
});
</script>

<style scoped>
.page-view { display: flex; flex-direction: column; gap: 16px; height: 100%; }

.search-section { background: #fff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 1px 6px rgba(0,0,0,.04); }
.section-title { font-size: .82rem; font-weight: 700; color: #667eea; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #f0f4ff; }

.search-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.search-row label { font-size: .85rem; font-weight: 600; color: #636e72; }
.search-row select { padding: 7px 10px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: .88rem; min-width: 120px; }
.search-row input { padding: 7px 10px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: .88rem; width: 140px; }
.search-row input:focus, .search-row select:focus { border-color: #667eea; outline: none; }

.btn-search { background: #fff; color: #64748b; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: .8rem; transition: all 0.2s; white-space: nowrap; }
.btn-search:hover { background: #f1f5f9; border-color: #94a3b8; }
/* The primary search button should look different */
.btn-search:first-of-type { background: #667eea; color: #fff; border: none; padding: 8px 18px; font-size: 0.85rem; }
.btn-search:first-of-type:hover { background: #5a67d8; }

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
.ff input:disabled, .ff select:disabled { background: #f8fafc; color: #94a3b8; }
</style>