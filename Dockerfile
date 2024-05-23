FROM python:3.12
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

CMD [ "uvicorn", "main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]