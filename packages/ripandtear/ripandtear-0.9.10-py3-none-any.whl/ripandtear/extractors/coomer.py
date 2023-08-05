import re
import logging
import time
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from yt_dlp.utils import asyncio

from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.extractors.common import Common
from ripandtear.utils.tracker import Tracker
from ripandtear.utils import rat_info


log = logging.getLogger(__name__)

re_single_content = re.compile(
    r"(https?://)([\w]+\.)?((coomer)\.(party))(/(data))([\w\/]+)(/)([\w\-\_]+)\.(\w+)")

re_content_page = re.compile(
    r"(https?://)([\w]+\.)?((coomer)\.(party))(/(onlyfans)/)(user/)([\w\_\-\.]+)(/(post)/)([\w]+)")

re_user_page = re.compile(
    r"(https?://)([\w]+\.)?((coomer)\.(party))(/(onlyfans)/)(user/)([\w\_\-\.]+)(\?o=[\w]+)?")


class Coomer(Common):

    def __init__(self):
        self.tracker = Tracker.getInstance()
        self.prefix = 'coomer'
        self.already_downloaded = rat_info.get_downloaded_urls()

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if re_single_content.match(url_dictionary['url']):
            log.debug("Found single content. Preparing download")
            await self.single_content_download(url_dictionary.copy())

        elif re_content_page.match(url_dictionary['url']):
            log.debug("Found content page. Preparing download")
            await self.content_page_download(url_dictionary.copy())

        elif re_user_page.match(url_dictionary['url']):
            log.debug("Found user page. Preparing download")
            await self.user_page_download(url_dictionary.copy())

        else:
            log.info(
                f"No regex pattern found for: {url_dictionary['url']}")

    async def call(self, url: str, url_dictionary: UrlDictionary) -> httpx.Response | None:
        try:

            async with httpx.AsyncClient() as client:
                log.debug(f"Making call to: {url}")
                response = await client.get(url, timeout=None, follow_redirects=True)

        except httpx.ReadError:
            await self.common_failed_attempt(url_dictionary.copy())
            return

        if response.status_code >= 300:
            # print(f"{response.status_code} - {url_dictionary}")
            url_dictionary['status_code'] = response.status_code
            await self.common_bad_status_code(url_dictionary.copy())
            return

        return response

    async def single_content_download(self, url_dictionary: UrlDictionary) -> None:

        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url_dictionary['url'], timeout=None, follow_redirects=True)

        except httpx.ReadError:
            await self.common_failed_attempt(url_dictionary.copy())
            return

        # print(response.headers)

        if url_dictionary.get('description') is None:
            url_dictionary['name'] = re_single_content.match(
                url_dictionary['url']).group(10)

        url_dictionary['url_to_download'] = str(response.url)

        try:
            url_dictionary['file_size'] = response.headers.get(
                'content-length')

        except KeyError:
            url_dictionary['file_size'] = 0

        url_dictionary['extension'] = response.headers.get('content-type')
        url_dictionary['filename'] = self.common_filename_creator(
            url_dictionary.copy())

        # log.warn(url_dictionary)
        log.debug("Url dictionary built. Sending to tracker")
        await self.tracker.add_url_dictionary(url_dictionary.copy())
        await self.common_advance_search_count(url_dictionary.copy())

    async def content_page_download(self, url_dictionary: UrlDictionary) -> None:

        if url_dictionary['url'] in self.already_downloaded:
            log.info(f"Already downloaded: {url_dictionary['url']}")
            return

        response = await self.call(url_dictionary['url'], url_dictionary.copy())

        try:
            html = BeautifulSoup(response.text, 'html.parser')

        except AttributeError:
            log.debug("The response was None. Returning")
            return

        post_content = html.find('div', {'class': 'post__content'})

        if post_content is not None:
            url_dictionary['description'] = post_content.text

        post_published = html.find('div', {'class': 'post__published'})
        date = post_published.time['datetime'].split(' ')[0]

        file_creation_date = datetime.strptime(
            (date), "%Y-%m-%d")

        epoch_time = time.mktime(file_creation_date.timetuple())
        url_dictionary['date'] = epoch_time

        url_dictionary['album_name'] = re_content_page.match(
            url_dictionary['url']).group(12)

        url_dictionary['url_to_record'] = url_dictionary['url']

        all_content = []

        downloads = html.find_all('a', {'class': 'post__attachment-link'})
        for download in downloads:
            all_content.append(download['href'])

        files = html.find_all('a', {'class': 'fileThumb'})
        for file in files:
            all_content.append(file['href'])

        tasks = []
        count = 1
        for href in all_content:
            url = f"https://coomer.party{href}"

            url_dictionary['prefix'] = self.prefix
            url_dictionary['count'] = count
            url_dictionary['url'] = url

            tasks.append(asyncio.create_task(self.run(url_dictionary.copy())))

            count += 1

        await asyncio.gather(*tasks)

    async def user_page_download(self, url_dictionary: UrlDictionary) -> None:

        try:
            count = int(url_dictionary['url'].split('=')[1])

        except IndexError:
            count = 0

        username = re_user_page.match(url_dictionary['url']).group(9)
        while True:

            call_url = f"https://coomer.party/onlyfans/user/{username}?o={count}"
            log.debug(f"Call Url: {call_url}")

            response = await self.call(call_url, url_dictionary.copy())

            if response is None:
                log.error(f"Problem finding: {call_url}")
                return

            html = BeautifulSoup(response.text, 'html.parser')

            posts = html.find_all('article', {'class': 'post-card'})
            log.debug(f"Number of posts found: {len(posts)}")

            if len(posts) == 0:
                log.info("No more posts found")
                break

            for post in posts:
                href = post.find('a')
                url = f"https://coomer.party{href['href']}"
                log.debug(url)
                url_dictionary['url'] = url
                log.debug(url_dictionary)
                await self.run(url_dictionary.copy())
            count += 25
