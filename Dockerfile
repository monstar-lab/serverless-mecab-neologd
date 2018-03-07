# Use an official Python runtime as a parent image
FROM python:3

# install system packages
RUN apt-get update && \
      apt-get -y install sudo

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

# install mecab
RUN mkdir /lambda_neologd
RUN curl -L \
  "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE" \
  -o mecab-0.996.tar.gz
RUN tar zxvf mecab-0.996.tar.gz && rm mecab-0.996.tar.gz
WORKDIR mecab-0.996
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
RUN python /app/seed_normalize.py
RUN ./bin/install-mecab-ipadic-neologd -y \
    -p /neologd --eliminate-redundant-entry
RUN ln -s /neologd /tmp/neologd
WORKDIR ..

# Install any needed packages specified in requirements.txt
WORKDIR /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app when the container launches
CMD ["mecab", "-d", "/tmp/neologd", "test-sentence.txt"]
