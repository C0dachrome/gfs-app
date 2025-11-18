from flask import Flask, request, Response, abort, stream_with_context
import requests
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# A general catch-all prxy that tries to pass everything through
# This route MUST match the URL structure you are using (e.g., /prxy/...)
@app.route('/prxy/<path:external_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def general_prxy(external_path):
    # Determine the target host from a query parameter
    # You must include the ?target_host=http://example.com part in your browser URL
    target_host = request.args.get('target_host')

    if not target_host:
        # If you forget the ?target_host= param, you will get this 400 error
        abort(400, description="Missing 'target_host' URL parameter.")
    
    # Construct the full URL, handling relative paths correctly
    target_url = urljoin(target_host, external_path)
    
    # 1. Make the request to the external site from the PythonAnywhere server
    try:
        # Use stream=True to handle large files efficiently
        resp = requests.request(
            method=request.method,
            url=target_url,
            params=request.args,
            data=request.get_data(), # Gets raw body data for all methods (POST form data etc.)
            cookies=request.cookies, # Pass user cookies if needed (careful with security)
            allow_redirects=False,
            stream=True
        )
    except requests.exceptions.RequestException as e:
        # Handle connection errors gracefully
        abort(502, description=f"Bad Gateway: Could not reach {target_url}")

    # 2. Re-create the response headers, filtering out problematic ones like 'Content-Encoding'
    headers = {}
    for name, value in resp.headers.items():
        if name.lower() not in ('content-encoding', 'transfer-encoding'):
            headers[name] = value

    # 3. Stream the content back to the client directly
    return Response(
        stream_with_context(resp.iter_content(chunk_size=1024)), 
        status=resp.status_code, 
        headers=headers
    )

# A simple root to explain usage
@app.route('/')
def index():
    # This message explains how to use the prxy
    return "To use the prxy, construct a URL like this on your site: /prxy/index.html?target_host=http://books.toscrape.com"

# The standard Flask entry point (ensure this is present for local testing)
if __name__ == '__main__':
    app.run(debug=True)
