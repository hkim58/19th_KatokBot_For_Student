/**
 * =============================================
 * Google Calendar 연동 메신저봇 (완전 실용 버전)
 * =============================================
 * 
 * 🎯 지원하는 자연어 명령어:
 * 
 * 📅 일정 조회:
 *   - "일정" / "오늘 일정" → 오늘 일정 보기
 *   - "내일 일정" / "내일" → 내일 일정 보기  
 *   - "이번주 일정" / "주간 일정" → 주간 일정 보기
 * 
 * ➕ 일정 추가:
 *   - "일정 추가 회의 내일 3시" → 내일 15:00에 회의 추가
 *   - "일정 추가 점심 오늘 12시 친구와" → 오늘 12:00에 점심 추가
 *   - "일정 추가 병원 2024-01-15 14:30" → 정확한 날짜/시간으로 추가
 * 
 * 🗑️ 일정 삭제:
 *   - "일정 삭제 1" → 조회된 일정 목록의 1번 삭제
 *   - "삭제 2" → 2번 일정 삭제
 * 
 * 🕐 빈시간 조회:
 *   - "빈시간 오늘" → 오늘 비어있는 시간대 확인
 *   - "빈시간 내일" → 내일 가능한 시간 확인
 *   - "빈시간 2024-01-15" → 특정 날짜 빈시간 확인
 * 
 * ❓ 도움말:
 *   - "캘린더 도움말" → 전체 명령어 안내
 *   - "서버 상태" → 연결 상태 확인
 * 
 * ⚙️ 설정 (코드 수정 필요):
 * 1. SERVER_URL을 실제 FastAPI 서버 주소로 변경
 * 2. TARGET_ROOMS를 실제 카톡방 이름으로 변경
 * 3. 메신저봇 앱에서 컴파일 및 실행
 * 
 * ⏱️ 예상 설정 시간: 30-60분 (Google Cloud 설정 포함)
 */

// ====== 설정 구간 ======
var CONFIG = {
    BOT_NAME: "GoogleCalendarBot",
    
    // 🎯 [필수 수정] FastAPI 서버 URL
    SERVER_URL: "http://your-server-ip:9000",  // 실제 서버 IP로 변경!
    
    // 🎯 [필수 수정] 봇이 작동할 방 목록
    TARGET_ROOMS: ["테스트방", "개인 일정방"],  // 실제 카톡방 이름으로 변경!
    
    // API 설정
    TIMEOUT: 15000,  // 15초 타임아웃
    MAX_RETRIES: 2   // 재시도 횟수
};

// ====== 봇 객체 가져오기 ======
var bot = BotManager.getCurrentBot();

// ====== 유틸리티 함수들 ======

/**
 * 날짜 문자열을 표준 형식으로 변환
 */
function parseDate(dateStr) {
    var today = new Date();
    
    if (dateStr === "오늘") {
        return formatDate(today);
    } else if (dateStr === "내일") {
        var tomorrow = new Date(today);
        tomorrow.setDate(today.getDate() + 1);
        return formatDate(tomorrow);
    } else if (dateStr === "모레") {
        var dayAfter = new Date(today);
        dayAfter.setDate(today.getDate() + 2);
        return formatDate(dayAfter);
    }
    
    // 기본적으로 입력된 문자열 반환
    return dateStr;
}

/**
 * Date 객체를 YYYY-MM-DD 형식으로 변환
 */
function formatDate(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    return year + "-" + month + "-" + day;
}

/**
 * 시간 문자열을 24시간 형식으로 변환
 */
function parseTime(timeStr) {
    // "3시" -> "15:00", "오후 3시" -> "15:00"
    if (timeStr.includes("오후")) {
        var hour = parseInt(timeStr.replace(/[^0-9]/g, ""));
        if (hour !== 12) hour += 12;
        return hour + ":00";
    } else if (timeStr.includes("오전")) {
        var hour = parseInt(timeStr.replace(/[^0-9]/g, ""));
        if (hour === 12) hour = 0;
        return String(hour).padStart(2, '0') + ":00";
    } else {
        var hour = parseInt(timeStr.replace(/[^0-9]/g, ""));
        return String(hour).padStart(2, '0') + ":00";
    }
}

