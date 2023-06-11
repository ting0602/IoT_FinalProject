# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioMessage
import DAN, time, threading, random, json
import config as c
import linebot_config as lb
from utils import *

ServerURL = 'https://7.iottalk.tw' 
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
group_id_set=set()                                         #LineBot's Friend's user id 
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
    
def loadGroupId():
    try:
        idFile = open('groupfile', 'r')
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

def saveGroupId(groupId):
    # 改成只限一個群組
        # idFile = open('groupfile', 'a')
        idFile = open('groupfile', 'w')
        idFile.write(groupId+';')
        idFile.close()



@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    # get mention
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    
    # if c.stage == 0:
    #     body = json.loads(body)
    #     try:
    #         mention_info = body["events"][0]["message"]["mention"]
    #         # 只能標註一人 設置一人的鬧鐘
    #         if len(mention_info["mentionees"]) == 1:
    #             mention_user = mention_info["mentionees"][0]["userId"]
    #             c.mention = mention_user
    #             userId = body["events"][0]["source"]["userId"]
    #             c.send_mention = userId
    #             print("mention user:", mention_user)
    #         print("get mention:", mention_info)
    #     except:
    #         # no mention
    #         c.mention = ''
    #         c.send_mention = ''
            
    return 'OK'

@app.route("/sound.mp3") # 提供 sound.mp3 的下載連結
def get_sound():
    return send_from_directory("static", "sound.mp3") # 回傳 static/sound.mp3

@app.route("/text.mp3") # 提供 text.mp3 的下載連結
def get_sound2():
    return send_from_directory("static", "text.mp3") # 回傳 static/sound.mp3

@app.route("/link.mp3") # 提供 link.mp3 的下載連結
def get_sound3():
    return send_from_directory("static", "link.mp3") # 回傳 static/sound.mp3

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    print("audio msg!")
    userId = event.source.user_id
    groupId = ''
    try:
        groupId = event.source.group_id
        c.groupId = groupId
    except:
        # not group
        pass
    print("group id", groupId)
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
    if not groupId in group_id_set:
        group_id_set.add(groupId)
        saveGroupId(groupId)
    audio_content = line_bot_api.get_message_content(event.message.id)
    result_msg = audio_msg_process(audio_content, userId)
    print("audio msg:", result_msg)
    DAN.push('line_in', result_msg)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("text msg")
    userId = event.source.user_id
    groupId = ''
    try:
        groupId = event.source.group_id
        c.groupId = groupId
    except:
        # not group
        pass
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
    if not groupId in group_id_set:
        group_id_set.add(groupId)
        saveGroupId(groupId)
        
    msg = event.message.text
    
    body = request.get_data(as_text=True)
    body = json.loads(body)
    metion_process(body)
    result_msg = message_process(msg, userId)
    if result_msg:
        print("text result: ", result_msg)
    # TODO: modify the push Msg
    # TODO: DAN.push()
    DAN.push('line_in', result_msg)


# TODO: DAN.pull()
times = 0
sleep_times = 0
def pull_odf():
    while 1:
        ODF = DAN.pull('line_out')
        # TODO: 之後改用 DAN.pull
        # adder_msg = DAN.pull('add_msg')
        adder_msg = random.randint(0, 1023)
        if c.stage == 3:
            msg, music, state = check_alarm()
            if msg:
                # 回傳題目
                # TODO: 回傳給加法器
                line_bot_api.push_message(c.groupId,TextSendMessage(text=msg))
        
        # 鬧鐘開始響，處理
        # FIXME: 還不確定加法器回傳值
        if c.stage == 4:
            # 正常回復
            # if int(adder_msg) == c.ans:
            if check_ans():
                times += 1
            # 貪睡
            # FIXME: 要改寫條件 我先亂寫
            elif int(adder_msg) == 1023:
                times = 0
                sleep_times += 1
            elif int(adder_msg) == 0:
                times = 0
                sleep_times += 1
            
            # 判斷是否停止 / 貪睡
            if times > 5:
                c.q_number -= 1
                if c.q_number > 0:
                    msg = generate_exam()
                    line_bot_api.push_message(c.groupId,TextSendMessage(text=msg))
            elif sleep_times > 3:
                alarm_sleep()
                c.stage = 3

        elif ODF:
            print("line_out", ODF)
            # for userId in user_id_set:
            line_bot_api.push_message(c.groupId,TextSendMessage(text=ODF[0]))   # Reply API example
        time.sleep(3)

t = threading.Thread(target=pull_odf)
t.daemon = True
t.start()
    
if __name__ == "__main__":

    idList = loadUserId()
    if idList: user_id_set = set(idList)
    
    groupList = loadGroupId()
    if groupList: group_id_set = set(groupList)

    # try:
    #     for userId in user_id_set:
    #         line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
    # except Exception as e:
    #     print(e)
    try:
        for groupId in group_id_set:
            line_bot_api.push_message(groupId, TextSendMessage(text='鬧鐘準備中\n請先輸入隨意值，得以喚醒智慧鬧鐘'))  # Push API example
    except Exception as e:
        print(e)
    
    # app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)
    app.run('0.0.0.0', port=32768, threaded=True, use_reloader=False)

    

