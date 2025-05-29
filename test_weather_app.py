import pytest
from weather_app import app, db, Search, validate_and_get_coordinates


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Прогноз погоды".encode('utf-8') in response.data


def test_weather_no_data(client):
    response = client.post('/weather', data={})
    assert response.status_code == 200
    assert "Недопустимые данные города".encode('utf-8') in response.data


def test_weather_invalid_city(client):
    response = client.post('/weather', data={'city': 'InvalidCity'})
    assert response.status_code == 200
    assert "Город не найден по указанному названию".encode('utf-8') in response.data



def test_autocomplete(client):
    response = client.get('/autocomplete?q=Moscow')
    assert response.status_code == 200
    assert "Moscow".encode('utf-8') in response.data


def test_validate_and_get_coordinates_invalid_city():
    city, lat, lon, error = validate_and_get_coordinates("InvalidCity", None, None)
    assert error == "Город не найден по указанному названию"
    assert city is None
    assert lat is None
    assert lon is None