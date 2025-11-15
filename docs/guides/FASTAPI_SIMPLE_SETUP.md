# 🌊 FastAPI 디지털오션 심플 가이드 (초보자용)

**작성일**: 2025-11-15  
**대상**: FastAPI 처음 배우는 학생들  
**목표**: 최소한의 복잡성으로 안전한 FastAPI 서버 구축  
**특징**: 코덱스 실무 표준 + 단계적 학습

---

## 🎯 **학습 철학**

### 💡 단계별 접근법
1. **1단계**: 기본 FastAPI 서버 (최소 의존성)
2. **2단계**: systemd 서비스 (실무 표준)
3. **3단계**: 스크립트 자동화 (선택사항)
4. **4단계**: 모니터링 도구 (고급 사용자)

### ⚠️ **보안 우선 원칙**
- ❌ **HTTP 재시작 API 금지** (보안 위험)
- ✅ **systemd 서비스 우선** (안전한 관리)
- ✅ **전용 사용자 분리** (권한 최소화)
- ✅ **로그 파일 관리** (운영 투명성)

---

## 🚀 1단계: 기본 FastAPI 서버 (15분)

### 1-1. 서버 초기 설정

```bash
# 서버 접속
ssh root@your-server-ip

# 기본 패키지 설치
apt update && apt upgrade -y
apt install -y git htop tmux curl
apt install -y python3.11 python3.11-venv python3-pip

# 보안 설정
adduser deploy
usermod -aG sudo deploy
timedatectl set-timezone Asia/Seoul

# 방화벽 (포트 9000 사용)
ufw allow ssh && ufw allow 9000 && ufw enable

# 사용자 전환
su - deploy
```

### 1-2. 최소 FastAPI 앱

```bash
# 실무 표준 경로
sudo mkdir -p /opt/fastapi
sudo chown deploy:deploy /opt/fastapi
cd /opt/fastapi

# 가상환경 (최소 의존성)
python3.11 -m venv venv
source venv/bin/activate

# FastAPI 핵심만 설치
pip install fastapi uvicorn[standard] python-dotenv
pip freeze > requirements.txt
```

**main.py (초보자용 - 18줄):**
```python
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="메신저봇 FastAPI 서버")

@app.get("/")
async def root():
    return {"message": "FastAPI 서버 정상 동작", "time": datetime.now()}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/echo") 
async def echo(data: dict):
    return {"echo": data, "received_at": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

### 1-3. 첫 테스트

```bash
# 개발 서버 실행
python main.py

# 새 터미널에서 테스트
curl http://localhost:9000/health
curl -X POST http://localhost:9000/api/echo -H "Content-Type: application/json" -d '{"test": "hello"}'
```

✅ **1단계 완료**: 기본 FastAPI 서버가 동작합니다!

---

## 🔧 2단계: systemd 서비스 (실무 표준)

### 2-1. 서비스 파일 생성

```bash
sudo tee /etc/systemd/system/fastapi.service << 'EOF'
[Unit]
Description=FastAPI MessengerBot Server
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/fastapi
Environment="PATH=/opt/fastapi/venv/bin"
ExecStart=/opt/fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 2-2. 서비스 시작

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# 상태 확인
sudo systemctl status fastapi
```

### 2-3. 서비스 관리 명령어

| 작업 | 명령어 |
|------|--------|
| 상태 확인 | `sudo systemctl status fastapi` |
| 재시작 | `sudo systemctl restart fastapi` |
| 로그 확인 | `sudo journalctl -u fastapi -f` |
| 중지 | `sudo systemctl stop fastapi` |
| 시작 | `sudo systemctl start fastapi` |

✅ **2단계 완료**: 서버가 자동으로 관리됩니다!

---

## ⚡ 3단계: 스크립트 자동화 (선택사항)

### 3-1. 관리 스크립트

**scripts/status.sh:**
```bash
#!/bin/bash
echo "📊 FastAPI 서버 상태"
echo "=================="

# 서비스 상태
if systemctl is-active --quiet fastapi; then
    echo "✅ systemd 서비스: 실행중"
else
    echo "❌ systemd 서비스: 중지됨"
fi

# 포트 확인  
if netstat -tuln | grep ":9000" > /dev/null; then
    echo "✅ 포트 9000: 열림"
else
    echo "❌ 포트 9000: 닫힘" 
fi

# 응답 확인
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ HTTP 응답: 정상"
    echo "🌐 서버: http://$(curl -s ifconfig.me):9000"
else
    echo "❌ HTTP 응답: 실패"
fi

echo ""
echo "📋 관리 명령어:"
echo "  sudo systemctl status fastapi    # 상태 확인"
echo "  sudo systemctl restart fastapi   # 재시작"
echo "  sudo journalctl -u fastapi -f    # 로그 확인"
```

**scripts/deploy.sh (코드 업데이트용):**
```bash
#!/bin/bash
set -e

echo "🚀 FastAPI 배포 시작"

cd /opt/fastapi

# 코드 백업
if [ -f main.py ]; then
    cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)
fi

# 서비스 중지
sudo systemctl stop fastapi

# 의존성 업데이트 (requirements.txt 변경된 경우)
if [ -f requirements.txt ]; then
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 서비스 재시작  
sudo systemctl start fastapi

# 헬스체크
sleep 3
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ 배포 성공!"
else
    echo "❌ 배포 실패 - 백업 파일 확인 필요"
fi
```

### 3-2. 별칭 설정

```bash
# ~/.bashrc에 추가
echo "
# FastAPI 관리 별칭  
alias fapi-status='/opt/fastapi/scripts/status.sh'
alias fapi-restart='sudo systemctl restart fastapi'
alias fapi-logs='sudo journalctl -u fastapi -f --lines 20'
alias fapi-deploy='/opt/fastapi/scripts/deploy.sh'
" >> ~/.bashrc

