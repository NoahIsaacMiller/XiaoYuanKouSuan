from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key, Listener
import pyautogui, pytesseract, solution1_recognise, cv2, time, math, paddleocr
from PIL import Image
from solution1_recognise import *

import logging

# 设置日志级别为 WARNING 或更高，这样可以减少输出
logging.getLogger("ppocr").setLevel(logging.WARNING)


mouse_controller = MouseController()
keyboard_controller = KeyboardController()
paddle_ocr = paddleocr.PaddleOCR(use_gpu=False, lang="en")



class AnsweringArea:
    def __init__(self,  x1, y1,
                        x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def MoveMouseSmoothly(mouse, a, b, delay=0.00004):
    step_count = 15
    step_length_x = int(a/step_count)
    step_length_y = int(b/step_count)
    for i in range(step_count):
        mouse.move(step_length_x, step_length_y)
        time.sleep(delay)

def DrawLessThanWithin(offset, pos):
    left_top = (pos[0][0] + offset[0], pos[0][1] + offset[1])
    bottom_right = (pos[1][0] + offset[0], pos[1][1] + offset[1])
    center = (int((left_top[0]+bottom_right[0])/2), int((left_top[1]+bottom_right[1])/2))
    mouse_controller.position = (center[0]+150, center[1]-150)
    mouse_controller.press(Button.left)
    MoveMouseSmoothly(mouse_controller, -300, 150)
    
    MoveMouseSmoothly(mouse_controller, 300, 150)
    mouse_controller.release(Button.left)
    
def DrawGreatThanWithin(offset, pos):
    left_top = (pos[0][0] + offset[0], pos[0][1] + offset[1])
    bottom_right = (pos[1][0] + offset[0], pos[1][1] + offset[1])
    center = (int((left_top[0]+bottom_right[0])/2), int((left_top[1]+bottom_right[1])/2))
    mouse_controller.position = (center[0]-150, center[1]-150)
    mouse_controller.press(Button.left)
    MoveMouseSmoothly(mouse_controller, 300, 150)
    MoveMouseSmoothly(mouse_controller, -300, 150)
    mouse_controller.release(Button.left)
    time.sleep(0.05)
def DrawEqualWithin(offset, pos):
    left_top = (pos[0][0] + offset[0], pos[0][1] + offset[1])
    bottom_right = (pos[1][0] + offset[0], pos[1][1] + offset[1])
    center = (int((left_top[0]+bottom_right[0])/2), int((left_top[1]+bottom_right[1])/2))
    mouse_controller.position = (center[0]-150, center[1]-50)
    mouse_controller.press(Button.left)
    MoveMouseSmoothly(mouse_controller, 300, 0)
    mouse_controller.release(Button.left)
    mouse_controller.position = (center[0]-150, center[1]+50)
    mouse_controller.press(Button.left)
    MoveMouseSmoothly(mouse_controller, 300, 0)
    mouse_controller.release(Button.left)



def GetWindowByCoordinate(x, y):      
    return pyautogui.getWindowsAt(x, y)[0]

# 用一个循环来获取, 可能会卡死
def GetWindowByClick():
    _ = [1]
    def inner(key):
        if key == Key.ctrl_l:
            _[0] = False
    listener = Listener(on_press=inner)
    listener.start()
    while _[0]:
        ...           
    listener.stop()
    return GetWindowByCoordinate(*pyautogui.position())

def OcrByPic(filename, lang="eng"):
    pytesseract.pytesseract.tesseract_cmd = r"D:\Environment\Tesseract-OCR\tesseract.exe"
    img = Image.open(filename).convert("L")
    # 将灰度图二值化
    threshold = 100
    binaryed_img = img.point(lambda grey_value : 255 if grey_value > threshold else 0)  
    binaryed_img.save("binaryed_question.png")
    # custom_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'    # 识别答题区文本
    
    return paddle_ocr.ocr("binaryed_question.png")      
    # return pytesseract.image_to_string(binaryed_img, lang=lang, config=custom_config)

def ClickButtonByCoordinate(coordinate_x, coordinate_y):
    mouse_controller.position = (coordinate_x, coordinate_y)
    mouse_controller.click(Button.left, 1)

def GetScreenshot(window):
    pyautogui.screenshot("screenshot.png", region=[window.left, window.top, window.width, window.height])

def SavePicAreaByPos(img, pos, filename):
        # 保存识别到的区域的图像
    cropped_img = img[pos[0][1]:pos[1][1], pos[0][0]:pos[1][0]]
    binary_threshold = 100  # 图像二值化的阈值, 下面是图像二值化
    Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)).point(lambda grey_value : 255 if grey_value > binary_threshold else 0).save(filename)


def FinishCompareValue(selected_window):
    while True:
        GetScreenshot(selected_window)
        img = cv2.imread("screenshot.png")
        pos_question_area = RecognizeTemplatePicToGetLocation(img, "template_pk_question_area.png")
        pos_answing_area = RecognizeTemplatePicToGetLocation(img, "template_pk_answing_area.png")
        # DrawRectangleByPos(img, pos_question_area)
        # DrawRectangleByPos(img, pos_answing_area)
        # cv2.imshow("locations", img)
        # cv2.setWindowProperty('locations', cv2.WND_PROP_TOPMOST, 1)
        # cv2.waitKey(1)
        # 开个窗口显示识别结果, 这里resize了一下, 防止窗口过大
        h, w  = img.shape[:2]
        new_img = cv2.resize(img, (int(w/2), int(h/2)))
        SavePicAreaByPos(img, pos_question_area, "question_area.png")
        offset = (selected_window.left, selected_window.top)
        string = OcrByPic("question_area.png", lang="chi_sim+eng")

        img_q = cv2.imread("question_area.png")
        if not string[0]:
            continue
        nums = [string[0][i][1][0] for i in range(len(string[0]))]

        if len(nums) == 2:
            a, b = nums
        elif len(nums) == 3:
            a, _, b = nums

        black_list = "<>=?"

        try:
            if a in black_list or b in black_list:
                continue
            b = int(b)
            a = int(a)
        except Exception as e:
            print(e)
            continue
        if a < b:
            DrawLessThanWithin(offset, pos_answing_area)
        elif a > b:
            DrawGreatThanWithin(offset, pos_answing_area)
        else:
            DrawEqualWithin(offset, pos_answing_area)
        time.sleep(0.4)


def main():
    selected_window = GetWindowByClick()
    FinishCompareValue(selected_window)
if __name__ == "__main__":
    main()