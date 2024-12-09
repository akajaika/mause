import cv2
import mediapipe as mp
import tkinter as tk
import time
import math
import threading

import win32api
import win32con

import argparse
from pythonosc import udp_client

import serial

from pythonosc import osc_server, dispatcher

# 初期座標を指定
WRIST_x = mx =  300
WRIST_y = my = 200
INDEX_FINGER_TIP_y = 200
MIDDLE_FINGER_TIP_y = 200
RING_FINGER_TIP_y = 200
PINKY_FINGER_TIP_y = 200
INDEX_FINGER_TIP_x = 200
MIDDLE_FINGER_TIP_x = 200
RING_FINGER_TIP_x = 200
PINKY_FINGER_TIP_x = 200
INDEX_FINGER_MCP_y = 300
INDEX_FINGER_MCP_x = 300
MIDDLE_FINGER_MCP_x = 300
RING_FINGER_MCP_x = 300
PINKY_FINGER_MCP_x = 300
fx = 300*3.2
fy = 200*2.7
D_INDEX = 20000
D_MIDDLE = 20000
D_RING = 20000
D_PINKY = 20000
DST = 120
D_HUND = 100

from collections import deque

# 平滑化のためのパラメータ
SMOOTHING_WINDOW_SIZE = 5

# 座標保存用のデータ構造
wrists_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
wrists_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

index_finger_tip_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
index_finger_tip_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

middle_finger_tip_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
middle_finger_tip_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

ring_finger_tip_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
ring_finger_tip_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

pinky_finger_tip_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
pinky_finger_tip_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

index_finger_mcp_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
index_finger_mcp_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

middle_finger_mcp_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
middle_finger_mcp_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

ring_finger_mcp_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
ring_finger_mcp_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

pinky_finger_mcp_x = deque(maxlen=SMOOTHING_WINDOW_SIZE)
pinky_finger_mcp_y = deque(maxlen=SMOOTHING_WINDOW_SIZE)

# Webカメラから入力
cap = cv2.VideoCapture(0)

# Tkクラス生成
frm = tk.Tk()
# 画面サイズ
frm.geometry('1920x1080')
# 画面タイトル
frm.title('handmodel')

# Canvasウィジェットをウィンドウに配置
canvas = tk.Canvas(frm, width=1920, height=1080)
canvas.pack()

# Handモデルのインスタンス化
with mp.solutions.hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

