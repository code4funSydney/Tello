import socket
import re

tello_ip = '192.168.10.1'
tello_port = 8889
tello_addr = (tello_ip, tello_port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9000))

def send(command):
  """Sends a command to the drone.
  Arguments:
      str: command -- The command to send to the drone
  """
  try:
    sock.sendto(command.encode(), tello_addr)
  except Exception as e:
    # TODO: Should we throw an exception?
    print("Error sending command to drone:\n\t" + str(e))

def receive():
  """Waits for and returns the response from the drone.
  Returns:
      str: The response from the drone
  """
  try:
    response, ip_address = sock.recvfrom(128)
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
    send(command)
    return receive()

def start():
    """Tell the drone to start receiving commands."""
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
        int: centimeters (20-500) -- The distance to move foward by in centimeters
    """
    assert(centimeters >= 20), "Distance is less than 20cm (valid range is 20cm-500cm)."
    assert(centimeters <= 500), "Distance is more than 500cm (valid range is 20cm-500cm)."
    response = send_and_wait('forward %d' % (centimeters))

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



