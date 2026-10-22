
import html
from datetime import date, datetime, timedelta
from urllib.parse import quote_plus, urlparse
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

# ============================================================
# 1. 기본 설정
# ============================================================
st.set_page_config(page_title="박스오피스 아카이브", page_icon="🎬", layout="wide")

BOXOFFICE_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)
MOVIE_INFO_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "movie/searchMovieInfo.json"
)

# ============================================================
# 2. 워홀의 실크스크린 팝아트에서 영감을 받은 디자인
#    반복 패널, 원색, 망점, 인쇄가 어긋난 듯한 제목 효과를 사용합니다.
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
      background-color:#fff4d6;
      background-image:
        radial-gradient(circle,rgba(15,15,15,.16) 1.1px,transparent 1.6px),
        linear-gradient(90deg,rgba(255,42,125,.16) 0 12%,transparent 12% 88%,rgba(0,198,208,.15) 88% 100%),
        linear-gradient(180deg,#fff8e7 0%,#f9edc9 100%);
      background-size:7px 7px,100% 100%,100% 100%;
      color:#171717;
    }
    .stApp::before {
      content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.12;
      background:repeating-linear-gradient(135deg,transparent 0 40px,rgba(0,0,0,.2) 41px 42px,transparent 43px 82px);
    }
    .block-container {max-width:1450px;padding-top:1.5rem;padding-bottom:4rem;position:relative;z-index:1;}
    h1,h2,h3 {color:#171717!important;font-weight:900!important;letter-spacing:-.035em;}
    h1 {font-size:clamp(2.1rem,4.3vw,3.7rem)!important;text-shadow:4px 3px 0 #00c9cf,-3px -2px 0 #ff4384;}
    h2 {text-shadow:2px 1px 0 rgba(255,67,132,.35);}
    p,label,[data-testid="stCaptionContainer"] {color:#302e28;}
    .gallery-kicker {display:inline-block;background:#ffe34c;border:2px solid #171717;box-shadow:3px 3px 0 #171717;padding:7px 10px;font-size:.72rem;font-weight:900;letter-spacing:.2em;margin-bottom:10px;transform:rotate(-1deg);}
    .gallery-subtitle {display:block;background:rgba(255,255,255,.48);border-left:6px solid #ff4384;padding:10px 13px;line-height:1.7;max-width:950px;}
    .warhol-strip {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;background:#171717;border:3px solid #171717;padding:4px;margin:12px 0 22px;box-shadow:7px 7px 0 #171717;}
    .warhol-cell {min-height:92px;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden;border:1px solid #171717;color:#171717;background-image:radial-gradient(rgba(0,0,0,.25) 1px,transparent 1.4px);background-size:6px 6px;}
    .warhol-cell:nth-child(6n+1){background-color:#ff4384}
    .warhol-cell:nth-child(6n+2){background-color:#ffe34c}
    .warhol-cell:nth-child(6n+3){background-color:#1ed4d0}
    .warhol-cell:nth-child(6n+4){background-color:#ff8a38}
    .warhol-cell:nth-child(6n+5){background-color:#a5e85b}
    .warhol-cell:nth-child(6n+6){background-color:#7885ff}
    .cell-symbol {font-size:clamp(1.7rem,3.5vw,3rem);font-weight:950;line-height:1;filter:drop-shadow(2px 2px 0 rgba(255,255,255,.55));animation:screenprintShift 4.5s steps(2) infinite;}
    .warhol-cell:nth-child(even) .cell-symbol{animation-delay:.55s}
    .cell-label{font-size:.58rem;letter-spacing:.14em;font-weight:950;margin-top:7px;}
    .museum-rule {height:3px;background:#171717;margin:1.35rem 0;box-shadow:0 3px 0 rgba(255,67,132,.55);}
    [data-testid="stMetric"] {background:#ffdf48;border:2px solid #171717;border-radius:0;padding:17px 18px;box-shadow:5px 5px 0 #171717;background-image:radial-gradient(rgba(0,0,0,.12) 1px,transparent 1.35px);background-size:7px 7px;}
    [data-testid="stMetricLabel"]{color:#2b2a23;font-weight:800}
    [data-testid="stMetricValue"]{color:#171717;font-weight:950}
    .stButton>button,.stLinkButton a {border:2px solid #171717;border-radius:0;background:#fff8df;color:#171717;font-weight:850;min-height:2.7rem;box-shadow:4px 4px 0 #171717;transition:transform .15s,box-shadow .15s,background .15s;}
    .stButton>button:hover,.stLinkButton a:hover {background:#ff4384;color:#171717;border-color:#171717;transform:translate(-1px,-1px);box-shadow:6px 6px 0 #171717;}
    [data-testid="stDateInput"] input {border-radius:0;background:#fffdf4;border:2px solid #171717;}
    .rise{color:#d70032;font-weight:950;white-space:nowrap}
    .fall{color:#1259b1;font-weight:950;white-space:nowrap}
    .steady{color:#555;font-weight:800;white-space:nowrap}
    .boxoffice-table{width:100%;border-collapse:collapse;background:#fffdf4;border:3px solid #171717;font-size:.94rem;}
    .boxoffice-table th{background:#171717;color:#fff9e3;padding:12px 10px;text-align:left;border:1px solid #171717;font-weight:900;white-space:nowrap;}
    .boxoffice-table td{padding:11px 10px;border:1px solid rgba(23,23,23,.28);font-weight:650;}
    .boxoffice-table tr:nth-child(6n+1){background:#ffb6cc}
    .boxoffice-table tr:nth-child(6n+2){background:#fff0a6}
    .boxoffice-table tr:nth-child(6n+3){background:#a9f0e8}
    .boxoffice-table tr:nth-child(6n+4){background:#ffd0a6}
    .boxoffice-table tr:nth-child(6n+5){background:#d6f1a2}
    .boxoffice-table tr:nth-child(6n+6){background:#c6ccff}
    .boxoffice-table tr:hover{outline:3px solid #171717;outline-offset:-3px;filter:saturate(1.2)}

    /* 장르에서 착안한 성숙한 시네마틱 모션 그래픽 */
    .cinema-stage{height:350px;position:relative;overflow:hidden;isolation:isolate;border:3px solid #171717;box-shadow:7px 7px 0 #171717;color:#f5f0e5;background:#171a1e;}
    .scene-topline{position:absolute;z-index:12;left:18px;top:16px;font-size:.63rem;letter-spacing:.2em;font-weight:800;color:rgba(248,244,233,.8)}
    .scene-lockup{position:absolute;z-index:12;left:18px;right:18px;bottom:15px;border-top:1px solid rgba(255,255,255,.4);padding-top:9px;display:flex;justify-content:space-between;align-items:end;gap:10px}
    .scene-lockup strong{font-size:clamp(.8rem,2vw,1.1rem);letter-spacing:.1em;font-weight:850}
    .scene-lockup span{font-size:.6rem;letter-spacing:.1em;color:rgba(250,247,238,.75);text-align:right}
    .scene-vignette{position:absolute;inset:0;z-index:10;pointer-events:none;box-shadow:inset 0 0 85px rgba(0,0,0,.7)}
    .scene-note{font-size:.84rem;line-height:1.7;color:#302e29;padding:12px 2px 0}

    /* 잠입·암살 모티프: 비, 고층 건물, 움직이는 인물 실루엣 */
    .scene-assassin{background:linear-gradient(180deg,#121923 0%,#303a43 45%,#090d12 100%)}
    .moon-glow{position:absolute;width:155px;height:155px;border-radius:50%;top:17px;right:18%;background:radial-gradient(circle,rgba(220,225,222,.6),rgba(157,177,190,.12) 45%,transparent 72%);filter:blur(2px)}
    .building{position:absolute;bottom:0;background:#0e1217;border-top:1px solid rgba(200,213,218,.16)}
    .building:after{content:"";position:absolute;inset:15px 9px 20px;background:repeating-linear-gradient(90deg,transparent 0 18px,rgba(165,181,190,.11) 19px 22px),repeating-linear-gradient(0deg,transparent 0 24px,rgba(165,181,190,.1) 25px 27px)}
    .b1{left:0;width:23%;height:75%}
    .b2{left:23%;width:22%;height:52%;background:#1a2027}
    .b3{right:0;width:28%;height:82%}
    .b4{right:25%;width:20%;height:44%;background:#202731}
    .lamp{position:absolute;z-index:2;top:-35px;left:52%;width:3px;height:210px;background:rgba(221,212,175,.75);box-shadow:0 0 25px 10px rgba(211,194,141,.17);transform:rotate(9deg)}
    .rain{position:absolute;z-index:4;inset:-30% -20%;opacity:.28;background:repeating-linear-gradient(104deg,transparent 0 25px,rgba(217,229,235,.5) 26px,transparent 27px 46px);animation:rainFall .7s linear infinite}
    .pavement{position:absolute;z-index:2;left:0;right:0;bottom:0;height:24%;background:linear-gradient(180deg,transparent,#080b0f 80%)}
    .figure{position:absolute;z-index:6;width:60px;height:155px;bottom:10%;filter:drop-shadow(4px 3px 5px rgba(0,0,0,.5))}
    .head{position:absolute;top:0;left:20px;width:21px;height:23px;border-radius:50%;background:#050608}
    .body{position:absolute;top:21px;left:9px;width:45px;height:75px;background:#06080b;clip-path:polygon(24% 0,72% 0,100% 100%,0 100%)}
    .leg{position:absolute;top:86px;width:15px;height:62px;background:#06080b;transform-origin:top center}
    .leg.l{left:16px}.leg.r{left:33px}
    .assassin{left:5%;animation:assassinMove 6.2s cubic-bezier(.5,0,.2,1) infinite}
    .assassin .leg.l{animation:legSwing .6s ease-in-out infinite}
    .assassin .leg.r{animation:legSwing .6s ease-in-out .3s infinite}
    .target{left:77%;animation:targetFade 6.2s steps(1) infinite;transform-origin:bottom center}
    .glint{position:absolute;z-index:8;top:40%;left:49%;width:2px;height:2px;background:#f3e7c2;opacity:0;box-shadow:0 0 3px 2px #f3e7c2;animation:glint 6.2s linear infinite}

    /* 액션·범죄·스릴러: 도시 추격 */
    .scene-action{background:linear-gradient(180deg,#1f2a35,#59636b 52%,#101419)}
    .skyline{position:absolute;bottom:0;left:0;right:0;height:55%;background:repeating-linear-gradient(90deg,#10151a 0 8%,#252e38 8% 10%,#10151a 10% 16%);clip-path:polygon(0 22%,10% 22%,10% 0,24% 0,24% 35%,36% 35%,36% 9%,52% 9%,52% 43%,67% 43%,67% 13%,84% 13%,84% 31%,100% 31%,100% 100%,0 100%)}
    .searchlight{position:absolute;top:-35%;right:8%;width:35%;height:135%;background:linear-gradient(180deg,rgba(218,224,212,.22),transparent 76%);clip-path:polygon(44% 0,54% 0,100% 100%,0 100%);animation:sweep 7s ease-in-out infinite alternate}
    .runner{position:absolute;bottom:13%;left:12%;width:48px;height:128px;animation:run 3.4s ease-in-out infinite alternate}
    .runner .head,.runner .body,.runner .leg{background:#080b0e}

    /* 공포·미스터리: 어두운 복도와 그림자 */
    .scene-horror{background:linear-gradient(90deg,#07090d,#24262b 48%,#08090c)}
    .door{position:absolute;width:29%;height:72%;right:18%;bottom:0;border:2px solid rgba(185,185,177,.35);background:linear-gradient(90deg,#111419,#292a2d 52%,#111318);box-shadow:0 0 35px rgba(190,194,182,.12)}
    .shadow-figure{position:absolute;width:80px;height:200px;left:8%;bottom:0;background:#030407;clip-path:polygon(39% 0,61% 0,70% 12%,73% 32%,100% 100%,0 100%,29% 34%,30% 13%);animation:creep 5s ease-in-out infinite alternate}
    .horror-light{position:absolute;top:-10%;right:20%;width:32%;height:120%;background:rgba(194,191,165,.12);filter:blur(16px);animation:flicker 3s steps(2) infinite}

    /* SF: 우주선과 행성 */
    .scene-scifi{background:radial-gradient(ellipse at 72% 37%,#364b64 0%,#1d2a40 31%,#080d18 72%)}
    .stars{position:absolute;inset:0;opacity:.7;background-image:radial-gradient(#eee8d8 1px,transparent 1.5px),radial-gradient(#8ca6bd 1px,transparent 1.5px);background-size:47px 51px,71px 63px;background-position:0 0,19px 23px;animation:stars 14s linear infinite}
    .planet{position:absolute;width:180px;height:180px;border-radius:50%;right:9%;top:14%;background:radial-gradient(circle at 30% 28%,#a9bdca,#4c6987 45%,#172338 75%);box-shadow:0 0 48px rgba(114,164,209,.32);animation:float 8s ease-in-out infinite}
    .spaceship{position:absolute;z-index:5;left:10%;top:49%;width:150px;height:32px;background:linear-gradient(180deg,#b9c3c7,#4a565f 48%,#111923 52%);clip-path:polygon(0 42%,56% 18%,100% 50%,57% 68%,15% 100%);animation:ship 7s ease-in-out infinite alternate}

    /* 멜로·로맨스: 노을과 도시의 실루엣 */
    .scene-romance{background:linear-gradient(180deg,#1b2330 0%,#6a5260 53%,#d0a28f 100%)}
    .romance-moon{position:absolute;width:120px;height:120px;border-radius:50%;top:14%;right:22%;background:radial-gradient(circle,#f4dfc6 0%,rgba(244,223,198,.65) 35%,transparent 72%)}
    .romance-city{position:absolute;left:0;right:0;bottom:0;height:47%;background:repeating-linear-gradient(90deg,#171a22 0 7%,#28262c 7% 9%,#141820 9% 16%);clip-path:polygon(0 35%,12% 35%,12% 0,26% 0,26% 46%,43% 46%,43% 15%,59% 15%,59% 34%,76% 34%,76% 4%,91% 4%,91% 42%,100% 42%,100% 100%,0 100%)}
    .person{position:absolute;z-index:5;bottom:11%;width:32px;height:118px;background:#12151b;clip-path:polygon(35% 0,65% 0,76% 18%,100% 100%,0 100%,24% 18%);animation:breathe 3.2s ease-in-out infinite}
    .person.p1{left:38%}.person.p2{left:53%;animation-delay:.7s}

    /* 분류하기 어려운 영화는 영사기 빛과 프레임으로 표현 */
    .scene-general{background:linear-gradient(135deg,#292c30,#131518 52%,#33312c)}
    .projector-screen{position:absolute;top:15%;left:21%;right:12%;height:63%;border:1px solid rgba(232,226,210,.36);background:linear-gradient(145deg,rgba(211,207,193,.17),rgba(122,130,139,.05));transform:perspective(600px) rotateY(-5deg)}
    .projector-beam{position:absolute;width:80%;height:120%;left:-9%;top:-10%;background:linear-gradient(110deg,rgba(225,219,197,.14),transparent 65%);clip-path:polygon(0 0,12% 0,100% 100%,62% 100%);animation:beam 4s ease-in-out infinite alternate}
    .film-frame{position:absolute;top:28%;left:37%;width:34%;height:34%;border:1px solid rgba(246,241,226,.45);animation:frameMove 5s ease-in-out infinite alternate}
    .film-frame:after{content:"";position:absolute;inset:12px;border:1px solid rgba(246,241,226,.2)}

    @keyframes screenprintShift{0%,100%{transform:translate(0,0)}50%{transform:translate(2px,-1px)}}
    @keyframes rainFall{from{transform:translate(-3%,-4%)}to{transform:translate(3%,4%)}}
    @keyframes assassinMove{0%,10%{left:5%;transform:scale(.94)}46%,62%{left:48%;transform:scale(1)}70%,78%{left:53%;transform:scale(.98)}100%{left:5%;transform:scale(.94)}}
    @keyframes legSwing{0%,100%{transform:rotate(13deg)}50%{transform:rotate(-13deg)}}
    @keyframes targetFade{0%,66%{opacity:1;transform:translateY(0)}70%{opacity:.55;transform:translateY(5px)}73%,92%{opacity:.12;transform:translateY(18px)}100%{opacity:1;transform:translateY(0)}}
    @keyframes glint{0%,67%,75%,100%{opacity:0;transform:scale(1)}70%{opacity:.95;transform:scale(13)}72%{opacity:.05;transform:scale(2)}}
    @keyframes sweep{from{transform:rotate(-18deg);opacity:.2}to{transform:rotate(18deg);opacity:.62}}
    @keyframes run{from{transform:translateX(0) skewX(-3deg)}to{transform:translateX(190px) skewX(5deg)}}
    @keyframes creep{from{left:8%;transform:scaleX(.9)}to{left:35%;transform:scaleX(1.35)}}
    @keyframes flicker{0%,90%,100%{opacity:.65}92%{opacity:.1}94%{opacity:.8}}
    @keyframes stars{from{background-position:0 0,19px 23px}to{background-position:70px 45px,-31px 80px}}
    @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
    @keyframes ship{from{transform:translateX(0) rotate(-3deg)}to{transform:translateX(90px) rotate(2deg)}}
    @keyframes breathe{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
    @keyframes beam{from{opacity:.4;transform:translateX(0)}to{opacity:.9;transform:translateX(18px)}}
    @keyframes frameMove{from{transform:translateX(-13px) rotate(-2deg);opacity:.6}to{transform:translateX(16px) rotate(2deg);opacity:1}}
    @media(prefers-reduced-motion:reduce){.cinema-stage *,.warhol-cell *{animation:none!important}}
    @media(max-width:650px){.warhol-strip{grid-template-columns:repeat(3,minmax(0,1fr))}.warhol-cell{min-height:72px}.cinema-stage{height:300px}.scene-lockup{left:12px;right:12px;bottom:12px}.boxoffice-table{font-size:.8rem}.boxoffice-table th,.boxoffice-table td{padding:7px 5px}}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 오류 처리 및 API 함수
# ============================================================
def show_troubleshooting(title: str, details: str = "") -> None:
    """오류가 발생하면 한국어로 확인할 사항을 안내합니다."""
    st.error(title)
    if details:
        st.write(details)
    st.markdown(
        "**확인해 보세요**\n"
        "- Streamlit Cloud의 Settings → Secrets에 `KOBIS_KEY`가 등록되어 있는지 확인하세요.\n"
        "- 인증키 앞뒤에 공백이 없는지, 키가 유효한지 확인하세요.\n"
        "- 선택한 날짜의 자료가 KOBIS에서 공개되었는지 확인하세요.\n"
        "- 인터넷 연결과 KOBIS API 상태를 확인한 뒤 다시 실행하세요."
    )


def describe_api_fault(fault_info) -> str:
    """KOBIS 오류 상자에서 코드와 메시지를 가능한 한 찾아냅니다."""
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
    """선택한 날짜의 일별 박스오피스를 요청합니다."""
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
    """선택한 영화의 장르, 감독, 출연진 등 상세정보를 요청합니다."""
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
    """KOBIS가 반환한 목록에서 이름을 뽑습니다."""
    if not isinstance(items, list):
        return []
    return [str(item[key]) for item in items if isinstance(item, dict) and item.get(key)]


def safe_text(value) -> str:
    """빈 항목은 '정보 없음'으로 표시합니다."""
    if value is None or str(value).strip() in ("", "None"):
        return "정보 없음"
    return str(value).strip()


def cinematic_scene(movie_title: str, genre_text: str) -> tuple[str, str, str]:
    """장르나 제목에서 모티프를 골라 CSS로 만든 시네마틱 장면을 반환합니다.

    KOBIS API 자체에는 실제 예고편 영상이나 줄거리 장면이 없습니다.
    따라서 이 장면은 공식 예고편을 분석해 복제한 장면이 아니라, 제목/장르에서
    착안한 창작 모션 그래픽입니다.
    """
    combined = f"{movie_title.lower()} {genre_text.lower()}"

    if any(word in combined for word in ["암살", "암살자", "킬러", "어쌔신", "저격", "hitman", "assassin", "sniper"]):
        title = "SHADOW OPERATION"
        note = "비 내리는 골목과 고층 건물 사이로 인물이 잠입합니다. 빛의 번쩍임과 짧은 컷 전환으로 첩보·암살 장르의 긴장감을 표현합니다."
        scene = """
        <div class="cinema-stage scene-assassin">
          <div class="moon-glow"></div>
          <div class="building b1"></div><div class="building b2"></div><div class="building b3"></div><div class="building b4"></div>
          <div class="lamp"></div><div class="rain"></div><div class="pavement"></div>
          <div class="figure target"><span class="head"></span><span class="body"></span><span class="leg l"></span><span class="leg r"></span></div>
          <div class="figure assassin"><span class="head"></span><span class="body"></span><span class="leg l"></span><span class="leg r"></span></div>
          <div class="glint"></div><div class="scene-topline">CINEMATIC MOTION STUDY / 01</div>
          <div class="scene-lockup"><strong>SHADOW OPERATION</strong><span>STEALTH · NOIR · CUT</span></div><div class="scene-vignette"></div>
        </div>"""
    elif any(word in combined for word in ["공포", "호러", "귀신", "저주", "horror", "halloween", "미스터리"]):
        title = "THE LAST DOOR"
        note = "어두운 복도, 닫힌 문, 천천히 길어지는 그림자로 긴장감을 표현합니다."
        scene = """
        <div class="cinema-stage scene-horror"><div class="horror-light"></div><div class="door"></div><div class="shadow-figure"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 02</div><div class="scene-lockup"><strong>THE LAST DOOR</strong><span>SUSPENSE · SHADOW</span></div><div class="scene-vignette"></div>
        </div>"""
    elif any(word in combined for word in ["sf", "공상과학", "우주", "외계", "미래", "science fiction", "space"]):
        title = "BEYOND ORBIT"
        note = "별 사이를 이동하는 우주선과 멀리 떠 있는 행성으로 광활한 SF 분위기를 표현합니다."
        scene = """
        <div class="cinema-stage scene-scifi"><div class="stars"></div><div class="planet"></div><div class="spaceship"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 03</div><div class="scene-lockup"><strong>BEYOND ORBIT</strong><span>SPACE · DISTANCE</span></div><div class="scene-vignette"></div>
        </div>"""
    elif any(word in combined for word in ["멜로", "로맨스", "로맨틱", "연애", "사랑", "romance", "romantic"]):
        title = "AFTER THE CITY LIGHTS"
        note = "도시의 노을과 멀리 마주 선 두 인물을 통해 감정을 절제된 화면으로 표현합니다."
        scene = """
        <div class="cinema-stage scene-romance"><div class="romance-moon"></div><div class="romance-city"></div><div class="person p1"></div><div class="person p2"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 04</div><div class="scene-lockup"><strong>AFTER THE CITY LIGHTS</strong><span>LIGHT · DISTANCE</span></div><div class="scene-vignette"></div>
        </div>"""
    elif any(word in combined for word in ["액션", "범죄", "스릴러", "느와르", "추격", "첩보", "스파이", "action", "crime", "thriller", "spy"]):
        title = "NIGHT PURSUIT"
        note = "도시의 고층 건물, 탐색등, 옥상을 가로지르는 실루엣으로 추격 장면을 표현합니다."
        scene = """
        <div class="cinema-stage scene-action"><div class="skyline"></div><div class="searchlight"></div>
          <div class="runner"><span class="head"></span><span class="body"></span><span class="leg l"></span><span class="leg r"></span></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 05</div><div class="scene-lockup"><strong>NIGHT PURSUIT</strong><span>URBAN · MOTION</span></div><div class="scene-vignette"></div>
        </div>"""
    else:
        title = "A FRAME IN THE DARK"
        note = "영사기의 빛과 움직이는 필름 프레임으로 영화관의 어둠 속에서 장면이 시작되는 순간을 표현합니다."
        scene = """
        <div class="cinema-stage scene-general"><div class="projector-screen"></div><div class="projector-beam"></div><div class="film-frame"></div>
          <div class="scene-topline">CINEMATIC MOTION STUDY / 06</div><div class="scene-lockup"><strong>A FRAME IN THE DARK</strong><span>LIGHT · FRAME · TIME</span></div><div class="scene-vignette"></div>
        </div>"""
    return scene, title, note


# ============================================================
# 4. 한국 시간 기준 날짜 선택
# ============================================================
now_korea = datetime.now(ZoneInfo("Asia/Seoul"))
yesterday = now_korea.date() - timedelta(days=1)

st.markdown('<div class="gallery-kicker">CINEMA ARCHIVE / POP ART EDITION</div>', unsafe_allow_html=True)
st.title("박스오피스 아카이브")
st.markdown(
    '<div class="gallery-subtitle">워홀의 실크스크린 팝아트에서 착안한 반복 이미지·원색·망점으로 하루의 영화 기록을 전시합니다.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="warhol-strip" aria-label="반복되는 팝아트 영화 필름 패널">
      <div class="warhol-cell"><div class="cell-symbol">🎬</div><div class="cell-label">FRAME 01</div></div>
      <div class="warhol-cell"><div class="cell-symbol">◉</div><div class="cell-label">REPEAT 02</div></div>
      <div class="warhol-cell"><div class="cell-symbol">FILM</div><div class="cell-label">SCREEN 03</div></div>
      <div class="warhol-cell"><div class="cell-symbol">✦</div><div class="cell-label">COLOR 04</div></div>
      <div class="warhol-cell"><div class="cell-symbol">▣</div><div class="cell-label">PRINT 05</div></div>
      <div class="warhol-cell"><div class="cell-symbol">🎞</div><div class="cell-label">FRAME 06</div></div>
    </div>
    """,
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

# 날짜가 바뀌면 이전에 선택한 영화는 초기화합니다.
if st.session_state.get("last_loaded_date") != target_date:
    st.session_state["selected_movie_key"] = ""
    st.session_state["last_loaded_date"] = target_date

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 5. 인증키는 Secrets에서만 읽기
# ============================================================
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
# 6. KOBIS에서 선택한 날짜의 데이터 가져오기
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

# HTTP 200이어도 faultInfo가 있으면 정상 응답이 아닙니다.
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
# 7. 응답 데이터 정리
# ============================================================
df = pd.DataFrame(movie_list)
required_columns = ["movieCd", "rank", "rankInten", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
for column in required_columns:
    if column not in df.columns:
        df[column] = ""

# KOBIS는 숫자도 문자열로 주므로 계산 가능한 정수로 변환합니다.
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
# 8. 1위 영화 지표 카드
# ============================================================
leader = df.iloc[0]
leader_trophy = " 🏆" if int(leader["audiAcc"]) > 1_000_000 else ""
st.subheader(f"{display_date} 박스오피스 1위 · {leader['movieNm']}{leader_trophy}")
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
# 10. 영화 선택, 시네마틱 애니메이션, 예고편
# ============================================================
st.subheader("영화 한 편을 선택해 장면 모티프와 상세정보 보기")
st.caption("영화마다 장르 기반 모션 그래픽을 보여 줍니다. 공식 예고편은 개별 검색 후 앱에서 재생할 수 있습니다.")

# 버튼을 두 열로 놓아 원하는 영화를 고를 수 있게 합니다.
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
    st.info("위에서 영화 제목을 누르면 애니메이션과 영화 정보가 나타납니다.")
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

    scene_html, scene_title, scene_note = cinematic_scene(selected_name, genre_text)
    trailer_query = quote_plus(f"{selected_name} 공식 예고편")
    trailer_search_url = f"https://www.youtube.com/results?search_query={trailer_query}"

    # HTML에 표시할 외부 문자열을 이스케이프해 안전하게 출력합니다.
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
        st.markdown(scene_html, unsafe_allow_html=True)
        st.markdown(
            f'<div class="scene-note"><b>{escaped_scene_title}</b><br>{escaped_scene_note}</div>',
            unsafe_allow_html=True,
        )
        st.link_button("▶ YouTube에서 이 영화의 공식 예고편 찾기", trailer_search_url, use_container_width=True)
        st.caption("검색 결과에서 제작사·배급사 등 공식 채널의 예고편을 확인해 주세요.")
        trailer_url = st.text_input(
            "예고편 URL을 붙여 넣으면 앱 안에서 재생됩니다",
            placeholder="https://www.youtube.com/watch?v=...",
            key=f"trailer_url_{target_date}_{selected_code or selected_rank}",
        )
        if trailer_url.strip():
            parsed_url = urlparse(trailer_url.strip())
            host = (parsed_url.hostname or "").lower()
            if host == "youtube.com" or host.endswith(".youtube.com") or host == "youtu.be":
                st.video(trailer_url.strip())
            else:
                st.warning("YouTube 예고편 URL을 붙여 넣어 주세요.")

    with detail_col:
        st.markdown(
            f"""
            <div style="background:rgba(255,255,252,.88);border:2px solid #171717;padding:22px 23px;box-shadow:6px 6px 0 #00c9cf;min-height:300px;">
              <div style="font-size:.68rem;letter-spacing:.2em;color:#777268;font-weight:850;margin-bottom:14px;">FILM DETAILS / KOBIS</div>
              <h3 style="font-size:1.55rem;margin-top:0;">{escaped_name}</h3>
              <p style="line-height:1.8;">{escaped_genre}</p>
              <div style="height:2px;background:#171717;margin:17px 0;"></div>
              <p><b>감독</b><br>{escaped_director}</p>
              <p><b>출연</b><br>{escaped_actor}</p>
              <p><b>제작 연도</b>　{escaped_year}<br>
                 <b>상영시간</b>　{escaped_runtime}<br>
                 <b>관람등급</b>　{escaped_grade}</p>
              <div style="height:2px;background:#171717;margin:17px 0;"></div>
              <p><b>선택한 날 관객수</b>　{selected_audi:,}명<br>
                 <b>누적 관객수</b>　{selected_total:,}명</p>
              <p style="font-size:.79rem;color:#777268;line-height:1.7;">이 모션 그래픽은 제목·장르에서 착안한 창작 장면입니다. KOBIS API는 실제 예고편과 상세 줄거리를 제공하지 않으므로 실제 장면을 자동 분석해 재현한 것은 아닙니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if info_error:
            st.warning(f"일부 상세정보를 가져오지 못했습니다. {info_error}")

st.markdown('<div class="museum-rule"></div>', unsafe_allow_html=True)


# ============================================================
# 11. 전체 박스오피스 표
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