// ====== API 호출 함수들 ======

/**
 * FastAPI 서버에 HTTP 요청 보내기
 */
function callAPI(endpoint, data, retryCount) {
    if (retryCount === undefined) retryCount = 0;
    
    try {
        Log.i("[" + CONFIG.BOT_NAME + "] API 호출: " + endpoint);
        
        var url = CONFIG.SERVER_URL + endpoint;
        var requestBody = JSON.stringify(data);
        
        var response = org.jsoup.Jsoup.connect(url)
            .header("Content-Type", "application/json")
            .header("User-Agent", "MessengerBot-GoogleCalendar/1.0")
            .requestBody(requestBody)
            .ignoreContentType(true)
            .timeout(CONFIG.TIMEOUT)
            .method(org.jsoup.Connection.Method.POST)
            .execute();
        
        var statusCode = response.statusCode();
        var responseBody = response.body();
        
        if (statusCode === 200) {
            var result = JSON.parse(responseBody);
            Log.i("[" + CONFIG.BOT_NAME + "] API 응답 성공");
            return result;
        } else {
            Log.e("[" + CONFIG.BOT_NAME + "] API 에러: HTTP " + statusCode);
            throw new Error("서버 응답 에러: " + statusCode);
        }
        
    } catch (e) {
        Log.e("[" + CONFIG.BOT_NAME + "] API 호출 실패: " + e.message);
        
        // 재시도 로직
        if (retryCount < CONFIG.MAX_RETRIES) {
            Log.i("[" + CONFIG.BOT_NAME + "] 재시도 " + (retryCount + 1) + "/" + CONFIG.MAX_RETRIES);
            java.lang.Thread.sleep(2000);  // 2초 대기
            return callAPI(endpoint, data, retryCount + 1);
        }
        
        return {
            success: false,
            error: "서버 연결 실패: " + e.message,
            message: "잠시 후 다시 시도해주세요."
        };
    }
}

// ====== 메인 기능 함수들 ======

/**
 * 일정 조회
 */
function getEvents(period) {
    Log.i("[" + CONFIG.BOT_NAME + "] 일정 조회 요청: " + period);
    
    var data = {
        action: "get_events",
        period: period || "today"
    };
    
    var result = callAPI("/api/calendar/events", data);
    
    if (result.success) {
        if (result.events && result.events.length > 0) {
            var message = "📅 " + (period === "today" ? "오늘" : period === "tomorrow" ? "내일" : period) + " 일정:\n\n";
            
            for (var i = 0; i < result.events.length; i++) {
                var event = result.events[i];
                message += (i + 1) + ". " + event.title + "\n";
                message += "   🕐 " + event.start_time;
                if (event.end_time) {
                    message += " - " + event.end_time;
                }
                message += "\n";
                if (event.description) {
                    message += "   📝 " + event.description + "\n";
                }
                message += "\n";
            }
            
            return message.trim();
        } else {
            return "📅 " + (period === "today" ? "오늘" : period === "tomorrow" ? "내일" : period) + " 일정이 없습니다.";
        }
    } else {
        return "❌ " + (result.message || "일정을 가져올 수 없습니다.");
    }
}

/**
 * 일정 추가
 */
function addEvent(title, datetime, description) {
    Log.i("[" + CONFIG.BOT_NAME + "] 일정 추가: " + title + " at " + datetime);
    
    var data = {
        action: "add_event",
        title: title,
        datetime: datetime,
        description: description || ""
    };
    
    var result = callAPI("/api/calendar/events", data);
    
    if (result.success) {
        var message = "✅ 일정이 등록되었습니다!\n\n";
        message += "📌 제목: " + title + "\n";
        message += "🕐 시간: " + datetime + "\n";
        if (description) {
            message += "📝 메모: " + description + "\n";
        }
        
        // 충돌 경고가 있는 경우
        if (result.warning) {
            message += "\n⚠️ " + result.warning;
        }
        
        return message;
    } else {
        return "❌ " + (result.message || "일정 등록에 실패했습니다.");
    }
}

