import cozmo
import paho.mqtt.client as mqtt

class CozmoDriver:

  def init(robot):
    this.robot = robot
    pass

  def run():
    pass

import asyncio
import cozmo

async def cozmo_program(robot: cozmo.robot.Robot):
  coz = CozmoDriver(robot)
  coz.run()

if __name__ == '__main__':
  cozmo.run_program(cozmo_program)
  
