import os
import requests

MODEL_PATH = os.getenv("MODEL_PATH", "myapp/landslide_model_new.h5")
FILE_ID = "1u8TS_wI8WHlpmEcqNSeHQZDgAFT-_pTk"

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"✅ Model already exists at {MODEL_PATH}")
        return

    print(f"⬇️ Downloading model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    session = requests.Session()
    response = session.get(url, stream=True)

    # Handle Google Drive large file warning
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            url = f"https://drive.google.com/uc?export=download&confirm={value}&id={FILE_ID}"
            response = session.get(url, stream=True)
            break

    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

    print(f"✅ Model downloaded successfully: {MODEL_PATH}")

if __name__ == "__main__":
    download_model()
