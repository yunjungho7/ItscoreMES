import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { useNotification } from './composables/useNotification'

const app = createApp(App)

// Global Error Handler
const { notifyError } = useNotification()
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Global Error:', err, info)
  notifyError('An unexpected error occurred in the application.')
}

app.use(router).mount('#app')
