FROM python:3.13-slim

WORKDIR /app
COPY app.py .

RUN pip install flask

EXPOSE 8080

CMD ["python", "app.py"]
