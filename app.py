from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import requests

app = Flask(__name__)

DATABASE = 'form_data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        db = get_db()
        db.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        db.commit()
        return redirect(url_for('weather_form'))
    return render_template('register.html')

@app.route('/weather_form')
def weather_form():
    return render_template('weather.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    date = request.form['date']
    weather_data = get_weather_data(city, date)

    if not weather_data:
        return "Error fetching weather data. Please try again."

    return render_template('weather_result.html', city=city, weather_data=weather_data)

@app.route('/users', methods=['GET'])
def users():
    db = get_db()
    cur = db.execute('SELECT * FROM users')
    users_list = cur.fetchall()
    return render_template('users.html', users=users_list)

def get_weather_data(city, date=None):
    api_key = "0b5d04b54c98466896d63534242509"  
    if date:
        # Fetch historical weather for the provided date
        url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={city}&dt={date}"
    else:
        # Fetch current weather
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    
    response = requests.get(url)
    data = response.json()

    # Error handling
    if response.status_code != 200 or 'error' in data:
        return None
    
    return data

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
