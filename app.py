from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

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
def debug_headers():
    """
    Return a JSON object with information about the request headers that
    are relevant for IP address detection. The object has the following
    properties:

    - remote_addr: the value of request.remote_addr
    - x_forwarded_for: the value of the X-Forwarded-For header
    - x_real_ip: the value of the X-Real-IP header
    - cf_connecting_ip: the value of the CF-Connecting-IP header
    - all_headers: a dictionary with all the request headers

    This endpoint is useful for debugging IP address detection issues.
    """
    headers_info = {
        'remote_addr': request.remote_addr,
        'x_forwarded_for': request.headers.get('X-Forwarded-For'),
        'x_real_ip': request.headers.get('X-Real-IP'),
        'cf_connecting_ip': request.headers.get('CF-Connecting-IP'),
        'all_headers': dict(request.headers)
    }
    return headers_info

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)