import json
import os
import logging
from datetime import datetime, timedelta
from filelock import FileLock

_DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
os.makedirs(_DATA_DIR, exist_ok=True)

SAVED_FILE     = os.path.join(_DATA_DIR, 'saved_videos.json')
API_USAGE_FILE = os.path.join(_DATA_DIR, 'api_usage.json')
HISTORY_FILE   = os.path.join(_DATA_DIR, 'search_history.json')
TRENDING_HISTORY_FILE = os.path.join(_DATA_DIR, 'trending_history.json')
SEARCH_CACHE_FILE   = os.path.join(_DATA_DIR, 'search_cache.json')
TRENDING_CACHE_FILE = os.path.join(_DATA_DIR, 'trending_cache.json')
_CACHE_MAX_ENTRIES = 80

def _lock(path):
    return FileLock(path + '.lock', timeout=5)


def load_all():
    if not os.path.exists(SAVED_FILE):
        return []
    with _lock(SAVED_FILE):
        with open(SAVED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def _write(data):
    with _lock(SAVED_FILE):
        with open(SAVED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def is_saved(video_id, username):
    return any(s['video_id'] == video_id and s['saved_by'] == username for s in load_all())


def save_video(video, username, keyword='', memo=''):
    with _lock(SAVED_FILE):
        saved = []
        if os.path.exists(SAVED_FILE):
            with open(SAVED_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
        if any(s['video_id'] == video['video_id'] and s['saved_by'] == username for s in saved):
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
        with open(SAVED_FILE, 'w', encoding='utf-8') as f:
            json.dump(saved, f, ensure_ascii=False, indent=2)
    return True


def update_memo(video_id, username, memo):
    with _lock(SAVED_FILE):
        if not os.path.exists(SAVED_FILE):
            return
        with open(SAVED_FILE, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        for s in saved:
            if s['video_id'] == video_id and s['saved_by'] == username:
                s['memo'] = memo
        with open(SAVED_FILE, 'w', encoding='utf-8') as f:
            json.dump(saved, f, ensure_ascii=False, indent=2)


def delete_video(video_id, username):
    with _lock(SAVED_FILE):
        if not os.path.exists(SAVED_FILE):
            return
        with open(SAVED_FILE, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        saved = [s for s in saved if not (s['video_id'] == video_id and s['saved_by'] == username)]
        with open(SAVED_FILE, 'w', encoding='utf-8') as f:
            json.dump(saved, f, ensure_ascii=False, indent=2)


def get_saved_by_user(username):
    return [s for s in load_all() if s['saved_by'] == username]


# ── API 사용량 ───────────────────────────────────────────────

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
    with _lock(API_USAGE_FILE):
        _, usage = _load_usage_file()
    return usage.get(username, 0)


def add_api_usage(units, username):
    with _lock(API_USAGE_FILE):
        today, usage = _load_usage_file()
        usage[username] = usage.get(username, 0) + units
        with open(API_USAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'date': today, 'usage': usage}, f)
    return usage[username]


# ── 검색 기록 ────────────────────────────────────────────────

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
    with _lock(HISTORY_FILE):
        today, history = _load_history_file()
        user_hist = [h for h in history.get(username, []) if h.get('keyword') != keyword]
        user_hist.insert(0, {
            'keyword': keyword,
            'time': datetime.now().strftime('%H:%M'),
            **analysis_snapshot,
        })
        history[username] = user_hist[:30]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'date': today, 'history': history}, f, ensure_ascii=False)


def get_search_history(username):
    with _lock(HISTORY_FILE):
        _, history = _load_history_file()
    return history.get(username, [])


# ── 트렌딩 검색 기록 ─────────────────────────────────────────

def _load_trending_history_file():
    today = datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(TRENDING_HISTORY_FILE):
        return today, {}
    with open(TRENDING_HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception:
            return today, {}
    if data.get('date') != today:
        return today, {}
    return today, data.get('history', {})


def add_trending_history(username, keyword, snapshot):
    with _lock(TRENDING_HISTORY_FILE):
        today, history = _load_trending_history_file()
        user_hist = [h for h in history.get(username, []) if h.get('keyword') != keyword]
        user_hist.insert(0, {
            'keyword': keyword,
            'time': datetime.now().strftime('%H:%M'),
            **snapshot,
        })
        history[username] = user_hist[:20]
        with open(TRENDING_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'date': today, 'history': history}, f, ensure_ascii=False)


def get_trending_history(username):
    with _lock(TRENDING_HISTORY_FILE):
        _, history = _load_trending_history_file()
    return history.get(username, [])


# ── 결과 캐시 ────────────────────────────────────────────────

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
    except Exception as e:
        logging.warning(f"캐시 쓰기 실패 ({fname}): {e}")

def get_search_cache(keyword: str, seed: int, ttl_hours: int = 2):
    with _lock(SEARCH_CACHE_FILE):
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
    with _lock(SEARCH_CACHE_FILE):
        cache = _load_cache_file(SEARCH_CACHE_FILE)
        cache[f"{keyword}::{seed}"] = {'ts': datetime.now().isoformat(), 'data': data}
        _save_cache_file(SEARCH_CACHE_FILE, cache)

def get_trending_cache(keyword: str, seed: int, ttl_hours: int = 2):
    with _lock(TRENDING_CACHE_FILE):
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
    with _lock(TRENDING_CACHE_FILE):
        cache = _load_cache_file(TRENDING_CACHE_FILE)
        cache[f"{keyword}::{seed}"] = {'ts': datetime.now().isoformat(), 'data': data}
        _save_cache_file(TRENDING_CACHE_FILE, cache)


# ── 채널 발굴 캐시 ───────────────────────────────────────────
CHANNEL_DISCOVERY_CACHE_FILE = os.path.join(_DATA_DIR, 'channel_discovery_cache.json')

def get_discovery_cache(channel_id: str, seed: int, ttl_hours: int = 2):
    with _lock(CHANNEL_DISCOVERY_CACHE_FILE):
        cache = _load_cache_file(CHANNEL_DISCOVERY_CACHE_FILE)
    entry = cache.get(f"{channel_id}::{seed}")
    if not entry:
        return None
    try:
        if datetime.now() - datetime.fromisoformat(entry['ts']) > timedelta(hours=ttl_hours):
            return None
    except Exception:
        return None
    return entry.get('data')

def set_discovery_cache(channel_id: str, seed: int, data):
    with _lock(CHANNEL_DISCOVERY_CACHE_FILE):
        cache = _load_cache_file(CHANNEL_DISCOVERY_CACHE_FILE)
        cache[f"{channel_id}::{seed}"] = {'ts': datetime.now().isoformat(), 'data': data}
        _save_cache_file(CHANNEL_DISCOVERY_CACHE_FILE, cache)
