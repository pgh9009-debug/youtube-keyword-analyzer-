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

/* ── 캡션 텍스트 ── */
[data-testid="stCaptionContainer"] p { color: #999 !important; }
[data-testid="stCaptionContainer"] strong, [data-testid="stCaptionContainer"] b { color: #ccc !important; }

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
.stInfo    { background: #0d131f !important; color: #e0e0e0 !important; }

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
        <div style="font-size:.9rem;color:#888;margin-bottom:40px">
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
    return int(hashlib.md5(uname.encode(), usedforsecurity=False).hexdigest(), 16) % 4

if 'run_keyword' not in st.session_state:
    st.session_state.run_keyword = ''
if 'refresh_seed' not in st.session_state:
    st.session_state.refresh_seed  = 0
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
if 'longform_refresh_seed' not in st.session_state:
    st.session_state.longform_refresh_seed  = 0
if 'longform_refresh_count' not in st.session_state:
    st.session_state.longform_refresh_count = 0
if 'channel_tab_refresh_seed' not in st.session_state:
    st.session_state.channel_tab_refresh_seed  = 0
if 'channel_tab_refresh_count' not in st.session_state:
    st.session_state.channel_tab_refresh_count = 0
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
if 'discovery_url'           not in st.session_state:
    st.session_state.discovery_url           = ''
if 'discovery_result'        not in st.session_state:
    st.session_state.discovery_result        = None
if 'discovery_seed'          not in st.session_state:
    st.session_state.discovery_seed          = 0
if 'discovery_refresh_count' not in st.session_state:
    st.session_state.discovery_refresh_count = 0
if 'discovery_channel_id'    not in st.session_state:
    st.session_state.discovery_channel_id    = ''
if 'trending_content_seed'   not in st.session_state:
    st.session_state.trending_content_seed   = 0
if 'trending_content_refresh' not in st.session_state:
    st.session_state.trending_content_refresh = 0
if 'custom_content_seed'     not in st.session_state:
    st.session_state.custom_content_seed     = 0
if 'custom_content_refresh'  not in st.session_state:
    st.session_state.custom_content_refresh  = 0
if 'sa_result'               not in st.session_state:
    st.session_state.sa_result               = None
if 'sa_vinfo'                not in st.session_state:
    st.session_state.sa_vinfo                = None
if 'sa_transcript'           not in st.session_state:
    st.session_state.sa_transcript           = ''
if 'sa_url'                  not in st.session_state:
    st.session_state.sa_url                  = ''
if 'sa_seed'                 not in st.session_state:
    st.session_state.sa_seed                 = 0
if 'sa_refresh_count'        not in st.session_state:
    st.session_state.sa_refresh_count        = 0

def _get_secret(key):
    """st.secrets → 환경변수 순으로 값 반환."""
    try:
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, "")

# 사용자별 API 키 로드 (users.json → 브라우저쿠키 → secrets/env fallback)
_all_cookies_keys = _cookies.getAll() or {}
if 'api_key' not in st.session_state:
    _stored_key = auth.get_api_key(username)
    _cookie_yt  = _all_cookies_keys.get(f'yt_apikey_{username}', '')
    st.session_state.api_key = _stored_key or _cookie_yt or _get_secret("YOUTUBE_API_KEY")

if 'anthropic_key' not in st.session_state:
    _stored_ant  = auth.get_anthropic_key(username)
    _cookie_ant  = _all_cookies_keys.get(f'ant_apikey_{username}', '')
    st.session_state.anthropic_key = _stored_ant or _cookie_ant or _get_secret("ANTHROPIC_API_KEY")

# 세션 시작 시 파일에서 오늘 API 사용량 복원 (날짜 바뀌면 자동 0)
if 'api_units_used' not in st.session_state:
    st.session_state.api_units_used = storage.get_api_usage(username)
if 'sq_used' not in st.session_state:
    st.session_state.sq_used = storage.get_sq_usage(username)

_api_bar = _api_text = _sq_text = None  # 사이드바 API 사용량 플레이스홀더
_sq_lim = 100

# ── 사이드바 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-size:1.25rem;font-weight:800;letter-spacing:-.5px;
                color:#fff;margin-bottom:2px">마케팅신</div>
    <div style="font-size:.72rem;color:#888;margin-bottom:12px">
        YouTube Intelligence
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.82rem;color:#aaa;margin-bottom:8px'>"
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

    page = st.radio("페이지", ["🔍 키워드 분석", "🔥 트렌딩", "📺 쇼츠 분석기", "🔭 채널 발굴", "📌 저장된 영상", "⚙️ 팀 관리"], label_visibility="collapsed")
    st.divider()

    # ── API 사용량 (모든 페이지에서 항상 표시) ─────────────
    st.markdown("**📊 오늘 내 API 사용량**")
    _api_bar  = st.empty()
    _api_text = st.empty()
    _sq_text  = st.empty()
    st.caption("검색 1회 ≈ 202 유닛 · 4 Search Queries · 채널 발굴 ≈ 510 유닛")
    _u  = st.session_state.get('api_units_used', 0)
    _sq = st.session_state.get('sq_used', 0)
    _api_bar.progress(min(int(_u / 10_000 * 100), 100))
    _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
    _sq_lim = 100
    _sq_text.caption(f"🔎 Search Queries {_sq} / {_sq_lim}회 ({max(_sq_lim - _sq, 0)} 남음)")
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
    elif page == "🔥 트렌딩":
        api_key = st.session_state.get('api_key', '')
        keyword_input = ''
        run = False
        keyword_b = ''
        run_compare = False

        _tr_hist = storage.get_trending_history(username)
        if _tr_hist:
            st.divider()
            st.markdown("**📋 오늘 검색 목록**")
            for _th in _tr_hist:
                _src = _th.get('source', 'trending')
                _icon = '🎯' if _src == 'custom' else '🔥'
                _active_kw = (
                    st.session_state.get('custom_kw_input', '') if _src == 'custom'
                    else st.session_state.trending_selected
                )
                _is_active = (_active_kw == _th['keyword'])
                _btn_label = f"{'▶ ' if _is_active else ''}{_icon} {_th['time']} {_th['keyword']}"
                if st.button(_btn_label, key=f"tr_hist_{_src}_{_th['keyword']}",
                             use_container_width=True,
                             type="primary" if _is_active else "secondary"):
                    if _src == 'custom':
                        st.session_state.custom_kw_input       = _th['keyword']
                        st.session_state.custom_kw_results     = (_th['related_kw'], _th['angle_kw'])
                        st.session_state.custom_content_seed   = 0
                        st.session_state.custom_content_refresh = 0
                    else:
                        st.session_state.trending_selected      = _th['keyword']
                        st.session_state.trending_analysis      = (_th['related_kw'], _th['angle_kw'], _th.get('videos', []))
                        st.session_state.trending_refresh_seed  = _th.get('refresh_seed', 0)
                        st.session_state.trending_refresh_count = _th.get('refresh_count', 0)
                        st.session_state.trending_content_seed  = 0
                        st.session_state.trending_content_refresh = 0
                    st.rerun()
    elif page == "📺 쇼츠 분석기":
        api_key = st.session_state.get('api_key', '')
        keyword_input = ''
        run = False
        keyword_b = ''
        run_compare = False

        # ── Anthropic API 키 (사용자별 저장) ──────────────
        with st.form("ant_key_sidebar_form"):
            _ant_sidebar_input = st.text_input(
                "Anthropic API 키",
                value=st.session_state.get('anthropic_key', ''),
                type="password",
                placeholder="sk-ant-..." if not st.session_state.get('anthropic_key') else "",
            )
            _ant_key_saved = st.form_submit_button("✅ 저장", use_container_width=True)
        if _ant_key_saved and _ant_sidebar_input.strip():
            auth.save_anthropic_key(username, _ant_sidebar_input.strip())
            st.session_state.anthropic_key = _ant_sidebar_input.strip()
            _cookies.set(f'ant_apikey_{username}', _ant_sidebar_input.strip(), max_age=90 * 24 * 3600)
            st.success("저장됐습니다.")
    else:
        api_key = st.session_state.get('api_key', '')
        keyword_input = ''
        run = False
        keyword_b = ''
        run_compare = False

if run:
    st.session_state.run_keyword   = keyword_input
    st.session_state.history_view  = None
    st.session_state.refresh_seed  = get_user_seed_offset(username)
    st.session_state.refresh_count = 0
    st.session_state.longform_refresh_seed  = get_user_seed_offset(username)
    st.session_state.longform_refresh_count = 0
    st.session_state.channel_tab_refresh_seed  = get_user_seed_offset(username)
    st.session_state.channel_tab_refresh_count = 0

# ══════════════════════════════════════════════════════════
# 헬퍼 함수
# ══════════════════════════════════════════════════════════

def _extract_vid_id(url):
    m = re.search(r'(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return m.group(1) if m else None


def _get_transcript(video_id):
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
    import tempfile

    # Streamlit Secrets에 YOUTUBE_COOKIES가 있으면 쿠키 파일로 IP 차단 우회
    _cookies_file = None
    try:
        _cookie_content = st.secrets.get("YOUTUBE_COOKIES", "")
        if _cookie_content:
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            # 공백 구분자를 탭으로 정규화 (Netscape 포맷 요구사항)
            for line in _cookie_content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    tmp.write(line + '\n')
                    continue
                parts = line.split('\t') if '\t' in line else line.split()
                if len(parts) >= 7:
                    tmp.write('\t'.join(parts[:7]) + '\n')
            tmp.flush()
            _cookies_file = tmp.name
    except Exception:
        pass

    _kwargs = {'cookies': _cookies_file} if _cookies_file else {}
    _last_err = None

    # 1. 한국어 우선, 없으면 영어
    for langs in [['ko'], ['en'], ['ko', 'en', 'ja', 'zh-Hans', 'zh-Hant']]:
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=langs, **_kwargs)
            return ' '.join(item['text'] for item in data)
        except NoTranscriptFound:
            continue
        except Exception as e:
            _last_err = e
            continue

    # 2. 사용 가능한 첫 번째 자막 (어떤 언어든)
    try:
        tl = YouTubeTranscriptApi.list_transcripts(video_id, **_kwargs)
        first = next(iter(tl))
        data = first.fetch()
        return ' '.join(item['text'] for item in data)
    except TranscriptsDisabled:
        raise ValueError("이 영상은 자막이 비활성화되어 있습니다.")
    except Exception as e:
        _last_err = e

    detail = f" ({type(_last_err).__name__}: {_last_err})" if _last_err else ""
    raise ValueError(f"이 영상에는 사용 가능한 자막이 없습니다.{detail}")


def _extract_json_obj(text):
    import json as _j
    # ```json ... ``` 블록 우선 시도
    m = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
    if m:
        try:
            return _j.loads(m.group(1))
        except Exception:
            pass
    # 가장 바깥 { } 범위 찾기 (중첩 고려)
    start = text.find('{')
    if start == -1:
        return None
    depth, end = 0, -1
    for i, c in enumerate(text[start:], start):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None
    try:
        return _j.loads(text[start:end + 1])
    except Exception:
        return None


def _extract_json_arr(text):
    import json as _j
    # ```json ... ``` 블록 우선 시도
    m = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', text)
    if m:
        try:
            return _j.loads(m.group(1))
        except Exception:
            pass
    # 가장 바깥 [ ] 범위 찾기
    start = text.find('[')
    if start == -1:
        return None
    depth, end = 0, -1
    for i, c in enumerate(text[start:], start):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None
    try:
        return _j.loads(text[start:end + 1])
    except Exception:
        return None


_SA_SEED_ANGLES = [
    "시청자의 감정적 공감과 공유 욕구를 자극하는 방향으로",
    "정보 전달과 '몰랐던 사실' 충격 요소를 활용하는 방향으로",
    "트렌드·시의성·챌린지 요소를 결합하는 방향으로",
    "개인 스토리텔링과 진정성 있는 경험 공유 방향으로",
]


def _claude_analyze_shorts(ant_key, vinfo, transcript, seed=0):
    import anthropic as _ant, json as _json
    angle = _SA_SEED_ANGLES[seed % len(_SA_SEED_ANGLES)]
    safe_transcript = transcript[:2000].replace('"', "'").replace('\\', '')
    prompt = (
        "당신은 한국 YouTube 쇼츠 콘텐츠 전략 전문가입니다.\n\n"
        "아래 쇼츠를 분析하고 반드시 순수 JSON 객체만 반환하세요. "
        "마크다운, 코드블록, 설명 텍스트 없이 { 로 시작해서 } 로 끝나는 JSON만 출력하세요.\n\n"
        "[영상 정보]\n"
        f"제목: {vinfo['title']}\n"
        f"채널: {vinfo['channel']}\n"
        f"조회수: {vinfo['views']:,}회 | 좋아요: {vinfo['likes']:,} | 댓글: {vinfo['comments']:,} | 길이: {vinfo['duration']}초\n\n"
        "[대본]\n"
        f"{safe_transcript}\n\n"
        "출력할 JSON (script 필드 없이, 분析과 추천만):\n"
        '{\n'
        '  "topic": "핵심 주제 1-2문장",\n'
        '  "structure": "전개 방式 분析: 훅→전개→결말 구조 설명",\n'
        '  "expression": "문장 구조·표현법: 말투, 리듬, 반복, 대비, 감정 자극 기법",\n'
        '  "reasons": ["높은 조회수 이유1", "이유2", "이유3"],\n'
        '  "recommendations": [\n'
        '    {\n'
        '      "type": "반전/주제 디벨롭/소재 변경/대상 바꾸기/감정 전환 중 택1",\n'
        '      "title": "영상 제목",\n'
        '      "hook": "첫 3초 훅 문장",\n'
        '      "structure": "전개 방式: 어떻게 이야기를 풀어나갈지",\n'
        '      "message": "시청자에게 전달할 핵심 메시지",\n'
        '      "why": "왜 조회수·공감이 오를지"\n'
        '    }\n'
        '  ]\n'
        '}\n\n'
        f"추천 5가지는 각각 다른 방향 유형으로. {angle}. 조회수와 공감 극대화가 목표."
    )
    client = _ant.Anthropic(api_key=ant_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    try:
        return _json.loads(text)
    except Exception:
        result = _extract_json_obj(text)
        if result is None:
            raise ValueError(f"JSON 파싱 실패. Claude 응답 앞부분:\n{text[:500]}")
        return result


def _claude_refresh_recos(ant_key, vinfo, transcript, seed):
    import anthropic as _ant, json as _json
    angle = _SA_SEED_ANGLES[seed % len(_SA_SEED_ANGLES)]
    safe_summary = transcript[:400].replace('"', "'").replace('\\', '')
    prompt = (
        "YouTube 쇼츠 콘텐츠 전략가입니다.\n\n"
        "아래 레퍼런스 쇼츠를 바탕으로 새로운 콘텐츠 방향 5가지를 "
        "JSON 배열로만 반환하세요. 반드시 ```json 없이 순수 JSON 배열만 출력하세요.\n\n"
        f"제목: {vinfo['title']} | 조회수: {vinfo['views']:,}회\n"
        f"대본 요약: {safe_summary}...\n\n"
        "출력 형식 (이 형식 그대로, 5개):\n"
        '[\n'
        '  {\n'
        '    "type": "방향 유형 (반전/주제 디벨롭/소재 변경/대상 바꾸기/감정 전환 중 택1)",\n'
        '    "title": "영상 제목",\n'
        '    "hook": "첫 3초 훅 문장",\n'
        '    "structure": "전개 방식: 어떻게 이야기를 풀어나갈지 구체적으로",\n'
        '    "message": "시청자에게 전달할 핵심 메시지",\n'
        '    "why": "왜 조회수·공감이 오를지"\n'
        '  }\n'
        ']\n\n'
        f"{angle} 작성. 각 방향 유형이 서로 다르게, 앞서 추천과 겹치지 않는 완전히 새로운 방향으로."
    )
    client = _ant.Anthropic(api_key=ant_key)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    try:
        return _json.loads(text)
    except Exception:
        return _extract_json_arr(text)


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
    st.session_state.sq_used = storage.add_sq_usage(analyzer._sq, st.session_state.username)
    if _sq_text is not None:
        _sq = st.session_state.sq_used
        _sq_text.caption(f"🔎 Search Queries {_sq} / {_sq_lim}회 ({max(_sq_lim - _sq, 0)} 남음)")

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
.vc-tags{height:18px;font-size:.72em;color:#999;
  overflow:hidden;white-space:nowrap;margin-bottom:3px}
.vc-meta{height:17px;font-size:.72em;color:#999;
  overflow:hidden;white-space:nowrap;text-overflow:ellipsis;margin-bottom:6px}
.vc-meta a{color:#999;text-decoration:none}
.vc-meta a:hover{color:#aaa}
.vc-stats{width:100%;border-collapse:collapse;font-size:.8em;margin-bottom:4px}
.vc-stats th{color:#999;font-weight:500;text-align:center;
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
                _safe_thumb = thumb if (thumb and (thumb.startswith('https://i.ytimg.com/') or thumb.startswith('https://yt3.ggpht.com/'))) else ''
                thumb_el = (f'<img class="vc-thumb" src="{_safe_thumb}">'
                            if _safe_thumb else '<div class="vc-no-thumb"></div>')
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


_CONTENT_POOLS = [
    ("📚 정보성", [
        ("{kw} 완벽 정리 — 처음 시작하는 사람이 꼭 봐야 할 영상", "입문자 타겟 + 넓은 검색 유입"),
        ("{kw} A to Z 완전 가이드 (2025년 최신판)", "포괄적 정보 → 긴 시청시간"),
        ("처음 하는 {kw}, 이것만 알면 됩니다", "단순명쾌 제목 → 클릭률 높음"),
        ("{kw} 핵심 개념 10가지 총정리", "숫자 리스트 → 스캔하기 쉬운 제목"),
        ("{kw} 기초부터 심화까지 한 번에 끝내기", "원스톱 콘텐츠 → 시청 지속시간 ↑"),
        ("초보자를 위한 {kw} 입문 강의 (무료)", "무료 강조 → 클릭 허들 낮춤"),
        ("{kw} 공부 순서와 로드맵 — 이렇게 시작하세요", "로드맵 → 북마크·저장 유도"),
        ("지금 당장 {kw} 시작하는 방법", "즉시 실행 가능 프레이밍"),
        ("{kw} 용어 정리 — 헷갈리는 개념 완벽 해설", "용어집 → 반복 방문 유도"),
        ("{kw} 기초 다지기 — 전문가도 처음엔 이것부터", "권위 활용 + 입문자 공감"),
        ("2025년 {kw} 완전 가이드", "연도 포함 → 최신 검색 유입"),
        ("{kw}와 {r0} 완전정복 가이드", "연관어 조합 → 두 검색어 유입"),
        ("모르면 손해! {kw} 필수 정보 총정리", "FOMO 자극 → 클릭 유도"),
    ]),
    ("⚠️ 반전형", [
        ("아무도 알려주지 않는 {kw}의 진짜 단점", "역발상 → 호기심 유발, 댓글 참여 ↑"),
        ("{kw}, 사실은 이게 함정입니다", "경고성 역발상 → 강한 클릭 충동"),
        ("{kw}에 대한 흔한 오해 7가지", "오해 교정 → 지식 욕구 자극"),
        ("저도 처음엔 {kw}가 좋은 줄 알았습니다", "개인 경험 반전 → 공감 유발"),
        ("{kw} 잘 알려진 사실이 틀렸습니다", "권위 도전 → 강한 호기심"),
        ("대부분이 {kw} 할 때 이 실수를 합니다", "집단 실수 지적 → 공감"),
        ("{kw}의 숨겨진 진실 — 아무도 말 안 해줬던 것", "비밀 프레이밍 → 클릭 유도"),
        ("전문가들도 틀린 {kw} 상식", "권위자 반전 → 신뢰 + 호기심"),
        ("{kw}를 오래 해온 제가 후회하는 것들", "경험자 후회 → 감정 이입"),
        ("{kw} 하면 안 되는 경우가 있습니다", "금기 사례 → 경각심 유발"),
        ("{r0}을 먼저 배웠다면 {kw}가 더 쉬웠을 텐데", "시퀀스 반전 → 공감"),
        ("유튜브에서 알려주지 않는 {kw} 현실", "미디어 비판 → 차별화"),
        ("3년간 {kw} 했는데 돌아보니 비효율적이었던 것들", "장기 경험 반전 → 공감"),
    ]),
    ("🔥 트렌드형", [
        ("2025년 {kw} 트렌드 완전 분석", "연도+트렌드 조합 → 시즌 검색에 강함"),
        ("요즘 {kw}에서 가장 뜨고 있는 것", "최신성 강조 → 지금 당장 클릭"),
        ("{kw} 2025년 전망 — 이렇게 바뀝니다", "미래 예측 → 관심 집중"),
        ("지금 {kw} 안 하면 뒤처지는 이유", "FOMO + 트렌드 결합"),
        ("2025 {kw} 핫 트렌드 TOP 5", "숫자+연도 → 검색 최적화"),
        ("{kw}에 새로운 바람이 불고 있습니다", "트렌드 변화 암시 → 궁금증"),
        ("상반기 {kw} 결산 — 올해 가장 주목받은 것", "시즌 결산 → 타이밍 맞춤"),
        ("{kw} 최신 트렌드 vs 예전 방식 비교", "변화 대조 → 두 타입 유입"),
        ("지금 {kw} 시장에서 일어나는 일", "현재 진행형 트렌드 → 긴급성"),
        ("{r0}과 함께 뜨는 {kw} 트렌드", "연관 키워드 트렌드 조합"),
        ("알고리즘이 지금 밀어주는 {kw} 콘텐츠", "알고리즘 언급 → 크리에이터 관심"),
        ("하반기 {kw} 체크리스트 — 이것 챙기세요", "체크리스트 → 저장 유도"),
        ("{kw} 시장에 일어나는 변화 — 한눈에 정리", "변화 요약 → 편의성"),
    ]),
    ("⛔ 경고형", [
        ("{kw} 할 때 절대 하면 안 되는 실수 TOP 5", "리스트+부정 프레이밍 → 클릭 충동"),
        ("{kw} 시작 전 반드시 알아야 할 것", "사전 경고 → 새 입문자 유입"),
        ("{kw}를 잘못 하면 생기는 일", "결과 기반 경고 → 공포 마케팅"),
        ("이것만큼은 {kw}에서 피하세요", "금기 사항 나열 → 저장 가치 ↑"),
        ("{kw} 후회하지 않으려면 이것부터 확인", "사전 점검 유도 → 클릭"),
        ("{kw} 함정 피하는 방법 — 초보자 주의", "함정 회피 → 초보자 타겟"),
        ("돈 날리지 않는 {kw} 선택 기준", "경제적 손실 회피 → 강한 동기"),
        ("{kw} 잘못 선택하면 이런 문제가 생깁니다", "문제 예고 → 경고 심리"),
        ("전문가가 말리는 {kw} 방식", "전문가 권위 + 경고"),
        ("{kw} 시작하기 전 체크해야 할 7가지", "체크리스트 → 저장·북마크"),
        ("{r0}과 {kw}를 함께 하면 안 되는 이유", "조합 경고 → 연관 키워드 유입"),
        ("저렴한 {kw}를 선택했다가 후회한 사례", "실제 사례 경고 → 공감"),
        ("{kw} 해외 실패 사례로 보는 함정 분석", "해외 사례 경고 → 신뢰성"),
    ]),
    ("📖 브이로그형", [
        ("{kw} 6개월 해봤더니 생긴 일 (솔직 후기)", "체험 스토리 → 진정성·구독 전환율 ↑"),
        ("{kw} 1년 현실 브이로그 — 솔직하게 다 말합니다", "장기 기록 → 신뢰감"),
        ("처음으로 {kw} 도전해봤습니다", "첫 도전 → 공감·응원 댓글 유도"),
        ("{kw} 하루 루틴 공개 — 실제 어떻게 하는지", "일상 공개 → 친근감"),
        ("{kw}를 시작한 이유와 3개월 후기", "동기+결과 → 비슷한 고민 유저 유입"),
        ("{kw} 현실 적나라하게 보여드립니다", "날것 그대로 → 진정성 포인트"),
        ("남들이 말 안 해주는 {kw} 일상", "미공개 일상 → 독점 느낌"),
        ("{kw} 초보였던 제가 지금은", "성장 스토리 → 동기부여"),
        ("{kw}를 포기하고 싶었던 순간과 극복기", "고난 극복 → 감정 이입"),
        ("{kw} 도전 30일 기록 — 변화가 있었나요?", "챌린지 기록 → 시리즈화"),
        ("같이 {kw} 해요 — 함께 성장하는 브이로그", "커뮤니티 형성 → 구독 유도"),
        ("{kw} 하면서 알게 된 것들", "경험에서 우러난 인사이트"),
        ("현직 {kw} 종사자의 하루", "현직 공개 → 직업 관련 키워드 유입"),
    ]),
    ("💰 수익형", [
        ("{kw}으로 수익 내는 방법 (실제 사례 공개)", "실용+실제 사례 → 클릭률 우수"),
        ("{kw}로 월 수익 만든 방법 — 실제 데이터 공개", "구체적 수익 → 강한 클릭 동기"),
        ("{kw} 관련 직업과 연봉 리얼 공개", "직업+연봉 → 커리어 탐색 유입"),
        ("{kw}로 부업하는 방법 — 직장인도 가능", "직장인 부업 → 타겟 확장"),
        ("{kw} 시장에서 돈 버는 사람들의 공통점", "성공 패턴 분석 → 학습 욕구"),
        ("무자본으로 {kw} 시작해서 수익화까지", "무자본 → 진입 장벽 낮춤"),
        ("{kw} 수익화 실패한 이유 — 제 경험담", "실패 분석 → 반면교사"),
        ("{kw}를 취미에서 수익으로 바꾼 방법", "취미 → 수익 전환 스토리"),
        ("{kw} 관련 창업 현실 — 1년 수입 공개", "창업 현실 → 리얼 데이터"),
        ("{kw} 프리랜서로 사는 삶", "프리랜서 라이프 → 직업 탐색"),
        ("{r0}과 {kw}를 합쳐서 새로운 수익 만들기", "조합 수익화 → 차별화"),
        ("{kw} 강의 만들어서 팔기 — 실제 수익 공개", "강의 수익화 → 크리에이터 관심"),
        ("{kw} 자격증으로 수입이 달라졌나요?", "자격증 ROI → 실용 정보"),
    ]),
    ("⚖️ 비교형", [
        ("{kw} vs {r0} — 뭘 선택해야 할까?", "두 키워드 유입 + 결정 도움"),
        ("{kw} 국내 vs 해외 방식 차이", "글로벌 비교 → 차별화 콘텐츠"),
        ("{kw} 예전 vs 지금 — 무엇이 달라졌나", "변화 비교 → 트렌드 관심"),
        ("전문가 {kw} vs 독학 {kw} — 결과 비교", "학습 방식 비교 → 선택 고민 해소"),
        ("{kw} 비용 vs 효과 — 실제로 해보니", "비용 대비 효과 → 실용적 관심"),
        ("{kw} 유료 vs 무료 — 뭐가 더 나을까?", "비용 비교 → 가성비 관심"),
        ("{kw} 입문자 vs 중급자 — 무엇이 다른가", "레벨별 비교 → 자기 수준 확인"),
        ("{kw}와 {a0} — 어떤 방식이 더 효과적인가", "각도 키워드 비교"),
        ("짧게 하는 {kw} vs 깊게 하는 {kw}", "접근 방식 비교 → 다양한 독자"),
        ("{kw} 성공 사례 vs 실패 사례 비교", "양면 사례 → 균형 잡힌 시각"),
        ("{kw} 국내 1등 vs 해외 1등 비교 분석", "글로벌 비교 → 넓은 관점"),
        ("{kw} A방법 vs B방법 — 직접 해봤습니다", "직접 비교 실험 → 신뢰성"),
        ("{r0} 후 {kw} vs {kw} 먼저 — 순서 비교", "순서 비교 → 실용 인사이트"),
    ]),
    ("🧩 조합형", [
        ("{r0}을 활용한 {kw} 전략", "연관 키워드 크로스오버 → 두 검색어 유입"),
        ("{kw}와 {r1}의 의외의 연결고리", "뜻밖의 조합 → 호기심 자극"),
        ("{a0} 관점에서 본 {kw} 접근법", "시각 전환 조합 → 차별화"),
        ("{kw} + {r0} = 시너지 내는 방법", "조합 공식 → 실용 가치"),
        ("{kw}를 {r1}처럼 하면 어떻게 될까?", "유추 조합 → 창의적 접근"),
        ("{kw}에 {a1}을 더하면 달라지는 것", "요소 추가 조합 → 차별화"),
        ("{r0} 배경지식으로 {kw} 더 잘 이해하기", "배경지식 조합 → 깊이"),
        ("{kw}와 전혀 달라 보이는 {a0}의 공통점", "의외 공통점 → 지적 자극"),
        ("{kw}에 {r2} 기법 적용해봤습니다", "기법 이식 → 실험적 콘텐츠"),
        ("다른 분야에서 배운 {kw} 인사이트", "크로스 도메인 → 창의적 관점"),
        ("{kw} + AI 활용법 — 10배 효율 내기", "AI 조합 → 현재 트렌드"),
        ("{r0} 잘하는 사람들이 {kw}도 잘하는 이유", "역량 연결 → 흥미로운 인사이트"),
        ("{kw}를 {a0} 방식으로 재해석해봤습니다", "재해석 조합 → 독창성"),
    ]),
    ("🔀 시각전환형", [
        ("{a0} 관점으로 보는 {kw} — 이게 핵심이다", "다른 시각 → 차별화 포지셔닝"),
        ("철학적으로 보는 {kw}의 본질", "철학적 시각 → 깊이 있는 콘텐츠"),
        ("{kw}를 데이터로만 봤더니 달라진 것", "데이터 시각 → 객관성 강조"),
        ("외국인 눈으로 본 {kw}의 독특함", "이방인 시각 → 신선함"),
        ("{kw}에서 배울 수 있는 삶의 교훈", "삶의 지혜로 재해석 → 감성"),
        ("역사에서 배우는 {kw} 원칙", "역사적 시각 → 권위성"),
        ("{kw}를 심리학으로 설명하면", "심리학 시각 → 지적 호기심"),
        ("아이 눈으로 본 {kw} — 어른들이 놓친 것", "역발상 시각 → 감성"),
        ("{a1} 관점에서 {kw}를 다시 보다", "각도 키워드 시각 전환"),
        ("10년 후 {kw}는 어떻게 변할까?", "미래 시각 → 예측성 콘텐츠"),
        ("{kw}를 경제학으로 분석하면", "경제학 렌즈 → 지적 흥미"),
        ("예술가가 {kw}를 바라보는 방식", "예술적 시각 → 창의성"),
        ("실패한 사람들에게서 배우는 {kw} 원칙", "역설적 학습원 → 반면교사"),
    ]),
    ("🎯 타겟형", [
        ("직장인을 위한 {kw} 현실 가이드", "직장인 타겟 → 명확한 대상"),
        ("20대라면 지금 당장 시작해야 할 {kw}", "연령 타겟 → 즉각성"),
        ("{kw} 처음 하는 사람 전용 — 이것만 따라하세요", "완전 초보 타겟"),
        ("바쁜 사람을 위한 {kw} 빠른 시작법", "바쁜 사람 타겟 → 효율"),
        ("돈 없어도 할 수 있는 {kw}", "저비용 타겟 → 진입 장벽 낮춤"),
        ("부모님도 이해하는 {kw} 쉬운 설명", "쉬운 설명 타겟 → 공유 가치"),
        ("혼자 하는 {kw} — 팀 없이도 가능합니다", "1인 타겟 → 독립적 접근"),
        ("학생도 할 수 있는 {kw} 시작 방법", "학생 타겟 → 젊은 유입"),
        ("맞벌이 가정을 위한 {kw} 효율 가이드", "특수 상황 타겟"),
        ("{kw} 이미 해봤는데 실패한 분들께", "재도전 타겟 → 특수 공감"),
        ("50대 이후에 시작하는 {kw}", "중장년 타겟 → 틈새 시장"),
        ("{kw}에 관심은 있지만 못 시작한 사람들", "망설임 타겟 → 결심 유도"),
        ("지방에 사는 사람도 할 수 있는 {kw}", "지역 타겟 → 차별화"),
    ]),
    ("📈 성장형", [
        ("{kw} 3개월 만에 성과 낸 방법", "단기 성과 → 강한 동기 부여"),
        ("{kw}로 인생이 달라진 이야기", "라이프 체인지 → 감동 스토리"),
        ("{kw} 꾸준히 했더니 생긴 변화들", "장기 변화 → 동기 유지"),
        ("매일 {kw} 30분의 기적", "작은 습관 → 달성 가능한 목표"),
        ("{kw} 성장 속도를 2배로 높이는 방법", "성장 가속 → 효율 욕구"),
        ("{kw} 1년 전 vs 지금 — 솔직한 성장 기록", "성장 기록 → 공감"),
        ("{kw} 레벨업 하는 현실적인 방법", "레벨업 → 게이미피케이션"),
        ("{kw}에서 정체기가 왔을 때 돌파하는 법", "정체기 극복 → 공감 + 해결책"),
        ("{kw} 성장 로드맵 — 이 순서대로 하세요", "명확한 경로 → 북마크"),
        ("작은 것부터 시작하는 {kw} 성장 전략", "작은 시작 → 실행 가능성"),
        ("{kw} 잘하는 사람들의 공통 습관", "모델링 → 학습 동기"),
        ("{kw}에서 포기하지 않는 법 — 동기 유지 전략", "동기 지속 → 장기 팬 유도"),
        ("{r0}이 {kw} 성장에 미치는 영향", "연관 키워드 성장 연결"),
    ]),
    ("🤔 질문형", [
        ("왜 {kw}를 해야 할까요?", "근본 질문 → 명확한 가치 제시"),
        ("{kw}, 언제 시작하는 게 좋을까요?", "타이밍 질문 → 실용적 답변"),
        ("{kw}를 얼마나 오래 해야 효과가 날까?", "기간 질문 → 현실적 기대"),
        ("왜 {kw}를 해도 안 될까요?", "실패 원인 → 공감 + 해결"),
        ("{kw}에서 가장 중요한 게 뭐냐고요?", "핵심 질문 → 직접적 답변"),
        ("{kw}와 {r0}, 어떤 게 맞는 선택일까요?", "비교 질문 → 결정 도움"),
        ("{kw} 얼마가 적정 비용일까요?", "비용 질문 → 실용 정보"),
        ("혼자 하는 {kw} vs 배우는 {kw} 어떤 게 나을까?", "방법론 질문 → 실용 답변"),
        ("{kw} 언제까지 해야 하나요?", "종료 시점 질문 → 현실적 안내"),
        ("{kw}에서 제일 먼저 배워야 하는 게 뭐예요?", "우선순위 질문 → 로드맵"),
        ("왜 {kw}하는 사람들이 늘고 있을까요?", "트렌드 이유 → 사회 맥락"),
        ("{kw} 해서 후회할 수도 있나요?", "리스크 질문 → 솔직한 답변"),
        ("{kw}에 재능이 없어도 가능한가요?", "진입 장벽 질문 → 희망 메시지"),
    ]),
    ("🏆 랭킹형", [
        ("{kw} TOP 10 — 이 순위가 궁금했다", "랭킹 → 스캔 가능, 클릭률 ↑"),
        ("국내 {kw} 콘텐츠 BEST 5 추천", "추천 랭킹 → 탐색 수요"),
        ("{kw} 역사상 최고의 순간 TOP 7", "역사 랭킹 → 레트로 감성"),
        ("{kw} 분야 세계 1위가 하는 것들", "세계 최고 → 권위 있는 정보"),
        ("{kw} 성공한 사람들의 공통점 TOP 5", "성공 패턴 랭킹"),
        ("망하는 {kw}들의 공통점 TOP 5", "실패 패턴 랭킹 → 경고"),
        ("{kw} 시작하기 좋은 방법 BEST 3", "방법론 랭킹 → 실용성"),
        ("{kw} 관련 책 TOP 5 — 이것만 읽으세요", "책 추천 랭킹 → 부가 가치"),
        ("{kw} 분야 뜨는 크리에이터 TOP 5 소개", "채널 추천 랭킹 → 크로스 프로모션"),
        ("{kw} 자격증 쓸모 있는 것들 순위", "자격증 랭킹 → 실용 정보"),
        ("{r0} 분야에서 {kw} 잘하는 사람 TOP 3", "연관 랭킹 조합"),
        ("{kw} 가성비 TOP 3 — 가격 대비 최고", "가성비 랭킹 → 경제적 관심"),
        ("{kw} 아직도 모르는 사람들이 많은 순위", "몰랐던 순위 → 호기심"),
    ]),
    ("🔬 심층분석형", [
        ("{kw}의 본질에 대한 깊은 고찰", "깊은 인사이트 → 지식욕 자극"),
        ("{kw} 완전 해부 — 구조와 원리까지", "구조 분석 → 전문성"),
        ("{kw} 통계로 보는 실태 분석", "데이터 분석 → 신뢰성"),
        ("{kw} 전문가 인터뷰 10인 핵심 정리", "전문가 종합 → 권위성"),
        ("{kw} 논쟁의 양면 — 찬성 vs 반대 완전 분석", "균형 분석 → 지성 어필"),
        ("{kw} 역사와 미래 — 큰 그림으로 보기", "거시 분석 → 넓은 시각"),
        ("{kw}를 제대로 알려면 알아야 할 배경 지식", "전제 지식 분석 → 깊이"),
        ("{kw} 성공 사례 10개 심층 분석", "사례 분석 → 학습 자료"),
        ("{kw} 비용 구조 완전 해부", "비용 분석 → 실용 정보"),
        ("{kw}와 {a0}의 관계 — 심층 분석", "각도 키워드 심층 연결"),
        ("{kw} 도구·방법론 비교 분석 (2025)", "방법론 비교 → 선택 도움"),
        ("{kw} 트렌드 예측 — 데이터 기반 분석", "예측 분석 → 미래 관심"),
        ("{r0}이 {kw}에 미치는 영향 — 연구 기반 분석", "인과관계 분석"),
    ]),
    ("📅 루틴형", [
        ("{kw} 매일 30분 루틴 — 이렇게 하면 됩니다", "소량 루틴 → 실행 가능성"),
        ("{kw} 주간 루틴 공개 — 실제로 이렇게 합니다", "루틴 공개 → 따라하기"),
        ("{kw} 아침 루틴으로 하루를 시작하는 방법", "아침 루틴 → 건강한 습관"),
        ("{kw} 지속하는 사람들의 습관 만들기 방법", "습관화 → 지속 가능성"),
        ("100일 {kw} 루틴 도전 — 결과는?", "챌린지 기록 → 시리즈 콘텐츠"),
        ("{kw} 시간 효율화 — 바쁜 사람을 위한 루틴", "효율 루틴 → 직장인 타겟"),
        ("{kw} 루틴 세우는 방법 — 작심삼일 탈출", "루틴 설계 → 지속성 고민"),
        ("{kw} 주말 집중 루틴 vs 평일 짧은 루틴", "루틴 비교 → 맞춤 선택"),
        ("{kw} 번아웃 없이 꾸준히 하는 루틴", "번아웃 방지 → 지속 가능"),
        ("전문가처럼 하는 {kw} 일일 체크리스트", "전문가 루틴 → 롤 모델링"),
        ("{kw} 효율 높이는 도구와 루틴 세트", "도구+루틴 조합 → 실용 가치"),
        ("{r0}과 병행하는 {kw} 루틴", "연관 루틴 조합 → 효율"),
        ("처음 시작하는 {kw} 4주 루틴 플랜", "단기 플랜 → 즉시 실행"),
    ]),
    ("🎭 스토리형", [
        ("{kw}로 인생이 바뀐 실화 — 제 이야기입니다", "실화 스토리 → 감동"),
        ("{kw}를 포기했다가 다시 시작한 이유", "포기 후 재기 → 강한 공감"),
        ("완전 실패했던 {kw} 경험에서 배운 것", "실패 스토리 → 반면교사"),
        ("{kw} 전문가가 되기까지 — 처음부터 끝까지", "성장 스토리 → 동기부여"),
        ("아무것도 모르던 내가 {kw}를 시작한 이야기", "제로 투 히어로 → 공감"),
        ("{kw} 하면서 만난 사람들 이야기", "관계 스토리 → 커뮤니티 가치"),
        ("{kw}에 인생을 건 사람의 이야기", "극한 스토리 → 강한 몰입"),
        ("{kw} 10년 베테랑이 말해주는 진짜 이야기", "오랜 경험 스토리 → 권위"),
        ("{kw}로 꿈을 이룬 사람들의 공통점", "성공 스토리 패턴 → 학습"),
        ("{kw} 업계 뒷이야기 — 아무도 모르는 것들", "내부자 이야기 → 독점 느낌"),
        ("{kw} 하면서 후회됐던 선택들과 그 결과", "선택 스토리 → 반면교사"),
        ("현직 {kw} 전문가의 하루 이야기", "현직 스토리 → 직업 탐색"),
        ("내가 {kw}에 빠지게 된 계기 — 솔직 고백", "개인 계기 → 진정성"),
    ]),
    ("🌍 글로벌형", [
        ("해외에서 {kw} 하는 방법 — 국내와 이렇게 다릅니다", "글로벌 비교 → 차별화"),
        ("미국·일본이 {kw}를 대하는 방식 vs 한국", "국가 비교 → 흥미로운 관점"),
        ("{kw} 세계 1위 국가는 어디? 그 이유는?", "글로벌 랭킹 → 흥미"),
        ("해외 {kw} 전문가에게 배운 것들", "해외 권위 → 신뢰성"),
        ("{kw}에서 배울 수 있는 해외 사례", "해외 사례 → 벤치마킹"),
        ("글로벌 {kw} 트렌드 — 한국은 어디쯤 있나?", "글로벌 위치 파악 → 관심"),
        ("한국에서만 통하는 {kw} 방식의 특징", "로컬 특수성 → 정체성"),
        ("해외 직접 체험하고 알게 된 {kw} 사실", "직접 체험 글로벌 → 신뢰"),
        ("{kw}로 해외 진출한 사람들의 이야기", "해외 진출 → 도전 정신"),
        ("영어로 배우는 {kw} vs 한국어로 배우는 {kw}", "언어 비교 → 학습 방법"),
        ("{r0}이 해외에서 어떻게 적용되는지 — {kw} 관점", "해외 적용 사례"),
        ("해외 {kw} 커뮤니티에서 배운 인사이트", "글로벌 커뮤니티 → 정보"),
        ("{kw}의 미래 — 글로벌 전문가들의 예측", "글로벌 미래 예측 → 신뢰"),
    ]),
    ("🛠️ 실전형", [
        ("{kw} 직접 해봤습니다 — 따라해보세요", "직접 시연 → 실용 콘텐츠"),
        ("{kw} 실습 가이드 — 화면 공개하며 알려드립니다", "스크린 공유 → 학습 가치"),
        ("{kw} 처음부터 끝까지 — 라이브로 보여드립니다", "라이브 실전 → 투명성"),
        ("{kw} 실전 케이스 스터디 — 이렇게 해서 성공했습니다", "성공 실전 사례"),
        ("{kw} 초보자가 빠르게 실력 쌓는 실전 연습법", "빠른 실전 → 입문자 유입"),
        ("{kw} 도전 — 완전 노베이스로 며칠 만에 가능할까?", "한계 도전 → 흥미 실험"),
        ("{kw} 실패 사례 재현 — 이렇게 하면 망합니다", "실패 실전 → 경고 + 학습"),
        ("{kw} 전문가처럼 하는 실전 팁 모음", "전문가 실전 팁 → 퀄리티"),
        ("{kw} 1만 원으로 시작해봤습니다", "저비용 실전 → 접근 가능성"),
        ("{kw} 최신 도구로 효율 10배 높이는 법", "도구 활용 실전 → 효율"),
        ("{kw} 단계별 실전 가이드 — 영상 하나로 끝내기", "통합 실전 → 시청 지속"),
        ("{r0} 지식으로 {kw} 실전에 적용하기", "지식 적용 실전 → 연관 키워드"),
        ("{kw} 실전에서 자주 쓰는 도구·명령어 모음", "실용 도구 모음 → 저장 유도"),
    ]),
    ("💬 인터뷰형", [
        ("{kw} 10년 전문가에게 직접 물어봤습니다", "전문가 인터뷰 → 권위"),
        ("{kw}로 성공한 사람들 인터뷰 모음", "성공 인터뷰 → 동기 부여"),
        ("{kw} 현직자가 말하는 진짜 현실", "현직 인터뷰 → 신뢰성"),
        ("{kw} 분야 채용 담당자에게 물어봤습니다", "채용 인터뷰 → 취업 관심"),
        ("{kw} 포기한 사람들은 왜 그랬을까?", "포기자 인터뷰 → 반면교사"),
        ("{kw} 유명 크리에이터에게 물어본 것들", "크리에이터 인터뷰 → 팬 관심"),
        ("{kw} 스타트업 대표 인터뷰 — 현장 이야기", "창업가 인터뷰 → 비즈니스"),
        ("{kw} 관련 전문가에게 묻다 — 솔직 인터뷰", "전문가 솔직 인터뷰 → 신뢰"),
        ("{kw}로 해외 취업한 사람 인터뷰", "해외 취업 인터뷰 → 도전 관심"),
        ("20대 {kw} 고수 vs 50대 {kw} 베테랑 인터뷰", "세대 비교 인터뷰 → 다양성"),
        ("{kw} 그만둔 사람들과 계속하는 사람들의 차이", "지속 vs 이탈 인터뷰"),
        ("{kw} 분야 스카우터의 솔직한 조언", "내부자 조언 인터뷰"),
        ("{r0} 전문가가 보는 {kw}의 미래", "연관 전문가 인터뷰 조합"),
    ]),
    ("🎪 챌린지형", [
        ("{kw} 30일 챌린지 — 과연 가능할까?", "챌린지 실험 → 흥미 + 구독"),
        ("{kw}를 단 7일 만에 마스터해봤습니다", "단기 마스터 챌린지 → 강한 동기"),
        ("{kw}를 전혀 모르는 상태에서 하루 만에 도전", "제로베이스 챌린지 → 공감"),
        ("{kw} 전문가처럼 흉내 낼 수 있을까? 도전!", "모방 챌린지 → 엔터테인먼트"),
        ("{kw} 1,000시간 투자하면 어떻게 될까?", "장기 투자 실험 → 기대감"),
        ("최소 비용으로 {kw} 챌린지 — 0원부터 시작", "0원 챌린지 → 접근 가능"),
        ("{kw}를 거꾸로 해봤습니다 — 결과는?", "역발상 챌린지 → 실험 정신"),
        ("{r0}만 써서 {kw} 해보기 챌린지", "제약 챌린지 → 창의성"),
        ("{kw} 하루 10시간 몰아치기 챌린지", "극한 챌린지 → 강렬한 관심"),
        ("{kw}에 100만 원 투자해봤습니다", "투자 챌린지 → 리얼 데이터"),
        ("아이와 함께 {kw} 챌린지 — 의외의 결과", "가족 챌린지 → 가족 유입"),
        ("{kw}를 AI로만 해봤습니다 — 가능할까?", "AI 한계 챌린지 → 현재 트렌드"),
        ("{kw} 전문가에게 하루 도전 — 배운 것들", "전문가 하루 도전 → 학습"),
    ]),
]


def get_content_suggestions(keyword, related_kw, angle_kw, seed=0):
    """20개 카테고리 × 10개 콘텐츠 주제 추천. seed(0-3)에 따라 다른 세트 노출."""
    rel = [k for k, _ in related_kw] if related_kw else []
    ang = [k for k, _ in angle_kw] if angle_kw else []
    while len(rel) < 5:
        rel.append(keyword)
    while len(ang) < 5:
        ang.append(keyword)
    fmt = {'kw': keyword, 'r0': rel[0], 'r1': rel[1], 'r2': rel[2], 'r3': rel[3],
           'a0': ang[0], 'a1': ang[1]}
    result = []
    for cat_type, pool in _CONTENT_POOLS:
        n = len(pool)
        off = (seed * 3) % n
        items = []
        for i in range(10):
            tmpl, reason = pool[(off + i) % n]
            try:
                title = tmpl.format(**fmt)
            except Exception:
                title = tmpl.replace('{kw}', keyword)
            items.append({'title': title, 'reason': reason})
        result.append({'type': cat_type, 'items': items})
    return result


def _render_content_sugg(suggestions, ctx_key):
    """콘텐츠 주제 추천 렌더링 + 알고리즘 초기화 버튼 (ctx_key: 'trending'|'custom')."""
    seed_key    = f'{ctx_key}_content_seed'
    refresh_key = f'{ctx_key}_content_refresh'
    seed    = st.session_state.get(seed_key, 0)
    refresh = st.session_state.get(refresh_key, 0)
    st.divider()
    _h1, _h2 = st.columns([5, 2])
    _h1.markdown("#### 💡 콘텐츠 주제 추천")
    _h1.caption(f"20개 카테고리 × 각 10개 아이디어 · 현재 세트 {seed + 1}")
    if refresh < 3:
        if _h2.button(f"🔄 알고리즘 초기화 ({refresh + 1}/3)",
                      key=f"cr_{ctx_key}_{refresh}", use_container_width=True):
            st.session_state[seed_key]    = seed + 1
            st.session_state[refresh_key] = refresh + 1
            st.rerun()
    else:
        _h2.caption("초기화 3회 완료")
    for _ci, _cat in enumerate(suggestions):
        with st.expander(f"{_cat['type']}", expanded=(_ci == 0)):
            for _idx, _item in enumerate(_cat['items']):
                st.markdown(
                    f"<div style='padding:7px 10px;margin-bottom:5px;"
                    f"border-left:3px solid #2a2a2a;background:#0e0e0e;"
                    f"border-radius:0 4px 4px 0'>"
                    f"<span style='font-size:.83em;color:#ddd'>"
                    f"<strong>{_idx + 1}.</strong> {_html.escape(_item['title'])}</span><br>"
                    f"<span style='font-size:.71em;color:#aaa'>"
                    f"{_html.escape(_item['reason'])}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )


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
        _rc_lf = st.session_state.get('longform_refresh_count', 0)
        _cs_lf = st.session_state.get('longform_refresh_seed', 0)
        if _rc_lf < 3:
            if st.button(f"🔄 알고리즘 초기화 ({_rc_lf+1}/3)", key="refresh_longform"):
                st.session_state.longform_refresh_seed  = (_cs_lf + 1) % 4
                st.session_state.longform_refresh_count = _rc_lf + 1
                st.session_state.refresh_seed = (_cs_lf + 1) % 4
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
        st.markdown("### 📅 업로드 타이밍 & 키워드 수명")
        st.caption("언제 올려야 조회수가 잘 나오는지, 이 키워드가 지금 뜨는지 식어가는지를 알 수 있습니다.")

        df_time = pd.DataFrame(results)
        df_time['date'] = pd.to_datetime(df_time['published_at'])
        if df_time['date'].dt.tz is not None:
            df_time['date'] = df_time['date'].dt.tz_localize(None)
        now = pd.Timestamp.now()
        df_time['days_old'] = (now - df_time['date']).dt.days

        wd_map   = {0:'월',1:'화',2:'수',3:'목',4:'금',5:'토',6:'일'}
        wd_order = ['월','화','수','목','금','토','일']
        df_time['weekday_kr'] = df_time['date'].dt.weekday.map(wd_map)

        overall_avg = df_time['view_count'].mean() or 1
        top_n   = max(1, len(df_time) // 4)
        top_vids = df_time.nlargest(top_n, 'view_count')

        # ── 최적 요일 계산 ─────────────────────────────────
        wd_avg_s = df_time.groupby('weekday_kr')['view_count'].mean().reindex(wd_order).fillna(0)
        best_day = wd_avg_s.idxmax() if wd_avg_s.sum() > 0 else '—'
        best_day_ratio = wd_avg_s[best_day] / overall_avg if best_day != '—' else 1.0
        top_day  = top_vids['weekday_kr'].value_counts().idxmax() if not top_vids.empty else best_day

        # ── 트렌드 계산 ────────────────────────────────────
        recent_df = df_time[df_time['days_old'] <= 90]
        mid_df    = df_time[(df_time['days_old'] > 90) & (df_time['days_old'] <= 365)]
        old_df    = df_time[df_time['days_old'] > 365]
        recent_avg = recent_df['view_count'].mean() if not recent_df.empty else None
        mid_avg    = mid_df['view_count'].mean()    if not mid_df.empty    else None
        old_avg    = old_df['view_count'].mean()    if not old_df.empty    else 0

        if recent_avg and mid_avg:
            trend_ratio = recent_avg / max(mid_avg, 1)
            if trend_ratio >= 1.3:
                trend_icon, trend_label, trend_desc = "📈", f"+{int((trend_ratio-1)*100)}% 성장 중", (
                    f"최근 3개월 영상이 그 이전보다 평균 **{int((trend_ratio-1)*100)}% 더** 많은 조회수를 받고 있습니다. "
                    "지금이 진입 타이밍입니다.")
            elif trend_ratio <= 0.75:
                trend_icon, trend_label, trend_desc = "📉", f"{abs(int((trend_ratio-1)*100))}% 하락 중", (
                    f"최근 3개월 영상이 이전 대비 **{abs(int((trend_ratio-1)*100))}% 낮은** 조회수를 기록합니다. "
                    "포화되거나 관심이 줄어드는 키워드일 수 있습니다.")
            else:
                trend_icon, trend_label, trend_desc = "➡️", "안정적 유지", (
                    "시기에 관계없이 조회수가 비슷합니다. 꾸준한 수요가 있는 검색 키워드입니다.")
        else:
            trend_icon, trend_label, trend_desc = "❓", "데이터 부족", "영상 수가 적어 트렌드를 측정하기 어렵습니다."

        # ── 콘텐츠 수명 계산 ───────────────────────────────
        if old_avg and overall_avg:
            longevity_ratio = old_avg / overall_avg
            if longevity_ratio >= 0.55:
                life_icon, life_label, life_desc = "🌿", "에버그린 (수명 김)", (
                    f"1년 이상 된 영상도 평균의 **{int(longevity_ratio*100)}%** 조회수를 유지합니다. "
                    "잘 만든 영상 하나가 오래 수익을 냅니다.")
            else:
                life_icon, life_label, life_desc = "⚡", "바이럴형 (최신 유리)", (
                    f"오래된 영상의 조회수가 평균의 **{int(longevity_ratio*100)}%** 수준으로 급감합니다. "
                    "빠른 업로드와 주기적 새 영상이 유리합니다.")
        else:
            life_icon, life_label, life_desc = "❓", "데이터 부족", "1년 이상 된 영상이 없어 수명을 측정하기 어렵습니다."

        last30_cnt = int((df_time['days_old'] <= 30).sum())

        # ── 4개 요약 카드 ──────────────────────────────────
        _c1, _c2, _c3, _c4 = st.columns(4)
        _c1.metric("🎯 최적 업로드 요일", best_day + "요일",
                   f"평균 대비 {best_day_ratio:.1f}배 조회수")
        _c2.metric(f"{trend_icon} 키워드 트렌드", trend_label)
        _c3.metric(f"{life_icon} 콘텐츠 수명", life_label)
        _c4.metric("📤 최근 30일 업로드", f"{last30_cnt}개",
                   "검색 결과 기준")

        st.divider()

        # ── 요일별 분석 ────────────────────────────────────
        st.markdown("#### 📅 요일별 업로드 타이밍 분석")
        st.caption(
            "왼쪽: 각 요일에 올라온 영상들의 평균 조회수 (높을수록 그 요일에 올린 영상이 잘 됨) | "
            "오른쪽: 상위 25% 인기 영상이 몇 요일에 집중됐는지"
        )

        colors_avg = ['#FFD700' if d == best_day else '#3a5a8a' for d in wd_order]
        colors_top = ['#FFD700' if d == top_day  else '#3a5a8a' for d in wd_order]

        wd_avg_df = wd_avg_s.reset_index()
        wd_avg_df.columns = ['요일', '평균 조회수']
        top_wd_s  = top_vids['weekday_kr'].value_counts().reindex(wd_order).fillna(0).reset_index()
        top_wd_s.columns = ['요일', '인기 영상 수']

        _wc1, _wc2 = st.columns(2)
        with _wc1:
            fig1 = px.bar(wd_avg_df, x='요일', y='평균 조회수',
                          title=f'요일별 평균 조회수 (★ {best_day}요일 강조)')
            fig1.update_traces(marker_color=colors_avg)
            fig1.update_layout(showlegend=False, margin=dict(t=40, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with _wc2:
            fig2 = px.bar(top_wd_s, x='요일', y='인기 영상 수',
                          title=f'상위 25% 인기 영상 요일 분포 (★ {top_day}요일 강조)')
            fig2.update_traces(marker_color=colors_top)
            fig2.update_layout(showlegend=False, margin=dict(t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        _best = best_day if best_day == top_day else f"{best_day} (평균) / {top_day} (인기 영상 집중)"
        st.info(f"💡 **추천 업로드 요일: {_best}** — 이 키워드에서 인기 있는 영상들이 가장 많이 올라온 요일입니다.")

        st.divider()

        # ── 키워드 트렌드 & 수명 ───────────────────────────
        st.markdown("#### 📈 키워드 트렌드 & 콘텐츠 수명")
        st.caption(
            "**트렌드**: 최근 영상이 오래된 영상보다 조회수가 높으면 성장 중, 낮으면 하락 중 | "
            "**수명**: 1년 이상 된 영상도 조회수가 높으면 에버그린 콘텐츠"
        )

        trend_rows = []
        for lbl, subset in [
            ('최근 3개월', recent_df),
            ('3개월~1년 전', mid_df),
            ('1년 이상 전', old_df),
        ]:
            if not subset.empty:
                trend_rows.append({
                    '업로드 시점': lbl,
                    '평균 조회수': int(subset['view_count'].mean()),
                    '영상 수': len(subset),
                })

        if trend_rows:
            df_tr = pd.DataFrame(trend_rows)
            bar_colors = ['#E74C3C', '#F39C12', '#27AE60'][:len(trend_rows)]
            fig3 = px.bar(df_tr, x='업로드 시점', y='평균 조회수', text='영상 수',
                          title='업로드 시점별 평균 조회수')
            fig3.update_traces(
                texttemplate='%{text}개 영상',
                textposition='outside',
                marker_color=bar_colors
            )
            fig3.update_layout(
                yaxis_title='평균 조회수',
                margin=dict(t=40, b=20),
                xaxis_title=''
            )
            st.plotly_chart(fig3, use_container_width=True)

            # 해석 메시지
            if trend_desc:
                if trend_ratio >= 1.3 if (recent_avg and mid_avg) else False:
                    st.success(f"{trend_icon} **키워드 트렌드** — {trend_desc}")
                elif trend_ratio <= 0.75 if (recent_avg and mid_avg) else False:
                    st.warning(f"{trend_icon} **키워드 트렌드** — {trend_desc}")
                else:
                    st.info(f"{trend_icon} **키워드 트렌드** — {trend_desc}")

            st.caption("")
            if life_icon == "🌿":
                st.success(f"{life_icon} **콘텐츠 수명** — {life_desc}")
            elif life_icon == "⚡":
                st.warning(f"{life_icon} **콘텐츠 수명** — {life_desc}")
            else:
                st.info(f"{life_icon} **콘텐츠 수명** — {life_desc}")

    # ════ 채널 ════
    with tabs[6]:
        st.markdown("### 📡 채널 분석")
        _rc_ch = st.session_state.get('channel_tab_refresh_count', 0)
        _cs_ch = st.session_state.get('channel_tab_refresh_seed', 0)
        if _rc_ch < 3:
            if st.button(f"🔄 알고리즘 초기화 ({_rc_ch+1}/3)", key="refresh_channel"):
                st.session_state.channel_tab_refresh_seed  = (_cs_ch + 1) % 4
                st.session_state.channel_tab_refresh_count = _rc_ch + 1
                st.session_state.refresh_seed = (_cs_ch + 1) % 4
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
                st.session_state.pop('_wk_result', None)
                st.session_state.pop('_wk_error', None)
                with st.spinner("주간 쇼츠 분석 중..."):
                    try:
                        from youtube_analyzer import YouTubeAnalyzer as _WKA
                        _wk_analyzer = _WKA(_wk_api)
                        _wk_result   = _wk_analyzer.analyze_channel_shorts(_wk_url.strip())
                        storage.add_api_usage(102, st.session_state.username)
                        st.session_state.sq_used = storage.add_sq_usage(_wk_analyzer._sq, st.session_state.username)
                        st.session_state['_wk_result'] = _wk_result
                    except Exception as _e:
                        st.session_state['_wk_error'] = str(_e)
                st.rerun()

            if st.session_state.get('_wk_error'):
                st.error(f"API 오류: {st.session_state['_wk_error']}")

            _wk_result = st.session_state.get('_wk_result')
            if '_wk_result' in st.session_state and _wk_result is None:
                st.warning("채널을 찾을 수 없습니다. URL을 확인해주세요. (예: https://www.youtube.com/@채널명)")
            elif _wk_result:
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
                letter-spacing:-.5px;margin-bottom:4px">키워드 분석</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
        검색어를 입력하면 YouTube 트렌드·기회·채널을 분석합니다
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
        kw          = hv.get('keyword', '')
        disp_label  = hv.get('display_label', kw)
        cur_seed    = hv.get('refresh_seed', 0)
        if not kw:
            st.session_state.history_view = None
            st.rerun()

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

        render_full_analysis(hv.get('results', []), hv.get('channels', {}), hv.get('related_kw', []),
                             hv.get('angle_kw', []), hv.get('title_patterns', {}), kw)

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
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
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
        with st.spinner("트렌딩 키워드 분석 중..."):
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
            st.session_state.sq_used = storage.add_sq_usage(_analyzer._sq, username)
            if _api_bar:
                _u = st.session_state.api_units_used
                _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
                _sq = st.session_state.sq_used
                _sq_text.caption(f"🔎 Search Queries {_sq} / {_sq_lim}회 ({max(_sq_lim - _sq, 0)} 남음)")
            st.rerun()
        else:
            st.warning("트렌딩 키워드를 불러오지 못했습니다. API 키와 할당량을 확인해주세요.")

    # ── 내 키워드 연관 검색어 분석 ──────────────────────────────
    st.divider()
    st.markdown("### 🎯 내 키워드 연관 검색어 분석")
    st.caption("영상으로 만들 키워드를 입력하면 검색량 순 연관어와 콘텐츠 추천을 바로 보여줍니다. (~101 유닛)")

    # 연관검색어 버튼 클릭 시 세팅된 트리거 키워드 처리
    _ck_trigger = st.session_state.get('_ck_search_trigger', '')
    if '_ck_search_trigger' in st.session_state:
        del st.session_state['_ck_search_trigger']
    if _ck_trigger:
        st.session_state['ck_text_input'] = _ck_trigger

    _ck_col1, _ck_col2 = st.columns([4, 1])
    with _ck_col1:
        _ck_input = st.text_input(
            "키워드", placeholder="예: 철학, 주식 투자, 다이어트",
            label_visibility="collapsed", key="ck_text_input"
        )
    with _ck_col2:
        _ck_run = st.button("🔍 분석", type="primary", use_container_width=True, key="ck_run_btn")

    if (_ck_run and _ck_input.strip()) or _ck_trigger:
        _ck_kw = _ck_trigger or _ck_input.strip()
        _ck_hit = storage.get_trending_cache(_ck_kw, -1)  # seed -1 = 커스텀 키워드 캐시
        if _ck_hit:
            st.session_state.custom_kw_input      = _ck_kw
            st.session_state.custom_kw_results    = tuple(_ck_hit)
            st.session_state.custom_content_seed    = 0
            st.session_state.custom_content_refresh = 0
            st.toast("캐시된 결과를 불러왔습니다 (API 0 유닛)", icon="⚡")
            storage.add_trending_history(username, _ck_kw, {
                'source': 'custom',
                'related_kw': _ck_hit[0],
                'angle_kw':   _ck_hit[1],
                'videos': [], 'refresh_seed': 0, 'refresh_count': 0,
            })
        else:
            with st.spinner(f"'{_ck_kw}' 연관어 분석 중..."):
                try:
                    _ck_analyzer = YouTubeAnalyzer(api_key)
                    _ck_rel = _ck_analyzer.get_related_keywords(_ck_kw)
                    _ck_rel2, _ck_ang, _ck_vids = _ck_analyzer.get_trending_analysis(_ck_kw)
                    st.session_state.custom_kw_input      = _ck_kw
                    st.session_state.custom_content_seed    = 0
                    st.session_state.custom_content_refresh = 0
                    st.session_state.custom_kw_results = (_ck_rel, _ck_ang)
                    storage.set_trending_cache(_ck_kw, -1, [_ck_rel, _ck_ang])
                    st.session_state.api_units_used = storage.add_api_usage(101, username)
                    st.session_state.sq_used = storage.add_sq_usage(_ck_analyzer._sq, username)
                    if _api_bar:
                        _u = st.session_state.api_units_used
                        _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                        _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
                        _sq = st.session_state.sq_used
                        _sq_text.caption(f"🔎 Search Queries {_sq} / {_sq_lim}회 ({max(_sq_lim - _sq, 0)} 남음)")
                    storage.add_trending_history(username, _ck_kw, {
                        'source': 'custom',
                        'related_kw': _ck_rel,
                        'angle_kw':   _ck_ang,
                        'videos': [], 'refresh_seed': 0, 'refresh_count': 0,
                    })
                except Exception as _ck_e:
                    st.error(f"API 오류: {_ck_e}")
        st.rerun()

    _ck_saved_input   = st.session_state.get('custom_kw_input', '')
    _ck_saved_results = st.session_state.get('custom_kw_results')
    if _ck_saved_results and _ck_saved_input:
        _ck_r, _ck_a = _ck_saved_results
        _ck_sugg = get_content_suggestions(_ck_saved_input, _ck_r, _ck_a, seed=st.session_state.get('custom_content_seed', 0))

        st.markdown(f"#### 🔍 `{_ck_saved_input}` 연관 검색어 (검색량 순위)")
        st.caption("순위 = YouTube 자동완성 기반 검색 빈도. 클릭하면 해당 키워드 심층 분석.")
        if _ck_r:
            for _idx, (_ckw, _clbl) in enumerate(_ck_r):
                if _idx % 3 == 0:
                    _ck_rcols = st.columns(3)
                with _ck_rcols[_idx % 3]:
                    st.caption(_clbl)
                    if st.button(_ckw, key=f"ck_rel_{_idx}", use_container_width=True):
                        st.session_state['_ck_search_trigger'] = _ckw
                        st.rerun()
        else:
            st.info("연관 검색어를 불러오지 못했습니다.")

        _render_content_sugg(_ck_sugg, 'custom')

    trending = st.session_state.trending_keywords
    selected = st.session_state.trending_selected

    if not trending and not selected:
        st.info("**🔍 키워드 불러오기** 버튼을 눌러 트렌딩 키워드를 가져오세요.")
        st.stop()

    # ── 트렌딩 키워드 그리드 (로드된 경우에만) ────────────────
    if trending:
        st.divider()
        period_label = "일주일" if st.session_state.trending_period == 'week' else "한달"
        st.markdown(f"### 📊 {period_label} 인기 키워드")
        st.caption("클릭하면 해당 키워드로 연관 키워드·다른 시각·콘텐츠 아이디어를 분석합니다.")

        for _i in range(0, min(len(trending), 24), 4):
            _row = trending[_i:_i+4]
            _cols = st.columns(4)
            for _col, (_kw, _cnt) in zip(_cols, _row):
                with _col:
                    _is_sel = (_kw == selected)
                    _label  = f"✅ {_kw}" if _is_sel else _kw
                    if st.button(_label, key=f"tk_{_i}_{_kw}", use_container_width=True,
                                  type="primary" if _is_sel else "secondary"):
                        st.session_state.trending_selected        = _kw
                        st.session_state.trending_analysis        = None
                        st.session_state.trending_refresh_seed    = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count   = 0
                        st.session_state.trending_content_seed    = 0
                        st.session_state.trending_content_refresh = 0
                        st.rerun()
                    _heat = "🔥🔥🔥" if _cnt >= 80 else ("🔥🔥" if _cnt >= 50 else "🔥")
                    st.caption(f"{_heat} 인기도 {_cnt}점")

    # ── 선택된 키워드 분석 ───────────────────────────────────
    if not selected:
        st.stop()

    st.divider()
    st.markdown(f"## 🔎 `{selected}` 심층 분석")

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
            st.session_state.sq_used = storage.add_sq_usage(_analyzer._sq, username)
            if _api_bar:
                _u = st.session_state.api_units_used
                _api_bar.progress(min(int(_u / 10_000 * 100), 100))
                _api_text.caption(f"{_u:,} / 10,000 유닛 사용 ({10_000 - _u:,} 남음)")
                _sq = st.session_state.sq_used
                _sq_text.caption(f"🔎 Search Queries {_sq} / {_sq_lim}회 ({max(_sq_lim - _sq, 0)} 남음)")

        # 히스토리 저장 후 rerun → 사이드바 검색 목록 즉시 반영
        _rel_h, _ang_h, _vids_h = st.session_state.trending_analysis
        storage.add_trending_history(username, selected, {
            'source':         'trending',
            'related_kw':     _rel_h,
            'angle_kw':       _ang_h,
            'videos':         _vids_h,
            'refresh_seed':   st.session_state.get('trending_refresh_seed', 0),
            'refresh_count':  st.session_state.get('trending_refresh_count', 0),
        })
        st.rerun()

    _rel_kw, _ang_kw, _ = st.session_state.trending_analysis
    _suggestions = get_content_suggestions(selected, _rel_kw, _ang_kw, seed=st.session_state.get('trending_content_seed', 0))

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
                        st.session_state.trending_selected        = _kw2
                        st.session_state.trending_analysis        = None
                        st.session_state.trending_refresh_seed    = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count   = 0
                        st.session_state.trending_content_seed    = 0
                        st.session_state.trending_content_refresh = 0
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
                        st.session_state.trending_selected        = _kw2
                        st.session_state.trending_analysis        = None
                        st.session_state.trending_refresh_seed    = get_user_seed_offset(username)
                        st.session_state.trending_refresh_count   = 0
                        st.session_state.trending_content_seed    = 0
                        st.session_state.trending_content_refresh = 0
                        st.rerun()
        else:
            st.info("태그 데이터가 부족합니다.")

    _render_content_sugg(_suggestions, 'trending')

# ══════════════════════════════════════════════════════════
elif page == "📺 쇼츠 분석기":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        📺 쇼츠 레퍼런스 분석기</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
        분석할 쇼츠의 대본을 붙여넣으면 주제·잘된 이유·콘텐츠 방향 5가지를 추천합니다
    </div>''', unsafe_allow_html=True)

    # ── Anthropic API 키 (사이드바에서 관리) ─────────────────
    _ant_key = st.session_state.get('anthropic_key', '')
    if not _ant_key:
        st.error("사이드바에서 Anthropic API 키를 먼저 입력해주세요.")
        st.stop()
    # ── 입력 폼 ───────────────────────────────────────────
    with st.form("shorts_ref_form"):
        _sh_url_input = st.text_input(
            "쇼츠 링크 (선택 — 영상 제목·조회수 자동 입력용)",
            placeholder="https://youtube.com/shorts/xxxxx  또는  youtu.be/xxxxx",
        )
        _sh_script_input = st.text_area(
            "대본 붙여넣기 ✳️",
            placeholder="분석할 쇼츠의 대본(자막)을 여기에 붙여넣으세요.",
            height=180,
        )
        _sh_submit = st.form_submit_button("🔍 분석 시작", type="primary", use_container_width=True)

    if _sh_submit:
        _script_text = _sh_script_input.strip()
        if not _script_text:
            st.error("대본을 입력해주세요.")
            st.stop()

        _vid_id = _extract_vid_id(_sh_url_input.strip()) if _sh_url_input.strip() else None

        with st.spinner("AI 분석 중... (10~20초)"):
            # 영상 정보: URL 있으면 API로, 없으면 기본값
            if _vid_id and api_key:
                try:
                    _yt_tmp = YouTubeAnalyzer(api_key)
                    _vr = _yt_tmp.youtube.videos().list(
                        part='snippet,statistics,contentDetails', id=_vid_id
                    ).execute()
                    if _vr.get('items'):
                        _vi_item = _vr['items'][0]
                        _sa_vinfo = {
                            'title':     _vi_item['snippet']['title'],
                            'channel':   _vi_item['snippet']['channelTitle'],
                            'views':     int(_vi_item.get('statistics', {}).get('viewCount', 0)),
                            'likes':     int(_vi_item.get('statistics', {}).get('likeCount', 0)),
                            'comments':  int(_vi_item.get('statistics', {}).get('commentCount', 0)),
                            'duration':  _yt_tmp.parse_duration(_vi_item['contentDetails']['duration']),
                            'thumbnail': _vi_item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                        }
                    else:
                        _sa_vinfo = {'title': '(제목 없음)', 'channel': '', 'views': 0, 'likes': 0, 'comments': 0, 'duration': 0, 'thumbnail': ''}
                except Exception:
                    _sa_vinfo = {'title': '(제목 없음)', 'channel': '', 'views': 0, 'likes': 0, 'comments': 0, 'duration': 0, 'thumbnail': ''}
            else:
                _sa_vinfo = {'title': '(제목 없음)', 'channel': '', 'views': 0, 'likes': 0, 'comments': 0, 'duration': 0, 'thumbnail': ''}

            try:
                _sa_result = _claude_analyze_shorts(_ant_key, _sa_vinfo, _script_text, seed=0)
                if not _sa_result:
                    st.error("AI 분석 응답 파싱 실패. 다시 시도해주세요.")
                    st.stop()
            except Exception as _ce:
                st.error(f"Claude API 오류:\n\n{_ce}")
                st.stop()

        st.session_state.sa_result        = _sa_result
        st.session_state.sa_vinfo         = _sa_vinfo
        st.session_state.sa_transcript    = _script_text
        st.session_state.sa_url           = _sh_url_input.strip()
        st.session_state.sa_seed          = 0
        st.session_state.sa_refresh_count = 0
        st.rerun()

    # ── 분석 결과 ─────────────────────────────────────────
    _sa = st.session_state.sa_result
    if not _sa:
        st.stop()

    _sv = st.session_state.sa_vinfo

    _sh_c1, _sh_c2 = st.columns([1, 3])
    if _sv.get('thumbnail'):
        _sh_c1.image(_sv['thumbnail'], use_container_width=True)
    with _sh_c2:
        st.markdown(f"### {_sv['title']}")
        st.caption(f"📺 {_sv['channel']} · {_sv['duration']}초")
        _m1, _m2, _m3 = st.columns(3)
        _m1.metric("조회수", f"{_sv['views']:,}")
        _m2.metric("좋아요", f"{_sv['likes']:,}")
        _m3.metric("댓글",   f"{_sv['comments']:,}")

    st.divider()

    st.markdown("#### 📝 대본")
    st.text_area("", value=st.session_state.sa_transcript, height=220, label_visibility="collapsed")

    st.divider()

    st.markdown("#### 🎯 핵심 주제")
    st.info(_sa.get('topic', ''))

    _ta, _tb = st.columns(2)
    with _ta:
        st.markdown("#### 🎬 전개 방식")
        st.markdown(_sa.get('structure', ''))
    with _tb:
        st.markdown("#### 🖊️ 문장 구조 & 표현법")
        st.markdown(_sa.get('expression', ''))

    st.markdown("#### ✨ 잘된 이유")
    for _ri, _r in enumerate(_sa.get('reasons', []), 1):
        st.markdown(f"**{_ri}.** {_r}")

    st.divider()

    _rc   = st.session_state.sa_refresh_count
    _seed = st.session_state.sa_seed
    _rh1, _rh2 = st.columns([4, 1])
    _rh1.markdown(f"#### 💡 콘텐츠 개발 방향 (세트 {_seed + 1})")
    _rh1.caption(_SA_SEED_ANGLES[_seed % len(_SA_SEED_ANGLES)])
    if _rc < 3:
        if _rh2.button(f"🔄 알고리즘 초기화 ({_rc + 1}/3)", key="sa_refresh_btn", use_container_width=True):
            with st.spinner("새 시각으로 전체 분석 중..."):
                try:
                    _new_result = _claude_analyze_shorts(
                        _ant_key, _sv, st.session_state.sa_transcript, seed=_seed + 1
                    )
                    if _new_result:
                        st.session_state.sa_result        = _new_result
                        st.session_state.sa_seed          = _seed + 1
                        st.session_state.sa_refresh_count = _rc + 1
                except Exception as _re:
                    st.error(f"재분析 오류: {_re}")
            st.rerun()
    else:
        _rh2.caption("초기화 3회 완료")

    for _ri, _rec in enumerate(_sa.get('recommendations', []), 1):
        _rtype = _rec.get('type', '')
        _label = f"**{_ri}. [{_rtype}]** {_rec.get('title', '')}" if _rtype else f"**{_ri}. {_rec.get('title', '')}**"
        with st.expander(_label, expanded=(_ri <= 2)):
            st.markdown(f"🎣 **훅 (첫 3초):** {_rec.get('hook', '')}")
            st.markdown(f"🎬 **전개 방식:** {_rec.get('structure', '')}")
            st.markdown(f"💬 **전달 메시지:** {_rec.get('message', '')}")
            st.markdown(f"📈 **왜 잘 될지:** {_rec.get('why', '')}")
# ══════════════════════════════════════════════════════════
elif page == "🔭 채널 발굴":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        🔭 채널 발굴</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
        레퍼런스 채널을 입력하면 키워드를 세밀하게 분석해 비슷한 결의 신규 채널을 발굴합니다
    </div>''', unsafe_allow_html=True)

    if not api_key:
        st.error("사이드바에서 API 키를 먼저 입력해주세요.")
        st.stop()

    _DISC_SEED_LABELS = [
        '기본 (관련도 중심)',
        '최신 발굴 (최근 1년)',
        '다양성 탐색 (참여율 중심)',
        '급성장 발굴 (조회수 중심)',
    ]

    with st.form("channel_discovery_form"):
        _disc_input = st.text_input(
            "채널 링크",
            placeholder="https://www.youtube.com/@채널명  또는  /channel/UCxxxx",
            label_visibility="collapsed",
        )
        _disc_submit = st.form_submit_button("🔭 발굴 시작", type="primary", use_container_width=True)

    if _disc_submit and _disc_input.strip():
        st.session_state.discovery_url           = _disc_input.strip()
        st.session_state.discovery_seed          = 0
        st.session_state.discovery_refresh_count = 0
        st.session_state.discovery_result        = None
        st.session_state.discovery_channel_id    = ''
        st.rerun()

    _disc_url  = st.session_state.get('discovery_url', '')
    _disc_seed = st.session_state.get('discovery_seed', 0)
    _disc_rc   = st.session_state.get('discovery_refresh_count', 0)

    if _disc_url and st.session_state.get('discovery_result') is None:
        _cached_ch_id = st.session_state.get('discovery_channel_id', '')
        if _cached_ch_id:
            _disc_cached = storage.get_discovery_cache(_cached_ch_id, _disc_seed)
            if _disc_cached:
                st.session_state.discovery_result = _disc_cached
                st.toast("캐시된 결과를 불러왔습니다 (API 0 유닛)", icon="⚡")
                st.rerun()
        with st.spinner("채널 키워드 분석 및 유사 채널 발굴 중… (약 510 유닛)"):
            try:
                _disc_analyzer = YouTubeAnalyzer(api_key)
                _disc_fetched  = _disc_analyzer.find_similar_channels(_disc_url, seed=_disc_seed)
                st.session_state.discovery_result     = _disc_fetched
                st.session_state.discovery_channel_id = _disc_fetched['channel_id']
                storage.set_discovery_cache(_disc_fetched['channel_id'], _disc_seed, _disc_fetched)
                st.session_state.api_units_used = storage.add_api_usage(510, username)
                st.session_state.sq_used = storage.add_sq_usage(_disc_analyzer._sq, username)
            except Exception as _disc_e:
                st.error(f"채널 발굴 오류: {_disc_e}")
                st.stop()
        st.rerun()

    _disc_data = st.session_state.get('discovery_result')
    if not _disc_data:
        st.info("채널 링크를 입력하고 **🔭 발굴 시작** 버튼을 눌러주세요.")
        st.stop()

    _ref = _disc_data['reference']
    _chs = _disc_data.get('channels', [])
    _kws = _disc_data.get('keywords_used', [])

    # ── 레퍼런스 채널 정보 ────────────────────────────────
    st.markdown("#### 📺 레퍼런스 채널")
    _rc1, _rc2 = st.columns([1, 5])
    with _rc1:
        if _ref.get('thumbnail'):
            st.image(_ref['thumbnail'], width=64)
    with _rc2:
        st.markdown(
            f"**[{_ref['title']}]({_ref['channel_url']})**  \n"
            f"구독자 **{fmt_num(_ref['subscriber_count'])}명** | "
            f"영상 **{_ref['video_count']:,}개** | "
            f"평균 조회수 **{fmt_num(_ref['avg_views_per_video'])}회**"
        )
        _ref_desc = (_ref.get('description') or '').strip()
        if _ref_desc:
            st.caption(_ref_desc[:120] + ('…' if len(_ref_desc) > 120 else ''))
    if _kws:
        st.caption("분석 키워드: " + "  ".join(f"`{k}`" for k in _kws))
    st.divider()

    # ── 알고리즘 초기화 (최대 3회) ───────────────────────
    _di_col, _db_col = st.columns([4, 1])
    _di_col.caption(
        f"알고리즘 모드: **{_DISC_SEED_LABELS[_disc_seed % 4]}**"
        + (f" · 초기화 {_disc_rc}/3회 사용" if _disc_rc > 0 else "")
    )
    if _disc_rc < 3:
        _next_disc_seed = (_disc_seed + 1) % 4
        if _db_col.button(
            f"🔄 알고리즘 초기화 ({_disc_rc + 1}/3)",
            help=f"다음 모드: {_DISC_SEED_LABELS[_next_disc_seed]}\n다른 키워드·정렬 기준으로 재발굴 (~510 유닛)",
            key="disc_refresh_btn"
        ):
            st.session_state.discovery_seed          = _next_disc_seed
            st.session_state.discovery_refresh_count = _disc_rc + 1
            st.session_state.discovery_result        = None
            st.rerun()
    else:
        _db_col.caption("초기화 3회 완료")

    # ── 요약 통계 ─────────────────────────────────────────
    _chs_a = [c for c in _chs if c.get('grade') == 'A']
    _chs_b = [c for c in _chs if c.get('grade') == 'B']
    _chs_c = [c for c in _chs if c.get('grade') == 'C']
    _ds1, _ds2, _ds3, _ds4 = st.columns(4)
    _ds1.metric("전체 발굴", f"{len(_chs)}개")
    _ds2.metric("🏆 A등급 (추천)", f"{len(_chs_a)}개")
    _ds3.metric("👍 B등급 (발굴)", f"{len(_chs_b)}개")
    _ds4.metric("🔍 C등급 (탐색)", f"{len(_chs_c)}개")
    st.divider()

    if not _chs:
        st.warning("유사 채널을 찾지 못했습니다. 다른 URL이나 알고리즘 초기화를 시도해보세요.")
        st.stop()

    # ── 채널 카드 (3등급 섹션) ────────────────────────────
    _GRADE_CFG = {
        'A': {
            'header':      '🏆 A등급 — 추천 채널',
            'desc':        '여러 관련 키워드에서 반복 등장 · 콘텐츠 품질 우수',
            'badge_color': '#FFD700',
            'badge_bg':    '#2a2000',
        },
        'B': {
            'header':      '👍 B등급 — 발굴 채널',
            'desc':        '관련 키워드에서 등장 · 발굴 가능성 있는 채널',
            'badge_color': '#74B9FF',
            'badge_bg':    '#0d1f35',
        },
        'C': {
            'header':      '🔍 C등급 — 탐색 채널',
            'desc':        '탐색해볼 만한 채널 (낮은 등장 빈도)',
            'badge_color': '#a0a0a0',
            'badge_bg':    '#1a1a1a',
        },
    }

    for _gk in ['A', 'B', 'C']:
        _grp = [c for c in _chs if c.get('grade') == _gk]
        if not _grp:
            continue
        _gc = _GRADE_CFG[_gk]
        st.markdown(f"#### {_gc['header']}")
        st.caption(_gc['desc'])

        for _di in range(0, len(_grp), 3):
            _drow  = _grp[_di:_di + 3]
            _dcols = st.columns(3)
            for _dcol, _dch in zip(_dcols, _drow):
                with _dcol:
                    _subs = _dch['subscriber_count']
                    _grade_badge = (
                        f"<span style='background:{_gc['badge_bg']};color:{_gc['badge_color']};"
                        f"padding:1px 7px;border-radius:4px;font-size:.7em;"
                        f"margin-left:5px;font-weight:700'>{_gk}등급</span>"
                    )
                    _thumb_el = (
                        f'<img src="{_dch["thumbnail"]}" '
                        f'style="width:48px;height:48px;border-radius:50%;'
                        f'object-fit:cover;flex-shrink:0">' 
                        if _dch.get('thumbnail') else
                        '<div style="width:48px;height:48px;border-radius:50%;'
                        'background:#1a1a1a;flex-shrink:0"></div>'
                    )
                    _desc_raw = (_dch.get('description') or '').strip()
                    _desc_esc = _html.escape(_desc_raw[:80]) + ('…' if len(_desc_raw) > 80 else '')
                    _vr_pct   = _dch.get('view_ratio_pct', 0)

                    st.markdown(
                        f'<div style="border:1px solid #222;border-radius:10px;'
                        f'padding:14px;background:#141414;margin-bottom:6px">'
                        f'<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px">'
                        f'{_thumb_el}'
                        f'<div style="flex:1;min-width:0">'
                        f'<div style="font-weight:700;font-size:.9em;line-height:1.3;margin-bottom:2px">'
                        f'<a href="{_dch["channel_url"]}" target="_blank" '
                        f'style="color:#f0f0f0;text-decoration:none">'
                        f'{_html.escape(_dch["title"])}</a>{_grade_badge}</div>'
                        f'<div style="font-size:.72em;color:#aaa;overflow:hidden;'
                        f'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">'
                        f'{_desc_esc if _desc_esc.strip() else "&nbsp;"}</div>'
                        f'</div></div>'
                        f'<table style="width:100%;border-collapse:collapse;font-size:.78em"><tr>'
                        f'<th style="color:#999;font-weight:500;text-align:center;'
                        f'padding:2px 0;border-bottom:1px solid #222">구독자</th>'
                        f'<th style="color:#999;font-weight:500;text-align:center;'
                        f'padding:2px 0;border-bottom:1px solid #222">평균 조회</th>'
                        f'<th style="color:#999;font-weight:500;text-align:center;'
                        f'padding:2px 0;border-bottom:1px solid #222">전환율</th>'
                        f'<th style="color:#999;font-weight:500;text-align:center;'
                        f'padding:2px 0;border-bottom:1px solid #222">등장 횟수</th>'
                        f'</tr><tr>'
                        f'<td style="font-weight:700;text-align:center;padding:3px 0;color:#e8e8e8">'
                        f'{fmt_num(_subs)}</td>'
                        f'<td style="font-weight:700;text-align:center;padding:3px 0;color:#e8e8e8">'
                        f'{fmt_num(_dch["avg_views_per_video"])}</td>'
                        f'<td style="font-weight:700;text-align:center;padding:3px 0;color:#e8e8e8">'
                        f'{_vr_pct}%</td>'
                        f'<td style="font-weight:700;text-align:center;padding:3px 0;color:#e8e8e8">'
                        f'{_dch["appearance_count"]}회</td>'
                        f'</tr></table></div>',
                        unsafe_allow_html=True
                    )
                    st.divider()
        st.divider()

# ══════════════════════════════════════════════════════════
elif page == "📌 저장된 영상":
    st.markdown('''
    <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:4px">
        📌 저장된 영상</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
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
    <div style="font-size:.82rem;color:#888;margin-bottom:20px">
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
            if username != 'admin':
                st.error("관리자만 팀원을 추가할 수 있습니다.")
            else:
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
