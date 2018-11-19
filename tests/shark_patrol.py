from tello import *

start()
takeoff() 

initial_tof = get_tof()

for j in range(4):
  clockwise(90)
  for i in range(5):
    forward(20)
    result = get_tof()
    if result < initial_tof - 100: 
      flip_forward()
    print(result)

land() 
