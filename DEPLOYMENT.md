# 배포 가이드

## 1. 사전 요구사항

### 1.1 시스템 요구사항
- Ubuntu 20.04 LTS 이상
- Docker 20.10+ 및 Docker Compose 2.0+
- 최소 4GB RAM, 20GB 스토리지
- Python 3.11+ (로컬 개발용)

### 1.2 필수 API 키
- YouTube Data API v3 키
- Google Gemini AI API 키
- Slack Webhook URL
- PostgreSQL 데이터베이스 자격 증명

## 2. 환경 설정

### 2.1 환경 변수 파일 생성
`.env` 파일을 프로젝트 루트에 생성:

```bash
# API Keys
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=poker_trend
POSTGRES_USER=poker_user
POSTGRES_PASSWORD=secure_password_here

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here

# Application
APP_ENV=production
API_KEY=your_internal_api_key_here
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO

# Scheduler
TIMEZONE=Asia/Seoul
DAILY_REPORT_HOUR=10
WEEKLY_REPORT_HOUR=12
MONTHLY_REPORT_HOUR=14
```

### 2.2 디렉토리 구조 생성
```bash
mkdir -p logs data/postgres data/redis
chmod -R 755 logs data
```

## 3. Docker 배포

### 3.1 Docker Compose 설정
`docker-compose.yml` 파일:

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: poker-trend-app
    ports:
      - "8000:8000"
    environment:
      - ENV_FILE=.env
    volumes:
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: poker-trend-db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: poker-trend-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: poker-trend-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

### 3.2 배포 실행
```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps
```

## 4. 데이터베이스 초기화

### 4.1 스키마 생성
```bash
# 데이터베이스 컨테이너 접속
docker exec -it poker-trend-db psql -U poker_user -d poker_trend

# SQL 스크립트 실행
docker exec -i poker-trend-db psql -U poker_user -d poker_trend < scripts/init_db.sql
```

### 4.2 초기 데이터 입력
```bash
# 키워드 데이터 입력
docker exec -it poker-trend-app python scripts/init_keywords.py
```

## 5. 프로덕션 설정

### 5.1 Nginx 설정
`nginx/nginx.conf`:

```nginx
upstream app {
    server app:8000;
}

server {
    listen 80;
    server_name poker-trend.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name poker-trend.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        proxy_pass http://app/api/v1/health;
    }
}
```

### 5.2 SSL 인증서 설정
```bash
# Let's Encrypt 사용
docker run -it --rm \
  -v ./nginx/ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  -d poker-trend.com
```

## 6. 모니터링 설정

### 6.1 헬스체크 설정
```bash
# 헬스체크 스크립트
cat > scripts/healthcheck.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
if [ $response -eq 200 ]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed"
    exit 1
fi
EOF

chmod +x scripts/healthcheck.sh
```

### 6.2 로그 로테이션
```bash
# logrotate 설정
cat > /etc/logrotate.d/poker-trend << 'EOF'
/home/ubuntu/poker-trend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
EOF
```

## 7. 백업 설정

### 7.1 데이터베이스 백업
```bash
# 백업 스크립트
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgres"
mkdir -p $BACKUP_DIR

docker exec poker-trend-db pg_dump -U poker_user poker_trend | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x scripts/backup.sh

# Cron 작업 추가
echo "0 2 * * * /home/ubuntu/poker-trend/scripts/backup.sh" | crontab -
```

## 8. 운영 관리

### 8.1 서비스 재시작
```bash
# 특정 서비스만 재시작
docker-compose restart app

# 전체 서비스 재시작
docker-compose restart
```

### 8.2 로그 확인
```bash
# 애플리케이션 로그
docker-compose logs -f app

# 특정 시간 범위 로그
docker-compose logs --since "2024-01-01" --until "2024-01-02" app
```

### 8.3 스케일링
```bash
# 애플리케이션 인스턴스 증가
docker-compose up -d --scale app=3
```

## 9. 문제 해결

### 9.1 일반적인 문제
- **API 키 오류**: .env 파일의 API 키 확인
- **데이터베이스 연결 실패**: PostgreSQL 컨테이너 상태 및 자격 증명 확인
- **슬랙 알림 실패**: Webhook URL 및 네트워크 연결 확인

### 9.2 디버깅 명령어
```bash
# 컨테이너 내부 접속
docker exec -it poker-trend-app bash

# Python 셸 실행
docker exec -it poker-trend-app python

# 데이터베이스 쿼리 실행
docker exec -it poker-trend-db psql -U poker_user -d poker_trend -c "SELECT * FROM reports ORDER BY created_at DESC LIMIT 5;"
```

## 10. 업데이트 절차

### 10.1 무중단 배포
```bash
# 1. 새 이미지 빌드
docker-compose build app

# 2. 새 컨테이너로 교체
docker-compose up -d --no-deps app

# 3. 헬스체크 확인
./scripts/healthcheck.sh

# 4. 이전 컨테이너 정리
docker system prune -f
```

### 10.2 데이터베이스 마이그레이션
```bash
# 마이그레이션 실행
docker exec -it poker-trend-app alembic upgrade head
```