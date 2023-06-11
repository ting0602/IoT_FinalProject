# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioMessage
import DAN, time, threading, random
import config as c
import linebot_config as lb
from utils import *

ServerURL = 'https://4.iottalk.tw' 
mac_addr = '119' + str(random.randint(100, 999))
Reg_addr = mac_addr   # Note that the mac_addr generated in DAN.py always be the same cause using UUID !
DAN.profile['dm_name']='Linebot'   # you can change this but should also add the DM in server
DAN.profile['df_list']=['line_in', 'line_out']   # Check IoTtalk to see what IDF/ODF the DM has
DAN.profile['d_name']= "SHT119_" +  str(random.randint(100, 999)) + "_" + DAN.profile['dm_name'] # None
DAN.device_registration_with_retry(ServerURL, Reg_addr) 
print("dm_name is ", DAN.profile['dm_name'])
print("d_name is ", DAN.profile['d_name'])
print("Server is ", ServerURL)

line_bot_api = LineBotApi(lb.token) #LineBot's Channel access token
handler = WebhookHandler(lb.secret)        #LineBot's Channel secret
user_id_set=set()                                         #LineBot's Friend's user id 
app = Flask(__name__, static_folder="static") # set static folder


def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None


def saveUserId(userId):
        idFile = open('idfile', 'a')
        idFile.write(userId+';')
        idFile.close()


@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/sound.mp3") # 提供 sound.mp3 的下載連結
def get_sound():
    return send_from_directory("static", "sound.mp3") # 回傳 static/sound.mp3

@app.route("/text.mp3") # 提供 sound.mp3 的下載連結
def get_sound2():
    return send_from_directory("static", "text.mp3") # 回傳 static/sound.mp3


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    print("audio msg!")
    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
    audio_content = line_bot_api.get_message_content(event.message.id)
    result_msg = audio_msg_process(audio_content, userId)
    DAN.push('line_in', result_msg)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
    msg = event.message.text
    result_msg = message_process(msg, userId)
    # TODO: modify the push Msg
    # TODO: DAN.push()
    DAN.push('line_in', result_msg)


# TODO: DAN.pull()
def pull_odf():
    while 1:
        ODF = DAN.pull('line_out')
        if c.stage == 3:
            check_alarm()
        if ODF:
            print("line_out", ODF)
            for userId in user_id_set:
                line_bot_api.push_message(userId,TextSendMessage(text=ODF[0]))   # Reply API example
        time.sleep(5)

t = threading.Thread(target=pull_odf)
t.daemon = True
t.start()
    
if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)

    try:
        for userId in user_id_set:
            line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
    except Exception as e:
        print(e)
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

