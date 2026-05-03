<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content printer-modal">
      <div class="modal-header-custom">
        <h2>📠 로컬 프린터 설정 (QZ Tray)</h2>
        <div class="modal-header-btns">
          <button class="btn-modal-action confirm" @click="save">💾 저장</button>
          <button class="btn-modal-action close" @click="$emit('close')">❌ 닫기</button>
        </div>
      </div>
      <div class="modal-body">
        <!-- QZ Tray 연결 상태 -->
        <div class="connection-status" :class="{ connected: isConnected }">
          <span class="dot"></span>
          {{ isConnected ? 'QZ Tray 연결됨' : 'QZ Tray 연결 안됨 (프로그램 실행 필요)' }}
          <button v-if="!isConnected" class="btn-mini" @click="connectQZ">재연결</button>
        </div>

        <div class="setting-row">
          <label>현재 선택된 프린터</label>
          <select v-model="selectedPrinter">
            <option value="">(선택 안함)</option>
            <option v-for="p in printerList" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div class="setting-row fetch-row">
          <label>OS 프린터 불러오기</label>
          <button class="btn-fetch" @click="fetchLocalPrinters" :disabled="!isConnected">
            🔄 로컬 프린터 목록 갱신
          </button>
        </div>

        <div class="printer-list-manage">
          <label>등록된 프린터 목록</label>
          <ul>
            <li v-for="(p, index) in printerList" :key="p">
              <span>{{ p }}</span>
              <button class="btn-del" @click="removePrinter(index)">🗑️</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as qz from 'qz-tray';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits(['close', 'saved']);

const selectedPrinter = ref('');
const printerList = ref<string[]>([]);
const isConnected = ref(false);

onMounted(async () => {
  // 1. 기존 저장된 목록 로드
  const saved = localStorage.getItem('local_printer_list');
  if (saved) {
    printerList.value = JSON.parse(saved);
  } else {
    printerList.value = ['Samsung M228x', 'Label Printer 1'];
    saveList();
  }
  
  selectedPrinter.value = localStorage.getItem('selected_printer') || '';

  // 2. QZ Tray 연결 시도
  await connectQZ();
});

onBeforeUnmount(async () => {
  if (qz.websocket.isActive()) {
    await qz.websocket.disconnect();
  }
});

async function connectQZ() {
  try {
    if (!qz.websocket.isActive()) {
      await qz.websocket.connect();
    }
    isConnected.value = true;
    console.log('QZ Tray Connected');
  } catch (err) {
    isConnected.value = false;
    console.warn('QZ Tray connection failed. Please ensure QZ Tray is running.');
  }
}

async function fetchLocalPrinters() {
  if (!isConnected.value) {
    await connectQZ();
    if (!isConnected.value) {
      alert('QZ Tray 프로그램이 실행 중인지 확인해 주세요.');
      return;
    }
  }

  try {
    const found: string[] = await qz.printers.find();
    // 기존 목록과 합치기 (중복 제거)
    const combined = Array.from(new Set([...printerList.value, ...found]));
    printerList.value = combined;
    saveList();
    alert(`로컬 PC에서 ${found.length}개의 프린터를 찾았습니다.`);
  } catch (err) {
    console.error('Error fetching printers:', err);
    alert('프린터 목록을 가져오는 중 오류가 발생했습니다.');
  }
}

function removePrinter(index: number) {
  const removed = printerList.value.splice(index, 1)[0];
  if (selectedPrinter.value === removed) {
    selectedPrinter.value = '';
  }
  saveList();
}

function saveList() {
  localStorage.setItem('local_printer_list', JSON.stringify(printerList.value));
}

function save() {
  localStorage.setItem('selected_printer', selectedPrinter.value);
  emit('saved', selectedPrinter.value);
  emit('close');
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.modal-content.printer-modal {
  background: white; width: 420px; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.modal-header-custom {
  background-color: #2c3e50; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center;
}
.modal-header-custom h2 { margin: 0; font-size: 1.1rem; }
.modal-header-btns { display: flex; gap: 8px; }
.btn-modal-action { padding: 6px 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.85rem; }
.btn-modal-action.confirm { background: #40c057; color: white; }
.btn-modal-action.close { background: #fa5252; color: white; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 15px; }

/* Connection Status */
.connection-status {
  padding: 10px; background: #fff5f5; border-radius: 8px; font-size: 0.85rem; font-weight: bold;
  display: flex; align-items: center; gap: 10px; color: #e03131; border: 1px solid #ffc9c9;
}
.connection-status.connected {
  background: #ebfbee; color: #2f9e44; border-color: #b2f2bb;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: #fa5252; }
.connected .dot { background: #40c057; box-shadow: 0 0 5px #40c057; }

.setting-row { display: flex; flex-direction: column; gap: 8px; }
.setting-row label { font-weight: 800; color: #495057; font-size: 0.9rem; }
.setting-row select { padding: 10px; border: 1px solid #dee2e6; border-radius: 8px; font-size: 1rem; width: 100%; }

.btn-fetch {
  padding: 10px; background: #339af0; color: white; border: none; border-radius: 8px;
  font-weight: bold; cursor: pointer; transition: background 0.2s;
}
.btn-fetch:hover:not(:disabled) { background: #228be6; }
.btn-fetch:disabled { background: #dee2e6; cursor: not-allowed; }

.btn-mini { padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; border: 1px solid #dee2e6; background: white; cursor: pointer; }

.printer-list-manage ul { list-style: none; padding: 0; margin: 5px 0 0 0; border: 1px solid #eee; border-radius: 8px; max-height: 120px; overflow-y: auto; }
.printer-list-manage li { padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; font-size: 0.9rem; }
.printer-list-manage li:last-child { border-bottom: none; }
.btn-del { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 4px; border-radius: 4px; }
.btn-del:hover { background: #fff5f5; }
</style>
