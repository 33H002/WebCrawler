import requests

from typing import Any, Optional


class BaseCrawler:
    def __init__(self):
        pass

    def get(self, url: str, params: dict, headers: Optional[dict] = None) -> str:
        r = requests.get(url, headers=headers, params=params)
        return r.text


class NaverBlogCrawler(BaseCrawler):
    def __init__(self, config: Any):
        super().__init__()
        self.client_id = config.CLIENT_ID
        self.client_secret = config.CLIENT_SECRET
        self.header = {"X-Naver-Client-Id": self.client_id, "X-Naver-Client-Secret": self.client_secret}
        self.url = "https://openapi.naver.com/v1/search/blog"

    def run(self, query: str, start: int = 1, sort: str = "sim", display: int = 100) -> str:
        param = {"query": query, "start": start, "sort": sort, "display": display}
        return super().get(self.url, headers=self.header, params=param)


class NaverCafeCrawler(NaverBlogCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = "https://openapi.naver.com/v1/search/cafearticle"


class NaverWebCrawler(NaverBlogCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = "https://openapi.naver.com/v1/search/webkr"

    def run(self, query: str, start: int = 1, display: int = 100, **kwargs) -> str:
        param = {"query": query, "start": start, "display": display}
        return super().get(self.url, headers=self.header, params=param)


class DaumBlogCrawler(BaseCrawler):
    def __init__(self, config: Any):
        super().__init__()
        self.rest_api_key = config.REST_API_KEY
        self.header = {"authorization": f"KakaoAK {self.rest_api_key}"}
        self.url = "https://dapi.kakao.com/v2/search/blog"

    def run(self, query: str, sort: str = "accuracy", page: int = 1, size: int = 50) -> str:
        param = {"query": query, "page": page, "sort": sort, "size": size}
        return super().get(self.url, headers=self.header, params=param)
        

class DaumCafeCrawler(DaumBlogCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = "https://dapi.kakao.com/v2/search/cafe"


class DaumWebCrawler(DaumBlogCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = "https://dapi.kakao.com/v2/search/web"


class YoutubeCrawler(BaseCrawler):
    def __init__(self, config: Any):
        super().__init__()
        self.key = config.API_KEY
        self.url = 'https://www.googleapis.com/youtube/v3/search'
        self.param = dict(key=self.key, part="id, snippet", maxResults=50)

    def run(self, query: str, pg_token: Optional[str] = None, **kwargs) -> str:
        self.param['q'] = query
        self.param['pageToken'] = pg_token
        if kwargs: self.param.update(kwargs['param'].items())
        return super().get(self.url, params=self.param)


class YoutubeVideoCrawler(YoutubeCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = 'https://www.googleapis.com/youtube/v3/videos'
        self.part = 'id, snippet, contentDetails, liveStreamingDetails, player, recordingDetails, statistics, status, topicDetails'
        self.param.update(dict(part=self.part))

    def run(self, vid: str, **kwargs) -> str:
        self.param['id'] = vid
        if kwargs: self.param.update(kwargs['param'].items())
        return super().get(self.url, params=self.param)


# 댓글
class YoutubeCommentsThreadsCrawler(YoutubeCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = 'https://www.googleapis.com/youtube/v3/commentThreads'
        self.param.update(dict(maxResults=100))

    def run(self, vid: str, pg_token: Optional[str] = None, **kwargs) -> str:
        self.param['videoId'] = vid
        self.param['pageToken'] = pg_token
        if kwargs: self.param.update(kwargs['param'].items())
        return super().get(self.url, params=self.param)


# 답글
class YoutubeCommentsCrawler(YoutubeCommentsThreadsCrawler):
    def __init__(self, config: Any):
        super().__init__(config)
        self.url = 'https://www.googleapis.com/youtube/v3/comments'

    def run(self, pid: str, pg_token: Optional[str] = None, **kwargs) -> str:
        self.param['parentId'] = pid
        self.param['pageToken'] = pg_token
        if kwargs: self.param.update(kwargs['param'].items())
        return super().get(self.url, params=self.param)


if __name__ == "__main__":
    pass