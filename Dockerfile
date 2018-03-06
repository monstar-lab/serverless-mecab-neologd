# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

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
RUN tar zxvf mecab-0.996.tar.gz
WORKDIR mecab-0.996
RUN ./configure --prefix=/lambda_neologd/local --enable-utf8-only
RUN make && make install

# install mecab-ipadic
RUN curl -L \
  "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM" \
  -o mecab-ipadic-2.7.0-20070801.tar.gz
RUN tar xvzf mecab-ipadic-2.7.0-20070801.tar.gz
WORKDIR mecab-ipadic-2.7.0-20070801
ENV PATH=/lambda_neologd/local/bin:${PATH}
ENV LD_LIBRARY_PATH=/lambda_neologd/local/lib:${LD_LIBRARY_PATH}
RUN ./configure --with-mecab-config=/lambda_neologd/local/bin/mecab-config --prefix=/lambda_neologd/local \
  --enable-utf8-only --with-charset=utf8
RUN make && make install

# Install any needed packages specified in requirements.txt
WORKDIR /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app when the container launches
CMD ["mecab", "test-sentence.txt"]
