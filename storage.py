import json
import os
from datetime import datetime, timedelta

SAVED_FILE     = os.path.join(os.path.dirname(__file__), 'saved_videos.json')
API_USAGE_FILE = os.path.join(os.path.dirname(__file__), 'api_usage.json')
HISTORY_FILE   = os.path.join(os.path.dirname(__file__), 'search_history.json')
SEARCH_CACHE_FILE   = os.path.join(os.path.dirname(__file__), 'search_cache.json')
TRENDING_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'trending_cache.json')
_CACHE_MAX_ENTRIES = 80   # 파일당 최대 항목 수


def load_all():
    if not os.path.exists(SAVED_FILE):
        return []
    with open(SAVED_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write(data):
    with open(SAVED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_saved(video_id, username):
    return any(s['video_id'] == video_id and s['saved_by'] == username for s in load_all())


def save_video(video, username, keyword='', memo=''):
    saved = load_all()
    if is_saved(video['video_id'], username):
        return False
    saved.append({
        'video_id': video['video_id'],
        'title': video['title'],
        'channel_title': video['channel_title'],
        'channel_id': video.get('channel_id', ''),
        'url': video['url'],
        'thumbnail': video.get('thumbnail', ''),
        'view_count': video.get('view_count', 0),
        'like_count': video.get('like_count', 0),
        'engagement_rate': video.get('engagement_rate', 0),
        'type': video.get('type', ''),
        'duration_str': video.get('duration_str', ''),
        'memo': memo,
        'keyword': keyword,
        'saved_by': username,
        'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    })
    _write(saved)
    return True


def update_memo(video_id, username, memo):
    saved = load_all()
    for s in saved:
        if s['video_id'] == video_id and s['saved_by'] == username:
            s['memo'] = memo
    _write(saved)


def delete_video(video_id, username):
    saved = [s for s in load_all() if not (s['video_id'] == video_id and s['saved_by'] == username)]
    _write(saved)


def get_saved_by_user(username):
    return [s for s in load_all() if s['saved_by'] == username]


# ── API 사용량 (사용자별·날짜별 영속 저장) ───────────────

def _load_usage_file():
    today = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(API_USAGE_FILE):
        return today, {}
    with open(API_USAGE_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception:
            return today, {}
    if data.get('date') != today:
        return today, {}
    return today, data.get('usage', {})


def get_api_usage(username):
    """오늘 날짜의 사용자별 API 사용량 반환."""
    _, usage = _load_usage_file()
    return usage.get(username, 0)


def add_api_usage(units, username):
    """사용자 사용량을 더하고 오늘의 누적 합계를 반환."""
    today, usage = _load_usage_file()
    usage[username] = usage.get(username, 0) + units
    with open(API_USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'date': today, 'usage': usage}, f)
    return usage[username]


# ── 검색 기록 (사용자별·날짜별, API 사용량과 동일 주기로 초기화) ──

def _load_history_file():
    today = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(HISTORY_FILE):
        return today, {}
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception:
            return today, {}
    if data.get('date') != today:
        return today, {}
    return today, data.get('history', {})


def add_search_history(username, keyword, analysis_snapshot):
    """
    검색 기록 저장. 같은 키워드가 이미 있으면 덮어씀 (새로고침 지원).
    analysis_snapshot: {'results': [...], 'channels': {...}, 'related_kw': [...],
                        'angle_kw': [...], 'title_patterns': {...}}
    """
    today, history = _load_history_file()
    user_hist = [h for h in history.get(username, []) if h['keyword'] != keyword]
    user_hist.insert(0, {
        'keyword': keyword,
        'time': datetime.now().strftime('%H:%M'),
        **analysis_snapshot,
    })
    history[username] = user_hist[:30]   # 하루 최대 30건
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({'date': today, 'history': history}, f, ensure_ascii=False)


def get_search_history(username):
    """오늘의 사용자 검색 기록 반환 (최신순)."""
    _, history = _load_history_file()
    return history.get(username, [])


# ── 결과 캐시 (검색/트렌딩 공유 캐시, TTL=2시간) ─────────────

def _load_cache_file(fname):
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache_file(fname, cache):
    if len(cache) > _CACHE_MAX_ENTRIES:
        sorted_items = sorted(cache.items(), key=lambda x: x[1].get('ts', ''))
        cache = dict(sorted_items[-_CACHE_MAX_ENTRIES:])
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception:
        pass

def get_search_cache(keyword: str, seed: int, ttl_hours: int = 2):
    """캐시 히트 시 data 반환, 없거나 만료 시 None."""
    cache = _load_cache_file(SEARCH_CACHE_FILE)
    entry = cache.get(f"{keyword}::{seed}")
    if not entry:
        return None
    try:
        if datetime.now() - datetime.fromisoformat(entry['ts']) > timedelta(hours=ttl_hours):
            return None
    except Exception:
        return None
    return entry.get('data')

def set_search_cache(keyword: str, seed: int, data: dict):
    cache = _load_cache_file(SEARCH_CACHE_FILE)
    cache[f"{keyword}::{seed}"] = {'ts': datetime.now().isoformat(), 'data': data}
    _save_cache_file(SEARCH_CACHE_FILE, cache)

def get_trending_cache(keyword: str, seed: int, ttl_hours: int = 2):
    cache = _load_cache_file(TRENDING_CACHE_FILE)
    entry = cache.get(f"{keyword}::{seed}")
    if not entry:
        return None
    try:
        if datetime.now() - datetime.fromisoformat(entry['ts']) > timedelta(hours=ttl_hours):
            return None
    except Exception:
        return None
    return entry.get('data')

def set_trending_cache(keyword: str, seed: int, data):
    cache = _load_cache_file(TRENDING_CACHE_FILE)
    cache[f"{keyword}::{seed}"] = {'ts': datetime.now().isoformat(), 'data': data}
    _save_cache_file(TRENDING_CACHE_FILE, cache)
