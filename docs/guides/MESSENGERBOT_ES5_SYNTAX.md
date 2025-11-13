# 📖 메신저봇 ES5 JavaScript 문법 가이드

## 🎯 왜 ES5를 써야 하나요?
메신저봇은 **Rhino 엔진**을 사용하며, 이는 ES5 (ECMAScript 5) 까지만 지원합니다.
최신 JavaScript (ES6+) 문법을 사용하면 오류가 발생합니다!

---

## ❌ 사용하면 안 되는 ES6+ 문법

### 1. 화살표 함수 (Arrow Function)
```javascript
// ❌ ES6 - 메신저봇에서 오류!
const greet = (name) => {
    return "안녕, " + name;
};

// ✅ ES5 - 메신저봇에서 작동
var greet = function(name) {
    return "안녕, " + name;
};
```

### 2. let과 const
```javascript
// ❌ ES6
let name = "철수";
const age = 20;

// ✅ ES5
var name = "철수";
var age = 20;  // 변경하지 않을 변수도 var 사용
```

### 3. 템플릿 리터럴 (Template Literals)
```javascript
// ❌ ES6
let message = `안녕하세요, ${name}님!`;

// ✅ ES5
var message = "안녕하세요, " + name + "님!";
```

### 4. 구조 분해 할당 (Destructuring)
```javascript
// ❌ ES6
const {room, content} = msg;

// ✅ ES5
var room = msg.room;
var content = msg.content;
```

### 5. 기본 매개변수 (Default Parameters)
```javascript
// ❌ ES6
function greet(name = "손님") {
    return "안녕, " + name;
}

// ✅ ES5
function greet(name) {
    name = name || "손님";  // 기본값 설정
    return "안녕, " + name;
}
```

### 6. 전개 연산자 (Spread Operator)
```javascript
// ❌ ES6
const arr2 = [...arr1, 4, 5];

// ✅ ES5
var arr2 = arr1.concat([4, 5]);
```

### 7. 클래스 (Class)
```javascript
// ❌ ES6
class Bot {
    constructor(name) {
        this.name = name;
    }
}

// ✅ ES5
function Bot(name) {
    this.name = name;
}
```

### 8. for...of 루프
```javascript
// ❌ ES6
for (let item of array) {
    console.log(item);
}

// ✅ ES5
for (var i = 0; i < array.length; i++) {
    console.log(array[i]);
}
```

---

## ✅ ES5에서 사용 가능한 유용한 기능들

### 1. 배열 메소드들
```javascript
// forEach - 사용 가능!
[1, 2, 3].forEach(function(item) {
    Log.d("숫자: " + item);
});

// map - 사용 가능!
var doubled = [1, 2, 3].map(function(x) {
    return x * 2;
});

// filter - 사용 가능!
var evens = [1, 2, 3, 4].filter(function(x) {
    return x % 2 === 0;
});

// reduce - 사용 가능!
var sum = [1, 2, 3].reduce(function(acc, cur) {
    return acc + cur;
}, 0);

// indexOf - 사용 가능!
var index = ["사과", "바나나"].indexOf("바나나");  // 1
```

### 2. JSON 처리
```javascript
// JSON.stringify - 사용 가능!
var jsonString = JSON.stringify({name: "철수", age: 20});

// JSON.parse - 사용 가능!
var obj = JSON.parse('{"name":"철수","age":20}');
```

### 3. Object 메소드들
```javascript
// Object.keys - 사용 가능!
var keys = Object.keys({a: 1, b: 2});  // ["a", "b"]

// hasOwnProperty - 사용 가능!
var obj = {name: "철수"};
if (obj.hasOwnProperty("name")) {
    Log.d("name 속성이 있음");
}
```

### 4. String 메소드들
```javascript
// trim - 사용 가능!
var cleaned = "  안녕  ".trim();  // "안녕"

// split - 사용 가능!
var parts = "사과,바나나,딸기".split(",");

// replace - 사용 가능!
var result = "Hello World".replace("World", "봇");

// substring, substr - 사용 가능!
var sub = "안녕하세요".substring(0, 2);  // "안녕"
```

---

## 💡 ES5 코딩 팁

