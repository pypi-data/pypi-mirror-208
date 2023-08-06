"""
Home to ResumeWatcher.

ResumeWatcher is a daemon thread that will wait for a resume event.
The resume event indicates that the OS has resumed from a standby or hibernation.
"""

import os
import threading
import uuid

import win32api
import win32con
import win32gui

"""
Notifies applications that the system is resuming from sleep or hibernation.
This event is delivered every time the system resumes and does not indicate whether a user is present.
"""
PBT_APMRESUMEAUTOMATIC = 0x12

if os.name != "nt":
    raise NotImplementedError(
        "The ResumeWatcher only works on Windows.. feel free to PR similar functionality for other OS's!"
    )

# Define the window class
class ResumeWatcher(threading.Thread):
    """
    This thread will run in the background and wait for a resume event:
    msg == WM_POWERBROADCAST and wparam == PBT_APMRESUMEAUTOMATIC.

    Periodically check is_resumed() to see if the system has resumed from a standby or hibernation.
    """

    def __init__(self):
        """
        Initializer, sets up the internal event and starts the daemon thread
        """
        self._event = threading.Event()
        threading.Thread.__init__(self, daemon=True)
        self.start()

    def run(self):
        """
        Ran inside the thread. Will setup the window and wait for the resume event.
        """
        class_name = __class__.__name__ + uuid.uuid4().hex
        wnd_class = win32gui.WNDCLASS()
        wnd_class.lpfnWndProc = self._wnd_proc
        wnd_class.lpszClassName = class_name
        win32gui.RegisterClass(wnd_class)

        # Create a window
        self.hwnd = win32gui.CreateWindow(
            class_name,
            class_name,
            win32con.WS_DISABLED,
            0,
            0,
            0,
            0,
            0,
            0,
            win32api.GetModuleHandle(None),
            None,
        )

        # This call will hang until exit is sent
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """
        Callback function called by the OS for WM_ messages sent to the window
        """
        if msg == win32con.WM_POWERBROADCAST and wparam == PBT_APMRESUMEAUTOMATIC:
            # We have gone through some sort of resume (hibernate or sleep/resume)
            self._event.set()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def is_resumed(self) -> bool:
        """
        Called to check if the OS has sent a resume event
        """
        return self._event.is_set()
