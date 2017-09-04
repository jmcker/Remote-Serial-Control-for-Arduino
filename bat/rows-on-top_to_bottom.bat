cd /d %~dp0
cd ../
SET t=1
python client.py turnOn(getRow(1)) sleep(%t%) turnOn(getRow(2)) sleep(%t%) turnOn(getRow(3)) sleep(%t%) turnOn(getRow(4)) sleep(%t%) turnOn(getRow(5)) sleep(%t%) loop(1) close