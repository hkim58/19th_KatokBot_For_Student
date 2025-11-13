# MessengerBot `log.json` 분석 가이드

메신저봇 폴더(예: `/storage/emulated/0/msgbot/Bots/TriggerSender/`)에 생성되는 `log.json`은 **하나의 JSON 배열**로 저장됩니다. 로그가 줄바꿈 없이 이어져 있기 때문에 단순히 `tail`을 사용하면 과거 항목만 보이고 최신 로그를 놓치기 쉽습니다. 아래 방법을 활용해 최신 로그를 정확히 확인하세요.

## 1. 끝에서부터 필요한 바이트만 보기

```bash
adb shell tail -c 4000 /storage/emulated/0/msgbot/Bots/TriggerSender/log.json
```

- `-c 4000`은 파일의 마지막 4000바이트만 표시합니다. 필요에 따라 숫자를 조정하세요.
- 한 줄로 출력되므로 필요한 부분만 복사해 다음 단계(jq/파이썬)로 넘기면 좋습니다.

## 2. `jq`로 JSON 배열 파싱

```bash
adb shell "cat /storage/emulated/0/msgbot/Bots/TriggerSender/log.json" \
  | jq '.[-10:]'
```

- 배열의 마지막 10개 항목만 보여줍니다.
- 각 항목은 `{ "a": "메시지", "b": 1, "c": "YYYY/MM/DD HH:MM:SS" }` 형태로 저장됩니다.

특정 필드만 보고 싶다면:

```bash
... | jq -r '.[-5:][] | "\(.c)  \(.a)"'
```

## 3. 파이썬 원라이너 사용

```bash
adb shell "cat /storage/emulated/0/msgbot/Bots/TriggerSender/log.json" \
  | python3 - <<'PY'
import json, sys
logs = json.load(sys.stdin)
for item in logs[-10:]:
    print(f"{item.get('c')}  {item.get('a')}")
PY
```

- `jq`가 설치되지 않았거나 복잡한 후처리가 필요할 때 활용합니다.

## 4. 편집기에서 보기

1. `adb pull`로 파일을 가져와 편집기(지원하는 경우)에 붙여 넣습니다.
2. JSON 포맷터(예: VS Code, jq, json.tool)로 줄바꿈을 적용해 가독성을 높입니다.

```bash
adb pull /storage/emulated/0/msgbot/Bots/TriggerSender/log.json .
python3 -m json.tool log.json > log_pretty.json
```

## 5. 트러블슈팅 팁

- **로그가 아예 없다면**: 스크립트가 실행되지 않았거나 폴더가 다를 수 있습니다. `bot.json`의 `main` 경로가 올바른지 확인하세요.
- **시간이 오래된 항목만 있다면**: 자동 배포 후 재컴파일이 되지 않은 상태일 수 있습니다. 메신저봇 앱에서 해당 스크립트를 다시 컴파일/실행하세요.
- **로그가 너무 커졌다면**: 분석 후 `adb shell "truncate -s 0 .../log.json"`으로 비워 새로 시작할 수 있습니다.

이 가이드를 AGENTS.md와 함께 유지해, 프로젝트 내 어디에서든 `log.json`을 안정적으로 확인할 수 있도록 하세요.
