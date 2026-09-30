# سورس ميمو - Source Memo - نظام البقاء حي
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "سورس ميمو شغال 24 ساعة - Source Memo is Alive! @memoo_factory_bot"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
