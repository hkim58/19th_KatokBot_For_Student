# 카카오톡 메신저봇 + FastAPI 서버 + Google Calendar MCP 완전 이해 강의안

## 1. 전체 구조 이해

- 카카오톡의 메신저봇(예: 메신저봇R 등)에서 사용자가 메시지를 입력
- 메시지(예: "내 일정 보여줘", "내일 3시 일정 추가해줘")를 FastAPI 서버로 전송 (Webhook 방식)
- FastAPI 서버에서는 Python 기반 MCP Google Calendar 서버를 설치해서, 자연어 요청 처리
- 서버는 Google OAuth 인증을 통해 자신의 구글 캘린더와 연결됨
- 자연어 명령 → MCP 툴로 파싱 → Google Calendar API 액션 실행
- 결과(일정 조회/추가/수정/삭제)를 다시 카톡 메시지로 응답

---

## 2. 구글 캘린더 MCP (FastAPI) 서버 설계

- MCP 서버는 Python으로 구현, FastAPI로 HTTP 엔드포인트 노출
- 주요 기능:
  - 캘린더 조회(본인 계정의 모든 일정 가져오기)
  - 새로운 일정 생성: 시간, 제목, 설명, 참석자 정보 등
  - 일정 수정/삭제
  - "충돌 체크": 동일 시간대에 기존 일정이 있을 경우, 충돌 메시지를 출력하고, 사용자에게 확인 요청("충돌 일정과 함께 등록할까요?")
  - Free/Busy 조회: 특정 시간에 일정이 있는지 확인
- Google OAuth 2.0 인증으로 최초 1회 본인 구글 계정 연결 후 토큰 저장 → 지속적으로 액세스 가능

---

## 3. 비개발자 학생을 위한 핵심 흐름 요약

1. 카톡에서 "일정 보여줘"라고 입력한다
2. 메신저봇이 해당 메시지를 FastAPI 서버의 /webhook 엔드포인트로 POST 전송한다
3. FastAPI 서버는 자연어를 해석해서, MCP Google Calendar 모듈에 전달한다
4. MCP 모듈은 구글 캘린더 API에서 사용자의 일정을 가져와 응답한다
5. FastAPI 서버에서 "오늘 일정: 3시 미팅, 5시 저녁"과 같이 카톡 형식으로 반환한다
6. 학생이 "내일 3시에 일정 등록해줘"라고 하면, FastAPI 서버가 Google Calendar MCP로 등록 액션 보내기
7. 등록 전에 동일 시간대에 일정 있는지 체크하여 "이미 3시 일정이 있는데 등록할까요?" 추가 질문
8. 사용자가 "네"라고 답하면, 최종적으로 일정 등록 후 확인 메시지 반환
9. 일정 수정/삭제도 모두 위와 같이 처리

---

## 4. 메신저봇 JS 코드 예시 (라이노 엔진)

```javascript
function response(room, msg, sender, isGroupChat, replier) {
  if (msg.startsWith("일정 보여줘")) {
    // FastAPI 서버로 POST 요청: 내 일정 보여달라고 전달
    var url = "https://my-fastapi-server.domain/webhook";
    var data = {
      "msg": msg,
      "sender": sender,
      "room": room
    };
    var res = org.jsoup.Jsoup.connect(url)
        .header("Content-Type", "application/json")
        .requestBody(JSON.stringify(data))
        .ignoreContentType(true)
        .post();
    var serverReply = res.body();
    replier.reply(serverReply); // 구글 일정 결과 그대로 전달
  }
  // 추가: 일정 추가/수정/삭제 명령 등 필요한 만큼 if..else
}
```

---

## 5. FastAPI 파이썬 서버 예시 코드

```python
from fastapi import FastAPI, Request
import uvicorn
import calendar_mcp_module  # MCP Google Calendar 모듈 임포트

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    req_json = await request.json()
    msg = req_json.get("msg")
    sender = req_json.get("sender")
    # 자연어 명령 해석: 예시 - "일정 보여줘"
    if "일정 보여줘" in msg:
        events = calendar_mcp_module.get_my_events()
        return events
    elif "일정 추가" in msg:
        # 시간, 제목, 설명 등 추가 파싱 필요
        # 충돌 체크: MCP의 free/busy 활용, 있으면 사용자에게 확인 질문 반환
        pass
    # 기타: 일정 수정/삭제 명령 해석 등 다양한 액션 가능
    return {"reply": "명령어를 인식못했습니다."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 6. 실제 구축 및 협업 팁

- 클로드코드, 코덱스 등과 협업할 때 MCP 서버의 명령어(캘린더 액션)를 자연어로 디자인하면 누구나 이해 가능
- JS와 파이썬 모두 단순 api 호출 구조라 비개발자도 쉽게 실습
- FastAPI 서버는 Digital Ocean에 배포, 외부 접속 허용해야 함
- Google OAuth 인증은 한번만, 토큰 자동 저장
- MCP 사용법 및 자연어 액션 디자인 예시는 Claude/Cursor 툴에 매핑해서 강의

---

## 7. 결론

- 누구나 가능한 카톡봇 + Google Calendar MCP 연동 데모 가능
- 실전 과제로 일정 추가/조회/수정/삭제 모두 체험
- 충돌 체크/자연어 질문 적용하여 캘린더 챗봇 완성


---

(본 강의안은 실제 실습에 기반한 구조 및 코드 예제로, 학생들이 이해하기 쉽게 단계별로 안내함)
