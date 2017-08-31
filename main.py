# v4.3
import os
import subprocess
import socket
import errno
import select
from threading import Thread
import thread
import threading
import ardcommands
sys = ardcommands.sys
time = ardcommands.time
sleep = time.sleep
initializeLedPins = ardcommands.initializeLedPins
initializeRelayPins = ardcommands.initializeRelayPins
getAllOutputPins = ardcommands.getAllOutputPins
getAllInputPins = ardcommands.getAllInputPins
setOutputPin = ardcommands.setOutputPin
setInputPin = ardcommands.setInputPin
connect = ardcommands.connect
setup = ardcommands.setup
turnOff = ardcommands.turnOff
turnOn = ardcommands.turnOn
blink = ardcommands.blink
getState = ardcommands.getState
getNextState = ardcommands.getNextState
getRow = ardcommands.getRow
getColumn = ardcommands.getColumn
getDiagonal = ardcommands.getDiagonal
letterToArray = ardcommands.letterToArray
text = ardcommands.text
reverse = ardcommands.reverse
combine = ardcommands.combine
smoothBlackout = ardcommands.smoothBlackout
getRandomArray = ardcommands.getRandomArray
blinkRandomArray = ardcommands.blinkRandomArray

# sys.argv[1:] is passed in initial main call
def main(args = []):
    global ard
    global allOutputPins
    global allInputPins
    global ledPins
    global relayPins
    global HOST
    global PORT
    global async
    global loopExitNow
    global videoExitNow
    global catchLoop
    global loopCommands
    global blackoutReadyState # command loop has turned off all of its pins

    # Global server settings
    HOST = 'localhost'
    PORT = 10000
    async = True

    # Initializing flags and containers
    loopExitNow = False
    videoExitNow = False
    catchLoop = False
    loopCommands = []
    blackoutReadyState = True

    # Handle command line arguments that are effective before initialization
    validArgs = ["?", "help", "-help", "-h", "/?", "-l", "-o", "-offline", "-i", "-input", "-r", "-relay", "-c"]
    validSecondArgs = ["-r", "-relay"]
    if (len(args) > 2):
        print "main.py takes only 2 argument. " + str(len(args)) + " arguments were given."
        exit()
    elif (len(args) > 1 and args[1] not in validSecondArgs):
        print args[1] + " is an invalid second argument. Valid second arguments are: %(validSecondArgs)s" % locals()
        print "Type \'main.py -help\' for a full list of arguments."
        exit()
    elif (len(args) > 0 and not args[0] in validArgs):
            print "%(args)s is not a valid argument. Type \'main.py -help\' for a list of arguments." % locals()
            exit()
    elif (len(args) > 0):
        if (args[0] == "?" or args[0] == "help" or args[0] == "-help" or args[0] == "-h" or args[0] == "/?"):
            helpPage(True)
        elif (args[0] == "-c"):
            commands(True)
        elif (args[0] != "-l" and args[0] != "-o" and args[0] != "-offline"):
            HOST = getIpAddress()
        elif (args[0] == "-l"):
            print "Host set to \'localhost\'."
            print
    else:
        HOST = getIpAddress()
		
	# Wait to import so that the help menu can be called on systems without nanpy installed yet
	from nanpy import (ArduinoApi, SerialManager)

    # Initialize pins, connect to Arduino, and setup pin modes
    ledPins = initializeLedPins(26)
    relayPins = initializeRelayPins([46, 47, 48, 49, 50, 51, 52])
    connect()
    setup()
    allOutputPins = getAllOutputPins()
    allInputPins = getAllInputPins()

    # Handle command line arguments that are effective after initialization
    if (len(args) > 0):
        # Check to see what state relays should be started in
        if ("-r" in args or "-relay" in args):
            turnOn(relayPins, 0)
            print
            print "Relays %(relayPins)s are set to ON." % globals()
            print
        if (args[0] == "-o" or args[0] == "-offline"):
            print
            print "Offline mode enabled."
            print "Use \'server CURRENT_IP\' to start server at IP address and override current host address: \'%(HOST)s\'" % globals()
            inputPromptWithHeader()
        elif (args[0] == "-i" or args[0] == "-input"):
            inputPromptWithHeader()

    serverStartup()

