from kaggle.api.kaggle_api_extended import KaggleApi
import os

api = KaggleApi()
api.authenticate()

os.makedirs("data/raw", exist_ok=True)

api.dataset_download_files(
    "mlg-ulb/creditcardfraud",
    path="data/raw",
    unzip=True
)

print("Download done!")