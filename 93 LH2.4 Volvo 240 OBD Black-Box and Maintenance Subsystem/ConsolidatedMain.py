#Diagnostic and Maintenance Routine Subsystem for The Volvo 240. (DMRS for V.240)
#Made Specifically for and tested on a 1993 240 with and LH-Jetronic 2.4 Fuel Injection System, an 
#EZK 116 Ignition System, ABS System, and AW70 Automatic Transmission.
#Made in Thonny, Sublime Text 3, and Microsoft Visual Studio Code.
#Platformed on a Raspberry Pi Pico
#Made By: Jacob Whittington, Screename:Cryo_Gen/CryoGeneSys, March 2022
#Using the Hardware Driver and Display Code Provided By: Tony Goodhew 19th Aug 2021
#Via his Instructable: Workout for Waveshare 1.3" IPS LCD Display Module for Raspberry Pi Pico (240x240)
#As well as the buzzer driver by: Avram Piltch of Tom's Hardware
#Via his article: How to Use a Buzzer to Play Music with Raspberry Pi Pico
#Lets Keep These Turbo-Bricks Going To A Million Miles!

from machine import Pin,SPI,PWM
import framebuf
import utime
import os
import math
import VideoDriver as vd


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

buzzer = Pin(27, Pin.OUT)
speedometer = Pin(26, Pin.IN, PULL_UP)

pwm = PWM(Pin(BL)) # Screen Brightness
pwm.freq(1000)
pwm.duty_u16(32768) # max 65535 - mid value

LCD = vd.LCD_1inch3() # Initialise the display
LCD.fill(vd.colour(0,0,0)) # BLACK
LCD.show()

#-------------------Begin Buzzer Driver By Avram Piltch of Tom's Hardware---------------#
#Code has been modified: I changed some variable and constant names
#So that they were easier to remember going forward.
#This will be used as the alert tone song for hardware maintenance. Intitalized only at
#Startup for not only code simplicity and speed but to also not distract the driver while
#vehicle is in motion.

notes = {
"F5": 698,
"G5": 784,
"C6": 1047
}

song = ["F5","G5","C6","F5","G5","C6","rest","F5","G5","C6","F5","G5","C6"]

def playnote(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)

def rest():
    buzzer.duty_u16(0)

def play(alert):
    for i in range(len(mysong)):
        if (mysong[i] == "rest"):
            rest()
        else:
            playnote(notes[alert[i]])
        sleep(0.3)
    rest()
#play(song)
#----------------------------- End Buzzer Driver ---------------------------------------#
################## Begin Character Map and Print to Screen Functions ####################
#------------------------------ Begin Tony's Code --------------------------------------#

def colour(R,G,B): # Convert 3 byte colours to 2 byte colours, RGB565
# Get RED value
    rp = int(R*31/255) # range 0 to 31
    if rp < 0: rp = 0
    r = rp *8
# Get Green value - more complicated!
    gp = int(G*63/255) # range 0 - 63
    if gp < 0: gp = 0
    g = 0
    if gp & 1:  g = g + 8192
    if gp & 2:  g = g + 16384
    if gp & 4:  g = g + 32768
    if gp & 8:  g = g + 1
    if gp & 16: g = g + 2
    if gp & 32: g = g + 4
# Get BLUE value       
    bp =int(B*31/255) # range 0 - 31
    if bp < 0: bp = 0
    b = bp *256
    colour = r+g+b
    return colour

yellow = colour(255,255,0)
blue = colour(0,0,255)
green = colour(0,255,0)
red = colour(255,0,0)

# 7-seg character definations and routines
nums =[1,1,1,1,1,1,0,  # 0 # One row per digit 
       0,1,1,0,0,0,0,  # 1
       1,1,0,1,1,0,1,  # 2
       1,1,1,1,0,0,1,  # 3
       0,1,1,0,0,1,1,  # 4
       1,0,1,1,0,1,1,  # 5
       1,0,1,1,1,1,1,  # 6
       1,1,1,0,0,0,0,  # 7
       1,1,1,1,1,1,1,  # 8
       1,1,1,0,0,1,1,  # 9
       1,1,1,1,1,0,1,  # a = 10 - HEX characters
       0,0,1,1,1,1,1,  # b = 11
       0,0,0,1,1,0,1,  # c = 12
       0,1,1,1,1,0,1,  # d = 13
       1,1,0,1,1,1,1,  # e = 14
       1,0,0,0,1,1,1,  # f = 15
       1,1,1,1,0,1,1,  # g needed for seg!
       0,0,0,0,0,0,1,  # -
       0,0,0,0,0,0,0]  # Blank

