import time
import pyaudio
import wave
from audio_utils import voice_input
from openai_utils import generate_command_from_prompt
from webserver import start_webserver
from command_utils import broadcast_command, calculate_delay

# --- Automatischer Konversationsmodus ---
def conversation_loop():
    print("Starte automatischen NAO-Konversationsmodus...")
    while True:
        command = generate_command_from_prompt("")
        if command.get("human_turn", False) or command.get("end_conversation", False):
            print("API signalisiert: Wechsel zurück zum Menschen.")
            break
        target_nao = command.get("nextNao")
        if target_nao and target_nao in connected_clients:
            broadcast_command(command, target_client=connected_clients[target_nao])
        else:
            if connected_clients:
                default_client = list(connected_clients.values())[0]
                broadcast_command(command, target_client=default_client)
            else:
                print("Keine NAO verbunden!")
                break
        text = command.get("text", "")
        api_delay = command.get("delay", 0)
        # Falls kein sinnvoller Delay von der API kommt, berechne dynamisch:
        if api_delay < 5:
            delay = calculate_delay(text, min_delay=5)
        else:
            delay = api_delay
        print(f"Warte {delay} Sekunden, bis der NAO seine Antwort beendet hat...")
        time.sleep(delay)
    print("Automatischer Dialog beendet. Zurück zum menschlichen Input.")

# --- Gesprächsmanager (Wechsel zwischen menschlicher Eingabe und automatischem Modus) ---
def conversation_manager():
    while True:
        mode = input("Wähle Eingabemodus ('t' für Text, 'v' für Voice, 'exit' zum Beenden): ").strip().lower()
        if mode == "exit":
            break
        if mode == "v":
            prompt = voice_input()
        elif mode == "t":
            prompt = input("Gib deine Texteingabe ein: ")
        else:
            print("Ungültige Auswahl. Bitte 't' oder 'v' eingeben.")
            continue
        command = generate_command_from_prompt(prompt)
        target_nao = command.get("nextNao")
        if target_nao and target_nao in connected_clients:
            broadcast_command(command, target_client=connected_clients[target_nao])
        else:
            broadcast_command(command)
        conversation_loop()

# --- Main Block: Webserver im Hintergrund ---
if __name__ == '__main__':
    start_webserver()
    conversation_manager()
    cherrypy.engine.stop()
