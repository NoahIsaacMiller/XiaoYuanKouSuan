import cv2

def RecognizeTemplatePicToGetLocation(target_pic, template_pic_path):
    template_pic = cv2.imread(template_pic_path)
    result = cv2.matchTemplate(target_pic, template_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    h, w = template_pic.shape[:2]
    bottom_right = (top_left[0]+w, top_left[1]+h)
    return (top_left, bottom_right)

def DrawRectangleByPos(img, pos):
    cv2.rectangle(img, pos[0], pos[1], (0, 255, 0), 5)





