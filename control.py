import pyautogui
from collections import deque
import time

class HeadMouse:
    def __init__(self, cfg):
        self.cfg = cfg
        self.x_queue = deque(maxlen=cfg.SMOOTHING)
        self.y_queue = deque(maxlen=cfg.SMOOTHING)

        self.left_start = None
        self.right_start = None
        self.last_left_click = 0
        self.last_right_click = 0

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.005

    def move(self, x, y):
        cur_x, cur_y = pyautogui.position()

        self.x_queue.append(x)
        self.y_queue.append(y)

        x_avg = sum(self.x_queue)/len(self.x_queue)
        y_avg = sum(self.y_queue)/len(self.y_queue)

        dx = (x - x_avg) * self.cfg.SENS_X
        dy = (y - y_avg) * self.cfg.SENS_Y

        if abs(dx) < self.cfg.MOVE_THRESHOLD:
            dx = 0
        if abs(dy) < self.cfg.MOVE_THRESHOLD:
            dy = 0

        new_x = max(0, cur_x + dx)
        new_y = max(0, cur_y + dy)

        pyautogui.moveTo(new_x, new_y)
        return new_x, new_y

    def handle_click(self, left_ratio, right_ratio):
        now = time.time()

        # LEFT
        if left_ratio > self.cfg.BLINK_THRESHOLD:
            if self.left_start is None:
                self.left_start = now
            elif now - self.left_start >= self.cfg.CLICK_TIME:
                if now - self.last_left_click >= self.cfg.CLICK_DELAY:
                    pyautogui.click(button='left')
                    self.last_left_click = now
                    self.left_start = None
                    return "LEFT"
        else:
            self.left_start = None

        # RIGHT
        if right_ratio > self.cfg.BLINK_THRESHOLD:
            if self.right_start is None:
                self.right_start = now
            elif now - self.right_start >= self.cfg.CLICK_TIME:
                if now - self.last_right_click >= self.cfg.CLICK_DELAY:
                    pyautogui.click(button='right')
                    self.last_right_click = now
                    self.right_start = None
                    return "RIGHT"
        else:
            self.right_start = None

        return None