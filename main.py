
import html
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st


# ============================================================
# 1. 앱 기본 설정과 KOBIS API 주소
# ============================================================
st.set_page_config(
    page_title="팝아트 박스오피스",
    page_icon="🎬",
    layout="wide",
)

BOXOFFICE_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)
MOVIE_INFO_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "movie/searchMovieInfo.json"
)

# 엔디 워홀의 팝아트에서 영감을 얻어 강렬한 색상과 망점 무늬를 만듭니다.
st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(circle, rgba(25,25,25,.10) 1.2px, transparent 1.5px) 0 0 / 12px 12px,
          linear-gradient(135deg, #fff4c2 0%, #fff9e8 54%, #ffe6ec 100%);
        color: #171717;
    }
    .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #171717 !important;
        font-weight: 900 !important;
    }
    h1 { letter-spacing: -1.2px; }

    [data-testid="stMetric"] {
        background: #fffdf4;
        border: 3px solid #171717;
        border-radius: 5px;
        padding: 17px 18px;
        box-shadow: 6px 6px 0 #171717;
    }
    [data-testid="stMetricLabel"] { font-weight: 800; }
    [data-testid="stMetricValue"] { font-weight: 900; }

    .stButton > button {
        border: 2px solid #171717;
        border-radius: 4px;
        background: #ffdf3d;
        color: #171717;
        font-weight: 850;
        box-shadow: 3px 3px 0 #171717;
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover {
        background: #ff7fa8;
        color: #171717;
        border-color: #171717;
        transform: translate(-1px, -1px);
        box-shadow: 5px 5px 0 #171717;
    }

    .pop-eyebrow {
        display: inline-block;
        padding: 5px 10px;
        margin-bottom: 8px;
        background: #171717;
        color: #fff;
        font-size: .76rem;
        font-weight: 900;
        letter-spacing: 1.5px;
        transform: rotate(-2deg);
    }

    .pop-art {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        overflow: hidden;
        border: 4px solid #171717;
        background: #171717;
        box-shadow: 8px 8px 0 #171717;
        gap: 3px;
    }
    .pop-tile {
        min-height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
        font-size: clamp(2rem, 5vw, 4.1rem);
        background-image: radial-gradient(rgba(0,0,0,.17) 1.2px, transparent 1.3px);
        background-size: 8px 8px;
    }
    .pop-tile:nth-child(1) { background-color: #ff4f87; }
    .pop-tile:nth-child(2) { background-color: #ffdf3d; }
    .pop-tile:nth-child(3) { background-color: #36d8cf; }
    .pop-tile:nth-child(4) { background-color: #8e7aff; }
    .pop-tile:nth-child(5) { background-color: #ff873a; }
    .pop-tile:nth-child(6) { background-color: #9bea63; }
    .pop-tile:nth-child(7) { background-color: #58bfff; }
    .pop-tile:nth-child(8) { background-color: #ff6a5e; }

    .pop-tile span {
        display: inline-block;
        filter: drop-shadow(3px 3px 0 rgba(0,0,0,.22));
        animation: popBounce 1.7s ease-in-out infinite;
    }
    .pop-tile:nth-child(even) span {
        animation-delay: .22s;
    }

    .pop-title {
        border: 4px solid #171717;
        border-top: 0;
        padding: 15px 18px;
        background: #ffdf3d;
        box-shadow: 8px 8px 0 #171717;
        font-size: clamp(1.1rem, 2.2vw, 1.8rem);
        font-weight: 950;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }

    .pop-detail {
        background: #fffdf4;
        border: 3px solid #171717;
        padding: 18px 20px;
        box-shadow: 6px 6px 0 #171717;
        min-height: 220px;
        overflow-wrap: anywhere;
    }
    .pop-detail p { line-height: 1.65; }

    .mini-label {
        display: inline-block;
        font-size: .75rem;
        font-weight: 900;
        background: #36d8cf;
        border: 2px solid #171717;
        padding: 4px 8px;
        margin: 3px 4px 3px 0;
        color: #171717;
    }

    .rise {
        color: #e31b23;
        font-weight: 950;
        white-space: nowrap;
    }
    .fall {
        color: #1769d2;
        font-weight: 950;
        white-space: nowrap;
    }
    .steady {
        color: #555;
        font-weight: 800;
        white-space: nowrap;
    }

    .boxoffice-table {
        width: 100%;
        border-collapse: collapse;
        background: #fffdf4;
        border: 3px solid #171717;
    }
    .boxoffice-table th {
        background: #171717;
        color: #fff;
        padding: 11px 9px;
        text-align: left;
        border: 1px solid #171717;
    }
    .boxoffice-table td {
        padding: 10px 9px;
        border: 1px solid #b8b3a1;
        font-weight: 650;
    }
    .boxoffice-table tr:nth-child(even) { background: #fff0bd; }
    .boxoffice-table tr:hover { background: #ffdce7; }

    @keyframes popBounce {
        0%, 100% { transform: translateY(0) rotate(-5deg) scale(1); }
        50% { transform: translateY(-9px) rotate(6deg) scale(1.12); }
    }

    @media (max-width: 650px) {
        .pop-tile { min-height: 75px; }
        .boxoffice-table { font-size: .8rem; }
        .boxoffice-table th,
        .boxoffice-table td { padding: 7px 5px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 2. 공통 오류 안내 함수
# ============================================================
def show_troubleshooting(title: str, details: str = "") -> None:
    """오류가 생겼을 때 한국어로 확인 방법을 안내합니다."""
    st.error(title)

    if details:
        st.write(details)

    st.markdown(
        "**확인해 보세요**\n"
        "- Streamlit Cloud의 Settings → Secrets에 `KOBIS_KEY`가 등록되어 있는지 확인하세요.\n"
        "- 인증키 앞뒤에 공백이 없는지, 유효한 키인지 확인하세요.\n"
        "- 선택한 날짜의 자료가 KOBIS에서 제공되는지 확인하세요.\n"
        "- 앱의 인터넷 연결과 KOBIS API 상태를 확인한 뒤 다시 실행하세요."
    )


def describe_api_fault(fault_info) -> str:
    """KOBIS 오류 응답에서 오류 코드와 메시지를 찾습니다."""
    if isinstance(fault_info, dict):
        code = (
            fault_info.get("errorCode")
            or fault_info.get("code")
            or "코드 없음"
        )
        message = (
            fault_info.get("errorMessage")
            or fault_info.get("message")
            or fault_info.get("errorMsg")
            or fault_info.get("faultString")
            or "응답에 구체적인 오류 메시지가 없습니다."
        )
        return f"KOBIS 오류 코드: {code}\n\nKOBIS 오류 메시지: {message}"

    return f"KOBIS 오류 정보: {fault_info}"


def names_from_api(items, key: str) -> list[str]:
    """KOBIS에서 받은 목록형 데이터를 문자열 목록으로 바꿉니다."""
    if not isinstance(items, list):
        return []

    result = []
    for item in items:
        if isinstance(item, dict):
            value = item.get(key)
            if value:
                result.append(str(value))

    return result


def safe_text(value) -> str:
    """정보가 비어 있을 때 대신 보여 줄 문구를 반환합니다."""
    if value is None or str(value).strip() in ("", "None"):
        return "정보 없음"

    return str(value).strip()


# ============================================================
# 3. KOBIS API 요청 함수
# ============================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_boxoffice(api_key: str, target_date: str) -> dict:
    """선택한 날짜의 일별 박스오피스를 조회합니다."""
    response = requests.get(
        BOXOFFICE_API_URL,
        params={
            "key": api_key,
            "targetDt": target_date,
        },
        timeout=20,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"KOBIS가 HTTP {response.status_code} 상태를 반환했습니다."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "KOBIS 응답을 JSON으로 읽을 수 없습니다."
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError("KOBIS 응답 형식이 예상과 다릅니다.")

    return payload


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_movie_info(api_key: str, movie_code: str) -> dict:
    """선택한 영화의 장르, 감독, 출연진 등 상세정보를 조회합니다."""
    response = requests.get(
        MOVIE_INFO_API_URL,
        params={
            "key": api_key,
            "movieCd": movie_code,
        },
        timeout=20,
    )

    if response.status_code != 200:
        return {
            "_error": (
                f"상세정보 API가 HTTP {response.status_code}를 반환했습니다."
            )
        }

    try:
        payload = response.json()
    except ValueError:
        return {"_error": "상세정보 응답을 JSON으로 읽을 수 없습니다."}

    if not isinstance(payload, dict):
        return {"_error": "상세정보 응답 형식이 예상과 다릅니다."}

    if payload.get("faultInfo"):
        return {"_error": describe_api_fault(payload["faultInfo"])}

    result = payload.get("movieInfoResult", {})
    info = result.get("movieInfo") if isinstance(result, dict) else None

    if not isinstance(info, dict):
        return {"_error": "이 영화의 상세정보가 응답에 없습니다."}

    return info


# ============================================================
# 4. 제목과 날짜 선택기
# ============================================================
now_in_korea = datetime.now(ZoneInfo("Asia/Seoul"))
today_in_korea = now_in_korea.date()
yesterday = today_in_korea - timedelta(days=1)

st.markdown(
    '<span class="pop-eyebrow">DAILY BOX OFFICE · POP ART EDITION</span>',
    unsafe_allow_html=True,
)
st.title("🎬 오늘 말고, 선택한 날의 박스오피스!")
st.caption(
    "KOBIS 공식 일별 박스오피스 · 한국 시간 기준 · "
    "팝아트에서 영감을 얻은 디자인"
)

# 오늘은 아직 집계 전일 수 있으므로 어제까지만 선택할 수 있습니다.
selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요 (어제까지 선택 가능)",
    value=yesterday,
    min_value=date(2004, 11, 11),
    max_value=yesterday,
    key="boxoffice_date_picker",
)

target_date = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

st.caption(f"선택한 조회 기준일: **{display_date}**")

# 날짜가 바뀌면 이전에 선택한 영화는 초기화합니다.
if st.session_state.get("last_loaded_date") != target_date:
    st.session_state["selected_movie_key"] = ""
    st.session_state["last_loaded_date"] = target_date

st.divider()


# ============================================================
# 5. 비밀 금고에서 API 인증키 읽기
# ============================================================
# 실제 인증키를 코드에 직접 적지 않습니다.
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    show_troubleshooting(
        "KOBIS 인증키를 찾을 수 없습니다.",
        'Settings → Secrets에 다음 형식으로 등록하세요: '
        '`KOBIS_KEY = "발급받은_실제_인증키"`',
    )
    st.stop()

if not isinstance(api_key, str) or not api_key.strip():
    show_troubleshooting(
        "KOBIS 인증키가 비어 있습니다.",
        "Secrets의 KOBIS_KEY 값이 비어 있지 않은지 확인하세요.",
    )
    st.stop()


# ============================================================
# 6. 선택한 날짜의 박스오피스 데이터 요청
# ============================================================
try:
    with st.spinner(f"{display_date} 박스오피스 자료를 불러오는 중..."):
        payload = fetch_boxoffice(api_key.strip(), target_date)

except requests.exceptions.Timeout:
    show_troubleshooting(
        "KOBIS 응답 시간이 초과되었습니다.",
        "20초 안에 응답을 받지 못했습니다. 잠시 후 다시 시도하세요.",
    )
    st.stop()

except requests.exceptions.RequestException as exc:
    show_troubleshooting(
        "KOBIS API에 연결하지 못했습니다.",
        f"연결 오류: {exc}",
    )
    st.stop()

except RuntimeError as exc:
    show_troubleshooting(
        "KOBIS API 요청에 실패했습니다.",
        str(exc),
    )
    st.stop()

# HTTP 200이어도 faultInfo가 있으면 API 오류로 처리합니다.
if payload.get("faultInfo"):
    show_troubleshooting(
        "KOBIS가 오류 정보를 반환했습니다.",
        describe_api_fault(payload["faultInfo"]),
    )
    st.stop()

box_office_result = payload.get("boxOfficeResult")

if not isinstance(box_office_result, dict):
    show_troubleshooting(
        "응답에 박스오피스 결과가 없습니다.",
        "KOBIS 응답에 boxOfficeResult가 있는지 확인하세요.",
    )
    st.stop()

movie_list = box_office_result.get("dailyBoxOfficeList")

# 영화 목록이 비어 있으면 사용자가 알아볼 수 있도록 별도 안내를 표시합니다.
if not isinstance(movie_list, list) or len(movie_list) == 0:
    st.warning(f"📭 {display_date}: 그날은 아직 집계 전입니다.")
    st.info(
        "선택한 날짜의 영화 목록이 비어 있습니다. "
        "날짜를 다시 선택하거나 잠시 후 확인해 주세요."
    )
    st.stop()


# ============================================================
# 7. API 자료 정리
# ============================================================
df = pd.DataFrame(movie_list)

required_columns = [
    "movieCd",
    "rank",
    "rankInten",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

# 예상한 열이 누락된 경우에도 오류가 나지 않도록 빈 열을 만듭니다.
for column in required_columns:
    if column not in df.columns:
        df[column] = ""

# API는 숫자도 문자열로 반환하므로 숫자 형태로 변환합니다.
for column in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]:
    df[column] = (
        pd.to_numeric(df[column], errors="coerce")
        .fillna(0)
        .astype(int)
    )

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

df["movieCd"] = df["movieCd"].fillna("").astype(str)

df = df.sort_values("rank", ascending=True).reset_index(drop=True)

# 영화 코드가 없을 때도 버튼을 구분할 수 있도록 임시 키를 만듭니다.
df["_selection_key"] = [
    code if code else f"rank-{rank}-{idx}"
    for idx, (code, rank) in enumerate(
        zip(df["movieCd"], df["rank"])
    )
]

if df.empty:
    st.warning(f"📭 {display_date}: 그날은 아직 집계 전입니다.")
    st.stop()


# ============================================================
# 8. 1위 영화 지표 카드
# ============================================================
leader = df.iloc[0]
leader_name = str(leader["movieNm"])

leader_trophy = (
    " 🏆" if int(leader["audiAcc"]) > 1_000_000 else ""
)

st.subheader(
    f"🏆 {display_date} 박스오피스 1위: "
    f"{leader_name}{leader_trophy}"
)

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


# ============================================================
# 9. 관객수 상위 5편 그래프
# ============================================================
st.subheader("📊 관객수 상위 5편")

top5 = df.sort_values(
    "audiCnt",
    ascending=False,
).head(5).copy()

chart_df = (
    top5.set_index("movieNm")[["audiCnt"]]
    .rename(columns={"audiCnt": "관객수"})
)

st.bar_chart(chart_df)

st.divider()


# ============================================================
# 10. 영화 제목 버튼
# ============================================================
st.subheader("🍿 영화를 눌러 작품 애니메이션과 상세정보 보기")
st.caption(
    "영화 제목을 누르면 팝아트 애니메이션과 함께 "
    "KOBIS에서 확인할 수 있는 영화 정보가 나타납니다."
)

# 영화 선택 버튼을 두 열로 배치합니다.
for start_idx in range(0, len(df), 2):
    button_columns = st.columns(2)

    for offset, column in enumerate(button_columns):
        row_idx = start_idx + offset

        if row_idx >= len(df):
            continue

        row = df.iloc[row_idx]

        trophy = (
            " 🏆" if int(row["audiAcc"]) > 1_000_000 else ""
        )

        button_label = (
            f"{int(row['rank'])}위 · {row['movieNm']}{trophy}"
        )

        with column:
            if st.button(
                button_label,
                key=f"pick_{target_date}_{row['_selection_key']}",
                use_container_width=True,
            ):
                st.session_state["selected_movie_key"] = (
                    row["_selection_key"]
                )

selected_key = st.session_state.get("selected_movie_key", "")

selected_rows = df[
    df["_selection_key"] == selected_key
]

if selected_rows.empty:
    st.info(
        "👆 위에서 관심 있는 영화 제목을 눌러 보세요. "
        "작품 소개와 애니메이션이 여기에 나타납니다."
    )

else:
    selected_movie = selected_rows.iloc[0]

    selected_name = str(selected_movie["movieNm"])
    selected_code = str(selected_movie["movieCd"]).strip()
    selected_audi = int(selected_movie["audiCnt"])
    selected_total = int(selected_movie["audiAcc"])
    selected_rank = int(selected_movie["rank"])

    movie_info = {}
    info_error = ""

    # 영화 코드를 이용해 상세정보를 가져옵니다.
    if selected_code:
        try:
            with st.spinner(
                f"{selected_name} 상세정보를 불러오는 중..."
            ):
                movie_info = fetch_movie_info(
                    api_key.strip(),
                    selected_code,
                )

            if "_error" in movie_info:
                info_error = str(movie_info["_error"])
                movie_info = {}

        except requests.exceptions.RequestException as exc:
            info_error = (
                f"상세정보 API에 연결하지 못했습니다: {exc}"
            )

    else:
        info_error = (
            "이 영화의 코드가 응답에 없어 "
            "상세정보 API를 조회하지 못했습니다."
        )

    genres = names_from_api(
        movie_info.get("genres", []),
        "genreNm",
    )
    directors = names_from_api(
        movie_info.get("directors", []),
        "peopleNm",
    )
    actors = names_from_api(
        movie_info.get("actors", []),
        "peopleNm",
    )
    audits = names_from_api(
        movie_info.get("audits", []),
        "watchGradeNm",
    )

    genre_text = ", ".join(genres) if genres else "장르 정보 없음"
    director_text = (
        ", ".join(directors) if directors else "감독 정보 없음"
    )
    actor_text = (
        ", ".join(actors[:5]) if actors else "출연진 정보 없음"
    )

    runtime_raw = safe_text(movie_info.get("showTm"))
    runtime = (
        f"{runtime_raw}분"
        if runtime_raw.isdigit()
        else runtime_raw
    )

    year = safe_text(movie_info.get("prdtYear"))
    grade = (
        ", ".join(audits)
        if audits
        else "관람등급 정보 없음"
    )

    # 장르에 따라 어울리는 아이콘을 선택합니다.
    genre_icons = [
        ("애니메이션", "🦊"),
        ("액션", "💥"),
        ("공포", "👻"),
        ("호러", "👻"),
        ("스릴러", "🕵️"),
        ("코미디", "😂"),
        ("드라마", "🎭"),
        ("SF", "🚀"),
        ("멜로", "💗"),
        ("범죄", "🕶️"),
        ("다큐멘터리", "🎙️"),
    ]

    movie_icon = "🎬"

    for genre_keyword, icon_symbol in genre_icons:
        if genre_keyword.lower() in genre_text.lower():
            movie_icon = icon_symbol
            break

    # 사용자 입력이나 API의 문자열이 HTML로 해석되지 않도록 처리합니다.
    escaped_name = html.escape(selected_name)
    escaped_genre = html.escape(genre_text)
    escaped_director = html.escape(director_text)
    escaped_actor = html.escape(actor_text)
    escaped_runtime = html.escape(runtime)
    escaped_year = html.escape(year)
    escaped_grade = html.escape(grade)
    repeated_icon = html.escape(movie_icon)

    st.markdown("---")
    st.subheader(f"🎞️ 선택한 영화: {selected_name}")

    poster_col, detail_col = st.columns(
        [1, 1.15],
        gap="large",
    )

    with poster_col:
        # 여러 색상의 아이콘이 반복해서 움직이는 팝아트 그림입니다.
        st.markdown(
            f"""
            <div class="pop-art" aria-label="{escaped_name} 팝아트 애니메이션">
                <div class="pop-tile"><span>{repeated_icon}</span></div>
                <div class="pop-tile"><span>{repeated_icon}</span></div>
                <div class="pop-tile"><span>{repeated_icon}</span></div>
                <div class="pop-tile"><span>{repeated_icon}</span></div>
                <div class="pop-tile"><span>🎟️</span></div>
                <div class="pop-tile"><span>{repeated_icon}</span></div>
                <div class="pop-tile"><span>✨</span></div>
                <div class="pop-tile"><span>{repeated_icon}</span></div>
            </div>
            <div class="pop-title">{escaped_name}</div>
            """,
            unsafe_allow_html=True,
        )

    with detail_col:
        # 애니메이션 옆에서 작품 정보를 동시에 보여 줍니다.
        st.markdown(
            f"""
            <div class="pop-detail">
              <span class="mini-label">RANK {selected_rank}</span>
              <span class="mini-label">{escaped_genre}</span>
              <span class="mini-label">{escaped_year}</span>

              <p><b>작품 정보</b></p>

              <p>
                이 작품은 <b>{escaped_genre}</b> 장르입니다.
                감독은 <b>{escaped_director}</b>이며,
                확인된 출연진은 <b>{escaped_actor}</b>입니다.
              </p>

              <p>
                <b>상영시간:</b> {escaped_runtime}<br>
                <b>관람등급:</b> {escaped_grade}
              </p>

              <p>
                <b>선택한 날의 관객수:</b> {selected_audi:,}명<br>
                <b>누적 관객수:</b> {selected_total:,}명
              </p>

              <p>
                ※ 소개는 KOBIS 상세정보에서 확인되는 제작 정보에
                기반합니다. API가 줄거리 요약을 제공하지 않으면
                줄거리를 임의로 만들어 넣지 않습니다.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if info_error:
            st.warning(
                "추가 상세정보 일부를 불러오지 못했습니다. "
                + info_error
            )

st.divider()


# ============================================================
# 11. 전체 박스오피스 표
# ============================================================
st.subheader("📋 일별 박스오피스 전체 목록")

st.caption(
    "순위 상승은 빨간 위 화살표, 순위 하락은 파란 아래 "
    "화살표로 표시합니다. 누적 관객이 100만 명을 넘으면 🏆가 붙습니다."
)

html_rows = []

for _, row in df.iterrows():
    rank_change = int(row["rankInten"])

    # rankInten 양수는 상승, 음수는 하락으로 표시합니다.
    if rank_change > 0:
        change_html = (
            f'<span class="rise">↑ {rank_change}</span>'
        )
    elif rank_change < 0:
        change_html = (
            f'<span class="fall">↓ {abs(rank_change)}</span>'
        )
    else:
        change_html = '<span class="steady">—</span>'

    movie_name = html.escape(str(row["movieNm"]))

    # 누적 관객이 100만 명을 초과한 영화에 트로피를 표시합니다.
    if int(row["audiAcc"]) > 1_000_000:
        movie_name += " 🏆"

    open_date = html.escape(str(row["openDt"]))

    html_rows.append(
        "<tr>"
        f"<td>{int(row['rank'])}위</td>"
        f"<td>{change_html}</td>"
        f"<td>{movie_name}</td>"
        f"<td>{open_date}</td>"
        f"<td>{int(row['audiCnt']):,}명</td>"
        f"<td>{int(row['audiAcc']):,}명</td>"
        f"<td>{int(row['scrnCnt']):,}개</td>"
        "</tr>"
    )

st.markdown(
    """
    <div style="overflow-x:auto;">
      <table class="boxoffice-table">
        <thead>
          <tr>
            <th>순위</th>
            <th>순위 증감</th>
            <th>영화명</th>
            <th>개봉일</th>
            <th>관객수</th>
            <th>누적관객</th>
            <th>스크린수</th>
          </tr>
        </thead>
        <tbody>
    """
    + "".join(html_rows)
    + """
        </tbody>
      </table>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "자료 출처: 영화관입장권통합전산망(KOBIS) "
    "일별 박스오피스 및 영화 상세정보 API"
)
