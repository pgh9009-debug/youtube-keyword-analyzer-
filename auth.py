import json
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from filelock import FileLock

_DATA_DIR     = os.environ.get('DATA_DIR', os.path.dirname(__file__))
os.makedirs(_DATA_DIR, exist_ok=True)
USERS_FILE    = os.path.join(_DATA_DIR, 'users.json')
SESSIONS_FILE = os.path.join(_DATA_DIR, 'sessions.json')

def _ulock(): return FileLock(USERS_FILE    + '.lock', timeout=5)
def _slock(): return FileLock(SESSIONS_FILE + '.lock', timeout=5)


def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    with _ulock():
        if not os.path.exists(USERS_FILE):
            default = {"admin": {"password": _hash("admin123"), "name": "관리자"}}
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
            return default
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def _write(users):
    with _ulock():
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)


def verify(username, password):
    users = load_users()
    return users.get(username, {}).get('password') == _hash(password)


def display_name(username):
    return load_users().get(username, {}).get('name', username)


def add_user(username, password, name):
    users = load_users()
    if username in users:
        return False, "이미 존재하는 아이디입니다."
    users[username] = {"password": _hash(password), "name": name}
    _write(users)
    return True, "추가 완료"


def change_password(username, old_pw, new_pw):
    if not verify(username, old_pw):
        return False, "현재 비밀번호가 틀렸습니다."
    users = load_users()
    users[username]['password'] = _hash(new_pw)
    _write(users)
    return True, "변경 완료"


def get_api_key(username):
    """저장된 사용자 API 키 반환 (없으면 None)."""
    return load_users().get(username, {}).get('api_key')


def save_api_key(username, api_key):
    """사용자 API 키를 users.json에 저장."""
    users = load_users()
    if username not in users:
        return False
    users[username]['api_key'] = api_key
    _write(users)
    return True


def get_anthropic_key(username):
    """저장된 사용자 Anthropic API 키 반환 (없으면 None)."""
    return load_users().get(username, {}).get('anthropic_key')


def save_anthropic_key(username, key):
    """사용자 Anthropic API 키를 users.json에 저장."""
    users = load_users()
    if username not in users:
        return False
    users[username]['anthropic_key'] = key
    _write(users)
    return True


# ── 관리자 전용 ────────────────────────────────────────────

def admin_update_user(target_id, new_id=None, new_name=None, new_pw=None):
    """아이디·이름·비밀번호를 한번에 수정 (관리자 전용, 현재 비밀번호 불필요)."""
    users = load_users()
    if target_id not in users:
        return False, "존재하지 않는 아이디입니다."

    data = users[target_id]

    if new_name is not None and new_name.strip():
        data['name'] = new_name.strip()

    if new_pw is not None and new_pw.strip():
        data['password'] = _hash(new_pw.strip())

    if new_id is not None and new_id.strip() and new_id.strip() != target_id:
        clean_id = new_id.strip()
        if clean_id in users:
            return False, f"'{clean_id}' 아이디가 이미 존재합니다."
        users[clean_id] = data
        del users[target_id]
    else:
        users[target_id] = data

    _write(users)
    return True, "저장 완료"


def admin_delete_user(target_id):
    """사용자 삭제 (관리자 전용)."""
    users = load_users()
    if target_id not in users:
        return False, "존재하지 않는 아이디입니다."
    del users[target_id]
    _write(users)
    return True, "삭제 완료"


# ── 세션 토큰 (자동 로그인) ────────────────────────────────

def _load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}


def _save_sessions(data):
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_session(username, days=30):
    """로그인 토큰 발급 후 반환 (만료된 토큰 자동 정리)"""
    with _slock():
        sessions = _load_sessions()
        now = datetime.now()
        sessions = {t: s for t, s in sessions.items()
                    if datetime.fromisoformat(s['expires_at']) > now}
        token = secrets.token_urlsafe(32)
        sessions[token] = {
            'username': username,
            'expires_at': (now + timedelta(days=days)).isoformat(),
        }
        _save_sessions(sessions)
    return token


def verify_session(token):
    """유효한 토큰이면 username 반환, 아니면 None"""
    if not token:
        return None
    with _slock():
        sessions = _load_sessions()
    s = sessions.get(token)
    if not s:
        return None
    if datetime.fromisoformat(s['expires_at']) < datetime.now():
        return None
    return s['username']


def revoke_session(token):
    """토큰 삭제 (로그아웃 시 호출)"""
    if not token:
        return
    with _slock():
        sessions = _load_sessions()
        sessions.pop(token, None)
        _save_sessions(sessions)
