import config as c
import linebot_config as lb
import re, datetime, random, json
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS

# stage 1: 設置鬧鐘時間
# stage 2: 設置鬧鐘題數
# stage 3: 設置鬧鐘鈴聲
# stage 4: 開始響
def message_process(msg, userId):
    return_msg = None
    stage = c.stage
    
    # helper
    if msg in c.helper:
        return_msg = c.helper_text
        return return_msg
    # 管理員設置
    # stage 0
    if msg == '我是管理員':
        if userId in c.admins:
            return_msg = '您已是管理員！'
        else:
            c.admins.append(userId)
            return_msg = '完成, 已將您設為管理員！' 
        return return_msg
    if msg == '取消管理員':
        if userId in c.admins:
            c.admins.remove(userId)
            return_msg = '完成, 已經取消您的管理員身分'
        else:
            return_msg = '抱歉，您並非管理員' 
        return return_msg
    
    if stage == 3:
        return return_msg
    
    # 設置鬧鐘
    # stage 0 -> 1
    # pattern = r"鬧鐘\s?(\d{1,2}:\d{2})"
    pattern = r"@(\w+)\s?鬧鐘\s?(\d{1,2}:\d{2})"
    matches = re.findall(pattern, msg)
    if len(matches) == 1 and stage == 0:  
        info = matches[0][1]
        hours, minutes = info.split(':')
        hours = int(hours)
        minutes = int(minutes)
        if userId not in c.admins:
            return_msg = '抱歉，您並非管理員\n請先輸入"我是管理員"以獲取管理員身分' 
        elif hours > 24 or minutes > 60:
            return_msg = '請輸入合理時間'
        elif c.send_mention != userId:
            print("my id", userId)
            print("send id", c.send_mention)
            print("mention ", c.mention)
            return_msg = '失敗，請使用正確的標記格式' 
        else:
            # current_time = time.time()
            c_hours = datetime.datetime.now().hour
            c_minutes = datetime.datetime.now().minute

            remaining_h = hours - int(c_hours)
            remaining_m = minutes - int(c_minutes)
            if remaining_m < 0:
                remaining_m = 60 + remaining_m
                remaining_h -= 1
            if remaining_h < 0:
                remaining_h += 24
            return_msg = '完成，已設定 ' + info + ' 的鬧鐘，鬧鐘將於 ' +  str(remaining_h) +' 小時 ' + str(remaining_m) + ' 分後響起。\n您可輸入 1~3 的數字，設置加法器的題數'
            c.alarm_h = hours
            c.alarm_m = minutes
            c.alarm_time = info # 更: c.alarm_time -> matches[0]
            c.stage = 1 # 更: set stage
            c.manager = userId
            c.target = c.mention
        return return_msg
    
    # 取消鬧鐘
    # stage 1 -> 0
    if stage >= 0 and msg == '取消鬧鐘':
        # if userId == c.target:
        #     return_msg = '取消失敗，您無法取消他人為您設置的鬧鐘'
        # elif userId in c.admins:
        #     return_msg = '完成，已取消設置原定於 ' + c.alarm_time + ' 響起的鬧鐘！' 
        #     c.stage = 0
        # else:
        #     return_msg = '取消失敗，請成為管理者後才取消'
        if userId == c.manager:
            return_msg = '完成，已取消設置原定於 ' + c.alarm_time + ' 響起的鬧鐘！' 
        else:
            return_msg = '失敗，非設置鬧鐘者無法取消鬧鐘'
        return return_msg
            
                
    # 已設置鬧鐘: 設置題目數
    # stage 1 -> 2
    pattern = r'^[1-9]\d*$'
    match = re.match(pattern, msg)
    if stage == 1 and match and userId == c.manager:
        q_number = int(match.group())
        if q_number <=3 and q_number > 0:
            c.q_number = q_number
            return_msg = '完成，已設置 ' + str(q_number) + ' 題，接著可設置鬧鐘音訊，可接受的輸入格式有：\n1. 直接傳送 mp3 音訊檔案\n2. 鈴聲:音樂網址\n3. 鈴聲:文字'
            c.stage = 2
        else:
            return_msg = '題數限制在 1~3 題，請輸入合法範圍內的數字'
        return return_msg
    
    # 已設置鬧鐘: 設置鈴聲
    # stage 2 -> 3
    if stage == 2 and '鈴聲' in msg and ':' in msg and userId == c.manager:
        _, data = msg.split(':')
        print(data)
        pattern = r'^(https?://)?(www\.)?[\w.-]+\.[a-zA-Z]{2,}(\/\S*)?$'
        # 1. Music Link
        if re.match(pattern, data):
            c.alarm_music = data
        # 2. Text
        else:
            tts=gTTS(text=data, lang='zh-tw')
            tts.save("./static/text.mp3")
            c.alarm_music = f"{lb.webhook_url}/text.mp3"
            # 轉換成的mp3會存到 static/text.mp3, url "{ngrok網址}/text.mp3" 可開啟text.mp3
        return_msg = '鈴聲設置完畢，您已完成所有的鬧鐘設置！'
        c.stage = 3
        return return_msg

    return return_msg

