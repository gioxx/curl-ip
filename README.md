# 🌐 IP Check Service

This file is also available in [Italian](README-IT.md).

A minimal web service that returns the client's public IP address. It replicates the behavior of [`https://checkip.amazonaws.com`](https://checkip.amazonaws.com), but is self-hosted and containerized.

## 🚀 Features

- Plain-text IP response
- Robust client IP resolution with precedence:
  1. `CF-Connecting-IP` (Cloudflare)
  2. `X-Real-IP` (reverse proxy)
  3. first value in `X-Forwarded-For`
  4. `request.remote_addr`
- Favicon served via permanent redirect to a GitHub-hosted `.ico` (or disable it if you prefer)
- Optional `/debug` endpoint (Basic Auth + env-gated)
- Lightweight Docker image; ready for Compose / Swarm
- Works behind reverse proxies (optional `ProxyFix`)

---

## 📦 Quick Start (Docker)

```bash
docker run -d -p 80:8080 gfsolone/ip:latest
# or using GHCR:
# docker run -d -p 80:8080 ghcr.io/gioxx/ip:latest
```

Then visit: `http://localhost`  
Or run: `curl http://localhost`

> Tip: prefer a fixed tag (e.g., `:1.0.0`) or a digest over `:latest` for reproducible deployments.

---

## 🧱 Docker Compose

### Ultra-minimal
Find the ready-made file here: [`docker-compose.yml`](example/docker-compose.yml)

```yaml
version: "3.8"
services:
  ip:
    image: gfsolone/ip:latest
    ports:
      - "80:8080"
    restart: unless-stopped
```

### Minimal with env (recommended)
You can find the ready-made file here: [`docker-compose-env.yml`](example/docker-compose-env.yml), you just have to remember to create the .env file (or use Portainer's env or whatever other product you are using), and finally rename this file to `docker-compose.yml`

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

`.env` example:

```env
ENABLE_DEBUG=false
DEBUG_TOKEN=change_me
```

> Using GHCR instead of Docker Hub? Replace the image with `ghcr.io/gioxx/ip:latest` (or a pinned tag).

---

## 🔧 Configuration

Environment variables:

- `ENABLE_DEBUG` (`true`/`false`)  
  Enables the `/debug` endpoint **only** when set to `true`.
- `DEBUG_TOKEN`  
  Basic Auth password for `/debug` (username is always `debug`).  
  **Do not bake secrets into images** — pass via environment or secrets.

Reverse proxy:

- If you run behind Nginx/Traefik, consider enabling Werkzeug’s `ProxyFix` (see comments in `app.py`) so `remote_addr` and host/port are set correctly by proxy headers.

Favicon:

- The app redirects `/favicon.ico` to a GitHub-hosted `.ico` and advertises it via a `Link` header from `/`.  
  Prefer pinning to a commit SHA for immutability, e.g.:  
  `https://raw.githubusercontent.com/gioxx/curl-ip/<commit_sha>/favicon.ico`  
  If you want to **disable** the favicon entirely, replace the route with a `204 No Content` and long cache.

---

## 🔍 Endpoints

- `GET /`  
  Returns the client IP as `text/plain; charset=utf-8`. Adds `Link: </favicon.ico>; rel="icon"`.

- `GET|HEAD /favicon.ico`  
  `308 Permanent Redirect` to the GitHub-hosted icon. Long cache (`Cache-Control: public, max-age=31536000, immutable`).

- `GET /debug`  
  Returns selected request headers and resolver info **only if**:
  - `ENABLE_DEBUG=true`, **and**
  - Basic Auth is valid (`username: debug`, `password: $DEBUG_TOKEN`).

---

## 🔍 Example

```bash
$ curl http://localhost
203.0.113.42
```

---

## 🌐 Public demo

A public demo endpoint is available at: https://ip.gioxx.org/

> **Heads-up:** this is hosted on a Raspberry Pi at home (best-effort availability).  
> It may be temporarily unreachable—please don’t rely on it for production.  
> The endpoint behaves like this service: it returns the client’s IP as plain text.

---

## 🗂️ Project Structure

```
.
├── app.py
├── Dockerfile
└── example/docker-compose.yml
```

---

## 📄 License

MIT License — do whatever you want, but keep the credits 😉

## 📬 Feedback and Contributions

Feedback, suggestions, and pull requests are welcome!  
Feel free to [open an issue](https://github.com/gioxx/curl-ip/issues) or contribute directly.
