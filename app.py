from flask import Flask, request, Response, redirect, jsonify
from functools import wraps
from markupsafe import escape
import base64, binascii, hmac, ipaddress, os

app = Flask(__name__)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

FAVICON_URL = "https://raw.githubusercontent.com/gioxx/curl-ip/main/favicon.ico"

@app.route('/favicon.ico', methods=['GET', 'HEAD'])
def favicon():
    """Permanent redirect to a GitHub-hosted .ico."""
    resp = redirect(FAVICON_URL, code=308)
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return resp

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

def require_auth(f):
    """
    Gate /debug behind ENABLE_DEBUG + DEBUG_TOKEN and then Basic Auth.
    Rules:
      - If ENABLE_DEBUG is missing or not 'true' -> 404
      - If ENABLE_DEBUG is 'true' but DEBUG_TOKEN is missing -> 500
      - Else -> enforce Basic Auth (username=debug, password=$DEBUG_TOKEN)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        enable_debug = os.environ.get('ENABLE_DEBUG')
        if not enable_debug or enable_debug.lower() != 'true':
            return 'Hey gringo, there is nothing to see here.', 404

        if not os.environ.get('DEBUG_TOKEN'):
            return 'Missing DEBUG_TOKEN environment variable in container configuration.', 500

        auth = request.headers.get('Authorization')
        if not auth or not check_auth(auth):
            return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Debug Area"'}
        return f(*args, **kwargs)
    return decorated

def _pick_client_ip() -> str:
    """
    Resolve client IP with precedence:
    1. CF-Connecting-IP, 2. X-Real-IP, 3. first X-Forwarded-For, 4. remote_addr
    Validate IPv4/IPv6; strip port/brackets if present.
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

@app.route('/info')
def get_info():
    """Redirect to ipinfo.io for detailed IP information."""
    ip = _pick_client_ip()
    return redirect(f'https://ipinfo.io/what-is-my-ip', code=302)

@app.route('/debug')
@require_auth
def debug_headers():
    """
    Debug endpoint (reachable only when ENABLE_DEBUG=true and DEBUG_TOKEN is set).
    Returns a JSON payload with selected details.
    """
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
    app.run(host='0.0.0.0', port=8080)
