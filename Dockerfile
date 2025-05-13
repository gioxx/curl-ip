FROM python:3.13-slim

WORKDIR /app

RUN pip install flask markupsafe

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
