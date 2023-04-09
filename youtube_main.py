import os
import sys
import argparse
import json
import sentry
import logging
import hashlib
from glob import glob
from datetime import datetime

import src.youtube as youtube
from config import Base as Config
from config import GoogleAPI


if __name__ == "__main__":

    sentry.init(Config.PROFILE, 'webcrawler')
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='%(asctime)s [%(filename)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S') 

    parser = argparse.ArgumentParser()
    parser.add_argument('--q', type=str, default='검색어')
    parser.add_argument('--save_path', type=str, default='./data_youtube')
    
    q = parser.parse_args().q
    save_path = parser.parse_args().save_path

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # video info
    res = youtube.searchVideos(GoogleAPI, query=q, type='video')
    vids = [x['id']['videoId'] for x in res['items']]
    
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H:%M:%S")
    filename = f"{save_path}/result_{q}_youtube_{timestamp}.json"
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

    # commentsThreads
    pids = []
    all_comments = {}
    for vid in vids:
        comments = {}
        for video in youtube.getCommentsThreads(GoogleAPI, vid=vid):
            try:
                for comm in video['items']:
                    key = comm['etag']
                    comments[key] = comm
                    if comm['snippet']['totalReplyCount']!= 0:
                        pids.append(comm['id'])
            except Exception:
                pass
        all_comments[vid] = comments

    newfilename = filename.replace('_youtube_', '_youtube_comm_')
    with open(newfilename, 'w', encoding="utf-8") as f:
        json.dump(all_comments, f, indent=4, ensure_ascii=False)

    # comments
    all_replies = {}
    for pid in pids:
        replies = {}
        for comment in youtube.getComments(GoogleAPI, pid=pid):
            try:
                for rep in comment['items']:
                    key = rep['etag']
                    replies[key] = rep
            except Exception:
                pass
        all_replies[pid] = replies
        
    newfilename = filename.replace('_youtube_', '_youtube_rep_')
    with open(newfilename, 'w', encoding="utf-8") as f:
        json.dump(all_replies, f, indent=4, ensure_ascii=False)
