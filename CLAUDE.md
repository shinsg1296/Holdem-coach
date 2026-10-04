# 홀덤의 바이블: 인수인계 (Claude Code용)

이 문서는 claude.ai 대화에서 만들던 프로젝트를 Claude Code로 넘기면서 쓴 인수인계서예요. Claude Code는 저장소를 열면 이 파일을 자동으로 읽어요.

## 0. 사용자와 일하는 방식
- 사용자: 에이닷 영어학원 대표("형"). 개발 지식이 어느 정도 있고, 직접 확인하면서 빠르게 반복하는 걸 좋아함.
- **한국어 해요체**로 답할 것. 아부 없이 직설적이고 근거 있는 피드백을 원함.
- 요청은 짧게 옴("바로 반영해줘", "~도 넣어줘"). 분명하면 바로 만들고, 비용이 크거나 해석이 갈리면 짧게 한 번만 물어볼 것.
- 결과는 **실제 폰에 설치되는 APK**로 확인함. 변경 후에는 항상 빌드와 릴리스까지 끝낼 것(4장).
- 사용자와 친구들만 쓰는 개인 앱. 헤즈업 상대 이름으로 실제 프로 이름을 쓰기로 사용자가 결정함(아래 6장).

## 1. 한 줄 요약
안드로이드 WebView 앱. 실제 게임 전체는 **HTML 파일 하나**(`app/src/main/assets/index.html`, 약 180KB)이고, Java는 감싸는 껍데기일 뿐이에요.
- 저장소: https://github.com/shinsg1296/holdem-coach (공개)
- 최신 APK: https://github.com/shinsg1296/holdem-coach/releases/latest/download/holdem-coach.apk
- claude.ai 아티팩트 버전: https://claude.ai/artifact/44xkFYu4zn25g56T4rf4xy
  - 같은 HTML이고, capabilities로 `sample`(Claude 질문)과 `db`(신고 저장)를 씀.

## 2. 소스의 기준 (가장 중요)
```
tools/holdem-live.html        ← 원본. 여기만 고칠 것 (claude.ai 아티팩트 버전과 같은 파일)
tools/build_web.py            ← 원본 → 앱용으로 변환
app/src/main/assets/index.html ← 생성물. 직접 고치지 말 것
```
- 빌드 명령: `python3 tools/build_web.py tools/holdem-live.html`
- `build_web.py`가 하는 일:
  - `<!doctype>`, head, `[hidden]` 리셋을 추가함. 아티팩트 호스트가 원래 넣어 주던 것들이에요.
  - `window.claude.use('sample')`를 사용자 API 키로 Anthropic API를 직접 호출하는 방식으로 바꿈. `anthropic-dangerous-direct-browser-access` 헤더를 쓰고, SSE 스트리밍을 함.
  - `window.claude.use('db')`(신고 저장)를 localStorage 저장 + 공유·복사로 바꿈.
  - "설정 · 신고 목록" 패널을 `<nav class="modes">` 앞에 넣음.
  - **패턴 문자열 치환 방식**이라, 원본에서 해당 문자열을 바꾸면 빌드가 "pattern not found"로 멈춰요. 그러면 `build_web.py`의 패턴도 같이 고칠 것.
- 아티팩트 버전에서만 쓰는 제약: 외부 스크립트는 cdnjs, jsdelivr 등만 허용되고, fetch와 WebSocket은 막혀 있어요. 그래서 온라인 대전은 앱에서만 동작해요(코드에서 host로 분기함).

## 3. 저장소 구조
```
app/src/main/java/com/adot/holdemcoach/MainActivity.java   WebView + WebViewAssetLoader(https://appassets.androidplatform.net/assets/)
                                                           JS 브리지 window.Android.share(text) / copy(text), onPause에서 saveSession()
app/src/main/assets/index.html        생성물
app/src/main/assets/firebase/*.js     Firebase compat SDK 10.12.2 (app/auth/database) 번들
app/holdem.keystore                   고정 서명키(비번 holdemcoach, alias holdem). 덮어쓰기 설치·데이터 유지용. 개인 사이드로드 전용
app/build.gradle.kts                  AGP 8.10.1, compileSdk 35, targetSdk 34(edge-to-edge 회피), minSdk 26, versionCode=GITHUB_RUN_NUMBER
.github/workflows/build-apk.yml       main 푸시 → assembleRelease → Releases(tag build-N)에 holdem-coach.apk 업로드
firebase/database.rules.json          RTDB 보안 규칙
firebase/SETUP.md                     사용자용 Firebase 설정 안내
tools/story/engine.js, build.js       스토리 1장 정답(EV) 사전 계산 → chapter1.json (HTML에 STORY 상수로 임베드됨)
tools/tests/*.py                      Playwright 회귀 테스트 (5장)
```

