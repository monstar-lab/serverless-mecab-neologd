# coding: utf-8
import re
APPLY_IDS = [30, 36, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52,
             53, 54, 56, 57]
APPLY_JOIN_IDS = [10, 13, 18, 20, 24, 25, 31, 32, 33, 51, 58]
NOT_ENDOFWORDS = [
    [13, "から"],
    [18, "が"],
    [18, "ものの"],
    [18, "と"],
    [24, "の"],
]
EX_APPLY_IDS = [
    [18, "て"], [18, "で"], [25, "た"], [25, "ず"], [25, "ない"],
    [25, "ます"], [25, "ん"], [25, "まし"], [25, "ませ"], [31, "い"], [54, "そう"]
]
IGNORE_WORDS =[u"そう", u"した", u"あと",  u"何度も",  u"何か"]

def wordFilter(token, buf):
    if len(buf) != 0:
        if token.posid == 4 \
            and re.search(r'[ー・]', token.surface) \
            and re.search(r'^[ぁ-んァ-タダ-ヶー・]+$', buf[-1].surface) \
            and buf[-1].posid != 30:
                return True

        for pid, w in EX_APPLY_IDS:
            if pid == token.posid and w == token.surface:
                return True
    if token.posid in APPLY_IDS:
        # アルファベットの羅列が名詞と判断されるのを防ぐ
        # (ID: 45で固有名詞,組織とID:38で一般名詞の2パターンがある)
        if len(token.surface) < 3 and re.search(r'[a-zA-Z:]+', token.surface):
            return False
        if len(buf) == 0 and token.surface in IGNORE_WORDS:
            return False
    return False
