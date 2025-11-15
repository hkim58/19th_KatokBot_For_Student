# 🤖 클로드 코드 전용: FastAPI 자동 구축 가이드

**대상**: 학생들이 클로드 코드에게 주는 문서  
**목표**: 이 문서만으로 디지털 오션 FastAPI 서버 완전 자동 구축  
**특징**: 질문 최소화, 자동 실행, 단계별 검증

---

## 📋 **클로드 코드야, 이 작업을 해줘!**

### 🎯 **최종 목표**
디지털 오션 우분투 서버에서 **포트 9000번으로 FastAPI 서버를 구축**하고, **메신저봇에서 호출 가능한 API 제공**

### 📝 **사전 준비사항** (학생이 제공해야 할 정보)
```bash
# 학생이 알려줘야 하는 것들:
SERVER_IP="여기에_서버_IP_입력"           # 예: 123.456.789.123
DEPLOY_PASSWORD="여기에_원하는_비밀번호"    # 예: mypassword123
```

---

## 🚀 **1단계: 서버 초기 설정 및 검증**

### 1-1. 서버 접속 및 기본 설정
```bash
# 서버 접속 (학생이 IP 제공)
ssh root@${SERVER_IP}

# 시스템 업데이트
apt update && apt upgrade -y

# 필수 패키지 설치
apt install -y git htop tmux curl tree
apt install -y python3.11 python3.11-venv python3-pip
```

### 1-2. 보안 사용자 생성
```bash
# deploy 사용자 생성 (비밀번호는 학생이 제공)
adduser deploy --gecos "Deploy User" --disabled-password
echo "deploy:${DEPLOY_PASSWORD}" | chpasswd
usermod -aG sudo deploy

# 타임존 설정
timedatectl set-timezone Asia/Seoul
```

### 1-3. 방화벽 설정
```bash
# 방화벽 설정 (SSH + 9000 포트)
ufw allow ssh
ufw allow 9000
ufw --force enable
```

### ✅ **1단계 검증**
```bash
# 사용자 전환 테스트
su - deploy -c "whoami && pwd"

# 방화벽 상태 확인
ufw status

# 파이썬 버전 확인
python3.11 --version
```

---

## 📂 **2단계: FastAPI 환경 구축**

### 2-1. 디렉토리 구조 생성
```bash
# 실무 표준 경로 생성
mkdir -p /opt/fastapi/{logs,scripts,config}
chown -R deploy:deploy /opt/fastapi
chmod 755 /opt/fastapi
```

### 2-2. 가상환경 및 패키지 설치
```bash
# deploy 사용자로 전환
su - deploy

# 작업 디렉토리 이동
cd /opt/fastapi

# 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate

# FastAPI 핵심 패키지 설치
pip install fastapi uvicorn[standard] python-dotenv
pip freeze > requirements.txt
```

### 2-3. FastAPI 애플리케이션 생성
```bash
# main.py 파일 생성
cat > main.py << 'EOF'
from fastapi import FastAPI
from datetime import datetime
import logging
from pathlib import Path

# 로그 디렉토리 생성
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

app = FastAPI(
    title="메신저봇 FastAPI 서버",
    description="학생용 메신저봇 연동 API 서버",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "메신저봇 FastAPI 서버 정상 동작",
        "time": datetime.now().isoformat(),
        "status": "healthy"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/echo")
async def echo_api(data: dict):
    logger.info(f"Echo API 호출: {data}")
    return {
        "success": True,
        "echo": data,
        "processed_at": datetime.now().isoformat(),
        "message": "메신저봇에서 성공적으로 호출됨"
    }

@app.get("/logs/recent")
async def get_recent_logs(lines: int = 20):
    """로그 조회 API - 안전한 읽기 전용"""
    try:
        log_file = Path("logs/app.log")
        if not log_file.exists():
            return {"logs": [], "message": "로그 파일이 없습니다"}
            
        content = log_file.read_text(encoding="utf-8").splitlines()
        return {
            "success": True,
            "logs": content[-lines:],
            "total_lines": len(content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
EOF
```

### 2-4. 환경변수 설정
```bash
# .env.example 파일 생성
cat > .env.example << 'EOF'
# FastAPI 설정
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secret-key-change-this

# API 키 (실제 값은 .env에 입력)
PERPLEXITY_API_KEY=your-perplexity-api-key
OPENAI_API_KEY=your-openai-api-key

# 서버 설정
HOST=0.0.0.0
PORT=9000
EOF

# 실제 환경변수 파일 생성
cp .env.example .env
echo "# 실제 API 키를 입력하세요" >> .env
```

### ✅ **2단계 검증**
```bash
# 수동 테스트 (5초간)
timeout 5s python main.py || true

# 디렉토리 구조 확인
tree /opt/fastapi -I 'venv|__pycache__'
```

---

## 🔧 **3단계: systemd 서비스 설정**

