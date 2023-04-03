import json
from typing import Any, Iterator, Optional

from WebCrawler import YoutubeCrawler, YoutubeCommentsThreadsCrawler, YoutubeCommentsCrawler, YoutubeVideoCrawler


def searchVideos(config: Any, query: str, **kwargs) -> Iterator[dict]:
    crawler = YoutubeCrawler(config)
    return json.loads(crawler.run(query, param=kwargs))


def getVideo(config: Any, vid: str, **kwargs) -> Iterator[dict]:
    crawler = YoutubeVideoCrawler(config)
    return json.loads(crawler.run(vid=vid, param=kwargs))


def getCommentsThreads(config: Any, vid: str, pg_token: Optional[str] = None, **kwargs) -> Iterator[dict]:
    while True:
        crawler = YoutubeCommentsThreadsCrawler(config)
        try:
            res = json.loads(crawler.run(vid=vid, pg_token=pg_token, param=kwargs))
            yield res

            if 'nextPageToken' not in res.keys():
                break
            else:
                pg_token = res['nextPageToken']
        except Exception:
            break


def getComments(config: Any, pid: str, pg_token: Optional[str] = None, **kwargs) -> Iterator[dict]:
    while True:
        crawler = YoutubeCommentsCrawler(config)
        try:
            res = json.loads(crawler.run(pid=pid, pg_token=pg_token, param=kwargs))
            yield res

            if 'nextPageToken' not in res.keys():
                break
            else:
                pg_token = res['nextPageToken']
        except Exception:
            break


if __name__ == "__main__":

    from config import GoogleAPI

    _vid = 'AAfmtUcyzhU'
    vid_info = getVideo(GoogleAPI, vid=_vid)

    print(f'--------------')
    print(f"title: {vid_info['items'][0]['snippet']['title']}")

    total = {}
    for i, item in enumerate(getCommentsThreads(GoogleAPI, vid=_vid, order='relevance', maxResults=10)):
        total[item['etag']] = item
        break

    print(f'--------------')
    print(total[list(total.keys())[0]]['items'][0])

    _pid = total[list(total.keys())[0]]['items'][0]['id']

    total_rep = {}
    for i, _item in enumerate(getComments(GoogleAPI, pid=_pid, maxResults=10)):
        total_rep[_item['etag']] = _item
        break

    print(f'--------------')
    print(total_rep[list(total_rep.keys())[0]]['items'][0])
