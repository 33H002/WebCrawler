##
 # youtubeAPI_all.py
 #
 # 190905
 ##

'''
pip install --upgrade google-api-python-client
'''
from apiclient.discovery import build

import googleapiclient.discovery

import json

from config import GoogleAPI

result   = {}
nextPage = None
_count   = 0

DEVELOPER_KEY = GoogleAPI.DEVELOPER_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION      = "v3"

youtube = googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEY)


#
# 댓글에 달린 답글 수집
# 댓글id
#
def youtube_comments(parentid, page=None):
    response = youtube.comments().list(
        part="id, snippet",
        parentId=parentid,
        pageToken=page,
        maxResults = 100,
        textFormat = "plainText"
    ).execute()

    result = []
    nextpage = -1

    # 다음 페이지
    if 'nextPageToken' in response:
        nextpage = response['nextPageToken']

    # 답글의 내용, 수정날짜, 좋아요 수 
    for comm in response.get("items"):
        comments = {}
        comments["content"]    = comm["snippet"]["textOriginal"]
        comments["publish_at"] = comm["snippet"]["publishedAt"]
        comments["like_count"] = comm["snippet"]["likeCount"]
        result.append(comments)

    return result, nextpage


#    
# 영상에 달린 댓글 수집
# 비디오id
#
def youtube_commentThreads(videoid, page=None):
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=videoid,
        order="relevance",
        pageToken=page,
        maxResults = 100,
        textFormat = "plainText"
    ).execute()

    result = []
    nextpage = -1

    # 다음 페이지
    if 'nextPageToken' in response:
        nextpage = response['nextPageToken']

    #
    # 댓글의 내용, 수정날자, 좋아요 수 
    # 답글이 달렸으면 답글 수집 함수 youtube_comments 호출
    #
    for comm in response.get("items"):
        comments = {}
        comments["content"]    = comm["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
        comments["publish_at"] = comm["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
        comments["like_count"] = comm["snippet"]["topLevelComment"]["snippet"]["likeCount"]

        # 답글이 달린 경우
        if comm["snippet"]["totalReplyCount"] != 0:
            rep = []
            nextCommentsPage = None
            _id = comm["id"]
            while(True):
                comments_result = youtube_comments(_id, nextCommentsPage)
                for _comm in comments_result[0]:
                    rep.append(_comm)
                # 다음 페이지로
                if comments_result[1] != -1:
                    nextCommentsPage = comments_result[1]
                # 끝까지 가져오면 break
                else: break
            comments["comments"] = rep
        result.append(comments)        

    return result, nextpage


#
# 채널 정보 수집
# 채널id
#
def youtube_channels(channelid):
    response = youtube.channels().list(
        part="snippet, statistics",
        id=channelid
    ).execute()

    result = {}

    # 채널 이름, 구독자 수 
    channel = response.get("items")[0]
    result["channel_name"]    = channel['snippet']['title']
    result["subscriber_count"] = channel['statistics']['subscriberCount']

    return result


#
# 영상 정보 수집
# 비디오id
#
def youtube_video(videoid):
    response = youtube.videos().list(
        part="snippet, statistics",
        id=videoid
    ).execute()

    result = {}
    video = response.get("items")[0]

    # 영상 제목, 설명, 수정날짜, 조회수, 영상id, 좋아요 수, 싫어요 수, 카테고리 id, 채널 id
    result["title"]       = video["snippet"]["title"]
    result["description"] = video["snippet"]["description"]
    result["publish_at"]  = video["snippet"]["publishedAt"]
    result["view_count"]  = video["statistics"]["viewCount"]
    result["id"]          = video["id"]
    result["like_count"]  = video["statistics"]["likeCount"]
    result["dislike_count"] = video["statistics"]["dislikeCount"]
    result["category_id"]   = video["snippet"]["categoryId"]
    result["channel_id"]    = video["snippet"]["channelId"]
    
    # 영상을 올린 채널 정보 수집
    result['channel'] = youtube_channels(result["channel_id"])
    
    return result


#
# 검색어를 입력
# 영상이면 영상 정보 및 댓글 수집 함수 호출
# 채널이면 채널 정보 수집 함수 호출
#
def youtube_search(q, max_results=50, page=None, count=0):
    response = youtube.search().list(
      q=q,
      part="id,snippet",
      maxResults=max_results,
      pageToken=page
    ).execute()

    result = {}
    nextpage = -1

    # 다음 페이지
    if 'nextPageToken' in response:
        nextpage = response['nextPageToken']

    for video in response.get("items", []):
        tmp = {}
        # 영상인 경우
        if video["id"]["kind"] == "youtube#video":
            videoid = video["id"]["videoId"]
            # 영상 정보 수집
            info = youtube_video(videoid)
            # 댓글 수집
            nextCommentsPage = None
            comments = []
            while(True):
                comments_result = youtube_commentThreads(videoid, nextCommentsPage)
                for comm in comments_result[0]: 
                    comments.append(comm)
                # 다음 페이지로
                if comments_result[1] != -1: 
                    nextCommentsPage = comments_result[1]
                # 끝까지 가져오면 break
                else: break

            tmp["type"] = "video"
            for k in info.keys(): tmp[k] = info[k]
            tmp["comments"] = comments

            result[count] = tmp
            count += 1
            
        # 채널인 경우   
        elif video["id"]["kind"] == "youtube#channel":
            channelid = video["id"]["channelId"]
            tmp["type"] = "channel"
            tmp["channel_id"] = channelid
            # 채널 정보 수집
            tmp["channel"] = youtube_channels(channelid)

            result[count] = tmp
            count += 1
        
        # 영상 x, 채널 x인 경우
        else: pass

        '''
        # 파일 쓰기
        with open('test.json', 'a', encoding='UTF-8') as f:
            f.write(json.dumps(dict(result), ensure_ascii=False, indent=4))     
            f.write(',\n')   
        '''
    return result, nextpage

def init():
    global result
    global nextPage
    global _count

    result   = {}
    nextPage = None
    _count   = 0


#
# main
#
def main(search_text, limit = 10):
    global result
    global nextPage
    global _count
    #search_text = input('Input Search Text: ')

    # 다음 페이지로 넘겨가면서 
    while(True):
        try:
            tmp = youtube_search(search_text, max_results=1, page=nextPage, count=_count)
            
            for k in tmp[0].keys(): result[k] = tmp[0][k]

            # 파일 쓰기
            with open('test.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(dict(result), ensure_ascii=False, indent=4))
            
            # num개까지 받아오기 
            _count   = len(result)
            if _count >= limit: break 
            # 다음 페이지로 
            elif tmp[1] != -1: nextPage = tmp[1]       
            # 끝까지 가져오면 break
            else: break

        except Exception as e:
            print(e)
            print('Page: ' + str(nextPage))
            break
        
    return result
