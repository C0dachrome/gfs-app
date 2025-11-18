from flask import Flask, request, abort, Response
import requests # Import the requests library

app = Flask(__name__)

@app.route('/')
def index():
    return "Go to /proxy?url=https://www.example.com to view a proxied site."

# Define the proxy endpoint
@app.route('/proxy')
def proxy_external_site():
    target_url = request.args.get('url')

    if not target_url:
        abort(400, description="Missing 'url' parameter.")

    # Security Check: Add validation if you want to restrict which sites can be proxied
    # In a real application, you should only allow specific, trusted domains.

    try:
        # Fetch the content from the external URL using your server's connection
        response = requests.get(target_url)
        
        # Create a Flask response object using the external content
        proxied_response = Response(response.content, response.status_code)
        
        # Copy necessary headers (like Content-Type) from the external site's response
        # to ensure the browser renders the content correctly (e.g., as text/html)
        for header, value in response.headers.items():
            # Exclude headers that might cause issues in a proxy setup (like security headers or content encoding)
            if header.lower() not in ['content-encoding', 'transfer-encoding', 'content-location', 'x-frame-options']:
                proxied_response.headers[header] = value

        return proxied_response

    except requests.exceptions.RequestException as e:
        abort(502, description=f"Bad Gateway: Could not reach the external site. Error: {e}")

