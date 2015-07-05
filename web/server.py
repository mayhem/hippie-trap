#!/usr/bin/env python
    
from flask import Flask, request, render_template

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

app = Flask(__name__,
        static_url_path = STATIC_PATH,
        static_folder = STATIC_FOLDER,
        template_folder = TEMPLATE_FOLDER)

@app.route('/')
def index():
    return render_template("index", title="Hue Chandelier")

@app.route('/ctrl/skip')
def skip():
    print "skip"
    # skip
    return "ok"

@app.route('/ctrl/hold')
def hold():
    print "hold"
    # hold
    return "ok"

@app.route('/ctrl/bdown')
def bdown():
    # brightness down
    print "brightness down"
    return "ok"

@app.route('/ctrl/bup')
def bup():
    # brightness up
    print "brightness up"
    return "ok"

@app.route('/ctrl/sup')
def sup():
    # speed up
    print "speed up"
    return "ok"

@app.route('/ctrl/sdown')
def sdown():
    # speed down
    print "speed down"
    return "ok"

@app.route('/run', methods=["POST"])
def run():
    print request.data
    return ""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
