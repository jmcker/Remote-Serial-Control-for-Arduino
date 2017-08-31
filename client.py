# v4.3
import socket
import errno
import sys

print "Remote Command Sender for Arduino [v1.0]"
print "Type \"close\" to stop the execution of this program."
print "Type \"exit\" to stop the execution of both this program and the server program."

HOST = '192.168.1.103'
PORT = 10000
args = sys.argv[1:]
if (len(args) > 0):
    ip = args[0]
    if (ip[0] == "["):
        HOST = ip[1:-1]
        args.pop(0)
    # Check if only the ending loop(#) command is present.
    # Signifies that the whole command should be looped, so loop() is added at args[0].
    if (any("loop(" in arg for arg in args) and not any("loop()" in arg for arg in args)):
        args.insert(0, "loop()")

    # Default to async disabled and re-enable after execution of all command line args
    #args.insert(0, "setAsync(False)")
    #args.append("setAsync(True)")

# Execute provided arguments
for arg in args:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((HOST, PORT))
    except socket.error as serr:
        print
        if (serr.errno == errno.ECONNREFUSED):
            print "Could not connect to %(HOST)s[%(PORT)s]." % locals()
            print "Please check network connections and ensure that the serverside program is running."
        else:
            raise serr
        print "Error number: ", serr.errno
        exit()
    
    if arg == "close":
        s.close()
        exit()
    elif arg == "exit" or arg == "exit()":
        s.send(arg)
        s.close()
        exit()
    else:
        s.send(arg)
        s.close()

# Switch to manual command input
while 1:
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((HOST, PORT))
    except socket.timeout:
        print
        print "The connection to %(HOST)s[%(PORT)s] timed out." % locals()
        print "Please check network connections and ensure that the serverside program is running."
        exit()
    except socket.error as serr:
        print
        if (serr.errno == errno.ECONNREFUSED):
            print "Could not connect to %(HOST)s[%(PORT)s]. The server refused the connection." % locals()
        elif (serr.errno == errno.ETIMEDOUT):
            print "The connection to %(HOST)s[%(PORT)s] timed out. Please check that the serverside program is running." % locals()
        else:
            raise serr
        print "Error number: ", serr.errno
        exit()            
    try:
        msg = raw_input("to %(HOST)s[%(PORT)s] $$>" % locals())
    except KeyboardInterrupt:
        print
        print "-- Exit on KeyboardInterrupt --"
        s.close()
        exit()
    if msg == "input":
        print
        print "Local command input has been enabled on the target machine."
        print "Remote command listening will be disabled until server is re-engaged."
        print
    if msg == "close":
        s.close()
        exit()
    if msg == "exit" or msg == "exit()":
        s.send(msg)
        s.close()
        exit()
        
    try:
        s.send(msg)
        s.close()
    except socket.error as serr:
        if serr.errno != errno.ECONNRESET:
            raise serr
        print
        print "Connection was reset by server. Please run client.py to reconnect."
        print "Error number: ", serr.errno
        exit()