source ~/.bashrc
chmod +x /opt/fastapi/scripts/*.sh
```

✅ **3단계 완료**: 스크립트로 간편 관리 가능!

---

## 📊 4단계: 로그 및 모니터링 (고급)

### 4-1. 로그 파일 분리

**main.py 로깅 추가 (선택사항):**
```python
import logging
from pathlib import Path

# 로그 디렉터리 생성
Path("logs").mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.post("/api/echo") 
async def echo(data: dict):
    logger.info(f"Echo request: {data}")
    return {"echo": data, "received_at": datetime.now()}
```

### 4-2. 로그 API (안전한 읽기 전용)

```python
@app.get("/logs/recent")
async def get_logs(lines: int = 20):
    """로그 조회 - 읽기 전용 (안전함)"""
    try:
        log_file = Path("logs/app.log")
        if not log_file.exists():
            return {"logs": [], "message": "로그 파일 없음"}
            
        content = log_file.read_text(encoding="utf-8").splitlines()
        return {"logs": content[-lines:], "total_lines": len(content)}
    except Exception as e:
        return {"error": str(e)}
```

### 4-3. 모니터링 명령어

```bash
# 실시간 로그 모니터링
sudo journalctl -u fastapi -f

# 시스템 리소스 확인
htop

# 디스크 사용량
df -h

# 서비스 상태 요약
systemctl status fastapi --no-pager
```

✅ **4단계 완료**: 운영급 모니터링 환경 구축!

---

## 🔒 보안 체크리스트

### ❌ **절대 하지 말 것**
- [ ] ~~HTTP로 서버 재시작 API~~ (보안 위험)
- [ ] ~~root 계정으로 서비스 실행~~ (권한 과부여)  
- [ ] ~~외부에 내부 로그 노출~~ (정보 누출)
- [ ] ~~인증 없는 관리 API~~ (무단 접근)

### ✅ **반드시 할 것**
- [x] systemd 서비스 사용 (안전한 관리)
- [x] 전용 deploy 사용자 (권한 분리)
- [x] 방화벽 필수 포트만 오픈 (접근 제한)
- [x] 로그 파일 권한 관리 (정보 보호)

---

## 🎯 **메신저봇 연동 예시**

**메신저봇 코드:**
```javascript
// 메신저봇에서 FastAPI 서버 호출
var API_URL = "http://your-server-ip:9000/api/echo";

function onMessage(msg) {
    if (msg.content === "!서버테스트") {
        try {
            var response = org.jsoup.Jsoup.connect(API_URL)
                .header("Content-Type", "application/json")
                .requestBody(JSON.stringify({
                    message: "메신저봇 테스트",
                    room: msg.room,
                    sender: msg.author.name
                }))
                .ignoreContentType(true)
                .timeout(10000)
                .method(org.jsoup.Connection.Method.POST)
                .execute();
                
            var result = JSON.parse(response.body());
            msg.reply("✅ 서버 연결 성공!\n받은 데이터: " + JSON.stringify(result.echo));
            
        } catch (e) {
            msg.reply("❌ 서버 연결 실패: " + e.message);
        }
    }
}
```

---

## 📋 **AI 도구별 사용법**

### 🤖 **Claude Code 사용자**
```bash
# SSH 접속 후
fapi-status          # 상태 확인
fapi-restart         # 재시작  
fapi-logs            # 로그 확인
fapi-deploy          # 배포
```

### 🎯 **Codex 사용자**  
```bash
# 동일한 명령어 실행
sudo systemctl status fastapi
sudo systemctl restart fastapi
sudo journalctl -u fastapi -f
/opt/fastapi/scripts/deploy.sh
```

---

## ✅ **완료 체크리스트**

### 🔧 **기본 설정**
- [ ] 서버 생성 및 접속
- [ ] deploy 사용자 생성
- [ ] Python 3.11 설치
- [ ] 방화벽 설정 (포트 9000)

### 📂 **FastAPI 설정**
- [ ] /opt/fastapi 디렉터리 생성
- [ ] 가상환경 생성 및 FastAPI 설치
- [ ] main.py 작성 (18줄 버전)
- [ ] 로컬 테스트 성공

### 🚀 **서비스 설정**
- [ ] systemd 서비스 파일 생성
- [ ] 서비스 등록 및 시작
- [ ] 서비스 상태 정상 확인
- [ ] 외부 접속 테스트

### 📊 **관리 도구 (선택)**
- [ ] 관리 스크립트 작성
- [ ] 별칭 설정
- [ ] 로그 시스템 구성
- [ ] 메신저봇 연동 테스트

---

## 🆘 **문제 해결**

### **1. 서비스 시작 실패**
```bash
# 로그 확인
sudo journalctl -u fastapi --no-pager

# 권한 확인
ls -la /opt/fastapi/
sudo chown -R deploy:deploy /opt/fastapi/

# 수동 테스트
cd /opt/fastapi && source venv/bin/activate && python main.py
```

### **2. 포트 접근 안됨**
```bash
# 방화벽 확인
sudo ufw status

# 포트 사용 확인
sudo netstat -tuln | grep 9000

# 외부 IP 확인
curl ifconfig.me
```

### **3. 의존성 문제**
```bash
# 가상환경 재생성
rm -rf /opt/fastapi/venv
cd /opt/fastapi
python3.11 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard]
```

---

**📝 최종 수정**: 2025-11-15  
**👨‍💻 작성자**: 코덱스 비평 반영한 개선판  
**🎯 특징**: 단순함 + 보안 + 실무표준 = 완벽한 학습 가이드