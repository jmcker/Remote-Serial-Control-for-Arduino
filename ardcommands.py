# v4.3
import sys
import serial
import time
from random import randint
from random import sample
sleep = time.sleep

global allOutputPins
global allInputPins
global ledPins
global relayPins
allOutputPins = []
allInputPins = []
ledPins = []
relayPins = []

# Initialize array of pin numbers starting at 2 (1 is unusable)
def initializeLedPins(numberOfPins):
    global ledPins
    ledPins = []
    for i in range(2, numberOfPins + 1):
        ledPins.append(i)
    return ledPins
    
# Initialize pins setup for connection to a relay (sink current when driven LOW)
def initializeRelayPins(relayPinList=[46, 47, 48, 49, 50, 51, 52, 53]):
    global relayPins
    relayPins = []
    for pin in relayPinList:
         relayPins.append(pin)   
    return relayPinList

# Connection to Arduino
def connect():
    global ard
    # Connection
    try:
        print "Connecting to Arduino..."
        connection = SerialManager() # port and baud rate ?
        ard = ArduinoApi (connection = connection)
    except:
        print "Could not connect to Arduino."
        exit()
    print "Connected successfully."
    print
    return ard
    
# Setupt the pin modes
def setup():
    global allOutputPins
    global allInputPins
    global ledPins
    global relayPins
    allOutputPins = combine(ledPins, relayPins)
    
    if len(allOutputPins) > 0:
        print "Initializing OUTPUT pin list..."
        for pin in allOutputPins:
            ard.pinMode(pin, ard.OUTPUT)
        print "Pins %(allOutputPins)s have been initialized as OUTPUT." % globals()
        print
    
    if len(allInputPins) > 0:
        print "Initializing INPUT pin list..."
        for pin in allInputPins:
            ard.pinMode(pin, ard.INPUT)
        print "Pins %(allInputPins)s have been initialized as INPUT." % globals()

# Return the full list of currently initialized OUTPUT pins
def getAllOutputPins():
    global allOutputPins
    return allOutputPins
    
# Return the full list of currently initialize INPUT pins
def getAllInputPins():
    global allInputPins
    return allInputPins

# Initialize an output pin
def setOutputPin(pin):
    ard.pinMode(pin, ard.OUTPUT)
    print "Pin %(pin)s has been initialized as OUTPUT" % locals()

# Initialize an input pin
def setInputPin(pin):
    ard.pinMode(pin, ard.INPUT)
    print "Pin %(pin)s has been initialized as INPUT" % locals()

# Turn off LEDs
# Accepts list or single integer
# delay determines how long the process should wait before performing its next action (next LED in list or different command)
def turnOff(ledPins, delay=0):
    if (isinstance(ledPins, list)):
        for pin in ledPins:
            ard.digitalWrite(pin, 0)
            printState(pin, 0)
            sleep(delay)
    elif (isinstance(ledPins, int)):
        pin = ledPins
        ard.digitalWrite(pin, 0)
        printState(pin, 0)
        sleep(delay)
    else:
        print "Unexpected object type was passed to turnOff(). Please pass list or integer."

# Turn on LEDs
# Accepts list or single integer
# delay determines how long the process should wait before performing its next action (next LED in list or different command)
def turnOn(ledPins, delay=0):
    if (isinstance(ledPins, list)):
        t0 = time.time()
        for pin in ledPins:
            ard.digitalWrite(pin, 1)
            printState(pin, 1)
            sleep(delay)
        t1 = time.time()
        print t1-t0
    elif (isinstance(ledPins, int)):
        pin = ledPins
        ard.digitalWrite(pin, 1)
        printState(pin, 1)
        sleep(delay)
    else:
        print "Unexpected object type was passed to turnOn(). Please pass list or integer."
        

