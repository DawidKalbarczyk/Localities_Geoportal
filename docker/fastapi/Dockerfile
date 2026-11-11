FROM python:3.12.3-slim

WORKDIR /code
COPY docker/fastapi/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY backend/fastapi /code/app

CMD ["fastapi", "run", "app/main.py", "--proxy-headers","--port", "8000"]