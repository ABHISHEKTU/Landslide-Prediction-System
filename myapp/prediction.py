from django.shortcuts import render
import requests
import numpy as np
import os
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix for quantization_config error in Dense layer during model load
from tensorflow.keras.layers import Dense
original_dense_init = Dense.__init__

def new_dense_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    return original_dense_init(self, *args, **kwargs)

Dense.__init__ = new_dense_init


# =========================
# CONFIG
# =========================

# Load from .env (never hardcode keys)
MODEL_PATH = os.getenv("MODEL_PATH", "myapp/landslide_model_new.h5")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Input image size expected by the model
IMG_SIZE = (224, 224)

print("\n================ MODEL LOADING ================")
print("MODEL PATH :", MODEL_PATH)
print("IMG SIZE   :", IMG_SIZE)

# Load the trained model without recompiling
model = load_model(MODEL_PATH, compile=False)

print("✅ Model loaded successfully")
print("Model inputs :", model.inputs)
print("Model outputs:", model.outputs)

# Configure Gemini AI model for generating risk analysis text
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

print("✅ Gemini configured")
print("==============================================\n")


# =========================
# IMAGE LOAD
# =========================

def load_image_from_disk(path, dem=False):

    mode = "grayscale" if dem else "rgb"

    print(f"\n🖼️ Loading image from disk")
    print("Path :", path)
    print("Mode :", mode)

    img = load_img(path, target_size=IMG_SIZE, color_mode=mode)
    arr = img_to_array(img) / 255.0

    print("Shape:", arr.shape)
    print("Min  :", arr.min())
    print("Max  :", arr.max())

    return arr


# =========================
# SATELLITE DOWNLOAD
# =========================

def download_satellite(lat, lon):

    try:

        url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&size=450,450&z=16&l=sat"

        print("\n================ SATELLITE DOWNLOAD ================")
        print("Latitude  :", lat)
        print("Longitude :", lon)
        print("URL       :", url)

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        print("Status code:", response.status_code)
        print("Content len:", len(response.content))

        filename = f"sat_{lat}_{lon}.png"
        path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        with open(path, "wb") as f:
            f.write(response.content)

        print("✅ Satellite saved:", path)
        print("===================================================\n")

        return filename

    except Exception as e:

        print("❌ Satellite Error:", e)

        filename = f"sat_{lat}_{lon}.png"
        path = os.path.join(settings.MEDIA_ROOT, filename)
        blank = np.zeros((224, 224, 3))
        Image.fromarray(blank.astype(np.uint8)).save(path)

        print("⚠️ Blank satellite image created:", path)

        return filename


# =========================
# DEM GRID DOWNLOAD
# =========================

def download_dem_grid(lat, lon):

    offset = 0.0015
    locations = []

    for i in np.linspace(lat - offset, lat + offset, 5):
        for j in np.linspace(lon - offset, lon + offset, 5):
            locations.append(f"{i},{j}")

    loc_string = "|".join(locations)
    url = f"https://api.opentopodata.org/v1/srtm30m?locations={loc_string}"

    print("\n================ DEM DOWNLOAD ================")
    print("Latitude  :", lat)
    print("Longitude :", lon)
    print("URL       :", url)

    try:

        response = requests.get(url)
        data = response.json()

        print("Status code:", response.status_code)

        elevs = [r['elevation'] for r in data['results']]
        grid = np.array(elevs).reshape((5, 5))

        if grid.max() != grid.min():
            grid = (grid - grid.min()) / (grid.max() - grid.min()) * 255
        else:
            grid = np.ones((5, 5)) * 127

        img = Image.fromarray(grid.astype(np.uint8)).resize(IMG_SIZE)

        filename = f"dem_{lat}_{lon}.png"
        path = os.path.join(settings.MEDIA_ROOT, filename)
        img.save(path)

        print("✅ DEM saved:", path)
        print("Average elevation:", np.mean(elevs))
        print("=============================================\n")

        return filename, np.mean(elevs)

    except Exception as e:
        print("❌ DEM Error:", e)
        return None, 0


# =========================
# 10 DAY WEATHER
# =========================

def get_10day_weather(lat, lon):

    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&past_days=10&daily=temperature_2m_mean,precipitation_sum&timezone=auto"

    print("\n================ 10 DAY WEATHER ================")

    try:

        response = requests.get(url)
        data = response.json()

        rain_list = data["daily"]["precipitation_sum"]
        temp_list = data["daily"]["temperature_2m_mean"]

        result = {
            "avg_temp": round(np.mean(temp_list), 2),
            "total_rain": round(sum(rain_list), 2),
            "rain_list": rain_list
        }

        print("Weather result:", result)
        print("================================================\n")

        return result

    except Exception as e:

        print("❌ Weather Error:", e)

        return {
            "avg_temp": 0,
            "total_rain": 0,
            "rain_list": []
        }


# =========================
# PREDICTION API
# =========================

@csrf_exempt
def landslide_prediction(request):

    try:

        print("\n\n================ LANDSLIDE PREDICTION START ================")

        lat = float(request.POST["latitude"])
        lon = float(request.POST["longitude"])

        print("Latitude  :", lat)
        print("Longitude :", lon)

        sat_file = download_satellite(lat, lon)
        dem_file, avg_elev = download_dem_grid(lat, lon)

        sat_p = os.path.join(settings.MEDIA_ROOT, sat_file)
        dem_p = os.path.join(settings.MEDIA_ROOT, dem_file) if dem_file else sat_p

        sat_in = np.expand_dims(load_image_from_disk(sat_p), axis=0)
        dem_in = np.expand_dims(load_image_from_disk(dem_p, dem=True), axis=0)

        pred = model.predict([sat_in, dem_in], verbose=0)
        prob = float(pred[0][0])

        ml_res = "Landslide Prone" if prob >= 0.5 else "Safe Area"

        print("Prediction label    :", ml_res)

        w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        w_response = requests.get(w_url)
        w_json = w_response.json()

        current_weather = {
            "temp": w_json["main"]["temp"],
            "humidity": w_json["main"]["humidity"],
            "rain": w_json.get("rain", {}).get("1h", 0),
            "wind": w_json["wind"]["speed"]
        }

        history = get_10day_weather(lat, lon)

        try:
            prompt = f"""
Landslide Risk Analysis

Location: {lat},{lon}
Prediction: {ml_res}
Temperature: {current_weather['temp']}
Humidity: {current_weather['humidity']}
10 Day Rainfall: {history['total_rain']} mm
"""
            ai_txt = gemini_model.generate_content(prompt).text
            print("✅ Gemini response received")

        except Exception as e:
            print("❌ Gemini Error:", e)
            ai_txt = f"Prediction: {ml_res}\n10 Day Rainfall: {history['total_rain']} mm\nHigher rainfall increases landslide risk."

        response_data = {
            "status": "success",
            "prediction": ml_res,
            "probability": f"{round(prob * 100, 2)}%",
            "environment": {
                "current_weather": current_weather,
                "history": history,
                "elevation": round(avg_elev, 2)
            },
            "ai_analysis": ai_txt
        }

        print("================ LANDSLIDE PREDICTION END =================\n\n")

        return JsonResponse(response_data)

    except Exception as e:

        print("\n❌ EXCEPTION OCCURRED")
        print(traceback.format_exc())

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })
