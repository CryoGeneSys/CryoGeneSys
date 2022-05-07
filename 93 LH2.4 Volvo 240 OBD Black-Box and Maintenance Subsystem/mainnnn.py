#Diagnostic and Maintenance Routine Subsystem for The Volvo 240.
#Made Specifically for and tested on a 1993 240 with and LH-Jetronic 2.4 Fuel Injection System, an 
#EZK 116 Ignition System, ABS System, and AW70 Automatic Transmission.
#Made in Thonny, Sublime Text 3, and Microsoft Visual Studio Code.
#Platformed on a Raspberry Pi Pico
#Made By: Jacob Whittington, Screename:Cryo_Gen, March 2022
#Using the Hardware Driver and Display Code Provided By: Tony Goodhew 19th Aug 2021
#Via his Instructable: Workout for Waveshare 1.3" IPS LCD Display Module for Raspberry Pi Pico (240x240)
#Lets Keep These Turbo-Bricks Going To A Million Miles!

from machine import Pin,SPI,PWM
import framebuf
import utime
import os
import math
import HardwareControl as HW
import VideoDriver as vd
#import FuelInjector as fi

BL = 13  # Pins used for display screen
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

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

# == Project specific routines ==============
yellow = colour(255,255,0)
blue = colour(0,0,255)
green = colour(0,255,0)
red = colour(255,0,0)

def fuelMenu():
    m = 0
    yellow = colour(255,255,0)
    blue = colour(0,0,255)
    green = colour(0,255,0)
    red = colour(255,0,0)
    run1 = True
    while run1:
        print("fuel")
        LCD.fill(0)
        c = colour(255,0,0)
        printstring("Fuel Injection",20,20,2,0,0,c)
        c = yellow
        if m == 0:
            c = blue
        printstring("1: Pull/Reset Codes",25,50,1,0,0,c)
        c = yellow
        if m == 1:
            c = blue
        printstring("2: Check ECU Inputs",25,80,1,0,0,c)
        c = yellow
        if m == 2:
            c = blue
        printstring("3: Check ECU Outputs",25,110,1,0,0,c)
        c = green
        printstring("Main",200,200,1,0,0,c)
        printstring("Menu",200,210,1,0,0,c)
        c = yellow
        LCD.show()
        
        # Check joystick UP/DOWN/CTRL
        if(up.value() == 0):
            m = m - 1
            if m < 0:
                m = 0
            
        elif(down.value() == 0):
            m = m + 1
            if m > 2:
                m = 2
                       
        elif(ctrl.value() == 0):
            if(m == 3):
                pass
                LCD.fill(0)
            if(m == 2):
                pass
                LCD.fill(0)
            if(m == 1):
                pass
                LCD.fill(0)
            if(m == 0):
                #fi.fuelFunction1()
                LCD.fill(0)
        LCD.show()
        if(HW.keyCheck() == 9):
            break


def diagnostics():
    m = 0
    run = True
    while run:
        print("diag")
        LCD.fill(0)
        c = colour(255,0,0)
        printstring("Diagnostics",20,20,2,0,0,c)
        c = yellow
        if m == 0:
            c = blue
        printstring("Fuel Injection System",25,50,1,0,0,c)
        c = yellow
        if m == 1:
            c = blue
        printstring("Ignition System",25,80,1,0,0,c)
        c = yellow
        if m == 2:
            c = blue
        printstring("Anti-Lock Braking System",25,110,1,0,0,c)
        c = green
        printstring("Back",200,200,1,0,0,c)
        c = yellow
        LCD.show()
        
        # Check joystick UP/DOWN/CTRL
        if(up.value() == 0):
            m = m - 1
            if m < 0:
                m = 0
            
        elif(down.value() == 0):
            m = m + 1
            if m > 2:
                m = 2
                       
        elif(ctrl.value() == 0):
            if(m == 3):
                pass
                LCD.fill(0)
            if(m == 2):
                pass
                LCD.fill(0)
            if(m == 1):
                pass
                LCD.fill(0)
            if(m == 0):
                fuelMenu()
                LCD.fill(0)
        LCD.show()
        if(HW.keyCheck() == 9):
            break
