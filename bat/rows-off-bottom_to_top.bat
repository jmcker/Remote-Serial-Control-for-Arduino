cd /d %~dp0
cd ../
SET t=1
python client.py turnOff(getRow(5)) sleep(%t%) turnOff(getRow(4)) sleep(%t%) turnOff(getRow(3)) sleep(%t%) turnOff(getRow(2)) sleep(%t%) turnOff(getRow(1)) sleep(%t%) loop(1) close