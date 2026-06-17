# Routine AI

AI 기반 루틴 관리 앱. 자연어로 루틴을 추가/삭제하고, 알림을 받아 매일 꾸준히 실천할 수 있도록 도와줍니다.

## 기능

- **AI 채팅**: 자연어로 루틴 추가/삭제 (예: "매일 아침 7시에 운동 30분 추가해줘")
- **오늘 루틴**: 오늘의 루틴 목록 확인 및 완료/건너뜀 처리
- **스트릭**: 연속 완료 일수 추적
- **푸시 알림**: 루틴 시간에 맞춰 동기부여 알림 전송
- **루틴 관리**: 등록된 루틴 목록 조회 및 삭제

## 기술 스택

**Backend**
- FastAPI + uvicorn
- SQLite (aiosqlite)
- Groq API (llama-3.3-70b-versatile)
- APScheduler (푸시 알림 스케줄링)
- Web Push (pywebpush)

**Frontend**
- Next.js 16 + TypeScript
- Tailwind CSS
- Service Worker (푸시 알림 수신)

## 로컬 실행

### 사전 준비

`backend/.env` 파일 생성:
```env
GROQ_API_KEY=gsk_...
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_CLAIMS_EMAIL=mailto:your@email.com
```

`frontend/.env.local` 파일 생성:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:3000` 접속

### Docker Compose

```bash
docker-compose up
```

## 배포

- **Backend**: Railway (`routine-ai/backend` 디렉토리)
- **Frontend**: Vercel (`routine-ai/frontend` 디렉토리)

### 필요한 환경변수

| 서비스 | 변수 | 설명 |
|--------|------|------|
| Backend | `GROQ_API_KEY` | Groq API 키 |
| Backend | `VAPID_PUBLIC_KEY` | Web Push 공개키 |
| Backend | `VAPID_PRIVATE_KEY` | Web Push 비밀키 |
| Backend | `VAPID_CLAIMS_EMAIL` | Web Push 연락처 이메일 |
| Backend | `CORS_ORIGINS` | 허용할 프론트엔드 URL |
| Frontend | `NEXT_PUBLIC_API_URL` | 백엔드 URL |