# Old method for toggling relay; toggles opposite of state
def toggleRelay(relayPins, state, delay=0):
    if state in [0, 1]:
        state = (int)(not state) # Relay must be driven LOW (0) to activate switch (1)
        if (isinstance(relayPins, list)):
            t0 = time.time()
            for pin in relayPins:
                ard.digitalWrite(pin, state)
                printState(pin, state, 1)
                sleep(delay)
            t1 = time.time()
            print t1-t0
        elif (isinstance(relayPins, int)):
            pin = relayPins
            ard.digitalWrite(pin, state)
            printState(pin, state, 1)
            sleep(delay)
        else:
            print "Unexpected object type was passed to toggleRelay(). Please pass list or integer."
    else:
        print "State: %(state)s is not a valid state. Please pass O (OFF) or 1 (ON)."
        

# Blink LEDs
# Using getNextState() ensures LEDs blink even if already on
# If state of LED is changed anytime after the call to getNextState(), the blink pattern will not be affected to represent this change
# Accepts list or single integer for pins
# Seconds is the time between on and off; default is 1
# Iterations is the number of blinks; default is 1
# waitAfter determines whether a final sleep of "seconds" length should be added after the blink is over--this makes the pattern look nice when looped; default is True
# delay determines how long the process should wait before performing its next action (next LED in list or different command)
def blink(ledPins, seconds=1, iterations=1, waitAfter=True, delay=0):
    for i in range(0, iterations):
        if (isinstance(ledPins, list)):
            nextState = getNextState(ledPins)
            i = 0
            t0 = time.time()
            for pin in ledPins:
                ard.digitalWrite(pin, nextState[i])
                printState(pin, nextState[i])
                sleep(delay)
                i = i + 1
                
            t1 = time.time()
            print t1-t0
            print "Waiting..."
            sleep(seconds)
            
            nextState = [(int)(not state) for state in nextState]
            i = 0
            for pin in ledPins:
                ard.digitalWrite(pin, nextState[i])
                printState(pin, nextState[i])
                sleep(delay)
                i = i + 1
        elif (isinstance(ledPins, int)):
            t0 = time.time()
            pin = ledPins
            nextState = getNextState(pin)
            ard.digitalWrite(pin, nextState)
            printState(pin, nextState)
            
            t1 = time.time()
            print t1-t0
            print "Waiting..."
            sleep(seconds)
            
            nextState = (int)(not nextState)
            ard.digitalWrite(pin, nextState)
            printState(pin, nextState)
            sleep(delay)
        elif (isinstance(ledPins, basestring)):
            text(ledPins)
        else:
            print "Unexpected object type was passed to turnOff(). Please pass list or integer."
            return
        if (waitAfter):
            print "Waiting..."
            sleep(seconds)

# Get current state of a single LED or list of LEDs
# Queries the current state and returns it
def getState(ledPins):
    if (isinstance(ledPins, list)):
        nextState = []
        for pin in ledPins:
            nextState.append((int)(ard.digitalRead(pin)))
        return nextState
    if (isinstance(ledPins, int)):
        pin = ledPins
        return (int)(ard.digitalRead(pin))
    else:
        print "Unexpected object type was passed to getState(). Please pass single integer or list."

# Get next state of single LED or list of LEDs
# Queries the current state and returns the opposite
def getNextState(ledPins):
    if (isinstance(ledPins, list)):
        nextState = []
        for pin in ledPins:
            nextState.append((int)(not ard.digitalRead(pin)))
        return nextState
    if (isinstance(ledPins, int)):
        pin = ledPins
        return (int)(not ard.digitalRead(pin))
    else:
        print "Unexpected object type was passed to getNextState(). Please pass single integer or list."

# Print the pins current state as HIGH or LOW
def printState(pin, state, isRelay=0):
    if not isRelay:
        if (state == 0):
            print "Pin %(pin)s is set to LOW." % locals()
        else:
            print "Pin %(pin)s is set to HIGH." % locals()
    else:
        if (state == 0):
            print "Relay %(pin)s is set to ON (NC)." % locals()
        else:
            print "Relay %(pin)s is set to OFF (NO)." % locals()

