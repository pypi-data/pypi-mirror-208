import asyncio
import httpx
import logging
import re

from bs4 import BeautifulSoup

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils import rat_info
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

sem = asyncio.Semaphore(6)

root_url = "https://tiktits.com/"

re_user_profile = re.compile(
    r"(users/)([\w\-_\(\)]+)")

re_video_page = re.compile(
    r"(video/|categories/)([\w\-]+/)?([\w\-_\(\)]+)(\.\w+)?")

re_direct_video_url = re.compile(
    r"(assets/)(uploads/)([\w\-_\(\)]+)\.(\w+)")

prefix = 'tiktits'


class Tiktits(Common):

    def __init__(self):

        self.already_downloaded_urls = rat_info.get_downloaded_urls()
        self.tracker = Tracker.getInstance()

    async def run(self, url_dictionary):
        log.debug("Inside tiktits")

        if re_user_profile.search(url_dictionary['url']):
            await self.user_profile_download(url_dictionary.copy())

        elif re_video_page.search(url_dictionary['url']):
            await self.video_page_download(url_dictionary.copy())

        elif re_direct_video_url.search(url_dictionary['url']):
            await self.direct_video_download(url_dictionary.copy())

        else:
            log.info(f"No regex pattern matches: {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary.copy())

    async def call(self, endpoint: str, url_dictionary: UrlDictionary) -> httpx.Response | None:

        url = f"https://tiktits.com/{endpoint}"

        log.debug("Making call to tiktits")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=None)

        except Exception:
            log.exception(f"Problem downloading: {url}")
            await self.common_failed_attempt(url_dictionary.copy())
            return

        if response.status_code >= 300:

            url_dictionary['status_code'] = int(response.status_code)
            await self.common_bad_status_code(url_dictionary.copy())
            await self.common_advance_search_count(url_dictionary.copy())
            return

        log.debug("Returning response")
        return response

    async def user_profile_download(self, url_dictionary: UrlDictionary) -> None:

        username = re_user_profile.search(url_dictionary['url']).group(2)
        endpoint = f"users/{username}"

        tasks = []
        while True:

            log.info("Searching page for content")
            response = await self.call(endpoint, url_dictionary.copy())

            # print(response.url)
            try:
                soup = BeautifulSoup(response.text, 'html.parser')

            except AttributeError:
                log.info(
                    "No user profile found. Possible deleted or doesn't exist")
                return

            all_videos = soup.find('div', {'class': 'categories__list'})

            all_video_containers = all_videos.find_all('a')

            for container in all_video_containers:

                url_dictionary['url'] = f"{root_url}{container['href']}"

                # log.debug(f"Adding url: {url_dictionary['url']}")
                tasks.append(asyncio.create_task(
                    self.run(url_dictionary.copy())))

            next_page = soup.find('li', {'class': 'next'})

            try:
                next_page_link = next_page.find('a')['href']
                endpoint = next_page_link

            except AttributeError:
                log.info("No more pages. Exiting loop")
                break

        await asyncio.gather(*tasks)

    async def video_page_download(self, url_dictionary: UrlDictionary) -> None:

        async with sem:

            if url_dictionary['url'] in self.already_downloaded_urls:
                return

            endpoint = re_video_page.search(url_dictionary['url']).group()
            response = await self.call(endpoint, url_dictionary.copy())

            if response is None:
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            video = soup.find('video', {'class': 'lazy-video'})
            video_sources = video.find_all('source')
            highest_quality_video = video_sources[0]['src']

            url_dictionary['name'] = re_video_page.search(
                url_dictionary['url']).group(3)

            url_dictionary['url'] = f"{root_url}{highest_quality_video}"
            url_dictionary['url_to_record'] = str(response.url)

            await self.run(url_dictionary.copy())

    async def direct_video_download(self, url_dictionary: UrlDictionary) -> None:

        endpoint = re_direct_video_url.search(url_dictionary['url']).group()

        response = await self.call(endpoint, url_dictionary.copy())

        if response is None:
            return

        url_dictionary['prefix'] = prefix
        url_dictionary['url_to_download'] = str(response.url)

        if response.headers.get('content-length'):
            url_dictionary['file_size'] = response.headers.get(
                'content-length')
        else:
            url_dictionary['file_size'] = None

        url_dictionary['date'] = await self.common_get_epoch_time(
            str(response.headers.get('last-modified')))

        # name could be set if url_dictionary is coming from video page
        # Otherwise set it now

        if url_dictionary.get('name') is None:
            url_dictionary['name'] = re_direct_video_url.search(
                url_dictionary['url']).group(3)

        url_dictionary['extension'] = response.headers.get('content-type')

        url_dictionary['filename'] = self.common_filename_creator(
            url_dictionary.copy())

        # print(url_dictionary)
        # await self.common_file_downloader(url_dictionary.copy())
        log.info("Url dictionary built. Sending to tracker")
        await self.tracker.add_url_dictionary(url_dictionary.copy())
        await self.common_advance_search_count(url_dictionary.copy())
