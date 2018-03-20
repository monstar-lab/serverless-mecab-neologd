# Use an official Python runtime as a parent image
FROM python:3
#FROM lambci/lambda:build-python3.6

# install system packages
RUN apt-get update && \
      apt-get -y install sudo zip libstdc++6
#RUN yum update && yum install sudo -y

# install aws cli to push dictionary to s3
# use "-e VARNAME=varvalue" to substitute actual values on "docker run" cmd
ENV AWS_DEFAULT_REGION='[your region]'
ENV AWS_ACCESS_KEY_ID='[your access key id]'
ENV AWS_SECRET_ACCESS_KEY='[your secret]'
RUN pip3 install awscli

# Copy the current directory contents into the container at /app
ADD . /app

# Set the working directory
WORKDIR /tmp

# Install miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda3 -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda3/bin:${PATH}
RUN conda update -y conda
RUN conda install -c dan_blanchard perl-autodie

# install mecab
RUN mkdir /lambda_neologd
RUN curl -L \
  "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE" \
  -o mecab-0.996.tar.gz
RUN tar zxvf mecab-0.996.tar.gz && rm mecab-0.996.tar.gz
WORKDIR mecab-0.996
ENV CXXFLAGS="$CXXFLAGS -L/usr/lib/x86_64-linux-gnu/libstdc++.so.6 -libstdc++"
RUN ./configure --prefix=/lambda_neologd/local --enable-utf8-only
RUN make && make install
WORKDIR ..
RUN rm -rf mecab-0.996

# install mecab-ipadic
RUN curl -L \
  "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM" \
  -o mecab-ipadic-2.7.0-20070801.tar.gz
RUN tar xvzf mecab-ipadic-2.7.0-20070801.tar.gz && \
    rm mecab-ipadic-2.7.0-20070801.tar.gz
WORKDIR mecab-ipadic-2.7.0-20070801
ENV PATH=/lambda_neologd/local/bin:${PATH}
ENV LD_LIBRARY_PATH=/lambda_neologd/local/lib:${LD_LIBRARY_PATH}
RUN ./configure --with-mecab-config=/lambda_neologd/local/bin/mecab-config --prefix=/lambda_neologd/local \
  --enable-utf8-only --with-charset=utf8
RUN make && make install
WORKDIR ..
RUN rm -rf mecab-ipadic-2.7.0-20070801

#install neologd dictionary
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd
WORKDIR mecab-ipadic-neologd
RUN ./bin/install-mecab-ipadic-neologd -y \
    -p /neologd -n --eliminate-redundant-entry
RUN python3 /app/seed_normalize.py
RUN ./bin/install-mecab-ipadic-neologd -y \
    -p /neologd --eliminate-redundant-entry
RUN ln -s /neologd /tmp/neologd
WORKDIR ..

# Install any needed packages specified in requirements.txt
WORKDIR /app

# upload mecab and neologd dictionary to s3
CMD ["aws", "s3", "cp", "/neologd", \
     "s3://serverless-mecab-neologd-dict/neologd", \
     "--recursive"]