# Get row of LEDs
# Returns array of LEDs in a given row
# Accepts integer row number
def getRow(row):
    if (row == 1):
        return [2, 3, 4, 5, 6]
    elif (row == 2):
        return [7, 8, 9, 10, 11]
    elif (row == 3):
        return [12, 13, 14, 15, 16]
    elif (row == 4):
        return [17, 18, 19, 20, 21]
    elif (row == 5):
        return [22, 23, 24, 25, 26]
    else:
        print "Row %(row)s is not defined. Please try again." % locals()
        exit()

# Get column of LEDs
# Returns array of LEDs in a given column
# Accepts integer column number
def getColumn(column):
    if (column == 1):
        return [2, 7, 12, 17, 22]
    elif (column == 2):
        return [3, 8, 13, 18, 23]
    elif (column == 3):
        return [4, 9, 14, 19, 24]
    elif (column == 4):
        return [5, 10, 15, 20, 25]
    elif (column == 5):
        return [6, 11, 16, 21, 26]
    else:
        print "Column %(column)s is not defined. Please try again." % locals()
        exit()

# Get diagonal of LEDs
# Returns array of LEDs in a given directional diagonal
# Accepts integer diagonal number and direction of diagonal as string
def getDiagonal(diagonal, direction = "LR"):
    if (direction == "LR"):
        if (diagonal == 1):
            return [6]
        elif (diagonal == 2):
            return [5, 11]
        elif (diagonal == 3):
            return [4, 10, 16]
        elif (diagonal == 4):
            return [3, 9, 15, 21]
        elif (diagonal == 5):
            return [2, 8, 14, 20, 26]
        elif (diagonal == 6):
            return [7, 13, 19, 25]
        elif (diagonal == 7):
            return [12, 18, 24]
        elif (diagonal == 8):
            return [17, 23]
        elif (diagonal == 9):
            return [22]
        else:
            print "Diagonal %(diagonal)s is not defined. Please try again." % locals()
            exit()
    elif (direction == "RL"):
        if (diagonal == 1):
            return [2]
        elif (diagonal == 2):
            return [3, 7]
        elif (diagonal == 3):
            return [4, 8, 12]
        elif (diagonal == 4):
            return [5, 9, 13, 17]
        elif (diagonal == 5):
            return [6, 10, 14, 18, 22]
        elif (diagonal == 6):
            return [11, 15, 19, 23]
        elif (diagonal == 7):
            return [16, 20, 24]
        elif (diagonal == 8):
            return [21, 25]
        elif (diagonal == 9):
            return [26]
        else:
            print "Diagonal %(diagonal)s is not defined. Please try again." % locals()
            exit()
    else:
        print "Direction %(direction)s is not defined. Please try again." % locals()
        exit()
        