# mp3 input 
# SETUP: pip install speechrecognition 
# SETUP: pip install pydub 
# SETUP: install ffmpeg: https://github.com/BtbN/FFmpeg-Builds/releases or pip install ffmpeg
# ffmpeg 下載教學 (比較詳細): https://vocus.cc/article/64701a2cfd897800014daed0
# mp3會存到 static/sound.mp3, url "{ngrok網址}/sound.mp3" 可開啟sound.mp3
# 設定正確的c.webhook_url
   
def audio_msg_process(audio_content, userId):
    print("recv audio!")
    return_msg = None
    if c.stage == 2:
        path='./static/sound.mp3' 
        with open(path, 'wb') as fd:
            for chunk in audio_content.iter_content():
                fd.write(chunk)
        return_msg = '鈴聲設置完畢，您已完成所有的鬧鐘設置！'
        c.stage = 3
        c.alarm_music = f"{lb.webhook_url}/sound.mp3"
    return return_msg
    
def metion_process(body):
    if c.stage == 0:
        try:
            mention_info = body["events"][0]["message"]["mention"]
            # 只能標註一人 設置一人的鬧鐘
            if len(mention_info["mentionees"]) == 1:
                mention_user = mention_info["mentionees"][0]["userId"]
                c.mention = mention_user
                userId = body["events"][0]["source"]["userId"]
                c.send_mention = userId
                print("mention user:", mention_user)
            print("get mention:", mention_info)
        except:
            # no mention
            c.mention = ''
            c.send_mention = ''

# stage = 3 時作用
# TODO: 回傳：題目(X) & 音訊資料(c.alarm_music) & 0/1 (要不要繼續叫)
def check_alarm():
    c_hours = datetime.datetime.now().hour
    c_minutes = datetime.datetime.now().minute
    # print(int(c_hours),c.alarm_h, int(c_minutes), c.alarm_m)
    if int(c_hours) == c.alarm_h and int(c_minutes) == c.alarm_m:
        c.stage = 4
        return_msg = generate_exam()
        print("start")
        return return_msg, c.alarm_music, 1
    return None, None, 0

# 生成題目
def generate_exam():
    c.ans = random.randint(0, 15)
    num1 = random.randint(0, 15)
    num2 = abs(c.ans - num1)
    exam = '該起床囉！\n題目：X + ' + str(num1) + ' = ' + str(num2)
    print(exam)
    return exam

def check_ans(num):
    # num: 0 ~ 1023
    # TODO: 對答案
    return True

# 貪睡 鬧鐘調整時間
def alarm_sleep():
    # add 5 min
    if c.alarm_m >= 55:
        c.alarm_m = (c.alarm_m + 5) - 60
        c.alarm_h += 1
    if c.alarm_h > 23:
        c.alarm_h = 0
        
def reset_config():
    c.manager = ''
    c.mention = ''
    c.send_mention = ''
    c.target = ''
    c.q_number = 0
    c.stage = 0
    c.alarm_h = 0
    c.alarm_m = 0
    c.alarm_music = ''
    c.alarm_time = ''
    c.ans = -1

# c.admins.append('123')
# c.mention = 'belle_id'
# # c.manager = '123'
# c.send_mention = '123'
  
# msg = message_process('@belle 鬧鐘09:35', '123')
# print(msg)

# c.alarm_h = 13
# c.alarm_m = 43
# msg = check_alarm()
# print(msg)
# c.ans = random.randint(0, 15)
# generate_exam()
# print("x = ", c.ans)