# serverless-mecab-neologd

## Build the dictionary and upload to s3
Build docker image
```shell
docker build -t dictionary-s3push .
```

Run image to push to s3 (pass aws credentials)
```shell
docker run -e AWS_DEFAULT_REGION=ap-northeast-1 \
    -e AWS_ACCESS_KEY_ID=<acces key id> \
    -e AWS_SECRET_ACCESS_KEY=<secret access key> \
    dictionary-s3push
```shell
