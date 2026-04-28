<template>
  <div class="notification-container">
    <transition-group name="toast">
      <div
        v-for="toast in notifications"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <div class="toast-content">
          <span v-if="toast.statusCode" class="status-code">[{{ toast.statusCode }}]</span>
          <span class="message">{{ toast.message }}</span>
        </div>
        <button class="close-btn" @click="removeNotification(toast.id)">&times;</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useNotification } from '../../composables/useNotification';

const { notifications, removeNotification } = useNotification();
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  color: white;
  min-width: 250px;
  animation: slideIn 0.3s ease-out;
}

.toast.error {
  background-color: #f44336;
}

.toast.success {
  background-color: #4caf50;
}

.toast.warning {
  background-color: #ff9800;
}

.toast.info {
  background-color: #2196f3;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-code {
  font-weight: bold;
  font-size: 0.9em;
}

.message {
  font-size: 0.95em;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  opacity: 0.8;
}

.close-btn:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