# ウィンドウに円を描画
    circle_center_x = 300 * 3.2 
    circle_center_y = 200 * 2.7 
    circle_radius = 50
    canvas.delete("all")  # 既存の描画を消去
    canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                        circle_center_x + circle_radius, circle_center_y + circle_radius, fill='red')

    #VRChat用のスクリプト
    """if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=9000,
            help="The port the OSC server is listening on")
        args = parser.parse_args()

        client = udp_client.SimpleUDPClient(args.ip, args.port)"""

    """#VRCOSC用スクリプト
    def handle_message(address, *args):
        global value
        value = args[0]
        # OSCメッセージの値を取得
        print(f"Received OSC message from {address}: {args}")

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/grub", handle_message)
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9001), dispatcher)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()"""

    # ウィンドウ表示の無限ループ
    while True:

        #time.sleep(1) #値見る用

        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 手の位置検出と描画
        results = hands.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for index, landmark in enumerate(hand_landmarks.landmark):
                    # 関節の座標を取得
                    x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])

                    # 各指の先の位置を取得
                    if index == 8:  # インデックス指の先
                        INDEX_FINGER_TIP_y = y
                        INDEX_FINGER_TIP_x = x
                    elif index == 12:  # 中指の先
                        MIDDLE_FINGER_TIP_y = y
                        MIDDLE_FINGER_TIP_x = x
                    elif index == 16:  # 薬指の先
                        RING_FINGER_TIP_y = y
                        RING_FINGER_TIP_x = x
                    elif index == 20:  # 小指の先
                        PINKY_FINGER_TIP_y = y
                        PINKY_FINGER_TIP_x = x
                    elif index == 5:  # 中指の先
                        INDEX_FINGER_MCP_y = y
                        INDEX_FINGER_MCP_x = x
                    elif index == 9:  # 薬指の先
                        MIDDLE_FINGER_MCP_x = x
                        MIDDLE_FINGER_MCP_y = y
                    elif index == 13:  # 小指の先
                        RING_FINGER_MCP_x = x
                        RING_FINGER_MCP_y = y
                    elif index == 17:  # 小指の先
                        PINKY_FINGER_MCP_x = x
                        PINKY_FINGER_MCP_y = y
                    elif index == 4:  
                        THUMB_FINGER_TIP_x = x
                    elif index == 4:  
                        THUMB_FINGER_TIP_y = y

                    #print(f"Hand {results.multi_handedness[0].classification[0].label}: Joint {index} - X: {x}, Y: {y}")

                # 検出された手の骨格をカメラ画像に重ねて描画
                mp.solutions.drawing_utils.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS)
        


        # カメラ画像を表示
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))

        # 手首の座標を取得して、WRIST_xとWRIST_yを更新
        if results.multi_hand_landmarks:
            wrist_landmark = results.multi_hand_landmarks[0].landmark[0]  # 手首に対応する最初のランドマークを仮定
            WRIST_x, WRIST_y = int(wrist_landmark.x * image.shape[1]), int(wrist_landmark.y * image.shape[0])


        
             #視点移動　水平 
            """
            if WRIST_x > 400:
                key_input = (400 - WRIST_x) / 200
                client.send_message("/input/LookHorizontal", key_input)

            if WRIST_x < 200:
                key_input = (200 - WRIST_x) /200
                client.send_message("/input/LookHorizontal", key_input)
            
            if 200 < WRIST_x < 400:
                key_input = 0.1
                client.send_message("/input/LookHorizontal", key_input)

            #視点移動　垂直
            if  WRIST_y < 250:
                key_input = (WRIST_y - 250)*-1 / 300
                client.send_message("/input/LookVertical", key_input)

            if  WRIST_y > 300:
                key_input = (WRIST_y - 300)*-1 / 500
                client.send_message("/input/LookVertical", key_input)

            if  250 < WRIST_y < 400:
                key_input = 0.1
                client.send_message("/input/LookVertical", key_input) """
            
        if  results.multi_hand_landmarks:
            wrist_landmark = results.multi_hand_landmarks[0].landmark[0]
            WRIST_x, WRIST_y = int(wrist_landmark.x * image.shape[1]), int(wrist_landmark.y * image.shape[0])

            # 最新の座標をリストに追加
            wrists_x.append(WRIST_x)
            wrists_y.append(WRIST_y)

            index_finger_tip_x.append(INDEX_FINGER_TIP_x)
            index_finger_tip_y.append(INDEX_FINGER_TIP_y)

            middle_finger_tip_x.append(MIDDLE_FINGER_TIP_x)
            middle_finger_tip_y.append(MIDDLE_FINGER_TIP_y)

            ring_finger_tip_x.append(RING_FINGER_TIP_x)
            ring_finger_tip_y.append(RING_FINGER_TIP_y)

            pinky_finger_tip_x.append(PINKY_FINGER_TIP_x)
            pinky_finger_tip_y.append(PINKY_FINGER_TIP_y)

            index_finger_mcp_x.append(INDEX_FINGER_MCP_x)
            index_finger_mcp_y.append(INDEX_FINGER_MCP_y)

            middle_finger_mcp_x.append(MIDDLE_FINGER_MCP_x)
            middle_finger_mcp_y.append(MIDDLE_FINGER_MCP_y)

            ring_finger_mcp_x.append(RING_FINGER_MCP_x)
            ring_finger_mcp_y.append(RING_FINGER_MCP_y)

            pinky_finger_mcp_x.append(PINKY_FINGER_MCP_x)
            pinky_finger_mcp_y.append(PINKY_FINGER_MCP_y)

            # 平滑化された座標を計算
            smoothed_WRIST_x = sum(wrists_x) / len(wrists_x)
            smoothed_WRIST_y = sum(wrists_y) / len(wrists_y)

            smoothed_INDEX_FINGER_TIP_x = sum(index_finger_tip_x) / len(index_finger_tip_x)
            smoothed_INDEX_FINGER_TIP_y = sum(index_finger_tip_y) / len(index_finger_tip_y)

            smoothed_MIDDLE_FINGER_TIP_x = sum(middle_finger_tip_x) / len(middle_finger_tip_x)
            smoothed_MIDDLE_FINGER_TIP_y = sum(middle_finger_tip_y) / len(middle_finger_tip_y)

            smoothed_RING_FINGER_TIP_x = sum(ring_finger_tip_x) / len(ring_finger_tip_x)
            smoothed_RING_FINGER_TIP_y = sum(ring_finger_tip_y) / len(ring_finger_tip_y)

            smoothed_PINKY_FINGER_TIP_x = sum(pinky_finger_tip_x) / len(pinky_finger_tip_x)
            smoothed_PINKY_FINGER_TIP_y = sum(pinky_finger_tip_y) / len(pinky_finger_tip_y)

            smoothed_INDEX_FINGER_MCP_x = sum(index_finger_mcp_x) / len(index_finger_mcp_x)
            smoothed_INDEX_FINGER_MCP_y = sum(index_finger_mcp_y) / len(index_finger_mcp_y)

            smoothed_MIDDLE_FINGER_MCP_x = sum(middle_finger_mcp_x) / len(middle_finger_mcp_x)
            smoothed_MIDDLE_FINGER_MCP_y = sum(middle_finger_mcp_y) / len(middle_finger_mcp_y)

            smoothed_RING_FINGER_MCP_x = sum(ring_finger_mcp_x) / len(ring_finger_mcp_x)
            smoothed_RING_FINGER_MCP_y = sum(ring_finger_mcp_y) / len(ring_finger_mcp_y)

            smoothed_PINKY_FINGER_MCP_x = sum(pinky_finger_mcp_x) / len(pinky_finger_mcp_x)
            smoothed_PINKY_FINGER_MCP_y = sum(pinky_finger_mcp_y) / len(pinky_finger_mcp_y)

            # 三平方の定理を使用して、平滑化された距離を計算
            D_INDEX = math.sqrt((smoothed_WRIST_y - smoothed_INDEX_FINGER_TIP_y)**2 + (smoothed_WRIST_x - smoothed_INDEX_FINGER_TIP_x)**2)
            D_MIDDLE = math.sqrt((smoothed_WRIST_y - smoothed_MIDDLE_FINGER_TIP_y)**2 + (smoothed_WRIST_x - smoothed_MIDDLE_FINGER_TIP_x)**2)
            D_PINKY = math.sqrt((smoothed_WRIST_y - smoothed_PINKY_FINGER_TIP_y)**2 + (smoothed_WRIST_x - smoothed_PINKY_FINGER_TIP_x)**2)
            D_RING = math.sqrt((smoothed_WRIST_y - smoothed_RING_FINGER_TIP_y)**2 + (smoothed_WRIST_x - smoothed_RING_FINGER_TIP_x)**2)
            D_HUND = math.sqrt((smoothed_WRIST_y - smoothed_INDEX_FINGER_MCP_y)**2 + (smoothed_WRIST_x - smoothed_INDEX_FINGER_MCP_x)**2)
            D_PINKY_MCP = math.sqrt((smoothed_WRIST_y - smoothed_PINKY_FINGER_MCP_y)**2 + (smoothed_WRIST_x - smoothed_PINKY_FINGER_MCP_x)**2)
            D_WIDE = math.sqrt((smoothed_INDEX_FINGER_MCP_y - smoothed_PINKY_FINGER_MCP_y)**2 + (smoothed_INDEX_FINGER_MCP_x - smoothed_PINKY_FINGER_MCP_x)**2)


            #print('D_HUND',D_HUND)
            #print('D_INDEX',D_INDEX)
            #print('D_MIDDLE',D_MIDDLE)
            #print('D_PINKY',D_PINKY)
            #print('D_RING',D_RING)
            #print(' ')
            #print(' ')
            #print(' ')
            DST = D_HUND*1.5 #* 1.2

            # 手首と指の位置の差の条件を設定して握りこみの判定
            if  (D_RING < DST)  and (D_PINKY < DST) :
                #if ((((WRIST_x * 3.2 - fx) * (WRIST_x * 3.2 - fx)) > 30) or (((WRIST_y - 200) * 2.7 - fy) * ((WRIST_y - 200) * 2.7 - fy) > 10)) \
                    #and ((((WRIST_x * 3.2 - fx) * (WRIST_x * 3.2 - fx)) < 1000) or (((WRIST_y - 200) * 2.7 - fy) * ((WRIST_y - 200) * 2.7 - fy) < 100)):
                    
                    circle_center_x = circle_center_x + (smoothed_WRIST_x * 3.2 - fx) * -1
                    circle_center_y = circle_center_y + ((smoothed_WRIST_y - 200) * 2.7 - fy)
                    circle_radius = 50
                    
                    #client.send_message("/hoge", 1.0)

                    #左クリック　押す
                    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

                    fx = smoothed_WRIST_x * 3.2
                    fy = (smoothed_WRIST_y - 200) * 2.7
                    canvas.delete("all")  # 既存の描画を消去 これ消したら残像で絵が描ける
                    canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                            circle_center_x + circle_radius, circle_center_y + circle_radius, fill='blue')
                    
                    mx = math.floor(circle_center_x)
                    my = math.floor(circle_center_y)
                    win32api.SetCursorPos((mx, my))
                    
                    
                    
            else: 
                    #左クリック　離す
                    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    fx = smoothed_WRIST_x * 3.2
                    fy = (smoothed_WRIST_y - 200) * 2.7
                    canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                            circle_center_x + circle_radius, circle_center_y + circle_radius, fill='red')
                    
                    #client.send_message("/hoge", 2.0)

            
            #人差し指、中指　左クリック        
            # if  (D_INDEX < DST )  :      
            #         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, mx, my, 0, 0)
            #         print(1)
            # else:
            #         win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, mx, my, 0, 0)
            #         print(2)

            # #薬指、小指　右クリック
            # if  (D_MIDDLE < DST): 
            #         win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                

            




            # ウィンドウをアップデート
            frm.update()
            
            D_HUND = 0
        # Escキーで終了
        if cv2.waitKey(5) & 0xFF == 27:
            break

# HandモデルとWebカメラの解放とOpenCVウィンドウの破棄
cap.release()
cv2.destroyAllWindows()

# Tkinterウィンドウの表示を維持
frm.mainloop()