import platform
import time
from typing import Optional, Tuple

import numpy as np
import pygetwindow

try:
    import bettercam
except Exception:
    bettercam = None

try:
    import mss
except Exception:
    mss = None

# Could be do with
# from config import *
# But we are writing it out for clarity for new devs
from config import screenShotHeight, screenShotWidth


class _MSSCamera:
    """Lightweight screenshot helper for non-Windows platforms."""

    def __init__(self, region: Tuple[int, int, int, int]):
        if mss is None:
            raise ImportError(
                "mss is required for Linux/macOS captures. Install it via `pip install mss`."
            )
        self._region = {
            "left": region[0],
            "top": region[1],
            "width": region[2] - region[0],
            "height": region[3] - region[1],
        }
        self._sct = mss.mss()

    def start(self, target_fps: int = 120, video_mode: bool = True):
        # MSS has no explicit start, but we mirror the Windows API for compatibility
        return self

    def stop(self):
        self._sct.close()

    def get_latest_frame(self):
        frame = np.array(self._sct.grab(self._region))
        return frame


def gameSelection() -> Optional[Tuple[object, int, Optional[int]]]:
    # Selecting the correct game window
    try:
        videoGameWindows = pygetwindow.getAllWindows()
        print("=== All Windows ===")
        for index, window in enumerate(videoGameWindows):
            # only output the window if it has a meaningful title
            if window.title != "":
                print("[{}]: {}".format(index, window.title))
        # have the user select the window they want
        try:
            userInput = int(input(
                "Please enter the number corresponding to the window you'd like to select: "))
        except ValueError:
            print("You didn't enter a valid number. Please try again.")
            return None
        # "save" that window as the chosen window for the rest of the script
        videoGameWindow = videoGameWindows[userInput]
    except Exception as e:
        print("Failed to select game window: {}".format(e))
        return None

    # Activate that Window
    activationRetries = 30
    activationSuccess = False
    while (activationRetries > 0):
        try:
            videoGameWindow.activate()
            activationSuccess = True
            break
        except pygetwindow.PyGetWindowException as we:
            print("Failed to activate game window: {}".format(str(we)))
            print("Trying again... (you should switch to the game now)")
        except Exception as e:
            print("Failed to activate game window: {}".format(str(e)))
            print("Read the relevant restrictions here: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow")
            activationSuccess = False
            activationRetries = 0
            break
        # wait a little bit before the next try
        time.sleep(3.0)
        activationRetries = activationRetries - 1
    # if we failed to activate the window then we'll be unable to send input to it
    # so just exit the script now
    if activationSuccess is False:
        return None
    print("Successfully activated the game window...")

    # Starting screenshoting engine
    left = ((videoGameWindow.left + videoGameWindow.right) // 2) - (screenShotWidth // 2)
    top = videoGameWindow.top + (videoGameWindow.height - screenShotHeight) // 2
    right, bottom = left + screenShotWidth, top + screenShotHeight

    region: tuple = (left, top, right, bottom)

    # Calculating the center Autoaim box
    cWidth: int = screenShotWidth // 2
    cHeight: int = screenShotHeight // 2

    print(region)

    if platform.system() == "Windows":
        if bettercam is None:
            print("bettercam failed to import. Please ensure it is installed on Windows.")
            return None
        camera = bettercam.create(region=region, output_color="BGRA", max_buffer_len=512)
        if camera is None:
            print("Your Camera Failed! Ask @Wonder for help in our Discord in the #ai-aimbot channel ONLY: https://discord.gg/rootkitorg")
            return None
        camera.start(target_fps=120, video_mode=True)
    else:
        camera = _MSSCamera(region)
        camera.start(target_fps=120, video_mode=True)

    return camera, cWidth, cHeight
