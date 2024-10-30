import os
from huggingface_hub import login
import torch
from transformers import VitsTokenizer, VitsModel
import numpy as np
import scipy.io.wavfile as wavfile


# Retrieve the token from the environment variable
access_token = os.getenv('HF_TOKEN')



# Load model and tokenizer
tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-eng",token=access_token)
model = VitsModel.from_pretrained("facebook/mms-tts-eng",token=access_token)

# Input text for TTS
text = "Hello, this is a text-to-speech example using the Facebook MMS TTS model."

# Tokenize input text
inputs = tokenizer(text, return_tensors="pt")

# Generate speech waveform
with torch.no_grad():
    outputs = model(**inputs)

# Extract and process the waveform
waveform = outputs.waveform.squeeze()  # Remove extra dimensions

# Scale to int16 range and convert to numpy array
waveform_np = (waveform.numpy() * 32767).astype(np.int16)

# Save as .wav file
wavfile.write("output.wav", rate=model.config.sampling_rate, data=waveform_np)