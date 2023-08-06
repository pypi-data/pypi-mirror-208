from datetime import datetime
import time


class cli:

    def __init__(self, speed=None, debug=None):
        self.speed = speed
        self.last_timestamp = time.time()
        self.debug = debug
        self.initialized = speed is not None and debug is not None

    def getTimestamp(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        return f"[{current_time}]"

    def fade(self, text, start_color, end_color):
        fade_steps = 10
        r_step = (end_color[0] - start_color[0]) / fade_steps
        g_step = (end_color[1] - start_color[1]) / fade_steps
        b_step = (end_color[2] - start_color[2]) / fade_steps
        faded_text = ""
        r, g, b = start_color
        for letter in text:
            r += r_step
            g += g_step
            b += b_step
            faded_text += f"\033[38;2;{int(r)};{int(g)};{int(b)}m{letter}\033[0m"
        return faded_text

    def print(self, tag, message):

        timestamp = self.getTimestamp()
        inittag = self.fade("ERROR", (255, 0, 0), (128, 0, 0))

        if not self.initialized:
            if not self.debug:
                print(f"{timestamp} [{inittag}] Not initialized!")
                input()
                exit()
                return
            else:
                print(f"{timestamp} [{inittag}] Not initialized correctly!")
                return

        tag_text = f"{tag}"
        message_text = message

        if tag == "INFO":
            tag_text = self.fade(tag_text, (148, 0, 211), (0, 191, 255))
        elif tag == "WARNING":
            tag_text = self.fade(tag_text, (255, 215, 0), (255, 69, 0))
        elif tag == "ERROR":
            tag_text = self.fade(tag_text, (255, 0, 0), (128, 0, 0))
        elif tag == "SUCCESS":
            tag_text = self.fade(tag_text, (0, 255, 0), (255, 255, 255))
        elif tag == "DEBUG":
            if not self.debug:
                return
            tag_text = self.fade(tag_text, (0, 0, 255), (0, 191, 255))
        else:
            print(f"{timestamp} [{inittag}] Invalid Tag: {tag}")
            input()
            exit()
        current_time = datetime.now().strftime("%H:%M:%S")

        time_elapsed = time.time() - self.last_timestamp
        self.last_timestamp += max(1 / self.speed - time_elapsed, 0)

        print(f"{timestamp} [{tag_text}] {message_text}")