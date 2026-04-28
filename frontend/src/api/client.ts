import { client } from './generated/client.gen';
import { useNotification } from '../composables/useNotification';

const { notifyError } = useNotification();

// Set base URL if needed
client.setConfig({
  baseUrl: (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000',
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
