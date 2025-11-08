import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:18000';

export const apiClient = axios.create({
  baseURL,
  timeout: 8000,
});

apiClient.interceptors.response.use(
  (resp) => resp,
  (error) => {
    // Normalize error message
    const message = error.response?.data?.error || error.message || 'Request failed';
    return Promise.reject(new Error(message));
  }
);
