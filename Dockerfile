FROM python:3.13.1-slim

EXPOSE 5678 8000

RUN apt-get update && apt-get install -y \
    redis-server \
    netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

COPY ./init.sh ./init.sh
RUN chmod +x init.sh
CMD ["./init.sh"]
