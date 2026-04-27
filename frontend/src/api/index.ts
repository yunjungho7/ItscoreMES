import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 5000,
});

// 전역 응답 인터셉터 (에러 캐치)
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.data) {
            // 요구사항에 맞춰 {statusCode: x, message: y} 포맷 캐치
            const { statusCode, message } = error.response.data;
            alert(`[Error ${statusCode || error.response.status}] ${message || 'Unknown Error'}`);
        } else {
            alert(`[Error] Network error or server is down.`);
        }
        return Promise.reject(error);
    }
);

export default api;