def seg(xx,yy,n,f,bg,fg):
    # (x, y, number, size-factor, background, foreground)
    c = [bg,fg]
    p = n * 7    
    LCD.fill_rect(xx+1*f,yy+0*f,3*f,1*f,c[nums[p]])
    LCD.fill_rect(xx+4*f,yy+1*f,1*f,3*f,c[nums[p+1]])
    LCD.fill_rect(xx+4*f,yy+5*f,1*f,3*f,c[nums[p+2]])
    LCD.fill_rect(xx+1*f,yy+8*f,3*f,1*f,c[nums[p+3]])
    LCD.fill_rect(xx+0*f,yy+5*f,1*f,3*f,c[nums[p+4]])
    LCD.fill_rect(xx+0*f,yy+1*f,1*f,3*f,c[nums[p+5]])
    LCD.fill_rect(xx+1*f,yy+4*f,3*f,1*f,c[nums[p+6]])   
    LCD.show()
# ========= End of 7-seg section ==========
'''
Adjustable font for the WaveShare 1.3" IPS LCD Display Module for Raspberry Pi Pico (240x240)
                         Tony Goodhew 17th Aug 2021
           Modified from code by Les Wright 2021 V 1.1 for Pimoroni Pico Display                  
              https://forums.pimoroni.com/t/pico-display-and-fonts/16194/18
'''
#ASCII Character Set
cmap = ['00000000000000000000000000000000000', #Space
        '00100001000010000100001000000000100', #!
        '01010010100000000000000000000000000', #"
        '01010010101101100000110110101001010', ##
        '00100011111000001110000011111000100', #$
        '11001110010001000100010001001110011', #%
        '01000101001010001000101011001001101', #&
        '10000100001000000000000000000000000', #'
        '00100010001000010000100000100000100', #(
        '00100000100000100001000010001000100', #)
        '00000001001010101110101010010000000', #*
        '00000001000010011111001000010000000', #+
        '000000000000000000000000000000110000100010000', #,
        '00000000000000011111000000000000000', #-
        '00000000000000000000000001100011000', #.
        '00001000010001000100010001000010000', #/
        '01110100011000110101100011000101110', #0
        '00100011000010000100001000010001110', #1
        '01110100010000101110100001000011111', #2
        '01110100010000101110000011000101110', #3
        '00010001100101011111000100001000010', #4
        '11111100001111000001000011000101110', #5
        '01110100001000011110100011000101110', #6
        '11111000010001000100010001000010000', #7
        '01110100011000101110100011000101110', #8
        '01110100011000101111000010000101110', #9
        '00000011000110000000011000110000000', #:
        '01100011000000001100011000010001000', #;
        '00010001000100010000010000010000010', #<
        '00000000001111100000111110000000000', #=
        '01000001000001000001000100010001000', #>
        '01100100100001000100001000000000100', #?
        '01110100010000101101101011010101110', #@
        '00100010101000110001111111000110001', #A
        '11110010010100111110010010100111110', #B
        '01110100011000010000100001000101110', #C
        '11110010010100101001010010100111110', #D
        '11111100001000011100100001000011111', #E
        '11111100001000011100100001000010000', #F
        '01110100011000010111100011000101110', #G
        '10001100011000111111100011000110001', #H
        '01110001000010000100001000010001110', #I
        '00111000100001000010000101001001100', #J
        '10001100101010011000101001001010001', #K
        '10000100001000010000100001000011111', #L
        '10001110111010110101100011000110001', #M
        '10001110011010110011100011000110001', #N
        '01110100011000110001100011000101110', #O
        '11110100011000111110100001000010000', #P
        '01110100011000110001101011001001101', #Q
        '11110100011000111110101001001010001', #R
        '01110100011000001110000011000101110', #S
        '11111001000010000100001000010000100', #T
        '10001100011000110001100011000101110', #U
        '10001100011000101010010100010000100', #V
        '10001100011000110101101011101110001', #W
        '10001100010101000100010101000110001', #X
        '10001100010101000100001000010000100', #Y
        '11111000010001000100010001000011111', #Z
        '01110010000100001000010000100001110', #[
        '10000100000100000100000100000100001', #\
        '00111000010000100001000010000100111', #]
        '00100010101000100000000000000000000', #^
        '00000000000000000000000000000011111', #_
        '11000110001000001000000000000000000', #`
        '00000000000111000001011111000101110', #a
        '10000100001011011001100011100110110', #b
        '00000000000011101000010000100000111', #c
        '00001000010110110011100011001101101', #d
        '00000000000111010001111111000001110', #e
        '00110010010100011110010000100001000', #f
        '000000000001110100011000110001011110000101110', #g
        '10000100001011011001100011000110001', #h
        '00100000000110000100001000010001110', #i
        '0001000000001100001000010000101001001100', #j
        '10000100001001010100110001010010010', #k
        '01100001000010000100001000010001110', #l
        '00000000001101010101101011010110101', #m
        '00000000001011011001100011000110001', #n
        '00000000000111010001100011000101110', #o
        '000000000001110100011000110001111101000010000', #p
        '000000000001110100011000110001011110000100001', #q
        '00000000001011011001100001000010000', #r
        '00000000000111110000011100000111110', #s
        '00100001000111100100001000010000111', #t
        '00000000001000110001100011001101101', #u
        '00000000001000110001100010101000100', #v
        '00000000001000110001101011010101010', #w
        '00000000001000101010001000101010001', #x
        '000000000010001100011000110001011110000101110', #y
        '00000000001111100010001000100011111', #z
        '00010001000010001000001000010000010', #{
        '00100001000010000000001000010000100', #|
        '01000001000010000010001000010001000', #}
        '01000101010001000000000000000000000' #}~
]

