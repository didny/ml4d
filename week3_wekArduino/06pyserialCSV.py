"""
Send CSV from Serial port to Wekinator Input 

"""
import pyglet

import serial

import argparse
import math
from threading import Thread

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from pyglet.window import key

from wekinator import Wekinator 

class Window(pyglet.window.Window):	


	##Arduino Serial port setting.
	#serialport = serial.Serial('/dev/cu.usbmodem1411') ##for Mac
	#serialport = serial.Serial('/dev/ttyACM0')  ##for Raspberry Pi
	serialport = serial.Serial("Com93")

	readValues = [0,0,0]

        
	#initialize method
	def __init__(self,*args, **kwargs):
		super().__init__(width=512, height=512,caption="02pyserialCSV.py",
								fullscreen=False,visible=True,resizable=False)
		## initialize a label with text
		## https://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/api/pyglet/text/pyglet.text.Label.html
		self.label = pyglet.text.Label('HOWDY',  font_name='Times New Roman',
								font_size=36,
								x=self.width//2, y=self.height//2,
								anchor_x='center', anchor_y='center')

		## setup OSC client to Wekinator localhost port 6448 
		##ToDo: move this to wekinator.py
		self.wek_input = udp_client.SimpleUDPClient(args[0].ip, 6448) 

		### set an update function at an interval of 1/60 sec
		pyglet.clock.schedule_interval(self.update, 1/60.0)
	
	def update(self,dt,):
			
		values = self.read_csv_serial()
		label.text = "({:.2f},{:.2f},{:.2f})".format(values[0],values[1],values[2])
		wek_send_message("/wek/inputs",values)

	#drawing method 
	def on_draw(self):
		self.clear()
		self.label.draw() # draw the label

	def read_csv_serial(self):
		str = self.serialport.readline().decode().strip('\r\n')
		print("Serial:{}".format(str))
		values = str.split(",")
		values = [float(i) for i in values]
		return values

	"""
  
	sending message to wekinator input.
	addr: contains OSC address such as "/wek/outputs"
	args: a value or list of values to be sent by OSC message
	"""

	def wek_send_message(addr, args):
		print("Address: {} {}".format(len(args),",".join(str(x) for x in args)))
		# msg = osc_message_builder.OscMessageBuilder(address="/wek/inputs")
		# # Add 3 messages in the bundle, each with more arguments.

		self.wek_input.send_message("/wek/inputs", args)
	
	"""
	this function is called(dispatched) when the program received 
	message from wekinator.
	addr: contains OSC address such as "/wek/outputs"
	*args: list of values sent by OSC message
	"""
	def on_wekinator_message(self, addr, *args):
		## print out incoming message
		print("Address: {} {}".format(addr,",".join(str(x) for x in args)))

		## assign first value as a hand indexes (0:rock 1:paper 2:scissors 3:none)
		## hand_idx variable is a global variable, changes made here will be applied 
		## to the entire program.
		if(len(args) == 3):
			self.rgbLedValues = [args[0],args[1],args[2]]

		## print out received hand.
		print("RGB: ({},{},{})".format(self.rgbLedValues[0],self.rgbLedValues[1],self.rgbLedValues[2]))
	


"""
  main routine to initialize the program

"""
if __name__ == "__main__":
  """
   checking command line options here.
   you can specify ip address and port number from 
   command line by adding "arguments" 

   python ****.py --ip "127.0.0.1" --port 12000 

  """ 
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=12000, help="The port to listen on")
  args = parser.parse_args()


  ### initialize an OSC server to receive messages from Wekinator.
  #server = Wekinator(args.ip,args.port,wek_message_handler)
  ##create window
  window = Window(args, width=640, height=480)

  ### start pyglet app
  pyglet.app.run()