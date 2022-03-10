#Should keep bot running constantly
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "Your bot is barley fucking funktioning!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
