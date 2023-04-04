##
 # naver_blog.py
 #
 # 19.09.27
 ##
import urllib
import requests
import time
import json
import re

import ocr_with_tesseract2 as o
from bs4 import BeautifulSoup


#
# 블로그 크롤링
#
# 검색 결과 페이지에 접근하여
# 포스트의 url을 얻은 후
# 다시 포스트 url로 접근하여 데이터(제목, 내용, 날짜)를 수집함
#
# 포스트 내 이미지에 대하여 ocr 수행한 결과
# 홍보성 글로 판단될 경우
# 해당 포스트는 수집하지 않음 
#
def run(keyword, start):
    # 검색 결과 페이지 접근  
    search_url = 'https://search.naver.com/search.naver?where=post&query={0}&st=sim&sm=tab_opt&date_from=20190902&date_to=20190908&date_option=8&srchby=all&post_blogurl=blog.naver.com&start={1}'.format(keyword, start)
    req  = requests.get(search_url)
    soup = BeautifulSoup(req.content, 'lxml')

    body      = soup.find('div', 'main_pack')
    container = body.findAll('li', {'class':'sh_blog_top'})

    i = 0
    result = []

    p = re.compile('\d')

    # 현재 페이지에 대하여
    while(True):
        try:
            if(i == len(container)): break
            else:
                # post list       
                time.sleep(0.5)
                con  = container[i].find('a', 'sh_blog_title _sp_each_url _sp_each_title').attrs
                date = ''.join(p.findall(container[i].find('dd', 'txt_inline').text))
                
                # post 접근
                newURL  = con['href']
                req     = requests.get(newURL)
                newPage = BeautifulSoup(req.content, 'lxml')

                # frame 접근
                time.sleep(0.5)
                frame  = newPage.find('iframe').attrs
                newReq = requests.get('http://blog.naver.com' + frame['src'])
                
                framepage = BeautifulSoup(newReq.text, 'lxml')

                # 제목, 내용, 이미지 url 받아오기
                title   = framepage.find('meta', {'property':'og:title'}).attrs['content']
                body    = framepage.find('div', ['se-main-container', 'postListBody'])
                text    = body.text.replace(u'\u200b', '')
                content = text.strip()
                images  = [img.attrs['data-lazy-src'] for img in body.find_all('img') if 'data-lazy-src' in img.attrs.keys()] 
                               
                # 이미지내의 글자 체크
                isAd = 0
                if len(images) == 0: pass
                elif check_str_from_images([images[-1]]) == 1: isAd = 1 # 마지막 이미지만 검사
                #elif check_str_from_images(images) == 1: isAd = 1      # 모든 이미지 검사
                
                if isAd == 0:    
                    doc = {'title' : title, 'date': date, 'content': content}
                    result.append(doc)
                else: print('is Ad')
                
                i += 1

        except Exception as e:
            print(e)
            i += 1

    return result


#
# 이미지 내의 문장에
# 특정 단어가 등장하면
# 홍보, 광고성 글이라고 판단
#
def check_str_from_images(images):
    p = re.compile('제공.?받아|지원.?받아|협찬|고료')
    flag = 0

    for image in images:
        str_from_image = o.extract_string(image)
        if p.search(str_from_image):
            flag = 1
            print(str_from_image)
            break
        else: pass

    return flag


#
# main
# 검색어에 대하여
# 첫 페이지부터 끝 페이지까지 루프를 돌며
# 블로그 포스트를 수집함
#
def main(keyword = '다이슨', startPage = 1, save_path='.'):
    keyword = urllib.parse.quote(keyword)
    pagenum = startPage
    
    while(True):
        if pagenum == 100: break
        result  = []
        res = run(keyword, (pagenum - 1) *10 + 1)
        for r in res: 
            result.append(r)
        pagenum += 1

        # 결과 파일 저장
        filename = f'{save_path}/result.json'
        for r in res: 
            with open(filename, 'a', encoding='UTF-8') as fw:
                fw.write(json.dumps(r, ensure_ascii=False, indent=4))
                fw.write(',\n')


if __name__ == '__main__':
    main()