def getIpAddress():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return str(s.getsockname()[0])
    except socket.error as serr:
        if (serr.errno != errno.ENETUNREACH):
            raise serr
        print
        print "The network is currently unavailable. Please check your connection."
        print "Error number: ", serr.errno
        print
        print "Press \'Enter\' to continue in offline mode or \'Crtl-C\' to abort..."
        try:
            t = time.time()
            while 1:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]: # non-blocking stdin
                    line = raw_input()
                    break
                if (int(time.time() - t) == 7):
                    print
                    print "-- Exit on Network Failure --"
                    exit()
        except KeyboardInterrupt:
            print
            print "-- Exit on Network Failure --"
            exit()
        print "Continuing with offline mode connection to %(HOST)s[%(PORT)s]..." % globals()
        print "----------------------------------------------------------------"
        main(["-o"])

def serverStartup(newHost=""):
    global serversocket
    global HOST

    # Server settings
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        # Allow user to start server from offline mode with specified address
        if (newHost):
            if (newHost.upper() == "CURRENT_IP"):
                HOST = getIpAddress()
        serversocket.bind((HOST, PORT))
        serversocket.listen(5)
    except socket.error as serr:
        print
        if (serr.errno == errno.EADDRINUSE):
            print "The requested address: %(HOST)s[%(PORT)s] is already in use. Please close any running connections and try again." % globals()
            print "Error number: " + str(serr.errno)
        else:
            raise serr
        exit()

    print
    print "Listening for commands... [HOST: %(HOST)s] [Port: %(PORT)s]" % globals()
    try:
        serverLoop()
    except KeyboardInterrupt:
        endScript("Exit on KeyboardInterrupt")

# Infinite loop creating threaded client objects
def serverLoop():
    while 1:
        # Accept connections
        (clientsocket, address) = serversocket.accept()
        newRemoteThread = ClientThread(False, (clientsocket, address))
        newRemoteThread.start()
        if (not async):
            newRemoteThread.join()

# Set the value of exitNow, which is used to signal exit of the command loop
def setLoopExitNow(val):
    global loopExitNow
    loopExitNow = val
    if (not val):
        print "loopExit = ", val
    else:
        print
        print "Exiting loop at next iteration..."
        print

# Seperate exit flag for video loop
def setVideoExitNow(val):
    global videoExitNow
    videoExitNow = val
    if (not val):
        print "videoExit = ", val
    else:
        print
        print "Video exit flagged..."
        print

# Global value that controls whether commands should wait for the previous command to finish
def setAsync(val):
    global async
    async = val
    print "async = ", val

# Start omxplayer loop
def startVideo(video="console-video.mp4", loops=-1):
    global videoExitNow
    videoExitNow = False

    while (loops > 0 or loops == -1) and not videoExitNow:
        try:
            print "Playing video..."
            a = subprocess.call(["omxplayer", "-b", video])
        except KeyboardInterrupt:
            print
            print "-- Exit on KeyboardInterrupt --"
            break
    videoExitNow = False

# Stop playback of omxplayer loop
def stopVideo():
    setVideoExitNow(True)
    a = subprocess.call(["pkill", "-f", "omxplayer.bin"])
    print
    print "Video stopped."
    print

# Exit loop, stop video, and turn off all pins (including relays) for blackout
def blackout():
    global blackoutReadyState
    blackoutList = ["setLoopExitNow(True)", "stopVideo()"]
    for command in blackoutList:
        newLocalThread = ClientThread(True)
        newLocalThread.msg = command
        newLocalThread.start()
        newLocalThread.join()

    while (True):
        if (blackoutReadyState):
            break
        sleep(1)
    turnOff(allOutputPins)

# Loop over a set of commands
def commandLoop(iterations):
    global async
    global blackoutReadyState
    tmpAsync = async
    setAsync(True) # Asynchronous execution must be enabled to stop an infinite loop with the setLoopExitNow command
    blackoutReadyState = False

    global loopExitNow
    global loopCommands
    loopExitNow = False
    loopForever = False
    if (iterations == -1):
        loopForever = True

    i = 0
    while (i < iterations or loopForever) and not loopExitNow:
        for command in loopCommands:
            if command == "exit" or command == "exit()":
                endScript()
            else:
                if (loopExitNow):
                    break
                newLocalThread = ClientThread(True)
                newLocalThread.msg = command
                newLocalThread.start()
                newLocalThread.join() # Wait for previous command to finish
        i = i + 1
    # Cleanup
    blackoutReadyState = True
    loopExitNow = False
    del loopCommands[:]
    setAsync(tmpAsync) # return async setting to its previous value

