from flask import Flask, render_template
from plotly_charts import journal_calendar


app = Flask(__name__)

@app.route('/codex-vitae')
def index():
    return render_template('index.html') 

def index():

    journal_calendar = journal_calendar()
    return render_template('index.html', plot=journal_calendar)
