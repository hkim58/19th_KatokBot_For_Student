# 📋 메신저봇 자동 배포 시스템 - 학생용 체크리스트

## 🎯 목표
메신저봇 개발 환경에서 자동 배포 시스템을 직접 구축하고 운영할 수 있다.

---

## 📝 사전 준비 체크리스트

### 1️⃣ 개발 환경 설정
- [ ] **Git 설치**
  ```bash
  git --version  # 설치 확인
  ```
  
- [ ] **GitHub 계정 생성**
  - https://github.com 가입
  - 이메일 인증 완료
  
- [ ] **ADB 설치**
  - Windows: [Platform Tools 다운로드](https://developer.android.com/studio/releases/platform-tools)
  - Mac: `brew install android-platform-tools`
  - Linux: `sudo apt install adb`

- [ ] **코드 에디터 설치**
  - [ ] VS Code 또는
  - [ ] Claude Code 또는
  - [ ] 기타 선호 에디터

### 2️⃣ 안드로이드 설정
- [ ] **개발자 옵션 활성화**
  - 설정 → 휴대전화 정보 → 빌드 번호 7번 탭
  
- [ ] **USB 디버깅 활성화**
  - 개발자 옵션 → USB 디버깅 ON
  
- [ ] **무선 디버깅 설정** (선택사항)
  - 개발자 옵션 → 무선 디버깅 ON
  - IP 주소 확인 및 메모

- [ ] **메신저봇 R 설치**
  - 앱 설치 및 권한 부여
  - 봇 저장 경로 확인

---

## 🚀 구축 단계별 체크리스트

### Step 1: 프로젝트 초기화
- [ ] **로컬 프로젝트 폴더 생성**
  ```bash
  mkdir my-msgbot-project
  cd my-msgbot-project
  ```

- [ ] **Git 초기화**
  ```bash
  git init
  ```

- [ ] **프로젝트 구조 생성**
  ```bash
  mkdir -p Bots/MyBot scripts docs
  ```

- [ ] **첫 번째 봇 파일 생성**
  ```bash
  echo "// MyBot.js" > Bots/MyBot/MyBot.js
  ```

### Step 2: GitHub Repository 설정
- [ ] **GitHub에서 새 Repository 생성**
  - Repository 이름: `my-msgbot-project`
  - Public/Private 선택
  - README 파일 생성 안함 (로컬에서 푸시할 것)

- [ ] **로컬과 GitHub 연결**
  ```bash
  git remote add origin https://github.com/[username]/[repo-name].git
  ```

- [ ] **첫 커밋 및 푸시**
  ```bash
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git push -u origin main
  ```

### Step 2.5: 표준 문서 작성 (가장 중요!)
- [ ] **README.md 작성**
  - [ ] 배포 방법 명시 (safe_deploy.sh 사용)
  - [ ] 금지 사항 명시 (git push 직접 사용 금지)
  - [ ] 템플릿 파일 참고: `templates/README.md`

- [ ] **CONTRIBUTING.md 작성**
  - [ ] 기여 규칙 정의
  - [ ] 코드 스타일 가이드
  - [ ] 템플릿 파일 참고: `templates/CONTRIBUTING.md`

- [ ] **CLAUDE.md 작성** (AI 사용 시)
  - [ ] AI 어시스턴트 지시사항
  - [ ] ES5 문법 규칙 명시
  - [ ] 템플릿 파일 참고: `templates/CLAUDE.md`

- [ ] **Git Hooks 설정** (선택사항)
  ```bash
  # .git/hooks/pre-push 파일 생성
  echo '#!/bin/bash
echo "⚠️  직접 push 금지! safe_deploy.sh 사용!"
exit 1' > .git/hooks/pre-push
  chmod +x .git/hooks/pre-push
  ```

### Step 3: 배포 스크립트 설정
- [ ] **템플릿 파일 복사**
  - `deploy.sh` 템플릿을 `scripts/` 폴더로 복사
  - `safe_deploy.sh` 템플릿을 `scripts/` 폴더로 복사

- [ ] **deploy.sh 수정**
  - [ ] DEVICE_IP 설정 (본인 안드로이드 IP)
  - [ ] BOTS 배열에 봇 이름 추가
  - [ ] 실행 권한 부여: `chmod +x scripts/deploy.sh`

- [ ] **safe_deploy.sh 수정**
  - [ ] GITHUB_USERNAME 설정
  - [ ] GITHUB_REPO 설정
  - [ ] ANDROID_IP 설정
  - [ ] 실행 권한 부여: `chmod +x scripts/safe_deploy.sh`

- [ ] **.gitignore 파일 생성**
  - 템플릿 `.gitignore` 파일 복사
  - 필요시 커스터마이징

### Step 4: 첫 배포 테스트
- [ ] **ADB 연결 테스트**
  ```bash
  ./scripts/deploy.sh --test
  ```

- [ ] **로컬 배포 테스트**
  ```bash
  ./scripts/deploy.sh
  ```

- [ ] **GitHub 푸시 테스트**
  ```bash
  ./scripts/safe_deploy.sh
  # 옵션 2 선택 (GitHub 동기화)
  ```

- [ ] **전체 배포 테스트**
  ```bash
  ./scripts/safe_deploy.sh
  # 옵션 3 선택 (전체 배포)
  ```

### Step 5: 실제 봇 개발
- [ ] **봇 코드 작성**
  - Bots/MyBot/MyBot.js 편집
  - ES5 문법 준수

- [ ] **테스트 및 디버깅**
  - 로컬 배포로 빠른 테스트
  - 메신저봇 앱에서 컴파일

- [ ] **버전 관리**
  - 의미있는 커밋 메시지 작성
  - 정기적인 GitHub 푸시

---

## 🔧 문제 해결 체크리스트

### Git 관련
- [ ] **"fatal: not a git repository"**
  - `git init` 실행했는지 확인
  
- [ ] **"Permission denied (publickey)"**
  - GitHub 로그인 확인
  - HTTPS URL 사용 권장

- [ ] **"Updates were rejected"**
  - `git pull origin main` 먼저 실행
  - 충돌 해결 후 다시 푸시

### ADB 관련
- [ ] **"device not found"**
  - USB 케이블 연결 확인
  - USB 디버깅 활성화 확인
  - ADB 드라이버 설치 확인

- [ ] **"device offline"**
  - 안드로이드에서 연결 승인
  - ADB 재시작: `adb kill-server && adb start-server`

- [ ] **무선 연결 실패**
  - 같은 Wi-Fi 네트워크 확인
  - 방화벽 설정 확인
  - 포트 5555 개방 확인

### 배포 스크립트 관련
- [ ] **"Permission denied"**
  - `chmod +x scripts/*.sh` 실행
  
- [ ] **"No such file or directory"**
  - 스크립트 경로 확인
  - 봇 파일 존재 확인

---

## 💡 핵심 포인트

### ⚠️ 가장 중요한 교훈
**"스크립트를 만드는 것보다 그것을 표준으로 정의하는 것이 더 중요하다"**

1. **README.md가 프로젝트의 헌법**
   - 모든 팀원이 첫 번째로 보는 문서
   - 배포 방법을 명확히 정의

2. **문서화가 코드보다 중요**
   - 좋은 문서 = 팀 효율성 향상
   - 나쁜 문서 = 혼란과 실수

3. **규칙을 시스템으로 강제**
   - Git Hooks로 잘못된 방법 차단
   - 자동화로 실수 방지

## 📊 완성도 평가 기준

### 🥉 Bronze (기본)
- [ ] Git 저장소 생성 완료
- [ ] 첫 커밋 성공
- [ ] 로컬 배포 성공
- [ ] 1개 봇 작동 확인

### 🥈 Silver (중급)
- [ ] GitHub 연동 완료
- [ ] safe_deploy.sh 작동
- [ ] 3개 이상 봇 관리
- [ ] 정기적인 커밋 (일 1회 이상)
- [ ] .gitignore 적절히 설정

### 🥇 Gold (고급)
- [ ] 팀 협업 환경 구축
- [ ] 브랜치 전략 적용
- [ ] 자동화 스크립트 커스터마이징
- [ ] 배포 로그 시스템 구축
- [ ] 롤백 기능 구현

### 💎 Diamond (전문가)
- [ ] CI/CD 파이프라인 구축
- [ ] 서버 연동 자동화
- [ ] 테스트 자동화
- [ ] 모니터링 시스템 구축
- [ ] 문서화 완벽 수행

---

## 📚 추가 학습 자료

### 필수 읽기
- [ ] [Git 기초](https://git-scm.com/book/ko/v2)
- [ ] [GitHub 시작하기](https://docs.github.com/ko/get-started)
- [ ] [ADB 명령어](https://developer.android.com/studio/command-line/adb)

### 추천 영상
- [ ] Git & GitHub 입문 (생활코딩)
- [ ] 메신저봇 R 기초 강좌
- [ ] Shell Script 기초

### 실습 프로젝트
- [ ] 날씨 알림 봇 만들기
- [ ] 할 일 관리 봇 만들기
- [ ] 팀 공지 봇 만들기

---

## 🎯 최종 목표

### 1주차 목표
- [ ] 배포 시스템 구축 완료
- [ ] 첫 봇 배포 성공

### 2주차 목표
- [ ] 3개 이상 봇 개발
- [ ] 일일 커밋 습관화

### 3주차 목표
- [ ] 팀 프로젝트 시작
- [ ] 협업 워크플로우 확립

### 4주차 목표
- [ ] 완성된 봇 서비스 운영
- [ ] 포트폴리오 정리

---

## 💬 질문 체크리스트

궁금한 점이 있다면 다음 정보와 함께 질문하세요:

- [ ] 운영체제 (Windows/Mac/Linux)
- [ ] Git 버전
- [ ] 에러 메시지 전체
- [ ] 시도한 해결 방법
- [ ] 스크린샷 (가능한 경우)

---

## 🏆 완료 인증

모든 체크리스트를 완료했다면:

1. GitHub Repository URL 공유
2. 배포 성공 스크린샷 제출
3. 개발한 봇 시연 영상 (선택)

---

*이 체크리스트는 지속적으로 업데이트됩니다.*
*최종 수정: 2024년 1월*