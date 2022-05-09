FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apk add --no-cache \
        gcc \
        openssl-dev \
        python3-dev \
        musl-dev \
        libressl-dev \
        libffi-dev \
        mariadb-dev

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

COPY entrypoint.prod.sh /code/
ENTRYPOINT ["sh", "entrypoint.prod.sh"]
