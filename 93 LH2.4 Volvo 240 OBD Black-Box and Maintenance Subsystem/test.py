from machine import Pin,SPI,PWM
import utime
import framebuf
import utime
import os
import math

BL = 13  # Pins used for display screen
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

keyA = Pin(15,Pin.IN, Pin.PULL_UP) # Normally 1 but 0 if pressed
keyB = Pin(17,Pin.IN, Pin.PULL_UP)
keyX = Pin(19,Pin.IN, Pin.PULL_UP)
keyY = Pin(21,Pin.IN, Pin.PULL_UP)

up = Pin(2,Pin.IN, Pin.PULL_UP)
down = Pin(18,Pin.IN, Pin.PULL_UP)
left = Pin(16,Pin.IN, Pin.PULL_UP)
right = Pin(20,Pin.IN, Pin.PULL_UP)
ctrl = Pin(3,Pin.IN, Pin.PULL_UP)

OBD_LED = Pin(4,Pin.IN, Pin.PULL_UP)
OBD_LEDEcho = Pin(28, Pin.OUT)
OBD_Probe2 = Pin(5, Pin.OUT)
OBD_Probe3 = Pin(6, Pin.OUT)
OBD_Probe5 = Pin(7, Pin.OUT)
OBD_Button = Pin(14, Pin.OUT)



# ======= Menu ==============  
def keyCheck():
    m = 0
    a = 0
    running = True
    while running:
        # Check joystick UP/DOWN/CTRL
        if(up.value() == 0):
            m = 1
            a = a + 1    
        elif(down.value() == 0):
            m = 2
            a = a + 1 
        elif(left.value() == 0):
            m = 3
            a = a + 1
        elif(right.value() == 0):
            m = 4
            a = a + 1
        elif(ctrl.value() == 0):
            m = 5
            a = a + 1
        elif(keyA.value() == 0):
            m = 6
            a = a + 1
        elif(keyB.value() == 0):
            m = 7
            a = a + 1
        elif(keyX.value() == 0):
            m = 8
            a = a + 1
        elif(keyY.value() == 0):
            m = 9
            a = a + 1
        elif(a >= 1):
            a = 0
            running = False
            utime.sleep_ms(100)
        utime.sleep_ms(100)
        
    return m




# ======= Menu

#Sets the pass through for 12v Signal to correct OBD port
def setProbe(probe):
    if probe == 2:
        OBD_Probe3.value(0)
        OBD_Probe5.value(0)
        OBD_Probe2.value(1)
        print("Probe 2 Enabled")
    if probe == 3:
        OBD_Probe2.value(0)
        OBD_Probe5.value(0)
        OBD_Probe3.value(1)
        print("Probe 3 Enabled")
    if probe == 5:
        OBD_Probe2.value(0)
        OBD_Probe3.value(0)
        OBD_Probe5.value(1)
        print("Probe 5 Enabled")

#Emulates the pressing of OBD Button
def OBDSendCode(x):
    if x == 1:
        OBD_Button.value(1)
        utime.sleep(6)
        OBD_Button.value(0)
        utime.sleep(4)
        OBD_Button.value(1)
        utime.sleep(6)
        OBD_Button.value(0)
        print("Sending Clear Code")

    if x == 2:
        OBD_Button.value(1)
        utime.sleep(2)
        OBD_Button.value(0)
        print("sending Code Query")

    if x == 3:
        OBD_Button.value(1)
        utime.sleep(2)
        OBD_Button.value(0)
        utime.sleep(1)
        OBD_Button.value(1)
        utime.sleep(2)
        OBD_Button.value(0)
        print("Sending Input Query")

