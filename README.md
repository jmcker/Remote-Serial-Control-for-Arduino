# Remote-Serial-Control-for-Arduino #

This program allows a client to control an Arduino via a remote host and [nanpy](https://pypi.python.org/pypi/nanpy)). Originally developed for a rather intricate theater prop, the setup includes commands for controlling a matrix of LEDs connected to the Arduino, displays connected to the remote host, and other aspects of the host operating system.

[This](https://www.youtube.com/watch?v=QumIhvYtRKQ) video describes how to setup an Arduino as a slave with nanpy.

Executing:
```python 
python main.py -help
```
will display the help menu, and
```python
python main.py -c
```
will display the full list of available commands.

main.py is run on the remote host machine, which should be connected to the Arduino via USB.

client.py can be used to connect to the remote host from any other computer. Multiple simultaneous connections are supported but take care as timed commands will overlap.

client.py accepts both an optional IP address followed by any number of commands to initially execute.

Example:
```python
python client.py loop() blink(2) blink(3) loop(5) blink([2, 3, 4, 5], 10) close
```
Example with optional IP:
```python
python client.py [192.168.1.103] loop() blink(2) blink(3) loop(5) blink([2, 3, 4, 5], 10) close
```
This command would blink pins 2 and 3 in succession, for one second each, 5 times. After exiting the loop, the command would finish by blinking pins 2, 3, 4, and 5 a single time, simultaneously, for 10 seconds (10s on/10s off) and finally, closing the client.py window. 
Most commands accept either an integer or an array and have additional parameters for controlling timing and repitition (see main.py -c for the command list with all parameters).

Commands entered in the client.py command line follow similar syntax and form but can only be entered one line at a time:
```python
192.168.1.103[10000] $$>blink(2)
192.168.1.103[10000] $$>blink(3)
```
All information, warnings, and errors are logged to the main.py window on the remote host screen. The most convenient way to work with the system is to SSH into the remote host, start main.py, and leave the shell visible on the client computer.

For more detailed installation and setup instructions, please contact me. Though the project was not designed with reuse in mind, I would be glad to help anyone interested and will hopefully find time to provide better documentation soon.

## System Requirements ##
* Python 2.7 (available [here](https://www.python.org/ftp/python/2.7.14/python-2.7.14rc1.amd64.msi) for 64-bit Windows or [here](https://www.python.org/ftp/python/2.7.14/python-2.7.14rc1.msi) for 32-bit Windows)
* [nanpy](https://pypi.python.org/pypi/nanpy)
* [Arduino IDE](https://www.arduino.cc/en/Main/Software)

## Contact ##
Jack McKernan ([jmcker@outlook.com](mailto:jmcker@outlook.com))
