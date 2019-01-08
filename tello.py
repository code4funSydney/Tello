import socket
import re
import sys
import cv2
import threading
import sys
import copy
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image
import platform
import time
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

# This is a pointer to the module object instance itself
this = sys.modules[__name__]

this.sock = None
this.mon = False

tello_ip = '192.168.10.1'
tello_port = 8889
tello_addr = (tello_ip, tello_port)

def send(command):
  """Sends a command to the drone.
  Arguments:
      str: command -- The command to send to the drone
  """
  if this.sock is None:
      raise RuntimeError("Call start() first!")
  try:
    this.sock.sendto(command.encode(), tello_addr)
  except Exception as e:
    # TODO: Should we throw an exception?
    print("Error sending command to drone:\n\t" + str(e))

def receive():
  """Waits for and returns the response from the drone.
  Returns:
      str: The response from the drone
  """
  try:
    response, ip_address = this.sock.recvfrom(128)
    response = response.decode(encoding='utf-8')
    return response
  except Exception as e:
    # TODO: Should we throw an exception?
    print("Error receiving response from drone:\n\t" + str(e))

def send_and_wait(command):
    """Sends a command to the drone and waits for the response.

    Arguments:
        str: command -- The command to send to the drone.

    Returns:
        str: The response from the drone.
    """
    try:
        send(command)
        return receive()
    except KeyboardInterrupt:
        # TODO: Test this works
        # Kill switch in case of emergency
        print("Interrupted. Attempting to shut off motors...")
        send("emergency")
        sys.exit(0)

def start():
    """Tell the drone to start receiving commands."""
    if (this.sock is None):
        this.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        this.sock.bind(('', 9000))
    response = send_and_wait("command")
    if response != "ok":
       raise RuntimeError("Drone failed to enter SDK mode.")

def takeoff():
    """Sends the command to the drone to take off."""
    response = send_and_wait("takeoff")
    if response != "ok":
        raise RuntimeError("Drone failed to take off.")

def land():
    """Sends the command to the drone to land."""
    response = send_and_wait("land")

def get_tof():
    """Gets the TOF sensor value
    Returns:
        int: The TOF value in millimeters
    """
    response = send_and_wait("tof?")
    # Remove trailing whitespace from response
    response = response.strip()
    # Check the response matches what we expected
    match = re.match(r'^[0-9]*mm$', response)
    assert match, "Drone did not respond with a value in millimeters."
    return int(response[:-2])

def get_battery():
    """Gets the battery value
    Returns:
        int: The percentage of battery remaining
    """
    response = send_and_wait("battery?")
    # Remove trailing whitespace from response
    response = response.strip()
    # Check the response matches what we expected
    match = re.match(r'^[0-9]*mm$', response)
    assert match, "Drone did not respond with an integer value."
    return int(response)

def get_mission_pad():
    """Gets the current marker id
    Returns:
        int: The current marker id
    """
    if not this.mon:
        send_and_wait("mon")
        this.mon = True
    response = send_and_wait("mid?")
    # Remove trailing whitespace from response
    response = response.strip()
    # Check the response matches what we expected
    match = re.match(r'^[0-9]*$', response)
    assert match, "Drone did not respond with a marker id."
    return int(response)


def forward(centimeters):
    """Moves forward by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move forward by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('forward %d' % (centimeters))

def backward(centimeters):
    """Moves backward by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move backward by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('back %d' % (centimeters))

def left(centimeters):
    """Moves to the left by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move left by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('left %d' % (centimeters))

def right(centimeters):
    """Moves to the right by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move right by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('right %d' % (centimeters))

def up(centimeters):
    """Moves up by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move up by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('up %d' % (centimeters))

def down(centimeters):
    """Moves down by a set distance

    Arguments:
        int: centimeters (20-500) -- The distance to move down by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('down %d' % (centimeters))

def anticlockwise(degrees):
    """Rotate anti-clockwise

    Arguments:
        int: degrees (1-360) -- Number of degrees to turn by
    """
    assert(degrees > 0), "Valid range for degrees to turn by is 1-360"
    assert(degrees <= 360), "Valid range for degrees to turn by is 1-360"
    response = send_and_wait('ccw %d' % (degrees))

def clockwise(degrees):
    """Rotate clockwise

    Arguments:
        int: degrees (1-360) -- Number of degrees to turn by
    """
    assert(degrees > 0), "Valid range for degrees to turn by is 1-360"
    assert(degrees <= 360), "Valid range for degrees to turn by is 1-360"
    response = send_and_wait('cw %d' % (degrees))

def flip_forward():
    """Performs a forward flip."""
    # TODO: Assert battery is high enough to perform flip before attempting
    send_and_wait("flip f")


class VideoStream:
    started = False
    thread = None
    kill_event = None
    frame = None
    windows = {}
    screen = None

    def start(self):
        if not self.started:
            send_and_wait("streamon")
            self.kill_event = threading.Event()
            if platform.system() == "Darwin":
                self.thread = threading.Thread(target=self._pygame_video_loop, args=[self.kill_event])
                pygame.init()
                self.screen = pygame.display.set_mode([640, 480])
                pygame.display.set_caption("Video Stream")
            else:
                self.thread = threading.Thread(target=self._tkinter_video_loop, args=[self.kill_event])
            self.thread.start()
            self.started = True


    def _tkinter_video_loop(self, stop_event):
        root = tk.Tk()
        root.title("Video Stream")
        root.protocol("WM_DELETE_WINDOW", lambda: stop_event.set())
        cap = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)
        label = None
        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret == True:
                self.frame = frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = ImageTk.PhotoImage(img)
                if label is None:
                    label = tk.Label(image=img)
                    label.image = img
                    label.pack()
                else:
                    label.configure(image=img)
                    label.image = img
            root.update()
        root.destroy()

    def _pygame_video_loop(self, stop_event):
        cap = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)
        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret == True:
                self.frame = frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.rot90(frame)
                frame = np.flip(frame, 0)
                frame = pygame.surfarray.make_surface(frame)
                self.screen.blit(frame, (0,0))
                pygame.display.update()
        pygame.quit()


    def stop(self):
        if self.started:
            self.kill_event.set()
            self.started = False
            send_and_wait("streamoff")

    def get_frame(self):
        return copy.deepcopy(self.frame)

    def __del__(self):
        if self.started:
            self.stop()

# Global video instance
_video = None

def start_video():
    global _video
    if _video is None:
        _video = VideoStream()
    _video.start()

def stop_video():
    global _video
    if _video is not None:
        _video.stop()
        del _video
        _video = None

def get_video_frame():
    global _video
    if _video is not None:
        return _video.get_frame()

