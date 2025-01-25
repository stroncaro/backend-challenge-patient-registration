FROM python:3.13.1-slim

EXPOSE 5678 8000

WORKDIR /code

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]
