
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# -----------------------------
# 1. 기본 화면 설정
# -----------------------------
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)

# KOBIS 일별 박스오피스 공식 API 주소
API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/"
    "webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
)


# -----------------------------
# 2. 공통 안내 화면
# -----------------------------
def show_troubleshooting(title: str, details: str = "") -> None:
    """오류가 발생했을 때 원인과 확인할 내용을 한국어로 보여 줍니다."""
    st.error(title)

    if details:
        st.write(details)

    st.markdown(
        "**확인해 보세요**\n"
        "- Streamlit Cloud의 Settings → Secrets에 "
        "`KOBIS_KEY`가 등록되어 있는지 확인하세요.\n"
        "- 인증키 앞뒤에 공백이 없는지, 발급받은 키가 유효한지 "
        "확인하세요.\n"
        "- KOBIS에서 해당 날짜의 박스오피스 자료가 아직 제공되지 "
        "않았다면 잠시 후 다시 실행하세요.\n"
        "- 앱이 인터넷에 연결되어 있고 KOBIS API에 접속할 수 "
        "있는지 확인하세요."
    )


# -----------------------------
# 3. 한국 시간 기준으로 어제 날짜 구하기
# -----------------------------
# 서버의 시간대에 의존하지 않도록 한국 시간대를 직접 지정합니다.
now_in_korea = datetime.now(ZoneInfo("Asia/Seoul"))
yesterday = now_in_korea.date() - timedelta(days=1)

# API는 YYYYMMDD 형식의 여덟 자리 날짜를 사용합니다.
target_date = yesterday.strftime("%Y%m%d")
display_date = yesterday.strftime("%Y년 %m월 %d일")


# -----------------------------
# 4. 화면 제목
# -----------------------------
st.title("🎬 어제의 박스오피스")
st.caption(
    f"KOBIS 일별 박스오피스 · 조회 기준일: "
    f"{display_date} (한국 시간)"
)
st.divider()


# -----------------------------
# 5. 비밀 금고에서 인증키 읽기
# -----------------------------
# 인증키를 코드에 직접 적지 않습니다.
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    show_troubleshooting(
        "KOBIS 인증키를 찾을 수 없습니다.",
        "Streamlit Cloud의 Secrets에 KOBIS_KEY라는 이름으로 "
        "인증키를 등록해야 합니다.\n\n"
        '예: KOBIS_KEY = "발급받은_인증키"',
    )
    st.stop()

if not isinstance(api_key, str) or not api_key.strip():
    show_troubleshooting(
        "KOBIS 인증키가 비어 있습니다.",
        "Secrets에 등록한 KOBIS_KEY 값이 비어 있지 않은지 "
        "확인하세요.",
    )
    st.stop()


# -----------------------------
# 6. KOBIS API에 데이터 요청
# -----------------------------
# timeout을 설정하여 응답이 오래 걸릴 때 무한정 기다리지 않습니다.
try:
    response = requests.get(
        API_URL,
        params={
            "key": api_key.strip(),
            "targetDt": target_date,
        },
        timeout=20,
    )

except requests.exceptions.Timeout:
    show_troubleshooting(
        "KOBIS API 응답 시간이 초과되었습니다.",
        "요청을 20초 안에 완료하지 못했습니다. "
        "잠시 후 다시 실행해 보세요.",
    )
    st.stop()

except requests.exceptions.RequestException as exc:
    show_troubleshooting(
        "KOBIS API에 연결하지 못했습니다.",
        f"연결 오류 내용: {exc}",
    )
    st.stop()


# HTTP 상태 코드가 200이 아니면 오류로 처리합니다.
if response.status_code != 200:
    show_troubleshooting(
        f"KOBIS API 요청에 실패했습니다. "
        f"(HTTP {response.status_code})",
        "KOBIS API 주소와 네트워크 연결 상태를 확인하세요.",
    )
    st.stop()


# -----------------------------
# 7. 응답 내용과 오류 정보 확인
# -----------------------------
# HTTP 상태가 200이어도 인증키가 틀리면 faultInfo가 올 수 있습니다.
try:
    payload = response.json()

except ValueError:
    show_troubleshooting(
        "KOBIS 응답을 JSON 형식으로 읽을 수 없습니다.",
        "API 응답 내용이 예상한 형식인지 확인한 뒤 다시 시도하세요.",
    )
    st.stop()

if not isinstance(payload, dict):
    show_troubleshooting(
        "KOBIS 응답 형식이 예상과 다릅니다.",
        "응답에 boxOfficeResult 정보가 있는지 확인하세요.",
    )
    st.stop()


# 잘못된 인증키 등의 경우 faultInfo에 오류 정보가 들어올 수 있습니다.
fault_info = payload.get("faultInfo")

