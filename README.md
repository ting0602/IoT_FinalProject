# 2023 NYCU IoT Final
## 關於我們
### 隊名: 
一個語不驚人死不休的隊伍
### 題目：
智慧鬧鐘
### 隊長：
109550119 邵筱庭 
### 組員：
109550134 梁詠晴 0810756 高維廣
### 摘要

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