def printchar(letter,xpos,ypos,size,charupdate,c):
    origin = xpos
    charval = ord(letter)
    #print(charval)
    index = charval-32 #start code, 32 or space
    #print(index)
    character = cmap[index] #this is our char...
    rows = [character[i:i+5] for i in range(0,len(character),5)]
    #print(rows)
    for row in rows:
        #print(row)
        for bit in row:
            #print(bit)
            if bit == '1':
                LCD.pixel(xpos,ypos,c)
                if size==2:
                    LCD.pixel(xpos,ypos+1,c)
                    LCD.pixel(xpos+1,ypos,c)
                    LCD.pixel(xpos+1,ypos+1,c)
                if size == 3:
                    LCD.pixel(xpos,ypos,c)
                    LCD.pixel(xpos,ypos+1,c)
                    LCD.pixel(xpos,ypos+2,c)
                    LCD.pixel(xpos+1,ypos,c)
                    LCD.pixel(xpos+1,ypos+1,c)
                    LCD.pixel(xpos+1,ypos+2,c)
                    LCD.pixel(xpos+2,ypos,c)
                    LCD.pixel(xpos+2,ypos+1,c)
                    LCD.pixel(xpos+2,ypos+2,c)
            xpos+=size
        xpos=origin
        ypos+=size
    if charupdate == True:
        LCD.show()
    
def delchar(xpos,ypos,size,delupdate):
    if size == 1:
        charwidth = 5
        charheight = 9
    if size == 2:
        charwidth = 10
        charheight = 18
    if size == 3:
        charwidth = 15
        charheight = 27
    c =colour(0,0,0) # Colour of background
    LCD.fill_rect(xpos,ypos,charwidth,charheight,c) #xywh
    if delupdate == True:
        LCD.show()

def printstring(string,xpos,ypos,size,charupdate,strupdate,c):   
    if size == 1:
        spacing = 8
    if size == 2:
        spacing = 14
    if size == 3:
        spacing = 18
    for i in string:
        printchar(i,xpos,ypos,size,charupdate,c)
        xpos+=spacing
    if strupdate == True:
        LCD.show()
# =============End of Characters section ===============

# There are a few lines here and there that were written by tony as well. I will include
# a copy of his original code in the repository for comparison. I wouldnt have been able to use this
# screen hardware without the resources he provided. A big thank you to the legend himself.
#------------------------------ End Tony's Code ----------------------------------------#
############################# Begin Hardware Driver #####################################
#------------------------------ Jacob's Code Begins ------------------------------------#

#This checks for the next state of the keys and returns the respective key identifing integer.
#The 100 millisecond delay added at the end is so the hardware has time to register the input.
# Think there was some key bouncing going on, this just gives enought time to mitigate that without
# having to include a whole-ass debounce circuit
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


#Sets the pass through for 12v Signal to correct OBD port
#Emulates the process of physically moving the plug to the 3 different ports.
#Under the hood (heh) what this does is connects the OBD box to each of the 3 seperate on board computers.
def setProbe(probe):
    #Fuel Injection and main computer
    if probe == 2:
        OBD_Probe3.value(0)
        OBD_Probe5.value(0)
        OBD_Probe2.value(1)
        print("Probe 2 Enabled")
    #ABS computer
    if probe == 3:
        OBD_Probe2.value(0)
        OBD_Probe5.value(0)
        OBD_Probe3.value(1)
        print("Probe 3 Enabled")
    #Ignition Computer
    if probe == 5:
        OBD_Probe2.value(0)
        OBD_Probe3.value(0)
        OBD_Probe5.value(1)
        print("Probe 5 Enabled")
    #None, Used for Cleanup
    if probe == 0:
        OBD_Probe2.value(0)
        OBD_Probe3.value(0)
        OBD_Probe5.value(0)
        print("No Probes Enabled")

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
# This takes a sample of the OBD LED state every second and adds it to a string. It does this over the course of 28 seconds for a 28 character string.
# This string is then compared to the dictionary to get the actual numeric code. The reason i chose 28 seconds specifically is because every LED on 
# state is 1 second long, every LED off state is also 1 second long if it still part of the same digit. The space between each digit is 2 seconds off. 
# Adding up the largest code (444) it translates to 1010101 (4) 00 (space) 1010101 (4) 00 (space) 1010101 (4) this gives us 25 digits. The last 3 digits
# should always be 3 0's. this acts as a convienient footer if i ever need to update this program and need a little more versatility. This totals the 28 
# digits. A visual graph of all code states will be included in the repository as CodeGraph.png

def OBDGetCode():
    waitTimeConstant = 1
    codeList = []
    LEDInitialGet = True
    codeString = ''
    #This makes the system wait to start counting down the 28 seconds until the first input is received.
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

def rapidFlashTest():
    rapidFlashRunning = True
    rapidFlashAccumulator = 0
    timeDivisor = 0
    rapidInitialGet = True
    while rapidInitialGet:
        if OBD_LED.value() 0:
            rapidInitialGet = False
    while rapidFlashRunning:
        if OBD_LED.value() == 0:
            rapidFlashAccumulator += 1
        timeDivisor += 1
        utime.sleep_ms(62) #1/16th of a second rounded down. may have to adjust
        x = rapidFlashAccumulator / timeDivisor
        if x < 0.4: #if we receive a full quarter second with no input we consider rapidflash state over. change this integer to tune and zero in on this detection.
            rapidFlashRunning = False
    return
        

########################### End Hardware Driver #################################
########################### Prompt Definitions Begin ############################

def ignitionPrompt():
    LCD.fill(0)
    c = red
    printstring("Turn Ignition to Position II",20,20,2,0,0,c)
    printstring("Then Hit Enter", 40,40,2,0,0,c)
    c = green
    printstring("Back",200,200,1,0,0,c)
    c = red
    LCD.show()


