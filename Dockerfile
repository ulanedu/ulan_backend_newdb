FROM python:3.8
WORKDIR /app
ADD requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple