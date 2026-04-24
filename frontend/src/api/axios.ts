import axios from 'axios';
import { storage } from '../utils/storage';

const isProd = process.env.NODE_ENV === 'production';
const BASE_URL = process.env.EXPO_PUBLIC_API_URL || (isProd ? 'https://neuroshield-ai-fraud-detection-app.onrender.com' : 'http://127.0.0.1:8000');

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000, // 15 seconds — prevents infinite loading if backend is down
});

apiClient.interceptors.request.use(async (config) => {
  const token = await storage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