########################### End Prompt Definitions ##############################
############################## Fuel Injection Function Begin #################################
def fuelMenu():
    run2 = True
    a = 0
    b = 0
    LCD.fill(0)

    while run2:
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Fuel Injection",30,20,2,0,0,c)
        c = blue #string,xpos,ypos,size,charupdate,strupdate,c
        printstring("Pull Stored Codes",60,40,1,0,0,c)
        printstring("Check ECU Inputs",60,60,1,0,0,c)
        printstring("Check ECU Outputs",60,80,1,0,0,c)
        printstring("Clear Codes",60,80,1,0,0,c
        c = green
        printstring("Back",200,200,1,0,0,c)
        
        if(a == 1):
            b = b - 1
            if(b < 0):
                b = 0
        if(a == 2):
            b = b + 1
            if(b > 3):
                b = 3

        c = red 
        if(b == 0):
            printstring("*",20,40,1,0,0,c)

        if(b == 1):
            printstring("*",20,60,1,0,0,c)

        if(b == 2):
            printstring("*",20,80,1,0,0,c)

        if(b == 3):
            printstring("*",20,100,1,0,0,c)

        LCD.show()    
        if(a == 5):
            if(b == 0):
                print("Selected Pull Codes")
            if(b == 1):
                print("Selected Check ECU Inputs")
            if(b == 2):
                print("Selected Check ECU Outputs")
            if(b == 3):
                print("Selected Clear Codes")
                fuelClear()
        if(a == 9):
            #This is to go back to main menu alon with th eneeded screen update
            run2 = False

        
        print(b)
        LCD.show()
        a = keyCheck()
    LCD.fill(0)

fuelDictionary = {
  "111": "No Faults Detected in ECU",
  "112": "Fault Detected In ECU",
  "113": "Fault Detected in Fuel Injectors",
  "121": "Fault Detected in Signal To/From Mass Air Meter",
  "123": "Fault Detected in Signal To/From Coolant Temperature Sensor",
  "131": "Fault: Engine RPM Signal Missing",
  "132": "Fault: Battery Voltage Too High/Low",
  "133": "Fault: Throttle Switch Idle Contacts Misadjusted or Shorted to Ground", #LH2.4 only
  "212": "Fault: Oxygen Sensor Signal Missing or Faulty",
  "213": "Fault: Throttle Switch Full Throttle Contacts Misadjusted or Shorted to Ground", #LH2.4 only
  "221": "Fault: Fuel System is Having To Compensate for Extreamly Lean/Rich Air-Fuel Mix at Cruise",
  "223": "Fault Detected in Signal To/From Air Control Valve",
  "231": "Fault: Fuel System is Having To Compensate for Moderatly Lean/Rich Air-Fuel Mix at Cruise",
  "232": "Fault: Fuel System is Having To Compensate for Moderatly Lean/Rich Air-Fuel Mix at Idle",
  "233": "Fault: Air Control Valve Closed, Possible Air Leak",
  "311": "Fault: Missing Vehicle Speed Signal",
  "312": "Fault: Anti-Knock Signal Missing",
  "322": "Fault: Air Mass Meter Hot-Wire Burn-Off Function Not Working", #LH2.4 Only
  "411": "Fault: Throttle Sensor Signal Missing or Faulty", #LH3.1 Only
  "000": "Error: OBD LED Signal Faulty. Check Wiring/Components To/Of DMRS System"
  }

checkEngineLightDictionary = {
    "off": "Check Engine Light Should Be Off",
    "on": "Check Engine Light Should Be On"
    } #If getting LH2.4 errors on LH3.1 or vice versa, Shit is really really bad. Good luck!

#This function is probably superfluous with the dictionary but whatever   
def fuelCode(led_code): 
    if led_code == 111:
        return fuelDictionary["111"], checkEngineLightDictionary["off"]
    elif led_code == 112:
        return fuelDictionary["112"], checkEngineLightDictionary["on"]
    elif led_code == 113:
        return fuelDictionary["113"], checkEngineLightDictionary["on"]
    elif led_code == 121:
        return fuelDictionary["121"], checkEngineLightDictionary["on"]
    elif led_code == 123:
        return fuelDictionary["123"], checkEngineLightDictionary["on"]
    elif led_code == 131:
        return fuelDictionary["131"], checkEngineLightDictionary["off"]
    elif led_code == 132:
        return fuelDictionary["132"], checkEngineLightDictionary["off"]
    elif led_code == 133:
        return fuelDictionary["133"], checkEngineLightDictionary["off"]
    elif led_code == 212:
        return fuelDictionary["212"], checkEngineLightDictionary["on"]
    elif led_code == 213:
        return fuelDictionary["213"], checkEngineLightDictionary["off"]
    elif led_code == 221:
        return fuelDictionary["221"], checkEngineLightDictionary["on"]
    elif led_code == 223:
        return fuelDictionary["223"], checkEngineLightDictionary["off"]
    elif led_code == 231:
        return fuelDictionary["231"], checkEngineLightDictionary["off"]
    elif led_code == 232:
        return fuelDictionary["232"], checkEngineLightDictionary["off"]
    elif led_code == 233:
        return fuelDictionary["233"], checkEngineLightDictionary["off"]
    elif led_code == 311:
        return fuelDictionary["311"], checkEngineLightDictionary["off"]
    elif led_code == 312:
        return fuelDictionary["312"], checkEngineLightDictionary["off"]
    elif led_code == 322:
        return fuelDictionary["322"], checkEngineLightDictionary["off"]
    elif led_code == 411:
        return fuelDictionary["411"], checkEngineLightDictionary["off"]
    else:
        return "Error, Code Not Found in Ignition Code Database"

###Erase Codes
def fuelClear():
    ignitionPrompt()
    a = keyCheck()
    if a == 5:
        setProbe(2)
        utime.sleep(2)
        OBDSendCode(1)
        utime.sleep(2)
        LCD.fill(0)
        printstring("Getting Code.....", 75,75,2,0,0,c)
        LCD.show()
        a = OBDGetCode()
        LCD.fill(0)
        c = (95,215,95)
        printstring(fuelCode(a), 10,10,1,0,0,c)
        LCD.show()
        waiting = True
        while waiting:
            a = keyCheck()
            if a == 9:
                LCD.Fill(0)
                fuelMenu()
                waiting = False
            else:
                pass
    if a == 9:
        setProbe(0)
        LCD.fill(0)
        fuelmenu()

###Function 1: Retrieval of stored codes
def fuelFunction1():
    a = 0
    b = 0
    LCD.fill(0)
    while b < 3:
        if b == 0:
            LED.fill(0)
            c = red
            printstring("Fuel ECU Code Check",30,10,2,0,0,c)
            c = blue
            printstring("This Function Will Pull The First Stored Code If Any",10,20,1,0,0,c)
            c = green
            printstring("Next",200,50,1,0,0,c)
            printstring("Back",200,200,1,0,0,c)
            LCD.show()
            if keyCheck() == 6:
                ignitionPrompt()
                if keyCheck() == 6:
                    setProbe(2)
                    utime.sleep(2)
                    OBDSendCode(1)
                    utime.sleep(2)
                    LCD.fill(0)
                    printstring("Getting Code.....", 75,75,2,0,0,c)
                    LCD.show()
                    x = OBDGetCode()
                    LCD.fill(0)
                    c = (95,215,95)
                    printstring(fuelCode(x), 10,10,1,0,0,c)
                    printstring("Next",200,50,1,0,0,c))
                    LCD.show()
                    if keyCheck() == 6:
                        b =+ 1

            if keyCheck() == 9:
                setProbe(0)
                b = 4
        else:
            LCD.fill(0)
            c = red
            printstring("Fuel ECU Code Check",30,10,2,0,0,c)
            c = blue
            printstring("Do you wish to check for any more stored codes?",20,40,1,0,0,c)
            c = green
            printstring("Yes",200,50,1,0,0,c)
            printstring("No-Back",200,100,1,0,0,c)            
            LCD.show()
            if keyCheck() == 6:
                ignitionPrompt()
                if keyCheck() == 6:
                    setProbe(2)
                    utime.sleep(2)
                    OBDSendCode(1)
                    utime.sleep(2)
                    LCD.fill(0)
                    printstring("Getting Code.....", 75,75,2,0,0,c)
                    LCD.show()
                    x = OBDGetCode()
                    LCD.fill(0)
                    c = (95,215,95)
                    printstring(fuelCode(x), 10,10,1,0,0,c)
                    printstring("Next",200,50,1,0,0,c))
                    LCD.show()
                    if keyCheck() == 6:
                        b =+ 1

            if keyCheck() == 7:
                b = 4
    setProbe(0)
    fuelMenu()