/**
 * 일정 삭제
 */
function deleteEvent(eventId) {
    Log.i("[" + CONFIG.BOT_NAME + "] 일정 삭제: " + eventId);
    
    var data = {
        action: "delete_event",
        event_id: eventId
    };
    
    var result = callAPI("/api/calendar/events", data);
    
    if (result.success) {
        return "✅ 일정이 삭제되었습니다.";
    } else {
        return "❌ " + (result.message || "일정 삭제에 실패했습니다.");
    }
}

/**
 * 빈 시간 확인
 */
function checkFreeTime(date) {
    Log.i("[" + CONFIG.BOT_NAME + "] 빈시간 확인: " + date);
    
    var data = {
        action: "check_free_time",
        date: parseDate(date)
    };
    
    var result = callAPI("/api/calendar/free-busy", data);
    
    if (result.success) {
        var message = "🕐 " + date + " 빈 시간:\n\n";
        
        if (result.free_slots && result.free_slots.length > 0) {
            for (var i = 0; i < result.free_slots.length; i++) {
                var slot = result.free_slots[i];
                message += "⭕ " + slot.start + " - " + slot.end + "\n";
            }
        } else {
            message += "❌ 빈 시간이 없습니다.";
        }
        
        return message;
    } else {
        return "❌ " + (result.message || "빈시간을 확인할 수 없습니다.");
    }
}

// ====== 메시지 파싱 함수들 ======

/**
 * "일정 추가" 명령어 파싱
 * 예: "일정 추가 회의 내일 3시", "일정 추가 점심약속 2024-01-15 12:00 친구와 점심"
 */
function parseAddEventCommand(content) {
    // "일정 추가" 제거
    var remaining = content.replace(/^일정\s*추가\s*/i, "").trim();
    
    var parts = remaining.split(/\s+/);
    if (parts.length < 2) {
        return null;
    }
    
    var title = parts[0];
    var timeStr = parts[1];
    var dateTimeStr = timeStr;
    
    // 시간 정보가 별도로 있는 경우
    if (parts.length > 2 && /^\d+시?$/.test(parts[2])) {
        dateTimeStr = timeStr + " " + parseTime(parts[2]);
    }
    
    // 설명이 있는 경우
    var description = "";
    if (parts.length > 3) {
        description = parts.slice(3).join(" ");
    } else if (parts.length > 2 && !/^\d+시?$/.test(parts[2])) {
        description = parts.slice(2).join(" ");
    }
    
    return {
        title: title,
        datetime: parseDate(dateTimeStr),
        description: description
    };
}

// ====== 메인 메시지 처리 ======

