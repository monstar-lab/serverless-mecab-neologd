# coding: utf-8
import os
import logging
import traceback
import unicodedata
import json
import boto3
import ctypes

import normalize
import termextract

libdir = os.path.join(os.getcwd(), 'local', 'lib')
libmecab = ctypes.cdll.LoadLibrary(os.path.join(libdir,'libmecab.so'))

# Configuration: AWS
AWS_S3_BUCKET = 'mecabdic'
BOTOCONF = {
    'aws_access_key_id': 'AKI.....',
    'aws_secret_access_key': 'pTWl.....',
    'region_name': 'ap-northeast-1'
}
boto3.setup_default_session(**BOTOCONF)
session = boto3._get_default_session()
session_region = session._session.get_config_variable('region')
s3 = boto3.client('s3')

MECAB_DIC_FILES = [ # mecab辞書のリスト
    'char.bin', 'dicrc', 'left-id.def','matrix.bin','pos-id.def',
    'rewrite.def', 'right-id.def', 'sys.dic', 'unk.dic',
]
DICDIR = '/tmp/neologd/' # 辞書の保存先

# S3から辞書をダウンロード
def prepareMecabDic():
    if not os.path.exists(DICDIR):
        os.mkdir(DICDIR)
    for mdic in MECAB_DIC_FILES:
        dest_dic = DICDIR + mdic
        if not os.path.exists(dest_dic) or os.path.getsize(dest_dic) == 0:
            with open(dest_dic, 'wb') as f:
                s3.download_file(AWS_S3_BUCKET, mdic, dest_dic)

prepareMecabDic()

import MeCab

# init MeCab
MECABRC = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')
tagger = MeCab.Tagger("-r %s" % MECABRC)

import normalize # サニタイズモジュール
import termextract # 合名詞生成，フレーズ抽出モジュール

def lambda_handler(event, context):
    text = event['queryStringParameters'].get('text', '')
    is_termext = event['queryStringParameters'].get('termextract', '')
    is_phrase = event['queryStringParameters'].get('phrase', '')

    if text:
        text = unicodedata.normalize('NFKC', text.strip()).lower()
        text = normalize.cleansingText(text)
        node = tagger.parse('')
        node = tagger.parseToNode(text)
        node = tagger.parse('')
        node = tagger.parseToNode(text)
        tokens = []
        if is_termext: # 合名詞生成
            tokens = termextract.tokenize(node)
        elif is_phrase: # フレーズ抽出
            tokens = termextract.phrases(node)
        else:
            while node:
                token = {
                    'surface': node.surface,
                    'posid': node.posid,
                    'feature': node.feature,
                 }
                 tokens.append(token)
                 node = node.next