# Threaded client object
# Can be initialized to connect to a socket and receive commands or to solely execute commands stored in the msg variable (dependant on value of local variable)
class ClientThread (Thread):
    def __init__(self, local, (clientsocket, address)=(None, None)):
        Thread.__init__(self)
        (self.clientsocket, self.address) = (clientsocket, address)
        self.local = local
        #print "[+] New socket thread started."

    def handle(self, clientsocket, address):
        self.chunks = []
        while 1:
            try:
                self.chunk = self.clientsocket.recv(1024)
            except socket.error as serr:
                if serr.errno != errno.ECONNRESET:
                    raise serr
                print
                print "Client closed connection..."
                print
                self.stop()
            if self.chunk == '':
                break
            self.chunks.append(self.chunk)
        self.msg = ''.join(self.chunks)
        self.execute()
        
    # Execution for remote connections and local input prompt entries.
    def execute(self):
        global catchLoop
        global loopCommands
        global shv # For manual use when data needs to be shared between threads
        global sha # "     "
        
        self.lowercaseMsg = self.msg.lower()
	
        # Turn off all pins and shutdown on exit or exit()
        if (self.lowercaseMsg == "exit" or self.lowercaseMsg == "exit()"):
            endScript()

        # Pull up user input
        if (self.lowercaseMsg == "input"):
            inputPromptWithHeader()

        # Pull up help screen
        if (self.lowercaseMsg == "help" or self.lowercaseMsg == "?"):
            helpPage()

        # Catch and handle loop signal
        if ("loop(" in self.lowercaseMsg):
            if (not catchLoop): # Catch first loop sign
                catchLoop = True
                print
                print "Collecting commands to be looped..."
                print "Start execution of loop by sending \'loop(iterations)\' or \'loop(-1)\' (infinite)."
                print
                self.stop()
            else:
                catchLoop = False
                iterations = self.msg[5:-1] # Get # from loop(#) format
                print
                if (iterations == "-1"):
                    print "Starting infinite loop of commands:"
                    print loopCommands
                    print "Send setExitNow(True) to flag the loop for exit."
                    print
                    try:
                        commandLoop(-1)
                    except KeyboardInterupt:
                        print
                        print "-- Loop exit on KeyboardInterupt --"
                    self.stop()
                elif (iterations.isdigit()):
                    try:
                        print "Starting loop of commands:"
                        print loopCommands
                        print "Iterations: ", iterations
                        print
                        print "Use setLoopExitNow(True) to flag the loop for early exit."
                        try:
                            commandLoop(int(iterations))
                        except KeyboardInterupt:
                            print
                            print "-- Loop exit on KeyboardInterupt --"
                        self.stop()
                    except ValueError:
                        print iterations + "is not an integer. Please pass a positive integer or -1 (indefinite)."
                else:
                    print iterations + "is not a valid iteration number for commandLoop(). Please pass a positive integer or -1 (indefinite)."
                    del loopCommands[:]
		    self.stop()
	
        # Execute a python file if present
        if (self.lowercaseMsg[:4] == "file"):
            # Check if the user already specified the file in the format "file:<filepath>"
            if (len(self.msg) > 5 and self.msg[4] == ":"):
                self.file = self.msg[5:]
            else:
                self.file = raw_input("execute file $$>")
            try:
                self.f = open(self.file)
                self.f.close()
            except IOError:
                print "File does not exist or could not be opened. Please try again."
                self.stop()
            execfile(self.file)
        
        # Start server
        if (self.lowercaseMsg == "server" or self.lowercaseMsg == "listen" or self.lowercaseMsg == "close"):
            serverStartup()
            
        # Start server with argument
        if ("server" in self.lowercaseMsg):
            if (self.lowercaseMsg.find(" ") != -1):
                param = self.lowercaseMsg[self.lowercaseMsg.find(" ") + 1:]
                serverStartup(param)

        # Execute or catch user command
        if (catchLoop):
            loopCommands.append(self.msg)
            print "Command \'%s\' added to command list." % self.msg
        else:
            try:
                exec(self.msg)
            except Exception as e:
                print(e)

        # End the current thread
        self.stop()

    # Check to see if the connection is from the local input prompt.
    # If it is, execute the commands, otherwise collect data from the socket connection.
    def run(self):
        if (self.local):
            self.execute()
        else:
            self.handle(self.clientsocket, self.address)
        
    # End the current thread
    def stop(self):
        sys.exit(1)

