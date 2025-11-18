from flask import Flask, request, redirect, abort

app = Flask(__name__)

@app.route('/redirect_service', methods=['GET'])
def redirect_service():
    # Retrieve the 'next' URL parameter from the query string
    next_url = request.args.get('next')

    # Basic validation: ensure the URL parameter is present
    if not next_url:
        # If 'next' parameter is missing, return a 400 Bad Request error
        abort(400, description="Missing 'next' URL parameter.")
    
    # VULNERABLE: Unvalidated redirect to user-provided URL
    # This code allows redirection to ANY external website specified in 'next_url'
    return redirect(next_url)

# A default root page, since the redirect page doesn't have a UI
@app.route('/')
def index():
    return "Use the /redirect_service?next=URL path to test the redirect functionality."

if __name__ == "__main__":
    app.run()
