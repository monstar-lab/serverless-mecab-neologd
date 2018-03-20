# MeCab NEologd for AWS Lambda

This is a sample project to build NEologd dictionary in Docker, deploy AWS Lambda with mecab by serverless framework

## Prerequisites
1. Create an AIM user with `AmazonS3FullAccess` privilage.
2. Create an S3 bucket called `serverless-mecab-neologd-dict`
3. Install Serverless Framework, setup properly
4. Setup Docker properly

## Build the dictionary and upload to s3
- Build docker image

```shell
docker build -t dictionary-s3push .
```

- Run image to push to s3 (pass aws credentials)
```shell
docker run -e AWS_DEFAULT_REGION=ap-northeast-1 \
    -e AWS_ACCESS_KEY_ID=<acces key id> \
    -e AWS_SECRET_ACCESS_KEY=<secret access key> \
    dictionary-s3push
```

## API endpoint with Lambda, APIGateway, Serverless framework

- Deploy
```shell
serverless deploy
```

#### Runtime
Python 2.7

#### Input event

* ``sentence``: 形態素解析対象の文字列
* ``stoptags``: 解析結果から除外したい品詞タグ（※ 複数設定する場合はカンマ区切りで指定可能）
* ``unk_feature``: 未知語を表示する。このフラグを ``true`` にすると未知語の品詞推定をやめ、未知語は常に "未知語" 品詞を出力します。default to ``false``

Input event sample:
```python
{
  "sentence": "今日は良い天気です",
  "stoptags": "助詞-係助詞"
}
```

#### Execution result

* ``reading``: 読み
* ``pos``: 品詞（品詞-品詞細分類1-品詞細分類2-品詞細分類3）
* ``baseform``: 原型
* ``surface``: 形態素の文字列情報
* ``feature``:  CSVで表記された素性情報
* ``stat``: 形態素の種類
  * 0: MECAB_NOR_NODE
  * 1: MECAB_UNK_NODE
  * 2: MECAB_BOS_NODE
  * 3: MECAB_EOS_NODE


## Example

- Call api with curl
```shell
curl -G --data-urlencode "sentence=彼女はペンパイナッポーアッポーペンと恋ダンスを踊った。" https://xxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/tokenize | jq
```

- Response
```json
[
  {
    "stat": 0,
    "baseform": "彼女",
    "feature": "名詞,代名詞,一般,*,*,*,彼女,カノジョ,カノジョ",
    "surface": "彼女",
    "pos": "名詞-代名詞-一般",
    "reading": "カノジョ"
  },
  {
    "stat": 0,
    "baseform": "は",
    "feature": "助詞,係助詞,*,*,*,*,は,ハ,ワ",
    "surface": "は",
    "pos": "助詞-係助詞",
    "reading": "ハ"
  },
  {
    "stat": 0,
    "baseform": "ペンパイナッポーアッポーペン",
    "feature": "名詞,固有名詞,一般,*,*,*,ペンパイナッポーアッポーペン,ペンパイナッポーアッポーペン,ペンパイナッポーアッポーペン",
    "surface": "ペンパイナッポーアッポーペン",
    "pos": "名詞-固有名詞-一般",
    "reading": "ペンパイナッポーアッポーペン"
  },
  {
    "stat": 0,
    "baseform": "と",
    "feature": "助詞,並立助詞,*,*,*,*,と,ト,ト",
    "surface": "と",
    "pos": "助詞-並立助詞",
    "reading": "ト"
  },
  {
    "stat": 0,
    "baseform": "恋ダンス",
    "feature": "名詞,固有名詞,一般,*,*,*,恋ダンス,コイダンス,コイダンス",
    "surface": "恋ダンス",
    "pos": "名詞-固有名詞-一般",
    "reading": "コイダンス"
  },
  {
    "stat": 0,
    "baseform": "を",
    "feature": "助詞,格助詞,一般,*,*,*,を,ヲ,ヲ",
    "surface": "を",
    "pos": "助詞-格助詞-一般",
    "reading": "ヲ"
  },
  {
    "stat": 0,
    "baseform": "踊",
    "feature": "名詞,一般,*,*,*,*,踊,オドリ,オドリ",
    "surface": "踊",
    "pos": "名詞-一般",
    "reading": "オドリ"
  },
  {
    "stat": 1,
    "baseform": "*",
    "feature": "名詞,一般,*,*,*,*,*",
    "surface": "った",
    "pos": "名詞-一般",
    "reading": "*"
  },
  {
    "stat": 0,
    "baseform": "。",
    "feature": "記号,句点,*,*,*,*,。,。,。",
    "surface": "。",
    "pos": "記号-句点",
    "reading": "。"
  }
]
```

## Appendix

MeCabはコードにネイティブバイナリを使用している為、以下のリンク先を参考にLambda実行環境と同じ環境でコンパイルしてください。(Amazon Linux)

※ 参考: [Lambda 実行環境と利用できるライブラリ](http://docs.aws.amazon.com/ja_jp/lambda/latest/dg/current-supported-versions.html)

## reference

https://github.com/KunihikoKido/aws-lambda-ja-tokenizer
https://speakerdeck.com/satorukadowaki/aws-apigateway-plus-python-lambda-plus-neologddezuo-rusabaresuri-ben-yu-xing-tai-su-jie-xi-api