from flask import Flask, request
from functools import wraps
from markupsafe import escape
import base64
import os

app = Flask(__name__)

def require_auth(f):
    """
    Decorator that checks if the request is authenticated to access the debug area.
    If not authenticated, it returns a 401 Unauthorized response with the
    WWW-Authenticate header set to 'Basic realm="Debug Area"'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not check_auth(auth):
            return 'Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Debug Area"'
            }
        return f(*args, **kwargs)
    return decorated

def check_auth(auth_header):
    """
    Check if the given 'Authorization' header is valid for accessing the debug area.
    The header should be in the format 'Basic <base64 encoded string>'.
    The decoded string should be in the format 'username:password'.
    The username should be 'debug' and the password should be the value of the
    DEBUG_TOKEN environment variable.
    """
    try:
        encoded = auth_header.split(' ')[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':')
        return username == 'debug' and password == os.environ.get('DEBUG_TOKEN')
    except:
        return False

@app.route('/')
def get_ip():
    """
    Return the client's public IP address. The priority of the headers are:
    1. CF-Connecting-IP (Cloudflare)
    2. X-Real-IP (Nginx)
    3. First IP from the chain in X-Forwarded-For
    4. request.remote_addr
    The IP is returned as a plain text response, with HTML escaping applied
    to prevent XSS attacks.
    """
    ip = (
        request.headers.get('CF-Connecting-IP') or  # Cloudflare
        request.headers.get('X-Real-IP') or         # Nginx
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or  # First IP from the chain
        request.remote_addr
    )
    return escape(ip) + "\n"

@app.route('/debug')
@require_auth
def debug_headers():
    """
    Debug endpoint to display request headers if debugging is enabled.
    Protected by Basic Authentication (username: debug, password: DEBUG_TOKEN).
    Returns:
        - A dictionary containing request headers information if authorized
        - 'Not Found' with HTTP status 404 if debugging is not enabled
    """
    if not os.environ.get('ENABLE_DEBUG', 'false').lower() == 'true':
        return 'Not Found', 404
   
    headers_info = {
        'remote_addr': request.remote_addr,
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_real_ip': request.headers.get('X-Real-IP'),
        'cf_connecting_ip': request.headers.get('CF-Connecting-IP'),
        'all_headers': dict(request.headers),
        'timestamp': request.headers.get('Date')
    }
    return headers_info

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)