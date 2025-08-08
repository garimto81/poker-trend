// Firebase 런타임 설정 예시 파일
// 실제 운영환경에서는 서버에서 동적으로 생성하거나 빌드 시 주입해야 합니다.

// 방법 1: 직접 window 객체에 설정
window.FIREBASE_API_KEY = "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k";
window.FIREBASE_AUTH_DOMAIN = "ggp-camera.firebaseapp.com";
window.FIREBASE_PROJECT_ID = "ggp-camera";
window.FIREBASE_STORAGE_BUCKET = "ggp-camera.appspot.com";
window.FIREBASE_MESSAGING_SENDER_ID = "906682771595";
window.FIREBASE_APP_ID = "1:906682771595:web:431b539435f4a0ca294c8e";
window.FIREBASE_MEASUREMENT_ID = "G-JLR9TMLSS1";

// 방법 2: 환경별 설정 객체로 관리
window.RUNTIME_CONFIG = {
    firebase: {
        apiKey: "AIzaSyD6LVOtT0x30CQNZDt5aSUEBKT8vXPhM6k",
        authDomain: "ggp-camera.firebaseapp.com",
        projectId: "ggp-camera",
        storageBucket: "ggp-camera.appspot.com",
        messagingSenderId: "906682771595",
        appId: "1:906682771595:web:431b539435f4a0ca294c8e",
        measurementId: "G-JLR9TMLSS1"
    },
    environment: "development", // 또는 "production"
    debugMode: true
};

console.log("🔥 Firebase runtime config loaded");