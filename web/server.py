#!/usr/bin/env python
    
from flask import Flask, render_template

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
