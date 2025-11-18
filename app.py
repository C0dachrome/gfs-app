from flask import Flask, request, redirect, abort, render_template # Import render_template

app = Flask(__name__)

# A default root page
@app.route('/')
def index():
    return "Use the /confirm_redirect?next=URL path to test the confirmation functionality."

# This new route is where the user lands first.
@app.route('/confirm_redirect', methods=['GET'])
def confirm_redirect():
    next_url = request.args.get('next')

    if not next_url:
        abort(400, description="Missing 'next' URL parameter.")
    
    # Pass the destination URL to the HTML template for display
    return render_template('confirm.html', next_url=next_url)

# This route handles the actual redirection ONLY after the user clicks 'Proceed'
@app.route('/proceed', methods=['POST'])
def proceed_to_redirect():
    # Get the next_url from the submitted form data (not the URL query params)
    next_url = request.form.get('next_url')

    if next_url:
        return redirect(next_url)
    
    abort(400, description="Invalid redirect attempt.")