## 4. 빌드 · 릴리스
1. `tools/holdem-live.html` 수정
2. `python3 tools/build_web.py tools/holdem-live.html`
3. 테스트 (5장)
4. 커밋하고 `git push origin main` → GitHub Actions가 2~3분 안에 APK를 Releases에 올림
   - 확인: `gh api repos/shinsg1296/Holdem-coach/actions/runs?per_page=1`
   - 저장소의 실제 이름은 `Holdem-coach`(대문자 H)라서, 푸시하면 "moved" 경고가 나오는데 무시해도 됨
5. 사용자는 위 latest 링크에서 받아 덮어쓰기로 설치함
6. (선택) claude.ai 아티팩트도 같은 원본으로 다시 게시. Claude Code에선 보통 생략

로컬에서 APK를 빌드하려면 Android SDK가 있어야 해요. 예전 클라우드 세션은 구글 maven이 막혀 있어서 Actions에만 의존했어요.

커밋 메시지는 한국어로 쓰고, 끝에 Co-Authored-By 줄을 붙여 왔음.

## 5. 테스트 (`tools/tests`, Python Playwright + Chromium)
- 모든 스크립트는 `python3 tools/tests/X.py file:///.../index.html` 형식으로 실행.
- 첫 실행 안내 오버레이가 클릭을 가려서, 각 스크립트는 `add_init_script`로 `holdem-welcomed=1`을 미리 넣어요. 새 테스트를 만들 때도 꼭 넣을 것.
- 로컬 파일로 열면 `[hidden]` 리셋이 없어요. 원본 HTML을 테스트할 때는 `add_style_tag('[hidden]{display:none!important}')`를 넣음. 앱 빌드에는 리셋이 이미 포함돼 있음.
- 실전 탭 레이즈 패널의 `.size`는 숨겨진 채로 DOM에 남아 있어요. 다른 모드를 테스트할 때는 `#mpMode .raisepanel .size`처럼 범위를 지정할 것.

| 스크립트 | 확인하는 것 |
|---|---|
| `ux_test.py` | 실전 120+ 액션, 레이즈 패널, 올인 2번 탭, 실수하면 멈춤(다시 고르기/진행), 좌석 정보, 세션 요약 |
| `smoke_hu.py` | 헤즈업 1단계 대결 |
| `smoke_story.py` | 스토리 1장 전 스테이지 정답 플레이 + 보스 분기 |
| `tut_test.py` | 족보 생성기 검증(10종 × 200회), 튜토리얼 10레슨 완주 |
| `extra_test.py` | 첫 실행 안내, 실력 확인, 오늘의 문제(시드 고정 확인), 테마, 레이팅 |
| `mp_test.py URL N ITER` | **멀티 N명**을 같은 브라우저 컨텍스트의 탭으로 실행. 로컬 전송(BroadcastChannel)으로 칩 보존과 상대 카드 비노출을 확인 |
| `shot_table.py` | 2/5/8인 테이블 스크린샷과 가로 넘침 확인 |

예전엔 엔진만 Node로 따로 떼어 수백 핸드씩 돌리는 시뮬레이터(칩 보존, 2~8인, 헤즈업 착취율)도 썼어요. 그건 저장소에 없으니 필요하면 다시 만들 것. `<script>` 부분을 뽑고 DOM은 스텁으로 대체하면 됨.

## 6. 앱 구조 (원본 HTML의 `/* ===== … ===== */` 섹션 순서)
전역 상태는 `G`(실전·헤즈업 공용), `SV`/`LV`(스토리·레슨), `MP`/`MPH`(멀티)예요.

1. **constants / evaluator / equity**
   - `ev(cards)`: 5~7장을 정수 점수로 평가. 카테고리는 `>>20`, 랭크는 니블 단위로 들어 있음
   - `best5`, `describe`, 카드 정수는 `rank*4+suit`(suit 순서 ♠♥♦♣)
   - `ORDER`: 프리플랍 강도 순위
   - `RFI_TXT`: 오픈 범위. `RFIB[뒤에 남은 사람 수]`