def maintenance():
    run = True
    a = 0
    b = 0
    while run:
        LCD.fill(0)
        n = 0
        c = colour(0,255,0)
        printstring("Maintenance",50,20,2,0,0,c)
        c = blue #string,xpos,ypos,size,charupdate,strupdate,c
        printstring("Test 1",60,40,1,0,0,c)
        printstring("Test 2",60,60,1,0,0,c)
        printstring("Test 3",60,80,1,0,0,c)
        a = HW.keyCheck()
        if(a == 1):
            b = b - 1
            if(b < 0):
                b = 0
        if(a == 2):
            b = b + 1
            if(b > 2):
                b = 2
        else:
            pass

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
            
        if(b == 0 and HW.keyCheck() == 5):
            print("1 is Good")
        if(b == 1 and HW.keyCheck() == 5):
            print("2 is Good")
        if(b == 2 and HW.keyCheck() == 5):
            print("3 is good")
                
        
        print(b)
        LCD.show()
        if(HW.keyCheck() == 9):
            break
def records():
    run = True
    while run:
        print("recor")
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Records",80,20,2,0,0,c)
        LCD.show()
        if(HW.keyCheck() == 9):
            break
def settings():
    run = True
    while run:
        print("sett")
        LCD.fill(0)
        c = colour(0,255,0)
        printstring("Settings",70,20,2,0,0,c)
        LCD.show()
        if(HW.keyCheck() == 9):
            break

# =============== Main ==============================
pwm = PWM(Pin(BL)) # Screen Brightness
pwm.freq(1000)
pwm.duty_u16(32768) # max 65535 - mid value

# Define pins for buttons and Joystick
keyA = Pin(15,Pin.IN,Pin.PULL_UP) # Normally 1 but 0 if pressed
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19,Pin.IN,Pin.PULL_UP)
keyY= Pin(21,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

LCD = vd.LCD_1inch3() # Initialise the display
LCD.fill(vd.colour(0,0,0)) # BLACK
LCD.show()


def drawMainMenu(m, yellow, blue):
        c = colour(255,0,0) 
        printstring("DMRS for V.240",17,10,2,0,0,c)
        c = yellow
        if m == 0:
            c = blue
        printstring("Diagnostics",35,50,2,0,0,c)
        c = yellow
        if m == 1:
            c = blue
        printstring("Maintenance",35,80,2,0,0,c)
        c = yellow
        if m == 2:
            c = blue
        printstring("Records",35,110,2,0,0,c)
        c = yellow
        if m == 3:
            c = blue
        printstring("Settings",35,140,2,0,0,c)
        c = yellow
        if m == 4:
            c = blue
        printstring("Quit Program",35,170,2,0,0,c)
        LCD.show()


# ======= Menu ==============  
def mainMenu():
    global m
    m = 0
    yellow = colour(255,255,0)
    blue = colour(0,0,255)
    running = True
    #while running: #begin menu "loop" except it's not a loop now, just a bunch self-referential menu functions
    drawMainMenu(m, yellow, blue) #draw inital menu to start with

    
    #functions called on key press via IRQ, _ used for throwaway var, IRQ requires a param for pin used, unneeded here
    def upHandler(_):
        global m
        m = m - 1
        if m < 0:
            m = 0
        print("in up handler")
            
    def downHandler(_):
        global m
        m = m + 1
        if m > 4:
            m = 4
        print("in down handler")   
    def ctrlHandler(_):
        global m
        if(m == 4): # Exit loop and HALT program
            running = False
        if(m == 3):
            settings()
            LCD.fill(0)
        if(m == 2):
            records()
            LCD.fill(0)
        if(m == 1):
            maintenance()
            LCD.fill(0)
        if(m == 0):
            diagnostics()
            LCD.fill(0)
        print("in cntrl Handler")       
    
    #Check joystick UP/DOWN/CTRL
    #impletmented using "p0.irq(lambda p:print(p))"-style IRQ handler from Pin class from machine library
    #functions set to trigger on falling edge only, defaults to rising and falling edges otherwise
    up.irq(upHandler(up), Pin.IRQ_LOW_LEVEL)
    down.irq(downHandler(down), Pin.IRQ_LOW_LEVEL)
    ctrl.irq(ctrlHandler(ctrl), Pin.IRQ_LOW_LEVEL)
    
# Finish
   # LCD.fill(0)
   # c = colour(255,0,0)
   # printstring("Halted",80,110,2,0,0,c)
   # LCD.show()
    # Tidy up
  #  utime.sleep(3)
  #  LCD.fill(0)
   # LCD.show()

mainMenu()