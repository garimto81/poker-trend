// 환경별 설정 파일
// 실제 운영 환경에서는 이 파일을 .env나 환경변수로 관리해야 합니다.

window.ENV_CONFIG = {
    DEVELOPMENT: {
        FIREBASE_API_KEY: "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        FIREBASE_AUTH_DOMAIN: "ggp-camera.firebaseapp.com",
        FIREBASE_PROJECT_ID: "ggp-camera",
        FIREBASE_STORAGE_BUCKET: "ggp-camera.appspot.com",
        FIREBASE_MESSAGING_SENDER_ID: "906682771595",
        FIREBASE_APP_ID: "1:906682771595:web:431b539435f4a0ca294c8e",
        FIREBASE_MEASUREMENT_ID: "G-JLR9TMLSS1",
        DEBUG_MODE: true
    },
    PRODUCTION: {
        FIREBASE_API_KEY: window.FIREBASE_API_KEY,
        FIREBASE_AUTH_DOMAIN: window.FIREBASE_AUTH_DOMAIN,
        FIREBASE_PROJECT_ID: window.FIREBASE_PROJECT_ID,
        FIREBASE_STORAGE_BUCKET: window.FIREBASE_STORAGE_BUCKET,
        FIREBASE_MESSAGING_SENDER_ID: window.FIREBASE_MESSAGING_SENDER_ID,
        FIREBASE_APP_ID: window.FIREBASE_APP_ID,
        FIREBASE_MEASUREMENT_ID: window.FIREBASE_MEASUREMENT_ID,
        DEBUG_MODE: false
    }
};

// 현재 환경 감지 (실제 운영에서는 빌드 시 설정)
window.CURRENT_ENV = window.location.hostname === 'localhost' || window.location.hostname.includes('127.0.0.1') 
    ? 'DEVELOPMENT' 
    : 'PRODUCTION';

console.log(`Environment: ${window.CURRENT_ENV}`);