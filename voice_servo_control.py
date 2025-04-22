import serial
import time
import speech_recognition as sr
import serial.tools.list_ports
import pygame

# -------------------------
# CONFIGURATION SECTION
# -------------------------

keywords = ['baby', 'young', 'elder', 'demise']
DEFAULT_PORT = 'COM9'  # Change if necessary

music_files = {
    'baby': 'baby.wav',
    'young': 'young.wav',
    'elder': 'elder.wav',
    'demise': 'death.wav'
}

def detect_keyword(text):
    text = text.lower()
    for i, word in enumerate(keywords):
        if word in text:
            return i, word
    return -1, None

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'UNO R4' in port.description:
            return port.device
    return None

def play_music(keyword):
    file = music_files.get(keyword)
    if file:
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except Exception as e:
            print(f"Error playing music for '{keyword}': {e}")

def stop_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

# -------------------------
# MAIN SCRIPT STARTS HERE
# -------------------------

port_name = find_arduino_port() or DEFAULT_PORT
try:
    arduino = serial.Serial(port_name, 9600, timeout=1)
    arduino.reset_input_buffer()
    print(f"Connected to Arduino on {port_name}")
    time.sleep(2)
except Exception as e:
    print(f"Could not connect to Arduino on {port_name}: {e}")
    exit(1)

recognizer = sr.Recognizer()
mic = sr.Microphone()

pygame.mixer.init()

print("Voice detection system ready...")
print(f"Listening for: {', '.join(keywords)}")

current_stop = 0  # Start position
current_music = None  # Track which music is currently playing

try:
    while True:
        print("Listening for keyword...")

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Processing audio...")
                spoken_text = recognizer.recognize_google(audio)
                print("You said:", spoken_text)

                index, keyword = detect_keyword(spoken_text)
                if index != -1 and keyword:
                    print(f"Detected keyword: '{keyword}' → Moving to stop {index}")
                    command = f"MOVE:{current_stop}:{index}\n"
                    arduino.write(command.encode())
                    current_stop = index

                    if current_music != keyword:
                        stop_music()
                        play_music(keyword)
                        current_music = keyword
                else:
                    print("No keyword detected.")

            except sr.WaitTimeoutError:
                print("No speech detected (timeout).")
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError as e:
                print(f"Speech recognition API error: {e}")

        time.sleep(1)  # Wait briefly before restarting recognition

except KeyboardInterrupt:
    print("\nScript interrupted by user. Exiting.")
finally:
    stop_music()
    if arduino and arduino.is_open:
        arduino.close()
        print("Serial connection closed.")
