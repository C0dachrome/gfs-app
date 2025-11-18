from flask import Flask, request, Response, abort, stream_with_context
import requests
from urllib.parse import urljoin, urlparse
# You still need 'beautifulsoup4' for rewriting HTML if you stick with that method

app = Flask(__name__)

# A general catch-all proxy that tries to pass everything through
@app.route('/prxy/<path:external_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def general_proxy(external_path):
    # Determine the target host from a query parameter
    target_host = request.args.get('target_host', 'http://example.com') # Use a default for testing

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
        abort(502, description=f"Bad Gateway: Could not reach {target_url}")

    # 2. Re-create the response headers, filtering out problematic ones like 'Content-Encoding'
    headers = {}
    for name, value in resp.headers.items():
        # Flask usually handles Transfer-Encoding, and Content-Encoding (gzip) can cause issues
        if name.lower() not in ('content-encoding', 'transfer-encoding'):
            headers[name] = value

    # 3. Stream the content back to the client directly
    # Note: This approach does NOT rewrite URLs in HTML or CSS files. 
    # It relies entirely on the target site using ABSOLUTE URLs for all resources.
    return Response(
        stream_with_context(resp.iter_content(chunk_size=1024)), 
        status=resp.status_code, 
        headers=headers
    )

# A simple root to explain usage
@app.route('/')
def index():
    return "Append the target URL to your browser bar like this: /prxy/relative/path?target_host=http://example.com"
