cd /d %~dp0
cd ../
SET t=1
python client.py turnOn(getColumn(5)) sleep(%t%) turnOn(getColumn(4)) sleep(%t%) turnOn(getColumn(3)) sleep(%t%) turnOn(getColumn(2)) sleep(%t%) turnOn(getColumn(1)) sleep(%t%) loop(1) close