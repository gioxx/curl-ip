from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def get_ip():
    """
    Returns the IP address of the client. If the request is forwarded by a proxy server,
    the IP address of the proxy server is returned instead.
    """
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return ip + "\n"
