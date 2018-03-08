# coding: utf-8
import re

CLEANSING_PATTERNS = [
    [r'\r\n|\r|\n|\\n', '。'], # 改行コードを除去
    [r'\t+|\s+', ' '], # 連続するタブまたは連続するスペース
    [u'\u30FC+', u'\u30FC'], # 連続するハイフンを1つのハイフンにする
    [r'([^\w])\s([^\w])', r'\1。\2'], # 2バイト文字間のスペースは句点で置換
    [u'・・+', '・'], # 連続する中点を1つに
    [u'。。+', '。'], # 連続する句点を1つに
]

def cleansingText(text):
    for src, dst in CLEANSING_PATTERNS:
        res = re.sub(src, dst, text)

    return res
