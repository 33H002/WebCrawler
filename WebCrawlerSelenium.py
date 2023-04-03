import time
import random

from tqdm import tqdm
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class BaseCrawler:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.options)


class BlogCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()

    def run(self, urls: List[str]) -> List[dict]:
        result = []
        for url in tqdm(urls):
            try:
                self.driver.get(url)
                self.driver.implicitly_wait(10)
                time.sleep(random.randint(5, 15)/10)

                title, text, tags = None, None, None

                if 'blog.naver.com' in url:
                    self.driver.switch_to.frame('mainFrame')
                    time.sleep(random.randint(5, 10) / 10)
                    source = self.driver.page_source
                    title = self.driver.find_element(By.CLASS_NAME, 'pcol1').text

                    if 'se_component_wrap' in source:
                        text = ' '.join(self.driver.find_element(By.CLASS_NAME, 'se_component_wrap').text.split('\n'))
                    elif 'se-main-container' in source:
                        text = ' '.join(self.driver.find_element(By.CLASS_NAME, 'se-main-container').text.split('\n'))
                    if 'class="wrap_tag"' in source:
                        tags = self.driver.find_element(By.CLASS_NAME, 'wrap_tag').text.split('\n')[1:]

                # HOTFIX
                else:
                    source = self.driver.page_source
                    body = self.driver.find_element(By.ID, 'content')
                    title = body.find_element(By.TAG_NAME, 'h1').text
                    text = ' '.join(body.find_element(By.CLASS_NAME, 'entry-content').text.split('\n'))
                    if 'class="tags"' in source:
                        tags = self.driver.find_element(By.CLASS_NAME, 'tags').text.split('\n')[1:]

                result.append({"link": url, "title": title, "contents": text, "tags": tags})

            # TODO
            except Exception as e:
                pass

        return result

    def quit(self):
        self.driver.quit()