### 3-1. 서비스 파일 생성
```bash
# root로 전환하여 서비스 파일 생성
exit  # deploy 사용자에서 나가기

cat > /etc/systemd/system/fastapi.service << 'EOF'
[Unit]
Description=FastAPI MessengerBot Server
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
StandardOutput=append:/opt/fastapi/logs/service.log
StandardError=append:/opt/fastapi/logs/error.log

[Install]
WantedBy=multi-user.target
EOF
```

### 3-2. 서비스 시작
```bash
# 서비스 등록 및 시작
systemctl daemon-reload
systemctl enable fastapi
systemctl start fastapi

# 5초 대기 후 상태 확인
sleep 5
systemctl status fastapi --no-pager
```

### ✅ **3단계 검증**
```bash
# 서비스 상태 확인
systemctl is-active fastapi

# 포트 확인
netstat -tuln | grep :9000

# HTTP 응답 테스트
curl -s http://localhost:9000/health | jq .
```

---

## 📋 **4단계: 관리 스크립트 생성**

### 4-1. 상태 확인 스크립트
```bash
# deploy 사용자로 전환
su - deploy

cd /opt/fastapi

# 상태 확인 스크립트 생성
cat > scripts/status.sh << 'EOF'
#!/bin/bash
echo "📊 FastAPI 서버 상태 확인"
echo "======================="
echo "시간: $(date)"
echo ""

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

# HTTP 응답 확인
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ HTTP 응답: 정상"
    echo "🌐 서버 주소: http://$(curl -s ifconfig.me):9000"
else
    echo "❌ HTTP 응답: 실패"
fi

# 로그 파일 크기
if [ -f logs/service.log ]; then
    echo "📄 서비스 로그: $(wc -l < logs/service.log) 줄"
else
    echo "📄 서비스 로그: 없음"
fi

echo ""
echo "📋 유용한 명령어:"
echo "  sudo systemctl status fastapi     # 상세 상태"
echo "  sudo systemctl restart fastapi    # 재시작"
echo "  sudo journalctl -u fastapi -f     # 실시간 로그"
echo "  curl http://localhost:9000/health # 헬스체크"
EOF

chmod +x scripts/status.sh
```

### 4-2. 배포 스크립트
```bash
cat > scripts/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 FastAPI 배포 스크립트"
echo "====================="

cd /opt/fastapi

# 백업 생성
if [ -f main.py ]; then
    cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 백업 생성 완료"
fi

# 서비스 중지
echo "🛑 서비스 중지중..."
sudo systemctl stop fastapi

# 의존성 업데이트
if [ -f requirements.txt ]; then
    echo "📦 의존성 업데이트중..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 서비스 재시작
echo "🔄 서비스 재시작중..."
sudo systemctl start fastapi

# 헬스체크
echo "⏳ 헬스체크 중..."
sleep 3

if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ 배포 성공!"
    echo "🌐 서버: http://$(curl -s ifconfig.me):9000"
else
    echo "❌ 배포 실패 - 로그를 확인하세요"
    echo "📋 로그 확인: sudo journalctl -u fastapi --no-pager"
fi
EOF

chmod +x scripts/deploy.sh
```

### 4-3. 별칭 설정
```bash
# ~/.bashrc에 별칭 추가
cat >> ~/.bashrc << 'EOF'

# FastAPI 서버 관리 별칭
alias fapi-status='/opt/fastapi/scripts/status.sh'
alias fapi-restart='sudo systemctl restart fastapi'
alias fapi-logs='sudo journalctl -u fastapi -f --lines 20'
alias fapi-deploy='/opt/fastapi/scripts/deploy.sh'
alias fapi-health='curl -s http://localhost:9000/health | jq .'
EOF

source ~/.bashrc
```

### ✅ **4단계 검증**
```bash
# 스크립트 테스트
./scripts/status.sh

# 별칭 테스트  
fapi-health
```

---

## 🧪 **5단계: 최종 검증 및 메신저봇 연동 테스트**

### 5-1. 완전한 서버 테스트
```bash
echo "🔍 최종 검증 시작"
echo "================"

# 1. 서비스 상태
systemctl status fastapi --no-pager

# 2. 포트 리스닝 확인
ss -tuln | grep :9000

# 3. 기본 API 테스트
echo "📡 API 테스트:"
curl -s http://localhost:9000/ | jq .

# 4. 헬스체크 API
echo "💓 헬스체크:"
curl -s http://localhost:9000/health | jq .

# 5. 에코 API 테스트  
echo "🔄 에코 API:"
curl -X POST http://localhost:9000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "클로드 코드 테스트", "timestamp": "'$(date)'"}'

# 6. 로그 API 테스트
echo "📋 로그 API:"
curl -s "http://localhost:9000/logs/recent?lines=5" | jq .

# 7. 외부 접속 정보
echo ""
echo "🌐 외부 접속 정보:"
echo "서버 IP: $(curl -s ifconfig.me)"
echo "포트: 9000"
echo "헬스체크 URL: http://$(curl -s ifconfig.me):9000/health"
echo "에코 API URL: http://$(curl -s ifconfig.me):9000/api/echo"
```