bot.on("message", function(msg) {
    // 설정된 방에서만 작동
    if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
        return;
    }
    
    var content = msg.content.trim();
    var room = msg.room;
    var author = msg.author.name;
    
    Log.i("[" + CONFIG.BOT_NAME + "] 메시지 수신: " + content);
    
    try {
        // ========== 일정 조회 ==========
        if (content === "일정" || content === "일정 보여줘" || content === "오늘 일정") {
            var response = getEvents("today");
            msg.reply(response);
        }
        else if (content === "내일 일정" || content === "내일 일정 보여줘") {
            var response = getEvents("tomorrow");
            msg.reply(response);
        }
        else if (content === "이번주 일정" || content === "주간 일정") {
            var response = getEvents("week");
            msg.reply(response);
        }
        
        // ========== 일정 추가 ==========
        else if (content.startsWith("일정 추가")) {
            var eventData = parseAddEventCommand(content);
            
            if (eventData) {
                var response = addEvent(eventData.title, eventData.datetime, eventData.description);
                msg.reply(response);
            } else {
                msg.reply("❌ 올바른 형식으로 입력해주세요.\n" +
                         "예: 일정 추가 회의 내일 3시\n" +
                         "예: 일정 추가 점심 2024-01-15 12:00 친구와");
            }
        }
        
        // ========== 일정 삭제 ==========
        else if (content.startsWith("일정 삭제")) {
            var deleteMatch = content.match(/일정\s*삭제\s*(\d+)/);
            if (deleteMatch) {
                var eventNumber = deleteMatch[1];
                var response = deleteEvent(eventNumber);
                msg.reply(response);
            } else {
                msg.reply("❌ 삭제할 일정 번호를 입력해주세요.\n예: 일정 삭제 1");
            }
        }
        
        // ========== 빈시간 확인 ==========
        else if (content.startsWith("빈시간")) {
            var freeTimeMatch = content.match(/빈시간\s*(.+)/);
            var date = freeTimeMatch ? freeTimeMatch[1].trim() : "오늘";
            
            var response = checkFreeTime(date);
            msg.reply(response);
        }
        
        // ========== 도움말 ==========
        else if (content === "캘린더 도움말" || content === "일정 도움말") {
            var helpMessage = "📅 Google Calendar Bot 사용법\n\n" +
                            "📋 일정 조회:\n" +
                            "• 일정, 오늘 일정\n" +
                            "• 내일 일정\n" +
                            "• 이번주 일정\n\n" +
                            "➕ 일정 추가:\n" +
                            "• 일정 추가 [제목] [날짜] [시간]\n" +
                            "• 예: 일정 추가 회의 내일 3시\n" +
                            "• 예: 일정 추가 점심 오늘 12시 친구와\n\n" +
                            "🗑️ 일정 삭제:\n" +
                            "• 일정 삭제 [번호]\n" +
                            "• 예: 일정 삭제 1\n\n" +
                            "🕐 빈시간 확인:\n" +
                            "• 빈시간 [날짜]\n" +
                            "• 예: 빈시간 오늘, 빈시간 내일\n\n" +
                            "❓ 기타:\n" +
                            "• 캘린더 도움말 (이 메시지)\n" +
                            "• 서버 상태 (서버 연결 확인)";
            
            msg.reply(helpMessage);
        }
        
        // ========== 서버 상태 확인 ==========
        else if (content === "서버 상태" || content === "캘린더 상태") {
            var data = { action: "health_check" };
            var result = callAPI("/api/health", data);
            
            if (result.success || result.status === "ok") {
                msg.reply("✅ Google Calendar 서버가 정상 작동 중입니다.");
            } else {
                msg.reply("❌ 서버 연결에 문제가 있습니다.\n" + (result.error || ""));
            }
        }
        
    } catch (e) {
        Log.e("[" + CONFIG.BOT_NAME + "] 메시지 처리 에러: " + e.message);
        msg.reply("❌ 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    }
});

// ====== 봇 초기화 ======
Log.i("[" + CONFIG.BOT_NAME + "] Google Calendar Bot 시작됨!");
Log.i("[" + CONFIG.BOT_NAME + "] 대상 방: " + CONFIG.TARGET_ROOMS.join(", "));
Log.i("[" + CONFIG.BOT_NAME + "] 서버 URL: " + CONFIG.SERVER_URL);

/**
 * ====== 사용법 요약 ======
 * 
 * 1. CONFIG 섹션에서 SERVER_URL과 TARGET_ROOMS 수정
 * 2. 메신저봇 앱에서 컴파일 및 실행
 * 3. 카톡방에서 명령어 테스트:
 *    - "일정" : 오늘 일정 보기
 *    - "일정 추가 회의 내일 3시" : 일정 추가
 *    - "캘린더 도움말" : 전체 사용법 보기
 * 
 * ====== 주의사항 ======
 * 
 * - FastAPI 서버가 먼저 실행되어야 함
 * - 서버의 Google Calendar MCP 설정 완료 필요
 * - 네트워크 연결 상태 확인
 * 
 * ====== 확장 가능한 기능 ======
 * 
 * - 일정 수정 기능
 * - 알림 설정
 * - 반복 일정
 * - 다른 캘린더 연동
 */