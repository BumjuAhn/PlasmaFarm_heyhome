# PlasmaFarm_heyhome 

### 실행하기
- 그냥 실행
```
python start.py
```
- 백그라운드 실행
```
nohup python3 -u start.py > output.log 2>&1 &
```
- 로그 보기
```
cat output.log
tail -f output.log
```
- 실행 확인
```
ps ax | grep .py
```
- 종료하기
```
kill -9 PID
ex. kill -9 13586
```
