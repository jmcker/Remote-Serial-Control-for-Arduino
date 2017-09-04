cd /d %~dp0
cd ../
python client.py blink([2,4,6,8],.5,5) linearExec([2,3,4,5,6,7,8,9],1,1) blink([2,3,4,5,6,7,8,9],.05,20) turnOff(ledPins) loop(1) close