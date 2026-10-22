
import html
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st


# ============================================================
# 1. 기본 설정과 KOBIS 공식 API 주소
# ============================================================
st.set_page_config(
    page_title="박스오피스 아카이브",
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


# ============================================================
# 2. 현대미술관 느낌의 배경과 영화 장면 애니메이션 디자인
# ============================================================
# 밝은 콘크리트 벽, 넓은 여백, 전시 라벨 같은 절제된 분위기를 만듭니다.
st.markdown(
    """
    <style>
    .stApp {
      background:
        radial-gradient(ellipse at 15% 0%, rgba(255,255,255,.96), transparent 42%),
        radial-gradient(ellipse at 88% 8%, rgba(211,205,192,.45), transparent 38%),
        linear-gradient(180deg, #f4f2ed 0%, #eeece6 52%, #e4e1d9 100%);
      color: #252521;
    }
    .stApp::before {
      content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
      opacity:.18;
      background:repeating-linear-gradient(0deg,transparent 0 5px,rgba(30,30,25,.025) 6px 7px);
    }
    .block-container { max-width:1450px; padding-top:2.2rem; padding-bottom:4rem; position:relative; z-index:1; }
    h1,h2,h3 { color:#252521 !important; font-weight:800 !important; letter-spacing:-.035em; }
    h1 { font-size:clamp(2rem,4vw,3.4rem) !important; }
    p,label,[data-testid="stCaptionContainer"] { color:#57574f; }
    .gallery-kicker {
      display:inline-block; color:#5d5a51; font-size:.72rem; letter-spacing:.22em;
      font-weight:850; border-top:1px solid #8e8b82; border-bottom:1px solid #8e8b82;
      padding:8px 0; margin-bottom:10px;
    }
    .gallery-subtitle { border-left:3px solid #9c4f3f; padding-left:13px; color:#6b685f; line-height:1.7; }
    .museum-rule { height:1px; background:#c7c3b8; margin:1.3rem 0; }
    [data-testid="stMetric"] {
      background:rgba(255,255,252,.8); border:1px solid #d1cec5; border-radius:2px;
      padding:18px 20px; box-shadow:0 5px 18px rgba(35,34,29,.045);
    }
    [data-testid="stMetricLabel"] { color:#66645b; font-weight:650; }
    [data-testid="stMetricValue"] { color:#242420; font-weight:800; }
    .stButton > button {
      border:1px solid #bdb9ad; border-radius:2px; background:rgba(255,255,252,.8);
      color:#292923; font-weight:650; min-height:2.65rem; box-shadow:none;
      transition:background .2s,border-color .2s,transform .2s;
    }
    .stButton > button:hover { background:#e4ddd0; color:#1d1d19; border-color:#6d695f; transform:translateY(-1px); }
    [data-testid="stDateInput"] input { border-radius:2px; background:rgba(255,255,252,.9); border-color:#c7c3b8; }
    .rise { color:#c62828; font-weight:850; white-space:nowrap; }
    .fall { color:#1769aa; font-weight:850; white-space:nowrap; }
    .steady { color:#6b695f; font-weight:700; white-space:nowrap; }
    .boxoffice-table { width:100%; border-collapse:collapse; background:rgba(255,255,252,.9); border:1px solid #c8c4ba; font-size:.94rem; }
    .boxoffice-table th { background:#e2dfd7; color:#383831; padding:12px 10px; text-align:left; border-bottom:1px solid #c4c0b6; font-weight:750; white-space:nowrap; }
    .boxoffice-table td { padding:11px 10px; border-bottom:1px solid #e0ddd5; font-weight:500; }
    .boxoffice-table tr:nth-child(even) { background:rgba(239,237,230,.72); }
    .boxoffice-table tr:hover { background:#e9e3d7; }

    /* 영화의 장르에 따라 달라지는, 유아적이지 않은 시네마틱 모션 그래픽 */
    .cinema-stage { height:360px; position:relative; overflow:hidden; isolation:isolate; border:1px solid #a7a398; box-shadow:0 14px 30px rgba(25,24,20,.12); color:#f5f0e5; background:#171a1e; }
    .cinema-stage * { box-sizing:border-box; }
    .scene-topline { position:absolute; z-index:12; left:19px; top:17px; font-size:.65rem; letter-spacing:.2em; font-weight:750; color:rgba(248,244,233,.76); }
    .scene-lockup { position:absolute; z-index:12; left:20px; right:20px; bottom:17px; border-top:1px solid rgba(255,255,255,.33); padding-top:10px; display:flex; justify-content:space-between; align-items:end; gap:12px; }
    .scene-lockup strong { font-size:clamp(.82rem,2vw,1.15rem); letter-spacing:.12em; font-weight:750; }
    .scene-lockup span { font-size:.63rem; letter-spacing:.1em; color:rgba(250,247,238,.72); text-align:right; }
    .scene-vignette { position:absolute; inset:0; z-index:10; pointer-events:none; box-shadow:inset 0 0 95px rgba(0,0,0,.64); }
    .scene-note { font-size:.8rem; line-height:1.65; color:#6a675e; padding:11px 2px 0; }

    /* 암살·킬러 영화: 빗속 골목, 표적 실루엣, 잠입과 컷 전환. 폭력 묘사는 그림자로만 표현합니다. */
    .scene-assassin { background:linear-gradient(180deg,#171d27 0%,#27313a 44%,#13171c 100%); }
    .moon-glow { position:absolute; width:170px; height:170px; border-radius:50%; top:17px; right:18%; background:radial-gradient(circle,rgba(213,220,220,.62),rgba(161,181,193,.15) 42%,transparent 72%); filter:blur(2px); }
    .scene-building { position:absolute; bottom:0; background:#101318; border-top:1px solid rgba(200,213,218,.15); }
    .scene-building::after { content:""; position:absolute; inset:16px 10px 20px; background:repeating-linear-gradient(90deg,transparent 0 19px,rgba(165,181,190,.12) 20px 23px),repeating-linear-gradient(0deg,transparent 0 25px,rgba(165,181,190,.09) 26px 29px); }
    .building-a { left:0; width:24%; height:76%; }
    .building-b { left:24%; width:22%; height:53%; background:#171c23; }
    .building-c { right:0; width:29%; height:81%; background:#101419; }
    .building-d { right:25%; width:20%; height:45%; background:#202731; }
    .scene-lamp { position:absolute; z-index:2; top:-40px; left:52%; width:3px; height:210px; background:rgba(221,212,175,.75); box-shadow:0 0 30px 12px rgba(211,194,141,.17); transform:rotate(10deg); }
    .scene-rain { position:absolute; z-index:4; inset:-30% -20%; opacity:.26; background:repeating-linear-gradient(104deg,transparent 0 26px,rgba(217,229,235,.5) 27px,transparent 28px 46px); animation:rainFall .65s linear infinite; }
    .scene-pavement { position:absolute; z-index:2; left:0; right:0; bottom:0; height:24%; background:linear-gradient(180deg,rgba(8,10,13,.08),#090c10 80%); }
    .scene-puddle { position:absolute; z-index:3; left:10%; right:5%; bottom:7%; height:18%; background:linear-gradient(165deg,transparent 15%,rgba(144,178,191,.2) 43%,rgba(202,185,137,.08) 58%,transparent 76%); transform:skewX(-18deg); filter:blur(2px); }
    .scene-figure { position:absolute; z-index:6; width:64px; height:160px; bottom:11%; }
    .figure-head { position:absolute; top:0; left:21px; width:21px; height:23px; border-radius:50%; background:#090b0e; }
    .figure-body { position:absolute; top:21px; left:10px; width:45px; height:75px; background:#080a0d; clip-path:polygon(24% 0,72% 0,100% 100%,0 100%); }
    .figure-leg { position:absolute; top:86px; width:15px; height:64px; background:#080a0d; transform-origin:top center; }
    .figure-leg.left { left:17px; } .figure-leg.right { left:34px; }
    .scene-assassin-figure { left:6%; animation:assassinMove 6.2s cubic-bezier(.5,0,.2,1) infinite; }
    .scene-assassin-figure .figure-leg.left { animation:legSwing .6s ease-in-out infinite; }
    .scene-assassin-figure .figure-leg.right { animation:legSwing .6s ease-in-out .3s infinite; }
    .scene-target-figure { left:76%; transform:scale(.88); transform-origin:bottom center; animation:targetDrop 6.2s steps(1) infinite; }
    .scene-target-figure .figure-body { background:#121820; border-left:1px solid rgba(210,220,225,.12); }
    .scene-glint { position:absolute; z-index:8; top:38%; left:48%; width:1px; height:1px; background:#f3e7c2; opacity:0; box-shadow:0 0 2px 1px #f3e7c2; animation:cinematicFlash 6.2s linear infinite; }
    .scene-cut { position:absolute; z-index:9; inset:0; background:#e4e0d5; opacity:0; animation:cutToWhite 6.2s linear infinite; mix-blend-mode:screen; }

    /* 액션·범죄·스릴러: 고층 도시와 추격 장면 */
    .scene-noir { background:linear-gradient(180deg,#202a35 0%,#58616a 54%,#13171b 100%); }
    .noir-haze { position:absolute; width:70%; height:45%; top:18%; left:15%; background:radial-gradient(ellipse,rgba(188,198,202,.32),transparent 70%); filter:blur(10px); }
    .noir-skyline { position:absolute; bottom:0; left:0; right:0; height:54%; background:repeating-linear-gradient(90deg,#10151a 0 8%,#202832 8% 10%,#10151a 10% 16%); clip-path:polygon(0 22%,10% 22%,10% 0,24% 0,24% 35%,36% 35%,36% 9%,52% 9%,52% 43%,67% 43%,67% 13%,84% 13%,84% 31%,100% 31%,100% 100%,0 100%); }
    .noir-searchlight { position:absolute; z-index:3; top:-35%; right:8%; width:35%; height:135%; background:linear-gradient(180deg,rgba(218,224,212,.2),transparent 76%); clip-path:polygon(44% 0,54% 0,100% 100%,0 100%); animation:searchSweep 7s ease-in-out infinite alternate; }
    .noir-runner { position:absolute; bottom:13%; left:13%; width:48px; height:128px; z-index:5; animation:rooftopRun 3.4s ease-in-out infinite alternate; }
    .noir-runner .figure-head,.noir-runner .figure-body,.noir-runner .figure-leg { background:#080b0e; }

    /* 공포·미스터리: 어두운 복도와 길어지는 그림자 */
    .scene-horror { background:linear-gradient(90deg,#07090d,#24262b 48%,#08090c); }
    .horror-corridor { position:absolute; inset:0; background:linear-gradient(90deg,transparent 0 15%,rgba(164,165,159,.09) 15.4% 15.8%,transparent 16% 84%,rgba(164,165,159,.08) 84.4% 84.8%,transparent 85%),linear-gradient(180deg,transparent 58%,rgba(0,0,0,.75)); }
    .horror-door { position:absolute; width:29%; height:72%; right:18%; bottom:0; border:2px solid rgba(185,185,177,.35); background:linear-gradient(90deg,#111419,#292a2d 52%,#111318); box-shadow:0 0 35px rgba(190,194,182,.12); }
    .horror-shadow { position:absolute; z-index:4; width:80px; height:200px; left:10%; bottom:0; background:#030407; clip-path:polygon(39% 0,61% 0,70% 12%,73% 32%,100% 100%,0 100%,29% 34%,30% 13%); animation:shadowCreep 5s ease-in-out infinite alternate; }
    .horror-light { position:absolute; top:-10%; right:20%; width:32%; height:120%; background:rgba(194,191,165,.12); filter:blur(16px); animation:horrorFlicker 3s steps(2) infinite; }

    /* SF: 행성과 우주선 */
    .scene-scifi { background:radial-gradient(ellipse at 72% 37%,#364b64 0%,#1d2a40 31%,#080d18 72%); }
    .space-stars { position:absolute; inset:0; opacity:.65; background-image:radial-gradient(#eee8d8 1px,transparent 1.5px),radial-gradient(#8ca6bd 1px,transparent 1.5px); background-size:47px 51px,71px 63px; background-position:0 0,19px 23px; animation:starDrift 14s linear infinite; }
    .space-planet { position:absolute; width:190px; height:190px; border-radius:50%; right:9%; top:14%; background:radial-gradient(circle at 30% 28%,#a9bdca,#4c6987 45%,#172338 75%); box-shadow:0 0 55px rgba(114,164,209,.32); animation:planetFloat 8s ease-in-out infinite; }
    .space-ship { position:absolute; z-index:5; left:10%; top:49%; width:150px; height:32px; background:linear-gradient(180deg,#b9c3c7,#4a565f 48%,#111923 52%); clip-path:polygon(0 42%,56% 18%,100% 50%,57% 68%,15% 100%); animation:shipTraverse 7s ease-in-out infinite alternate; }
    .space-engine { position:absolute; left:7%; top:54%; width:48px; height:5px; background:#b4d8ef; filter:blur(4px); animation:enginePulse .8s ease-in-out infinite alternate; }

    /* 멜로·로맨스: 도시 야경과 마주 선 두 사람 */
    .scene-romance { background:linear-gradient(180deg,#1b2330 0%,#6a5260 53%,#d0a28f 100%); }
    .romance-moon { position:absolute; width:120px; height:120px; border-radius:50%; top:14%; right:22%; background:radial-gradient(circle,#f4dfc6 0%,rgba(244,223,198,.65) 35%,transparent 72%); }
    .romance-city { position:absolute; left:0; right:0; bottom:0; height:47%; background:repeating-linear-gradient(90deg,#171a22 0 7%,#28262c 7% 9%,#141820 9% 16%); clip-path:polygon(0 35%,12% 35%,12% 0,26% 0,26% 46%,43% 46%,43% 15%,59% 15%,59% 34%,76% 34%,76% 4%,91% 4%,91% 42%,100% 42%,100% 100%,0 100%); }
    .romance-person { position:absolute; z-index:5; bottom:11%; width:32px; height:118px; background:#12151b; clip-path:polygon(35% 0,65% 0,76% 18%,100% 100%,0 100%,24% 18%); }
    .romance-person.left { left:38%; animation:personBreath 3.2s ease-in-out infinite; }
    .romance-person.right { left:53%; animation:personBreath 3.2s ease-in-out .7s infinite; }

    /* 장르 분류가 없으면 영사기 빛과 프레임을 보여 줍니다. */
    .scene-general { background:linear-gradient(135deg,#292c30 0%,#131518 52%,#33312c 100%); }
    .projector-screen { position:absolute; top:15%; left:21%; right:12%; height:63%; border:1px solid rgba(232,226,210,.36); background:linear-gradient(145deg,rgba(211,207,193,.17),rgba(122,130,139,.05)); transform:perspective(600px) rotateY(-5deg); }
    .projector-beam { position:absolute; width:80%; height:120%; left:-9%; top:-10%; background:linear-gradient(110deg,rgba(225,219,197,.14),transparent 65%); clip-path:polygon(0 0,12% 0,100% 100%,62% 100%); animation:beamPulse 4s ease-in-out infinite alternate; }
    .film-frame { position:absolute; top:28%; left:37%; width:34%; height:34%; border:1px solid rgba(246,241,226,.45); animation:filmFrameMove 5s ease-in-out infinite alternate; }
    .film-frame::after { content:""; position:absolute; inset:12px; border:1px solid rgba(246,241,226,.2); }

    @keyframes rainFall { from { transform:translate(-3%,-4%); } to { transform:translate(3%,4%); } }
    @keyframes assassinMove { 0%,10% { left:6%; transform:scale(.94); } 46%,62% { left:48%; transform:scale(1); } 70%,78% { left:53%; transform:scale(.98); } 100% { left:6%; transform:scale(.94); } }
    @keyframes legSwing { 0%,100% { transform:rotate(13deg); } 50% { transform:rotate(-13deg); } }
    @keyframes cinematicFlash { 0%,67%,75%,100% { opacity:0; transform:scale(1); } 70% { opacity:.95; transform:scale(13); } 72% { opacity:.05; transform:scale(2); } }
    @keyframes targetDrop { 0%,66% { opacity:1; transform:scale(.88) translateY(0); } 70% { opacity:.72; transform:scale(.86) translateY(5px); } 72%,92% { opacity:.12; transform:scale(.82) translateY(19px); } 100% { opacity:1; transform:scale(.88) translateY(0); } }
    @keyframes cutToWhite { 0%,68%,76%,100% { opacity:0; } 70% { opacity:.55; } 72% { opacity:.02; } }
    @keyframes rooftopRun { from { transform:translateX(0) skewX(-3deg); } to { transform:translateX(190px) skewX(5deg); } }
    @keyframes searchSweep { from { transform:rotate(-18deg); opacity:.2; } to { transform:rotate(18deg); opacity:.62; } }
    @keyframes shadowCreep { from { left:8%; transform:scaleX(.9); } to { left:35%; transform:scaleX(1.35); } }
    @keyframes horrorFlicker { 0%,90%,100% { opacity:.65; } 92% { opacity:.1; } 94% { opacity:.8; } }
    @keyframes starDrift { from { background-position:0 0,19px 23px; } to { background-position:70px 45px,-31px 80px; } }
    @keyframes planetFloat { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-9px); } }
    @keyframes shipTraverse { from { transform:translateX(0) rotate(-3deg); } to { transform:translateX(90px) rotate(2deg); } }
    @keyframes enginePulse { from { opacity:.45; transform:scaleX(.75); } to { opacity:1; transform:scaleX(1.15); } }
    @keyframes personBreath { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-3px); } }
    @keyframes beamPulse { from { opacity:.4; transform:translateX(0); } to { opacity:.9; transform:translateX(18px); } }
    @keyframes filmFrameMove { from { transform:translateX(-13px) rotate(-2deg); opacity:.6; } to { transform:translateX(16px) rotate(2deg); opacity:1; } }
    @media (prefers-reduced-motion:reduce) { .cinema-stage * { animation:none !important; } }
    @media (max-width:650px) {
      .cinema-stage { height:300px; }
      .scene-lockup { left:13px; right:13px; bottom:12px; }
      .scene-lockup strong { font-size:.8rem; }
      .boxoffice-table { font-size:.8rem; }
      .boxoffice-table th,.boxoffice-table td { padding:7px 5px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 오류 안내와 API 보조 함수
# ============================================================
def show_troubleshooting(title: str, details: str = "") -> None:
    """오류가 발생하면 한국어로 확인할 사항을 알려 줍니다."""
    st.error(title)
    if details:
        st.write(details)
    st.markdown(
        "**확인해 보세요**\n"
        "- Streamlit Cloud의 Settings → Secrets에 `KOBIS_KEY`가 등록되어 있는지 확인하세요.\n"
        "- 인증키 앞뒤에 공백이 없는지, 유효한 키인지 확인하세요.\n"
        "- 선택한 날짜의 자료가 KOBIS에서 제공되는지 확인하세요.\n"
        "- 인터넷 연결과 KOBIS API 상태를 확인한 뒤 다시 실행하세요."
    )


def describe_api_fault(fault_info) -> str:
    """오류 응답에서 API가 제공하는 오류 코드와 메시지를 찾습니다."""
    if isinstance(fault_info, dict):
        code = fault_info.get("errorCode") or fault_info.get("code") or "코드 없음"
        message = (
            fault_info.get("errorMessage")
            or fault_info.get("message")
            or fault_info.get("errorMsg")
            or fault_info.get("faultString")
            or "응답에 구체적인 오류 메시지가 없습니다."
        )
        return f"KOBIS 오류 코드: {code}\n\nKOBIS 오류 메시지: {message}"
    return f"KOBIS 오류 정보: {fault_info}"


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_boxoffice(api_key: str, target_date: str) -> dict:
    """선택한 날짜의 일별 박스오피스를 가져옵니다."""
    response = requests.get(
        BOXOFFICE_API_URL,
        params={"key": api_key, "targetDt": target_date},
        timeout=20,
    )
    if response.status_code != 200:
        raise RuntimeError(f"KOBIS가 HTTP {response.status_code} 상태를 반환했습니다.")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("KOBIS 응답을 JSON으로 읽을 수 없습니다.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("KOBIS 응답 형식이 예상과 다릅니다.")
    return payload


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_movie_info(api_key: str, movie_code: str) -> dict:
    """선택한 영화의 장르, 감독, 출연진 등 상세정보를 가져옵니다."""
    response = requests.get(
        MOVIE_INFO_API_URL,
        params={"key": api_key, "movieCd": movie_code},
        timeout=20,
    )
    if response.status_code != 200:
        return {"_error": f"상세정보 API가 HTTP {response.status_code}를 반환했습니다."}
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


def names_from_api(items, key: str) -> list[str]:
    """KOBIS가 반환한 목록에서 이름을 추출합니다."""
    if not isinstance(items, list):
        return []
    return [str(item[key]) for item in items if isinstance(item, dict) and item.get(key)]


def safe_text(value) -> str:
    """빈 값 대신 읽기 쉬운 안내 문구를 반환합니다."""
    if value is None or str(value).strip() in ("", "None"):
        return "정보 없음"
    return str(value).strip()


def make_cinematic_scene(movie_title: str, genre_text: str) -> tuple[str, str, str]:
    """제목·장르에 맞는 영화적 모티프를 CSS 애니메이션으로 구성합니다.

    KOBIS API는 일반적으로 실제 영화 장면이나 줄거리를 제공하지 않으므로,
    화면은 영화 제목과 장르에서 착안한 창작 모션 그래픽입니다.
    """
    combined = f"{movie_title.lower()} {genre_text.lower()}"

    # 제목에 암살·킬러 등이 있으면 잠입과 장면 전환이 있는 누아르 장면을 씁니다.
    if any(word in combined for word in ["암살", "암살자", "킬러", "어쌔신", "저격", "hitman", "assassin", "sniper"]):
        title = "SHADOW OPERATION"
        note = "비 내리는 골목에서 그림자 속 인물이 접근하고, 한순간의 컷 전환으로 끝나는 누아르 모티프입니다. 폭력적인 장면은 그림자와 빛으로만 표현합니다."
        scene = """
        <div class="cinema-stage scene-assassin">
          <div class="moon-glow"></div>
          <div class="scene-building building-a"></div><div class="scene-building building-b"></div>
          <div class="scene-building building-c"></div><div class="scene-building building-d"></div>
          <div class="scene-lamp"></div><div class="scene-rain"></div>
          <div class="scene-pavement"></div><div class="scene-puddle"></div>
          <div class="scene-figure scene-target-figure"><span class="figure-head"></span><span class="figure-body"></span><span class="figure-leg left"></span><span class="figure-leg right"></span></div>
          <div class="scene-figure scene-assassin-figure"><span class="figure-head"></span><span class="figure-body"></span><span class="figure-leg left"></span><span class="figure-leg right"></span></div>
          <div class="scene-glint"></div><div class="scene-cut"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 01</div>
          <div class="scene-lockup"><strong>SHADOW OPERATION</strong><span>STEALTH · NOIR · CUT</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    elif any(word in combined for word in ["공포", "호러", "귀신", "저주", "horror", "halloween"]):
        title = "THE LAST DOOR"
        note = "어두운 복도, 닫힌 문, 벽을 타고 길어지는 그림자를 이용해 긴장감을 표현합니다."
        scene = """
        <div class="cinema-stage scene-horror">
          <div class="horror-corridor"></div><div class="horror-light"></div>
          <div class="horror-door"></div><div class="horror-shadow"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 02</div>
          <div class="scene-lockup"><strong>THE LAST DOOR</strong><span>SUSPENSE · SHADOW</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    elif any(word in combined for word in ["sf", "공상과학", "우주", "외계", "미래", "science fiction", "space"]):
        title = "BEYOND ORBIT"
        note = "별 사이를 천천히 가로지르는 우주선과 행성의 움직임으로 광활한 SF 분위기를 표현합니다."
        scene = """
        <div class="cinema-stage scene-scifi">
          <div class="space-stars"></div><div class="space-planet"></div>
          <div class="space-engine"></div><div class="space-ship"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 03</div>
          <div class="scene-lockup"><strong>BEYOND ORBIT</strong><span>SPACE · DISTANCE</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    elif any(word in combined for word in ["멜로", "로맨스", "로맨틱", "연애", "사랑", "romance", "romantic"]):
        title = "AFTER THE CITY LIGHTS"
        note = "도시 야경과 서로 마주 선 두 인물, 노을빛을 통해 감정을 절제해 표현합니다."
        scene = """
        <div class="cinema-stage scene-romance">
          <div class="romance-moon"></div><div class="romance-city"></div>
          <div class="romance-person left"></div><div class="romance-person right"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 04</div>
          <div class="scene-lockup"><strong>AFTER THE CITY LIGHTS</strong><span>LIGHT · DISTANCE</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    elif any(word in combined for word in ["액션", "범죄", "스릴러", "느와르", "추격", "첩보", "스파이", "action", "crime", "thriller", "spy"]):
        title = "NIGHT PURSUIT"
        note = "도시 옥상과 탐색등, 달리는 인물의 실루엣으로 긴박한 추격 장면을 표현합니다."
        scene = """
        <div class="cinema-stage scene-noir">
          <div class="noir-haze"></div><div class="noir-skyline"></div><div class="noir-searchlight"></div>
          <div class="noir-runner"><span class="figure-head"></span><span class="figure-body"></span><span class="figure-leg left"></span><span class="figure-leg right"></span></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 05</div>
          <div class="scene-lockup"><strong>NIGHT PURSUIT</strong><span>URBAN · MOTION</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    else:
        title = "A FRAME IN THE DARK"
        note = "영사기의 빛과 움직이는 프레임으로 영화관의 어둠 속에서 장면이 시작되는 순간을 표현합니다."
        scene = """
        <div class="cinema-stage scene-general">
          <div class="projector-screen"></div><div class="projector-beam"></div><div class="film-frame"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 06</div>
          <div class="scene-lockup"><strong>A FRAME IN THE DARK</strong><span>LIGHT · FRAME · TIME</span></div>
          <div class="scene-vignette"></div>
        </div>
        """
    return scene, title, note


# ============================================================
# 4. 한국 시간 기준 날짜 선택
# ============================================================
# 배포 서버의 시간대에 기대지 않고 한국 시간으로 어제를 계산합니다.
now_korea = datetime.now(ZoneInfo("Asia/Seoul"))
yesterday = now_korea.date() - timedelta(days=1)

st.markdown('<div class="gallery-kicker">CINEMA ARCHIVE / DAILY EXHIBITION</div>', unsafe_allow_html=True)
st.title("박스오피스 아카이브")
st.markdown(
    '<div class="gallery-subtitle">하루의 관객 흐름을 수집하고, 영화 한 편을 작은 전시처럼 감상합니다.</div>',
    unsafe_allow_html=True,
)

selected_date = st.date_input(
    "조회할 날짜를 선택하세요 (어제까지 선택 가능)",
    value=yesterday,
    min_value=date(2004, 11, 11),
    max_value=yesterday,
    key="boxoffice_date_picker",
)
target_date = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")
st.caption(f"선택한 조회 기준일: **{display_date}**")

# 다른 날짜로 바꾸면 이전에 선택했던 영화는 초기화합니다.
if st.session_state.get("last_loaded_date") != target_date:
    st.session_state["selected_movie_key"] = ""
    st.session_state["last_loaded_date"] = target_date

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 5. 인증키를 비밀 금고에서 읽기
# ============================================================
# 인증키는 소스 코드에 절대 적지 않고 Streamlit Secrets에서 불러옵니다.
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    show_troubleshooting(
        "KOBIS 인증키를 찾을 수 없습니다.",
        'Settings → Secrets에 `KOBIS_KEY = "발급받은_실제_인증키"` 형식으로 등록하세요.',
    )
    st.stop()

if not isinstance(api_key, str) or not api_key.strip():
    show_troubleshooting("KOBIS 인증키가 비어 있습니다.", "Secrets의 KOBIS_KEY 값을 확인하세요.")
    st.stop()


# ============================================================
# 6. 선택한 날짜의 박스오피스 가져오기
# ============================================================
try:
    with st.spinner(f"{display_date} 박스오피스 자료를 불러오는 중..."):
        payload = fetch_boxoffice(api_key.strip(), target_date)
except requests.exceptions.Timeout:
    show_troubleshooting("KOBIS 응답 시간이 초과되었습니다.", "20초 안에 응답을 받지 못했습니다. 잠시 후 다시 시도하세요.")
    st.stop()
except requests.exceptions.RequestException as exc:
    show_troubleshooting("KOBIS API에 연결하지 못했습니다.", f"연결 오류: {exc}")
    st.stop()
except RuntimeError as exc:
    show_troubleshooting("KOBIS API 요청에 실패했습니다.", str(exc))
    st.stop()

# HTTP 상태가 200이어도 faultInfo가 있으면 정상 응답이 아닙니다.
if payload.get("faultInfo"):
    show_troubleshooting("KOBIS가 오류 정보를 반환했습니다.", describe_api_fault(payload["faultInfo"]))
    st.stop()

box_office_result = payload.get("boxOfficeResult")
if not isinstance(box_office_result, dict):
    show_troubleshooting("응답에 박스오피스 결과가 없습니다.", "KOBIS 응답에 boxOfficeResult가 있는지 확인하세요.")
    st.stop()

movie_list = box_office_result.get("dailyBoxOfficeList")
if not isinstance(movie_list, list) or len(movie_list) == 0:
    st.warning(f"📭 {display_date}: 그날은 아직 집계 전입니다.")
    st.info("선택한 날짜의 영화 목록이 비어 있습니다. 날짜를 바꾸거나 잠시 후 다시 확인하세요.")
    st.stop()


# ============================================================
# 7. 데이터 정리
# ============================================================
df = pd.DataFrame(movie_list)
required_columns = ["movieCd", "rank", "rankInten", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
for column in required_columns:
    if column not in df.columns:
        df[column] = ""

# KOBIS의 숫자는 문자열이므로 계산이 가능하게 정수로 바꿉니다.
for column in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]:
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

df["movieNm"] = df["movieNm"].fillna("").astype(str).replace("", "영화명 정보 없음")
df["openDt"] = df["openDt"].fillna("").astype(str).replace("", "정보 없음")
df["movieCd"] = df["movieCd"].fillna("").astype(str)
df = df.sort_values("rank", ascending=True).reset_index(drop=True)
df["_selection_key"] = [
    code if code else f"rank-{rank}-{idx}"
    for idx, (code, rank) in enumerate(zip(df["movieCd"], df["rank"]))
]

if df.empty:
    st.warning(f"📭 {display_date}: 그날은 아직 집계 전입니다.")
    st.stop()


# ============================================================
# 8. 1위 영화의 주요 지표 카드
# ============================================================
leader = df.iloc[0]
leader_name = str(leader["movieNm"])
leader_trophy = " 🏆" if int(leader["audiAcc"]) > 1_000_000 else ""
st.subheader(f"{display_date} 박스오피스 1위 · {leader_name}{leader_trophy}")
metric1, metric2, metric3 = st.columns(3)
with metric1:
    st.metric("일일 관객수", f"{int(leader['audiCnt']):,}명")
with metric2:
    st.metric("누적 관객수", f"{int(leader['audiAcc']):,}명")
with metric3:
    st.metric("스크린 수", f"{int(leader['scrnCnt']):,}개")

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 9. 관객수 상위 5편 그래프
# ============================================================
st.subheader("관객수 상위 5편")
top5 = df.sort_values("audiCnt", ascending=False).head(5).copy()
chart_df = top5.set_index("movieNm")[["audiCnt"]].rename(columns={"audiCnt": "관객수"})
st.bar_chart(chart_df)

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 10. 영화를 선택하면 장르별 애니메이션과 상세정보 표시
# ============================================================
st.subheader("영화 한 편을 선택해 장면 모티프 보기")
st.caption("장르에 맞춘 시네마틱 모션 그래픽과 KOBIS의 제작 정보를 함께 보여 줍니다.")

# 버튼을 두 열로 놓아 원하는 영화를 선택할 수 있게 합니다.
for start_idx in range(0, len(df), 2):
    button_columns = st.columns(2)
    for offset, column in enumerate(button_columns):
        row_idx = start_idx + offset
        if row_idx >= len(df):
            continue
        row = df.iloc[row_idx]
        trophy = " 🏆" if int(row["audiAcc"]) > 1_000_000 else ""
        button_label = f"{int(row['rank'])}위 · {row['movieNm']}{trophy}"
        with column:
            if st.button(button_label, key=f"pick_{target_date}_{row['_selection_key']}", use_container_width=True):
                st.session_state["selected_movie_key"] = row["_selection_key"]

selected_key = st.session_state.get("selected_movie_key", "")
selected_rows = df[df["_selection_key"] == selected_key]

if selected_rows.empty:
    st.info("위에서 영화 제목을 누르면 장면 애니메이션과 작품 정보가 이곳에 나타납니다.")
else:
    selected_movie = selected_rows.iloc[0]
    selected_name = str(selected_movie["movieNm"])
    selected_code = str(selected_movie["movieCd"]).strip()
    selected_audi = int(selected_movie["audiCnt"])
    selected_total = int(selected_movie["audiAcc"])
    selected_rank = int(selected_movie["rank"])

    movie_info = {}
    info_error = ""
    if selected_code:
        try:
            with st.spinner(f"{selected_name} 상세정보를 불러오는 중..."):
                movie_info = fetch_movie_info(api_key.strip(), selected_code)
            if "_error" in movie_info:
                info_error = str(movie_info["_error"])
                movie_info = {}
        except requests.exceptions.RequestException as exc:
            info_error = f"상세정보 API에 연결하지 못했습니다: {exc}"
    else:
        info_error = "영화 코드가 없어 상세정보 API를 조회하지 못했습니다."

    genres = names_from_api(movie_info.get("genres", []), "genreNm")
    directors = names_from_api(movie_info.get("directors", []), "peopleNm")
    actors = names_from_api(movie_info.get("actors", []), "peopleNm")
    audits = names_from_api(movie_info.get("audits", []), "watchGradeNm")
    genre_text = ", ".join(genres) if genres else "장르 정보 없음"
    director_text = ", ".join(directors) if directors else "감독 정보 없음"
    actor_text = ", ".join(actors[:5]) if actors else "출연진 정보 없음"
    runtime_raw = safe_text(movie_info.get("showTm"))
    runtime = f"{runtime_raw}분" if runtime_raw.isdigit() else runtime_raw
    year = safe_text(movie_info.get("prdtYear"))
    grade = ", ".join(audits) if audits else "관람등급 정보 없음"

    scene_html, scene_title, scene_note = make_cinematic_scene(selected_name, genre_text)
    escaped_name = html.escape(selected_name)
    escaped_genre = html.escape(genre_text)
    escaped_director = html.escape(director_text)
    escaped_actor = html.escape(actor_text)
    escaped_runtime = html.escape(runtime)
    escaped_year = html.escape(year)
    escaped_grade = html.escape(grade)
    escaped_scene_note = html.escape(scene_note)
    escaped_scene_title = html.escape(scene_title)

    st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)
    st.subheader(f"전시 작품 · {selected_name}")
    scene_col, detail_col = st.columns([1, 1.15], gap="large")

    with scene_col:
        # 영화 영상을 복제하지 않고 CSS 모션 그래픽으로 분위기를 만듭니다.
        st.markdown(scene_html, unsafe_allow_html=True)
        st.markdown(
            f'<div class="scene-note"><b>{escaped_scene_title}</b><br>{escaped_scene_note}</div>',
            unsafe_allow_html=True,
        )

    with detail_col:
        st.markdown(
            f"""
            <div style="background:rgba(255,255,252,.8);border:1px solid #d1cec5;padding:22px 23px;box-shadow:0 10px 24px rgba(35,34,29,.055);min-height:300px;">
              <div style="font-size:.68rem;letter-spacing:.2em;color:#777268;font-weight:800;margin-bottom:14px;">FILM DETAILS / KOBIS</div>
              <h3 style="font-size:1.55rem;margin-top:0;">{escaped_name}</h3>
              <p style="color:#6b675d;line-height:1.8;">{escaped_genre}</p>
              <div style="height:1px;background:#d5d1c7;margin:17px 0;"></div>
              <p><b>감독</b><br>{escaped_director}</p>
              <p><b>출연</b><br>{escaped_actor}</p>
              <p><b>제작 연도</b>　{escaped_year}<br>
                 <b>상영시간</b>　{escaped_runtime}<br>
                 <b>관람등급</b>　{escaped_grade}</p>
              <div style="height:1px;background:#d5d1c7;margin:17px 0;"></div>
              <p><b>선택한 날 관객수</b>　{selected_audi:,}명<br>
                 <b>누적 관객수</b>　{selected_total:,}명</p>
              <p style="font-size:.79rem;color:#777268;line-height:1.7;">애니메이션은 영화 제목·장르에서 착안한 시각적 해석입니다. KOBIS가 실제 영상이나 줄거리 장면을 제공하는 것은 아니므로, 실제 영화 장면을 재현한 것으로 표시하지 않습니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if info_error:
            st.warning(f"일부 상세정보를 가져오지 못했습니다. {info_error}")

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 11. 전체 일별 박스오피스 표
# ============================================================
st.subheader("일별 박스오피스 전체 목록")
st.caption("순위 상승은 빨간 위 화살표, 하락은 파란 아래 화살표로 표시합니다. 누적 관객이 100만 명을 넘으면 🏆가 붙습니다.")

html_rows = []
for _, row in df.iterrows():
    rank_change = int(row["rankInten"])
    if rank_change > 0:
        change_html = f'<span class="rise">↑ {rank_change}</span>'
    elif rank_change < 0:
        change_html = f'<span class="fall">↓ {abs(rank_change)}</span>'
    else:
        change_html = '<span class="steady">—</span>'

    movie_name = html.escape(str(row["movieNm"]))
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
        <thead><tr>
          <th>순위</th><th>순위 증감</th><th>영화명</th><th>개봉일</th>
          <th>관객수</th><th>누적관객</th><th>스크린수</th>
        </tr></thead><tbody>
    """ + "".join(html_rows) + """
      </tbody></table>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("자료 출처: 영화관입장권통합전산망(KOBIS) 일별 박스오피스 및 영화 상세정보 API")
