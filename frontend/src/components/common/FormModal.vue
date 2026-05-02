<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="visible" @click.self="$emit('close')">
      <div class="modal-container" :style="{ width: width }">
        <div class="modal-header">
          <div class="header-title-wrap">
            <span v-if="icon" class="header-icon">{{ icon }}</span>
            <h3>{{ title }}</h3>
          </div>
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
  icon?: string;
  width?: string;
  showDelete?: boolean;
  showSave?: boolean;
}>(), {
  showSave: true
});
defineEmits(['close', 'save', 'delete']);
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-container { background: #fff; border-radius: 20px; max-width: 94vw; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid #e2e8f0; }
@keyframes modalIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px; border-bottom: 1px solid #f1f5f9; }
.header-title-wrap { display: flex; align-items: center; gap: 12px; }
.header-icon { font-size: 1.4rem; display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: #f8fafc; border-radius: 12px; border: 1px solid #f1f5f9; }
.modal-header h3 { margin: 0; font-size: 1.15rem; font-weight: 800; color: #0f172a; letter-spacing: -0.025em; }
.btn-close { background: #f8fafc; border: 1px solid #f1f5f9; width: 36px; height: 36px; border-radius: 10px; font-size: 1.1rem; cursor: pointer; color: #94a3b8; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
.btn-close:hover { background: #fee2e2; color: #ef4444; border-color: #fecaca; transform: rotate(90deg); }
.modal-body { padding: 24px 28px; overflow-y: auto; flex: 1; scrollbar-gutter: stable; }
.modal-footer { display: flex; align-items: center; gap: 12px; padding: 16px 28px; border-top: 1px solid #f1f5f9; background: #f8fafc; border-radius: 0 0 20px 20px; }
.spacer { flex: 1; }
.btn-primary { background: #0f172a; color: #fff; border: none; padding: 10px 24px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.95rem; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.btn-primary:hover { background: #1e293b; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(15,23,42,0.15); }
.btn-danger { background: #fff; color: #dc2626; border: 1px solid #fecaca; padding: 10px 20px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.95rem; transition: all 0.2s; }
.btn-danger:hover { background: #fef2f2; border-color: #ef4444; }
.btn-secondary { background: #fff; color: #475569; border: 1px solid #e2e8f0; padding: 10px 20px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.95rem; transition: all 0.2s; }
.btn-secondary:hover { background: #f8fafc; border-color: #cbd5e1; }
</style>
