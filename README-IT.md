# 🌐 IP Check Service

Questo file è disponibile anche in [inglese](README.md).

Un servizio web minimale che restituisce l’indirizzo IP pubblico del client. Replica il comportamento di [`https://checkip.amazonaws.com`](https://checkip.amazonaws.com), ma è self-hosted e containerizzato.

## 🚀 Funzionalità

- Risposta in testo semplice (plain-text)
- Risoluzione IP con precedenza robusta:
  1. `CF-Connecting-IP` (Cloudflare)
  2. `X-Real-IP` (reverse proxy)
  3. primo valore in `X-Forwarded-For`
  4. `request.remote_addr`
- Favicon servita via redirect permanente verso una `.ico` su GitHub (o disattivabile)
- Endpoint `/debug` opzionale (Basic Auth + abilitazione via env)
- Immagine Docker leggera; pronta per Compose / Swarm
- Compatibile con reverse proxy (opzionale `ProxyFix`)

---

## 📦 Avvio rapido (Docker)

```bash
docker run -d -p 80:8080 gfsolone/ip:latest
# oppure via GHCR:
# docker run -d -p 80:8080 ghcr.io/gioxx/ip:latest
```

Poi visita: `http://localhost`  
Oppure: `curl http://localhost`

> Suggerimento: preferisci un tag fisso (es. `:1.0.0`) o un digest al posto di `:latest` per deploy riproducibili.

---

## 🧱 Docker Compose

### Ultra-minimale
Trovi qui il file già pronto: [`docker-compose.yml`](example/docker-compose.yml)

```yaml
version: "3.8"
services:
  ip:
    image: gfsolone/ip:latest
    ports:
      - "80:8080"
    restart: unless-stopped
```

### Minimale con variabili d’ambiente (consigliato)
Trovi qui il file già pronto: [`docker-compose-env.yml`](example/docker-compose-env.yml), tu dovrai solo ricordarti di creare il file .env (o usare l'env di Portainer o qualsiasi altro prodotto tu stai utilizzando), e infine rinominare questo file in `docker-compose.yml`

```yaml
version: "3.8"
services:
  ip:
    image: gfsolone/ip:latest
    ports:
      - "80:8080"
    env_file:
      - .env
    restart: unless-stopped
```

`.env` di esempio:

```env
ENABLE_DEBUG=false
DEBUG_TOKEN=cambia_questa_password
```

> Usi GHCR al posto di Docker Hub? Sostituisci l’immagine con `ghcr.io/gioxx/ip:latest` (o un tag fisso).

---

## 🔧 Configurazione

Variabili d’ambiente:

- `ENABLE_DEBUG` (`true`/`false`)  
  Abilita l’endpoint `/debug` **solo** quando impostata a `true`.
- `DEBUG_TOKEN`  
  Password per la Basic Auth di `/debug` (lo username è sempre `debug`).  
  **Non inserire segreti nell’immagine** — passali come environment o secrets.

Reverse proxy:

- Se sei dietro Nginx/Traefik, valuta l’abilitazione di `ProxyFix` (vedi commenti in `app.py`) per far riflettere correttamente IP/host impostati dal proxy.

Favicon:

- L’app reindirizza `/favicon.ico` a una `.ico` ospitata su GitHub e la “annuncia” con un header `Link` dalla `/`.  
  Preferisci un URL “pinnato” a un commit per garantire immutabilità, ad es.:  
  `https://raw.githubusercontent.com/gioxx/curl-ip/<commit_sha>/favicon.ico`  
  Se vuoi **disabilitarla**, sostituisci la route con una risposta `204 No Content` con cache lunga.

---

## 🔍 Endpoint

- `GET /`  
  Restituisce l’IP del client come `text/plain; charset=utf-8`. Aggiunge `Link: </favicon.ico>; rel="icon"`.

- `GET|HEAD /favicon.ico`  
  `308 Permanent Redirect` verso l’icona su GitHub. Cache lunga (`Cache-Control: public, max-age=31536000, immutable`).

- `GET /debug`  
  Restituisce alcune informazioni sugli header **solo se**:
  - `ENABLE_DEBUG=true`, **e**
  - la Basic Auth è valida (`username: debug`, `password: $DEBUG_TOKEN`).

---

## 🔍 Esempio

```bash
$ curl http://localhost
203.0.113.42
```

---

## 🌐 Demo pubblica

È disponibile un endpoint demo: https://ip.gioxx.org

> **Nota:** è ospitato su un Raspberry Pi a casa (best effort).  
> Potrebbe non essere sempre raggiungibile—meglio non usarlo in produzione.  
> L’endpoint si comporta come questo servizio: restituisce l’IP del client in testo semplice.

---

## 🗂️ Struttura del progetto

```
.
├── app.py
├── Dockerfile
└── example/docker-compose.yml
```

---

## 📄 Licenza

Licenza MIT — fai ciò che vuoi, ma mantieni i crediti 😉

## 📬 Feedback e contributi

Feedback, suggerimenti e richieste di pull sono benvenuti!
Sentitevi liberi di [segnalare un problema](https://github.com/gioxx/curl-ip/issues) o di contribuire direttamente.