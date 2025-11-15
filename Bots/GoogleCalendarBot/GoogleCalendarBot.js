/**
 * GoogleCalendarBot.js
 * --------------------
 * FastAPI + Google Calendar MCP 서버와 연동해 일정을 조회/추가/삭제하는 예제입니다.
 *
 * 명령어 (TARGET_ROOMS에서만 작동):
 * 1) 캘린더 조회 [YYYY-MM-DD|오늘|내일]
 * 2) 캘린더 빈시간 [YYYY-MM-DD|오늘|내일]
 * 3) 캘린더 추가 (YYYY-MM-DD|오늘|내일) HH:MM 제목
 * 4) 캘린더 삭제 <EVENT_ID>
 *
 * FastAPI 서버에 그대로 메시지를 전달하고, 서버가 자연어 파싱 및 Google Calendar API 연동을 처리합니다.
 * 학생은 FASTAPI_WEBHOOK_URL, TARGET_ROOMS만 자신의 환경에 맞게 수정하면 바로 사용 가능합니다.
 */

var bot = BotManager.getCurrentBot();

var CONFIG = {
    BOT_NAME: "GoogleCalendarBot",
    TARGET_ROOMS: ["DEBUG ROOM", "카카오봇 실습방"], // ← 사용하는 채팅방으로 교체
    FASTAPI_WEBHOOK_URL: "http://127.0.0.1:9000/calendar/webhook", // ← FastAPI 서버 주소
    REQUEST_TIMEOUT: 10000
};

function sendToServer(payload, room) {
    new java.lang.Thread(function() {
        try {
            var response = org.jsoup.Jsoup.connect(CONFIG.FASTAPI_WEBHOOK_URL)
                .header("Content-Type", "application/json")
                .ignoreContentType(true)
                .timeout(CONFIG.REQUEST_TIMEOUT)
                .requestBody(JSON.stringify(payload))
                .method(org.jsoup.Connection.Method.POST)
                .execute();

            var body = response.body();
            bot.send(room, body);
        } catch (e) {
            Log.e("[" + CONFIG.BOT_NAME + "] FastAPI 요청 실패: " + e.message);
            bot.send(room, "서버와 통신할 수 없습니다. FastAPI 로그를 확인해주세요.");
        }
    }).start();
}

bot.on("message", function(msg) {
    if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
        return;
    }

    var text = msg.content.trim();
    if (text.indexOf("캘린더 ") !== 0) {
        return;
    }

    var payload = {
        room: msg.room,
        sender: msg.author ? msg.author.name : "Unknown",
        message: text
    };

    bot.send(msg.room, "🔁 요청을 처리 중입니다...");
    sendToServer(payload, msg.room);
});

Log.i("[" + CONFIG.BOT_NAME + "] FastAPI 연동 캘린더 봇 준비 완료");
