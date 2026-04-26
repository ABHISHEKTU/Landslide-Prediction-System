

# ================================================================================





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

# Path to the trained landslide ML model
MODEL_PATH = r"c:\Users\AKSHAY\Downloads\landslide_model_new.h5"

# Input image size expected by the model
IMG_SIZE = (224, 224)

# OpenWeatherMap API key for current weather data
WEATHER_API_KEY = "c24edd93da6f4c456247c93bb20ed6a0"

# Google Gemini API key for AI analysis text
GEMINI_API_KEY = "AIzaSyB0o-yusVZjKZVxYKG3v1po_X7AaWhyO3M"


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

    # Load as grayscale for DEM image, RGB for satellite image
    mode = "grayscale" if dem else "rgb"

    print(f"\n🖼️ Loading image from disk")
    print("Path :", path)
    print("Mode :", mode)

    # Load and resize image, then normalize pixel values to 0-1
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

    # Download satellite image from Yandex static maps API
    try:

        url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&size=450,450&z=16&l=sat"

        print("\n================ SATELLITE DOWNLOAD ================")
        print("Latitude  :", lat)
        print("Longitude :", lon)
        print("URL       :", url)

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        print("Status code:", response.status_code)
        print("Content len:", len(response.content))

        # Save satellite image to media folder
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

        # If download fails create a blank black image as fallback
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

    # Create a 5x5 grid of coordinates around the location
    offset = 0.0015
    locations = []

    for i in np.linspace(lat - offset, lat + offset, 5):
        for j in np.linspace(lon - offset, lon + offset, 5):
            locations.append(f"{i},{j}")

    # Fetch elevation data for all 25 grid points from OpenTopoData
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
        print("Raw DEM response keys:", data.keys())

        # Extract elevation values from response
        elevs = [r['elevation'] for r in data['results']]

        print("Elevations:", elevs)

        # Reshape flat list into 5x5 elevation grid
        grid = np.array(elevs).reshape((5, 5))

        print("DEM Grid Shape:", grid.shape)
        print("DEM Grid Min  :", grid.min())
        print("DEM Grid Max  :", grid.max())

        # Normalize elevation values to 0-255 for image conversion
        if grid.max() != grid.min():
            grid = (grid - grid.min()) / (grid.max() - grid.min()) * 255
        else:
            grid = np.ones((5, 5)) * 127

        # Resize 5x5 grid to model input size and save as image
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
        print("=============================================\n")
        return None, 0


# =========================
# 10 DAY WEATHER
# =========================

def get_10day_weather(lat, lon):

    # Fetch past 10 days rainfall and temperature from Open-Meteo archive API
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&past_days=10&daily=temperature_2m_mean,precipitation_sum&timezone=auto"

    print("\n================ 10 DAY WEATHER ================")
    print("URL:", url)

    try:

        response = requests.get(url)
        data = response.json()

        print("Status code:", response.status_code)
        print("Weather keys:", data.keys())

        rain_list = data["daily"]["precipitation_sum"]
        temp_list = data["daily"]["temperature_2m_mean"]

        # Calculate average temperature and total rainfall over 10 days
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
        print("================================================\n")

        # Return zeros if weather fetch fails
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
        print("Request method:", request.method)
        print("POST data      :", dict(request.POST))

        # Get latitude and longitude from POST request
        lat = float(request.POST["latitude"])
        lon = float(request.POST["longitude"])

        print("Latitude  :", lat)
        print("Longitude :", lon)

        # Download satellite image and DEM elevation data for the location
        sat_file = download_satellite(lat, lon)
        dem_file, avg_elev = download_dem_grid(lat, lon)

        sat_p = os.path.join(settings.MEDIA_ROOT, sat_file)
        dem_p = os.path.join(settings.MEDIA_ROOT, dem_file) if dem_file else sat_p

        print("\n📁 File paths")
        print("Satellite path:", sat_p)
        print("DEM path      :", dem_p)
        print("Satellite exists:", os.path.exists(sat_p))
        print("DEM exists      :", os.path.exists(dem_p))

        # Load both images and expand dims to create batch of 1 for model input
        sat_in = np.expand_dims(load_image_from_disk(sat_p), axis=0)
        dem_in = np.expand_dims(load_image_from_disk(dem_p, dem=True), axis=0)

        print("\n📦 Model input arrays")
        print("sat_in shape:", sat_in.shape)
        print("dem_in shape:", dem_in.shape)
        print("sat_in min/max:", sat_in.min(), sat_in.max())
        print("dem_in min/max:", dem_in.min(), dem_in.max())

        # Run ML model prediction with satellite and DEM inputs
        pred = model.predict([sat_in, dem_in], verbose=0)
        prob = float(pred[0][0])

        print("\n🤖 Model prediction")
        print("Raw prediction array:", pred)
        print("Probability value   :", prob)

        # Classify as Landslide Prone if probability >= 50%
        ml_res = "Landslide Prone" if prob >= 0.5 else "Safe Area"

        print("Prediction label    :", ml_res)

        # Fetch current weather data from OpenWeatherMap
        w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"

        print("\n================ CURRENT WEATHER ================")
        print("Weather URL:", w_url)

        w_response = requests.get(w_url)
        w_json = w_response.json()

        print("Status code :", w_response.status_code)
        print("Weather JSON:", w_json)

        current_weather = {
            "temp": w_json["main"]["temp"],
            "humidity": w_json["main"]["humidity"],
            "rain": w_json.get("rain", {}).get("1h", 0),
            "wind": w_json["wind"]["speed"]
        }

        print("Parsed current weather:", current_weather)
        print("================================================\n")

        # Get 10 day historical rainfall and temperature
        history = get_10day_weather(lat, lon)

        # Generate AI risk analysis using Gemini
        try:
            prompt = f"""
Landslide Risk Analysis

Location: {lat},{lon}

Prediction: {ml_res}

Temperature: {current_weather['temp']}

Humidity: {current_weather['humidity']}

10 Day Rainfall: {history['total_rain']} mm
"""
            print("\n================ GEMINI REQUEST ================")
            print("Prompt:")
            print(prompt)

            ai_txt = gemini_model.generate_content(prompt).text

            print("✅ Gemini response received")
            print("AI Text:", ai_txt[:500])
            print("===============================================\n")

        except Exception as e:
            print("❌ Gemini Error:", e)

            # Fallback manual analysis if Gemini fails
            ai_txt = f"""
Manual Analysis

Prediction: {ml_res}

10 Day Rainfall: {history['total_rain']} mm

Higher rainfall increases landslide risk.
"""

        # Build final response data
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

        print("\n================ FINAL RESPONSE ================")
        print(response_data)
        print("================================================")
        print("================ LANDSLIDE PREDICTION END =================\n\n")

        return JsonResponse(response_data)

    except Exception as e:

        print("\n❌ EXCEPTION OCCURRED")
        print(traceback.format_exc())

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })