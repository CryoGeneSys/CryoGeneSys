from machine import Pin,SPI,PWM


# Define pins for buttons and Joystick
keyA = Pin(15,Pin.IN,Pin.PULL_UP) # Normally 1 but 0 if pressed
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19,Pin.IN,Pin.PULL_UP)
keyY = Pin(21,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)


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
        elif(a == 1):
            a = 0
            running = False
    return m
