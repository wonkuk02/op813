원플(Oneplus 3t)에서 오픈파일럿 이식하려면?
------
1. 일단 /data 디렉토리에서 0.8.9 브렌치를 설치해야 상위 버전으로 이동할 수 있습니다.
```
cd /data/ && mv openpilot openpilot-backup;
git clone https://github.com/kans-ky/oneplus.git openpilot --branch 089-Volt
```

2. 아래 명령 실행합니다
```
chmod 700 /data/openpilot/scripts/oneplus_update_neos.sh;
cd /data/openpilot/scripts/ && ./oneplus_update_neos.sh
```

3. 원플용 Neos(recovery, system 이미지)가 다운로드되면 자동으로 부팅됩니다. 
   두번 정도 리부팅되고 나면 fastboot 모드로 들어갑니다.

4. fastboot 모드에서 볼륨 상하버튼으로 리커버리모드 선택한 뒤 파워버튼으로 실행합니다. 

5. 리커버리 모드에서 차례대로 apply update` -> `Choose from emulated` -> `0/` -> `update.zip` -> `Reboot system now` 선택합니다.
   원플용 0.8.9버전으로 부팅됩니다. 
   긴 빌드과정이(15분이상) 끝나면 0.8.9버전으로 부팅됩니다. 
   터치 반응이 없으므로 강제부팅합니다.

6. 곧바로 0.8.13브렌치를 클론합니다. 0.7.x버전과 0.8.x 이온접속 개인키 변경법은 생략합니다.
   토글 메뉴로 들어가서 Enable Community Features 버튼 녹색으로 On해야 합니다.
```
cd /data/ && mv openpilot openpilot-089;
git clone https://github.com/kans-ky/op813.git openpilot --branch Volt-oneplus
```
7. 아래 명령을 실행합니다.
```
chmod 700 /data/openpilot/unix.sh;
cd /data/openpilot/ && ./unix.sh;
reboot;
```

8. 마찬가지로 부팅과정을 거치고 나면 0.8.13으로 부팅됩니다.
   성공하시기를 바랍니다.
