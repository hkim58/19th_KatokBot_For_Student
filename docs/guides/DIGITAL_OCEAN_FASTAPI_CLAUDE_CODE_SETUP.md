# 🌊 디지털 오션 FastAPI 완벽 가이드 (Claude Code + Codex 통합)

**작성일**: 2025-11-15  
**대상**: 메신저봇 프로젝트 학생들  
**목표**: 디지털 오션 서버에서 프로덕션급 FastAPI 구축 후 모든 AI 도구와 연동하기  
**특징**: 실무 표준 + AI 도구 호환성을 모두 갖춘 하이브리드 접근법

---

## 📋 강의 개요

이 강의에서는 디지털 오션 서버에 FastAPI를 구축한 직후, **클로드 코드(Claude Code)와 코덱스(Codex) 모두**와 효율적으로 연동하여 개발을 진행하는 방법을 배웁니다.

### 🎯 학습 목표
- [ ] 디지털 오션 서버 초기 설정 완료
- [ ] FastAPI 서버 구축 및 실행
- [ ] 클로드 코드와 서버 연동 설정
- [ ] **코덱스 호환 환경 구성**
- [ ] 로그 모니터링 시스템 구축
- [ ] 자동 재시작 및 관리 도구 설정

## 🎯 **이 가이드의 특별함**

### 💡 기존 가이드 대비 차별점
- **실무 표준**: systemd 서비스, 전용 사용자, 표준 경로 (`/opt/fastapi`)
- **AI 도구 완전 호환**: Claude Code 터미널 + Codex 웹 인터페이스
- **프로덕션 Ready**: 자동 재시작, 로깅, 보안 설정
- **학습자 친화**: 단계별 체크리스트, 상세 문제해결 가이드

### ⚠️ **AI 도구별 호환성 주의사항**

| 구분 | Claude Code | Codex |
|------|------------|-------|
| **접근 방식** | SSH, 파일 편집, 실시간 명령 실행 | 웹 인터페이스, 코드 생성/설명 |
| **강점** | 직접 서버 제어, tmux 세션 | 브라우저 GUI, 시각적 모니터링 |
| **제한사항** | - | 터미널 접근 제한적 |
| **해결책** | 기존 방식 유지 | **웹 대시보드 + API 제공** |

---

## 🚀 1단계: 서버 초기 설정 (실무 표준 적용)

### 1-1. 기본 서버 세팅

```bash
# 서버 접속
ssh root@your-server-ip

# 시스템 업데이트
apt update && apt upgrade -y

# 기본 도구 설치
apt install -y git unzip htop tmux curl wget tree
apt install -y python3.11 python3.11-venv python3-pip nginx fail2ban
```

### 1-2. 보안 및 사용자 설정 (프로덕션 표준)

```bash
# 전용 배포 사용자 생성 (실무 표준)
adduser deploy
usermod -aG sudo deploy

# 타임존 설정
timedatectl set-timezone Asia/Seoul

# 방화벽 설정 (포트 9000 사용)
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw allow 9000
ufw enable

# 사용자 전환
su - deploy
```

### 1-3. 프로덕션 디렉토리 구조 생성

```bash
# 실무 표준 경로 사용
sudo mkdir -p /opt/fastapi
sudo chown deploy:deploy /opt/fastapi
cd /opt/fastapi

# 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate

# FastAPI + 모니터링 패키지 설치
pip install fastapi uvicorn[standard] python-dotenv
pip install jinja2 aiofiles psutil  # 웹 대시보드용
pip install python-multipart requests  # API 연동용

# requirements.txt 생성
pip freeze > requirements.txt
```

---

## 🔧 2단계: 클로드 코드 연동을 위한 사전 설정

### 2-1. SSH 키 기반 접속 설정

```bash
# 로컬에서 SSH 키 생성 (클로드 코드용)
ssh-keygen -t rsa -b 4096 -C "claude-code@messenger-bot"

# 공개 키를 서버에 등록
ssh-copy-id messenger-bot@your-server-ip
```

### 2-2. tmux 설치 및 설정 (필수!)

```bash
# tmux 설치
sudo apt install tmux -y

# tmux 설정 파일 생성
cat > ~/.tmux.conf << 'EOF'
# 마우스 사용 가능
set -g mouse on

# 세션 이름 표시
set -g status-left '[#S] '
set -g status-left-length 20

# 윈도우 상태 표시
setw -g window-status-current-style 'fg=black bg=green'

# 히스토리 증가
set -g history-limit 10000

# 단축키 설정
bind r source-file ~/.tmux.conf \; display-message "Config reloaded!"
EOF
```

