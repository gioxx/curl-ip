# 🌐 IP Check Service

This file is [also available in italian](README-IT.md).

A minimal web service that returns the client's public IP address. It replicates the behavior of [`https://checkip.amazonaws.com`](https://checkip.amazonaws.com), but is self-hosted and containerized.

## 🚀 Features

- Returns the client's IP (or `X-Forwarded-For` header if present)
- Plain text response
- Lightweight Docker container
- Ready for deployment with Docker Compose
- Ideal as a public or internal microservice

---

## 📦 Usage via Docker

### Quick Start:

```bash
docker run -d -p 80:8080 gfsolone/ip:latest
```

Then visit: `http://localhost`  
Or run: `curl http://localhost`

---

## 🧱 Usage via Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  ip:
    container_name: ip
    image: gfsolone/ip:latest
    ports:
      - "80:8080"
    restart: unless-stopped
```

Then run:

```bash
docker compose up -d
```

---

## 📦 Usage via GitHub Container Registry (GHCR)

Alternatively to Docker Hub, you can use the package image directly from GitHub Container Registry (GHCR). To run the service, use the following command:

```bash
docker run -d -p 80:8080 ghcr.io/gioxx/ip:latest
```

Then visit: `http://localhost`  
Or run: `curl http://localhost`

---

## 🔍 Example Response

```bash
$ curl http://localhost
203.0.113.42
```

---

## 🛠️ Technical Requirements

- The app is developed in Python with [Flask](https://flask.palletsprojects.com/)
- It exposes the IP using `request.remote_addr` or `X-Forwarded-For`
- Listens on port `8080` at `0.0.0.0` for compatibility with Docker

---

## 🗂️ Project Structure

```
.
├── app.py
├── Dockerfile
└── docker-compose.yml
```

---

## 📄 License

MIT License — do whatever you want, but keep the credits 😉
