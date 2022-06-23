###Fuel Injection System Testing
###OBD Black Box Connected to LH-2.4 or LH-3.1 Fuel Injection System Computer Via Probe Port 2

import MenuPrompts as prompt
import ProbePassthrough as probe
import ButtonPassthrough as button
import LEDPassthrough as ledp
import utime as time
import CarInfo
import HardwareControl as HW

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
  "411": "Fault: Throttle Sensor Signal Missing or Faulty" #LH3.1 Only
  }

checkEngineLightDictionary = {
    "off": "Check Engine Light Should Be Off",
    "on": "Check Engine Light Should Be On"
    } #If getting LH2.4 errors on LH3.1 or vice versa, Shit is really really bad. Good luck!
    
def fuelCode(led_code): #This function is probably superfluous with the dictionary but whatever
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
def clear():
    c = colour(255,0,0)
    printstring("Turn Ignition to Position II",20,20,2,0,0,c)
    probe.port2()
    button.clearPress()
    time.sleep(4)
    button.clearPress()
    time.sleep(2)
    button.press()
    a = ledp.get()
    fuelCode(a)

###Function 1: Retrieval of stored codes
def fuelFunction1():
    a = 0
    b = 0
    while b < 3:
        if b == 0:
            print("This Function Will Pull The First Stored Code If Any")
        else:
            print("Do you wish to check for anymore stored codes?") #A yes B No C should be Back and D should be Home
            if UB.keyA.value() == 0:
                c = True
            if UB.keyB.value() == 0:
                c = False
        prompt.ignitionPrompt() #all prompts should have wait
        probe.port2() #as opposed to port3 or port6
        button.press() #as opposed to clearPress
        ledp.get(a)
        print(fuelCode(a))
        if c == False:
            probe.none()
            break
        b =+ 1

###Function 2: Testing ECU Inputs
def fuelFunction2():
    print("This tests these ECU inputs: Throttle Switch/Sensor, Engine RPM Signal, AC Microswitch Signal, and AC Compressor Signal.")
    prompt.ignitionPrompt()
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

