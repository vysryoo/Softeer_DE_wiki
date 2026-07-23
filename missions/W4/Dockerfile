FROM ubuntu:22.04

# 프롬프트 입력 방지
ENV DEBIAN_FRONTEND=noninteractive

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3 \
    python3-pip \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
RUN ln -s /usr/lib/jvm/java-11-openjdk-$(dpkg --print-architecture) /usr/lib/jvm/java-11-openjdk
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk
ENV SPARK_VERSION=3.4.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH

# Apache Spark 다운로드 및 압축 해제
RUN wget -qO- "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | tar -xz -C /opt/ \
    && mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# 분석/테스트에 필요한 Python 패키지 설치
RUN pip3 install --no-cache-dir pyspark==3.4.1 pandas numpy scipy pyarrow pytest

# 작업 디렉토리 설정
WORKDIR ${SPARK_HOME}