if fault_info:
    if isinstance(fault_info, dict):
        error_code = fault_info.get("errorCode", "코드 없음")
        error_message = fault_info.get(
            "errorMessage",
            "오류 메시지 없음",
        )
        error_details = (
            f"KOBIS 오류 코드: {error_code}\n\n"
            f"KOBIS 오류 메시지: {error_message}"
        )
    else:
        error_details = f"KOBIS 오류 정보: {fault_info}"

    show_troubleshooting(
        "KOBIS가 오류 정보를 반환했습니다.",
        error_details,
    )
    st.stop()


# -----------------------------
# 8. 영화 목록 확인
# -----------------------------
box_office_result = payload.get("boxOfficeResult")

if not isinstance(box_office_result, dict):
    show_troubleshooting(
        "응답에 박스오피스 결과가 없습니다.",
        "KOBIS 응답에 boxOfficeResult가 포함되어 있는지 확인하세요.",
    )
    st.stop()

movie_list = box_office_result.get("dailyBoxOfficeList")

if not isinstance(movie_list, list) or len(movie_list) == 0:
    show_troubleshooting(
        f"{display_date} 영화 목록이 비어 있습니다.",
        "해당 날짜 자료가 아직 집계·공개되지 않았거나 "
        "KOBIS 응답에 영화 목록이 없는 상태입니다.",
    )
    st.stop()


# -----------------------------
# 9. 표와 그래프에 사용할 데이터 정리
# -----------------------------
# API는 숫자도 문자열로 돌려주므로 숫자 형식으로 변환합니다.
df = pd.DataFrame(movie_list)

# 필요한 열이 빠진 응답에서도 오류를 줄이도록 열을 준비합니다.
required_columns = [
    "rank",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

for column in required_columns:
    if column not in df.columns:
        df[column] = ""

# 순위·관객수·누적관객·스크린수를 숫자로 변환합니다.
numeric_columns = [
    "rank",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

for column in numeric_columns:
    df[column] = (
        pd.to_numeric(df[column], errors="coerce")
        .fillna(0)
        .astype(int)
    )

# 영화명과 개봉일이 비어 있으면 안내 문구를 표시합니다.
df["movieNm"] = (
    df["movieNm"]
    .fillna("")
    .astype(str)
    .replace("", "영화명 정보 없음")
)

df["openDt"] = (
    df["openDt"]
    .fillna("")
    .astype(str)
    .replace("", "정보 없음")
)

if df.empty:
    show_troubleshooting(
        f"{display_date} 영화 목록이 비어 있습니다.",
        "KOBIS에서 해당 날짜의 자료를 제공하는지 확인하세요.",
    )
    st.stop()


# -----------------------------
# 10. 1위 영화 지표 카드 3개
# -----------------------------
# API의 순위를 기준으로 정렬한 뒤 첫 번째 영화를 1위로 표시합니다.
df = df.sort_values("rank", ascending=True).reset_index(drop=True)
leader = df.iloc[0]

st.subheader(f"🏆 1위 영화: {leader['movieNm']}")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "일일 관객수",
        f"{int(leader['audiCnt']):,}명",
    )

with metric2:
    st.metric(
        "누적 관객수",
        f"{int(leader['audiAcc']):,}명",
    )

with metric3:
    st.metric(
        "스크린 수",
        f"{int(leader['scrnCnt']):,}개",
    )

st.divider()


# -----------------------------
# 11. 관객수 상위 5편 막대그래프
# -----------------------------
st.subheader("📊 관객수 상위 5편")

# 순위가 아닌 실제 일일 관객수를 기준으로 상위 다섯 편을 고릅니다.
top5 = df.sort_values(
    "audiCnt",
    ascending=False,
).head(5).copy()

chart_df = (
    top5.set_index("movieNm")[["audiCnt"]]
    .rename(columns={"audiCnt": "관객수"})
)

if not top5.empty:
    st.bar_chart(chart_df)
else:
    st.info("그래프로 표시할 영화 데이터가 없습니다.")

st.divider()


# -----------------------------
# 12. 전체 영화 목록 표
# -----------------------------
st.subheader("📋 일별 박스오피스 전체 목록")

# 요청한 항목만 한국어 열 이름으로 보여 줍니다.
table_df = df[
    [
        "rank",
        "movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
    ]
].rename(
    columns={
        "rank": "순위",
        "movieNm": "영화명",
        "openDt": "개봉일",
        "audiCnt": "관객수",
        "audiAcc": "누적관객",
        "scrnCnt": "스크린수",
    }
)

# 숫자에 천 단위 쉼표와 단위를 붙여 읽기 쉽게 표시합니다.
formatted_table = table_df.style.format(
    {
        "순위": "{:.0f}위",
        "관객수": "{:,.0f}명",
        "누적관객": "{:,.0f}명",
        "스크린수": "{:,.0f}개",
    }
)

st.dataframe(
    formatted_table,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "자료 출처: 영화관입장권통합전산망(KOBIS) "
    "일별 박스오피스 API"
)
