from datetime import datetime
import time


class cli:
    def __init__(self, speed=1, debug=False):
        self.speed = speed
        self.last_timestamp = time.time()
        self.debug = debug
        self.initialized = True

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
        if not self.initialized:
            print(f"[ERR] Glaceon Not Initialized!")
            return

        # split the tag and message
        tag_text = f"{tag}"
        message_text = message

        # fade the tag colors
        if tag == "INFO":
            tag_text = self.fade(tag_text, (148, 0, 211), (0, 191, 255))
        elif tag == "WARNING":
            tag_text = self.fade(tag_text, (255, 215, 0), (255, 69, 0))
        elif tag == "ERROR":
            tag_text = self.fade(tag_text, (255, 0, 0), (128, 0, 0))
        elif tag == "SUCCESS":
            tag_text = self.fade(tag, (0, 255, 0), (255, 255, 255))
        elif tag == "DEBUG":
            if not self.debug:
                return
            tag_text = self.fade(tag_text, (0, 0, 255), (0, 191, 255))

        # get the current timestamp
        current_time = time.time()
        time_elapsed = current_time - self.last_timestamp
        self.last_timestamp = current_time

        # delay the output based on the specified speed
        time.sleep(max(1 / self.speed - time_elapsed, 0))

        # print the timestamp, tag, and message
        timestamp = self.getTimestamp()
        print(f"{timestamp} [{tag_text}] {message_text}")
