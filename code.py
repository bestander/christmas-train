
import time
import os
import wifi
import ipaddress
import socketpool
import board
import digitalio
import microcontroller
import pwmio
from adafruit_httpserver import Server, Request, JSONResponse

class L298N:
    def __init__(self, ENA, IN1, IN2):
        self.IN1 = IN1
        self.IN2 = IN2
        self.pwm = ENA
        self.speed = 40000
        self.ismoving = False
        self.direction = 'STOP'
        self.time = 0
         
    def forward(self):
        self.IN1.value = True
        self.IN2.value = False
        self.ismoving =  True
        self.direction = 'FORWARD'
        
    def backward(self):
        self.IN1.value = False
        self.IN2.value = True
        self.ismoving = True
        self.direction = 'BACKWARD'
        
    def stop(self):
        self.IN1.value = False
        self.IN2.value = False
        self.ismoving = False
        self.Direction = 'STOP'
        
    def setSpeed(self, speed):
      #   self.pwm.frequency = 15000
        self.speed = speed
        # self.pwm.duty_cycle = speed
        
    def getSpeed(self):
        return self.speed
    
    def getDirection(self):
        return self.direction
    
    def run(self, direction):
        self.direction = direction
        if self.direction == 'FORWARD':
            self.forward()
        elif self.direction == 'BACKWARD':
            self.backward()
        elif self.direction == 'STOP':
            self.stop()
        else:
            pass
    
    def forwardFor(self, Time):
        self.time = Time
        self.forward()
        time.sleep(self.time)
        self.stop()
        
    def backwardFor(self, Time):
        self.time = Time
        self.backward()
        time.sleep(self.time)
        self.stop()
        
    def runFor(self, direction, Time):
        self.direction = direction
        self.time = Time
        if self.direction == 'FORWARD':
            self.forward()
            time.sleep(self.time)
            self.stop()
        elif self.direction == 'BACKWARD':
            self.backward()
            time.sleep(self.time)
            self.stop()
        elif self.direction == 'STOP':
            self.stop()
            time.sleep(self.time)
        else:
            pass
            
    def isMoving(self):
        if self.ismoving == True:
            print('True')
        elif self.ismoving == False:
            print('False')
        else:
            pass

#  connect to SSID
print("Connecting to WiFi")
ipv4 =  ipaddress.IPv4Address(os.getenv('IPV4_ADDRESS'))
netmask =  ipaddress.IPv4Address(os.getenv('IPV4_MASK'))
gateway =  ipaddress.IPv4Address(os.getenv('IPV4_GATEWAY'))
wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
print("Connected to WiFi")


pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

IN1 = digitalio.DigitalInOut(board.GP1)
IN1.direction = digitalio.Direction.OUTPUT
IN2 = digitalio.DigitalInOut(board.GP2)
IN2.direction = digitalio.Direction.OUTPUT
ENA = pwmio.PWMOut(board.GP10, frequency=50000)

motor1 = L298N(ENA, IN1, IN2)
motor1.setSpeed(60000)

@server.route("/")
def base(request: Request):
   motor1.forward()
   print("going forward")
   time.sleep(5)
   motor1.stop()
   temp = microcontroller.cpu.temperature
   led.value = not led.value
   return JSONResponse(request, {"success": "true12", "temp": temp})



server.serve_forever(str(wifi.radio.ipv4_address))