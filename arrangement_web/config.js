// Firebase 환경 설정
export const getFirebaseConfig = () => {
    const config = {
        apiKey: window.FIREBASE_API_KEY || "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        authDomain: window.FIREBASE_AUTH_DOMAIN || "ggp-camera.firebaseapp.com",
        projectId: window.FIREBASE_PROJECT_ID || "ggp-camera",
        storageBucket: window.FIREBASE_STORAGE_BUCKET || "ggp-camera.appspot.com",
        messagingSenderId: window.FIREBASE_MESSAGING_SENDER_ID || "906682771595",
        appId: window.FIREBASE_APP_ID || "1:906682771595:web:431b539435f4a0ca294c8e",
        measurementId: window.FIREBASE_MEASUREMENT_ID || "G-JLR9TMLSS1"
    };
    
    // 설정 유효성 검사
    if (!config.apiKey || config.apiKey === 'undefined') {
        throw new Error('유효한 Firebase API 키가 설정되지 않았습니다.');
    }
    
    // 개발 환경에서만 로그 출력
    if (window.location.hostname === 'localhost' || window.location.hostname.includes('127.0.0.1')) {
        console.log('🔥 Firebase config loaded:', { ...config, apiKey: config.apiKey.substring(0, 10) + '...' });
    }

    return config;
};

// 상수 설정
export const CONSTANTS = {
    DATE_RANGE: 15, // 타임라인 표시 일수
    MAX_TASK_TITLE_LENGTH: 200,
    MAX_CATEGORY_NAME_LENGTH: 50,
    RENDER_DEBOUNCE_MS: 100,
    AUTO_SAVE_DELAY_MS: 1000,
    MAX_RETRIES: 3
};

// 담당자 설정
export const ASSIGNEES = { 
    "Aiden Kim":   {i:"A", c:"bg-blue-500",   hex: "#3b82f6"}, 
    "Matthew Kim": {i:"M", c:"bg-green-500",  hex: "#22c55e"}, 
    "Kai Kim":     {i:"K", c:"bg-yellow-500", hex: "#eab308"}, 
    "Trey Song":   {i:"T", c:"bg-purple-500", hex: "#a855f7"} 
};

// 에러 메시지
export const ERROR_MESSAGES = {
    FIREBASE_INIT_FAILED: "서비스 초기화에 실패했습니다. 페이지를 새로고침해주세요.",
    NETWORK_ERROR: "네트워크 연결을 확인해주세요.",
    PERMISSION_DENIED: "권한이 없습니다.",
    INVALID_DATA: "잘못된 데이터입니다.",
    SAVE_FAILED: "저장에 실패했습니다. 다시 시도해주세요.",
    DELETE_FAILED: "삭제에 실패했습니다. 다시 시도해주세요."
};