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

# 'https://cyberdrop.me/a/7ADTZ9dO'
re_cyberdrop_album = re.compile(
    r"(https?://)(www\.)?(cyberdrop\.(cc|me|to))(/a/)(\w+)")

re_cyberdrop_single = re.compile(
    r"(https?://)([\w-]+\.)(cyberdrop\.(cc|me|to))/([\w\-_\(\)\%\+]+)\.(\w+)")


class Cyberdrop(Common):

    def __init__(self):

        self.tracker = Tracker.getInstance()

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if re_cyberdrop_single.match(url_dictionary['url']):
            await self.single_downloader(url_dictionary)

        if re_cyberdrop_album.match(url_dictionary['url']):
            await self.album_downloader(url_dictionary)

    async def single_downloader(self, url_dictionary: UrlDictionary) -> None:

        async with sem:
            log.info(
                f"Individual file found. Attempting download: {url_dictionary['url']}")
            try:
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.head(url_dictionary['url'], timeout=15, follow_redirects=True)

            except Exception:
                log.warn(
                    f"Problem downloading url: {url_dictionary['url']}")
                await self.common_failed_attempt(url_dictionary)
                return

            # print(response.headers)
            url_dictionary['name'] = re_cyberdrop_single.match(
                url_dictionary['url']).group(5)
            url_dictionary['extension'] = response.headers['Content-Type']
            url_dictionary['url_to_download'] = url_dictionary['url']
            url_dictionary['file_size'] = int(
                response.headers['Content-Length'])
            url_dictionary['filename'] = self.common_filename_creator(
                url_dictionary.copy())

            # print(url_dictionary)
            # await self.common_file_downloader(url_dictionary.copy())
            log.debug("Url dictionary built. Sending to tracker")
            await self.tracker.add_url_dictionary(url_dictionary.copy())

            url_dictionary['progress']['search_object'].advance(
                url_dictionary['progress']['search_id'], 1)

    async def album_downloader(self, url_dictionary: UrlDictionary) -> None:

        log.info(
            f"Cyberdrop album found. Attempting to find files: {url_dictionary['url']}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url_dictionary['url'], timeout=60)

        except httpx.ReadError:
            log.error(
                f"Problem downloading url: {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

        except httpx.ConnectError:
            log.error(
                f"Problem downloading url: {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

        if response.status_code >= 300:
            url_dictionary['response'] = response

            url_dictionary['fail'] = True
            log.debug("Bulding dictionary failed. Sending to tracker")
            await self.tracker.add_url_dictionary(url_dictionary.copy())

            url_dictionary['progress']['search_object'].advance(
                url_dictionary['progress']['search_id'], 1)
            return

        log.debug("Got response. Parsing for individual file urls")
        try:
            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find('div', {"id": "table"})
            hrefs = table.find_all('a', {"class": "image"})

        except AttributeError:
            log.info(f"Album deleted: {url_dictionary['url']}")

            await self.common_failed_attempt(url_dictionary)
            return

        tasks = []
        already_downloaded_urls = rat_info.get_downloaded_urls()

        log.info("Preparing to download individual files")
        for link in hrefs:
            url = str(link['href'])
            url = url.replace(" ", "%20")

            if already_downloaded_urls is not None:
                if url in already_downloaded_urls and url_dictionary['download'] is True:
                    continue

                elif url not in already_downloaded_urls and url_dictionary['download'] is True:
                    url_dictionary['url'] = url
                    tasks.append(asyncio.create_task(
                        self.run(url_dictionary.copy())))

                elif url_dictionary['download'] is False:
                    print(url)

            elif url_dictionary['download'] is False:
                print(url)

            else:
                url_dictionary['url'] = url
                tasks.append(asyncio.create_task(
                    self.run(url_dictionary.copy())))

        await asyncio.gather(*tasks)
