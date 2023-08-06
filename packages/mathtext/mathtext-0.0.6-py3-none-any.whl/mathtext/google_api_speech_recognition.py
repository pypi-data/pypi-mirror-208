import soundex

model = soundex.Soundex()

def sound_distance(a, b):
    return model.compare(a, b)

"""
def encode_text_sound(text):
    diff = gTTS(text=text, lang='en', slow=False)
    diff.save('temp_file.mp3')
    sound = AudioSegment.from_mp3("temp_file.mp3")
    sound.export("temp_file.wav", format="wav")
    r = sr.Recognizer()
    with sr.AudioFile('temp_file.wav') as source:
        audio_text = r.listen(source)
    try:
        text = r.recognize_google(audio_text)
     
    except:
        pass
    os.system('rm temp_file.wav')
    os.system('rm temp_file.mp3')

    return text

def sound_distance(a, b):
    diff_a = encode_text_sound(a)
    diff_b = encode_text_sound(b)
    return find_char_diff(diff_a, diff_b)
"""