2. **players / range model**: `oppModel(o)`가 액션으로 범위%를 정하고, 보드에서의 액션(벳·콜·체크)에 따라 `KEEP` 가중치를 줌
3. **coach**
   - `coach(p)`가 반환하는 것: 승률(MC 900회), 선택지별 EV(`evRaise`, 폴드 에퀴티 포함), 헤즈업이면 턴·리버 `playOut` 시뮬레이션
   - 보정 장치:
     - 최소 방어 빈도 보정은 블러프캐처에만 적용
     - 팟의 2배를 넘는 올인은 트리플·투페어 이상일 때만 추천
     - 기대값 차이가 작으면 수동적인 선택을 우선
   - 상황 구분: `kind`가 `rfi` / `sbvbb` / `bbopt` / `ev`
   - `grade()`가 good/ok/bad를 매기고, `tierLabel()`이 최선/좋음/부정확/실수/큰 실수(lv)를 매김
4. **bots**: `botDecide`. 성향 파라미터는 loose, aggr, station, bluff, trap, xr, over, shove. 헤즈업에선 `huAdjust`로 사용자 습관 착취 보정
5. **engine**: `playHand(ep)` → `bettingRound` → `finishHand`(사이드 팟 처리)
   - **`G.epoch`로 중단 처리**: `abortHand()`가 epoch를 올리면 진행 중이던 루프가 `throw 'abort'`로 빠짐
   - `next()`로만 시작할 것
6. **hero turn**
   - `setupControls`, `openRaise`/`closeRaise`, `heroAct`
   - 올인은 `G.allinArmed`로 두 번 눌러야 확정
   - 실수하면 멈춤: `G.paused` → `retryAct`/`continueAct` → `commitAct`
7. **render**: 타원 테이블 좌표 계산은 CX/CY/RX/RY. 칩, D 버튼, 보드 겹침 회피 규칙이 있음
8. **discussion with Claude**: 결정마다 컨텍스트를 만드는 `buildCtx`, 코치 페르소나는 `RULES`
9. **report**: "이 해설이 이상해요" 신고. 아티팩트에선 db의 `reports`, 앱에선 localStorage에 저장
10. **session persistence**: `SAVE_KEY`, `G.away`(헤즈업 중엔 실전 세션 저장을 막음)
11. **UX layer**: verdict tier, decLog, 핸드 기록, 세션 요약·새는 곳(leakTags), 올인 승률, 좌석 정보(VPIP/PFR), 칩 수집 애니메이션
12. **heads-up ladder**
    - 상대: 머니메이커 → 헬무스 → 거스 핸슨 → 조니 챈 → 톰 드완 → 필 아이비(보스)
    - 설명엔 실제 경력과 별명만 쓰고, 지어낸 대사는 넣지 않음. 화면에 "실제 플레이와 다름"을 표시함
    - 읽기: 사용자가 볼 수 있는 정보(액션, 쇼다운 카드)만으로 통계를 냄. 보스는 평생 기록(`READ_KEY`)까지 씀
    - 블라인드는 10핸드마다 상승. 별점은 판단 점수 기준
13. **story**: 1장 10스테이지, 정답은 사전 계산. 보스는 2003 WSOP 머니메이커 vs 파르하(출처 PokerNews)
14. **tutorial**: 10레슨 + 족보 문제 생성기(`GEN.rank2/name5/best7/winner`). 무작위 생성은 `Math.random`만 쓰기 때문에 `withSeed`로 고정할 수 있음
15. **daily / placement / rating / theme / welcome**
16. **multiplayer** (7장)

### localStorage 키
| 키 | 내용 |
|---|---|
| `holdem-live-session-v1` | 실전 세션 |
| `holdem-np` | 인원 |
| `holdem-mode` | 마지막 탭 |
| `holdem-story-v1` | 스토리·튜토리얼 별 (t1..t10, 1..10) |
| `holdem-hu-v1` | 헤즈업 별 |
| `holdem-read-v1` | 헤즈업 평생 읽기 통계 |
| `holdem-rating-v1` | 판단 레이팅 |
| `holdem-daily-v1` | 오늘의 문제 기록 |
| `holdem-theme` | 테이블 테마 |
| `holdem-detail`, `holdem-learnpause` | 설정 |
| `holdem-welcomed` | 첫 실행 안내 표시 여부 |
| `holdem-fbcfg` | Firebase 설정 |
| `holdem-mpname`, `holdem-mproom` | 멀티 이름·방 |
| `apiKey`, `model` | 앱의 Claude 질문 기능 |
| `holdem-reports-v1` | 앱 신고 목록 |

