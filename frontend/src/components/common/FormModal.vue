<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="visible" @click.self="$emit('close')">
      <div class="modal-container" :style="{ width: width }">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <button class="btn-close" @click="$emit('close')">✕</button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div class="modal-footer">
          <button v-if="showDelete" class="btn-danger" @click="$emit('delete')">🗑 삭제</button>
          <div class="spacer"></div>
          <button class="btn-secondary" @click="$emit('close')">취소</button>
          <button v-if="showSave !== false" class="btn-primary" @click="$emit('save')">💾 저장</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  visible: boolean;
  title: string;
  width?: string;
  showDelete?: boolean;
  showSave?: boolean;
}>(), {
  showSave: true
});
defineEmits(['close', 'save', 'delete']);
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.45); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-container { background: #fff; border-radius: 16px; max-width: 94vw; max-height: 88vh; display: flex; flex-direction: column; box-shadow: 0 24px 80px rgba(0,0,0,0.22); animation: modalIn 0.22s ease-out; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-20px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; border-bottom: 1px solid #f0f2f5; }
.modal-header h3 { margin: 0; font-size: 1.05rem; font-weight: 700; color: #1e293b; }
.btn-close { background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px; font-size: 1rem; cursor: pointer; color: #64748b; transition: all 0.15s; display: flex; align-items: center; justify-content: center; }
.btn-close:hover { background: #e2e8f0; color: #334155; }
.modal-body { padding: 22px 24px; overflow-y: auto; flex: 1; }
.modal-footer { display: flex; align-items: center; gap: 8px; padding: 14px 24px; border-top: 1px solid #f0f2f5; }
.spacer { flex: 1; }
.btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; padding: 9px 22px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.88rem; transition: opacity 0.15s; }
.btn-primary:hover { opacity: 0.9; }
.btn-danger { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; padding: 9px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.88rem; }
.btn-danger:hover { background: #fecaca; }
.btn-secondary { background: #f1f5f9; color: #475569; border: none; padding: 9px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.88rem; }
.btn-secondary:hover { background: #e2e8f0; }
</style>