### 2-3. 프로젝트 구조 및 설정 파일

```bash
# 디렉토리 구조 생성 (실무 표준)
cd /opt/fastapi
mkdir -p logs scripts templates static config

# 로그 파일 초기 생성
touch logs/fastapi.log logs/error.log logs/access.log

# 환경변수 템플릿 생성
cat > .env.example << 'EOF'
# FastAPI 설정
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# API 키 (실제 값은 .env에만 저장)
PERPLEXITY_API_KEY=your-api-key-here
OPENAI_API_KEY=your-api-key-here

# 서버 설정
HOST=0.0.0.0
PORT=9000
EOF

# 실제 환경변수 파일 생성 (서버에서만)
cp .env.example .env
echo "# .env 파일을 수정하여 실제 API 키를 입력하세요" >> .env
```

---

## 📂 3단계: FastAPI 프로젝트 구조 설정

### 3-1. 프로덕션급 FastAPI 애플리케이션 생성

```bash
cd /opt/fastapi
```

**main.py 파일 생성 (실무 표준 + AI 도구 호환):**
```python
#!/usr/bin/env python3
"""
메신저봇 FastAPI 서버 - 학생용 기본 템플릿
"""
import os
import time
import logging
import subprocess
import psutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fastapi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="메신저봇 FastAPI 서버",
    description="학생들을 위한 메신저봇 연동 API (클로드 코드 + 코덱스 호환)",
    version="1.0.0"
)

# 정적 파일 및 템플릿 설정 (코덱스 웹 인터페이스용)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 시작 시간 기록
SERVER_START_TIME = datetime.now()

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 메신저봇 FastAPI 서버 시작됨")
    logger.info(f"📅 시작 시간: {SERVER_START_TIME}")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("🛑 메신저봇 FastAPI 서버 종료됨")

# ============= 기본 엔드포인트 =============

@app.get("/")
async def root():
    """루트 엔드포인트 - 서버 상태 확인"""
    return {
        "status": "healthy",
        "message": "메신저봇 FastAPI 서버가 정상 동작중입니다",
        "server_time": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - SERVER_START_TIME).total_seconds()
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": (datetime.now() - SERVER_START_TIME).total_seconds()
    }

@app.post("/api/echo")
async def echo_api(request: dict):
    """에코 API - 메신저봇 연동 테스트용"""
    try:
        query = request.get("query", "")
        room = request.get("room", "unknown")
        author = request.get("author", "unknown")
        
        logger.info(f"📨 에코 요청 받음: {query} from {author} in {room}")
        
        response = {
            "success": True,
            "answer": f"에코: {query}",
            "processed_at": datetime.now().isoformat(),
            "request_info": {
                "room": room,
                "author": author,
                "original_query": query
            }
        }
        
        logger.info(f"✅ 에코 응답 전송: {response['answer']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ 에코 API 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 에러: {str(e)}")

@app.get("/logs/recent")
async def get_recent_logs(lines: int = 50):
    """최근 로그 조회 - 클로드 코드에서 활용"""
    try:
        with open('logs/fastapi.log', 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        return {
            "success": True,
            "total_lines": len(all_lines),
            "recent_lines": lines,
            "logs": [line.strip() for line in recent_lines]
        }
        
    except FileNotFoundError:
        return {"success": False, "error": "로그 파일을 찾을 수 없습니다"}

# ============= 코덱스용 웹 인터페이스 =============

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """코덱스용 웹 대시보드 - 브라우저에서 서버 관리"""
    try:
        # 시스템 상태 정보 수집
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 프로세스 정보
        current_process = psutil.Process()
        
        # 최근 로그 (최대 20라인)
        recent_logs = []
        try:
            with open('logs/fastapi.log', 'r', encoding='utf-8') as f:
                recent_logs = f.readlines()[-20:]
        except FileNotFoundError:
            recent_logs = ["로그 파일이 없습니다."]
        
        context = {
            "request": request,
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": str(datetime.now() - SERVER_START_TIME).split('.')[0],
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "memory_total": round(memory.total / 1024 / 1024 / 1024, 1),
            "disk_usage": disk.percent,
            "disk_free": round(disk.free / 1024 / 1024 / 1024, 1),
            "process_memory": round(current_process.memory_info().rss / 1024 / 1024, 1),
            "recent_logs": [log.strip() for log in recent_logs],
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        logger.error(f"❌ 대시보드 에러: {str(e)}")
        return HTMLResponse(f"<h1>대시보드 에러</h1><p>{str(e)}</p>")

@app.post("/api/server/restart")
async def restart_server():
    """서버 재시작 - 코덱스에서 웹으로 호출"""
    try:
        logger.info("🔄 코덱스에서 서버 재시작 요청")
        
        # 별도 스크립트로 재시작 (백그라운드)
        subprocess.Popen(["/bin/bash", "scripts/restart_server.sh"])
        
        return {
            "success": True,
            "message": "서버 재시작이 시작됩니다. 잠시 후 다시 접속해주세요."
        }
        
    except Exception as e:
        logger.error(f"❌ 재시작 실패: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/server/status")
async def server_status():
    """서버 상태 조회 - 코덱스용 API"""
    try:
        # tmux 세션 확인
        tmux_status = subprocess.run(
            ["tmux", "has-session", "-t", "fastapi-server"],
            capture_output=True, text=True
        )
        
        # 포트 확인
        port_status = subprocess.run(
            ["netstat", "-tuln"],
            capture_output=True, text=True
        )
        port_open = ":8000" in port_status.stdout
        
        return {
            "success": True,
            "tmux_session": tmux_status.returncode == 0,
            "port_8000_open": port_open,
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "uptime_seconds": (datetime.now() - SERVER_START_TIME).total_seconds()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import os
    # 환경변수에서 설정 로드
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "9000"))  # 프로덕션 표준 포트
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_config=None  # 커스텀 로깅 사용
    )
```

