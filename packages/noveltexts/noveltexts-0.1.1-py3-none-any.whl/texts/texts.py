import speech_recognition as sr

def voice_command():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("tell now...")
        audio = r.listen(source)
        print('listening completed')

    try:
        text = r.recognize_google(audio)
        print("Transcription:")
        return (text)
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error: {e}")


if __name__ =='__main__':
  print(voice_command())
