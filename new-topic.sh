#!/usr/bin/env bash
#
# 새 학습 주제 폴더 생성
#
#   ./new-topic.sh <번호>                                  로드맵에 있는 주제 (권장)
#   ./new-topic.sh <번호> <슬러그> <타입> "<주제명>"          로드맵에 없는 주제
#   ./new-topic.sh list                                    아직 시작 안 한 주제 목록
#
set -euo pipefail

cd "$(dirname "$0")"

PROGRESS="PROGRESS.md"

usage() {
  cat <<'EOF'
사용법:

  ./new-topic.sh <번호>
      PROGRESS.md 에 있는 주제. 슬러그·타입·주제명을 자동으로 채운다.
      예) ./new-topic.sh 32

  ./new-topic.sh <번호> <슬러그> <타입> "<주제명>"
      로드맵에 없는 주제를 직접 추가할 때.
      예) ./new-topic.sh 37 view-transitions experiment "View Transitions API"

  ./new-topic.sh list
      아직 시작하지 않은 주제 목록을 본다.

타입 고르는 기준:
  재현해서 수치나 화면으로 확인할 수 있는가?
    있다 -> experiment (성능, 브라우저 런타임, 언어 동작)
    없다 -> concept    (설계, 경계, 상태 소유권, API, 도메인)
EOF
}

# PROGRESS.md 표에서 번호로 한 행을 찾아 "주제명<TAB>슬러그<TAB>타입" 출력
lookup() {
  awk -F'|' -v want="$1" '
    /^\| *[0-9]+ *\|/ {
      num = $2; gsub(/ /, "", num)
      if (num != want) next
      topic = $3; slug = $4; type = $5
      gsub(/^ +| +$/, "", topic)
      gsub(/^ +| +$|`/, "", slug)
      gsub(/^ +| +$/, "", type)
      print topic "\t" slug "\t" type
      exit
    }
  ' "$PROGRESS"
}

# ── list ─────────────────────────────────────────────────────
if [ "${1:-}" = "list" ]; then
  echo "아직 시작하지 않은 주제:"
  echo
  awk -F'|' '
    /^## 티어|^## 성능/ { section = $0; sub(/^## /, "", section) }
    /^\| *[0-9]+ *\|/ {
      num = $2; topic = $3; slug = $4; type = $5; status = $6
      gsub(/ /, "", num); gsub(/ /, "", status)
      gsub(/^ +| +$/, "", topic); gsub(/^ +| +$|`/, "", slug); gsub(/^ +| +$/, "", type)
      if (status != "⬜") next
      if (section != prev) { print "  [" section "]"; prev = section }
      printf "    %-3s %-24s %-11s %s\n", num, slug, type, topic
    }
  ' "$PROGRESS"
  echo
  echo "시작하려면: ./new-topic.sh <번호>"
  exit 0
fi

if [ $# -eq 0 ]; then
  usage
  exit 1
fi

# ── 인자 해석 ────────────────────────────────────────────────
NUM_RAW="$1"

if ! [[ "$NUM_RAW" =~ ^[0-9]+$ ]]; then
  echo "오류: 번호는 숫자여야 합니다 (입력값: $NUM_RAW)" >&2
  echo >&2
  usage >&2
  exit 1
fi

if [ $# -eq 1 ]; then
  # 로드맵에서 조회
  ROW=$(lookup "$NUM_RAW")
  if [ -z "$ROW" ]; then
    echo "오류: PROGRESS.md 에 ${NUM_RAW}번 주제가 없습니다." >&2
    echo >&2
    echo "로드맵 밖의 주제라면 네 개를 직접 지정하세요:" >&2
    echo "  ./new-topic.sh ${NUM_RAW} <슬러그> <experiment|concept> \"<주제명>\"" >&2
    echo >&2
    echo "목록을 보려면: ./new-topic.sh list" >&2
    exit 1
  fi
  TOPIC=$(printf '%s' "$ROW" | cut -f1)
  SLUG=$(printf '%s' "$ROW" | cut -f2)
  TYPE=$(printf '%s' "$ROW" | cut -f3)
  FROM_ROADMAP=1
elif [ $# -eq 4 ]; then
  SLUG="$2"
  TYPE="$3"
  TOPIC="$4"
  FROM_ROADMAP=0
else
  echo "오류: 인자는 1개(번호만) 또는 4개여야 합니다." >&2
  echo >&2
  usage >&2
  exit 1
fi

NUM=$(printf '%02d' "$NUM_RAW")

if ! [[ "$SLUG" =~ ^[a-z0-9-]+$ ]]; then
  echo "오류: 슬러그는 영소문자·숫자·하이픈만 사용합니다 (입력값: $SLUG)" >&2
  exit 1
fi

case "$TYPE" in
  experiment|concept) ;;
  *)
    echo "오류: 타입은 experiment 또는 concept 입니다 (입력값: $TYPE)" >&2
    exit 1
    ;;
esac

TEMPLATE="_template-${TYPE}"
DEST="${NUM}-${SLUG}"

[ -d "$TEMPLATE" ] || { echo "오류: 템플릿 폴더가 없습니다: $TEMPLATE" >&2; exit 1; }
[ -e "$DEST" ] && { echo "오류: 이미 존재합니다: $DEST" >&2; exit 1; }

cp -R "$TEMPLATE" "$DEST"

# sed 치환에서 특수문자로 해석되는 문자 이스케이프
esc() { printf '%s' "$1" | sed 's/[&|\\]/\\&/g'; }

TOPIC_ESC=$(esc "$TOPIC")
DATE_ESC=$(date '+%Y-%m-%d')

find "$DEST" -type f \( -name '*.md' -o -name '*.html' \) -print0 |
  while IFS= read -r -d '' f; do
    sed -i '' "s|{{TOPIC}}|${TOPIC_ESC}|g; s|{{DATE}}|${DATE_ESC}|g" "$f"
  done

echo "생성 완료: ${DEST}/  (${TYPE})"
echo
echo "  주제: ${TOPIC}"
if [ "$FROM_ROADMAP" = "1" ]; then
  echo "  출처: PROGRESS.md ${NUM_RAW}번"
else
  echo "  출처: 직접 지정 (로드맵 밖)"
  echo
  echo "  ※ 계속 다룰 주제라면 PROGRESS.md 표에도 추가해두세요."
fi
echo
echo "다음 순서:"
echo "  1. ${DEST}/README.md 의 '이 주제를 고른 이유' 를 채운다"
if [ "$FROM_ROADMAP" = "1" ]; then
  echo "  2. docs/프론트엔드-기반지식-학습맵.md 에서 ${NUM_RAW}번 '학습 지도'를 00-MAP.md 로 옮긴다"
  echo "     같은 주제의 '더 깊게 파면 좋은 부분'은 00-MAP.md 의 '파고들 후보'로"
else
  echo "  2. 00-MAP.md 의 프롬프트를 AI에게 던진다 (얇게! 두 문장 이내)"
fi
echo "  3. 바로 01-QUESTIONS.md 로 넘어가 스스로 설명해본다"
echo
echo "PROGRESS.md 의 상태를 🟡 로, 폴더 칸을 ${DEST} 로 갱신할 것."
