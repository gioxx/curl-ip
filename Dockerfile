FROM python:3.13-slim
WORKDIR /app
RUN pip install flask markupsafe
COPY app.py .
EXPOSE 8080
ENV ENABLE_DEBUG=false
ENV DEBUG_TOKEN=your_super_secret_token_here
CMD ["python", "app.py"]