# DigitalOcean FastAPI 서버 & Codex 협업 강의안

> 새로 만든 DigitalOcean(Ubuntu 22.04) 인스턴스에서 FastAPI 서비스를 신속히 준비하고 Codex CLI와 함께 운영할 때 필요한 필수 절차입니다. 각 단계는 Codex가 그대로 실행/복기할 수 있도록 명령어 위주로 구성했습니다.

## 0. Claude Code vs Codex 차이 핵심 정리

| 항목 | Claude Code | Codex CLI |
| --- | --- | --- |
| SSH 접근 | 상시 가능 | 세션당 1개의 CLI 인스턴스 |
| 파일 편집 | VSCode 스타일 | CLI + 편집 명령 (apply_patch 등) |
| 서버 제어 | 자유로운 명령 조합 가능 | 미리 정의된 명령/스크립트가 있으면 반복 실행이 쉬움 |
| UI/로그 | 브라우저 확인 가능 | CLI 로그/`tmux`/`journalctl` 명령이 필요 |

**따라서**: `scripts/` 폴더에 start/stop/restart 스크립트를 두고, `logs/fastapi.log` 같은 파일을 유지하면 두 에이전트 모두 동일한 절차로 서버 상태를 공유할 수 있습니다.

## 1. 서버 기본 세팅

1. **접속 및 사용자 분리**
   - `ssh root@<IP>`
   - `adduser deploy && usermod -aG sudo deploy`
2. **패키지 최신화**
   - `sudo apt update && sudo apt upgrade -y`
3. **방화벽**
   - `sudo ufw allow 22 && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw allow 9000`
   - `sudo ufw enable`
4. **기본 도구**
   - `sudo apt install -y git unzip htop tmux tree curl wget`
5. **타임존**
   - `sudo timedatectl set-timezone Asia/Seoul`

> Codex에 “서버 초기화 체크리스트 실행”을 요청하면 위 명령을 순차적으로 수행하게 할 수 있습니다.

## 2. Python & FastAPI 환경 준비

1. **필수 패키지**
   - `sudo apt install -y python3.11 python3.11-venv python3-pip`
2. **작업 디렉터리**
   - `sudo mkdir -p /opt/fastapi && sudo chown deploy:deploy /opt/fastapi`
   - `mkdir -p /opt/fastapi/{logs,scripts,config,static,templates}`
   - `touch /opt/fastapi/logs/fastapi.log`
3. **가상환경 생성**
   ```bash
   cd /opt/fastapi
   python3.11 -m venv venv
   source venv/bin/activate
   ```
4. **FastAPI 설치**
   - `pip install fastapi uvicorn[standard] python-dotenv`
5. **예제 앱 작성**
   ```python
   # main.py
   from fastapi import FastAPI
   app = FastAPI()

   @app.get("/health")
   async def health():
       return {"status": "ok"}

   @app.get("/logs/recent")
   async def recent_logs(lines: int = 20):
       path = Path("logs/fastapi.log")
       if not path.exists():
           return {"success": False, "logs": []}
       content = path.read_text(encoding="utf-8").splitlines()
       return {"success": True, "logs": content[-lines:]}
   ```
6. **필수 파일**
   - `pip freeze > requirements.txt`
   - `.env.example` (API 키 자리만 명시)

> Codex에 `fastapi` 디렉터리를 넘길 때 `requirements.txt/main.py/.env.example`가 있으면 즉시 가상환경을 복원하거나 테스트 서버를 올릴 수 있습니다.

## 3. uvicorn 수동 테스트

```bash
cd /opt/fastapi
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

- 브라우저나 `curl http://<IP>:9000/health`로 확인.
- Codex에게 “로컬 uvicorn 테스트” 요청 시 동일 명령을 실행하도록 지시하면 됩니다.

## 4. systemd 서비스 구성

`/etc/systemd/system/fastapi.service`

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

명령:
```
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
```

> Codex나 Claude Code에게 "서비스 재시작"만 부탁하면 `sudo systemctl restart fastapi` 명령으로 일관되게 처리됩니다.

## 5. Codex 협업 팁

