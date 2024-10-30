import speech_recognition as sr

def live_transcribe():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)
        print("You can start speaking now...")

        while True:
            try:
                # Capture audio from the microphone
                audio = recognizer.listen(source)

                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                print(f"Transcription: {text}")

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    live_transcribe()