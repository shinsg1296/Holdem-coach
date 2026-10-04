# 홀덤의 바이블 (안드로이드)

## 폰에 설치 (GitHub 자동 빌드)
main에 올라갈 때마다 GitHub가 APK를 만들어 Releases에 올립니다.
폰 브라우저에서 아래 주소를 열면 최신 APK가 바로 받아집니다.

https://github.com/shinsg1296/holdem-coach/releases/latest/download/holdem-coach.apk

처음 설치할 때 "출처를 알 수 없는 앱 설치"를 허용해야 합니다. 같은 키로 서명하므로 새 버전은 덮어서 설치되고 저장된 게임도 유지됩니다.

## PC에서 직접 빌드 (선택)

1. Android Studio에서 **Open** → 이 `HoldemCoach` 폴더를 선택합니다.
2. 처음 열면 Gradle 동기화가 자동으로 진행됩니다(인터넷 필요, 몇 분 걸릴 수 있어요).
3. 메뉴 **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.
4. 완료 알림의 **locate**를 누르면 `app/build/outputs/apk/debug/app-debug.apk`가 나옵니다.
5. 이 파일을 폰으로 옮겨 설치합니다(“출처를 알 수 없는 앱” 허용 필요).
   폰을 USB로 연결했다면 Android Studio의 ▶ Run 버튼으로 바로 설치해도 됩니다.

## 앱 안에서
- 위쪽 **인원**에서 2~8명을 고를 수 있습니다. 바꾸면 새 세션이 시작됩니다.
- **설정 · 신고 목록**에서 Anthropic API 키를 넣으면 해설에 대해 Claude에게 질문할 수 있습니다.
  키는 https://console.anthropic.com 에서 발급하며, 사용료는 Claude 구독과 별도로 청구됩니다.
  키가 없어도 게임과 자동 채점·해설은 모두 작동합니다(오프라인 가능).
- 이상한 해설은 **이 해설이 이상해요**로 신고 → 설정의 **공유/복사**로 Claude 대화창에 보내면 엔진을 고칠 수 있습니다.

## 게임 화면 수정 후 다시 반영하기
`tools/holdem-live.html`(claude.ai 버전)을 고친 뒤:
```
python3 tools/build_web.py tools/holdem-live.html
```
`app/src/main/assets/index.html`이 다시 만들어집니다.
