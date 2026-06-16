import re

# 완전히 제거할 기능어 (동사 활용형, 부사, 지시어 등)
REMOVE_WORDS = {
    # 동사/형용사 활용형
    '없이', '없다', '없고', '없어', '없는',
    '있이', '있다', '있고', '있어', '있는',
    '해야', '하면', '하기', '하는', '한다', '하고', '해서', '하지', '했던',
    '살아야', '살기', '사는', '살면', '살고', '살아',
    '되어야', '되기', '되는', '되면', '되고', '되어',
    '이어야', '이기', '이는', '이면', '이고',
    '알아야', '알기', '아는', '알면',
    '해줘', '해줘야', '해줘서',
    # 부사
    '정말', '진짜', '너무', '매우', '아주', '참', '꼭', '반드시', '계속',
    '왜', '어떻게', '언제', '어디서', '얼마나', '얼마',
    '많이', '조금', '약간', '잠깐', '잠시', '자주', '항상', '절대', '전혀',
    '알고', '알아', '알아야', '알면', '알기',
    # 지시/의문어
    '이런', '저런', '그런', '어떤', '무슨', '모든', '각종', '여러',
    # 접속어
    '그리고', '하지만', '그러나', '그래서', '따라서', '또한', '그냥',
    # 관형어
    '나의', '나는', '내가', '우리', '우리의',
    # 형용사 활용형
    '싶은', '싶어', '싶다', '싶으면', '싶고',
    '좋은', '나쁜', '힘든', '어려운', '쉬운',
    '안', '못', '잘', '더', '덜',
}

# 끝에서 제거할 조사·어미 (긴 것 먼저)
SUFFIXES = [
    '으로서', '에서의', '에게의', '으로부터', '에게서',
    '이라는', '이라고', '이라면', '이라서', '이라도',
    '라는', '라고', '라면', '라서',
    '에서', '에게', '부터', '까지', '처럼', '보다', '만큼',
    '하는', '하기', '해야', '해서', '하면', '하고',
    '없는', '있는', '없이', '없어', '있어',
    '으로', '에도', '에만', '에는',
    '은데', '는데', '이지', '이고', '이며', '이나', '이든',
    '아서', '어서',
    '은', '는', '이', '가', '을', '를', '의', '와', '과', '도', '만', '로',
]


def strip_suffix(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            candidate = word[:-len(suffix)]
            # 제거 후 너무 짧아지면 원본 유지
            if len(candidate) >= 2:
                return candidate
    return word


def extract_keywords(text):
    """
    문장에서 핵심 명사성 키워드 추출.
    "친구 없이 살아야 하는 이유" → ["친구", "이유"]
    "다이어트 하면 안 되는 이유" → ["다이어트", "이유"]
    """
    words = text.strip().split()
    if len(words) <= 2:
        return words  # 짧은 입력은 그대로

    result = []
    for word in words:
        if word in REMOVE_WORDS:
            continue
        cleaned = strip_suffix(word)
        if not cleaned or cleaned in REMOVE_WORDS:
            continue
        if len(cleaned) < 1:
            continue
        if cleaned not in result:
            result.append(cleaned)

    return result if result else words


def is_sentence(text):
    """3단어 이상 + 기능어/조사 포함이면 문장으로 판단"""
    words = text.strip().split()
    if len(words) < 3:
        return False
    has_function = any(
        w in REMOVE_WORDS or any(w.endswith(s) for s in SUFFIXES)
        for w in words
    )
    return has_function


def get_search_query(text):
    """
    반환: (YouTube 검색에 쓸 쿼리, 추출된 키워드 리스트, 문장 여부)
    """
    text = text.strip()
    if not is_sentence(text):
        return text, [text], False

    keywords = extract_keywords(text)
    query = ' '.join(keywords) if keywords else text
    return query, keywords, True
