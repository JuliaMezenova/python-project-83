from flask import Flask, render_template
from dotenv import load_dotenv
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

load_dotenv()  # take environment variables from .env.


@app.route("/")
def hello_world():
    return render_template('index.html')
