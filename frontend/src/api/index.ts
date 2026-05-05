import axios from 'axios';
import { useNotification } from '../composables/useNotification';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 5000,
});

const { notifyError } = useNotification();

// 전역 요청 인터셉터 (토큰 주입)
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 전역 응답 인터셉터 (에러 캐치)
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            // 인증 만료 또는 유효하지 않은 경우
            localStorage.removeItem('user');
            localStorage.removeItem('access_token');
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        if (error.response && error.response.data) {
            // 요구사항에 맞춰 {statusCode: x, message: y} 포맷 캐치
            const { statusCode, message } = error.response.data;
            notifyError(message || 'Unknown Error', statusCode || error.response.status);
        } else {
            notifyError('Network error or server is down.');
        }
        return Promise.reject(error);
    }
);

export default api;
