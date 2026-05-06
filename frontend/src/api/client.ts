import { client } from './generated/client.gen';
import { useNotification } from '../composables/useNotification';

const { notifyError } = useNotification();

// Set base URL if needed
client.setConfig({
  // Nginx 프록시(/api)를 통해 백엔드와 통신하므로 상대 경로 사용
  baseUrl: (import.meta.env.VITE_API_BASE_URL as string) || '/api',
});

// Request interceptor for Auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error interceptor
client.interceptors.error.use((error, response) => {
  let message = 'An unexpected error occurred';
  const statusCode = response?.status;

  if (error && typeof error === 'object') {
    if ('message' in error) {
      message = (error as any).message;
    }
    // FastAPI often returns errors in 'detail' field
    if ('detail' in error) {
      if (typeof (error as any).detail === 'string') {
        message = (error as any).detail;
      } else if (Array.isArray((error as any).detail)) {
        // Pydantic validation errors
        message = (error as any).detail.map((d: any) => `${d.loc?.join('.') || 'error'}: ${d.msg}`).join(', ');
      }
    }
  }

  notifyError(message, statusCode);
  return error;
});

export default client;
