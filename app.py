from flask import Flask, request, Response, jsonify
from functools import wraps
from markupsafe import escape
from io import BytesIO
import base64
import binascii
import hmac
import ipaddress
import os
# If you run behind a reverse proxy (Nginx/Traefik), consider enabling ProxyFix:
# from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# --- IP favicon in Base64 ---
FAVICON_B64 = (
    "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"
)
FAVICON_BYTES = base64.b64decode(FAVICON_B64)

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

        # Strict base64 decode
        decoded = base64.b64decode(encoded, validate=True).decode('utf-8')
        if ':' not in decoded:
            return False
        username, password = decoded.split(':', 1)

        expected_user = 'debug'
        expected_pass = os.environ.get('DEBUG_TOKEN') or ''
        return hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass)
    except (binascii.Error, UnicodeDecodeError):
        return False

@app.route('/favicon.ico', methods=['GET', 'HEAD'])
def favicon():
    """Return a PNG favicon to avoid 404s and enable browser caching."""
    return Response(
        FAVICON_BYTES,
        mimetype='image/png',
        headers={'Cache-Control': 'public, max-age=31536000, immutable'}
    )

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
        # Remove possible port suffix (e.g., "1.2.3.4:12345")
        ip_clean = ip.split('%')[0].split(']')[-1].split(':')[0] if ip.startswith('[') else ip.split(':')[0]
        try:
            ipaddress.ip_address(ip_clean)
            return ip_clean
        except ValueError:
            continue
    # As a very last resort, return what Flask gives us
    return request.remote_addr or '0.0.0.0'

@app.route('/')
def get_ip():
    """
    Return the client's public IP address as plain text.
    HTML-escaped to avoid accidental XSS if proxies inject odd values.
    """
    ip = _pick_client_ip()
    return escape(ip) + "\n"

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

    headers_info = {
        'remote_addr': request.remote_addr,
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_real_ip': request.headers.get('X-Real-IP'),
        'cf_connecting_ip': request.headers.get('CF-Connecting-IP'),
        'all_headers': dict(request.headers),
    }
    return jsonify(headers_info)

if __name__ == '__main__':
    # Use 0.0.0.0:8080 by default; adjust as needed.
    app.run(host='0.0.0.0', port=8080)