###Function 2: Testing ECU Inputs
def fuelFunction2():
    print("This tests these ECU inputs: Throttle Switch/Sensor, Engine RPM Signal, AC Microswitch Signal, and AC Compressor Signal.")
    ignitionPrompt()
    probe.port2()
#Full Throttle Test Begin
    a = 0
    b = 0
    prompt.fullThrottle()
    button.press()
    time.sleep(1)
    button.press()
    ledp.get(a)
    if a == 5:
        print("LED should be rapidly flashing")
    else:
        print("Internal Error: Expected ECU Rapid-Flash prompt, got something else:", a)
#LED should rapid flash here
    prompt.closeThrottle()
    ledp.get(a)
    if a == 6: #rapid flash to low with 3/4 sec wait
        ledp.get(b)
        if b == "333":
            if CarInfo.type == "LH-2.4":
                print("Full Throttle Switch Good!")
            if CarInfo.type == "LH-3.1":
                print("Full Throttle Sensor Good!")
        else:
            print("error: Expected 333 'All-Good' Code but instead received:", b)
    if a == 5:
        if CarInfo.type == "LH-2.4":
            print("Fault: Full Throttle Switch Signal Missing or Unreadable, Check Part")
        if CarInfo.type == "LH-3.1":
            print("Fault: Full Throttle Sensor Signal Missing or Unreadable, Check Part")
        
    else:
        print("error: Expected 'All-Good' or 'No-Good' got something else unexpected:", a)
    prompt.next()
    #Full Throttle Test Over
    #Off-Idle Test Begin
    prompt.offIdleThrottle()
    ledp.get(a)
    if a == 6:
        ledp.get(a)
        if a == "332":
                print("Off-Idle Signal Good!")
        if a == 5: #Rapid Flash
                    print("Off-Idle Signal Missing or Unreadable, Check Part")
    else:
        print("error: Expected 332 Good signal or Rapid-Flash Bad Signal, Got This Instead:", a)
    prompt.next()
    #Off-Idle Test Over
    #Engine RPM Test Begin
    prompt.startEngine()
    ledp.get(a)
    if a == 6:
        ledp.get(a)
        if a == "331":
            print("RPM Signal OK!")
        if a == 5:
            print("RPM Signal Not Found, See '280-Ignition System' in Service Manual, If OK Check 'Electrical Tests'")
    else:
        print("error: Expected 331 Good RPM Signal or Rapid-Flash Bad Signal, Got", a, " Instead")
    prompt.next()
    #Engine RPM Test Over
    #AC Microswitch Test Begin
    prompt.ACMicroswitch()
    #led off 114 then rapid flash
    if CarInfo.type == "LH-3.1":
        ledp.get(a)
        if a == 6:
            ledp.get(a)
            if a == "114":
                print("AC Microswitch Signal OK!")
            if a == 5:
                print("AC Microswitch Signal Missing or Unreadable, Service Needed")
        else:
            print("error: Expected 114 AC Microswitch All-Good Code or Rapid-Flash Bad Signal, Got", a, " Instead")
        prompt.compressor() #Wait until you hear compressor engage and immediately hit next to get code
        ledp.get(a)
        if a == "134":
            print("AC Compressor OK!")
        if a == 5:
            print("AC Compressor Signal Missing or Unreadable, Only Service if AC Certified as Service Can Be Dangerous")
        else:
            print("error: Expected 134 AC Compressor All-Good Signal or Rapid-Flash Bad Signal, Got", a, " Instead")
            
    else:
        ledp.get(a)
        if a == 6:
            ledp.get(a)
            if a == "114":
                print("AC Microswitch Signal OK!")
            if a == 5:
                print("AC Microswitch Signal Missing or Unreadable, Service Needed")
        else:
            print("error: Expected 114 AC Microswitch All-Good Code or Rapid-Flash Bad Signal, Got", a, " Instead")
    prompt.next()
    #AC Microswitch Test Over
    #Automatic Transmission Idle Compensation Test Begin
    prompt.Trans() #Park, Drive, Then Neutral
    ledp.get(a)
    if a == 6:
        ledp.get(a)
        if a == "124":
            print("ECU is Properly Adjusting Idle Speed To Compensate For Transmission Load!")
        if a == 5:
            print("Test LH System Inputs and Components Used to Control Engine Idle Speed, ECU not Properly Compensating For Transmission Load")
    else:
        print("error: Expected 124 ECU Transmission Load OK Signal, or Rapid-Flash Bad Signal, Got", a," Instead")
    prompt.next()
    #Automatic Transmission Idle Compensation Test Over
    #End Function 2
    print("Please Shift Back To Park and Shut off The Ignition. Fuel Injection Signal Testing is Over")
    probe.none()

