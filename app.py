# main.py
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base64
import io
import numpy as np
import torch
from transformers import VitsTokenizer, VitsModel
import os
import scipy.io.wavfile as wavfile
import speech_recognition as sr
from logger import logging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Retrieve the token from the environment variable
access_token = os.getenv('HF_TOKEN')

# Load model and tokenizer
tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-eng", token=access_token)
model = VitsModel.from_pretrained("facebook/mms-tts-eng", token=access_token)

# Flag to control recording state
stop_recording_flag = False

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logging.info("Starting html code...")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/text-to-speech")
async def text_to_speech(data: dict):
    try:
        logging.info(f"data:{data} ")

        text = data.get("text")
        logging.info(f"Input text: {text}")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt")

        # Generate speech waveform
        with torch.no_grad():
            outputs = model(**inputs)

        # Extract and process the waveform
        waveform = outputs.waveform.squeeze()  # Remove extra dimensions

        # Scale to int16 range and convert to numpy array
        waveform_np = (waveform.numpy() * 32767).astype(np.int16)

        # Save to buffer
        buffer = io.BytesIO()
        wavfile.write(buffer, rate=model.config.sampling_rate, data=waveform_np)
        buffer.seek(0)

        # Convert to base64
        audio_base64 = base64.b64encode(buffer.read()).decode()

        return JSONResponse({"audio": audio_base64})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/transcribe")
async def live_transcribe(websocket: WebSocket):
    global stop_recording_flag  # Access the global stop flag
    await websocket.accept()

    logging.info("Initialize the recognizer")
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        logging.info("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)
        
        logging.info("You can start speaking now...")

        while True:
            # Check if stop flag is set, and break if it is
            if stop_recording_flag:
                await websocket.send_text("Recording stopped.")
                break

            try:
                # Capture audio from the microphone
                audio = recognizer.listen(source)

                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                logging.info(f"Transcription: {text}")

                # Check if the user wants to stop via voice command
                if "stop listening" in text.lower():
                    logging.info("Stopping transcription by voice command.")
                    stop_recording_flag = True  # Set stop flag

                # Send the transcription to the client unless stopping was triggered by voice command
                if not stop_recording_flag:
                    await websocket.send_text(text)

            except sr.UnknownValueError:
                await websocket.send_text(" ")
            except sr.RequestError as e:
                await websocket.send_text(f"Could not request results from Google Speech Recognition service; {e}")

@app.post("/stop-recording")
async def stop_recording():
    global stop_recording_flag
    stop_recording_flag = True  # Set the flag to stop recording
    return {"status": "Recording stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)