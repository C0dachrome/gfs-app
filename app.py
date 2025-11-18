from flask import Flask

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # ... your login logic here ...
    if valid_credentials:
        next_url = request.args.get('next')
        if next_url:
            # VULNERABLE: Unvalidated redirect to user-provided URL
            return redirect(next_url)
        return redirect('/') # Default redirect
    return "Login Failed
if __name__ == "__main__":
    app.run()
