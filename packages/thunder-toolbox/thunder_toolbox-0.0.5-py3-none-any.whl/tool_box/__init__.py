import pyautogui
import time
from pyautogui import typewrite, press, write


class KeyBoardTools:

    @staticmethod
    def printer(text):
        return print(text)


    @staticmethod
    def spammer(text, count=0, freeze_time=3):
        time.sleep(freeze_time)
        for ctr in range(count):
            pyautogui.typewrite(text)
            pyautogui.press('enter')
        return "Spamming done!"
