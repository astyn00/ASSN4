"""
CUSTOM WEATHER EXPORTER - ASSIGNMENT 4
=======================================
Этот скрипт собирает метрики погоды из OpenWeather API
и публикует их для Prometheus каждые 20 секунд.

КАК ИСПОЛЬЗОВАТЬ:
1. Получи бесплатный API ключ: https://openweathermap.org/api
2. Установи зависимости: pip install prometheus-client requests
3. Экспортируй ключ: export OPENWEATHER_API_KEY="твой_ключ"
4. Запусти: python custom_exporter.py
5. Проверь: http://localhost:8000
"""

import os
import time
import requests
from datetime import datetime
from prometheus_client import start_http_server, Gauge, Counter, Info
import logging

# ============= НАСТРОЙКИ =============
API_KEY = os.getenv('OPENWEATHER_API_KEY', '070d6841777095580fb61bb96ab296aa')
CITY = os.getenv('CITY', 'Astana')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 20))  # Секунды
PORT = int(os.getenv('PORT', 8000))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= PROMETHEUS METRICS =============

# 1. ТЕМПЕРАТУРА (основная метрика)
temperature = Gauge(
    'weather_temperature_celsius',
    'Current temperature in Celsius',
    ['city', 'country']
)

# 2. ОЩУЩАЕМАЯ ТЕМПЕРАТУРА
feels_like = Gauge(
    'weather_feels_like_celsius',
    'Feels like temperature in Celsius',
    ['city', 'country']
)

# 3. ВЛАЖНОСТЬ
humidity = Gauge(
    'weather_humidity_percent',
    'Humidity percentage',
    ['city', 'country']
)

# 4. ДАВЛЕНИЕ
pressure = Gauge(
    'weather_pressure_hpa',
    'Atmospheric pressure in hPa',
    ['city', 'country']
)

# 5. СКОРОСТЬ ВЕТРА
wind_speed = Gauge(
    'weather_wind_speed_mps',
    'Wind speed in meters per second',
    ['city', 'country']
)

# 6. НАПРАВЛЕНИЕ ВЕТРА
wind_direction = Gauge(
    'weather_wind_direction_degrees',
    'Wind direction in degrees',
    ['city', 'country']
)

# 7. ОБЛАЧНОСТЬ
clouds = Gauge(
    'weather_clouds_percent',
    'Cloudiness percentage',
    ['city', 'country']
)

# 8. ВИДИМОСТЬ
visibility = Gauge(
    'weather_visibility_meters',
    'Visibility in meters',
    ['city', 'country']
)

# 9. УФ-ИНДЕКС (если доступен)
uv_index = Gauge(
    'weather_uv_index',
    'UV index',
    ['city', 'country']
)

# 10. ВОСХОД/ЗАКАТ (в unix timestamp)
sunrise_time = Gauge(
    'weather_sunrise_timestamp',
    'Sunrise time in Unix timestamp',
    ['city', 'country']
)

sunset_time = Gauge(
    'weather_sunset_timestamp',
    'Sunset time in Unix timestamp',
    ['city', 'country']
)

# 11. СЧЁТЧИК УСПЕШНЫХ ЗАПРОСОВ
api_requests_total = Counter(
    'weather_api_requests_total',
    'Total number of API requests',
    ['status']
)

# 12. ИНФОРМАЦИЯ О ПОГОДЕ (описание)
weather_info = Info(
    'weather_description',
    'Current weather description'
)

# ============= ФУНКЦИИ =============

def get_weather_data():
    """
    Получает данные о погоде из OpenWeather API
    """
    url = f'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': CITY,
        'appid': API_KEY,
        'units': 'metric',  # Цельсий
        'lang': 'en'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        api_requests_total.labels(status='success').inc()
        
        logger.info(f"✓ Weather data received for {CITY}")
        return data
        
    except requests.exceptions.RequestException as e:
        api_requests_total.labels(status='error').inc()
        logger.error(f"✗ Error fetching weather data: {e}")
        return None