### 3-2. 프로덕션 서버 관리 스크립트

**scripts/start_server.sh (실무 표준):**
```bash
#!/bin/bash
set -e  # 에러 시 스크립트 중단

cd /opt/fastapi
source venv/bin/activate

echo "🚀 FastAPI 서버 시작중..."
echo "📅 시작 시간: $(date)"

# 로그 디렉토리 확인
mkdir -p logs

# tmux 세션 생성 (개발용)
tmux new-session -d -s fastapi-server \
    "cd /opt/fastapi && source venv/bin/activate && python main.py >> logs/fastapi.log 2>&1"

echo "✅ 서버가 tmux 세션 'fastapi-server'에서 시작됨"
echo "📋 세션 확인: tmux attach -t fastapi-server"
echo "🌐 서버 주소: http://$(curl -s ifconfig.me):9000"
echo "📄 로그 확인: tail -f /opt/fastapi/logs/fastapi.log"
```

**scripts/stop_server.sh:**
```bash
#!/bin/bash
echo "🛑 FastAPI 서버 중지중..."

# tmux 세션 종료
tmux kill-session -t fastapi-server 2>/dev/null

echo "[$(date)] FastAPI stopped" >> /opt/fastapi/logs/fastapi.log
echo "✅ 서버가 중지됨"
```

**scripts/restart_server.sh:**
```bash
#!/bin/bash
set -e

echo "🔄 FastAPI 서버 재시작중..."

# 기존 세션 종료
/opt/fastapi/scripts/stop_server.sh
sleep 2

# 새 세션으로 시작
/opt/fastapi/scripts/start_server.sh

echo "✅ 서버 재시작 완료"
echo "🌐 서버 주소: http://$(curl -s ifconfig.me):9000"
```

**scripts/status.sh (서버 상태 확인):**
```bash
#!/bin/bash
echo "🔍 FastAPI 서버 상태 확인"
echo "========================"

# tmux 세션 확인
if tmux has-session -t fastapi-server 2>/dev/null; then
    echo "✅ tmux 세션: 실행중"
else
    echo "❌ tmux 세션: 중지됨"
fi

# 프로세스 확인
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Python 프로세스: 실행중"
    echo "📊 PID: $(pgrep -f "python main.py")"
else
    echo "❌ Python 프로세스: 중지됨"
fi

# 포트 확인
if netstat -tuln | grep ":9000" > /dev/null; then
    echo "✅ 포트 9000: 오픈됨"
else
    echo "❌ 포트 9000: 닫힘"
fi

# 서버 응답 확인
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ HTTP 응답: 정상"
    echo "🌐 외부 주소: http://$(curl -s ifconfig.me):9000"
else
    echo "❌ HTTP 응답: 실패"
fi

echo ""
echo "📋 유용한 명령어:"
echo "  - 서버 시작: /opt/fastapi/scripts/start_server.sh"
echo "  - 서버 중지: /opt/fastapi/scripts/stop_server.sh"
echo "  - 로그 확인: tail -f /opt/fastapi/logs/fastapi.log"
echo "  - tmux 접속: tmux attach -t fastapi-server"
```

