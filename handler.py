# coding=utf-8
import json
import os
import settings
import sys

# preload libmecab
import ctypes
libdir = os.path.join(os.getcwd(), 'local', 'lib')
libmecab = ctypes.cdll.LoadLibrary(os.path.join(libdir, 'libmecab.so'))
# #libmecab = ctypes.cdll.LoadLibrary(os.path.join(libdir, 'libmecab.dylib'))

# Configuration: AWS
import boto3
AWS_S3_BUCKET = 'serverless-mecab-neologd-dict'
AWS_S3_DICTIONARY_DIR = 'neologd'
AWS_S3_MECAB_DIR = 'mecab'
# BOTOCONF = {
#     'aws_access_key_id': os.environ['SERVERLESS_AWS_ACCESS_KEY_ID'],
#     'aws_secret_access_key': os.environ['SERVERLESS_AWS_SECRET_ACCESS_KEY'],
#     'region_name': os.environ['SERVERLESS_AWS_REGION_NAME']
# }
BOTOCONF = {}
boto3.setup_default_session(**BOTOCONF)
session = boto3._get_default_session()
session_region = session._session.get_config_variable('region')
s3 = boto3.client('s3')

MECAB_DIC_FILES = [ # mecab辞書のリスト
    'char.bin', 'dicrc', 'left-id.def','matrix.bin','pos-id.def',
    'rewrite.def', 'right-id.def', 'sys.dic', 'unk.dic'
]
DICDIR = '/tmp/neologd/' # 辞書の保存先

# download dictionary from S3
def prepareMecabDic():
    if not os.path.exists(DICDIR):
        os.mkdir(DICDIR)
    for mdic in MECAB_DIC_FILES:
        dest_dic = DICDIR + mdic
        if not os.path.exists(dest_dic) or os.path.getsize(dest_dic) == 0:
            with open(dest_dic, 'wb') as f:
                s3.download_file(AWS_S3_BUCKET,
                        AWS_S3_DICTIONARY_DIR + '/' + mdic, dest_dic)

prepareMecabDic()

libdir = os.path.join(os.getcwd(), 'lib')
sys.path.append(libdir)
import MeCab

# prepare Tagger
#dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
dicdir = DICDIR
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')
default_tagger = MeCab.Tagger("-d{} -r{}".format(dicdir, rcfile))
unk_tagger = MeCab.Tagger("-d{} -r{} --unk-feature 未知語,*,*,*,*,*,*,*,*".format(dicdir, rcfile))

DEFAULT_STOPTAGS = ['BOS/EOS']

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def tokenize(event, context):
    queryParams = event.get('queryStringParameters', {})
    sentence = queryParams.get('sentence', '').encode('utf-8')
    stoptags = queryParams.get('stoptags', '').encode('utf-8').split(',') + DEFAULT_STOPTAGS
    unk_feature = queryParams.get('unk_feature', False)

    tokens = []
    tagger = unk_tagger if unk_feature else default_tagger
    node = tagger.parseToNode(sentence)
    while node:
        feature = node.feature + ',*,*'
        part_of_speech = get_part_of_speech(feature)
        reading = get_reading(feature)
        base_form = get_base_form(feature)
        token = {
            "surface": node.surface.decode('utf-8'),
            "feature": node.feature.decode('utf-8'),
            "pos": part_of_speech.decode('utf-8'),
            "reading": reading.decode('utf-8'),
            "baseform": base_form.decode('utf-8'),
            "stat": node.stat,
        }
        if part_of_speech not in stoptags:
            tokens.append(token)
        node = node.next

    #return {"tokens": tokens}
    response = {
        "statusCode": 200,
        "body": json.dumps(tokens)
    }
    return response

def get_part_of_speech(feature):
    return '-'.join([v for v in feature.split(',')[:4] if v != '*'])

def get_reading(feature):
    return feature.split(',')[7]

def get_base_form(feature):
    return feature.split(',')[6]
