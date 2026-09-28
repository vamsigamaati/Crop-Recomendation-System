import os
import urllib.request

def download_dataset():
    url = "https://raw.githubusercontent.com/arzzahid66/Optimizing_Agricultural_Production/master/Crop_recommendation.csv"
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    dest_path = os.path.join(data_dir, "Crop_recommendation.csv")
    
    print(f"Downloading dataset from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Dataset successfully downloaded and saved to: {dest_path}")
        print(f"File size: {os.path.getsize(dest_path)} bytes")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        raise e

if __name__ == "__main__":
    download_dataset()