### 1. 변수 선언
```javascript
// 모든 변수는 함수 시작 부분에 선언하는 것이 좋음
function processMessage(msg) {
    var content, room, author, result;  // 한 번에 선언
    
    content = msg.content;
    room = msg.room;
    author = msg.author.name;
    
    // 처리 로직...
}
```

### 2. 콜백 함수 패턴
```javascript
// 비동기 처리시 콜백 함수 사용
function fetchData(callback) {
    // API 호출 등...
    var result = "데이터";
    callback(result);
}

fetchData(function(data) {
    Log.d("받은 데이터: " + data);
});
```

### 3. 즉시 실행 함수 (IIFE)
```javascript
// 전역 변수 오염 방지
(function() {
    var privateVar = "비공개";
    
    // 봇 코드...
    bot.on("message", function(msg) {
        // ...
    });
})();
```

### 4. 객체 생성 패턴
```javascript
// 팩토리 패턴
function createBot(name) {
    return {
        name: name,
        greet: function() {
            return "안녕, 나는 " + this.name;
        }
    };
}

var myBot = createBot("루나");
```

### 5. 배열과 객체 복사
```javascript
// 배열 복사
var original = [1, 2, 3];
var copy = original.slice();  // 얕은 복사

// 객체 복사 (얕은 복사)
function copyObject(obj) {
    var copy = {};
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            copy[key] = obj[key];
        }
    }
    return copy;
}
```

---

## 🔧 메신저봇 특화 패턴

### 1. 안전한 속성 접근
```javascript
// 중첩된 객체 안전하게 접근
function safeGet(obj, path, defaultValue) {
    var keys = path.split('.');
    var result = obj;
    
    for (var i = 0; i < keys.length; i++) {
        if (result && result.hasOwnProperty(keys[i])) {
            result = result[keys[i]];
        } else {
            return defaultValue;
        }
    }
    
    return result;
}

// 사용 예
var name = safeGet(msg, 'author.name', '익명');
```

### 2. 명령어 파싱
```javascript
function parseCommand(content) {
    var parts = content.split(' ');
    return {
        command: parts[0],
        args: parts.slice(1)
    };
}

// 사용
var parsed = parseCommand("계산 1+1");
// {command: "계산", args: ["1+1"]}
```

### 3. 타이머 관리
```javascript
// setTimeout 대체
function delay(callback, ms) {
    new java.lang.Thread(function() {
        java.lang.Thread.sleep(ms);
        callback();
    }).start();
}

// 사용
delay(function() {
    bot.send(room, "3초 후 메시지");
}, 3000);
```

---

## ⚠️ 주의사항

### 1. strict mode 사용 불가
```javascript
// ❌ 메신저봇에서 작동 안함
"use strict";
```

### 2. Promise, async/await 사용 불가
```javascript
// ❌ ES6+ 기능
async function fetchData() {
    await someAsyncOperation();
}

// ✅ 콜백 패턴 사용
function fetchData(callback) {
    someAsyncOperation(function(result) {
        callback(result);
    });
}
```

### 3. Symbol, Map, Set 사용 불가
```javascript
// ❌ ES6+ 자료구조
const map = new Map();
const set = new Set();

// ✅ 객체와 배열 사용
var map = {};
var set = [];  // 중복 제거는 직접 구현
```

---

## 📚 ES5 참고 자료

### 유용한 polyfill 함수들
```javascript
// Array.prototype.includes 대체
function includes(array, item) {
    return array.indexOf(item) !== -1;
}

// String.prototype.startsWith 대체
function startsWith(str, search) {
    return str.substring(0, search.length) === search;
}

// String.prototype.endsWith 대체
function endsWith(str, search) {
    return str.substring(str.length - search.length) === search;
}

// Object.assign 대체 (얕은 복사)
function assign(target, source) {
    for (var key in source) {
        if (source.hasOwnProperty(key)) {
            target[key] = source[key];
        }
    }
    return target;
}
```

---

## 🎯 핵심 정리

1. **var만 사용** (let, const 금지)
2. **function 키워드 사용** (화살표 함수 금지)
3. **문자열 연결은 +** (템플릿 리터럴 금지)
4. **콜백 패턴 사용** (Promise, async/await 금지)
5. **ES5 배열 메소드 활용** (forEach, map, filter 등은 사용 가능!)

메신저봇 개발시 이 가이드를 참고하여 ES5 문법만 사용하세요! 💪