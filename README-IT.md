# 🌐 IP Check Service

Questo file è [disponibile anche in inglese](README.md).

Un servizio web minimale che restituisce l'indirizzo IP pubblico del client HTTP. Replica il comportamento di [`https://checkip.amazonaws.com`](https://checkip.amazonaws.com), ma è self-hosted e containerizzato.

## 🚀 Funzionalità

- Restituisce l'IP del client (o header `X-Forwarded-For` se presente)
- Risposta in plain text
- Contenitore Docker leggero
- Pronto per il deploy con Docker Compose
- Ideale come microservizio pubblico o interno

---

## 📦 Utilizzo via Docker

### Esecuzione rapida:

```bash
docker run -d -p 80:8080 gfsolone/ip:latest
```

Visita poi: `http://localhost`  
Oppure esegui: `curl http://localhost`

---

## 🧱 Utilizzo via Docker Compose

Crea un file `docker-compose.yml`:

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

Poi esegui:

```bash
docker compose up -d
```

---

## 📦 Utilizzo via GitHub Container Registry (GHCR)

In alternativa a Docker Hub, puoi utilizzare l'immagine del pacchetto direttamente dal GitHub Container Registry (GHCR). Per eseguire il servizio, utilizza il seguente comando:

```bash
docker run -d -p 80:8080 ghcr.io/gioxx/ip:latest
```

Visita poi: `http://localhost`  
Oppure esegui: `curl http://localhost`

---

## 🔍 Esempio di risposta

```bash
$ curl http://localhost
203.0.113.42
```

---

## 🛠️ Requisiti tecnici

- L'app è sviluppata in Python con [Flask](https://flask.palletsprojects.com/)
- Espone l'indirizzo IP usando `request.remote_addr` o `X-Forwarded-For`
- Ascolta sulla porta `8080` all'indirizzo `0.0.0.0` per la compatibilità con Docker

---

## 🗂️ Struttura del progetto

```
.
├── app.py
├── Dockerfile
└── docker-compose.yml
```

---

## 📄 Licenza

MIT License — fai ciò che vuoi, ma lascia i crediti 😉
