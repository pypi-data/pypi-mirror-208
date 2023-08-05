import cv2
import numpy as np
import base64

def recognize_slider(back_img_str, cut_img_str):

    back_img_data = base64.b64decode(back_img_str)
    cut_img_data = base64.b64decode(cut_img_str)
    
    # 读取图片
    back_img = cv2.imdecode(np.frombuffer(back_img_data,np.uint8),cv2.IMREAD_COLOR)
    cut_img = cv2.imdecode(np.frombuffer(cut_img_data,np.uint8),cv2.IMREAD_COLOR)

    # 识别图片边缘
    back_edge = cv2.Canny(back_img, 100, 300)
    cut_edge = cv2.Canny(cut_img, 100, 300)
    
    # 转换图片格式
    back_ = cv2.cvtColor(back_edge, cv2.COLOR_GRAY2RGB)
    cut_ = cv2.cvtColor(cut_edge, cv2.COLOR_GRAY2RGB)
    
    # 缺口匹配
    res = cv2.matchTemplate(back_, cut_, cv2.TM_CCOEFF_NORMED)
    max_loc = cv2.minMaxLoc(res)[-1]  # 寻找最优匹配
    
    # 返回缺口坐标
    return max_loc

