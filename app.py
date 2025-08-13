from flask import Flask, request
from functools import wraps
from markupsafe import escape
import base64

def require_auth(f):
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

    This route is only accessible if the environment variable 'ENABLE_DEBUG' 
    is set to 'true' and the correct debug token is provided via query 
    parameter 'token' or header 'X-Debug-Token'.

    Returns:
        - A dictionary containing request headers information if authorized,
          including 'remote_addr', 'x_forwarded_for', 'x_real_ip', 
          'cf_connecting_ip', and 'timestamp'.
        - 'Not Found' with HTTP status 404 if debugging is not enabled.
        - 'Forbidden' with HTTP status 403 if the debug token is invalid.
    """

    if not os.environ.get('ENABLE_DEBUG', 'false').lower() == 'true':
        return 'Not Found', 404
    
    token = request.args.get('token') or request.headers.get('X-Debug-Token')
    if token != os.environ.get('DEBUG_TOKEN'):
        return 'Forbidden', 403
    
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