- **README_DEPLOY.md** 예시:
  1. `source venv/bin/activate`
  2. `uvicorn main:app --host 0.0.0.0 --port 9000`
  3. `sudo systemctl restart fastapi`
  - Codex가 동일 명령을 실행하며 로그까지 제공.
- **tmux 세션**: `tmux new -s codex` → Codex에게 “tmux attach -t codex” 요청으로 실시간 로그 공유.
- **환경 변수**: `.env`는 서버에서만 생성, Codex에겐 `.env.example`만 전달.
- **로그 파일 공유**: 모든 uvicorn 출력이 `/opt/fastapi/logs/fastapi.log`에 남도록 `logging` 설정을 추가하면 Codex가 `tail -n 50 logs/fastapi.log`로 즉시 확인 가능.
- **디렉터리 트리 안내** (README에 고정):
  ```
  /opt/fastapi
  ├── config/
  ├── logs/fastapi.log
  ├── scripts/start_server.sh
  ├── scripts/restart_server.sh
  ├── static/
  ├── templates/
  ├── venv/
  └── main.py
  ```

## 6. 재부팅 및 로그 확인

| 작업 | 명령 |
| --- | --- |
| 상태 확인 | `sudo systemctl status fastapi` |
| 재시작 | `sudo systemctl restart fastapi` |
| 부팅 시 자동실행 | `sudo systemctl is-enabled fastapi` |
| 실시간 로그 | `sudo journalctl -u fastapi -f` |
| 최근 10분 로그 | `sudo journalctl -u fastapi --since "10 minutes ago"` |

Codex가 로그 확인을 도와줄 때도 동일 명령을 복사해 실행하도록 요청하면 됩니다.

## 7. 보조 도구 & 모니터링

- `sudo apt install -y nginx` → 추후 HTTPS/리버스 프록시 준비.
- `sudo apt install -y fail2ban` → 기본 SSH 보안.
- 자원 모니터링: `htop`, `df -h`, `free -m`.
- `docs/deploy.md` 같은 문서에 “로그 확인 명령”을 표 형태로 기록해 두면, Codex가 문제 발생 시 동일 명령을 실행하고 결과를 공유하기 쉬워집니다.

## 8. start/stop/restart 스크립트 (선택 사항)

`/opt/fastapi/scripts/start_server.sh`

```bash
#!/bin/bash
cd /opt/fastapi
source venv/bin/activate
LOG_DIR=/opt/fastapi/logs
mkdir -p "$LOG_DIR"
echo "[$(date)] FastAPI start" >> "$LOG_DIR/fastapi.log"
tmux new-session -d -s fastapi-app \
  "cd /opt/fastapi && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 9000 >> logs/fastapi.log 2>&1"
echo "tmux attach -t fastapi-app # 로 로그 확인"
```

`/opt/fastapi/scripts/stop_server.sh`
```bash
#!/bin/bash
tmux kill-session -t fastapi-app 2>/dev/null
echo "[$(date)] FastAPI stopped" >> /opt/fastapi/logs/fastapi.log
```

`/opt/fastapi/scripts/restart_server.sh`
```bash
#!/bin/bash
set -e
/opt/fastapi/scripts/stop_server.sh
/opt/fastapi/scripts/start_server.sh
```

> Codex·Claude Code 모두 위 스크립트를 실행해 동일한 동작을 얻을 수 있습니다. systemd 사용 중이라면 `Restart=always`를 유지하되, 개발 중에는 tmux 스크립트를 사용해 빠르게 로그를 확인하는 패턴이 특히 편리합니다.

---

### 마무리
1. **SSH → venv → uvicorn → systemd → 로그** 순서를 반복 학습하면 FastAPI 서버를 언제든 재현 가능.
2. Codex와 협업 시 명령·경로·환경 구성을 문서화해 두면 CLI가 그대로 따라 하며 기록을 남겨 줍니다.
3. 서버 템플릿을 만들어 두고 새 프로젝트마다 이 문서를 복사해 맞춤 경로만 수정하면, 누구나 DigitalOcean에서 FastAPI를 안정적으로 운영할 수 있습니다.
