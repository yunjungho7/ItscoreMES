<template>
  <div class="page-view">
    <section class="search-section">
      <div class="section-title">BOM (Tree Grid)</div>
      <div class="search-row">
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
            <th style="min-width: 250px">품번</th>
            <th style="min-width: 150px">품명</th>
            <th style="width: 100px; text-align: center;">소요량</th>
            <th style="width: 80px; text-align: center;">순서</th>
            <th style="width: 100px; text-align: center;">사용여부</th>
            <th style="width: 160px; text-align: center;">작업</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="flatRows.length === 0">
            <td colspan="6" class="empty-td">
              등록된 BOM이 없습니다.
              <div v-if="allBoms.length > 0" style="font-size: 0.8rem; color: #e74c3c; margin-top: 8px;">
                (시스템 알림: {{ allBoms.length }}건의 데이터를 불러왔으나 트리 구조를 생성하지 못했습니다. 데이터 순환 참조를 확인하세요.)
              </div>
            </td>
          </tr>
          <tr v-for="node in flatRows" :key="node.id" class="data-row">
            <!-- 트리 컬럼 -->
            <td class="tree-cell" :style="{ paddingLeft: `${node.level * 24 + 12}px` }">
              <span 
                class="toggle-icon" 
                :class="{ 'has-children': node.children.length > 0, 'expanded': node.expanded }"
                @click.stop="toggleExpand(node)"
              >
                <span v-if="node.children.length > 0">▶</span>
                <span v-else class="bullet">•</span>
              </span>
              <span class="code-text">{{ node.partNo }}</span>
            </td>
            
            <!-- 나머지 컬럼 -->
            <td>{{ node.partNm }}</td>
            <td style="text-align: center;">{{ node.data ? node.data.REQQTY : '-' }}</td>
            <td style="text-align: center;">{{ node.data ? node.data.ORD : '-' }}</td>
            <td style="text-align: center;">
              <template v-if="node.data">
                <span :class="['status-badge', node.data.USEYN ? 'active' : 'inactive']">
                  {{ node.data.USEYN ? '사용' : '미사용' }}
                </span>
              </template>
              <template v-else>
                -
              </template>
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

    <!-- Modal for BOM Add/Edit -->
    <FormModal :visible="showModal" :title="editMode ? 'BOM 수정' : 'BOM 등록'" width="800px" :showDelete="false" @close="showModal = false" @save="handleSave">
      <div class="fg">
        <div class="ff" style="margin-bottom: 20px;">
          <label class="required">모품번 (Parent Part)</label>
          <div class="input-with-btn" style="max-width: 400px;">
            <input type="text" :value="form.PAR_PARTNO ? `${goodsMap[form.PAR_PARTNO] || ''} (${form.PAR_PARTNO})` : ''" readonly placeholder="모품번 선택" />
            <button class="btn-search-sm" @click="openParentPicker" :disabled="editMode || lockParent" title="검색">🔍</button>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-header">
            <span class="detail-title">자식 품목 리스트 (Children)</span>
            <button 
              class="btn-row-add" 
              @click="addChildRow" 
              :disabled="!form.PAR_PARTNO"
              :title="!form.PAR_PARTNO ? '모품번을 먼저 선택하세요' : ''"
            >＋ 행추가</button>
          </div>
          <table class="detail-table">
            <thead>
              <tr>
                <th class="req-th">자품번 (Child Part)</th>
                <th style="width: 100px;">소요량</th>
                <th style="width: 80px;">순서</th>
                <th style="width: 60px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="form.details.length === 0">
                <td colspan="4" class="empty-detail">행 추가 버튼을 눌러 자식 품목을 등록하세요.</td>
              </tr>
              <tr v-for="(item, idx) in form.details" :key="idx">
                <td>
                  <div class="input-with-btn">
                    <input type="text" :value="item.CHILD_PARTNO ? `${goodsMap[item.CHILD_PARTNO] || ''} (${item.CHILD_PARTNO})` : ''" readonly placeholder="자품번 선택" />
                    <button class="btn-search-sm" @click="openChildPicker(idx)" title="검색">🔍</button>
                  </div>
                </td>
                <td><input type="number" step="0.00001" v-model.number="item.REQQTY" /></td>
                <td><input type="number" v-model.number="item.ORD" /></td>
                <td style="text-align: center;">
                  <button class="btn-row-del" @click="removeChildRow(idx)">✕</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </FormModal>

    <!-- ═══ 품목 선택 팝업 ═══ -->
    <Teleport to="body">
      <div v-if="showGoodsPicker" class="modal-overlay-picker" @click.self="showGoodsPicker=false">
        <div class="picker-modal">
          <div class="picker-header">
            <h3>품목 선택</h3>
            <button class="btn-close-sm" @click="showGoodsPicker=false">✕</button>
          </div>
          <div class="picker-search">
            <input type="text" v-model="goodsSearch" placeholder="품번 또는 품명 검색" @keyup.enter="filterGoods" />
            <button class="btn-search" @click="filterGoods">조회</button>
          </div>
          <div class="picker-list">
            <table class="picker-tbl">
              <thead><tr><th>품번</th><th>품명</th><th>품목유형</th></tr></thead>
              <tbody>
                <tr v-for="g in filteredGoods" :key="g.PARTNO" @click="selectGoods(g)" class="clickable">
                  <td>{{ g.PARTNO }}</td><td>{{ g.PARTNM }}</td><td>{{ g.PARTTYPE }}</td>
                </tr>
                <tr v-if="filteredGoods.length===0"><td colspan="3" class="empty">결과 없음</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../../../api'; 
