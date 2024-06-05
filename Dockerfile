FROM python:3.12
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

CMD [ "fastapi", "run", "main.py", "--port", "5000"]