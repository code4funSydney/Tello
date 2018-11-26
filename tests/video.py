from tello import *
import time

video = VideoStream()

video.start()

time.sleep(5)

video.stop()

