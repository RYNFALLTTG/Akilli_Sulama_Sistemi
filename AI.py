import time
import requests
import RPi.GPIO as GPIO

# Sensor ve role pin aya
SOIL_MOISTURE_PIN = 18  # Dijital toprak nem GPIO Pin
RELAY_PIN = 17  # Role Pin

# OpenWeatherMap ayarlari
API_KEY = 'de7ecd2a916df77f88a4e3b5c8ab5eec'
CITY = 'KONYA'
WEATHER_API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Nem esik degerleri (Dijital sensorr icin )
SOIL_MOISTURE_THRESHOLD = GPIO.LOW  # Toprak nemli oldugunda sensor HIGH 

# GPIO ayarlari
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_MOISTURE_PIN, GPIO.IN)  # Dijital sensor pinini giris olarak ayarla
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Basta pompayi kapali tut

# OpenWeatherMap'ten veri cekme
def get_weather_data():
    try:
        response = requests.get(WEATHER_API_URL)
        data = response.json()
        weather_main = data['weather'][0]['main']
        rain = (weather_main == 'Rain')
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return rain, temp, humidity
    except Exception as e:
        print(f"Weather data error: {e}")
        return False, None, None

# Ana kontrol dongusu
try:
    while True:
        # 1. Toprak nemini oku (Dijital sensorden)
        soil_moisture = GPIO.input(SOIL_MOISTURE_PIN)
        print(f"Soil Moisture Level: {'Wet' if soil_moisture == GPIO.HIGH else 'Dry'}")

        # 2. Hava durumu verisini cek
        rain, temp, humidity = get_weather_data()
        print(f"Rain: {rain}, Temp: {temp}°C, Humidity: {humidity}%")

        # 3. Karar verme
        if soil_moisture == SOIL_MOISTURE_THRESHOLD and not rain:
            # Toprak kuru ve yagmur yok -> Sulamaya basla
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Roleyi ac, pompa ac
            print("Pump ON: Soil is dry and no rain detected.")
        else:
            # Toprak nemli veya yagmur var -> Sulamayi kapat
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Roleyi kapat, pompa dursun
            print("Pump OFF: Soil is wet or rain detected.")

        # 4. 10 dakikada bir kontrol
        time.sleep(600)

except KeyboardInterrupt:
    print("Program durduruldu.")
    GPIO.cleanup()
