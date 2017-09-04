cd /d %~dp0
cd ../
SET t=1
python client.py turnOff(getColumn(1)) sleep(%t%) turnOff(getColumn(2)) sleep(%t%) turnOff(getColumn(3)) sleep(%t%) turnOff(getColumn(4)) sleep(%t%) turnOff(getColumn(5)) sleep(%t%) loop(1) close