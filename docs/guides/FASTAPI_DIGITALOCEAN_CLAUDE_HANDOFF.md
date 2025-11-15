# Claude Code 전용 요청 템플릿

> 이 문서를 Claude Code에 그대로 전달하면, DigitalOcean Ubuntu 22.04 서버 위에 FastAPI 환경을 자동으로 구축하도록 안내합니다.

## 1. 서버 접속 및 체크리스트

```
ssh deploy@<SERVER_IP>
cd /opt/fastapi || sudo mkdir -p /opt/fastapi && sudo chown deploy:deploy /opt/fastapi && cd /opt/fastapi
```

1. `sudo apt update && sudo apt upgrade -y`
2. `sudo apt install -y python3.11 python3.11-venv python3-pip git unzip htop tmux`
3. `sudo timedatectl set-timezone Asia/Seoul`

## 2. 프로젝트 구조

```
/opt/fastapi
├── venv/
├── main.py
├── requirements.txt
├── .env.example
├── logs/fastapi.log
└── scripts/{start,stop,restart}_server.sh
```

Claude에게 다음을 실행시켜 주세요:

1. `python3.11 -m venv venv && source venv/bin/activate`
2. `pip install fastapi uvicorn[standard] python-dotenv`
3. `pip freeze > requirements.txt`
4. `.env.example` 파일 생성 (API_KEY= 등 자리만 작성)

## 3. 샘플 앱

```python
from pathlib import Path
from fastapi import FastAPI

app = FastAPI(title="Student FastAPI Server")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/logs/recent")
async def logs(lines: int = 20):
    log_path = Path("logs/fastapi.log")
    if not log_path.exists():
        return {"success": False, "logs": []}
    content = log_path.read_text(encoding="utf-8").splitlines()
    return {"success": True, "logs": content[-lines:]}
```

Claude에게 `mkdir -p logs && touch logs/fastapi.log`도 함께 요청합니다.

## 4. uvicorn 테스트 명령

```
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

테스트가 끝나면 Ctrl+C로 종료하고 다음 단계로 넘어갑니다.

## 5. systemd 서비스

`sudo tee /etc/systemd/system/fastapi.service`:

```
[Unit]
Description=FastAPI Service
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/fastapi
Environment="PATH=/opt/fastapi/venv/bin"
ExecStart=/opt/fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

이후:
```
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

## 6. 로그 & 재시작

- 실시간 로그: `sudo journalctl -u fastapi -f`
- 최근 로그: `tail -n 50 logs/fastapi.log`
- 재시작: `sudo systemctl restart fastapi`

이 체크리스트를 Claude에게 전달하면, 동일한 명령 순서로 서버 설정을 완료해 줄 것입니다.
