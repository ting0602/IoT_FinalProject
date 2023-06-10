import config as c
import re, time, datetime, math

def message_process(msg, userId):
    return_msg = None
    stage = c.stage
    
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
            return_msg = '完成, 已將取消您的管理員身分'
        else:
            return_msg = '抱歉，您並非管理員' 
        return return_msg
    
    if stage == 3:
        return return_msg
    
    # 設置鬧鐘
    # stage 0 -> 1
    pattern = r"鬧鐘\s?(\d{1,2}:\d{2})"
    matches = re.findall(pattern, msg)
    if len(matches) == 1 and stage == 0:  
        hours, minutes = matches[0].split(':')
        hours = int(hours)
        minutes = int(minutes)
        if hours > 24 or minutes > 60:
            return_msg = '請輸入合理時間'
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
            return_msg = '完成，已設定 ' + matches[0] + ' 的鬧鐘，鬧鐘將於 ' +  str(remaining_h) +' 小時 ' + str(remaining_m) + ' 分後響起。\n您可輸入 1~3 的數字，設置加法器的題數'
            c.alter_h = hours
            c.minutes = minutes
            print(return_msg)
        return return_msg
    
    # 取消鬧鐘
    # stage 1 -> 0
    if stage >= 0 and msg == '取消鬧鐘':
        # TODO: 還沒寫設置 target member (需要先抓目標id，或是取消這部分)
        if userId == c.target:
            return_msg = '取消失敗，您無法取消他人為您設置的鬧鐘'
        elif userId in c.admins:
            return_msg = '完成，已取消設置原定於 ' + c.alarm_time + ' 響起的鬧鐘！'
            c.stage = 0
        else:
            return_msg = '取消失敗，請成為管理者後才取消'
        return return_msg
            
                
    # 已設置鬧鐘: 設置題目數
    # stage 1 -> 2
    pattern = r'^[1-9]\d*$'
    match = re.match(pattern, msg)
    if stage == 1 and match:
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
    # TODO: mp3輸入 (不確定會長怎樣 先跳過)
    if stage == 2 and '鈴聲' in msg and ':' in msg:
        _, data = msg.split(':')
        pattern = r'^(https?://)?(www\.)?[\w.-]+\.[a-zA-Z]{2,}(\/\S*)?$'
        # 1. Music Link
        # if re.match(pattern, data):
        #     ...
        # 2. Text
        c.alarm_music = data
        return_msg = '鈴聲設置完畢！'
        c.stage = 3
        return return_msg

    return return_msg

# TODO: 這個函式會一直跑，檢查是不是該響了
# 回傳：題目(c.exam_list) & 音訊資料(c.alarm_music) & 0/1 (要不要繼續叫)
def check_alarm():
    c_hours = datetime.datetime.now().hour
    c_minutes = datetime.datetime.now().minute
    if c_hours == c.alarm_h and c_minutes == c.alarm_m:
        # TODO: 啟動鬧鐘
        # 賴床：
        # 結束：重設config各值
        print("start")
        
# message_process('鬧鐘12:35', '123')