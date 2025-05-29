# Weather Forecast Web Application

## Features Implemented
- **Weather Forecast**: Users can input a city name and get a 7-day weather forecast (max/min temperature, precipitation, wind speed) from Open-Meteo API.
- **Autocomplete**: City name suggestions using Nominatim API.
- **Recent City**: Suggests the last searched city via browser cookies.
- **Search History**: Stores user searches in SQLite database.
- **Search Stats API**: Endpoint (`/api/search_stats`) to view city search counts.
- **Docker**: App is containerized for easy deployment.
- **Tests**: Basic unit tests for main routes using `pytest`.

## Technologies Used
- **Python/Flask**: Web framework for backend.
- **Open-Meteo API**: Weather data.
- **Nominatim API**: City autocomplete.
- **SQLite**: Search history storage.
- **Tailwind CSS/jQuery**: Frontend styling and autocomplete.
- **Docker**: Containerization.
- **pytest**: Testing.

## How to Run

### Prerequisites
- Docker installed
- Internet connection for API calls

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Build and run the Docker container:
   ```bash
   docker build -t weather-app .
   docker run -p 5000:5000 weather-app
   ```
3. Open `http://localhost:5000` in your browser.
4. To run tests:
   ```bash
   docker exec -it <container-id> pytest
   ```

### Usage
- Enter a city name in the input field; autocomplete suggestions appear after typing 2+ characters.
- Select a city and submit to view the weather forecast.
- Revisit the site to see the last searched city as a suggestion.
- Access `/api/search_stats` to see city search statistics.

## Notes
- The app uses the user's IP as a simple user ID for search history.
- Ensure internet access for API calls to Open-Meteo and Nominatim.