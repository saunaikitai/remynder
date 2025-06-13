import RPi.GPIO as GPIO # Raspberry PiのGPIOピンを制御するためのライブラリ
import time             # 時間に関する操作を行うためのライブラリ（ここでは待機のために使用）

# 使用するGPIOピンの番号を定義します (BCMモードでのGPIO番号)
# 例: GPIO 17番ピンを使用する場合
LED_PIN = 17

# GPIOの初期設定
GPIO.setmode(GPIO.BCM)      # GPIOの番号付け方式をBCMモードに設定
GPIO.setup(LED_PIN, GPIO.OUT) # 指定したLED_PINを出力モードに設定

try:
    print(f"LED (GPIO {LED_PIN}) をONにします。")
    GPIO.output(LED_PIN, GPIO.HIGH) # LED_PINにHIGH信号を出力し、LEDをONにする

    print("LEDが点灯しました。Ctrl+Cを押すとプログラムが終了し、LEDがOFFになります。")
    while True:
        # プログラムを終了させずにLEDをONの状態に保つために、無限ループで待機
        time.sleep(1)

except KeyboardInterrupt:
    # Ctrl+C (キーボード割り込み) が押されたときに実行される
    print("\nCtrl+Cが押されました。プログラムを終了します。")

finally:
    # プログラムが終了する際に必ず実行されるクリーンアップ処理
    GPIO.output(LED_PIN, GPIO.LOW) # LEDをOFFにする
    GPIO.cleanup()                 # GPIOピンの設定をリセットし、安全な状態に戻す
    print("GPIOクリーンアップ完了。LEDがOFFになりました。")