#Captures LED Code
def OBDGetCode():
    waitTimeConstant = 1
    codeList = []
    LEDInitialGet = True
    codeString = ''
    while LEDInitialGet == True:
        if OBD_LED.value() == 0: #Inverted for some reason but this means LED is ON
            codeList.append(1)
            utime.sleep(waitTimeConstant)
            LEDInitialGet = False
            

    
    for x in range(27):
        if OBD_LED.value() == 0:
            codeList.append(1)
            
        if OBD_LED.value() == 1:
            codeList.append(0)
            
        utime.sleep(waitTimeConstant)
    
    for x in codeList:
        codeString += str(x)
    print("codeString = ", codeString)
    print("Final Code Is = ", codeGetDictionary[codeString])
    #clean up
    OBD_LEDEcho.value(0)
    return codeGetDictionary[codeString]    





codeGetDictionary = {
    "1001001000000000000000000000":"111",
    "1001001010000000000000000000":"112",
    "1001001010100000000000000000":"113",
    "1001010010000000000000000000":"121",
    "1001010010101000000000000000":"123",
    "1001010100100000000000000000":"131",
    "1001010100101000000000000000":"132",
    "1001010100101010000000000000":"133",
    "1010010010100000000000000000":"212",
    "1010010010101000000000000000":"213",
    "1010010100100000000000000000":"221",
    "1010010100101010000000000000":"223",
    "1010010101001000000000000000":"231",
    "1010010101001010000000000000":"232",
    "1010010101001010100000000000":"233",
    "1010100100100000000000000000":"311",
    "1010100100101000000000000000":"312",
    "1010100101001010000000000000":"322",
    "1010101001001000000000000000":"411",
    "1001010010100000000000000000":"122",
    "1001010010101010000000000000":"124",
    "1001010010101010100000000000":"125",
    "1001010100101010101000000000":"135",
    "1001010101001000000000000000":"141",
    "1001010101001010000000000000":"142",
    "1001010101001010100000000000":"143",
    "1001010101001010101000000000":"144",
    "1001010101010010000000000000":"151",
    "1001010101010010100000000000":"152",
    "1001010101010010101010100000":"155",
    "1010010010000000000000000000":"211",
    "1010010010101010000000000000":"214",
    "1010010010101010100000000000":"215",
    "1010010100101000000000000000":"222",
    "1010010100101010100000000000":"224",
    "1010010101001010101010000000":"235",
    "1010100100101010000000000000":"313",
    "1010100100101010100000000000":"314",
    "1010100101001000000000000000":"321",
    "1010100101001010100000000000":"323",
    "1010100101001010101000000000":"324",
    "1010101001001010000000000000":"412",
    "1010101001001010100000000000":"413",
    "1010101001001010101000000000":"414",
    "1010101001001010101010000000":"415",
    "1010101001010010000000000000":"421",
    "1010101001010010100000000000":"422",
    "1010101001010010101000000000":"423",
    "1010101001010010101010000000":"424",
    "1010101001010101001000000000":"441",
    "1010101001010101001010000000":"442",
    "1010101001010101001010100000":"443",
    "1010101001010101001010101000":"444",
    "1001010101010010101010000000":"154",
    "1010010101001010101000000000":"234",
    "1010010101010010000000000000":"241",
    "1010100101010010101010000000":"334",
    "1111111111111111111111111111":"000"

}

###Begin Testing Code

def main():
    main = True
    x = 0
    print("Starting Script")
    while main:
        if(x == 6):
            print("Starting SetProbe 2")
            setProbe(2)
        if(x == 7):
            print("starting SetProbe 3")
            setProbe(3)
        if(x == 8):
            print("Starting SetProbe 5")
            setProbe(5)
        if(x == 1):
            print("Starting OBD SendCode Clear")
            OBDSendCode(1)
            print("Done with Sending Clear")
        if(x == 2):
            print("Starting OBD SendCode CodeQuery")
            OBDSendCode(2)
        if(x == 3):
            print("Starting OBD SendCode InputQuery")
            OBDSendCode(3)
        if(x == 5):
            print("Starting OBD GetCode")
            OBDGetCode()
        else:
            pass
        
        
        x = keyCheck()
        
        
    

main()
