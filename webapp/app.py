from flask import Flask, render_template, request, redirect, url_for
from collections import Counter
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__, static_folder='assets')
client = MongoClient('mongodb+srv://chsh7390:qwaszx1203@cluster0.0ap2wng.mongodb.net/?retryWrites=true&w=majority')

db = client['KAVACH_NEW']
crimes = db['CRIME']

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    all_crimes = crimes.find()
    count = crimes.count_documents({})
    return render_template('dashboard.html', title='Dashboard',
                           crimes=all_crimes, count=count)

@app.route('/vizualize')
def vizualize():
    all_crimes = list(crimes.find())
    cnt = Counter([x['city'] for x in all_crimes]).most_common(5)
    cnt_crime = Counter([x['nature'] for x in all_crimes]).most_common(5)
    return render_template('vizualize.html', title='Vizualization', cnt=cnt, cnt_crime=cnt_crime)

@app.post('/put')
def put():
    city = request.form['city']
    coordinates = eval(request.form['coordinates'])
    time = datetime.now()
    level = request.form['level']
    nature = request.form['nature']
    reported = request.form['reported']
    crimes.insert_one({'city': city,
            'coordinates': coordinates,
            'time': time,
            'level': level,
            'nature': nature,
            'reported': reported})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
