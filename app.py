from flask import Flask, request
from markupsafe import escape  # Modifica l'importazione

app = Flask(__name__)

@app.route('/')
def get_ip():
    """
    Returns the IP address of the client. If the request is forwarded by a proxy server,
    the IP address of the proxy server is returned instead.
    """
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return escape(ip) + "\n"  # Usa l'escape importato correttamente

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
