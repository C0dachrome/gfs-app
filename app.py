from flask import Flask

application = Flask(_name_)

@application.route("/")
def home:
    return "hello"
if __name__ == "__main__":
    application.run()
