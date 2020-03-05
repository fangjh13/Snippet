FROM python:3.8.2

LABEL REFRESH_AT=2020-03-05

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# config SCKEY environment
ENV SCKEY=FILL_YOUR_SCKEY

RUN pip install aiohttp==3.6.2 lxml==4.5.0 -i https://mirrors.aliyun.com/pypi/simple

ADD price.py .

CMD [ "python", "price.py" ]