## 7. 친구와 온라인 대전: 현재 상태와 다음 할 일
- **구조**
  - 방장 폰이 딜러: `mpStartHand`/`mpApply`/`mpSettle`과 500ms마다 도는 `mpHostTick`이 제한 시간, 올인 런아웃, 다음 핸드, 리바인을 처리함
  - 참가자는 `rooms/<code>/actions`에 액션을 push하기만 함
  - 공개 상태는 `rooms/<code>/state`(방장만 쓰기)에 올라감. 홀카드는 `hands/<code>/<uid>`에 있고 본인만 읽을 수 있음(rules)
  - 방장이 핸드 도중에 다시 들어오면 그 핸드는 무효 처리하고 칩을 돌려줌
- **전송 계층**: `makeFirebaseNet(cfg)`(익명 로그인, RTDB) / `makeLocalNet()`(테스트용, `{"local":true}`)
- **⚠️ 실제 Firebase 연결은 한 번도 테스트하지 않았음.** 로컬 전송으로만 검증했어요.
- **다음 할 일**
  1. 사용자의 Firebase 프로젝트 만들기. 사용자가 Claude Code에게 직접 맡길 수도 있음. 절차는 `firebase/SETUP.md`
     - 순서: 익명 Auth → RTDB(asia-southeast1, 잠금 모드) → `database.rules.json` 게시 → 웹 앱 등록 → firebaseConfig 받기
  2. 원본 HTML의 multiplayer 섹션 위에 `const FB_DEFAULT={...firebaseConfig...};`를 추가. `mpCfg()`가 기본값으로 읽음. 그다음 빌드와 릴리스
  3. 실제 기기 2대로 접속 테스트. 볼 것: 익명 로그인, WebSocket, 보안 규칙 거부 여부(특히 actions 삭제와 hands 쓰기), 방장 앱이 백그라운드로 갔을 때 멈추는 문제
  4. 남은 개선 후보: 방장 이전(host migration), 빈자리 AI 채우기, 멀티 중 코치 해설

## 8. 알려진 한계 · 주의
- 코치 엔진은 근사 모델이에요. 멀티웨이는 쇼다운까지 간다고 단순화했고, 상대 성향은 코치 계산에 쓰지 않음(헤즈업 상대가 변칙적이면 해설이 정답과 다를 수 있음)
- 실전 모드 EV는 몬테카를로라서 같은 상황에서도 조금씩 흔들려요. 스토리는 사전 계산이라 고정됨
- 사용자가 신고한 엔진 버그 3건(SB 림프 판정, AA 오픈 올인 채점, 멀티웨이 올인 추천)은 v2.1에서 수정함
- 앱의 "Claude에게 질문"은 사용자 API 키가 있어야 함. 기본 모델은 `claude-sonnet-5-5`
- 실제 포커 앱 UI 조사 결과(레이즈 패널, 5단계 평가, 세션 요약 등)는 이미 반영함
  - 미반영: 행동 타이머(실전 모드엔 의도적으로 안 넣음), 아바타·애니메이션 추가 다듬기

## 9. 백로그 (사용자가 언급했거나 제안했던 것)
- 스토리 2장 이후(밸류 벳·블러프 심화), 실제 유명 핸드 20~30개는 검증한 뒤 보스로 추가
  - 100스테이지까지 늘리는 것이 사용자의 목표
- 처음 만든 "즉답 트레이너"(프리플랍·팟 오즈·쇼다운 드릴)를 앱 탭으로 넣을지는 미결정
- 실전 모드 AI 이름 변경 여부(지금은 바위·상어·불도저·낚시꾼·여우·거북·도박꾼)
- 플레이스토어 출시: 이름이 "홀덤의 바이블"인 앱은 웹 검색으로는 안 보였지만, 스토어 안에서 직접 확인하진 못함