def inputPromptWithHeader():
    print
    print "-- Local Command Entry --"
    print "Port listening is no longer active."
    print "Type \"server\" or \"listen\" to resume."
    print "----------------------------------------------------------------"
    inputPrompt()

def inputPrompt():
    while 1:
        try:
            userInput = raw_input("$$>")
        except KeyboardInterrupt:
            endScript("Exit on KeyboardInterrupt")
        newLocalThread = ClientThread(True)
        newLocalThread.msg = userInput
        newLocalThread.start()
        newLocalThread.join()

# End the script
def endScript(reason="Complete"):
    turnOff(ledPins)
    turnOn(relayPins) # Relay connections must have power even without program running; driving the pin HIGH activates circuits connected to the Normally Closed terminal (NC)
    print
    print "-- %(reason)s --" % locals()
    os._exit(0)

def helpPage(exitAfter=False):
    print
    print "----------- Remote Command Server for Arduino [v4.3] -----------"
    print "                     Author: Jack McKernan"
    print
    print
    print "                   Command Line Arguments"
    print "----------------------------------------------------------------"
    print
    print "-l              Host set to \'localhost\' for use with client.py on a local machine."
    print
    print "-o or -offline  Offline mode: local input prompt will be available upon startup. Must be first argument."
    print "                Host defaults to \'localhost\' should the server be started from the input prompt."
    print "                Use serverStartup(<new host>) to overwrite."
    print
    print "-i              Local input prompt will be available upon startup."
    print "                Host will be set to current IP address."
    print
    print "-r or -relay    Start relays with power to the NC circuit (without -r, default is to NO circuit)."
    print
    print "-h, -help, or ? Access this help page."
    print
    print "-c              Display full list of program commands."
    print
    if (exitAfter):
		exit()

