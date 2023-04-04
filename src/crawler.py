from typing import Any, Iterator

from WebCrawler import *
from WebCrawlerSelenium import *


def getNaverData(config: Any, query: str, start: int = 1, end: int = 1000,
                 sort: str = "sim", display: int = 100, mode: str = 'blog') -> Iterator[str]:
    assert start >= 1 and start <= 1000, 'check "start" range (1, 1000)'
    assert end >= start and end <= 1000, 'check "end" range (start, 1000)'
    assert sort in ['sim', 'date'], '"sort" supports [sim, date]'
    assert display >= 1 and display <= 100, 'check "display" range (1, 100)'
    assert mode in ['blog', 'cafe', 'web'], '"mode" supports [blog, cafe, web]'

    _crawler = None
    if mode == 'blog':
        _crawler = NaverBlogCrawler(config)
    elif mode == 'cafe':
        _crawler = NaverCafeCrawler(config)
    elif mode == 'web':
        _crawler = NaverWebCrawler(config)

    for _start in range(start, end+1, display):
        yield _crawler.run(query=query, start=_start, sort=sort, display=display)


def getDaumData(config: Any, query: str, start: int = 1, end: int = 50,
                sort: str = "accuracy", size: int = 50, mode: str = 'blog') -> Iterator[str]:
    assert start >= 1 and start <= 50, 'check "start" range (1, 50)'
    assert end >= start and end <= 50, 'check "end" range (start, 50)'
    assert sort in ['accuracy', 'recency'], '"sort" supports [accuracy, recency]'
    assert size >= 1 and size <= 50, 'check "size" range (1, 50)'
    assert mode in ['blog', 'cafe', 'web'], '"mode" supports [blog, cafe, web]'

    _crawler = None
    if mode == 'blog':
        _crawler = DaumBlogCrawler(config)
    elif mode == 'cafe':
        _crawler = DaumCafeCrawler(config)
    elif mode == 'web':
        _crawler = DaumWebCrawler(config)

    for _page in range(start, end+1):
        yield _crawler.run(query=query, page=_page, sort=sort, size=size)


def getBlogContents(urls: List[str]) -> List[dict]:
    _crawler = BlogCrawler()
    result = _crawler.run(urls)
    _crawler.quit()
    return result
