from flask import Flask, request, Response, abort
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# Base route to explain usage
@app.route('/')
def index():
    return "Use the /prxy?target_host=http://example.com/some/path to access the proxy."

@app.route('/prxy', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/prxy/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(subpath=""):
    # 1. Dynamically get the target host from a URL parameter
    target_host = request.args.get('target_host')

    if not target_host:
        abort(400, description="Missing 'target_host' URL parameter.")
        
    # Build the full target URL using urljoin for robust path handling
    full_target_url = urljoin(target_host, subpath)

    # 2. Make the request to the external site
    try:
        # Pass through arguments and form data (for POST requests)
        if request.method in ['POST', 'PUT']:
             resp = requests.request(
                 method=request.method,
                 url=full_target_url,
                 params=request.args,
                 data=request.form,
                 stream=True # Use stream=True for efficiency
             )
        else:
             resp = requests.request(
                 method=request.method,
                 url=full_target_url,
                 params=request.args,
                 stream=True
             )

    except requests.exceptions.RequestException as e:
        # Handle connection errors gracefully
        abort(502, description=f"Bad Gateway: Could not reach the target host.")

    # 3. Handle HTML content rewriting
    content_type = resp.headers.get('Content-Type', '')
    
    if 'text/html' in content_type:
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # This is the core logic: rewrite all relative URLs to point back through *this* proxy
        for tag in soup.find_all(['a', 'link', 'script', 'img', 'form']):
            # Determine which attribute to check (href or src or action)
            attr_name = ''
            if tag.name in ['a', 'link']: attr_name = 'href'
            elif tag.name in ['script', 'img']: attr_name = 'src'
            elif tag.name == 'form': attr_name = 'action'
            
            if attr_name and tag.has_attr(attr_name):
                original_url = tag[attr_name]
                
                # Check if the URL is relative (starts with /) or absolute but within the same domain
                if original_url.startswith('/') or urlparse(original_url).netloc == urlparse(target_host).netloc:
                    # Rewrite the URL to route back to OUR proxy endpoint, 
                    # preserving the original target host parameter for the next request.
                    proxied_url = f"/prxy{original_url}?target_host={target_host}"
                    tag[attr_name] = proxied_url

        # Return the modified HTML content
        # We need to manually strip response headers that might cause issues (like content-encoding)
        headers = dict(resp.headers)
        del headers['Content-Encoding'] # Avoid double encoding issues
        
        return Response(str(soup), resp.status_code, headers)

    # For CSS, JS, images, just return them directly (they typically load fine if linked absolutely by the target site)
    return Response(resp.content, resp.status_code, resp.headers.items())

if __name__ == '__main__':
    app.run(debug=True)

