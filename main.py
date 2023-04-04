import os
import argparse
import json
import hashlib
import sentry_sdk # TODO
from glob import glob
from datetime import datetime

import src.crawler as crawler
from config import NaverAPI, KakaoAPI


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--q', type=str, default='검색어')
    parser.add_argument('--save_path', type=str, default='./data')
    
    q = parser.parse_args().q
    save_path = parser.parse_args().save_path

    if not os.path.exists(save_path):
        os.makedirs(save_path)
     

    """Naver API 블로그/카페/웹 검색 결과"""
    for service in ['blog', 'cafe', 'web']:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H:%M:%S")
        filename = f"{save_path}/result_{q}_naver_{service}_{timestamp}.json"
        
        cnt = 0
        all_items = {}
        for item in crawler.getNaverData(NaverAPI, query=q, start=1, end=1000, sort='sim', display=100, mode=service):
            _item = json.loads(item)['items']
            for i in _item:
                key = hashlib.sha256(f'{filename}_{cnt}'.encode()).hexdigest()
                all_items[key] = i
                cnt += 1
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=4, ensure_ascii=False)

    
    """Kakao API 블로그/카페/웹 검색 결과"""
    for service in ['blog', 'cafe', 'web']:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H:%M:%S")
        filename = f"{save_path}/result_{q}_daum_{service}_{timestamp}.json"

        cnt = 0
        all_items = {}
        for item in crawler.getDaumData(KakaoAPI, query=q, start=1, end=50, sort='accuracy', size=50, mode=service):
            _item = json.loads(item)['documents']
            for i in _item:
                key = hashlib.sha256(f'{filename}_{cnt}'.encode()).hexdigest()
                all_items[key] = i
                cnt += 1

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=4, ensure_ascii=False)
    
    
    """Selenium 블로그 게시글 내용"""
    files = glob(f'{save_path}/*_{q}_*blog*')
    for file in sorted(files): 

        with open(file, 'r') as f:
            _d = json.load(f)

        keys = list(_d.keys())
        links = list(map(lambda x: x['link'] if 'link' in _d[keys[0]] else x['url'], _d.values()))
        
        for i, (chunk, key) in enumerate(zip([links[i:i+100] for i in range(0, len(links), 100)], [keys[i:i+100] for i in range(0, len(keys), 100)])):
            result = {}
            if True:
                _result = crawler.getBlogContents(chunk)
                for r, k in zip(_result, key):
                    result[k] = r

                new_filename = file.replace('blog', f'blog_details_{i}').replace('data', 'data_details')
                with open(new_filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
    