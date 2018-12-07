import socket
import re
import sys
import cv2
import threading
import sys

# This is a pointer to the module object instance itself
this = sys.modules[__name__]

this.sock = None

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

    def start(self):
        if not self.started:
            send_and_wait("streamon")
            self.kill_event = threading.Event()
            self.thread = threading.Thread(target=self._work, args=[self.kill_event])
            self.thread.start()
            self.started = True

    def _work(self, stop_event):
        cap = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)
        #cap = cv2.VideoCapture(0) 
        while not stop_event.is_set():
            ret, frame = cap.read()
            cv2.imshow('Video', frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        cap.release()

    def stop(self):
        if self.started:
            self.kill_event.set()
            self.thread.join()
            self.started = False
            send_and_wait("streamoff")

    def __del__(self):
        if self.started:
            self.stop()

