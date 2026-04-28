import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { useNotification } from './composables/useNotification'

const app = createApp(App)

const { notifyError, notifyInfo } = useNotification()

// Global Error Handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Global Error:', err, info)
  notifyError('An unexpected error occurred in the application.')
}

// window.alert Shim (Phase 1 Stabilization)
window.alert = (message: string) => {
  notifyInfo(message)
}

app.use(router).mount('#app')
