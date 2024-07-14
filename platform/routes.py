from flask import Flask, send_from_directory, render_template
import os
from app import app

@app.route('/')
def index():
    return render_template('index.html')


