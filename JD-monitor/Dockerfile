FROM python:3.8.2

LABEL REFRESH_AT=2020-03-04

ENV SCKEY=FILL_YOUR_SCKEY

RUN pip install aiohttp==3.6.2 lxml==4.5.0 -i https://mirrors.aliyun.com/pypi/simple

ADD price.py .

CMD [ "python", "price.py" ]