###Function 3: Testing ECU Outputs
def fuelFunction3():

######################## Fuel Injection Function END ##########################
########################### Ignition System Begin #############################

########################### Ignition System Ends ##############################
############################ ABS System Begins ################################

def ABSFunction1():
    pass

ABSDictionary = {
    "111": "No Error Code Set",
    "121": "Left side front wheel sensor: faulty signal at speed less than 40km/h(25 MPH)",
    "122": "Right side front wheel sensor: faulty signal at speed less than 40km/h(25 MPH)",
    "123": "Left side rear wheel sensor: faulty signal at speed less than 40km/h(25 MPH)",
    "124": "Right side rear wheel sensor: faulty signal at speed less than 40km/h(25 MPH)",
    "125": "Signal faulty from at least one wheel sensor for a long period",
    "135": "Control Module (CM) faulty",
    "141": "Faulty pedal sensor: shorted to ground or supply",
    "142": "Faulty stop (brake) lamp switch: open circuit",
    "143": "Control Module (CM) faulty",
    "144": "Brake discs overheated",
    "151": "Left front wheel sensor: open circuit or short-circuit to battery voltage",
    "152": "Right front wheel sensor: open circuit or short-circuit to battery voltage",
    "155": "Rear axle sensor: open circuit or short-circuit to battery voltage",
    "211": "Left front wheel sensor: no signal on moving off",
    "212": "Right front wheel sensor: no signal on moving off",
    "213": "Left rear wheel sensor: no signal on moving off",
    "214": "Right rear wheel sensor: no signal on moving off",
    "215": "Valve relay: open circuit or short-circuit",
    "221": "Left front wheel sensor: ABS operation signal missing",
    "222": "Right front wheel sensor: ABS operation signal missing",
    "223": "Left rear wheel sensor: ABS operation signal missing",
    "224": "Right rear wheel sensor: ABS operation signal missing",
    "231": "Left front wheel sensor: signal missing",
    "232": "Right front wheel sensor: signal missing",
    "235": "Rear axle sensor: signal missing",
    "311": "Left front wheel sensor: open circuit or short-circuit",
    "312": "Right front wheel sensor: open circuit or short-circuit",
    "313": "Left rear wheel sensor: open circuit or short-circuit",
    "314": "Right rear wheel sensor: open circuit or short-circuit",
    "321": "Left front wheel sensor: irregular interference at speeds over 40 km/h(25 MPH)",
    "322": "Right front wheel sensor: irregular interference at speeds over 40 km/h(25 MPH)",
    "323": "Left rear wheel sensor: irregular interference at speeds over 40 km/h(25 MPH)",
    "324": "Right rear wheel sensor: irregular interference at speeds over 40 km/h(25 MPH)",
    "411": "Left front wheel inlet valve: open circuit or short circuit",
    "412": "Left front return valve: open circuit or short circuit",
    "413": "Right front wheel inlet valve: open circuit or short circuit",
    "414": "Right front return valve: open circuit or short circuit",
    "415": "Rear valve: open circuit or short circuit",
    "421": "Rear wheel circuit inlet valve: open circuit or short circuit",
    "422": "Rear wheel circuit return valve: open circuit or short circuit",
    "423": "Traction control system (TRACS) valve: open circuit or short circuit",
    "424": "Pressure switch for TRACS: faulty or short circuit",
    "441": "Control Module (CM) faulty",
    "442": "Pump pressure low",
    "443": "Pump motor/relay: electrical or mechanical fault",
    "444": "No power supply to valves in hydraulic unit"
    }


############################# ABS System Ends #################################
############################## Secondary Menus ################################

