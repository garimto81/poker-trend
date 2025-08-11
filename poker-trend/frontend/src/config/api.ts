// API 설정
const isDevelopment = process.env.NODE_ENV === 'development';
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// API 기본 URL 설정
export const API_BASE_URL = (() => {
  // 환경변수에서 API URL 가져오기
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // 로컬 개발 환경
  if (isDevelopment || isLocalhost) {
    return 'http://localhost:3000';
  }
  
  // 프로덕션 환경 - GitHub Pages
  return 'https://api.garimto81.com';
})();

// WebSocket URL 설정
export const WS_BASE_URL = (() => {
  // 환경변수에서 WebSocket URL 가져오기
  if (process.env.REACT_APP_WS_URL) {
    return process.env.REACT_APP_WS_URL;
  }
  
  // 로컬 개발 환경
  if (isDevelopment || isLocalhost) {
    return 'ws://localhost:3000';
  }
  
  // 프로덕션 환경
  return 'wss://api.garimto81.com';
})();

// API 엔드포인트
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    register: '/api/auth/register',
    profile: '/api/auth/profile',
    refresh: '/api/auth/refresh',
  },
  
  // Trends
  trends: {
    list: '/api/trends',
    latest: '/api/trends/latest',
    details: (id: string) => `/api/trends/${id}`,
    stats: '/api/trends/stats',
  },
  
  // Content
  content: {
    list: '/api/content',
    create: '/api/content/create',
    details: (id: string) => `/api/content/${id}`,
    upload: '/api/content/upload',
    templates: '/api/content/templates',
  },
  
  // Analytics
  analytics: {
    dashboard: '/api/analytics/dashboard',
    performance: '/api/analytics/performance',
    trends: '/api/analytics/trends',
    export: '/api/analytics/export',
  },
  
  // Health Check
  health: '/health',
};

// Axios 기본 설정
export const axiosConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// GitHub Pages 특화 설정
export const isGitHubPages = window.location.hostname.includes('github.io') || 
                            window.location.hostname.includes('garimto81.com');

// 모의 데이터 사용 여부 (GitHub Pages에서 백엔드 없이 테스트용)
export const USE_MOCK_DATA = isGitHubPages && !process.env.REACT_APP_API_URL;

export default {
  API_BASE_URL,
  WS_BASE_URL,
  API_ENDPOINTS,
  axiosConfig,
  isGitHubPages,
  USE_MOCK_DATA,
};