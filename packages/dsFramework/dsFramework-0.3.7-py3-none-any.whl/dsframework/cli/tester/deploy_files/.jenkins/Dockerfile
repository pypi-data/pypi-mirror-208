FROM xoominfoaws.pe.jfrog.io/zi-docker-virtual/python:latest
WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "./app.py"]