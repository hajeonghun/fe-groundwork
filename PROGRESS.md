# 진행 현황

주제 목록은 [`docs/프론트엔드-기반지식-학습맵.md`](docs/프론트엔드-기반지식-학습맵.md) 기준.

**상태 표기** — ⬜ 시작 전 / 🟡 진행 중 / ✅ 완료 (완료 기준은 각 폴더 README 참고)

**한 번에 하나만 🟡 로 둔다.** 여러 주제를 동시에 벌이면 전부 미완으로 남는다.

> ⚠️ **이 표는 `new-topic.sh`가 읽는 데이터이기도 하다.**
> `./new-topic.sh 32` 처럼 번호만 넣으면 여기서 슬러그·타입·주제명을 찾아 폴더를 만든다.
> **표의 열 구조(`| # | 주제 | 슬러그 | 타입 | 상태 | 폴더 |`)를 바꾸면 스크립트가 깨진다.**
> 주제를 추가할 때는 기존 행과 같은 형식으로 넣는다.

---

## 지금 하는 것

<!-- 주제 하나만. 시작일과 목표 완료일을 적는다. -->

| 주제 | 시작일 | 목표 |
|------|--------|------|
|  |  |  |

---

## 티어 1 (우선)

| # | 주제 | 슬러그 | 타입 | 상태 | 폴더 |
|---|------|--------|------|------|------|
| 1 | 렌더링 파이프라인 / 컴포지팅 | `rendering-pipeline` | experiment | ⬜ |  |
| 2 | 이벤트 루프, 태스크 vs 마이크로태스크 | `event-loop` | experiment | ⬜ |  |
| 3 | 메모리 관리와 누수 패턴 | `memory-management` | experiment | ⬜ |  |
| 6 | HTTP/2·3, 캐싱 전략, CDN | `http-caching` | experiment | ⬜ |  |
| 7 | 브라우저 보안 모델 | `browser-security` | experiment | ⬜ |  |
| 8 | 인증과 세션 | `auth-session` | concept | ⬜ |  |
| 10 | JavaScript 코어 | `javascript-core` | experiment | ⬜ |  |
| 11 | 비동기 프로그래밍 패턴 | `async-patterns` | experiment | ⬜ |  |
| 12 | TypeScript 타입 시스템 | `typescript-types` | experiment | ⬜ |  |
| 14 | CSS 레이아웃 엔진 | `css-layout` | experiment | ⬜ |  |
| 23 | 상태의 소유권 | `state-ownership` | concept | ⬜ |  |
| 27 | 디버깅·프로파일링 방법론 | `debugging-profiling` | experiment | ⬜ |  |
| 31 | 도메인 지식 | `domain-knowledge` | concept | ⬜ |  |
| 32 | 성능 지표와 Core Web Vitals | `web-vitals` | experiment | ⬜ |  |
| 33 | 이미지와 미디어 최적화 | `images-media` | experiment | ⬜ |  |

## 티어 2

| # | 주제 | 슬러그 | 타입 | 상태 | 폴더 |
|---|------|--------|------|------|------|
| 4 | 브라우저 저장소 | `browser-storage` | experiment | ⬜ |  |
| 5 | Web Worker와 오프스레드 처리 | `web-worker` | experiment | ⬜ |  |
| 13 | 불변성과 참조 동등성 | `immutability` | experiment | ⬜ |  |
| 15 | 접근성 | `accessibility` | experiment | ⬜ |  |
| 16 | 폼과 입력 처리 | `forms-input` | experiment | ⬜ |  |
| 18 | 모듈 시스템과 번들링 | `modules-bundling` | experiment | ⬜ |  |
| 20 | 배포 전략 | `deployment` | concept | ⬜ |  |
| 21 | 관측성 | `observability` | concept | ⬜ |  |
| 22 | 렌더링 전략 | `rendering-strategy` | concept | ⬜ |  |
| 24 | 모듈 경계와 의존성 방향 | `module-boundaries` | concept | ⬜ |  |
| 25 | 컴포넌트 설계와 합성 | `component-design` | concept | ⬜ |  |
| 26 | 테스트 전략 | `testing-strategy` | concept | ⬜ |  |
| 29 | 시스템 설계 기초 | `system-design` | concept | ⬜ |  |
| 30 | API 설계와 데이터 모델링 | `api-design` | concept | ⬜ |  |
| 34 | 폰트 로딩 최적화 | `font-loading` | experiment | ⬜ |  |
| 35 | 서드파티 스크립트 관리 | `third-party-scripts` | experiment | ⬜ |  |
| 36 | 성능 예산과 회귀 방지 | `perf-budget` | concept | ⬜ |  |

## 티어 3

| # | 주제 | 슬러그 | 타입 | 상태 | 폴더 |
|---|------|--------|------|------|------|
| 9 | 실시간 통신 | `realtime` | concept | ⬜ |  |
| 17 | 국제화와 로케일 | `i18n` | experiment | ⬜ |  |
| 19 | 트랜스파일과 브라우저 호환성 | `transpile-compat` | experiment | ⬜ |  |
| 28 | 정적 분석과 코드 리뷰 | `static-analysis` | concept | ⬜ |  |

---

## 성능 특화 트랙

성능을 주 무기로 삼는다면 이 순서로 (학습맵 부록 C).

**1단계 측정 기반** → 27 · 32 · 21
**2단계 로딩** → 33 · 6 · 18 · 34 · 35
**3단계 런타임** → 1 · 2 · 13 · 3 · 5
**4단계 체계화** → 36 · 22 · 29

> 1단계를 건너뛰고 최적화부터 하는 것이 가장 흔한 실패다.
> 측정 없는 최적화는 운에 맡기는 것이고, 효과가 있었는지도 알 수 없다.

### 첫 한 달 (학습맵 부록 C)

- [ ] `web-vitals`로 실사용자 지표 수집 시작 *(데이터가 쌓이는 데 시간이 걸리니 가장 먼저)*
- [ ] 주요 업무 화면 3개에 자체 지표 정의 (조회 클릭 → 그리드 렌더 완료)
- [ ] 가장 느린 화면의 LCP를 4단계로 분해
- [ ] 표준 루프대로 하나만 개선하고 전후 수치 기록
- [ ] 번들 크기 상한을 CI에 추가

---

## 타입 분류에 대해

위 표의 타입은 **권장일 뿐 고정이 아니다.** 판단 기준은 하나다.

> 재현해서 수치나 화면으로 확인할 수 있는가?

애매한 주제가 여럿 있다. 예를 들어 **7번 보안**은 CSP 위반이나 CORS preflight를 재현할 수 있어 experiment로 뒀지만, 인증 흐름 설계 쪽으로 파고들면 concept이 맞다.
**21번 관측성**도 도구 붙이는 건 실험이지만 무엇을 측정할지 정하는 건 판단이다.

**형식에 맞추려고 억지 데모를 만들지 않는다.**
시작한 뒤 안 맞으면 `03-MEASUREMENTS.md`를 `03-CASES.md`로 바꾸면 된다. 그 반대도 마찬가지다.

---

## 회고

<!-- 주제 3~4개를 마칠 때마다 여기에 적는다.
     무엇이 잘 됐고, 어떤 단계에서 자꾸 막히는지.
     이 프로젝트 자체의 구조도 그때 손본다. -->

### (날짜)

- 잘 된 것:
- 자꾸 건너뛰게 되는 단계:
- 구조에서 바꿀 것:
