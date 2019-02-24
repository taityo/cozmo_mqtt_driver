import json
import time
import base64

from PIL import Image
import paho.mqtt.client as mqtt


class CozmoClient:
  def __init__(self, host='localhost', port=1883):
    # instance valiable
    self.host = host
    self.port = port
    
    # callback valiable
    self.callback_lift = None
    self.callback_head = None
    self.callback_saytext = None
    self.callback_camera = None

    ### Subscriber
    
    # lift subscriber
    self.lift_sub = mqtt.Client()
    self.lift_sub.on_connect = self.on_connect_lift
    self.lift_sub.on_message = self.on_message_lift

    # head subscriber
    self.head_sub = mqtt.Client()
    self.head_sub.on_connect = self.on_connect_head
    self.head_sub.on_message = self.on_message_head
    
    # say_text subscriber
    self.saytext_sub = mqtt.Client()
    self.saytext_sub.on_connect = self.on_connect_saytext
    self.saytext_sub.on_message = self.on_message_saytext
     
    # camera subscriber
    self.camera_sub = mqtt.Client()
    self.camera_sub.on_connect = self.on_connect_camera
    self.camera_sub.on_message = self.on_message_camera
  
 
    ### Publisher
    self.lift_pub = mqtt.Client() # lift publisher
    self.head_pub = mqtt.Client() # head publisher
    self.saytext_pub = mqtt.Client() # saytext publisher
    
  def run(self):
    ### Subscriber
     
    # lift subscriber
    self.lift_sub.connect_async(self.host, self.port, keepalive=60)
    self.lift_sub.loop_start()

    # head subscriber
    self.head_sub.connect_async(self.host, self.port, keepalive=60)
    self.head_sub.loop_start()
     
    # say_text subscriber
    self.saytext_sub.connect_async(self.host, self.port, keepalive=60)
    self.saytext_sub.loop_start()
    
    # camera subscriber
    self.camera_sub.connect_async(self.host, self.port, keepalive=60)
    self.camera_sub.loop_start()


    ### Publisher

    # lift publisher
    self.lift_pub.connect_async(self.host, self.port, keepalive=60)
    self.lift_pub.loop_start()

    # head publisher
    self.head_pub.connect_async(self.host, self.port, keepalive=60)
    self.head_pub.loop_start()

    # saytext publisher
    self.saytext_pub.connect_async(self.host, self.port, keepalive=60)
    self.saytext_pub.loop_start()
    
  ### Subscriber Callback Function

  # lift function
  def on_connect_lift(self, client, userdate, flags, respons_code):
    self.lift_sub.subscribe('/lift_pos')
    print('Connected lift_sub !!')

  def on_message_lift(self, client, userdata, msg):
    print('Subscribed lift_sub !!')

    lift_pos = json.loads(msg.payload)
    if self.callback_lift != None:
      self.callback_lift(lift_pos)

  # head function
  def on_connect_head(self, client, userdate, flags, respons_code):
    self.head_sub.subscribe('/head_angle')
    print('Connected head_sub !!')

  def on_message_head(self, client, userdata, msg):
    print('Subscribed head_sub !!')

    head_angle = json.loads(msg.payload)
    if self.callback_head != None:
      self.callback_head(head_angle)

  # saytext function
  def on_connect_saytext(self, client, userdate, flags, respons_code):
    self.saytext_sub.subscribe('/saying_now')
    print('Connected saytext !!')

  def on_message_saytext(self, client, userdata, msg):
    print('Subscribed saytext_sub !!')

    say_text = json.loads(msg.payload)
    if self.callback_saytext != None:
      self.callback_saytext(say_text)

  # camera function
  def on_connect_camera(self, client, userdate, flags, respons_code):
    self.camera_sub.subscribe('/camera_image')
    print('Connected camera !!')

  def on_message_camera(self, client, userdata, msg):

    camera_image = json.loads(msg.payload)

    ### Image Decode
   
    raw_image = camera_image['raw_image']
    # str -> base64
    bai_image = raw_image.encode('utf-8')
    # base64 -> bainary
    b642bai_img = base64.b64decode(bai_image)
    # bainary -> pil
    pil_img = Image.frombytes('RGB', (320,240), b642bai_img)
    #pil_img.show()

    if self.callback_camera != None:
      self.callback_camera(pil_img)

    print('Subscribed camera_sub !!')

  ### Publisher Function
 
  def publish_move_lift(self, speed):
    
    move_lift = {
      'speed': speed
    }
    
    # dict -> str on json & publish
    self.lift_pub.publish('/move_lift', json.dumps(move_lift))
    print('Publish lift_pub')

  def publish_move_head(self, speed):
    
    move_head = {
      'speed': speed
    }
    
    # dict -> str on json & publish
    self.head_pub.publish('/move_head', json.dumps(move_head))
    print('Publish head_pub')

  def publish_say_text(self, text, volume=1):
    
    say_text = {
      'text': text,
      'volume': volume
    }
    
    # dict -> str on json & publish
    self.head_pub.publish('/say_text', json.dumps(say_text))
    print('Publish saytext_pub')


num = 0.1
i = 0

def func(p):

  print(p)
    

if __name__ == '__main__':

  cozmo_client = CozmoClient()
  
  # callback function
  cozmo_client.callback_camera = func
  #cozmo_client.callback_saytext = func

  cozmo_client.run()
  while True:
    #cozmo_client.publish_say_text("this is test")
    i = i + 1
    print('i :' + str(i))

    time.sleep(1)





