from slack import create_app
import speech_recognition as sr
from flask import redirect, request


app = create_app()

@app.route("/transcribe")
def transcribe():
    current_page = request.args.get('current_page', '')
    print(current_page)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        text_to_speech("Voice Assistance activated")
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        text = r.recognize_google(audio)
        if "play" in text.lower():
            return redirect('/play')
        elif "learn" in text.lower():
            return redirect('/learn')
        elif "home" in text.lower():
            return redirect('/')
        else:
            return redirect('/' + current_page)
    except:
        print("No commands")
        return redirect('/' + current_page)



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
