#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__, static_folder='.', static_url_path='')


html=open("findings.txt",'r').read()

@app.route("/")
def charts():
    return html

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=6060)