def diagnostics():
    run = True
    a = 0
    b = 0
    LCD.fill(0)
    while run:
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Diagnostics",50,20,2,0,0,c)
        c = blue #string,xpos,ypos,size,charupdate,strupdate,c
        printstring("Fuel Injection System",30,40,1,0,0,c)
        printstring("Ignition System",30,60,1,0,0,c)
        printstring("Anti-Lock Breaking System",30,80,1,0,0,c)
        c = green
        printstring("Back",200,200,1,0,0,c)
        
        if(a == 1):
            b = b - 1
            if(b < 0):
                b = 0
        if(a == 2):
            b = b + 1
            if(b > 2):
                b = 2

        c = red 
        if(b == 0):
            printstring("*",20,40,1,0,0,c)
            print(b)
        if(b == 1):
            printstring("*",20,60,1,0,0,c)
            print(b)
        if(b == 2):
            printstring("*",20,80,1,0,0,c)
            print(b)
        LCD.show()    
        if(a == 5):
            if(b == 0):
                print("Selected Fuel Injection")
                fuelMenu()
            if(b == 1):
                print("Selected Ignition")
                ignitionMenu()
            if(b == 2):
                print("Selected ABS")
                ABSMenu()
        if(a == 9):
            #This is to go back to main menu along with the needed screen update
            run = False
      
        print(b)
        LCD.show()
        a = keyCheck()
     
def maintenance():
    run = True
    a = 0
    b = 0
    LCD.fill(0)
    while run:
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Maintenance",50,20,2,0,0,c)
        c = blue #string,xpos,ypos,size,charupdate,strupdate,c
        printstring("View Current Warnings",30,40,1,0,0,c)
        printstring("View Part Health",30,60,1,0,0,c)
        printstring("View Fluid Health",30,80,1,0,0,c)
        printstring("Enter New Repair/Change",30,100,1,0,0,c)
        c = green
        printstring("Back",200,200,1,0,0,c)
        
        if(a == 1):
            b = b - 1
            if(b < 0):
                b = 0
        if(a == 3):
            b = b + 1
            if(b > 3):
                b = 3

        c = red 
        if(b == 0):
            printstring("*",20,40,1,0,0,c)
            print(b)
        if(b == 1):
            printstring("*",20,60,1,0,0,c)
            print(b)
        if(b == 2):
            printstring("*",20,80,1,0,0,c)
            print(b)
        if(b == 3):
            printstring("*",20,100,1,0,0,c)

        LCD.show()    
        if(a == 5):
            if(b == 0):
                print("View Current Warnings")
            if(b == 1):
                print("View Part Health")
            if(b == 2):
                print("View Fluid Health")
            if(b == 3):
                print("View New Repair/Change")
        if(a == 9):
            #This is to go back to main menu alon with th eneeded screen update
            run = False

        
        print(b)
        LCD.show()
        a = keyCheck()

def records():
    run = True
    while run:
        print("recor")
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Records",80,20,2,0,0,c)
        LCD.show()
        if(keyCheck() == 9):
            break

def settings():
    run = True
    while run:
        print("sett")
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Settings",70,20,2,0,0,c)
        LCD.show()
        if(keyCheck() == 9):
            break


# ================================= The Main Menu ======================================= #
def mainMenu():
    m = 0
    n = 0
    red = colour(255,0,0)
    yellow = colour(255,255,0)
    blue = colour(0,0,255)
    running = True
    while running:
        LCD.fill(0)
        c = red
        printstring("DMRS for V.240",17,10,2,0,0,c)
        c = blue 
        printstring("Diagnostics",35,50,2,0,0,c)
        printstring("Maintenance",35,80,2,0,0,c)
        printstring("Records",35,110,2,0,0,c)
        printstring("Settings",35,140,2,0,0,c)
        printstring("Quit Program",35,170,2,0,0,c) 
        
        if(m == 0):
            pass
        if(m == 1):
            n = n - 1
            if(n < 0):
                n = 0
        if(m == 2):
            n = n + 1
            if(n > 4):
                n = 4


        c = red 
        if(n == 0):
            printstring("*",20,50,1,0,0,c)
            print(n)
        if(n == 1):
            printstring("*",20,80,1,0,0,c)
            print(n)
        if(n == 2):
            printstring("*",20,110,1,0,0,c)
            print(n)
        if(n == 3):
            printstring("*",20,140,1,0,0,c)
            print(n)
        if(n == 4):
            printstring("*",20,170,1,0,0,c)
            print(n)
        
        if(m == 5):
            if(n == 0):
                print("Diagnostics Run")
                diagnostics()
            if(n == 1):
                print("Maintenance Run")
                maintenance()
            if(n == 2):
                print("Records Run")
                records()
            if(n == 3):
                print("Settings Run")
                settings()
            if(n == 4):
                print("Halting")
                break
        
        LCD.show()
        #This is below this lcd.show for a reason. If not the device boots to a black screen bc it hangs on hw.keycheck until an input is received.
        m = keyCheck()


# Finish
    LCD.fill(0)
    c = colour(255,0,0)
    printstring("Halted",80,110,2,0,0,c)
    LCD.show()
    #Clean Up
    utime.sleep(3)
    LCD.fill(0)
    LCD.show()

mainMenu()