import subprocess
import os

def download_model():
    
    url = "https://dl.fbaipublicfiles.com/mms/tts/eng.tar.gz"
    output_file = "eng.tar.gz"
    data_directory = "data"

    os.makedirs(data_directory, exist_ok=True)

    try:
        # Download the file using curl
        subprocess.run(["curl", url, "--output", output_file], check=True)

        # Extract the tar.gz file into the data directory
        subprocess.run(["tar", "-xzf", output_file, "-C", data_directory], check=True)

        print("Model downloaded and extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


download_model()