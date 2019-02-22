import asyncio
import cozmo
from cozmoMqttDriver import CozmoDriver as Cozmo

def cozmo_program(robot: cozmo.robot.Robot):
  coz = Cozmo(robot)
  coz.run()
  

cozmo.run_program(cozmo_program)
