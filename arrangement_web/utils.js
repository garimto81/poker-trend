// 유틸리티 함수들
import { CONSTANTS, ERROR_MESSAGES } from './config.js';

// 에러 처리 클래스
export class ErrorHandler {
    static handle(error, context = '', showToUser = true) {
        console.error(`Error in ${context}:`, error);
        
        let userMessage = ERROR_MESSAGES.SAVE_FAILED;
        
        if (error.code) {
            switch (error.code) {
                case 'permission-denied':
                    userMessage = ERROR_MESSAGES.PERMISSION_DENIED;
                    break;
                case 'network-request-failed':
                case 'unavailable':
                    userMessage = ERROR_MESSAGES.NETWORK_ERROR;
                    break;
                case 'invalid-argument':
                    userMessage = ERROR_MESSAGES.INVALID_DATA;
                    break;
                default:
                    userMessage = ERROR_MESSAGES.SAVE_FAILED;
            }
        }
        
        if (showToUser) {
            this.showUserMessage(userMessage);
        }
        
        return userMessage;
    }
    
    static showUserMessage(message) {
        // 사용자에게 에러 메시지 표시
        const event = new CustomEvent('showErrorMessage', { detail: message });
        document.dispatchEvent(event);
    }
    
    static async withRetry(operation, maxRetries = CONSTANTS.MAX_RETRIES) {
        let lastError;
        
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                if (i < maxRetries - 1) {
                    // 지수 백오프: 1초, 2초, 4초
                    await this.delay(Math.pow(2, i) * 1000);
                }
            }
        }
        
        throw lastError;
    }
    
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 입력 검증 클래스
export class InputValidator {
    static validateTaskTitle(title) {
        if (!title || typeof title !== 'string') {
            throw new Error('제목을 입력해주세요.');
        }
        
        const trimmed = title.trim();
        if (trimmed.length === 0) {
            throw new Error('제목을 입력해주세요.');
        }
        
        if (trimmed.length > CONSTANTS.MAX_TASK_TITLE_LENGTH) {
            throw new Error(`제목은 ${CONSTANTS.MAX_TASK_TITLE_LENGTH}자 이하여야 합니다.`);
        }
        
        // XSS 방지를 위한 기본적인 HTML 태그 제거
        return this.sanitizeHTML(trimmed);
    }
    
    static validateCategoryName(name) {
        if (!name || typeof name !== 'string') {
            throw new Error('카테고리 이름을 입력해주세요.');
        }
        
        const trimmed = name.trim();
        if (trimmed.length === 0) {
            throw new Error('카테고리 이름을 입력해주세요.');
        }
        
        if (trimmed.length > CONSTANTS.MAX_CATEGORY_NAME_LENGTH) {
            throw new Error(`카테고리 이름은 ${CONSTANTS.MAX_CATEGORY_NAME_LENGTH}자 이하여야 합니다.`);
        }
        
        return this.sanitizeHTML(trimmed);
    }
    
    static validateUrl(url) {
        if (!url) return ''; // URL은 선택사항
        
        try {
            const urlObj = new URL(url);
            // HTTP/HTTPS만 허용
            if (!['http:', 'https:'].includes(urlObj.protocol)) {
                throw new Error('HTTP 또는 HTTPS URL만 허용됩니다.');
            }
            return url;
        } catch {
            throw new Error('유효하지 않은 URL입니다.');
        }
    }
    
    static validateDate(date) {
        if (!date) {
            throw new Error('날짜를 입력해주세요.');
        }
        
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) {
            throw new Error('유효하지 않은 날짜입니다.');
        }
        
        return date;
    }
    
    static validateProgress(progress) {
        const num = parseInt(progress, 10);
        if (isNaN(num) || num < 0 || num > 100) {
            throw new Error('진행률은 0-100 사이의 숫자여야 합니다.');
        }
        return num;
    }
    
    static sanitizeHTML(str) {
        // 기본적인 HTML 태그 및 스크립트 제거
        return str.replace(/<[^>]*>/g, '').replace(/javascript:/gi, '');
    }
}

// 날짜 유틸리티
export class DateUtils {
    static formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        d.setHours(0, 0, 0, 0);
        const year = d.getFullYear();
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        const day = d.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    static isToday(date) {
        return this.formatDate(date) === this.formatDate(new Date());
    }
    
    static isWeekend(date) {
        const day = new Date(date).getDay();
        return day === 0 || day === 6; // 일요일(0) 또는 토요일(6)
    }
    
    static getDateRange(centerDate, rangeDays = CONSTANTS.DATE_RANGE) {
        const start = new Date(centerDate);
        start.setDate(start.getDate() - rangeDays);
        start.setHours(0, 0, 0, 0);
        
        const end = new Date(centerDate);
        end.setDate(end.getDate() + rangeDays);
        end.setHours(0, 0, 0, 0);
        
        return { start, end };
    }
    
    static generateDateArray(startDate, endDate) {
        const dates = [];
        const current = new Date(startDate);
        
        while (current <= endDate) {
            dates.push(new Date(current));
            current.setDate(current.getDate() + 1);
        }
        
        return dates;
    }
}

// 디바운스 함수
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 쓰로틀 함수
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 로컬 스토리지 유틸리티
export class StorageUtils {
    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    }
    
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.warn('LocalStorage 저장 실패:', error);
        }
    }
    
    static remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.warn('LocalStorage 삭제 실패:', error);
        }
    }
}