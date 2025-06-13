import RPi.GPIO as GPIO
import pygame
import time
from datetime import datetime, timedelta
import sqlite3
import os
import pytz
import threading

# GPIOピン番号 (適宜変更)
LIGHT_PIN = 17
# スピーカー制御
pygame.mixer.init()
SOUND_PATH = os.path.join(os.path.dirname(__file__), 'alarm.wav')
try:
    alarm_sound = pygame.mixer.Sound(SOUND_PATH)
except pygame.error as e:
    print(f"サウンドファイルの読み込みに失敗しました: {e}")
    alarm_sound = None

# GPIOの初期設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)

def turn_light_on(duration=10):
    GPIO.output(LIGHT_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LIGHT_PIN, GPIO.LOW)

def turn_light_off():
    GPIO.output(LIGHT_PIN, GPIO.LOW)

def play_sound(duration=10):
    if alarm_sound:
        channel = alarm_sound.play()
        time.sleep(duration)
        channel.stop()
    else:
        print("アラーム音が設定されていません。")

# データベースのパス
DATABASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tasks.db'))

def get_db_control():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_tasks():
    db = get_db_control()
    cur = db.execute('SELECT id, task, deadline, is_completed FROM tasks')
    tasks = cur.fetchall()
    db.close()
    return tasks

def check_reminders():
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    tasks = get_tasks()

    for task in tasks:
        deadline = datetime.fromisoformat(task['deadline']).astimezone(pytz.timezone('Asia/Tokyo'))
        time_until_deadline = deadline - now

        if task['is_completed'] == 0 and 0 < time_until_deadline.total_seconds() <= 24 * 3600:
            # 期限24時間以内のタスクで、現在の時刻が1時間ごとのタイミングであれば
            if now.minute == 0 and now.second < 10: # 毎時0分0秒から9秒までの間に実行
                print(f"【リマインダー】{task['task']} は24時間以内に期限を迎えます。LEDとスピーカーを10秒間ONにします。")
                turn_light_on(10)
                play_sound(10)
        elif task['is_completed'] == 1:
            print(f"【完了】{task['task']} が完了しました。LEDとスピーカーをOFFにします。")
            turn_light_off()
            # 必要であれば、スピーカーOFFの関数も呼び出す (play_sound(0) など)
            pygame.mixer.stop() # pygameのmixerを停止してスピーカーをOFFにする

def run_punishment():
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    tasks = get_tasks()

    for task in tasks:
        deadline = datetime.fromisoformat(task['deadline']).astimezone(pytz.timezone('Asia/Tokyo'))
        if task['is_completed'] == 0 and now > deadline and now.minute == 0 and now.second < 10:
            print(f"【罰ゲーム】{task['task']} の期限超過。LEDとスピーカーを10秒間ONにします。")
            turn_light_on(10)
            play_sound(10)

if __name__ == '__main__':
    try:
        while True:
            check_reminders()
            run_punishment()
            time.sleep(60)
    except KeyboardInterrupt:
        print("制御を終了します。")
    finally:
        pygame.mixer.quit()
        GPIO.cleanup()