# Return the array of LED pins that represent a letter
def letterToArray(letter):
    if (len(letter) == 1):
        letter = letter.upper()
        if (letter == "A"):
            return [4, 8, 10, 12, 13, 14, 15, 16, 17, 21, 22, 26]
        elif (letter == "B"):
            return [2, 3, 4, 5, 7, 11, 12, 13, 14, 15, 17, 21, 22, 23, 24, 25, 26]
        elif (letter == "C"):
            return [3, 4, 5, 6, 7, 12, 17, 23, 24, 25, 26]
        elif (letter == "D"):
            return [2, 3, 4, 5, 7, 11, 12, 16, 17, 21, 22, 23, 24, 25]
        elif (letter == "E"):
            return [2, 3, 4, 5, 6, 7, 12, 13, 14, 17, 22, 23, 24, 25, 26]
        elif (letter == "F"):
            return [2, 3, 4, 5, 6, 7, 12, 13, 14, 17, 22]
        elif (letter == "G"):
            return [3, 4, 5, 6, 7, 12, 14, 15, 16, 17, 21, 23, 24, 25, 26]
        elif (letter == "H"):
            return [2, 6, 7, 11, 12, 13, 14, 15, 16, 17, 21, 22, 26]
        elif (letter == "I"):
            return [2, 3, 4, 5, 6, 9, 14, 19, 22, 23, 24, 25, 26]
        elif (letter == "J"):
            return [2, 3, 4, 5, 6, 9, 14, 17, 19, 23, 24]
        elif (letter == "K"):
            return [2, 5, 6, 7, 9, 12, 13, 17, 19, 22, 25, 26]
        elif (letter == "L"):
            return [2, 7, 12, 17, 22, 23, 24, 25, 26]
        elif (letter == "M"):
            return [2, 6, 7, 8, 10, 11, 12, 14, 16, 17, 21, 22, 26]
        elif (letter == "N"):
            return [2, 6, 7, 8, 11, 12, 14, 16, 17, 20, 21, 22, 26]
        elif (letter == "O"):
            return [3, 4, 5, 7, 11, 12, 16, 17, 21, 23, 24, 25]
        elif (letter == "P"):
            return [2, 3, 4, 5, 7, 11, 12, 13, 14, 15, 17, 22]
        elif (letter == "Q"):
            return [3, 4, 5, 7, 11, 12, 16, 17, 20, 23, 24, 26]
        elif (letter == "R"):
            return [2, 3, 4, 5, 7, 11, 12, 13, 14, 15, 17, 20, 22, 26]
        elif (letter == "S"):
           return [3, 4, 5, 6, 7, 13, 14, 15, 21, 22, 23, 24, 25]
        elif (letter == "T"):
            return [2, 3, 4, 5, 6, 9, 14, 19, 24]
        elif (letter == "U"):
            return [2, 6, 7, 11, 12, 16, 17, 21, 23, 24, 25]
        elif (letter == "V"):
            return [2, 6, 7, 11, 12, 16, 18, 20, 24]
        elif (letter == "W"):
            return [2, 6, 7, 11, 12, 14, 16, 17, 19, 21, 23, 25]
        elif (letter == "X"):
            return [2, 6, 8, 10, 14, 18, 20, 22, 26]
        elif (letter == "Y"):
            return [2, 6, 8, 10, 14, 19, 24]
        elif (letter == "Z"):
            return [2, 3, 4, 5, 6, 10, 14, 18, 22, 23, 24, 25, 26]
        elif (letter == " "):
            return []
        else:
            print letter, " is not a valid character."
    else:
        print "Please enter a single character only."

# Print to the LEDs one letter at a time
def text(text, seconds=1, iterations=1, delay=0):
    for letter in text:
        blink(letterToArray(letter), seconds, iterations, False, delay)
            
# Accepts a list and returns a list of the reverse order
def reverse(alist):
    return alist[::-1]

# Combines two arrays without allowing duplicates
def combine(a, b):
    return a + list(set(b)-set(a))

# Basic pattern to be run as a smooth way of shutting down
def smoothBlackout():
    turnOn(reverse(getRow(1)), .1)
    turnOn(reverse(getRow(2)), .1)
    turnOn(reverse(getRow(3)), .1)
    turnOn(reverse(getRow(4)), .1)
    turnOn(reverse(getRow(5)), .1)
    sleep(.1)
    turnOff(reverse(getRow(1)), .1)
    turnOff(reverse(getRow(2)), .1)
    turnOff(reverse(getRow(3)), .1)
    turnOff(reverse(getRow(4)), .1)
    turnOff(reverse(getRow(5)), .1)

def getRandomArray():
    numOfPins = randint(5, 10)
    return sample(xrange(min(ledPins), max(ledPins)), numOfPins)

# Pattern of random blinking lights
def blinkRandomArray(seconds=1, iterations=1, waitAfter=False, delay=0):
    numOfPins = randint(5, 10)
    pinNumbers = sample(xrange(min(ledPins), max(ledPins)), numOfPins)
    blink(pinNumbers, seconds, iterations, False, delay)
