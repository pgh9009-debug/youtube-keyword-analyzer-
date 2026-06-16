import os
import re
import hashlib
import html as _html
from datetime import datetime, timedelta
from collections import Counter
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly_dark"
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController
from youtube_analyzer import YouTubeAnalyzer
from keyword_extractor import get_search_query
import auth
import storage

load_dotenv()

st.set_page_config(page_title="마케팅신", page_icon="📊", layout="wide")

_cookies = CookieController()

st.markdown("""
<style>
/* ── 기본 배경 & 텍스트 ── */
html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"] > .main {
    background-color: #0d0d0d !important;
    color: #e8e8e8 !important;
}
[data-testid="stHeader"] { background: #0d0d0d !important; }
[data-testid="block-container"] { padding-top: 2rem !important; }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #222 !important;
}
[data-testid="stSidebar"] * { color: #e8e8e8 !important; }
[data-testid="stSidebar"] .stRadio label { color: #e8e8e8 !important; }
[data-testid="stSidebar"] hr { border-color: #2a2a2a !important; }

/* ── 라디오 버튼 ── */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    padding: 6px 10px !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    transition: background .15s !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background: #1e1e1e !important;
}

/* ── 입력 필드 ── */
input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #1a1a1a !important;
    color: #f0f0f0 !important;
    border: 1px solid #2e2e2e !important;
    border-radius: 8px !important;
}
input:focus, textarea:focus {
    border-color: #ffffff !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,.1) !important;
}
input::placeholder, textarea::placeholder { color: #555 !important; }

/* ── 슬라이더 ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #fff !important;
}
[data-testid="stSlider"] div[data-testid="stSliderThumbValue"] { color: #ccc !important; }

/* ── 버튼 ── */
button[kind="primary"], [data-testid="baseButton-primary"] {
    background: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: opacity .15s !important;
}
button[kind="primary"]:hover, [data-testid="baseButton-primary"]:hover { opacity: .85 !important; }
button[kind="secondary"], [data-testid="baseButton-secondary"] {
    background: #1a1a1a !important;
    color: #e8e8e8 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    transition: border-color .15s, background .15s !important;
}
button[kind="secondary"]:hover, [data-testid="baseButton-secondary"]:hover {
    border-color: #888 !important;
    background: #222 !important;
}

/* ── 폼 ── */
[data-testid="stForm"] {
    background: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* ── 탭 ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #111 !important;
    border-bottom: 1px solid #222 !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #888 !important;
    border-radius: 6px 6px 0 0 !important;
    border: none !important;
    font-size: .85em !important;
    padding: 8px 14px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #1e1e1e !important;
    color: #fff !important;
    border-bottom: 2px solid #fff !important;
}

/* ── 메트릭 ── */
[data-testid="stMetric"] {
    background: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stMetricLabel"] { color: #888 !important; font-size: .8em !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-size: 1.5em !important; }

/* ── expander ── */
[data-testid="stExpander"] {
    background: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: #ccc !important; }

/* ── 구분선 ── */
hr { border-color: #222 !important; }

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] iframe { filter: invert(0.88) hue-rotate(180deg) !important; border-radius: 8px !important; }

/* ── 알림 박스 ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid #333 !important;
}
.stSuccess { background: #0d1f12 !important; color: #6fcf97 !important; }
.stWarning { background: #1f1a0d !important; color: #f2c94c !important; }
.stError   { background: #1f0d0d !important; color: #eb5757 !important; }
.stInfo    { background: #0d131f !important; color: #56b4d3 !important; }

/* ── 셀렉트박스 ── */
[data-baseweb="select"] div {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
    border-color: #2e2e2e !important;
}
[data-baseweb="popover"] { background-color: #1a1a1a !important; }
[data-baseweb="menu"] { background-color: #1a1a1a !important; }
[data-baseweb="option"]:hover { background-color: #2a2a2a !important; }

/* ── 진행바 ── */
[data-testid="stProgressBar"] > div {
    background: #1e1e1e !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #ffffff, #aaaaaa) !important;
    border-radius: 4px !important;
}

/* ── 캡션 & 마크다운 ── */
.stCaption, [data-testid="stCaptionContainer"] { color: #666 !important; }
h1, h2, h3, h4 { color: #f0f0f0 !important; }
a { color: #b0b0b0 !important; }
a:hover { color: #fff !important; }

/* ── 로그인 화면 카드 ── */
.login-card {
    background: #141414;
    border: 1px solid #222;
    border-radius: 14px;
    padding: 32px;
}

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 로그인 체크
# ══════════════════════════════════════════════════════════
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.session_token = ''

# ── 쿠키로 자동 로그인 ─────────────────────────────────────
# streamlit-cookies-controller 는 쿠키를 비동기로 로드함.
# getAll() == None  → 아직 미로드 (첫 렌더): 로딩 화면을 보여주고 대기
# getAll() == dict  → 로드 완료: 토큰 확인 후 자동 로그인 or 로그인 폼 표시
if not st.session_state.logged_in:
    _all_cookies = _cookies.getAll()

    if _all_cookies is None:
        # 쿠키 컨트롤러 초기화 중 — 다음 렌더를 기다림
        with st.container():
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_c = st.columns([1, 2, 1])[1]
            col_c.markdown("#### 📊 마케팅신")
            col_c.caption("로딩 중…")
        st.stop()

    _saved_token = _all_cookies.get('yt_session')
    if _saved_token:
        _saved_user = auth.verify_session(_saved_token)
        if _saved_user:
            st.session_state.logged_in = True
            st.session_state.username = _saved_user
            st.session_state.session_token = _saved_token
            st.rerun()

if not st.session_state.logged_in:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:60vh;padding-top:60px">
        <div style="font-size:2.6rem;font-weight:800;letter-spacing:-1px;
                    color:#fff;margin-bottom:4px">마케팅신</div>
        <div style="font-size:.9rem;color:#555;margin-bottom:40px">
            YouTube 키워드 인텔리전스 플랫폼
        </div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div style="background:#141414;border:1px solid #222;border-radius:14px;
                    padding:28px 28px 20px">
            <div style="font-size:1rem;font-weight:600;color:#e8e8e8;
                        margin-bottom:18px;text-align:center">로그인</div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            uname = st.text_input("아이디", label_visibility="collapsed", placeholder="아이디")
            pw    = st.text_input("비밀번호", type="password", label_visibility="collapsed", placeholder="비밀번호")
            submitted = st.form_submit_button("로그인", use_container_width=True, type="primary")
        if submitted:
            if auth.verify(uname, pw):
                _token = auth.create_session(uname, days=30)
                _cookies.set('yt_session', _token, max_age=30 * 24 * 3600)
                st.session_state.logged_in = True
                st.session_state.username = uname
                st.session_state.session_token = _token
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
    st.stop()

# ══════════════════════════════════════════════════════════
# 로그인 후 메인 앱
# ══════════════════════════════════════════════════════════
username = st.session_state.username

_SEED_LABELS = [
    '기본 (관련도+조회수)',
    '최신인기 (날짜+평점, 최근1년)',
    '숨겨진발굴 (평점+날짜, 최근2년)',
    '급상승 (조회수+관련도, 최근6개월)',
]

def get_user_seed_offset(uname: str) -> int:
    """사용자별 고유 시드 오프셋 — 같은 키워드를 다른 사용자가 검색해도 서로 다른 결과"""
    return int(hashlib.md5(uname.encode()).hexdigest(), 16) % 4

if 'run_keyword' not in st.session_state:
    st.session_state.run_keyword = ''
if 'refresh_seed' not in st.session_state:
    st.session_state.refresh_seed  = 0    # 0=기본, 1=최신인기, 2=숨겨진발굴, 3=급상승
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0    # 현재 키워드에서 사용한 새로고침 횟수 (최대 3)
if 'history_view' not in st.session_state:
    # 새로고침 후에도 오늘 가장 최근 검색 결과를 자동 복원
    _today_hist = storage.get_search_history(username)
    st.session_state.history_view = _today_hist[0] if _today_hist else None
if 'trending_keywords'      not in st.session_state:
    st.session_state.trending_keywords      = []
if 'trending_selected'      not in st.session_state:
    st.session_state.trending_selected      = ''
if 'trending_analysis'      not in st.session_state:
    st.session_state.trending_analysis      = None
if 'trending_period'        not in st.session_state:
    st.session_state.trending_period        = 'week'
if 'trending_refresh_seed'  not in st.session_state:
    st.session_state.trending_refresh_seed  = 0
if 'trending_refresh_count' not in st.session_state:
    st.session_state.trending_refresh_count = 0
if 'custom_kw_input'        not in st.session_state:
    st.session_state.custom_kw_input        = ''
if 'custom_kw_results'      not in st.session_state:
    st.session_state.custom_kw_results      = None

# 사용자별 API 키 로드 (users.json → 없으면 env fallback, 관리자 전용)
if 'api_key' not in st.session_state:
    _stored_key = auth.get_api_key(username)
    if _stored_key:
        st.session_state.api_key = _stored_key
    elif username == 'admin':
        st.session_state.api_key = os.getenv("YOUTUBE_API_KEY", "")
    else:
        st.session_state.api_key = ''

# 세션 시작 시 파일에서 오늘 API 사용량 복원 (날짜 바뀌면 자동 0)
if 'api_units_used' not in st.session_state:
    st.session_state.api_units_used = storage.get_api_usage(username)

_api_bar = _api_text = None  # 사이드바 API 사용량 플레이스홀더

# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-size:1.25rem;font-weight:800;letter-spacing:-.5px;
                color:#fff;margin-bottom:2px">마케팅신</div>
    <div style="font-size:.72rem;color:#444;margin-bottom:12px">
        YouTube Intelligence
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.82rem;color:#666;margin-bottom:8px'>"
                f"👤 {auth.display_name(username)}</div>", unsafe_allow_html=True)
    if st.button("로그아웃", use_container_width=True):
        _tok = st.session_state.get('session_token', '')
        if _tok:
            auth.revoke_session(_tok)
            _cookies.remove('yt_session')
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.run_keyword = ''
        st.session_state.session_token = ''
        st.rerun()
    st.divider()

    page = st.radio("페이지", ["🔍 키워드 분석", "🔥 트렌딩", "📺 쇼츠 분석기", "📌 저장된 영상", "⚙️ 팀 관리"], label_visibility="collapsed")
    st.divider()

    if page == "🔍 키워드 분석":
        st.header("분석 설정")

        # ── API 키 (사용자별 저장) ─────────────────────────
        with st.form("api_key_form"):
            api_key_input = st.text_input(
                "YouTube API 키",
                value=st.session_state.get('api_key', ''),
                type="password",
                placeholder="AIza..." if not st.session_state.get('api_key') else "",
            )
            api_key_saved = st.form_submit_button("✅ 적용", use_container_width=True)

        if api_key_saved and api_key_input.strip():
            _k = api_key_input.strip()
            auth.save_api_key(username, _k)
            st.session_state.api_key = _k
            st.success("API 키가 저장되었습니다.")

        api_key = st.session_state.get('api_key', '')

        with st.form("search_form"):
            keyword_input = st.text_input("검색 키워드", placeholder="예: 주식 투자", key="kw_main")
            max_results = st.slider("최대 결과 수", 10, 50, 20, step=5)
            run = st.form_submit_button("🔍 분석 시작", type="primary", use_container_width=True)
        st.divider()
        st.markdown("**키워드 비교 (선택)**")
        with st.form("compare_form"):
            keyword_b = st.text_input("비교 키워드", placeholder="예: 부동산 투자", key="kw_b")
            run_compare = st.form_submit_button("⚖️ 비교 분석", use_container_width=True)

        # API 사용량 (사용자별, st.empty로 분석 완료 후 즉시 갱신)
        st.divider()
        st.markdown("**📊 오늘 내 API 사용량**")
        _api_bar = st.empty()
        _api_text = st.empty()
        st.caption("분析 1회 ≈ 202 유닛 · 2시간 내 동일 검색은 0 유닛 (캐시 적용)")
        _u = st.session_state.get('api_units_used', 0)
        _api_bar.progress(min(int(_u / 10_000 * 100), 100))
        _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")

        # ── 오늘 검색 목록 ─────────────────────────────────
        _today_hist = storage.get_search_history(username)
        if _today_hist:
            st.divider()
            st.markdown("**📋 오늘 검색 목록**")
            for _entry in _today_hist:
                _is_active = (
                    st.session_state.get('history_view') is not None
                    and st.session_state.history_view.get('keyword') == _entry['keyword']
                )
                _btn_label = f"{'▶ ' if _is_active else ''}{_entry['time']} {_entry['keyword']}"
                if st.button(_btn_label, key=f"hist_{_entry['keyword']}", use_container_width=True,
                             type="primary" if _is_active else "secondary"):
                    st.session_state.history_view = _entry
                    st.session_state.run_keyword = ''
                    st.rerun()
    else:
        api_key = st.session_state.get('api_key', '')
        keyword_input = ''
        run = False
        keyword_b = ''
        run_compare = False

if run:
    st.session_state.run_keyword   = keyword_input
    st.session_state.history_view  = None
    st.session_state.refresh_seed  = get_user_seed_offset(username)   # 사용자별 고유 시작 시드
    st.session_state.refresh_count = 0   # 새 키워드마다 새로고침 횟수 리셋

# ══════════════════════════════════════════════════════════
# 헬퍼 함수
# ══════════════════════════════════════════════════════════
def run_analysis(api_key, keyword, max_results, refresh_seed=0):
    # ── 캐시 확인 (2시간 TTL, 팀원 공유) ──────────────────────
    cached = storage.get_search_cache(keyword, refresh_seed)
    if cached:
        st.toast("캐시된 결과를 불러왔습니다 (API 0 유닛)", icon="⚡")
        return (cached['results'], cached['channels'], cached['related_kw'],
                cached['angle_kw'], cached['title_patterns'])

    analyzer = YouTubeAnalyzer(api_key)
    results = analyzer.analyze_keyword(keyword, max_results, refresh_seed=refresh_seed)
    channels = analyzer.get_channel_analysis(results)
    related_kw = analyzer.get_related_keywords(keyword)
    angle_kw = analyzer.get_angle_keywords(keyword, results)
    title_patterns = analyzer.get_title_patterns(results)
    for v in results:
        ch = channels.get(v['channel_id'], {})
        v['subscriber_count'] = ch.get('subscriber_count', 1)
    # API 유닛 누적: search×2(200) + videos.list(1~2) + channels(1) ≈ 202
    st.session_state.api_units_used = storage.add_api_usage(202, st.session_state.username)

    # 결과 캐시 저장
    storage.set_search_cache(keyword, refresh_seed, {
        'results': results, 'channels': channels, 'related_kw': related_kw,
        'angle_kw': angle_kw, 'title_patterns': title_patterns,
    })
    return results, channels, related_kw, angle_kw, title_patterns


def fmt_num(n):
    """숫자를 잘리지 않는 짧은 포맷으로 변환 (1234567 → 123.5만)"""
    if n >= 100_000_000:
        return f"{n/100_000_000:.1f}억"
    if n >= 10_000:
        return f"{n/10_000:.1f}만"
    return f"{n:,}"


def render_kw_buttons(kw_list, prefix):
    """
    kw_list: [(keyword, label), ...] 형식
    label 예: '🔥 1위', '📈 4위', '3개 영상' 등
    """
    if not kw_list:
        return
    for idx, (kw, label) in enumerate(kw_list):
        # 3개씩 행으로 묶어서 렌더링
        if idx % 3 == 0:
            cols = st.columns(3)
        with cols[idx % 3]:
            st.caption(label)
            if st.button(kw, key=f"{prefix}_{idx}", use_container_width=True):
                st.session_state.run_keyword = kw
                st.rerun()


def save_btn(v, keyword):
    already = storage.is_saved(v['video_id'], username)
    label = "✅ 저장됨" if already else "📌 저장"
    if not already:
        if st.button(label, key=f"save_{v['video_id']}", use_container_width=True):
            storage.save_video(v, username, keyword)
            st.toast(f"저장했습니다: {v['title'][:30]}...")
            st.rerun()
    else:
        st.button(label, key=f"save_{v['video_id']}", disabled=True, use_container_width=True)


_CARD_CSS_INJECTED = False

def render_video_cards(data, keyword=''):
    """3열 카드 레이아웃.
    썸네일·제목·태그·채널·통계를 단일 HTML 블록(고정 높이)으로 묶어
    저장 버튼이 모든 카드에서 동일한 위치에 렌더링되도록 보장."""
    global _CARD_CSS_INJECTED
    if not _CARD_CSS_INJECTED:
        st.markdown("""<style>
.vc-thumb{width:100%;height:160px;object-fit:cover;border-radius:8px;display:block}
.vc-no-thumb{width:100%;height:160px;background:#1a1a1a;border-radius:8px;border:1px solid #222}
.vc-title{height:44px;overflow:hidden;margin:8px 0 4px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  font-weight:600;font-size:.88em;line-height:1.35em;color:#f0f0f0}
.vc-title a{text-decoration:none;color:#f0f0f0}
.vc-title a:hover{color:#fff;text-decoration:underline}
.vc-tags{height:18px;font-size:.72em;color:#555;
  overflow:hidden;white-space:nowrap;margin-bottom:3px}
.vc-meta{height:17px;font-size:.72em;color:#555;
  overflow:hidden;white-space:nowrap;text-overflow:ellipsis;margin-bottom:6px}
.vc-meta a{color:#555;text-decoration:none}
.vc-meta a:hover{color:#aaa}
.vc-stats{width:100%;border-collapse:collapse;font-size:.8em;margin-bottom:4px}
.vc-stats th{color:#555;font-weight:500;text-align:center;
  padding:2px 0;border-bottom:1px solid #222}
.vc-stats td{font-weight:700;text-align:center;padding:3px 0;color:#e8e8e8}
</style>""", unsafe_allow_html=True)
        _CARD_CSS_INJECTED = True

    for i in range(0, len(data), 3):
        row  = data[i:i+3]
        cols = st.columns(3)
        for col, v in zip(cols, row):
            with col:
                raw    = v['title']
                tags   = re.findall(r'#\S+', raw)
                ctitle = _html.escape(re.sub(r'\s*#\S+', '', raw).strip() or raw)
                ch_esc = _html.escape(v['channel_title'])
                tag_html = '  '.join(tags[:5]) if tags else '&nbsp;'
                thumb    = v.get('thumbnail', '')
                thumb_el = (f'<img class="vc-thumb" src="{thumb}">'
                            if thumb else '<div class="vc-no-thumb"></div>')
                ch_url   = f"https://www.youtube.com/channel/{v['channel_id']}"

                st.markdown(f"""<div>
{thumb_el}
<div class="vc-title"><a href="{v['url']}" target="_blank">{ctitle}</a></div>
<div class="vc-tags">{tag_html}</div>
<div class="vc-meta">📺 <a href="{ch_url}" target="_blank">{ch_esc}</a>&nbsp;·&nbsp;{v['published_at']}&nbsp;·&nbsp;⏱&nbsp;{v['duration_str']}</div>
<table class="vc-stats"><tr>
  <th>조회수</th><th>좋아요</th><th>댓글</th><th>참여율</th>
</tr><tr>
  <td>{fmt_num(v['view_count'])}</td><td>{fmt_num(v['like_count'])}</td>
  <td>{fmt_num(v['comment_count'])}</td><td>{v['engagement_rate']}%</td>
</tr></table></div>""", unsafe_allow_html=True)
                save_btn(v, keyword)
                st.divider()


def get_content_suggestions(keyword, related_kw, angle_kw):
    """인기 포맷 템플릿 + 연관/시각 키워드 조합으로 콘텐츠 주제 추천."""
    top_rel    = [kw for kw, _ in related_kw[:3]]
    top_angles = [kw for kw, _ in angle_kw[:3]]
    base = [
        {'title': f"{keyword} 완벽 정리 — 처음 시작하는 사람이 꼭 봐야 할 영상",
         'type': '📚 정보성', 'reason': '입문자 타겟 + 넓은 검색 유입'},
        {'title': f"아무도 알려주지 않는 {keyword}의 진짜 단점",
         'type': '⚠️ 반전형', 'reason': '역발상 제목 → 호기심 유발, 댓글 참여 ↑'},
        {'title': f"2025년 {keyword} 트렌드 완전 분석",
         'type': '🔥 트렌드', 'reason': '연도+트렌드 조합 → 시즌 검색에 강함'},
        {'title': f"{keyword} 할 때 절대 하면 안 되는 실수 TOP 5",
         'type': '⛔ 경고형', 'reason': '리스트+부정 프레이밍 → 클릭 충동 강함'},
        {'title': f"{keyword} 6개월 해봤더니 생긴 일 (솔직 후기)",
         'type': '📖 브이로그', 'reason': '체험 스토리 → 진정성·구독 전환율 ↑'},
        {'title': f"{keyword}으로 수익 내는 방법 (실제 사례 공개)",
         'type': '💰 수익화', 'reason': '실용+실제 사례 → 클릭률 우수'},
    ]
    if len(top_rel) >= 1:
        base.append({'title': f"{keyword} vs {top_rel[0]} — 뭘 선택해야 할까?",
                     'type': '⚖️ 비교형', 'reason': f"연관 키워드 '{top_rel[0]}'와 비교 구도 → 두 검색어 유입"})
    if len(top_rel) >= 2:
        base.append({'title': f"{top_rel[1]}을 활용한 {keyword} 전략",
                     'type': '🧩 조합형', 'reason': f"연관어 '{top_rel[1]}' 크로스오버 → 틈새 타겟"})
    for angle in top_angles[:2]:
        base.append({'title': f"{angle} 관점으로 보는 {keyword} — 이게 핵심이다",
                     'type': '🔀 시각전환', 'reason': f"다른 시각 키워드 '{angle}' 활용 → 차별화 포지셔닝"})
    return base[:10]


def render_chart_only(data, label):
    df = pd.DataFrame(data)
    fig = px.bar(df.head(10), x='view_count', y='title', orientation='h',
                 title=f"{label} 상위 10개 조회수",
                 labels={'view_count': '조회수', 'title': ''})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)


def render_full_analysis(results, channels, related_kw, angle_kw, title_patterns, keyword):
    shorts = [r for r in results if r['type'] == 'shorts']
    longform = [r for r in results if r['type'] == 'longform']

    # ── 연관 키워드 두 트랙 ────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🔍 검색량 높은 연관 키워드")
        with st.expander("📋 산정 기준", expanded=False):
            st.markdown(
                "- **데이터**: YouTube 자동완성 API (실시간 검색 빈도 반영)\n"
                "- **1위 = 검색량이 가장 높은 연관어**\n"
                "- **관련성 필터**: 원본 키워드 단어(2자↑)와 겹치는 제안만 포함 — 무관한 자동완성 제거\n"
                "- 버튼 클릭 시 해당 키워드로 즉시 재검색"
            )
        if related_kw:
            render_kw_buttons(related_kw, "rel")
        else:
            st.info("데이터를 불러오지 못했습니다.")
    with col_b:
        st.markdown("#### 🔀 다른 시각 키워드")
        with st.expander("📋 산정 기준", expanded=False):
            st.markdown(
                "- **가중 점수** = 조회수 가중치 × 최신성 가중치\n"
                "- 조회수 가중치: 10만 기준, 높을수록 최대 2배 (로그 스케일)\n"
                "- 최신성 가중치: 최근 영상 1.0 → 5년 이상 전 0.5\n"
                "- **필터 제외**: 원본 키워드 단어, #shorts·구독·좋아요 등 범용 태그\n"
                "- 숫자 = 해당 태그 등장 영상 수 (2개 이상만 표시)"
            )
        if angle_kw:
            angle_with_label = [(kw, f"{cnt}개 영상") for kw, cnt in angle_kw]
            render_kw_buttons(angle_with_label, "ang")
        else:
            st.info("태그 데이터가 부족합니다.")
    st.divider()

    # ── 요약 + CSV ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 영상", len(results))
    c2.metric("쇼츠", len(shorts))
    c3.metric("롱폼", len(longform))
    c4.metric("총 조회수", f"{sum(r['view_count'] for r in results):,}")
    df_all = pd.DataFrame(results)
    csv = df_all.to_csv(index=False).encode('utf-8-sig')
    st.download_button("⬇️ 전체 데이터 CSV 저장", csv, f"{keyword}_분석결과.csv", "text/csv")
    st.divider()

    # ── 탭 ───────────────────────────────────────────────
    tab_labels = ["📱 쇼츠", "🎬 롱폼", "🎯 기회 점수", "⚔️ 포맷 전략", "📝 제목·태그", "📅 시점·트렌드", "📡 채널", "📊 주간조회수"]
    tabs = st.tabs(tab_labels)

    # ════ 쇼츠 ════
    with tabs[0]:
        st.markdown("### 📱 쇼츠")
        if not shorts:
            st.info("쇼츠 결과가 없습니다.")
        else:
            render_video_cards(shorts, keyword)
            with st.expander("📊 쇼츠 차트 보기"):
                render_chart_only(shorts, "쇼츠")

    # ════ 롱폼 ════
    with tabs[1]:
        st.markdown("### 🎬 롱폼")
        _rc_lf = st.session_state.get('refresh_count', 0)
        _cs_lf = st.session_state.get('refresh_seed', 0)
        if _rc_lf < 3:
            if st.button(f"🔄 알고리즘 초기화 ({_rc_lf+1}/3)", key="refresh_longform"):
                st.session_state.refresh_seed = (_cs_lf + 1) % 4
                st.session_state.refresh_count = _rc_lf + 1
                st.session_state.run_keyword = keyword
                st.session_state.history_view = None
                st.rerun()
        else:
            st.caption("새로고침 3회 완료")
        if not longform:
            st.info("롱폼 결과가 없습니다.")
        else:
            render_video_cards(longform, keyword)
            with st.expander("📊 롱폼 차트 보기"):
                render_chart_only(longform, "롱폼")

    # ════ 기회 점수 ════
    with tabs[2]:
        st.markdown("### 🎯 키워드 기회 점수")
        st.caption("조회수 높은데 채널 규모가 작을수록 → 블루오션")
        df = pd.DataFrame(results)
        df['opportunity_ratio'] = df['view_count'] / df['subscriber_count'].clip(lower=100)
        max_r = df['opportunity_ratio'].max() or 1
        df['opportunity_score'] = (df['opportunity_ratio'] / max_r * 10).round(1)
        kw_score = round(df.head(10)['opportunity_score'].mean(), 1)
        small_pct = round(len(df[df['subscriber_count'] < 100_000]) / len(df) * 100)
        avg_subs = int(df['subscriber_count'].mean())

        c1, c2, c3 = st.columns(3)
        icon = "🟢" if kw_score >= 7 else "🟡" if kw_score >= 4 else "🔴"
        c1.metric("키워드 기회 점수", f"{icon} {kw_score} / 10")
        c2.metric("10만 이하 채널 비율", f"{small_pct}%")
        c3.metric("상위 채널 평균 구독자", f"{avg_subs:,}명")

        if kw_score >= 7:
            st.success("✅ 블루오션 가능성 높음")
        elif kw_score >= 4:
            st.warning("⚠️ 중간 경쟁 키워드 — 차별화 필요")
        else:
            st.error("🔴 레드오션 — 대형 채널이 상위 독식")

        fig = px.scatter(df, x='subscriber_count', y='view_count',
                         size='opportunity_score', color='opportunity_score',
                         hover_name='title', color_continuous_scale='RdYlGn',
                         title='채널 구독자 vs 조회수 (색상=기회 점수)',
                         labels={'subscriber_count': '채널 구독자', 'view_count': '조회수'})
        st.plotly_chart(fig, use_container_width=True)

        top_opp = df.nlargest(10, 'opportunity_score')[['title', 'channel_title', 'subscriber_count', 'view_count', 'opportunity_score', 'url']].copy()
        top_opp.columns = ['제목', '채널', '구독자', '조회수', '기회 점수', 'URL']
        top_opp['구독자'] = top_opp['구독자'].apply(lambda x: f"{x:,}")
        top_opp['조회수'] = top_opp['조회수'].apply(lambda x: f"{x:,}")
        st.dataframe(top_opp, column_config={"URL": st.column_config.LinkColumn("링크")}, use_container_width=True, hide_index=True)

    # ════ 포맷 전략 ════
    with tabs[3]:
        st.markdown("### ⚔️ 쇼츠 vs 롱폼 전략")
        avg_sv = int(sum(v['view_count'] for v in shorts) / len(shorts)) if shorts else 0
        avg_lv = int(sum(v['view_count'] for v in longform) / len(longform)) if longform else 0
        avg_se = round(sum(v['engagement_rate'] for v in shorts) / len(shorts), 2) if shorts else 0
        avg_le = round(sum(v['engagement_rate'] for v in longform) / len(longform), 2) if longform else 0

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📱 쇼츠")
            st.metric("평균 조회수", f"{avg_sv:,}")
            st.metric("평균 참여율", f"{avg_se}%")
            st.metric("영상 수", len(shorts))
        with col2:
            st.markdown("#### 🎬 롱폼")
            st.metric("평균 조회수", f"{avg_lv:,}")
            st.metric("평균 참여율", f"{avg_le}%")
            st.metric("영상 수", len(longform))

        st.divider()
        if avg_sv or avg_lv:
            vw = "쇼츠" if avg_sv > avg_lv else "롱폼"
            ew = "쇼츠" if avg_se > avg_le else "롱폼"
            if vw == ew:
                st.success(f"✅ **{vw}** 추천 — 조회수와 참여율 모두 우세")
            else:
                st.info(f"조회수 우세: **{vw}** / 참여율 우세: **{ew}**")

        fig = go.Figure([
            go.Bar(name='쇼츠', x=['평균 조회수'], y=[avg_sv], marker_color='#FF6B6B'),
            go.Bar(name='롱폼', x=['평균 조회수'], y=[avg_lv], marker_color='#4ECDC4'),
        ])
        fig.update_layout(title='쇼츠 vs 롱폼 평균 조회수', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        if longform:
            df_long = pd.DataFrame(longform)
            df_long['duration_min'] = df_long['duration_sec'] // 60
            bins = [0, 5, 10, 20, 30, 60, 999]
            bin_labels = ['5분 이하', '5~10분', '10~20분', '20~30분', '30~60분', '60분+']
            df_long['length_group'] = pd.cut(df_long['duration_min'], bins=bins, labels=bin_labels)
            grp = df_long.groupby('length_group', observed=True)['view_count'].mean().reset_index()
            grp.columns = ['길이 구간', '평균 조회수']
            fig2 = px.bar(grp, x='길이 구간', y='평균 조회수', title='롱폼 길이 구간별 평균 조회수')
            st.plotly_chart(fig2, use_container_width=True)

    # ════ 제목·태그 분석 ════
    with tabs[4]:
        st.markdown("### 📝 제목 패턴 & 태그 분석")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 제목에서 자주 나온 단어")
            if title_patterns:
                df_title = pd.DataFrame(title_patterns, columns=['단어', '빈도'])
                fig = px.bar(df_title.head(15), x='빈도', y='단어', orientation='h',
                             labels={'단어': '', '빈도': '등장 횟수'})
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### 공통 태그 TOP 20")
            all_tags = []
            for v in results:
                all_tags.extend(v.get('tags', []))
            tag_counts = Counter([t.lower() for t in all_tags]).most_common(20)
            if tag_counts:
                df_tags = pd.DataFrame(tag_counts, columns=['태그', '빈도'])
                fig2 = px.bar(df_tags, x='빈도', y='태그', orientation='h',
                              labels={'태그': '', '빈도': '등장 횟수'})
                fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("태그 데이터가 없습니다.")

        df_all2 = pd.DataFrame(results)
        df_all2['title_len'] = df_all2['title'].apply(len)
        fig3 = px.scatter(df_all2, x='title_len', y='view_count', hover_name='title',
                          title='제목 글자 수 vs 조회수',
                          labels={'title_len': '제목 글자 수', 'view_count': '조회수'})
        st.plotly_chart(fig3, use_container_width=True)

    # ════ 시점·트렌드 ════
    with tabs[5]:
        st.markdown("### 📅 업로드 시점 & 트렌드")
        df_time = pd.DataFrame(results)
        df_time['date'] = pd.to_datetime(df_time['published_at'])
        wd_map = {0:'월',1:'화',2:'수',3:'목',4:'금',5:'토',6:'일'}
        df_time['weekday_kr'] = df_time['date'].dt.weekday.map(wd_map)
        wd_order = ['월','화','수','목','금','토','일']

        col1, col2 = st.columns(2)
        with col1:
            wd_v = df_time.groupby('weekday_kr', sort=False)['view_count'].mean().reindex(wd_order).reset_index()
            wd_v.columns = ['요일', '평균 조회수']
            fig = px.bar(wd_v, x='요일', y='평균 조회수', title='요일별 평균 조회수')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            wd_c = df_time['weekday_kr'].value_counts().reindex(wd_order).reset_index()
            wd_c.columns = ['요일', '영상 수']
            fig2 = px.bar(wd_c, x='요일', y='영상 수', title='요일별 업로드 빈도')
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### 📈 트렌드 방향")
        now = pd.Timestamp.now()
        df_time['date'] = df_time['date'].dt.tz_localize(None) if df_time['date'].dt.tz is not None else df_time['date']
        recent = df_time[df_time['date'] >= now - timedelta(days=90)]
        mid = df_time[(df_time['date'] >= now - timedelta(days=365)) & (df_time['date'] < now - timedelta(days=90))]
        old = df_time[df_time['date'] < now - timedelta(days=365)]

        trend_rows = []
        for label_t, subset in [('최근 3개월', recent), ('3개월~1년', mid), ('1년 이상 전', old)]:
            if not subset.empty:
                trend_rows.append({'기간': label_t, '평균 조회수': int(subset['view_count'].mean()), '영상 수': len(subset)})

        if trend_rows:
            df_tr = pd.DataFrame(trend_rows)
            fig3 = px.bar(df_tr, x='기간', y='평균 조회수', text='영상 수', title='시기별 평균 조회수')
            fig3.update_traces(texttemplate='%{text}개', textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)
            if len(trend_rows) >= 2:
                r, o = trend_rows[0]['평균 조회수'], trend_rows[1]['평균 조회수']
                if r > o * 1.2:
                    st.success("📈 성장 중인 키워드 — 최근 영상이 더 높은 조회수를 받고 있습니다.")
                elif r < o * 0.8:
                    st.warning("📉 하락 중인 키워드 — 관심도가 줄어들고 있을 수 있습니다.")
                else:
                    st.info("➡️ 안정적인 키워드 — 꾸준한 수요가 있습니다.")

    # ════ 채널 ════
    with tabs[6]:
        st.markdown("### 📡 채널 분析")
        _rc_ch = st.session_state.get('refresh_count', 0)
        _cs_ch = st.session_state.get('refresh_seed', 0)
        if _rc_ch < 3:
            if st.button(f"🔄 알고리즘 초기화 ({_rc_ch+1}/3)", key="refresh_channel"):
                st.session_state.refresh_seed = (_cs_ch + 1) % 4
                st.session_state.refresh_count = _rc_ch + 1
                st.session_state.run_keyword = keyword
                st.session_state.history_view = None
                st.rerun()
        else:
            st.caption("새로고침 3회 완료")
        if not channels:
            st.info("채널 정보를 불러오지 못했습니다.")
        else:
            from youtube_analyzer import YouTubeAnalyzer as _YTA
            ch_videos_map = {}
            for v in results:
                ch_videos_map.setdefault(v['channel_id'], []).append(v)

            grade_color = {'S': '#FFD700', 'A': '#A8E063', 'B': '#74B9FF',
                           'C': '#B2BEC3', 'D': '#EDEDED'}
            grade_icons = {'S': '🏆', 'A': '🥇', 'B': '🥈', 'C': '🥉', 'D': '💤'}

            graded = []
            for ch in channels.values():
                ch_vids     = ch_videos_map.get(ch['channel_id'], [])
                avg_eng     = round(sum(v['engagement_rate'] for v in ch_vids) / len(ch_vids), 2) if ch_vids else 0
                view_ratio  = round(ch['avg_views_per_video'] / max(ch['subscriber_count'], 1) * 100, 1)
                avg_like    = round(sum(v['like_count'] / max(v['view_count'], 1) * 100 for v in ch_vids) / len(ch_vids), 2) if ch_vids else 0
                avg_cmt     = round(sum(v['comment_count'] / max(v['view_count'], 1) * 100 for v in ch_vids) / len(ch_vids), 3) if ch_vids else 0
                grade, grade_label, total_score = _YTA.grade_channel(ch, ch_vids)
                graded.append({
                    **ch,
                    'avg_engagement': avg_eng,
                    'view_ratio_pct': view_ratio,
                    'avg_like_rate':  avg_like,
                    'avg_cmt_rate':   avg_cmt,
                    'grade':          grade,
                    'grade_label':    grade_label,
                    'total_score':    total_score,
                })

            # ── 등급 기준 설명 ──────────────────────────────
            with st.expander("📋 채널 등급 산정 기준", expanded=False):
                st.markdown(
                    "**종합 점수** = 전환율(40%) + 좋아요율(35%) + 댓글율(15%) + 생산성(10%)\n\n"
                    "| 지표 | 5점 | 4점 | 3점 | 2점 | 1점 |\n"
                    "|---|---|---|---|---|---|\n"
                    "| 전환율 (조회수÷구독자) | ≥50% | ≥20% | ≥10% | ≥5% | <5% |\n"
                    "| 좋아요율 (좋아요÷조회수) | ≥5% | ≥3% | ≥1.5% | ≥0.5% | <0.5% |\n"
                    "| 댓글율 (댓글÷조회수) | ≥0.3% | ≥0.1% | ≥0.05% | ≥0.01% | <0.01% |\n"
                    "| 생산성 (총 업로드 수) | ≥500개 | ≥200개 | ≥50개 | ≥10개 | <10개 |\n\n"
                    "**등급**: S(4.0↑) · A(3.0↑) · B(2.0↑) · C(1.5↑) · D(1.5↓)"
                )

            # ── 등급별 요약 ─────────────────────────────────
            from collections import Counter as _C
            grade_counts = _C(g['grade'] for g in graded)
            gc1, gc2, gc3, gc4, gc5 = st.columns(5)
            gc1.metric("🏆 S등급", grade_counts.get('S', 0))
            gc2.metric("🥇 A등급", grade_counts.get('A', 0))
            gc3.metric("🥈 B등급", grade_counts.get('B', 0))
            gc4.metric("🥉 C등급", grade_counts.get('C', 0))
            gc5.metric("💤 D등급", grade_counts.get('D', 0))
            st.divider()

            # ── 등급 카드 ───────────────────────────────────
            for grade_val in ['S', 'A', 'B', 'C', 'D']:
                group = [g for g in graded if g['grade'] == grade_val]
                if not group:
                    continue
                gc = grade_color[grade_val]
                gi = grade_icons[grade_val]
                st.markdown(f"#### {gi} {grade_val}등급 채널")
                for i in range(0, len(group), 3):
                    row  = group[i:i+3]
                    cols = st.columns(3)
                    for col, ch in zip(cols, row):
                        with col:
                            st.markdown(
                                f"**[{ch['title']}]({ch['channel_url']})**&nbsp;&nbsp;"
                                f"<span style='background:{gc};padding:2px 8px;"
                                f"border-radius:4px;font-weight:bold;font-size:.85em'>"
                                f"{ch['grade_label']} ({ch['total_score']}/5.0)</span>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"| 구독자 | 영상당 조회 | 전환율 | 좋아요율 | 댓글율 |\n"
                                f"|---|---|---|---|---|\n"
                                f"| {fmt_num(ch['subscriber_count'])} "
                                f"| {fmt_num(ch['avg_views_per_video'])} "
                                f"| {ch['view_ratio_pct']}% "
                                f"| {ch['avg_like_rate']}% "
                                f"| {ch['avg_cmt_rate']}% |"
                            )
                            st.divider()

            # ── 전체 테이블 ─────────────────────────────────
            with st.expander("📋 전체 채널 테이블 보기"):
                df_ch = pd.DataFrame(graded)
                disp  = df_ch[['grade_label', 'total_score', 'title',
                                'subscriber_count', 'avg_views_per_video',
                                'view_ratio_pct', 'avg_like_rate',
                                'avg_cmt_rate', 'channel_url']].copy()
                disp.columns = ['등급', '점수', '채널명', '구독자',
                                 '영상당 조회', '전환율(%)', '좋아요율(%)', '댓글율(%)', '채널 링크']
                disp['구독자']    = disp['구독자'].apply(fmt_num)
                disp['영상당 조회'] = disp['영상당 조회'].apply(fmt_num)
                st.dataframe(disp,
                             column_config={"채널 링크": st.column_config.LinkColumn("채널 링크")},
                             use_container_width=True, hide_index=True)

    # ════ 주간조회수 ════
    with tabs[7]:
        st.markdown("### 📊 채널 주간 쇼츠 조회수 분석")
        st.caption("채널 링크를 입력하면 최근 4주 쇼츠의 주별 조회수·좋아요·댓글 합계를 분석합니다.")

        _wk_api = st.session_state.get('api_key', '')
        if not _wk_api:
            st.warning("API 키를 입력해주세요.")
        else:
            with st.form("weekly_shorts_form"):
                _wk_url = st.text_input("채널 링크",
                    placeholder="https://www.youtube.com/@채널명  또는  /channel/UCxxxx")
                _wk_submit = st.form_submit_button("📊 분석 시작", type="primary",
                                                    use_container_width=True)

            if _wk_submit and _wk_url.strip():
                with st.spinner("주간 쇼츠 분석 중..."):
                    try:
                        from youtube_analyzer import YouTubeAnalyzer as _WKA
                        _wk_analyzer = _WKA(_wk_api)
                        _wk_result   = _wk_analyzer.analyze_channel_shorts(_wk_url.strip())
                        storage.add_api_usage(102, st.session_state.username)
                        st.session_state['_wk_result'] = _wk_result
                    except Exception as _e:
                        st.error(f"API 오류: {_e}")
                        _wk_result = None

            _wk_result = st.session_state.get('_wk_result')
            if _wk_result:
                if not _wk_result.get('weeks') or _wk_result.get('total_shorts', 0) == 0:
                    st.warning(f"**{_wk_result['channel_name']}** 채널에서 최근 28일 내 쇼츠를 찾지 못했습니다.")
                else:
                    st.markdown(f"#### 📺 {_wk_result['channel_name']}")
                    st.caption(f"분석 쇼츠: {_wk_result['total_shorts']}개 | 한달 조회수 합계: {_wk_result['monthly_total']:,}회 | 평균: {_wk_result['monthly_avg']:,}회/편")

                    # ── 주별 테이블 ──────────────────────────────
                    rows = []
                    for w in _wk_result['weeks']:
                        rows.append({
                            '기간':         w['label'],
                            '쇼츠 수':      w['count'],
                            '조회수 합계':   w['total_views'],
                            '좋아요 합계':   w['total_likes'],
                            '댓글 합계':     w['total_comments'],
                            '편당 평균 조회수': w['avg_views'],
                        })
                    _wk_df = pd.DataFrame(rows)

                    st.dataframe(
                        _wk_df.style.format({
                            '조회수 합계': '{:,}',
                            '좋아요 합계': '{:,}',
                            '댓글 합계':   '{:,}',
                            '편당 평균 조회수': '{:,}',
                        }),
                        use_container_width=True, hide_index=True
                    )

                    st.divider()

                    # ── 월 평균 메트릭 ──────────────────────────
                    wm1, wm2, wm3 = st.columns(3)
                    wm1.metric("📅 월 평균 조회수/편", f"{_wk_result['monthly_avg']:,}회")
                    wm2.metric("📅 한달 총 조회수",    f"{_wk_result['monthly_total']:,}회")
                    wm3.metric("📅 분석 쇼츠 수",      f"{_wk_result['total_shorts']}개")

                    # ── 막대 차트 ────────────────────────────────
                    _chart_rows = [w for w in _wk_result['weeks'] if w['count'] > 0]
                    if len(_chart_rows) >= 2:
                        _fig_wk = px.bar(
                            x=[w['label'] for w in _chart_rows],
                            y=[w['total_views'] for w in _chart_rows],
                            text=[f"{w['total_views']:,}" for w in _chart_rows],
                            labels={'x': '기간', 'y': '조회수 합계'},
                            title="주별 쇼츠 조회수 합계",
                            color=[w['total_views'] for w in _chart_rows],
                            color_continuous_scale='Blues',
                        )
                        _fig_wk.update_traces(textposition='outside')
                        _fig_wk.update_layout(showlegend=False, coloraxis_showscale=False,
                                              yaxis_tickformat=',')
                        st.plotly_chart(_fig_wk, use_container_width=True)


# ══════════════════════════════════════════════════════════
# 페이지 라우팅
# ══════════════════════════════════════════════════════════
if page == "🔍 키워드 분석":
    st.markdown("""
    <div style="font-size:1.6rem;font-weight:800;color:#fff;
                letter-spacing:-.5px;margin-bottom:4px">키워드 분析</div>
    <div style="font-size:.82rem;color:#444;margin-bottom:20px">
        검색어를 입력하면 YouTube 트렌드·기회·채널을 분析합니다
    </div>
    """, unsafe_allow_html=True)
    trigger = st.session_state.run_keyword

    # ── 새 분석 실행 (run_keyword 가 세팅된 경우) ─────────────
    if trigger:
        if not api_key:
            st.error("API 키를 입력해주세요.")
            st.stop()

        search_query, extracted_kws, is_sent = get_search_query(trigger)
        if is_sent:
            search_query_display = '  +  '.join(extracted_kws)
        else:
            search_query = trigger

        seed = st.session_state.refresh_seed
        with st.spinner(f"'{search_query}' 분석 중… (알고리즘 모드 {seed+1}/3)"):
            try:
                results, channels, related_kw, angle_kw, title_patterns = \
                    run_analysis(api_key, search_query, max_results, refresh_seed=seed)
            except Exception as e:
                st.error(f"API 오류: {e}")
                st.stop()

        if not results:
            st.warning("검색 결과가 없습니다.")
            st.stop()

        # 결과를 history_view 에 저장하고 run_keyword 초기화 → 사이드바 갱신을 위해 rerun
        _snapshot = {
            'keyword':        search_query,
            'display_label':  trigger if is_sent else search_query,
            'time':           datetime.now().strftime('%H:%M'),
            'refresh_seed':   seed,
            'results':        results,
            'channels':       channels,
            'related_kw':     related_kw,
            'angle_kw':       angle_kw,
            'title_patterns': title_patterns,
        }
        st.session_state.history_view = _snapshot
        st.session_state.run_keyword  = ''
        storage.add_search_history(username, search_query, _snapshot)

        # API 사용량 즉시 갱신
        if _api_bar is not None:
            _u = st.session_state.get('api_units_used', 0)
            _api_bar.progress(min(int(_u / 10_000 * 100), 100))
            _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")

        st.rerun()   # 사이드바에 검색 목록 즉시 반영

    # ── 결과 표시 (history_view 에서) ────────────────────────
    hv = st.session_state.get('history_view')
    if hv:
        kw          = hv['keyword']
        disp_label  = hv.get('display_label', kw)
        cur_seed    = hv.get('refresh_seed', 0)

        st.markdown(f"## 🔎 `{disp_label}` 분석 결과")
        c_info, c_btn = st.columns([4, 1])
        refresh_count = st.session_state.get('refresh_count', 0)
        c_info.caption(
            f"알고리즘 모드: **{_SEED_LABELS[cur_seed % 4]}** · {hv['time']} 검색"
            + (f" · 새로고침 {refresh_count}/3회 사용" if refresh_count > 0 else "")
        )

        if refresh_count < 3:
            next_seed  = (cur_seed + 1) % 4
            next_label = _SEED_LABELS[next_seed]
            if c_btn.button(f"🔄 알고리즘 초기화 ({refresh_count+1}/3)",
                            help=f"다음 모드: {next_label}\n다른 기준으로 새 영상 셋을 가져옵니다 (≈304 유닛)"):
                st.session_state.refresh_seed  = next_seed
                st.session_state.refresh_count = refresh_count + 1
                st.session_state.run_keyword   = kw
                st.session_state.history_view  = None
                st.rerun()
        else:
            c_btn.caption("새로고침 3회 완료")

        render_full_analysis(hv['results'], hv['channels'], hv['related_kw'],
                             hv['angle_kw'], hv['title_patterns'], kw)

        # 키워드 비교
        if run_compare and keyword_b:
            st.divider()
            st.markdown(f"## ⚖️ 키워드 비교: `{kw}` vs `{keyword_b}`")
            with st.spinner(f"'{keyword_b}' 분석 중..."):
                try:
                    res_b, ch_b, _, _, _ = run_analysis(api_key, keyword_b, max_results)
                    for v in res_b:
                        v['subscriber_count'] = ch_b.get(v['channel_id'], {}).get('subscriber_count', 1)
                except Exception as e:
                    st.error(f"비교 키워드 오류: {e}")
                    res_b = []
            if res_b:
                results = hv['results']
                shorts_a = [r for r in results if r['type'] == 'shorts']
                long_a   = [r for r in results if r['type'] == 'longform']
                shorts_b = [r for r in res_b if r['type'] == 'shorts']
                long_b   = [r for r in res_b if r['type'] == 'longform']
                cmp = {
                    '평균 조회수': [int(sum(r['view_count'] for r in results)/len(results)),
                                    int(sum(r['view_count'] for r in res_b)/len(res_b))],
                    '평균 참여율(%)': [round(sum(r['engagement_rate'] for r in results)/len(results),2),
                                      round(sum(r['engagement_rate'] for r in res_b)/len(res_b),2)],
                    '쇼츠 수': [len(shorts_a), len(shorts_b)],
                    '롱폼 수': [len(long_a), len(long_b)],
                }
                df_cmp = pd.DataFrame(cmp, index=[kw, keyword_b]).T.reset_index()
                df_cmp.columns = ['지표', kw, keyword_b]
                st.dataframe(df_cmp, use_container_width=True, hide_index=True)
                fig = go.Figure([
                    go.Bar(name=kw,       x=['평균 조회수', '평균 참여율(%)'],
                           y=cmp['평균 조회수'][:1] + cmp['평균 참여율(%)'][:1]),
                    go.Bar(name=keyword_b, x=['평균 조회수', '평균 참여율(%)'],
                           y=cmp['평균 조회수'][1:] + cmp['평균 참여율(%)'][1:]),
                ])
                fig.update_layout(barmode='group', title='키워드 비교')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("사이드바에서 키워드를 입력하고 **🔍 분석 시작** 버튼을 눌러주세요.")

# ══════════════════════════════════════════════════════════
elif page == "🔥 트렌딩":
    st.markdown("""
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        🔥 트렌딩 키워드</div>
    <div style="font-size:.82rem;color:#444;margin-bottom:20px">
        YouTube 인기 영상 기반 — 지금 사람들이 많이 보는 주제를 파악하세요
    </div>""", unsafe_allow_html=True)

    if not api_key:
        st.warning("API 키가 없습니다. **🔍 키워드 분석** 페이지에서 YouTube API 키를 먼저 입력해주세요.")
        st.stop()

    # ── 기간 선택 + 불러오기 ────────────────────────────────
    c_period, c_btn = st.columns([3, 1])
    with c_period:
        period_opt = st.radio("기간", ["📅 일주일 트렌딩", "🗓️ 한달 인기"],
                              horizontal=True, label_visibility="collapsed")
    with c_btn:
        load_btn = st.button("🔍 키워드 불러오기", type="primary", use_container_width=True)

    period_code = 'week' if '일주일' in period_opt else 'month'

    if load_btn:
        with st.spinner("트렌딩 키워드 분析 중..."):
            _analyzer = YouTubeAnalyzer(api_key)
            try:
                _kws = _analyzer.get_trending_keywords(period=period_code)
            except Exception as _e:
                st.error(f"API 오류: {_e}")
                st.stop()
        if _kws:
            st.session_state.trending_keywords = _kws
            st.session_state.trending_period   = period_code
            st.session_state.trending_selected = ''
            st.session_state.trending_analysis = None
            _units = 1 if period_code == 'week' else 106
            st.session_state.api_units_used = storage.add_api_usage(_units, username)
            if _api_bar:
                _u = st.session_state.api_units_used
                _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
            st.rerun()
        else:
            st.warning("트렌딩 키워드를 불러오지 못했습니다. API 키와 할당량을 확인해주세요.")

    # ── 내 키워드 연관 검색어 분析 ──────────────────────────────
    st.divider()
    st.markdown("### 🎯 내 키워드 연관 검색어 분析")
    st.caption("영상으로 만들 키워드를 입력하면 검색량 순 연관어와 콘텐츠 추천을 바로 보여줍니다. (~101 유닛)")

    _ck_col1, _ck_col2 = st.columns([4, 1])
    with _ck_col1:
        _ck_input = st.text_input(
            "키워드", placeholder="예: 철학, 주식 투자, 다이어트",
            label_visibility="collapsed", key="ck_text_input"
        )
    with _ck_col2:
        _ck_run = st.button("🔍 분析", type="primary", use_container_width=True, key="ck_run_btn")

    if _ck_run and _ck_input.strip():
        _ck_kw = _ck_input.strip()
        _ck_hit = storage.get_trending_cache(_ck_kw, -1)  # seed -1 = 커스텀 키워드 캐시
        if _ck_hit:
            st.session_state.custom_kw_input   = _ck_kw
            st.session_state.custom_kw_results = tuple(_ck_hit)
            st.toast("캐시된 결과를 불러왔습니다 (API 0 유닛)", icon="⚡")
        else:
            with st.spinner(f"'{_ck_kw}' 연관어 분析 중..."):
                try:
                    _ck_analyzer = YouTubeAnalyzer(api_key)
                    _ck_rel = _ck_analyzer.get_related_keywords(_ck_kw)
                    _ck_rel2, _ck_ang, _ck_vids = _ck_analyzer.get_trending_analysis(_ck_kw)
                    st.session_state.custom_kw_input   = _ck_kw
                    st.session_state.custom_kw_results = (_ck_rel, _ck_ang)
                    storage.set_trending_cache(_ck_kw, -1, [_ck_rel, _ck_ang])
                    st.session_state.api_units_used = storage.add_api_usage(101, username)
                    if _api_bar:
                        _u = st.session_state.api_units_used
                        _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                        _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
                except Exception as _ck_e:
                    st.error(f"API 오류: {_ck_e}")
        st.rerun()

    _ck_saved_input   = st.session_state.get('custom_kw_input', '')
    _ck_saved_results = st.session_state.get('custom_kw_results')
    if _ck_saved_results and _ck_saved_input:
        _ck_r, _ck_a = _ck_saved_results
        _ck_sugg = get_content_suggestions(_ck_saved_input, _ck_r, _ck_a)

        st.markdown(f"#### 🔍 `{_ck_saved_input}` 연관 검색어 (검색량 순위)")
        st.caption("순위 = YouTube 자동완성 기반 검색 빈도. 클릭하면 해당 키워드 심층 분析.")
        if _ck_r:
            for _idx, (_ckw, _clbl) in enumerate(_ck_r):
                if _idx % 3 == 0:
                    _ck_rcols = st.columns(3)
                with _ck_rcols[_idx % 3]:
                    st.caption(_clbl)
                    if st.button(_ckw, key=f"ck_rel_{_idx}", use_container_width=True):
                        st.session_state.trending_selected      = _ckw
                        st.session_state.trending_analysis      = None
                        st.session_state.trending_refresh_seed  = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count = 0
                        st.rerun()
        else:
            st.info("연관 검색어를 불러오지 못했습니다.")

        st.divider()
        st.markdown("#### 💡 콘텐츠 주제 추천")
        st.caption("이 키워드로 만들 수 있는 영상 제목 아이디어")
        _ck_c1, _ck_c2 = st.columns(2)
        for _csi, _cs in enumerate(_ck_sugg):
            with (_ck_c1 if _csi % 2 == 0 else _ck_c2):
                st.markdown(
                    f"<div style='border:1px solid #333;border-radius:8px;"
                    f"padding:12px 14px;margin-bottom:10px;background:#141414'>"
                    f"<span style='font-size:.72em;color:#888'>{_cs['type']}</span><br>"
                    f"<strong style='font-size:.91em'>{_html.escape(_cs['title'])}</strong><br>"
                    f"<span style='font-size:.76em;color:#aaa'>{_html.escape(_cs['reason'])}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    trending = st.session_state.trending_keywords
    if not trending:
        st.info("**🔍 키워드 불러오기** 버튼을 눌러 트렌딩 키워드를 가져오세요.")
        st.stop()

    # ── 트렌딩 키워드 그리드 ─────────────────────────────────
    st.divider()
    period_label = "일주일" if st.session_state.trending_period == 'week' else "한달"
    st.markdown(f"### 📊 {period_label} 인기 키워드")
    st.caption("클릭하면 해당 키워드로 연관 키워드·다른 시각·콘텐츠 아이디어를 분析합니다.")

    for _i in range(0, min(len(trending), 24), 4):
        _row = trending[_i:_i+4]
        _cols = st.columns(4)
        for _col, (_kw, _cnt) in zip(_cols, _row):
            with _col:
                _is_sel = (_kw == st.session_state.trending_selected)
                _label  = f"✅ {_kw}" if _is_sel else _kw
                if st.button(_label, key=f"tk_{_i}_{_kw}", use_container_width=True,
                              type="primary" if _is_sel else "secondary"):
                    st.session_state.trending_selected      = _kw
                    st.session_state.trending_analysis      = None
                    st.session_state.trending_refresh_seed  = get_user_seed_offset(username)
                    st.session_state.trending_refresh_count = 0
                    st.rerun()
                _heat = "🔥🔥🔥" if _cnt >= 80 else ("🔥🔥" if _cnt >= 50 else "🔥")
                st.caption(f"{_heat} 인기도 {_cnt}점")

    # ── 선택된 키워드 분석 ───────────────────────────────────
    selected = st.session_state.trending_selected
    if not selected:
        st.stop()

    st.divider()
    st.markdown(f"## 🔎 `{{selected}}` 심층 분석")

    _tr_rc = st.session_state.get('trending_refresh_count', 0)
    _tr_cs = st.session_state.get('trending_refresh_seed', 0)
    _tr_info_col, _tr_btn_col = st.columns([4, 1])
    _tr_info_col.caption(
        f"알고리즘 모드: **{_SEED_LABELS[_tr_cs % 4]}**"
        + (f" · 새로고침 {_tr_rc}/3회 사용" if _tr_rc > 0 else "")
    )
    if _tr_rc < 3:
        if _tr_btn_col.button(
            f"🔄 알고리즘 초기화 ({_tr_rc+1}/3)", key="tr_refresh_btn",
            help=f"다음 모드: {_SEED_LABELS[(_tr_cs+1)%4]}\n다른 기준으로 영상을 다시 불러옵니다 (~101 유닛)"
        ):
            st.session_state.trending_refresh_seed  = (_tr_cs + 1) % 4
            st.session_state.trending_refresh_count = _tr_rc + 1
            st.session_state.trending_analysis = None
            st.rerun()
    else:
        _tr_btn_col.caption("새로고침 3회 완료")

    if st.session_state.trending_analysis is None:
        _tr_seed = st.session_state.get('trending_refresh_seed', 0)
        _tr_cached = storage.get_trending_cache(selected, _tr_seed)
        if _tr_cached:
            st.session_state.trending_analysis = tuple(_tr_cached)
            st.toast("캐시된 결과를 불러왔습니다 (API 0 유닛)", icon="⚡")
        else:
            with st.spinner(f"'{selected}' 분석 중..."):
                _analyzer = YouTubeAnalyzer(api_key)
                _rel, _ang, _vids = _analyzer.get_trending_analysis(selected, refresh_seed=_tr_seed)
            st.session_state.trending_analysis = (_rel, _ang, _vids)
            storage.set_trending_cache(selected, _tr_seed, [_rel, _ang, _vids])
            st.session_state.api_units_used = storage.add_api_usage(101, username)
            if _api_bar:
                _u = st.session_state.api_units_used
                _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
    _rel_kw, _ang_kw, _ = st.session_state.trending_analysis
    _suggestions = get_content_suggestions(selected, _rel_kw, _ang_kw)

    # 연관 키워드 + 다른 시각 키워드
    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### 🔍 연관 키워드")
        st.caption("YouTube 자동완성 기반 — 클릭 시 해당 키워드로 재분석")
        if _rel_kw:
            for _idx, (_kw2, _lbl) in enumerate(_rel_kw):
                if _idx % 3 == 0:
                    _rcols = st.columns(3)
                with _rcols[_idx % 3]:
                    st.caption(_lbl)
                    if st.button(_kw2, key=f"tr_rel_{_idx}", use_container_width=True):
                        st.session_state.trending_selected      = _kw2
                        st.session_state.trending_analysis      = None
                        st.session_state.trending_refresh_seed  = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count = 0
                        st.rerun()
        else:
            st.info("연관 키워드를 불러오지 못했습니다.")
    with cb:
        st.markdown("#### 🔀 다른 시각 키워드")
        st.caption("상위 영상 태그 분석 — 클릭 시 해당 키워드로 재분석")
        if _ang_kw:
            for _idx, (_kw2, _cnt2) in enumerate(_ang_kw):
                if _idx % 3 == 0:
                    _acols = st.columns(3)
                with _acols[_idx % 3]:
                    st.caption(f"{_cnt2}개 영상")
                    if st.button(_kw2, key=f"tr_ang_{_idx}", use_container_width=True):
                        st.session_state.trending_selected      = _kw2
                        st.session_state.trending_analysis      = None
                        st.session_state.trending_refresh_seed  = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count = 0
                        st.rerun()
        else:
            st.info("태그 데이터가 부족합니다.")

    # 콘텐츠 주제 추천
    st.divider()
    st.markdown("#### 💡 콘텐츠 주제 추천")
    st.caption("인기 포맷 템플릿 + 연관·시각 키워드 조합 — 바로 사용할 수 있는 영상 제목 아이디어")
    _sc1, _sc2 = st.columns(2)
    for _si, _s in enumerate(_suggestions):
        with (_sc1 if _si % 2 == 0 else _sc2):
            st.markdown(
                f"<div style='border:1px solid #e0e0e0;border-radius:8px;"
                f"padding:12px 14px;margin-bottom:10px'>"
                f"<span style='font-size:.72em;color:#888'>{_s['type']}</span><br>"
                f"<strong style='font-size:.91em'>{_html.escape(_s['title'])}</strong><br>"
                f"<span style='font-size:.76em;color:#aaa'>{_html.escape(_s['reason'])}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════
elif page == "📺 쇼츠 분석기":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        📺 쇼츠 조회수 분석기</div>
    <div style="font-size:.82rem;color:#444;margin-bottom:20px">
        체널 링크를 입력하면 최근 4주간 주별 쇼츠 조회수를 분석합니다
    </div>''', unsafe_allow_html=True)

    if not api_key:
        st.error("사이드바에서 API 키를 먼저 입력해주세요.")
        st.stop()

    with st.form("shorts_analyzer_form"):
        ch_url = st.text_input(
            "채널 링크",
            placeholder="https://www.youtube.com/@채널명  또는  /channel/UCxxxx",
        )
        sh_submit = st.form_submit_button("📊 분석 시작", type="primary", use_container_width=True)

    if sh_submit and ch_url.strip():
        with st.spinner("쇼츠 조회수 분석 중..."):
            try:
                _analyzer = YouTubeAnalyzer(api_key)
                sh_result = _analyzer.analyze_channel_shorts(ch_url.strip())
                st.session_state.api_units_used = storage.add_api_usage(102, username)
            except Exception as e:
                st.error(f"API 오류: {e}")
                sh_result = None

        if sh_result is None:
            st.error("채널을 찾을 수 없습니다. URL을 확인해주세요.")
        elif not sh_result['weeks'] or sh_result['total_shorts'] == 0:
            st.warning(f"**{sh_result['channel_name']}** 채널에서 최근 28일 내 쇼츠를 찾지 못했습니다.")
        else:
            st.markdown(f"### 📺 {sh_result['channel_name']}")
            st.caption(f"분석 쇼츠: {sh_result['total_shorts']}개 | 한달 총 조회수: {sh_result.get('monthly_total', 0):,}회 | 편당 평균: {sh_result['monthly_avg']:,}회")

            # ── 주별 테이블 ───────────────────────────────
            _sh_rows = []
            for w in sh_result['weeks']:
                _sh_rows.append({
                    '기간': w['label'], '쇼츠 수': w['count'],
                    '조회수 합계': w['total_views'], '좋아요 합계': w['total_likes'],
                    '댓글 합계': w['total_comments'], '편당 평균 조회수': w['avg_views'],
                })
            _sh_df = pd.DataFrame(_sh_rows)
            st.dataframe(
                _sh_df.style.format({
                    '조회수 합계': '{:,}', '좋아요 합계': '{:,}',
                    '댓글 합계': '{:,}', '편당 평균 조회수': '{:,}',
                }),
                use_container_width=True, hide_index=True
            )

            st.divider()

            # ── 월 요약 메트릭 ────────────────────────────
            sm1, sm2, sm3 = st.columns(3)
            sm1.metric("📅 편당 평균 조회수", f"{sh_result['monthly_avg']:,}회")
            sm2.metric("📅 한달 총 조회수",   f"{sh_result.get('monthly_total', 0):,}회")
            sm3.metric("📅 분석 쇼츠 수",     f"{sh_result['total_shorts']}개")

            # ── 막대 차트 ─────────────────────────────────
            chart_data = [w for w in sh_result['weeks'] if w['count'] > 0]
            if len(chart_data) >= 2:
                fig = px.bar(
                    x=[w['label'] for w in chart_data],
                    y=[w['total_views'] for w in chart_data],
                    labels={'x': '기간', 'y': '조회수 합계'},
                    title="주별 쇼츠 조회수 합계",
                    text=[f"{w['total_views']:,}" for w in chart_data],
                    color=[w['total_views'] for w in chart_data],
                    color_continuous_scale='Blues',
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_tickformat=',')
                st.plotly_chart(fig, use_container_width=True)

            # API 사용량 갱신
            if _api_bar is not None:
                _u = st.session_state.get('api_units_used', 0)
                _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")

# ══════════════════════════════════════════════════════════
elif page == "📌 저장된 영상":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        📌 저장된 영상</div>
    <div style="font-size:.82rem;color:#444;margin-bottom:20px">
        직접 삭제하기 전까지 영구 보관됩니다
    </div>''', unsafe_allow_html=True)
    saved = storage.get_saved_by_user(username)

    if 'confirm_del_video' not in st.session_state:
        st.session_state.confirm_del_video = ''

    if not saved:
        st.info("아직 저장된 영상이 없습니다. 분석 결과에서 📌 저장 버튼을 눌러주세요.")
    else:
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        col_stat1.metric("총 저장 영상", f"{len(saved)}개")
        kw_cnt = len({s['keyword'] for s in saved if s['keyword']})
        col_stat2.metric("키워드 수", f"{kw_cnt}개")
        col_stat3.metric("최근 저장", saved[0]['saved_at'] if saved else "-")

        st.divider()

        # 키워드별 필터
        keywords_in_saved = sorted({s['keyword'] for s in saved if s['keyword']})
        filter_kw = st.selectbox("🔖 키워드 필터", ["전체"] + keywords_in_saved)
        filtered = saved if filter_kw == "전체" else [s for s in saved if s['keyword'] == filter_kw]
        st.caption(f"{len(filtered)}개 표시 중")

        for i in range(0, len(filtered), 3):
            row = filtered[i:i+3]
            cols = st.columns(3)
            for col, v in zip(cols, row):
                with col:
                    if v.get('thumbnail'):
                        st.image(v['thumbnail'], use_container_width=True)
                    st.markdown(f"**[{v['title']}]({v['url']})**")
                    ch_url = f"https://www.youtube.com/channel/{v['channel_id']}" if v.get('channel_id') else '#'
                    st.caption(f"📺 [{v['channel_title']}]({ch_url})  ·  {v.get('type','').upper()}")
                    st.caption(f"🔖 `{v.get('keyword','')}`  ·  {v['saved_at']}")

                    memo_key = f"memo_{v['video_id']}"
                    new_memo = st.text_input("메모", value=v.get('memo', ''), key=memo_key, placeholder="메모 입력...")
                    if new_memo != v.get('memo', ''):
                        storage.update_memo(v['video_id'], username, new_memo)

                    # 삭제 2단계 확인
                    vid = v['video_id']
                    if st.session_state.confirm_del_video == vid:
                        st.warning("정말 삭제할까요?")
                        dc1, dc2 = st.columns(2)
                        if dc1.button("✅ 확인 삭제", key=f"del_ok_{vid}", use_container_width=True, type="primary"):
                            storage.delete_video(vid, username)
                            st.session_state.confirm_del_video = ''
                            st.rerun()
                        if dc2.button("❌ 취소", key=f"del_cancel_{vid}", use_container_width=True):
                            st.session_state.confirm_del_video = ''
                            st.rerun()
                    else:
                        if st.button("🗑️ 삭제", key=f"del_{vid}", use_container_width=True):
                            st.session_state.confirm_del_video = vid
                            st.rerun()
                    st.divider()

        # CSV 내보내기
        df_saved = pd.DataFrame(filtered)
        csv = df_saved.to_csv(index=False).encode('utf-8-sig')
        st.download_button("⬇️ 저장 목록 CSV 내보내기", csv, "저장된영상.csv", "text/csv")

# ══════════════════════════════════════════════════════════
elif page == "⚙️ 팀 관리":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        ⚙️ 팀 관리</div>
    <div style="font-size:.82rem;color:#444;margin-bottom:20px">
        팀원 계정 관리 및 권한 설정
    </div>''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 팀원 추가")
        with st.form("add_user_form"):
            new_id = st.text_input("아이디")
            new_name = st.text_input("이름")
            new_pw = st.text_input("비밀번호", type="password")
            add_ok = st.form_submit_button("추가", use_container_width=True)
        if add_ok:
            ok, msg = auth.add_user(new_id, new_pw, new_name)
            (st.success if ok else st.error)(msg)

    with col2:
        st.markdown("### 비밀번호 변경")
        with st.form("change_pw_form"):
            old_pw = st.text_input("현재 비밀번호", type="password")
            new_pw1 = st.text_input("새 비밀번호", type="password")
            new_pw2 = st.text_input("새 비밀번호 확인", type="password")
            change_ok = st.form_submit_button("변경", use_container_width=True)
        if change_ok:
            if new_pw1 != new_pw2:
                st.error("새 비밀번호가 일치하지 않습니다.")
            else:
                ok, msg = auth.change_password(username, old_pw, new_pw1)
                (st.success if ok else st.error)(msg)

    st.divider()
    st.markdown("### 현재 팀원 목록")

    users = auth.load_users()
    is_admin = (username == 'admin')

    # 삭제 확인 상태
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = ''

    for uid, udata in users.items():
        with st.expander(f"**{uid}** — {udata.get('name', '')}"):
            if is_admin:
                with st.form(f"edit_user_{uid}"):
                    ec1, ec2 = st.columns(2)
                    edit_id   = ec1.text_input("아이디", value=uid, key=f"eid_{uid}")
                    edit_name = ec2.text_input("이름",   value=udata.get('name', ''), key=f"ename_{uid}")
                    edit_pw   = st.text_input(
                        "새 비밀번호 (빈칸이면 변경 안 함)",
                        type="password", key=f"epw_{uid}"
                    )
                    save_btn = st.form_submit_button("💾 저장", use_container_width=True, type="primary")

                if save_btn:
                    new_pw_val = edit_pw if edit_pw.strip() else None
                    ok, msg = auth.admin_update_user(
                        uid,
                        new_id=edit_id,
                        new_name=edit_name,
                        new_pw=new_pw_val,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                # 삭제 (본인·admin 계정 제외)
                if uid != username and uid != 'admin':
                    if st.session_state.confirm_delete == uid:
                        st.warning(f"**{uid}** 계정을 삭제합니다. 되돌릴 수 없습니다.")
                        dcol1, dcol2 = st.columns(2)
                        if dcol1.button("확인 삭제", key=f"del_confirm_{uid}", type="primary"):
                            ok, msg = auth.admin_delete_user(uid)
                            st.session_state.confirm_delete = ''
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        if dcol2.button("취소", key=f"del_cancel_{uid}"):
                            st.session_state.confirm_delete = ''
                            st.rerun()
                    else:
                        if st.button("🗑️ 삭제", key=f"del_{uid}"):
                            st.session_state.confirm_delete = uid
                            st.rerun()
            else:
                st.write(f"아이디: `{uid}`")
                st.write(f"이름: {udata.get('name', '')}")