def commands(exitAfter=False):
    print
    print "                                               General Command List"
    print "  --------------------------------------------------------------------------------------------------------------------"
    print
    print "turnOn(int/list pinNumbers, double delay=0)   - Write one or more Arduino pins to HIGH."
    print "                                           -\'delay\' determines how long the process should wait after turning on each"
    print "                                             invdividual pin."
    print
    print "turnOff(int/list pinNumbers, double delay=0)  - Write one or more Arduino pins to LOW."
    print "                                           -\'delay\' determines how long the process should wait after turning on each"
    print "                                             invdividual pin."
    print
    print "blink(int/list/string pinNumbers, double seconds=1, int iteration=1, bool waitAfter=True, double delay)"
    print "                                           - Blink one or more LEDs. Strings are passed to the \'text()\' function. LEDs"
    print "                                             remains in changed state for \'seconds.\'"
    print "                                           -\'waitAfter\' determines if a delay of \'seconds\' should be added after the"
    print "                                             LED's state is changed back."
    print "                                           -\'delay\' determines how long the process should wait after turning on each"
    print "                                             invdividual pin."
    print "                                           - If state of LED is changed anytime after this method is called, the blink"
    print "                                             pattern will not be affected to represent this change."
    print
    print "getState(int/list pinNumbers)                 - Returns the integer representation of pin state."
    print "                                           - Returns a list of pin states when passed a list or a single integer when"
    print "                                             passed a single integer."
    print
    print "getNextState(int/list pinNumbers)             - Returns the integer representation of the pin state opposite that of its"
    print "                                             current state."
    print "                                           - Returns a list of pin states when passed a list or a single integer when"
    print "                                             passed a single integer."
    print
    print "printState(int pin, int/bool state)        - Prints the pin number and state (as HIGH or LOW) in a verbose format."
    print
    print "getRow(int rowNumber)                      - Returns an array of pin numbers in a given row."
    print "                                           - Row numbers are 1 through 5."
    print
    print "getColumn(int columnNumber)                - Returns an array of pin numbers in a given column."
    print "                                           - Column numbers are 1 through 5."
    print
    print "getDiagonal(int diagonalNumber, string diagonalDirection)"
    print "                                           - Returns an array of pin numbers in a given diagonal."
    print "                                           - Diagonal numbers are 1 through 9."
    print "                                           - Diagonal directions are \'LR\' (left to right) and \'RL\' (right to left)."
    print
    print "letterToArray(char letter)                 - Returns an array of pin numbers that form the uppercase version of the"
    print "                                             given letter."
    print "                                           - All 26 letters of the English alphabet are valid. Passing space will"
    print "                                             return an empty array."
    print
    print "text(String anyString, double seconds=1, int iterations=1, double delay=0)"
    print "                                           - Uses the methods letterToArray() and blink() to display a string one"
    print "                                             characater at a time."
    print "                                           -\'seconds,\' \'iterations,\' and \'delay\' are all parameters passed directly"
    print "                                             to the blink() function."
    print "                                           -\'seconds\' controls how long each letter is lit for."
    print "                                           -\'iterations\' will blink the same letter repeatadly before moving to the next."
    print "                                           - To repeat an entire string, see the loop() functionality below."
    print "                                           -\'delay\' determines how long the process should wait after turning on each"
    print "                                             invdividual pin."
    print
    print "reverse(list anyList)                      - Return a reversed list."
    print
    print "combine(list aList, bList)                 - Combines two lists and corrects for duplicate entries."
    print
    print "getRandomArray()                           - Returns an array of random pin numbers."
    print "                                           - Number of pins in the list can be between 5 and 10."
    print
    print "blinkRandomArray(double seconds=1, int iterations=1, bool waitAfter=False, double delay=0)"
    print "                                           - Uses the methods getRandomArray() and blink() to blink a random array"
    print "                                             of pin numbers."
    print "                                           -\'seconds,\' \'iterations,\' \'waitAfter,\'and \'delay\' are all parameters"
    print "                                             passed directly to the blink() function."
    print "                                           -\'seconds\' controls how long each set of pins is lit for."
    print "                                           -\'iterations\' will blink the same array repeatadly before moving to the next."
    print "                                           - To repeatedly blink randomly, see the loop() functionality below."
    print "                                           -\'delay\' determines how long the process should wait after turning on each"
    print "                                             invdividual pin."
    print
    print "                                                     Looping"
    print "  --------------------------------------------------------------------------------------------------------------------"
    print
    print "loop()                                     - Starts the process of collecting commands for the loop."
    print "                                           - On-screen instructions should explain."
    print
    print "loop(int iterations)                       - After completing the above process, this command starts the loop."
    print "                                           -\'iterations\' can be any positive number or -1 for an infinite loop."
    print "                                           - Exit from the loop can be flagged with setLoopExitNow(True)."
    print 
    print "setLoopExitNow(bool val)                   - Flag a looping command for exit (True) or reset the loop flag (False)."
    print
    print "                                                      Video"
    print "  --------------------------------------------------------------------------------------------------------------------"
    print "startVideo(String file)                    - Start playback of a video file on the display."
    print "                                           - Default file = \'console-playback.mp4\'"
    print
    print "setVideoExitNow(bool)                      - Flag video playback for exit by sending True."
    print
    print "                                                      Misc."
    print "  --------------------------------------------------------------------------------------------------------------------"
    print
    print "setAsync(bool)                             - Because the server progam is threaded, multiple clients can connect, and"
    print "                                             multiple commands can be executed simultaneously. setAsync(False) turns off"
    print "                                             this ability to some extent by calling thread.join() after each command is"
    print "                                             executed. This method can be used to turn asynchronous execution on or off."
    print "                                             NOTE: async is enabled by default during a loop in order to allow access"
    print "                                             to the loop exit commands and prevent accidental infinite loops."
    print "                                           - On = True      Off = False"
    if (exitAfter):
        exit()
		
if __name__ == "__main__":
    main(sys.argv[1:])