import FormModal from '../../../components/common/FormModal.vue';

interface TreeNode {
  id: string;      // Unique key for v-for
  partNo: string;  // Product/Part Number
  partNm: string;  // Product Name
  data: any;       // Original BOM record (null if root)
  children: TreeNode[];
  expanded: boolean;
  level: number;
}

// ─────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────
const loading = ref(false);
const allBoms = ref<any[]>([]);
const allGoods = ref<any[]>([]);
const goodsMap = ref<Record<string, string>>({}); // PARTNO -> PARTNM
const treeData = ref<TreeNode[]>([]);

// Modal Form State
const form = reactive({
  PAR_PARTNO: '',
  REGUSERID: 1,
  details: [] as any[]
});
const editMode = ref(false);
const showModal = ref(false);
const lockParent = ref(false);

// Picker state
const showGoodsPicker = ref(false);
const goodsSearch = ref('');
const pickingType = ref<'parent' | 'child'>('parent');
const pickingChildIdx = ref(-1);
const filteredGoods = ref<any[]>([]);

// Get the PARTTYPE of the currently selected Parent Part
const selectedParentType = computed(() => {
  if (!form.PAR_PARTNO) return null;
  const parent = allGoods.value.find(g => g.PARTNO === form.PAR_PARTNO);
  return parent ? parent.PARTTYPE : null;
});

// PARTTYPE Hierarchy: 완제품 > 반제품 > 원자재
const TYPE_RANK: Record<string, number> = {
  'PARTGUBUN001': 3,  // 완제품
  'PARTGUBUN002': 2,  // 반제품
  'PARTGUBUN003': 1,  // 원자재
  'PARTGUBUN004': 1,  // 부자재
  // 기존 한글명 호환
  '완제품': 3,
  '반제품': 2,
  '원자재': 1
};

function openParentPicker() {
  if (editMode.value || lockParent.value) return;
  pickingType.value = 'parent';
  goodsSearch.value = '';
  filterGoods();
  showGoodsPicker.value = true;
}

function openChildPicker(idx: number) {
  pickingType.value = 'child';
  pickingChildIdx.value = idx;
  goodsSearch.value = '';
  filterGoods();
  showGoodsPicker.value = true;
}

function filterGoods() {
  const s = goodsSearch.value.toLowerCase();
  let baseList: any[] = [];
  
  if (pickingType.value === 'parent') {
    baseList = parentOptions.value;
  } else {
    // Child picker logic:
    // 1. Exclude the parent part itself
    // 2. Exclude items with PARTTYPE higher than or equal to the parent's type
    const pType = selectedParentType.value;
    const pRank = pType ? (TYPE_RANK[pType] || 0) : 0;
    
    baseList = allGoods.value.filter(g => {
      // Rule 1: Not the parent itself
      if (g.PARTNO === form.PAR_PARTNO) return false;
      
      // Rule 2: Child type rank must be strictly lower than parent type rank
      const cRank = TYPE_RANK[g.PARTTYPE] || 0;
      return cRank < pRank;
    });
  }
  
  if (s) {
    filteredGoods.value = baseList.filter(g => 
      (g.PARTNO && g.PARTNO.toLowerCase().includes(s)) || 
      (g.PARTNM && g.PARTNM.toLowerCase().includes(s))
    );
  } else {
    filteredGoods.value = baseList;
  }
}

