from flask import Flask

app = Flask(_name_)

@app.route("/")
def home:
    return "hello"
if __name__ == "__main__":
    app.run()
