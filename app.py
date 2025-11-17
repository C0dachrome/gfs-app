from flask import Flask

application = Flask(__name__)

@application.route("/")
def home():
    return "hello"
if __name__ == "__main__":
    application.run()
