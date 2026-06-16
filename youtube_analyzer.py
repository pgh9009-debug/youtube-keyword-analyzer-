from googleapiclient.discovery import build
from datetime import datetime, timedelta
import isodate
import requests
import json
import re
from collections import Counter


class YouTubeAnalyzer:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def parse_duration(self, duration_str):
        try:
            return int(isodate.parse_duration(duration_str).total_seconds())
        except Exception:
            return 0

    def format_duration(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _search_video_ids(self, query, max_results, order='relevance', published_after=None):
        params = dict(q=query, part='id', type='video',
                      maxResults=max_results, order=order)
        if published_after:
            params['publishedAfter'] = published_after
        resp = self.youtube.search().list(**params).execute()
        return [item['id']['videoId'] for item in resp.get('items', [])]

    # 새로고침 시드별 검색 설정
    # seed 0 (기본):     관련도 + 조회수순   + 쇼츠 관련도   — YouTube 기본 알고리즘
    # seed 1 (최신인기): 날짜순 + 평점순     + 쇼츠 날짜순   — 최근 1년, 좋아요 비율 높은 영상
    # seed 2 (숨겨진발굴):평점순 + 날짜순    + 쇼츠 조회수   — 최근 2년, 알고리즘 미노출 콘텐츠
    # seed 3 (6개월급상승):조회수 + 관련도   + 쇼츠 평점순   — 최근 6개월 내 급성장 영상
    _REFRESH_CONFIGS = [
        {'main': 'relevance', 'sub': 'viewCount', 'shorts': 'relevance', 'days': None},
        {'main': 'date',      'sub': 'rating',    'shorts': 'date',      'days': 365},
        {'main': 'rating',    'sub': 'date',      'shorts': 'viewCount', 'days': 730},
        {'main': 'viewCount', 'sub': 'relevance', 'shorts': 'rating',    'days': 180},
    ]

    def analyze_keyword(self, keyword, max_results=20, refresh_seed=0):
        """
        refresh_seed: 0=기본 / 1=최신인기 / 2=숨겨진발굴 / 3=6개월급상승
        반환: results 리스트
        """
        cfg = self._REFRESH_CONFIGS[refresh_seed % len(self._REFRESH_CONFIGS)]
        after = None
        if cfg['days']:
            after = (datetime.utcnow() - timedelta(days=cfg['days'])).strftime('%Y-%m-%dT%H:%M:%SZ')

        relevance_ids = self._search_video_ids(keyword, max_results, order=cfg['main'], published_after=after)
        viewcount_ids = self._search_video_ids(keyword, max_results, order=cfg['sub'],  published_after=after)
        shorts_ids    = self._search_video_ids(f"{keyword} #shorts", 50, order=cfg['shorts'], published_after=after)

        # 중복 제거: 쇼츠 → 조회수순 → 관련도순 우선 배치
        seen = set()
        video_ids = []
        for vid in shorts_ids + viewcount_ids + relevance_ids:
            if vid not in seen:
                seen.add(vid)
                video_ids.append(vid)

        if not video_ids:
            return []

        # 50개씩 나눠서 조회 (API 한 번에 최대 50개)
        all_items = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            resp = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(chunk)
            ).execute()
            all_items.extend(resp.get('items', []))

        videos_resp = {'items': all_items}

        results = []
        for item in videos_resp.get('items', []):
            snippet = item['snippet']
            stats = item.get('statistics', {})
            duration_sec = self.parse_duration(item['contentDetails']['duration'])
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0))
            comment_count = int(stats.get('commentCount', 0))
            engagement_rate = round((like_count + comment_count) / view_count * 100, 2) if view_count else 0
            tags_text = ' '.join(snippet.get('tags', [])).lower()
            text = (snippet.get('title', '') + snippet.get('description', '') + tags_text).lower()
            # 쇼츠 판별: 60초 이하 OR #shorts 태그/제목 OR 180초 이하이면서 shorts 키워드 포함
            is_shorts = (
                duration_sec <= 60
                or '#shorts' in text
                or 'shorts' in tags_text
                or (duration_sec <= 180 and 'shorts' in text)
            )

            results.append({
                'video_id': item['id'],
                'title': snippet['title'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'][:10],
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count,
                'engagement_rate': engagement_rate,
                'duration_sec': duration_sec,
                'duration_str': self.format_duration(duration_sec),
                'type': 'shorts' if is_shorts else 'longform',
                'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                'url': f"https://youtube.com/watch?v={item['id']}",
                'tags': snippet.get('tags', []),
            })

        results.sort(key=lambda x: x['view_count'], reverse=True)

        # 채널당 최대 2개 영상 제한 — 같은 채널이 결과를 독점하지 않도록
        ch_count = Counter()
        deduped = []
        for v in results:
            if ch_count[v['channel_id']] < 2:
                deduped.append(v)
                ch_count[v['channel_id']] += 1

        return deduped

    def get_related_keywords(self, keyword):
        """
        YouTube 자동완성 기반 연관 키워드.
        반환: [(keyword, rank_label), ...]
        - 원본 키워드 단어(2자↑)와 겹치는 제안만 포함 → 무관한 자동완성 제거
        """
        kw_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', keyword.lower()))
        try:
            resp = requests.get(
                'https://suggestqueries.google.com/complete/search',
                params={'client': 'firefox', 'ds': 'yt', 'q': keyword, 'hl': 'ko'},
                timeout=5
            )
            data = json.loads(resp.text)
            raw = [kw for kw in data[1][:18] if kw != keyword]

            # 1차 필터: 원본 키워드 단어와 교집합이 있는 것만
            filtered = [s for s in raw
                        if kw_words & set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', s.lower()))]

            # 너무 적으면 2차: 원본이 부분 문자열로 포함된 것 추가
            if len(filtered) < 5:
                for s in raw:
                    if s not in filtered and keyword.lower() in s.lower():
                        filtered.append(s)

            result = []
            for i, kw in enumerate(filtered[:12]):
                if i == 0:   label = '🔥 1위'
                elif i == 1: label = '🔥 2위'
                elif i == 2: label = '🔥 3위'
                elif i < 6:  label = f'📈 {i+1}위'
                else:        label = f'{i+1}위'
                result.append((kw, label))
            return result
        except Exception:
            return []

    def get_angle_keywords(self, keyword, videos):
        """
        태그 기반 '다른 시각' 키워드.
        반환: [(keyword, count), ...] — count는 등장 영상 수
        가중치: 조회수 × 최신성 (고조회수·최신 영상 태그를 더 중요하게)
        """
        kw_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', keyword.lower()))
        generic_stop = {
            'shorts', 'short', '쇼츠', 'youtube', 'youtuber', '유튜브', '유튜버',
            'viral', '바이럴', 'trending', '트렌딩', 'subscribe', '구독',
            'video', '영상', 'vlog', '브이로그', 'like', '좋아요',
            'content', '콘텐츠', 'daily', '일상', 'official', '공식',
        }

        tag_score = Counter()
        tag_video_count = Counter()
        now = datetime.now()

        for v in videos:
            try:
                days_old = (now - datetime.strptime(v['published_at'], '%Y-%m-%d')).days
            except Exception:
                days_old = 365
            recency_w = max(0.5, 1.0 - days_old / 1825)           # 5년 기준 0.5~1.0
            view_w    = min(2.0, (max(1, v['view_count']) / 100_000) ** 0.3)  # 10만 기준

            seen = set()
            for tag in v.get('tags', []):
                tl = tag.lower().strip()
                if tl in seen or len(tl) < 2 or tl in generic_stop:
                    continue
                seen.add(tl)
                t_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', tl))
                if kw_words & t_words:   # 원본 키워드 단어 포함 → 제외
                    continue
                tag_score[tl]       += recency_w * view_w
                tag_video_count[tl] += 1

        # 2개 이상 영상 등장 & 가중치 점수 상위 10개
        candidates = [(t, tag_video_count[t])
                      for t, _ in tag_score.most_common(20)
                      if tag_video_count[t] >= 2]
        return candidates[:10]

    def get_title_patterns(self, videos):
        """제목에서 자주 등장하는 키워드 추출 (불용어 제거)"""
        stop = {
            '이', '가', '을', '를', '은', '는', '의', '에', '와', '과', '로', '으로',
            '하는', '하기', '하면', '해서', '그리고', '하다', '있는', '없는', '대한',
            '위한', '이런', '저런', '이번', '영상', '유튜브', '채널', '구독', '좋아요',
            'the', 'a', 'an', 'is', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'by'
        }
        words = []
        for v in videos:
            for w in re.findall(r'[가-힣a-zA-Z0-9]+', v['title']):
                if len(w) >= 2 and w.lower() not in stop:
                    words.append(w)
        return Counter(words).most_common(20)

    def get_trending_keywords(self, period='week', region='KR', max_results=50):
        """
        인기 영상 제목 기반 트렌딩 키워드 추출.
        반환: [(keyword, hotness_score), ...]  — hotness_score: 최고 키워드=100 기준 상대 점수
          week : videos.list(chart=mostPopular) → 1 유닛
          month: search.list(relevanceLanguage='ko') + videos.list → 101 유닛

        점수 = 출현빈도(60%) + 해당 영상 평균 조회수 비율(40%)
        · search.list 에서 regionCode + order=viewCount 조합은 API 미지원 →
          month 는 relevanceLanguage='ko' 사용
        """
        stop = {
            # 조사·어미
            '이','가','을','를','은','는','의','에','와','과','로','으로','에서','에게',
            '부터','까지','이나','보다','처럼','만큼','라서','이서','에도',
            # 접속·지시
            '그리고','그래서','그런데','하지만','또는','혹은','이유','경우',
            '이것','그것','저것','여기','거기',
            # 동사·형용사 어간
            '하는','하기','하면','해서','했다','하다','됩니다','이다','있다','없다',
            '있는','없는','되는','같은','되고','하고','이고','만들','받는','주는',
            '알아','보는','가는','오는','나오','해주','드리','알려','정리',
            # 부사
            '진짜','정말','너무','완전','매우','아주','바로','이미','다시','계속',
            '쉽게','빠르게','처음','나중','같이','함께','그냥','혼자','직접','이렇게',
            # 서술형 형용사
            '좋은','나쁜','큰','작은','많은','적은','새로운','다양한','특별한',
            '중요한','필요한','기본','일반','공통','심한','강한','약한',
            # 미디어·유튜브 일반어
            '영상','유튜브','채널','구독','좋아요','댓글','알림','조회','시청',
            '썸네일','업로드','라이브','방송','공식','소개','리뷰','후기','브이로그',
            '일상','콘텐츠','컨텐츠','에피소드','시리즈','편집','커버',
            # 시간
            '오늘','어제','내일','이번','다음','지난','요즘','최근','올해','작년',
            '년도','연도','시간','분기',
            # 숫자·단위·서수
            '번째','가지','개월','년째','위','등','명','원','번','개','만에',
            # 영어 불용어
            'the','a','an','is','in','on','at','to','for','and','or','by','of',
            'my','this','that','with','from','have','been','will','what','how',
            'why','when','where','who','can','get','all','new','more','see','out',
            # 포맷 태그
            'shorts','short','vlog','ep','mv','ver','ft','official','remix',
            'part','feat','live','cover','challenge','video','clip',
        }

        try:
            if period == 'week':
                resp  = self.youtube.videos().list(
                    part='snippet,statistics',
                    chart='mostPopular',
                    regionCode=region,
                    maxResults=max_results
                ).execute()
                items = resp.get('items', [])
            else:
                # month: regionCode + order=viewCount 조합은 YouTube API 미지원.
                # relevanceLanguage='ko' 로 한국어 콘텐츠 필터링
                after = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
                s_resp = self.youtube.search().list(
                    part='id', type='video',
                    order='viewCount',
                    publishedAfter=after,
                    relevanceLanguage='ko',
                    maxResults=max_results
                ).execute()
                ids = [i['id']['videoId'] for i in s_resp.get('items', [])]
                if not ids:
                    return []
                v_resp = self.youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(ids[:50])
                ).execute()
                items = v_resp.get('items', [])

            if not items:
                return []

            # ── 조회수 기반 가중 점수 계산 ──────────────────────
            view_counts = [int(it.get('statistics', {}).get('viewCount', 0)) for it in items]
            avg_view    = max(sum(view_counts) / len(view_counts), 1)
            n           = len(items)

            kw_cnt   = Counter()   # 등장 영상 수
            kw_vsum  = {}          # 등장한 영상들의 조회수 합

            for item, vc in zip(items, view_counts):
                title = item['snippet'].get('title', '')
                seen  = set()
                for w in re.findall(r'[가-힣]{2,}|[a-zA-Z]{4,}', title):
                    if w.lower() in stop or w in seen:
                        continue
                    seen.add(w)
                    kw_cnt[w] += 1
                    kw_vsum[w] = kw_vsum.get(w, 0) + vc

            # 최소 임계값: 전체 영상의 8% 이상 등장 (50개 기준 ≈ 4회)
            min_cnt = max(3, int(n * 0.08))

            raw = {}
            for kw, cnt in kw_cnt.items():
                if cnt < min_cnt:
                    continue
                freq_s = cnt / n                                  # 0~1  빈도 점수
                view_s = (kw_vsum[kw] / cnt) / avg_view          # ~1   조회수 영향
                raw[kw] = freq_s * 0.6 + min(view_s, 3) / 3 * 0.4

            if not raw:
                return []

            # 최고값 = 100 으로 정규화
            max_s  = max(raw.values())
            scored = sorted(
                [(kw, max(1, round(s / max_s * 100))) for kw, s in raw.items()],
                key=lambda x: x[1], reverse=True
            )
            return scored[:20]

        except Exception:
            return []

    def get_trending_analysis(self, keyword, max_results=20):
        """
        트렌딩 키워드 상세 분석 (가벼운 버전 — 연관/시각 키워드용)
        API 비용: search(100) + videos(1) ≈ 101유닛
        반환: (related_kw, angle_kw, videos)
        """
        try:
            video_ids = self._search_video_ids(keyword, max_results)
            if not video_ids:
                return [], [], []
            resp = self.youtube.videos().list(
                part='snippet,statistics', id=','.join(video_ids)
            ).execute()
            videos = []
            for item in resp.get('items', []):
                sn  = item['snippet']
                st_ = item.get('statistics', {})
                videos.append({
                    'title':        sn['title'],
                    'channel_id':   sn['channelId'],
                    'published_at': sn['publishedAt'][:10],
                    'view_count':   int(st_.get('viewCount', 0)),
                    'like_count':   int(st_.get('likeCount', 0)),
                    'comment_count':int(st_.get('commentCount', 0)),
                    'tags':         sn.get('tags', []),
                })
            related_kw = self.get_related_keywords(keyword)
            angle_kw   = self.get_angle_keywords(keyword, videos)
            return related_kw, angle_kw, videos
        except Exception:
            return [], [], []

    @staticmethod
    def grade_channel(ch, channel_videos):
        """
        채널 등급 산출 (S/A/B/C/D)
        종합 점수 = 전환율(40%) + 좋아요율(35%) + 댓글율(15%) + 생산성(10%)
        반환: (grade, grade_label, total_score)
        """
        subs      = max(ch.get('subscriber_count', 1), 1)
        avg_views = ch.get('avg_views_per_video', 0)

        # 1) 구독자 전환율 (영상당 평균 조회수 / 구독자) — 40%
        view_ratio = avg_views / subs
        if view_ratio >= 0.5:    ratio_score = 5
        elif view_ratio >= 0.2:  ratio_score = 4
        elif view_ratio >= 0.1:  ratio_score = 3
        elif view_ratio >= 0.05: ratio_score = 2
        else:                    ratio_score = 1

        # 2) 좋아요율 (likes / views) — 35%
        if channel_videos:
            avg_like_rate = sum(v['like_count'] / max(v['view_count'], 1) * 100
                                for v in channel_videos) / len(channel_videos)
            avg_cmt_rate  = sum(v['comment_count'] / max(v['view_count'], 1) * 100
                                for v in channel_videos) / len(channel_videos)
        else:
            avg_like_rate = avg_cmt_rate = 0

        if avg_like_rate >= 5:    like_score = 5
        elif avg_like_rate >= 3:  like_score = 4
        elif avg_like_rate >= 1.5:like_score = 3
        elif avg_like_rate >= 0.5:like_score = 2
        else:                     like_score = 1

        # 3) 댓글율 (comments / views) — 15%
        if avg_cmt_rate >= 0.3:    cmt_score = 5
        elif avg_cmt_rate >= 0.1:  cmt_score = 4
        elif avg_cmt_rate >= 0.05: cmt_score = 3
        elif avg_cmt_rate >= 0.01: cmt_score = 2
        else:                      cmt_score = 1

        # 4) 채널 생산성 (총 업로드 수) — 10%
        vcnt = ch.get('video_count', 0)
        if vcnt >= 500:   prod_score = 5
        elif vcnt >= 200: prod_score = 4
        elif vcnt >= 50:  prod_score = 3
        elif vcnt >= 10:  prod_score = 2
        else:             prod_score = 1

        total = (ratio_score * 0.40 + like_score * 0.35
                 + cmt_score * 0.15 + prod_score * 0.10)
        score = round(total, 1)

        if total >= 4.0:   return 'S', '🏆 S', score
        elif total >= 3.0: return 'A', '🥇 A', score
        elif total >= 2.0: return 'B', '🥈 B', score
        elif total >= 1.5: return 'C', '🥉 C', score
        else:              return 'D', '💤 D', score

    def _resolve_channel_id(self, url):
        """채널 URL / 핸들 / ID → channel_id 반환."""
        url = url.strip()
        # /channel/UC... 직접 ID
        m = re.search(r'/channel/(UC[\w-]+)', url)
        if m:
            return m.group(1)
        # /@handle
        m = re.search(r'/@([\w.-]+)', url)
        if m:
            resp = self.youtube.channels().list(part='id', forHandle=m.group(1)).execute()
            if resp.get('items'):
                return resp['items'][0]['id']
        # /c/name 또는 /user/name
        m = re.search(r'/(?:c|user)/([\w.-]+)', url)
        if m:
            resp = self.youtube.search().list(part='snippet', q=m.group(1),
                                              type='channel', maxResults=1).execute()
            if resp.get('items'):
                return resp['items'][0]['snippet']['channelId']
        return None

    def analyze_channel_shorts(self, channel_url):
        """
        채널의 최근 4주 쇼츠 주별 평균 조회수 분석.
        반환: {
            'channel_name': str,
            'weeks': [{'label','count','avg_views'}, ...],  # 인덱스 0=최신, 3=4주전
            'monthly_avg': int,
            'total_shorts': int,
        }
        """
        channel_id = self._resolve_channel_id(channel_url)
        if not channel_id:
            return None

        # 채널 이름
        ch_resp = self.youtube.channels().list(part='snippet', id=channel_id).execute()
        if not ch_resp.get('items'):
            return None
        channel_name = ch_resp['items'][0]['snippet']['title']

        # 최근 28일 쇼츠 검색 (videoDuration=short → 4분 이하)
        after = (datetime.utcnow() - timedelta(days=28)).strftime('%Y-%m-%dT%H:%M:%SZ')
        s_resp = self.youtube.search().list(
            part='id,snippet', channelId=channel_id,
            type='video', videoDuration='short',
            publishedAfter=after, maxResults=50, order='date'
        ).execute()
        items = s_resp.get('items', [])
        if not items:
            return {'channel_name': channel_name, 'weeks': [], 'monthly_avg': 0, 'total_shorts': 0}

        vid_ids = [i['id']['videoId'] for i in items]
        pub_map = {i['id']['videoId']: i['snippet']['publishedAt'] for i in items}

        # 통계 + 영상 길이 조회
        v_resp = self.youtube.videos().list(
            part='statistics,contentDetails', id=','.join(vid_ids)
        ).execute()

        now = datetime.utcnow()
        # 버킷: (views, likes, comments) 튜플 리스트
        buckets = [[] for _ in range(4)]  # 0=1주차(최신) … 3=4주전

        for item in v_resp.get('items', []):
            vid_id = item['id']
            dur    = self.parse_duration(item['contentDetails']['duration'])
            if dur > 180:   # 3분 초과 → 쇼츠 아님
                continue
            st_   = item.get('statistics', {})
            views = int(st_.get('viewCount',   0))
            likes = int(st_.get('likeCount',   0))
            cmts  = int(st_.get('commentCount', 0))
            pub   = pub_map.get(vid_id, '')
            try:
                pub_dt   = datetime.fromisoformat(pub.replace('Z', '+00:00')).replace(tzinfo=None)
                days_ago = (now - pub_dt).days
            except Exception:
                continue
            week_idx = min(days_ago // 7, 3)
            buckets[week_idx].append((views, likes, cmts))

        labels    = ['1주 (최신)', '2주전', '3주전', '4주전']
        weeks     = []
        all_views = []
        for label, bucket in zip(labels, buckets):
            if bucket:
                tv = sum(b[0] for b in bucket)
                tl = sum(b[1] for b in bucket)
                tc = sum(b[2] for b in bucket)
                avg_v = round(tv / len(bucket))
            else:
                tv = tl = tc = avg_v = 0
            weeks.append({
                'label':        label,
                'count':        len(bucket),
                'total_views':  tv,
                'total_likes':  tl,
                'total_comments': tc,
                'avg_views':    avg_v,
            })
            all_views.extend(b[0] for b in bucket)

        total_all   = sum(all_views)
        monthly_avg = round(total_all / len(all_views)) if all_views else 0
        return {
            'channel_name':  channel_name,
            'weeks':         weeks,
            'monthly_avg':   monthly_avg,
            'monthly_total': total_all,
            'total_shorts':  len(all_views),
        }

    def get_channel_analysis(self, videos):
        channel_ids = list({v['channel_id'] for v in videos})
        if not channel_ids:
            return {}
        channels = {}
        # channels.list도 한 번에 최대 50개 — 청크 처리
        for i in range(0, len(channel_ids), 50):
            chunk = channel_ids[i:i+50]
            resp = self.youtube.channels().list(
                part='snippet,statistics', id=','.join(chunk)
            ).execute()
            for item in resp.get('items', []):
                stats = item.get('statistics', {})
                sub = int(stats.get('subscriberCount', 0))
                vcnt = int(stats.get('videoCount', 1))
                total_views = int(stats.get('viewCount', 0))
                channels[item['id']] = {
                    'channel_id': item['id'],
                    'title': item['snippet']['title'],
                    'subscriber_count': sub,
                    'video_count': vcnt,
                    'total_view_count': total_views,
                    'avg_views_per_video': round(total_views / vcnt) if vcnt else 0,
                    'thumbnail': item['snippet']['thumbnails'].get('default', {}).get('url', ''),
                    'channel_url': f"https://www.youtube.com/channel/{item['id']}",
                }
        return channels
