import os

MODEL_PATH = os.getenv("MODEL_PATH", "myapp/landslide_model_new.h5")
FILE_ID = "1u8TS_wI8WHlpmEcqNSeHQZDgAFT-_pTk"

def download_model():
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)
        if size > 10_000_000:
            print(f"✅ Model already exists at {MODEL_PATH} ({size // 1_000_000}MB)")
            return
        else:
            print(f"⚠️ Corrupted file ({size} bytes). Re-downloading...")
            os.remove(MODEL_PATH)

    print(f"⬇️ Downloading model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    import gdown
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, MODEL_PATH, quiet=False)

    size = os.path.getsize(MODEL_PATH)
    print(f"✅ Model downloaded: {MODEL_PATH} ({size // 1_000_000}MB)")

if __name__ == "__main__":
    download_model()