function selectGoods(g: any) {
  if (pickingType.value === 'parent') {
    form.PAR_PARTNO = g.PARTNO;
  } else if (pickingType.value === 'child') {
    form.details[pickingChildIdx.value].CHILD_PARTNO = g.PARTNO;
  }
  showGoodsPicker.value = false;
}

// Filtered options for Parent Part Number (only "완제품" for new root registration)
const parentOptions = computed(() => {
  if (editMode.value || lockParent.value) {
    // In edit or add-child mode, show all goods so the current value can be mapped to a label
    return allGoods.value;
  }
  // In new root registration, only show Finished Products
  return allGoods.value.filter(g => g.PARTTYPE === 'PARTGUBUN001' || g.PARTTYPE === '완제품');
});

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
async function fetchAllData() {
  loading.value = true;
  try {
    const [bomRes, goodsRes] = await Promise.all([
      api.get('/api/master/bom', { params: { size: 9999 } }),
      api.get('/api/master/goods', { params: { size: 9999 } })
    ]);
    
    allBoms.value = bomRes.data.data || [];
    allGoods.value = goodsRes.data.data || [];
    
    // Build goods mapping
    const map: Record<string, string> = {};
    allGoods.value.forEach(g => { map[g.PARTNO] = g.PARTNM; });
    goodsMap.value = map;

    buildTree();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function buildTree() {
  const adjList: Record<string, any[]> = {};
  
  // Find all unique children to determine roots
  const childSet = new Set(allBoms.value.map(bom => bom.CHILD_PARTNO));
  let roots = Array.from(new Set(allBoms.value.map(bom => bom.PAR_PARTNO))).filter(p => !childSet.has(p));

  // If no true roots found (due to cycles), use all unique parents as roots
  if (roots.length === 0 && allBoms.value.length > 0) {
    roots = Array.from(new Set(allBoms.value.map(bom => bom.PAR_PARTNO)));
  }

  // Group by Parent Part No
  allBoms.value.forEach(bom => {
    if (!adjList[bom.PAR_PARTNO]) adjList[bom.PAR_PARTNO] = [];
    adjList[bom.PAR_PARTNO].push(bom);
  });

  // Sort
  Object.keys(adjList).forEach(key => {
    adjList[key].sort((a, b) => (a.ORD || 0) - (b.ORD || 0));
  });

  // Recursive Build
  function createNode(partNo: string, bomRecord: any, level: number, parentId: string, path: string[]): TreeNode {
    const id = parentId ? `${parentId}_${partNo}` : partNo;
    const currentPath = [...path, partNo];
    
    // Check for cycles in the current path to prevent infinite recursion
    const childrenRecords = adjList[partNo] || [];
    const children = childrenRecords
      .filter(childRec => !currentPath.includes(childRec.CHILD_PARTNO)) // Prevent direct cycles
      .map(childRec => createNode(childRec.CHILD_PARTNO, childRec, level + 1, id, currentPath));
    
    const existingNode = findNodeById(treeData.value, id);
    const expanded = existingNode ? existingNode.expanded : (level < 2); // Auto-expand first 2 levels

    return {
      id,
      partNo,
      partNm: goodsMap.value[partNo] || '',
      data: bomRecord,
      children,
      expanded,
      level
    };
  }

  treeData.value = roots.map(rootPartNo => createNode(rootPartNo, null, 0, '', []));
}

function findNodeById(nodes: TreeNode[], id: string): TreeNode | null {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children.length > 0) {
      const found = findNodeById(node.children, id);
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
  lockParent.value = false;
  form.PAR_PARTNO = '';
  form.details = [];
  showModal.value = true;
}

async function openAddChild(node: TreeNode) {
  editMode.value = false;
  lockParent.value = true;
  form.PAR_PARTNO = node.partNo;
  try {
    const res = await api.get(`/api/master/bom/detail/${node.partNo}`);
    form.details = res.data || [];
  } catch (e) {
    form.details = [];
  }
  showModal.value = true;
}

async function openEditNode(node: TreeNode) {
  const par_partno = node.data ? node.data.PAR_PARTNO : node.partNo;
  editMode.value = true;
  lockParent.value = true;
  form.PAR_PARTNO = par_partno;
  try {
    const res = await api.get(`/api/master/bom/detail/${par_partno}`);
    form.details = res.data || [];
  } catch (e) {
    form.details = [];
  }
  showModal.value = true;
}

function addChildRow() {
  form.details.push({ CHILD_PARTNO: '', REQQTY: 1, ORD: form.details.length + 1 });
}

function removeChildRow(index: number) {
  form.details.splice(index, 1);
}

async function deleteNode(node: TreeNode) {
  if (!node.data) return;
  if (!confirm(`'${node.partNo}' (${node.partNm}) 관계를 삭제하시겠습니까?`)) return;
  try {
    await api.delete(`/api/master/bom/${node.data.PAR_PARTNO}/${node.data.CHILD_PARTNO}`);
    alert('삭제되었습니다.');
    fetchAllData();
  } catch (e) {
    console.error(e);
  }
}

async function handleSave() {
  if (!form.PAR_PARTNO) {
    alert('모품번을 선택하세요.');
    return;
  }
  if (form.details.some(d => !d.CHILD_PARTNO)) {
    alert('자품번을 모두 선택하거나 빈 줄을 제거하세요.');
    return;
  }

  try {
    await api.post('/api/master/bom', form);
    alert('저장되었습니다.');
    showModal.value = false;
    fetchAllData();
  } catch (e) {
    console.error(e);
    alert('저장 중 오류가 발생했습니다.');
  }
}

onMounted(() => {
  fetchAllData();
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
.code-text { font-weight: 600; color: #1e293b; }

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
.fg { display: grid; grid-template-columns: repeat(1, 1fr); gap: 14px; }
.ff { display: flex; flex-direction: column; gap: 5px; }
.ff label { font-size: .82rem; font-weight: 600; color: #64748b; }
.ff input, .ff select { padding: 9px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: .88rem; transition: border-color .15s; }
.ff input:focus, .ff select:focus { border-color: #667eea; outline: none; box-shadow: 0 0 0 3px rgba(102,126,234,.1); }
.ff input:disabled, .ff select:disabled { background: #f8fafc; color: #94a3b8; }

/* Detail Table Styles */
.detail-section { margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.detail-header { background: #f8fafc; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; }
.detail-title { font-size: 0.85rem; font-weight: 700; color: #475569; }
.btn-row-add { background: #6366f1; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; cursor: pointer; }
.btn-row-add:hover:not(:disabled) { background: #4f46e5; }
.btn-row-add:disabled { background: #cbd5e1; cursor: not-allowed; }

.detail-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.detail-table th { background: #f1f5f9; padding: 8px 10px; text-align: left; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.detail-table td { padding: 6px 10px; border-bottom: 1px solid #f1f5f9; }
.detail-table input, .detail-table select { width: 100%; padding: 6px 8px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.82rem; }
.detail-table input:focus, .detail-table select:focus { border-color: #6366f1; outline: none; }

.btn-row-del { background: #fee2e2; color: #ef4444; border: 1px solid #fecaca; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; }
.btn-row-del:hover { background: #fecaca; }

.empty-detail { text-align: center; padding: 20px; color: #94a3b8; font-style: italic; }

/* ═══ 품목 선택 팝업 ═══ */
.modal-overlay-picker{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1100;display:flex;align-items:center;justify-content:center}
.picker-modal{background:#fff;border-radius:10px;width:500px;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.2);overflow:hidden}
.picker-header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#f8f9fa;border-bottom:1px solid #e9ecef}
.picker-header h3{margin:0;font-size:1.05rem;font-weight:700;color:#2c3e50}
.btn-close-sm{background:none;border:none;font-size:1.2rem;cursor:pointer;color:#95a5a6}
.btn-close-sm:hover{color:#e74c3c}
.picker-search{display:flex;gap:8px;padding:14px 20px;background:#fff;border-bottom:1px solid #e9ecef}
.picker-search input{flex:1;padding:8px 12px;border:1px solid #dfe6e9;border-radius:6px;font-size:.9rem}
.picker-list{flex:1;overflow-y:auto;padding:10px 20px 20px}
.picker-tbl{width:100%;border-collapse:collapse;font-size:.85rem}
.picker-tbl th{padding:8px 10px;background:#f1f5f9;text-align:left;font-weight:600;color:#3a4a6b;border-bottom:1px solid #e9ecef}
.picker-tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f5}
.clickable{cursor:pointer;transition:background .12s}.clickable:hover{background:#e8f5e9}
.input-with-btn{display:flex;gap:4px;height: 36px;}
.input-with-btn input{flex:1;cursor:pointer;background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:0 10px;}
.btn-search-sm{background:#667eea;color:#fff;border:none;padding:0 12px;border-radius:6px;cursor:pointer;font-size:1rem;}
.ff label.required::before { content: '◎ '; color: #27ae60; }
th.req-th::before { content: '* '; color: #e74c3c; }
</style>