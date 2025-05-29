from flask import Flask, request, render_template, jsonify, make_response, session
import requests
from datetime import datetime, timedelta
import json
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
CORS(app)

# Configure Flask-SQLAlchemy for session storage and search history
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
Session(app)


# Define Search model for storing search history
class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)


# Initialize database
def init_db():
    with app.app_context():
        db.create_all()


init_db()


# Weather Provider abstraction
class WeatherProvider:
    def get_forecast(self, lat, lon):
        raise NotImplementedError


class OpenMeteoProvider(WeatherProvider):
    def get_forecast(self, lat, lon):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&timezone=auto"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()['daily']
        except requests.RequestException:
            return None


weather_provider = OpenMeteoProvider()


# Fetch city suggestions from Nominatim
def get_city_suggestions(query):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5"
    try:
        response = requests.get(url, headers={'User-Agent': 'WeatherApp/1.0'})
        response.raise_for_status()
        data = response.json()
        return [{'name': item['display_name'], 'lat': item['lat'], 'lon': item['lon']} for item in data]
    except requests.RequestException:
        return []


# Validate and get coordinates
def validate_and_get_coordinates(city, lat, lon):
    if not city:
        return None, None, None, "Недопустимые данные города"

    if not all([lat, lon]):
        suggestions = get_city_suggestions(city)
        if not suggestions:
            return None, None, None, "Город не найден по указанному названию"
        suggestion = suggestions[0]
        city, lat, lon = suggestion['name'], suggestion['lat'], suggestion['lon']

    try:

        lat, lon = float(lat), float(lon)
        return city, lat, lon, None
    except (ValueError, TypeError):
        return None, None, None, "Недопустимые координаты города"


# Process weather request
def process_weather_request(user_id, city, lat, lon):
    weather_data = weather_provider.get_forecast(lat, lon)
    if not weather_data:
        return None, "Не удалось получить данные о погоде"

    search = Search(user_id=user_id, city=city, timestamp=datetime.now().isoformat())
    db.session.add(search)
    db.session.commit()

    return weather_data, None


@app.route('/')
def index():
    last_city = request.cookies.get('last_city', '')
    return render_template('index.html', last_city=last_city)


def render_error(error, last_city):
    return render_template('index.html', error=error, last_city=last_city)


@app.route('/weather', methods=['POST'])
def weather():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    city = request.form.get('city')
    lat = request.form.get('lat')
    lon = request.form.get('lon')

    city, lat, lon, error = validate_and_get_coordinates(city, lat, lon)
    if error:
        return render_error(error, city)

    weather_data, error = process_weather_request(session['user_id'], city, lat, lon)
    if error:
        return render_error(error, city)

    response = make_response(render_template('weather.html', city=city, weather=weather_data))
    response.set_cookie('last_city', city, max_age=30 * 24 * 60 * 60)
    return response


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    suggestions = get_city_suggestions(query)
    return jsonify(suggestions)


@app.route('/api/search_stats', methods=['GET'])
def search_stats():
    stats = db.session.query(Search.city, db.func.count(Search.city).label('count')) \
        .group_by(Search.city).order_by(db.desc('count')).all()
    return jsonify([{'city': city, 'count': count} for city, count in stats])


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)