##
 # ocr_with_tesseract.py
 #
 # 19.09.30
 ##
import re
import cv2
import numpy as np
import urllib
import imutils
import pytesseract


#
# 이미지 url을 받아
# 전처리 후
# string 추출하여 반환
#
def extract_string(imgurl):
    while(True):
        try:
            # 이미지 open
            img = imutils.url_to_image(imgurl)
            # 전처리
            img = preprosessing(img)
            # text area 추출
            rects = detect_text_area(img)
             # text 추출
            result = []
            for rect in rects:
                (x_min, y_min, x_max, y_max) = rect
                cropped = img[y_min:y_max, x_min:x_max]
                result.append(pytesseract.image_to_string(cropped, lang='kor'))

            return ' '.join(result)
        
        # url에 한글이 있는 경우
        except ValueError:
            imgurl = encoding_url(imgurl)
        # 처리할 수 없는 이미지
        except TypeError as e:
            print('Error ar extract_string() ', e)
            return []


#
# url 변환
#
def encoding_url(imgurl):
    p = re.compile('[ㄱ-힗]+')
    encodedUrl = imgurl
    for toencode in p.findall(imgurl):
        encodedUrl = encodedUrl.replace(toencode, urllib.parse.quote(toencode))
    return encodedUrl


#
# 이미지 전처리
# 흑백 이미지를 binary image로
# 잡음을 제거하여
# 결과 반환
#
def preprosessing(img):
    # 흑백
    gray       = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이진화
    binary     = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # 잡음 제거
    blurred = cv2.GaussianBlur(binary, (5, 5), 0)
    return blurred


# 
# text area 추출
# 이미지를 팽창시켜 
# 단어가 최소한의 area로 같이 묶일 수 있도록 함
# area 윤곽선을 추출한 뒤
# 사각형 모양으로 단순화 시켜 반환
#
def detect_text_area(img):
    # 팽창 연산 적용할 커널
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)) 
    # 팽창
    dilated = cv2.dilate(img, kernel, iterations=5)
    # 텍스트 영역 윤곽선, 경계선
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 각각 area를 사각형 모양으로 단순화 시킴
    rects = []
    for i in range(len(contours)):
        (x_min, y_min, x_max, y_max) = 99999, 99999, 0, 0
        for j in range(len(contours[i])):
            if   x_min > contours[i][j][0][0]: x_min = contours[i][j][0][0]
            elif x_max < contours[i][j][0][0]: x_max = contours[i][j][0][0]
            if   y_min > contours[i][j][0][1]: y_min = contours[i][j][0][1]
            elif y_max < contours[i][j][0][1]: y_max = contours[i][j][0][1]
        rects.append((x_min, y_min, x_max, y_max))
    return rects


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    testurl = 'https://postfiles.pstatic.net/MjAxOTA5MDJfMTU0/MDAxNTY3NDEzODU3MjMy.y9gzURzvTs4JyNrL1dySKEVC6IVnWXCx12CN_hI_ndsg.B5XSoAxEZgqAG-UW656AovbsknBNclz-c_DdkVjsgAsg.JPEG.gmdshop/Screenshot_2019-09-02_at_17.44.01.jpg?type=w966'
  
    img = imutils.url_to_image(testurl)

    plt.imshow(img, cmap='bone')
    plt.show()

    print(extract_string(testurl))