def update_metrics(data):
    """
    Обновляет Prometheus метрики на основе данных о погоде
    """
    if not data:
        return
    
    try:
        city_name = data['name']
        country = data['sys']['country']
        
        # Основные метрики
        temperature.labels(city=city_name, country=country).set(
            data['main']['temp']
        )
        
        feels_like.labels(city=city_name, country=country).set(
            data['main']['feels_like']
        )
        
        humidity.labels(city=city_name, country=country).set(
            data['main']['humidity']
        )
        
        pressure.labels(city=city_name, country=country).set(
            data['main']['pressure']
        )
        
        # Ветер
        wind_speed.labels(city=city_name, country=country).set(
            data['wind'].get('speed', 0)
        )
        
        wind_direction.labels(city=city_name, country=country).set(
            data['wind'].get('deg', 0)
        )
        
        # Облачность и видимость
        clouds.labels(city=city_name, country=country).set(
            data['clouds']['all']
        )
        
        visibility.labels(city=city_name, country=country).set(
            data.get('visibility', 0)
        )
        
        # Восход и закат
        sunrise_time.labels(city=city_name, country=country).set(
            data['sys']['sunrise']
        )
        
        sunset_time.labels(city=city_name, country=country).set(
            data['sys']['sunset']
        )
        
        # Информация о погоде (описание)
        weather_desc = data['weather'][0]['description']
        weather_main = data['weather'][0]['main']
        weather_info.info({
            'city': city_name,
            'country': country,
            'description': weather_desc,
            'main': weather_main
        })
        
        # Логируем текущие значения
        logger.info(
            f"📊 Metrics updated: "
            f"Temp={data['main']['temp']}°C, "
            f"Humidity={data['main']['humidity']}%, "
            f"Pressure={data['main']['pressure']}hPa"
        )
        
    except (KeyError, TypeError) as e:
        logger.error(f"✗ Error updating metrics: {e}")


def collect_metrics():
    """
    Основной цикл сбора метрик
    """
    logger.info("=" * 60)
    logger.info("  WEATHER EXPORTER - ASSIGNMENT 4")
    logger.info("  Custom Prometheus Exporter for OpenWeather API")
    logger.info("=" * 60)
    logger.info(f"City: {CITY}")
    logger.info(f"Update interval: {UPDATE_INTERVAL} seconds")
    logger.info(f"Metrics endpoint: http://localhost:{PORT}")
    logger.info("=" * 60)
    
    # Стартуем HTTP сервер для Prometheus
    start_http_server(PORT)
    logger.info(f"✓ HTTP server started on port {PORT}")
    logger.info(f"✓ Metrics available at http://localhost:{PORT}/metrics")
    logger.info("\n🚀 Starting metric collection...\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        logger.info(f"[Iteration {iteration}] Fetching weather data...")
        
        # Получаем данные о погоде
        weather_data = get_weather_data()
        
        # Обновляем метрики
        update_metrics(weather_data)
        
        # Ждём до следующего обновления
        logger.info(f"⏱  Waiting {UPDATE_INTERVAL} seconds...\n")
        time.sleep(UPDATE_INTERVAL)


# ============= MAIN =============

if __name__ == '__main__':
    # Проверяем наличие API ключа
    if API_KEY == 'твой_ключ_здесь' or not API_KEY:
        logger.error("=" * 60)
        logger.error("ERROR: OpenWeather API key not found!")
        logger.error("=" * 60)
        logger.error("Please:")
        logger.error("1. Get free API key from: https://openweathermap.org/api")
        logger.error("2. Set environment variable:")
        logger.error("   export OPENWEATHER_API_KEY='your_key_here'")
        logger.error("3. Or edit API_KEY in the script")
        logger.error("=" * 60)
        exit(1)
    
    try:
        collect_metrics()
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("✓ Weather Exporter stopped by user")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()