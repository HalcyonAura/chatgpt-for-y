from flask import Flask, request, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os

# load_dotenv()
# # OpenAI API key
# client = OpenAI(
#   api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
# )
app = Flask(__name__)

@app.route("/index", methods=["GET","POST"])
def index():
    if request.method:
        question = request.form.get("question")
        return render_template("index.html", question=question)
    else:
        return render_template("index.html")