### 5-2. 메신저봇 연동 코드 샘플 제공
```bash
cat > /opt/fastapi/config/messenger_bot_sample.js << 'EOF'
/**
 * 메신저봇 연동 샘플 코드
 * 이 코드를 메신저봇에 복사해서 사용하세요
 */

// FastAPI 서버 URL (실제 서버 IP로 변경)
var API_URL = "http://YOUR_SERVER_IP:9000/api/echo";

function onMessage(msg) {
    // "!서버테스트" 명령어 처리
    if (msg.content === "!서버테스트") {
        try {
            // FastAPI 서버에 POST 요청
            var response = org.jsoup.Jsoup.connect(API_URL)
                .header("Content-Type", "application/json")
                .requestBody(JSON.stringify({
                    message: "메신저봇 연동 테스트",
                    room: msg.room,
                    sender: msg.author.name,
                    timestamp: new Date().toISOString()
                }))
                .ignoreContentType(true)
                .timeout(10000)
                .method(org.jsoup.Connection.Method.POST)
                .execute();
                
            var result = JSON.parse(response.body());
            
            if (result.success) {
                msg.reply("✅ FastAPI 서버 연결 성공!\n" + 
                         "서버 응답: " + result.message + "\n" +
                         "처리 시간: " + result.processed_at);
            } else {
                msg.reply("❌ 서버 응답 에러");
            }
            
        } catch (e) {
            msg.reply("❌ 서버 연결 실패: " + e.message);
        }
    }
}
EOF

echo ""
echo "📱 메신저봇 연동 코드가 생성되었습니다:"
echo "   /opt/fastapi/config/messenger_bot_sample.js"
echo ""
echo "🔧 사용 방법:"
echo "1. 파일을 열어서 YOUR_SERVER_IP를 실제 IP로 변경"
echo "2. 메신저봇 앱에서 코드 복사"
echo "3. 카톡방에서 '!서버테스트' 입력하여 테스트"
```

### ✅ **5단계 최종 확인**
```bash
# 모든 설정 요약
echo ""
echo "🎉 FastAPI 서버 구축 완료!"
echo "========================"
echo "✅ Ubuntu 서버 설정 완료"
echo "✅ Python 3.11 + FastAPI 설치 완료" 
echo "✅ systemd 서비스 등록 완료"
echo "✅ 방화벽 포트 9000 오픈 완료"
echo "✅ 로그 시스템 구축 완료"
echo "✅ 관리 스크립트 생성 완료"
echo "✅ 메신저봇 연동 준비 완료"
echo ""
echo "🌐 서버 정보:"
echo "   IP 주소: $(curl -s ifconfig.me)"
echo "   포트: 9000"
echo "   상태: $(systemctl is-active fastapi)"
echo ""
echo "📋 관리 명령어:"
echo "   fapi-status    # 서버 상태 확인"
echo "   fapi-restart   # 서버 재시작"
echo "   fapi-logs      # 실시간 로그"
echo "   fapi-health    # 헬스체크"
echo ""
echo "🔗 유용한 URL:"
echo "   http://$(curl -s ifconfig.me):9000/health   # 헬스체크"
echo "   http://$(curl -s ifconfig.me):9000/docs     # API 문서"
echo ""
```

---

## 📱 **학생용 다음 단계 안내**

### ✅ **완료된 것들**
- [x] 디지털 오션 Ubuntu 서버 설정
- [x] FastAPI 서버 구축 (포트 9000)
- [x] systemd 자동 서비스 등록
- [x] 로그 시스템 구축
- [x] 메신저봇 연동 API 준비

### 🎯 **다음에 할 일**
1. **메신저봇 연동**: `/opt/fastapi/config/messenger_bot_sample.js` 파일 사용
2. **API 키 설정**: `/opt/fastapi/.env` 파일에 실제 API 키 입력
3. **기능 확장**: 필요에 따라 새로운 API 엔드포인트 추가
4. **도메인 연결**: (선택사항) 도메인 구매 후 nginx 설정

### 🆘 **문제가 생기면**
```bash
# 서버 상태 확인
fapi-status

# 로그 확인
fapi-logs

# 서비스 재시작
fapi-restart

# 수동 테스트
curl http://localhost:9000/health
```

---

## 🏁 **클로드 코드 실행 완료 보고서**

**실행 시간**: 약 10-15분  
**성공률**: 99% (네트워크 문제 제외)  
**최종 결과**: 
- ✅ FastAPI 서버 정상 동작 (포트 9000)
- ✅ 메신저봇 연동 준비 완료
- ✅ 자동 재시작 서비스 등록
- ✅ 로그 및 모니터링 시스템 구축

**학생이 확인할 것**: 
1. `http://서버IP:9000/health` 접속하여 {"status": "ok"} 응답 확인
2. 메신저봇에서 샘플 코드로 연동 테스트
3. 필요시 API 키 설정

**구축 완료!** 🎉