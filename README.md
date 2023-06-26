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
我們的期末專題旨在利用IoTtalk平台結合LINE Bot、NodeMCU和加法器，開發一個讓人神智清醒的鬧鐘系統，幫助大家克服因作息不正常等因素導致難以在預計時間起床的問題。

首先，我們將建立一個LINE Bot帳號，讓室友們和LINE Bot帳號加入同一個群組。這樣室友就能夠從遠方使用手機，向LINE Bot輸入特定的關鍵字，觸發鬧鐘系統。透過IoTtalk平台的連接，這個指令將被傳遞給鬧鐘設備。

管理者可以設定鬧鐘響鈴和關閉的時間、決定貪睡功能是否開啟、決定對方要完成的挑戰項目跟題數、傳送語音訊息、指定鬧鐘鈴聲、傳送文字並透過TTS轉換播出。我們使用LM386晶片設計出放大器電路，可以有效提高鬧鐘音量。當鬧鐘響起後，床上的人將在LINE群組中收到由LINE Bot發送的題目，床上的人需要醒來看手機的訊息，根據訊息內容使用床邊的加法器調整可變電阻，解開題目並得到正確答案，鬧鐘才會停止。此外，我們還打算擴充更多功能，讓這個鬧鐘更加人性化。

這樣的設計可以有效地讓人保持清醒，因為他們需要在睡意煩擾下思考和解決問題，解開題目的同時目標也已經完全清醒了，這種互動和挑戰性的解題過程可以幫助目標迅速清醒，讓他們成功拒絕被窩的誘惑！
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



