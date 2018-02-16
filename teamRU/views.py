from flask import Flask, render_template, request, json
import random
from teamRU import app

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')