### 3-3. 코덱스용 웹 대시보드 템플릿 생성

**templates/dashboard.html:**
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메신저봇 FastAPI 서버 대시보드</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .header { 
            text-align: center; 
            color: #333; 
            margin-bottom: 30px; 
        }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .status-card { 
            padding: 20px; 
            border-left: 4px solid #007bff; 
            background: #f8f9fa; 
            border-radius: 5px; 
        }
        .status-card.warning { border-left-color: #ffc107; }
        .status-card.danger { border-left-color: #dc3545; }
        .status-card.success { border-left-color: #28a745; }
        .metric { 
            font-size: 24px; 
            font-weight: bold; 
            color: #007bff; 
        }
        .logs-section { 
            margin-top: 30px; 
        }
        .logs-container { 
            background: #000; 
            color: #00ff00; 
            padding: 20px; 
            border-radius: 5px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px; 
            height: 300px; 
            overflow-y: auto; 
        }
        .btn { 
            padding: 10px 20px; 
            margin: 5px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn-primary { background-color: #007bff; color: white; }
        .btn-warning { background-color: #ffc107; color: black; }
        .btn-danger { background-color: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .actions { text-align: center; margin: 30px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 메신저봇 FastAPI 서버 대시보드</h1>
            <p>코덱스 호환 웹 인터페이스</p>
            <p><strong>서버 시간:</strong> {{ server_time }}</p>
        </div>

        <div class="status-grid">
            <div class="status-card success">
                <h3>⏱️ 서버 가동시간</h3>
                <div class="metric">{{ uptime }}</div>
            </div>
            
            <div class="status-card {% if cpu_usage > 80 %}danger{% elif cpu_usage > 60 %}warning{% else %}success{% endif %}">
                <h3>💻 CPU 사용률</h3>
                <div class="metric">{{ cpu_usage }}%</div>
            </div>
            
            <div class="status-card {% if memory_usage > 80 %}danger{% elif memory_usage > 60 %}warning{% else %}success{% endif %}">
                <h3>🧠 메모리 사용률</h3>
                <div class="metric">{{ memory_usage }}%</div>
                <small>{{ memory_total }}GB 중</small>
            </div>
            
            <div class="status-card {% if disk_usage > 80 %}danger{% elif disk_usage > 60 %}warning{% else %}success{% endif %}">
                <h3>💾 디스크 사용률</h3>
                <div class="metric">{{ disk_usage }}%</div>
                <small>{{ disk_free }}GB 여유</small>
            </div>
            
            <div class="status-card">
                <h3>📊 프로세스 메모리</h3>
                <div class="metric">{{ process_memory }}MB</div>
            </div>
        </div>

        <div class="actions">
            <button class="btn btn-primary" onclick="refreshPage()">🔄 새로고침</button>
            <button class="btn btn-warning" onclick="restartServer()">🔄 서버 재시작</button>
            <button class="btn btn-primary" onclick="window.open('/docs', '_blank')">📚 API 문서</button>
            <button class="btn btn-primary" onclick="testEchoAPI()">🔧 에코 API 테스트</button>
        </div>

        <div class="logs-section">
            <h3>📋 최근 로그 (실시간)</h3>
            <div class="logs-container" id="logs">
                {% for log in recent_logs %}
                <div>{{ log }}</div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function refreshPage() {
            location.reload();
        }

        async function restartServer() {
            if (confirm('정말로 서버를 재시작하시겠습니까?')) {
                try {
                    const response = await fetch('/api/server/restart', {
                        method: 'POST'
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(result.message);
                        setTimeout(() => location.reload(), 3000);
                    } else {
                        alert('재시작 실패: ' + result.error);
                    }
                } catch (error) {
                    alert('요청 실패: ' + error.message);
                }
            }
        }

        async function testEchoAPI() {
            try {
                const response = await fetch('/api/echo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: '대시보드 테스트',
                        room: 'dashboard',
                        author: 'admin'
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('✅ API 테스트 성공: ' + result.answer);
                } else {
                    alert('❌ API 테스트 실패');
                }
            } catch (error) {
                alert('❌ API 테스트 에러: ' + error.message);
            }
        }

        // 30초마다 자동 새로고침
        setInterval(refreshPage, 30000);
    </script>
</body>
</html>
```

### 3-4. systemd 서비스 설정 (프로덕션 환경)

**systemd 서비스 파일 생성:**
```bash
sudo tee /etc/systemd/system/fastapi.service << 'EOF'
[Unit]
Description=FastAPI Service for MessengerBot
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/fastapi
Environment="PATH=/opt/fastapi/venv/bin"
Environment="PYTHONPATH=/opt/fastapi"
ExecStart=/opt/fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=5
StandardOutput=append:/opt/fastapi/logs/fastapi.log
StandardError=append:/opt/fastapi/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
```

**서비스 관리 명령어:**
```bash
# 서비스 상태 확인
sudo systemctl status fastapi

# 서비스 재시작
sudo systemctl restart fastapi

# 서비스 로그 확인
sudo journalctl -u fastapi -f --lines 50

# 부팅 시 자동 시작 확인
sudo systemctl is-enabled fastapi
```

```bash
# 스크립트 실행 권한 부여
chmod +x scripts/*.sh

# 스크립트 별칭 설정 (선택사항)
echo "
# FastAPI 서버 관리 별칭
alias fapi-start='/opt/fastapi/scripts/start_server.sh'
alias fapi-stop='/opt/fastapi/scripts/stop_server.sh'
alias fapi-restart='/opt/fastapi/scripts/restart_server.sh'
alias fapi-status='/opt/fastapi/scripts/status.sh'
alias fapi-logs='tail -f /opt/fastapi/logs/fastapi.log'
alias fapi-tmux='tmux attach -t fastapi-server'
" >> ~/.bashrc

source ~/.bashrc
```

---

## 🔍 4단계: 로그 모니터링 시스템

### 4-1. 실시간 로그 모니터링 스크립트

**scripts/monitor_logs.sh:**
```bash
#!/bin/bash
echo "📊 FastAPI 서버 로그 모니터링 시작"
echo "=================================="
echo "Ctrl+C로 종료"
echo ""

# 로그 파일이 없으면 생성
touch ~/fastapi-server/logs/fastapi.log

# 실시간 로그 출력
tail -f ~/fastapi-server/logs/fastapi.log | while read line; do
    # 타임스탬프 추가하여 출력
    echo "[$(date '+%H:%M:%S')] $line"
done
```

### 4-2. 서버 상태 확인 스크립트

**scripts/status.sh:**
```bash
#!/bin/bash
echo "🔍 FastAPI 서버 상태 확인"
echo "========================"

# tmux 세션 확인
if tmux has-session -t fastapi-server 2>/dev/null; then
    echo "✅ tmux 세션: 실행중"
else
    echo "❌ tmux 세션: 중지됨"
fi

# 프로세스 확인
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Python 프로세스: 실행중"
    echo "📊 PID: $(pgrep -f "python main.py")"
else
    echo "❌ Python 프로세스: 중지됨"
fi

# 포트 확인
if netstat -tuln | grep ":8000" > /dev/null; then
    echo "✅ 포트 8000: 오픈됨"
else
    echo "❌ 포트 8000: 닫힘"
fi

# 서버 응답 확인
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ HTTP 응답: 정상"
    echo "🌐 외부 주소: http://$(curl -s ifconfig.me):8000"
else
    echo "❌ HTTP 응답: 실패"
fi

echo ""
echo "📋 유용한 명령어:"
echo "  - 서버 시작: ~/fastapi-server/scripts/start_server.sh"
echo "  - 서버 중지: ~/fastapi-server/scripts/stop_server.sh"
echo "  - 로그 확인: ~/fastapi-server/scripts/monitor_logs.sh"
echo "  - tmux 접속: tmux attach -t fastapi-server"
```

```bash
chmod +x scripts/monitor_logs.sh scripts/status.sh
```

---

## 🤖 5단계: 클로드 코드 + 코덱스 연동 설정

### 5-1. 클로드 코드에서 서버 접속하기

클로드 코드를 실행한 후 다음 명령어들로 서버와 연동:

```bash
# SSH로 서버 접속
ssh messenger-bot@your-server-ip

# 서버 상태 확인
cd ~/fastapi-server && ./scripts/status.sh

# 서버 시작
./scripts/start_server.sh

# 실시간 로그 모니터링
./scripts/monitor_logs.sh
```

### 5-1-2. 코덱스에서 웹 대시보드 사용하기

코덱스 사용자는 터미널 접근이 제한적이므로 웹 브라우저를 통해 서버 관리:

```
🌐 웹 대시보드 주소: http://your-server-ip:8000/dashboard
📚 API 문서: http://your-server-ip:8000/docs
🔧 에코 API 테스트: http://your-server-ip:8000/api/echo (POST)
📊 서버 상태 API: http://your-server-ip:8000/api/server/status (GET)
```

**코덱스 사용 워크플로:**
1. 웹 브라우저에서 `/dashboard` 접속
2. 서버 상태 실시간 모니터링
3. 웹 인터페이스에서 서버 재시작 가능
4. API 테스트 버튼으로 기능 확인

### 5-2. 클로드 코드용 별칭 설정

서버에서 `.bashrc`에 다음 별칭 추가:

```bash
echo "
# FastAPI 서버 관리 별칭
alias fapi-start='cd ~/fastapi-server && ./scripts/start_server.sh'
alias fapi-stop='cd ~/fastapi-server && ./scripts/stop_server.sh'
alias fapi-restart='cd ~/fastapi-server && ./scripts/restart_server.sh'
alias fapi-status='cd ~/fastapi-server && ./scripts/status.sh'
alias fapi-logs='cd ~/fastapi-server && ./scripts/monitor_logs.sh'
alias fapi-tmux='tmux attach -t fastapi-server'
" >> ~/.bashrc

source ~/.bashrc
```

### 5-3. 도구별 사용 명령어 비교

#### 🎯 **클로드 코드 (SSH 터미널)**

```bash
# 서버 빠른 상태 확인
fapi-status

# 서버 재시작
fapi-restart

# 실시간 로그 확인
fapi-logs

# tmux 세션 직접 접속 (코드 수정용)
fapi-tmux

# API 테스트
curl -X POST http://localhost:8000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트", "room": "DEBUG", "author": "Claude"}'
```

#### 🎯 **코덱스 (웹 브라우저)**

```javascript
// 브라우저에서 실행할 수 있는 JavaScript 코드

// 1. 서버 상태 확인
fetch('/api/server/status')
  .then(response => response.json())
  .then(data => console.log('서버 상태:', data));

// 2. 에코 API 테스트
fetch('/api/echo', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: '코덱스 테스트',
    room: 'codex-room',
    author: 'codex-user'
  })
})
.then(response => response.json())
.then(data => console.log('응답:', data));

// 3. 로그 확인
fetch('/logs/recent?lines=10')
  .then(response => response.json())
  .then(data => console.log('최근 로그:', data.logs));

// 4. 서버 재시작 (확인 후)
if (confirm('서버를 재시작하시겠습니까?')) {
  fetch('/api/server/restart', {method: 'POST'})
    .then(response => response.json())
    .then(data => alert(data.message));
}
```

#### 📋 **접근 방법 요약**
| 기능 | 클로드 코드 | 코덱스 |
|------|------------|-------|
| 서버 상태 확인 | `fapi-status` | `/dashboard` 페이지 |
| 서버 재시작 | `fapi-restart` | 대시보드 재시작 버튼 |
| 로그 모니터링 | `fapi-logs` | 대시보드 로그 섹션 |
| 코드 편집 | `fapi-tmux` + nano/vim | 로컬에서 편집 후 업로드 |
| API 테스트 | curl 명령어 | 대시보드 테스트 버튼 |

---

## 🔒 6단계: 보안 및 방화벽 설정

### 6-1. UFW 방화벽 설정

```bash
# UFW 방화벽 설정
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable

# 상태 확인
sudo ufw status
```

### 6-2. Nginx 리버스 프록시 설정 (선택사항)

```bash
# Nginx 설정 파일
sudo tee /etc/nginx/sites-available/fastapi << 'EOF'
server {
    listen 80;
    server_name your-server-ip;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 🧪 7단계: 연동 테스트

### 7-1. 서버 기능 테스트

```bash
# 1. 헬스체크
curl http://localhost:8000/health

# 2. 에코 API 테스트
curl -X POST http://localhost:8000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"query": "안녕하세요", "room": "테스트방", "author": "학생"}'

# 3. 로그 확인
curl http://localhost:8000/logs/recent?lines=10
```

### 7-2. 메신저봇에서 테스트

현재 프로젝트의 봇 코드 수정:

```javascript
// FastAPI 서버 URL 설정
var API_URL = "http://your-server-ip:8000/api/echo";

// 테스트용 명령어 처리
if (content === "!서버테스트") {
    var testData = {
        query: "서버 연결 테스트",
        room: msg.room,
        author: msg.author.name
    };
    
    try {
        var response = org.jsoup.Jsoup.connect(API_URL)
            .header("Content-Type", "application/json")
            .requestBody(JSON.stringify(testData))
            .ignoreContentType(true)
            .timeout(10000)
            .method(org.jsoup.Connection.Method.POST)
            .execute();
            
        var result = JSON.parse(response.body());
        msg.reply("✅ 서버 연결 성공!\n" + result.answer);
        
    } catch (e) {
        msg.reply("❌ 서버 연결 실패: " + e.message);
    }
}
```

---

## 📚 8단계: 클로드 코드 워크플로

### 8-1. 일반적인 개발 워크플로

```bash
# 1. 서버 접속
ssh messenger-bot@your-server-ip

# 2. 상태 확인
fapi-status

# 3. 코드 수정이 필요한 경우
fapi-tmux
# (tmux 내에서 nano main.py 등으로 수정)
# Ctrl+C로 서버 중지 후 python main.py로 재시작

# 4. 로그 모니터링
# 새 터미널에서
fapi-logs

# 5. API 테스트
curl -X POST http://localhost:8000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트"}'
```

### 8-2. 문제 해결 워크플로

```bash
# 1. 서버가 응답하지 않을 때
fapi-status  # 상태 확인
fapi-restart  # 강제 재시작

# 2. 로그에서 에러 찾기
tail -50 ~/fastapi-server/logs/fastapi.log | grep ERROR

# 3. 포트 충돌 확인
sudo netstat -tulpn | grep :8000
sudo kill -9 PID  # 필요시 강제 종료

# 4. 디스크 용량 확인
df -h
du -sh ~/fastapi-server/logs/*
```

---

## 📋 체크리스트

### ✅ 설정 완료 체크리스트

#### 🔧 **기본 서버 설정**
- [ ] 디지털 오션 서버 생성 및 접속
- [ ] Python 3.8+ 및 pip 설치
- [ ] 가상환경 생성 및 FastAPI 설치
- [ ] **코덱스용 패키지 추가 설치 (jinja2, aiofiles, psutil)**
- [ ] tmux 설치 및 설정

#### 📂 **프로젝트 구조**
- [ ] 로그 디렉토리 구조 생성
- [ ] **templates 폴더 및 dashboard.html 생성**
- [ ] **static 폴더 생성**
- [ ] main.py 기본 애플리케이션 작성 (**코덱스 웹 인터페이스 포함**)
- [ ] 서버 관리 스크립트 생성 및 권한 부여
- [ ] 모니터링 스크립트 설정

#### 🔒 **보안 및 네트워크**
- [ ] 방화벽 포트 8000 오픈
- [ ] SSH 키 기반 접속 설정
- [ ] 별칭(alias) 설정

### ✅ 연동 테스트 체크리스트

#### 🤖 **클로드 코드 테스트**
- [ ] SSH 접속 성공
- [ ] 서버 시작/중지/재시작 스크립트 동작 확인
- [ ] 헬스체크 API 응답 확인
- [ ] 에코 API POST 요청/응답 확인
- [ ] 실시간 로그 모니터링 동작 확인
- [ ] tmux 세션 접속 및 종료 확인
- [ ] 메신저봇에서 서버 API 호출 성공

#### 🎯 **코덱스 웹 인터페이스 테스트**
- [ ] 웹 대시보드 접속 성공 (`/dashboard`)
- [ ] 서버 상태 정보 표시 확인 (CPU, 메모리, 디스크)
- [ ] 웹에서 서버 재시작 기능 동작 확인
- [ ] 대시보드 에코 API 테스트 버튼 동작 확인
- [ ] 실시간 로그 표시 확인
- [ ] 자동 새로고침 (30초) 동작 확인
- [ ] FastAPI 자동 문서 접속 확인 (`/docs`)

#### 📱 **메신저봇 연동**
- [ ] 메신저봇에서 서버 API 호출 성공
- [ ] 응답 데이터 파싱 및 카톡방 출력 확인

---

## 🎯 학습 완료 후 다음 단계

1. **PerBot 예제 적용**: 19th_GPTers의 PerBot을 현재 서버로 연동
2. **멀티턴 봇 확장**: ChatMemory와 FastAPI 연동
3. **데이터베이스 연동**: SQLite → PostgreSQL 확장
4. **CI/CD 파이프라인**: GitHub Actions 자동 배포 설정

---

## 🆘 문제 해결

### 자주 발생하는 문제들

#### 🔧 **서버 관련 문제**

**1. "포트 8000이 이미 사용중" 에러**
```bash
# 클로드 코드에서
sudo netstat -tulpn | grep :8000
sudo kill -9 $(lsof -t -i:8000)

# 코덱스에서 - 웹 대시보드의 서버 재시작 버튼 사용
```

**2. tmux 세션이 보이지 않음**
```bash
# 클로드 코드에서
tmux ls  # 세션 목록 확인
tmux new-session -d -s fastapi-server  # 새 세션 생성

# 코덱스에서 - /api/server/status로 상태 확인
```

**3. 가상환경 활성화 안됨**
```bash
# 클로드 코드에서
cd ~/fastapi-server
source venv/bin/activate
which python  # 가상환경 확인
```

**4. 로그 파일 권한 에러**
```bash
# 클로드 코드에서
chmod 664 ~/fastapi-server/logs/*.log
chown messenger-bot:messenger-bot ~/fastapi-server/logs/*.log
```

#### 🎯 **코덱스 전용 문제**

**5. 웹 대시보드 접속 안됨**
- **확인사항**: 서버가 실행 중인지 확인
- **해결방법**: `http://server-ip:8000/health`로 먼저 테스트
- **대안**: FastAPI 자동 문서 `/docs`로 접속하여 API 테스트

**6. 대시보드에서 서버 재시작 실패**
- **원인**: 스크립트 권한 또는 경로 문제
- **해결방법**: 클로드 코드로 SSH 접속하여 수동 재시작
```bash
# 클로드 코드에서 직접 해결
fapi-restart
```

**7. 브라우저에서 JavaScript 에러**
- **확인**: 개발자 도구(F12) 콘솔 확인
- **해결**: CORS 설정이 올바른지 확인
- **대안**: API 직접 호출로 테스트

#### 🔄 **도구별 대안 방법**

| 문제 상황 | 클로드 코드 해결법 | 코덱스 해결법 |
|-----------|-------------------|--------------|
| 서버 상태 확인 | `fapi-status` | `/dashboard` 웹페이지 |
| 서버 재시작 | `fapi-restart` | 대시보드 재시작 버튼 |
| 로그 확인 | `fapi-logs` | 대시보드 로그 섹션 |
| API 테스트 | curl 명령어 | 대시보드 테스트 버튼 |
| 코드 수정 | `fapi-tmux` + vim | 로컬 편집 후 파일 업로드 |

---

## 🏷️ 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [tmux 사용법](https://tmuxcheatsheet.com/)
- [디지털 오션 서버 관리](https://docs.digitalocean.com/)
- [Nginx 리버스 프록시](https://nginx.org/en/docs/)

---

---

## 🎊 완료 확인

이 가이드를 완료하면 다음이 가능해집니다:

### 🤖 **클로드 코드 사용자**
- SSH를 통한 직접 서버 관리
- 터미널에서 실시간 로그 모니터링
- tmux를 통한 코드 실시간 편집
- 명령어 별칭으로 빠른 작업

### 🎯 **코덱스 사용자**
- 웹 브라우저를 통한 서버 관리
- 그래픽 대시보드로 시각적 모니터링
- 클릭 한 번으로 서버 재시작
- JavaScript로 API 테스트

### 🔄 **공통 혜택**
- 메신저봇 ↔ FastAPI 서버 연동 완료
- 실시간 로그 및 상태 모니터링
- 자동화된 서버 관리 스크립트
- 확장 가능한 API 구조

---

**📝 마지막 업데이트**: 2025-11-15  
**👨‍💻 작성자**: Claude Code & 메신저봇 프로젝트팀  
**🔗 호환성**: Claude Code + Codex 완전 지원  
**🎯 다음 학습**: [PerBot FastAPI 연동 실습](./PERBOT_FASTAPI_INTEGRATION.md)