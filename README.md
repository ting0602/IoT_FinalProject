# 2023 NYCU IoT Final
## 關於我們
### 隊名
一個語不驚人死不休的隊伍
### 題目
智慧鬧鐘
### 隊長
109550119 邵筱庭 
### 組員
109550134 梁詠晴 0810756 高維廣
### 摘要
我們的期末專題旨在利用 IoTtalk 平台結合 LINE Bot、NodeMCU 和加法器，開發一個需要使用加法器解題才能關閉的鬧鐘系統，幫助大家克服起床的難題。

透過將智慧鬧鐘加入宿舍群組，室友們可以在群組內對鬧鐘進行客製化設定。可設定項目包括鬧鐘使用對象、鬧鐘時間、數學題數、鈴聲輸入。當鬧鐘響起後，床上的人需要醒來看手機的題目，並使用床邊的加法器，調整上面的可變電阻、按壓實體按鈕來解開題目，答題正確鬧鐘才會停止。這樣的設計可以有效地讓人保持清醒，成功拒絕被窩的誘惑！
### 雲端連結
[Google Drive](https://drive.google.com/drive/folders/1slHWqAkRcl_rViRqjXJkpGxVoBGZ4hJr?usp=drive_link)
### Demo
[報告影片](https://youtu.be/K7yixxrrM-c)

[DEMO 影片](https://youtu.be/wSWIVKEH5BY)
## 使用說明
### Step0. 創建 LineBot
到 [Line Developers](https://developers.line.biz/zh-hant/) 創建一個帳號，設定完畢後獲得 token 和 secret
### Step1. 下載專案
```
git clone https://github.com/ting0602/IoT_FinalProject.git
```
### Step2. 下載所需套件
```
pip install -r requirements.txt
```
### Step3. 創建檔案
新增檔案 `linebot_config.py` 檔案內容如下
```
secret = {LineBot's Channel access secret}
token = {LineBot's Channel access token}
webhook_url = {Your computer address}
```
### Step4. 使用 ngrok 生成 webhook
[下載 ngrok](https://ngrok.com/download)

執行以下指令，讓程式跑在 port 32768
```
python LineBot_basic.py
```
並將下載後的 `ngrok.exe` 移至專案檔案夾底下，執行以下指令以獲得 https 網址
```
./ngrok http 32768
```
接著把獲得的網址到 Line Developers 網站設定成這個 LineBot 的 webhook
### Step5. 使用 IoTTalk 連接 IDF 和 ODF
連接方式可參考雲端中專題成果報告書中的 IoTTalk 專案架構部分
### Step6. NodeMCU程式燒入、接線
依照 https://github.com/IoTtalk/ArduTalk-for-NodeMCU/ 內的說明下載 Arduino 並完成設定後，下載 2.6.3 版本的 ESP8266 函式庫，執行以下指令：
```
git clone https://github.com/earlephilhower/ESP8266Audio
```
並把 ```src/AudioFileSourceICYStream.cpp``` 內的第53行 ```http.setFollowRedirects(HTTPC_FORCE_FOLLOW_REDIRECTS)``` 刪掉

將下載到的資料夾移到 ```C:\Users\[username]\AppData\Local\Arduino15\packages\esp8266\hardware\esp8266\2.6.3\libraries```

調整Arduino的設定：

Tools->Upload Speed->115200

Tools->lwIP Variant->V2 Higher Bandwidth

Tools->CPU Frequency->160MHz

點選Upload燒入到板子上，建立Wi-Fi熱點，把NodeMCU的Rx接腳接上自製的放大器音樂輸入端，並完成接地接線即可

HINT: 加法器的接線可參考專題成果報告書中的硬體設備連接圖



