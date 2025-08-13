from flask import Flask, request, Response, redirect, jsonify
from functools import wraps
from markupsafe import escape
import base64
import binascii
import hmac
import ipaddress
import os
# If you run behind a reverse proxy (Nginx/Traefik), consider enabling ProxyFix:
# from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# Host favicon from GitHub
FAVICON_URL = "https://raw.githubusercontent.com/gioxx/curl-ip/main/favicon.ico"

@app.route('/favicon.ico', methods=['GET', 'HEAD'])
def favicon():
    """Permanent redirect to a GitHub-hosted .ico."""
    resp = redirect(FAVICON_URL, code=308)  # 308 Permanent Redirect preserves method/body
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return resp

def require_auth(f):
    """
    Decorator enforcing Basic Auth for /debug.
    Username must be 'debug' and password equals the DEBUG_TOKEN env var.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not check_auth(auth):
            return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Debug Area"'}
        return f(*args, **kwargs)
    return decorated

def check_auth(auth_header: str) -> bool:
    """
    Validate Basic auth header 'Basic <base64>'.
    Uses constant-time comparison for credentials.
    """
    try:
        scheme, _, encoded = auth_header.partition(' ')
        if scheme.lower() != 'basic' or not encoded:
            return False
        decoded = base64.b64decode(encoded, validate=True).decode('utf-8')
        if ':' not in decoded:
            return False
        username, password = decoded.split(':', 1)
        expected_user = 'debug'
        expected_pass = os.environ.get('DEBUG_TOKEN') or ''
        return hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass)
    except (binascii.Error, UnicodeDecodeError):
        return False

def _pick_client_ip() -> str:
    """
    Resolve client IP with the following precedence:
    1. CF-Connecting-IP (Cloudflare)
    2. X-Real-IP (Nginx/Proxy)
    3. First IP from X-Forwarded-For
    4. request.remote_addr
    Validates the IP format (IPv4/IPv6). If an invalid value is found, falls back.
    """
    candidates = [
        request.headers.get('CF-Connecting-IP'),
        request.headers.get('X-Real-IP'),
        (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip() or None,
        request.remote_addr
    ]
    for ip in candidates:
        if not ip:
            continue
        # Remove possible port suffix (e.g., "1.2.3.4:12345") and handle bracketed IPv6
        ip_clean = ip.split('%')[0].split(']')[-1].split(':')[0] if ip.startswith('[') else ip.split(':')[0]
        try:
            ipaddress.ip_address(ip_clean)
            return ip_clean
        except ValueError:
            continue
    return request.remote_addr or '0.0.0.0'

@app.route('/')
def get_ip():
    """Return client IP as text and advertise the favicon via Link header."""
    ip = _pick_client_ip()
    return Response(
        escape(ip) + "\n",
        mimetype='text/plain; charset=utf-8',
        headers={'Link': f'<{FAVICON_URL}>; rel="icon"'}
    )

@app.route('/debug')
@require_auth
def debug_headers():
    """
    Debug endpoint protected by Basic Auth.
    Only available when ENABLE_DEBUG=true.
    Returns a JSON payload with selected details.
    """
    if os.environ.get('ENABLE_DEBUG', 'false').lower() != 'true':
        return 'Hey gringo, there is nothing to see here.', 404

    # Avoid reflecting Authorization header back
    safe_headers = {k: v for k, v in request.headers.items() if k.lower() != 'authorization'}
    headers_info = {
        'remote_addr': request.remote_addr,
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_real_ip': request.headers.get('X-Real-IP'),
        'cf_connecting_ip': request.headers.get('CF-Connecting-IP'),
        'all_headers': safe_headers,
    }
    return jsonify(headers_info)

if __name__ == '__main__':
    # Use 0.0.0.0:8080 by default; adjust as needed.
    app.run(host='0.0.0.0', port=8080)
